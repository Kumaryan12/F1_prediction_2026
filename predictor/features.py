from __future__ import annotations

import numpy as np
import pandas as pd

from .config import (
    CIRCUIT_VOL,
    DEFAULT_SC,
    DEFAULT_VSC,
    DEFAULT_PIT_LOSS,
    CIRCUIT_EXTRAS,
    LOW_DF_GPS,
)

try:
    from .config import STREET_GPS
except Exception:
    STREET_GPS: set[str] = set()

try:
    from .config import LONG_STRAIGHT_GPS
except Exception:
    LONG_STRAIGHT_GPS: set[str] = set()


# -------------------------------------------------------------------
# Driver and team priors
#
# Belgian GP / Spa-Francorchamps configuration
#
# These values represent pre-race competitiveness, not pure driver
# ability. They combine:
#
# - 2026 championship performance
# - recent race form
# - current team competitiveness
# - suitability for Spa
# - high-speed confidence
# - straight-line efficiency
# - tyre management
# - mixed-weather performance
#
# Freeze these values before using Belgian GP qualifying or race data.
# -------------------------------------------------------------------

DRIVER_SKILL_PRIOR = {
    # ---------------------------------------------------------------
    # Championship-leading group
    # ---------------------------------------------------------------

    # Championship leader and strongest overall 2026 campaign.
    "ANT": 1.00,

    # Championship P2, Austrian GP winner and Silverstone runner-up.
    "RUS": 0.99,

    # Championship P3 and Silverstone podium finisher.
    "HAM": 0.97,

    # Silverstone winner and strong recent upward trajectory.
    "LEC": 0.96,

    # ---------------------------------------------------------------
    # Leading challengers
    # ---------------------------------------------------------------

    # McLaren's leading championship driver.
    "NOR": 0.92,

    # Strong overall package, although recent results have been uneven.
    "PIA": 0.89,

    # Strong Spa-specific driver profile, but weaker current team form.
    "VER": 0.92,

    # Strongest driver outside the leading four teams this season.
    "HAD": 0.87,

    # ---------------------------------------------------------------
    # Upper midfield
    # ---------------------------------------------------------------

    "GAS": 0.82,

    # Strong Silverstone result and competitive recent form.
    "LAW": 0.83,

    # Rookie uncertainty remains, but current results justify an increase.
    "LIN": 0.80,

    "BEA": 0.77,
    "COL": 0.76,

    # Audi's current points scorer and strong Silverstone finisher.
    "BOR": 0.76,

    # ---------------------------------------------------------------
    # Midfield
    # ---------------------------------------------------------------

    "SAI": 0.75,
    "ALB": 0.74,
    "OCO": 0.72,
    "HUL": 0.71,

    # ---------------------------------------------------------------
    # Lower current-performance group
    # ---------------------------------------------------------------

    # Strong historical ability, but Aston Martin is currently weak.
    "ALO": 0.70,

    "BOT": 0.66,
    "PER": 0.65,
    "STR": 0.64,
}

DEFAULT_DRIVER_PRIOR = 0.74


ROOKIE_DRIVERS = {
    "LIN",
}


RETURNEE_DRIVERS = {
    "BOT",
    "PER",
}


# -------------------------------------------------------------------
# Team-name normalization
#
# All legacy Sauber/Kick Sauber naming is normalized to Audi for the
# 2026 prediction frame.
# -------------------------------------------------------------------

TEAM_ALIAS = {
    # Audi / legacy Sauber naming
    "Audi": "Audi",
    "Audi F1 Team": "Audi",
    "Sauber": "Audi",
    "Kick Sauber": "Audi",
    "Stake Kick Sauber": "Audi",
    "Stake F1 Team Kick Sauber": "Audi",
    "Stake F1 Team": "Audi",

    # Cadillac
    "Cadillac": "Cadillac",
    "Cadillac F1 Team": "Cadillac",
    "Cadillac Formula 1 Team": "Cadillac",

    # Haas
    "Haas": "Haas F1 Team",
    "Haas F1 Team": "Haas F1 Team",
    "MoneyGram Haas F1 Team": "Haas F1 Team",

    # Racing Bulls
    "RB": "Racing Bulls",
    "VCARB": "Racing Bulls",
    "Racing Bulls": "Racing Bulls",
    "Visa Cash App RB": "Racing Bulls",
    "Visa Cash App Racing Bulls": "Racing Bulls",

    # Red Bull
    "Red Bull": "Red Bull Racing",
    "Red Bull Racing": "Red Bull Racing",
    "Oracle Red Bull Racing": "Red Bull Racing",

    # Ferrari
    "Ferrari": "Ferrari",
    "Scuderia Ferrari": "Ferrari",
    "Scuderia Ferrari HP": "Ferrari",

    # Mercedes
    "Mercedes": "Mercedes",
    "Mercedes-AMG": "Mercedes",
    "Mercedes-AMG PETRONAS Formula One Team": "Mercedes",

    # McLaren
    "McLaren": "McLaren",
    "McLaren F1 Team": "McLaren",

    # Williams
    "Williams": "Williams",
    "Williams Racing": "Williams",

    # Aston Martin
    "Aston Martin": "Aston Martin",
    "Aston Martin Aramco": "Aston Martin",
    "Aston Martin Aramco F1 Team": "Aston Martin",

    # Alpine
    "Alpine": "Alpine",
    "BWT Alpine F1 Team": "Alpine",
}


TEAM_BASELINE_PRIOR = {
    # Constructors' Championship leader.
    "Mercedes": 1.00,

    # Second in the championship and winner of the latest race.
    "Ferrari": 0.96,

    # Third in the championship with strong aero efficiency.
    "McLaren": 0.89,

    # Strong driver pairing but inconsistent 2026 package.
    "Red Bull Racing": 0.84,

    # Upper midfield
    "Racing Bulls": 0.74,
    "Alpine": 0.73,

    # Lower midfield
    "Haas F1 Team": 0.66,
    "Williams": 0.61,
    "Audi": 0.58,

    # Lower group
    "Aston Martin": 0.53,
    "Cadillac": 0.49,
}

DEFAULT_TEAM_PRIOR = 0.70


# -------------------------------------------------------------------
# General helpers
# -------------------------------------------------------------------

def _ensure_numeric(
    df: pd.DataFrame,
    cols: list[str],
) -> None:
    """Convert available columns to numeric values in place."""

    for col in cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")


def _normalize_team_names(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Normalize historical and current constructor names."""

    out = df.copy()

    if "team" in out.columns:
        out["team"] = (
            out["team"]
            .astype(str)
            .str.strip()
            .replace(TEAM_ALIAS)
        )

    return out


def _inverse_minmax_strength(
    series: pd.Series,
) -> pd.Series:
    """
    Convert lower-is-better finishing form into higher-is-better strength.

    Example:
        average finish 2.0 -> high strength
        average finish 16.0 -> low strength
    """

    values = pd.to_numeric(series, errors="coerce")

    minimum = values.min(skipna=True)
    maximum = values.max(skipna=True)

    if (
        pd.isna(minimum)
        or pd.isna(maximum)
        or maximum == minimum
    ):
        return pd.Series(
            np.nan,
            index=series.index,
            dtype=float,
        )

    return 1.0 - (values - minimum) / (maximum - minimum)


def _latest_by_entity(
    df: pd.DataFrame,
    entity_col: str,
    value_cols: list[str],
) -> pd.DataFrame:
    """
    Return the latest non-null value for each entity and feature.

    Archetype features therefore use the latest relevant archetype race,
    rather than blindly using the latest race of any circuit type.
    """

    if entity_col not in df.columns:
        raise ValueError(
            f"_latest_by_entity requires column '{entity_col}'."
        )

    entities = sorted(
        df[entity_col]
        .dropna()
        .unique()
    )

    result = pd.DataFrame({
        entity_col: entities,
    })

    for col in value_cols:
        if col not in df.columns:
            continue

        valid = df.dropna(
            subset=[entity_col, col],
        ).copy()

        if valid.empty:
            result[col] = np.nan
            continue

        if "date" in valid.columns:
            valid = valid.sort_values(
                "date",
                kind="mergesort",
            )

        latest = (
            valid
            .groupby(entity_col, as_index=False)
            .tail(1)[[entity_col, col]]
        )

        result = result.merge(
            latest,
            on=entity_col,
            how="left",
            validate="one_to_one",
        )

    return result


def _fill_from_general_or_median(
    out: pd.DataFrame,
    train: pd.DataFrame,
    col: str,
    general_col: str | None,
) -> None:
    """
    Fill a prediction feature using:

    1. general rolling form
    2. training-set median
    """

    if col not in out.columns:
        out[col] = np.nan

    if (
        general_col is not None
        and general_col in out.columns
        and col != general_col
    ):
        out[col] = out[col].fillna(out[general_col])

    if out[col].isna().any() and col in train.columns:
        median = pd.to_numeric(
            train[col],
            errors="coerce",
        ).median(skipna=True)

        if pd.notna(median):
            out[col] = out[col].fillna(median)


# -------------------------------------------------------------------
# Manual priors
# -------------------------------------------------------------------

def add_driver_skill_prior(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Add driver competitiveness and status flags."""

    out = df.copy()

    if "driver" not in out.columns:
        out["driver_skill_prior"] = DEFAULT_DRIVER_PRIOR
        out["rookie_flag"] = 0
        out["returnee_flag"] = 0
        return out

    out["driver"] = (
        out["driver"]
        .astype(str)
        .str.upper()
        .str.strip()
    )

    out["driver_skill_prior"] = (
        out["driver"]
        .map(DRIVER_SKILL_PRIOR)
        .fillna(DEFAULT_DRIVER_PRIOR)
    )

    out["rookie_flag"] = (
        out["driver"]
        .isin(ROOKIE_DRIVERS)
        .astype(int)
    )

    out["returnee_flag"] = (
        out["driver"]
        .isin(RETURNEE_DRIVERS)
        .astype(int)
    )

    return out


def add_team_prior_strength(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Add the current constructor competitiveness prior."""

    out = _normalize_team_names(df)

    if "team" not in out.columns:
        out["team_prior_strength"] = DEFAULT_TEAM_PRIOR
        return out

    out["team_prior_strength"] = (
        out["team"]
        .map(TEAM_BASELINE_PRIOR)
        .fillna(DEFAULT_TEAM_PRIOR)
    )

    return out


# -------------------------------------------------------------------
# Historical and live strength blending
# -------------------------------------------------------------------

def add_live_strength_adjustments(
    df: pd.DataFrame,
    hist_team_weight: float = 0.40,
    live_team_weight: float = 0.60,
    hist_driver_weight: float = 0.40,
    live_driver_weight: float = 0.60,
) -> pd.DataFrame:
    """
    Create historical and live strength features.

    Outputs:
        driver_hist_strength
        team_hist_strength
        driver_strength_blend_2026
        team_strength_blend_2026

    Spa is sensitive to:
        aerodynamic efficiency
        straight-line speed
        sector-two balance
        wind
        tyre warm-up
        weather variation

    Live session performance is useful, but it is intentionally limited
    to 60% of the blended feature because practice programmes may differ.
    """

    out = _normalize_team_names(df.copy())

    if "drv_form3" in out.columns:
        out["driver_hist_strength"] = _inverse_minmax_strength(
            out["drv_form3"]
        )
    else:
        out["driver_hist_strength"] = np.nan

    if "team_form3" in out.columns:
        out["team_hist_strength"] = _inverse_minmax_strength(
            out["team_form3"]
        )
    else:
        out["team_hist_strength"] = np.nan

    if "driver_2026_session_strength" in out.columns:
        historical = pd.to_numeric(
            out["driver_hist_strength"],
            errors="coerce",
        )

        live = pd.to_numeric(
            out["driver_2026_session_strength"],
            errors="coerce",
        )

        out["driver_strength_blend_2026"] = np.where(
            historical.notna() & live.notna(),
            hist_driver_weight * historical
            + live_driver_weight * live,
            historical.fillna(live),
        )
    else:
        out["driver_strength_blend_2026"] = (
            out["driver_hist_strength"]
        )

    if "team_2026_strength" in out.columns:
        historical = pd.to_numeric(
            out["team_hist_strength"],
            errors="coerce",
        )

        live = pd.to_numeric(
            out["team_2026_strength"],
            errors="coerce",
        )

        out["team_strength_blend_2026"] = np.where(
            historical.notna() & live.notna(),
            hist_team_weight * historical
            + live_team_weight * live,
            historical.fillna(live),
        )
    else:
        out["team_strength_blend_2026"] = (
            out["team_hist_strength"]
        )

    return out


# -------------------------------------------------------------------
# Circuit context
# -------------------------------------------------------------------

def add_circuit_context_df(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Add circuit, strategy, weather and volatility features."""

    if "gp" not in df.columns:
        raise ValueError(
            "add_circuit_context_df requires a 'gp' column."
        )

    def _lookup(gp: str) -> pd.Series:
        sc_prob, vsc_prob, pit_loss = CIRCUIT_VOL.get(
            gp,
            (
                DEFAULT_SC,
                DEFAULT_VSC,
                DEFAULT_PIT_LOSS,
            ),
        )

        extras = dict(
            CIRCUIT_EXTRAS.get(
                gp,
                CIRCUIT_EXTRAS.get("_default", {}),
            )
        )

        extras.setdefault(
            "is_low_df",
            float(gp in LOW_DF_GPS),
        )

        extras.setdefault(
            "is_street",
            float(gp in STREET_GPS),
        )

        is_long_straight = gp in LONG_STRAIGHT_GPS

        if "long_straight_index" not in extras:
            if extras["is_low_df"]:
                extras["long_straight_index"] = 0.85
            elif is_long_straight:
                extras["long_straight_index"] = 0.70
            else:
                extras["long_straight_index"] = 0.50

        extras.setdefault(
            "tow_importance",
            0.65 if is_long_straight else 0.50,
        )

        extras.setdefault(
            "overtake_index",
            0.58 if is_long_straight else 0.50,
        )

        extras.setdefault("braking_intensity", 0.55)
        extras.setdefault("warmup_penalty", 0.07)
        extras.setdefault("expected_stops", 2.0)
        extras.setdefault("deg_rate", 0.65)
        extras.setdefault("stint_len_typical", np.nan)

        return pd.Series({
            "sc_prob": sc_prob,
            "vsc_prob": vsc_prob,
            "pit_loss": pit_loss,
            **extras,
        })

    context = df["gp"].astype(str).apply(_lookup)

    out = pd.concat(
        [
            df.reset_index(drop=True),
            context.reset_index(drop=True),
        ],
        axis=1,
    )

    numeric_cols = [
        "sc_prob",
        "vsc_prob",
        "pit_loss",
        "expected_stops",
        "overtake_index",
        "tow_importance",
        "is_low_df",
        "is_street",
        "long_straight_index",
        "braking_intensity",
        "warmup_penalty",
        "deg_rate",
        "stint_len_typical",
        "surface_bumpiness",
        "wind_sensitivity",
        "track_limits_risk",
        "elevation_change_index",
        "mechanical_failure_risk",
        "corner_count",
        "avg_speed_kph",
        "rain_prob_race",
        "wet_lap_fraction",
        "wet_start_prob",
        "mixed_conditions_risk",
        "driver_2026_session_strength",
        "driver_2026_reliability",
        "team_2026_strength",
        "team_2026_reliability",
        "driver_hist_strength",
        "team_hist_strength",
        "driver_strength_blend_2026",
        "team_strength_blend_2026",
        "driver_skill_prior",
        "team_prior_strength",
        "rookie_flag",
        "returnee_flag",
    ]

    _ensure_numeric(out, numeric_cols)

    return out


# -------------------------------------------------------------------
# Leakage-safe rolling forms
# -------------------------------------------------------------------

def add_driver_team_form(
    full_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Create leakage-safe driver, team and circuit-archetype rolling form.

    Every rolling calculation uses shift(1), ensuring that the current
    race result is never used to predict itself.
    """

    required = {
        "year",
        "gp",
        "date",
        "driver",
        "team",
        "finish_pos",
    }

    missing = required.difference(full_df.columns)

    if missing:
        raise ValueError(
            "add_driver_team_form is missing columns: "
            f"{sorted(missing)}"
        )

    df = full_df.copy()

    df["driver"] = (
        df["driver"]
        .astype(str)
        .str.upper()
        .str.strip()
    )

    df = _normalize_team_names(df)

    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce",
    )

    df["finish_pos"] = pd.to_numeric(
        df["finish_pos"],
        errors="coerce",
    )

    df = df.dropna(
        subset=[
            "date",
            "driver",
            "team",
            "finish_pos",
        ]
    )

    df = df.sort_values(
        [
            "date",
            "year",
            "gp",
            "driver",
        ],
        kind="mergesort",
    ).reset_index(drop=True)

    # ---------------------------------------------------------------
    # General driver form
    # ---------------------------------------------------------------

    df["drv_form3"] = (
        df
        .groupby("driver", sort=False)["finish_pos"]
        .transform(
            lambda values: (
                values
                .shift(1)
                .rolling(
                    window=3,
                    min_periods=1,
                )
                .mean()
            )
        )
    )

    # ---------------------------------------------------------------
    # General team form
    #
    # Calculate one team result per race first, preventing each team's
    # two drivers from being treated as separate chronological races.
    # ---------------------------------------------------------------

    team_events = (
        df
        .groupby(
            [
                "year",
                "gp",
                "date",
                "team",
            ],
            as_index=False,
            sort=False,
        )["finish_pos"]
        .mean()
        .rename(columns={
            "finish_pos": "team_event_finish",
        })
        .sort_values(
            [
                "date",
                "year",
                "gp",
                "team",
            ],
            kind="mergesort",
        )
    )

    team_events["team_form3"] = (
        team_events
        .groupby("team", sort=False)["team_event_finish"]
        .transform(
            lambda values: (
                values
                .shift(1)
                .rolling(
                    window=3,
                    min_periods=1,
                )
                .mean()
            )
        )
    )

    df = df.merge(
        team_events[
            [
                "year",
                "gp",
                "date",
                "team",
                "team_form3",
            ]
        ],
        on=[
            "year",
            "gp",
            "date",
            "team",
        ],
        how="left",
        validate="many_to_one",
    )

    # ---------------------------------------------------------------
    # Manual current priors
    # ---------------------------------------------------------------

    df["driver_skill_prior"] = (
        df["driver"]
        .map(DRIVER_SKILL_PRIOR)
        .fillna(DEFAULT_DRIVER_PRIOR)
    )

    df["team_prior_strength"] = (
        df["team"]
        .map(TEAM_BASELINE_PRIOR)
        .fillna(DEFAULT_TEAM_PRIOR)
    )

    df["rookie_flag"] = (
        df["driver"]
        .isin(ROOKIE_DRIVERS)
        .astype(int)
    )

    df["returnee_flag"] = (
        df["driver"]
        .isin(RETURNEE_DRIVERS)
        .astype(int)
    )

    # ---------------------------------------------------------------
    # Archetype rolling-form helper
    # ---------------------------------------------------------------

    def _add_archetype_forms(
        gps: set[str],
        driver_output_col: str,
        team_output_col: str,
        window: int = 3,
    ) -> None:
        """
        Add leakage-safe form for a selected circuit archetype.

        Values exist on archetype-event rows. Non-archetype rows remain
        missing and are later filled using general rolling form.
        """

        df[driver_output_col] = np.nan
        df[team_output_col] = np.nan

        mask = df["gp"].isin(gps)

        if not mask.any():
            return

        archetype_driver = (
            df.loc[
                mask,
                [
                    "driver",
                    "date",
                    "year",
                    "gp",
                    "finish_pos",
                ],
            ]
            .copy()
            .sort_values(
                [
                    "date",
                    "year",
                    "gp",
                    "driver",
                ],
                kind="mergesort",
            )
        )

        archetype_driver[driver_output_col] = (
            archetype_driver
            .groupby(
                "driver",
                sort=False,
            )["finish_pos"]
            .transform(
                lambda values: (
                    values
                    .shift(1)
                    .rolling(
                        window=window,
                        min_periods=1,
                    )
                    .mean()
                )
            )
        )

        df.loc[
            archetype_driver.index,
            driver_output_col,
        ] = archetype_driver[driver_output_col]

        archetype_team_events = (
            df.loc[mask]
            .groupby(
                [
                    "year",
                    "gp",
                    "date",
                    "team",
                ],
                as_index=False,
                sort=False,
            )["finish_pos"]
            .mean()
            .rename(columns={
                "finish_pos": "team_archetype_finish",
            })
            .sort_values(
                [
                    "date",
                    "year",
                    "gp",
                    "team",
                ],
                kind="mergesort",
            )
        )

        archetype_team_events[team_output_col] = (
            archetype_team_events
            .groupby(
                "team",
                sort=False,
            )["team_archetype_finish"]
            .transform(
                lambda values: (
                    values
                    .shift(1)
                    .rolling(
                        window=window,
                        min_periods=1,
                    )
                    .mean()
                )
            )
        )

        team_lookup = archetype_team_events[
            [
                "year",
                "gp",
                "date",
                "team",
                team_output_col,
            ]
        ]

        matched = (
            df.loc[
                mask,
                [
                    "year",
                    "gp",
                    "date",
                    "team",
                ],
            ]
            .merge(
                team_lookup,
                on=[
                    "year",
                    "gp",
                    "date",
                    "team",
                ],
                how="left",
                validate="many_to_one",
            )
        )

        df.loc[
            df.index[mask],
            team_output_col,
        ] = matched[team_output_col].to_numpy()

    # Spa belongs to both low-downforce/power-sensitive and
    # long-straight/high-speed archetypes.
    _add_archetype_forms(
        gps=LOW_DF_GPS,
        driver_output_col="lowdf_driver_form3",
        team_output_col="lowdf_team_form3",
    )

    _add_archetype_forms(
        gps=STREET_GPS,
        driver_output_col="street_driver_form3",
        team_output_col="street_team_form3",
    )

    _add_archetype_forms(
        gps=LONG_STRAIGHT_GPS,
        driver_output_col="longstraight_driver_form3",
        team_output_col="longstraight_team_form3",
    )

    # For training rows where archetype history is unavailable, fall
    # back to the driver's or team's general rolling form.
    df["lowdf_driver_form3"] = (
        df["lowdf_driver_form3"]
        .fillna(df["drv_form3"])
    )

    df["lowdf_team_form3"] = (
        df["lowdf_team_form3"]
        .fillna(df["team_form3"])
    )

    df["street_driver_form3"] = (
        df["street_driver_form3"]
        .fillna(df["drv_form3"])
    )

    df["street_team_form3"] = (
        df["street_team_form3"]
        .fillna(df["team_form3"])
    )

    df["longstraight_driver_form3"] = (
        df["longstraight_driver_form3"]
        .fillna(df["drv_form3"])
    )

    df["longstraight_team_form3"] = (
        df["longstraight_team_form3"]
        .fillna(df["team_form3"])
    )

    df = add_live_strength_adjustments(df)

    return df


# -------------------------------------------------------------------
# Merge latest forms into prediction frame
# -------------------------------------------------------------------

def merge_latest_forms(
    predict_df: pd.DataFrame,
    train_df_with_forms: pd.DataFrame,
) -> pd.DataFrame:
    """
    Merge the latest available general and archetype form into the
    upcoming-race prediction dataframe.
    """

    required_predict = {
        "driver",
        "team",
    }

    missing_predict = required_predict.difference(
        predict_df.columns
    )

    if missing_predict:
        raise ValueError(
            "merge_latest_forms prediction frame is missing: "
            f"{sorted(missing_predict)}"
        )

    required_train = {
        "driver",
        "team",
        "date",
        "gp",
    }

    missing_train = required_train.difference(
        train_df_with_forms.columns
    )

    if missing_train:
        raise ValueError(
            "merge_latest_forms training frame is missing: "
            f"{sorted(missing_train)}"
        )

    out = predict_df.copy()

    out["driver"] = (
        out["driver"]
        .astype(str)
        .str.upper()
        .str.strip()
    )

    out = _normalize_team_names(out)

    train = train_df_with_forms.copy()

    train["driver"] = (
        train["driver"]
        .astype(str)
        .str.upper()
        .str.strip()
    )

    train = _normalize_team_names(train)

    train["date"] = pd.to_datetime(
        train["date"],
        errors="coerce",
    )

    train = train.dropna(
        subset=[
            "date",
            "driver",
            "team",
        ]
    )

    # ---------------------------------------------------------------
    # General driver features
    # ---------------------------------------------------------------

    driver_general_cols = [
        "drv_form3",
        "driver_skill_prior",
        "driver_hist_strength",
        "rookie_flag",
        "returnee_flag",
    ]

    latest_driver_general = _latest_by_entity(
        train,
        entity_col="driver",
        value_cols=[
            col
            for col in driver_general_cols
            if col in train.columns
        ],
    )

    out = out.merge(
        latest_driver_general,
        on="driver",
        how="left",
        validate="many_to_one",
    )

    # ---------------------------------------------------------------
    # Driver archetype features
    # ---------------------------------------------------------------

    driver_archetypes = [
        (
            LOW_DF_GPS,
            "lowdf_driver_form3",
        ),
        (
            STREET_GPS,
            "street_driver_form3",
        ),
        (
            LONG_STRAIGHT_GPS,
            "longstraight_driver_form3",
        ),
    ]

    for gp_set, col in driver_archetypes:
        if col not in train.columns:
            out[col] = np.nan
            continue

        subset = train[
            train["gp"].isin(gp_set)
        ].copy()

        if subset.empty:
            out[col] = np.nan
            continue

        latest = _latest_by_entity(
            subset,
            entity_col="driver",
            value_cols=[col],
        )

        out = out.merge(
            latest,
            on="driver",
            how="left",
            validate="many_to_one",
        )

    # ---------------------------------------------------------------
    # General team features
    # ---------------------------------------------------------------

    team_general_cols = [
        "team_form3",
        "team_prior_strength",
        "team_hist_strength",
    ]

    latest_team_general = _latest_by_entity(
        train,
        entity_col="team",
        value_cols=[
            col
            for col in team_general_cols
            if col in train.columns
        ],
    )

    out = out.merge(
        latest_team_general,
        on="team",
        how="left",
        validate="many_to_one",
    )

    # ---------------------------------------------------------------
    # Team archetype features
    # ---------------------------------------------------------------

    team_archetypes = [
        (
            LOW_DF_GPS,
            "lowdf_team_form3",
        ),
        (
            STREET_GPS,
            "street_team_form3",
        ),
        (
            LONG_STRAIGHT_GPS,
            "longstraight_team_form3",
        ),
    ]

    for gp_set, col in team_archetypes:
        if col not in train.columns:
            out[col] = np.nan
            continue

        subset = train[
            train["gp"].isin(gp_set)
        ].copy()

        if subset.empty:
            out[col] = np.nan
            continue

        latest = _latest_by_entity(
            subset,
            entity_col="team",
            value_cols=[col],
        )

        out = out.merge(
            latest,
            on="team",
            how="left",
            validate="many_to_one",
        )

    # ---------------------------------------------------------------
    # Driver-feature fallback handling
    # ---------------------------------------------------------------

    driver_fill_specs = {
        "drv_form3": None,
        "lowdf_driver_form3": "drv_form3",
        "street_driver_form3": "drv_form3",
        "longstraight_driver_form3": "drv_form3",
        "driver_hist_strength": None,
    }

    for col, fallback_col in driver_fill_specs.items():
        _fill_from_general_or_median(
            out=out,
            train=train,
            col=col,
            general_col=fallback_col,
        )

    # Always refresh the manually frozen priors for the upcoming race.
    out["driver_skill_prior"] = (
        out["driver"]
        .map(DRIVER_SKILL_PRIOR)
        .fillna(DEFAULT_DRIVER_PRIOR)
    )

    out["rookie_flag"] = (
        out["driver"]
        .isin(ROOKIE_DRIVERS)
        .astype(int)
    )

    out["returnee_flag"] = (
        out["driver"]
        .isin(RETURNEE_DRIVERS)
        .astype(int)
    )

    # ---------------------------------------------------------------
    # Team-feature fallback handling
    # ---------------------------------------------------------------

    team_fill_specs = {
        "team_form3": None,
        "lowdf_team_form3": "team_form3",
        "street_team_form3": "team_form3",
        "longstraight_team_form3": "team_form3",
        "team_hist_strength": None,
    }

    for col, fallback_col in team_fill_specs.items():
        _fill_from_general_or_median(
            out=out,
            train=train,
            col=col,
            general_col=fallback_col,
        )

    # Always refresh the manually frozen team priors.
    out["team_prior_strength"] = (
        out["team"]
        .map(TEAM_BASELINE_PRIOR)
        .fillna(DEFAULT_TEAM_PRIOR)
    )

    out = add_live_strength_adjustments(out)

    return out


# -------------------------------------------------------------------
# Qualifying proxy
# -------------------------------------------------------------------

def add_quali_proxy(
    predict_df: pd.DataFrame,
    train_df: pd.DataFrame,
    window: int = 3,
    driver_weight: float = 0.70,
) -> pd.DataFrame:
    """
    Fill missing grid positions using recent qualifying performance.

    Proxy:
        driver_weight * driver qualifying form
        + (1 - driver_weight) * team qualifying form
    """

    if not 0.0 <= driver_weight <= 1.0:
        raise ValueError(
            "driver_weight must be between 0 and 1."
        )

    if window < 1:
        raise ValueError(
            "window must be at least 1."
        )

    out = predict_df.copy()

    if "grid_pos" not in out.columns:
        out["grid_pos"] = np.nan

    out["grid_pos"] = pd.to_numeric(
        out["grid_pos"],
        errors="coerce",
    )

    if not out["grid_pos"].isna().any():
        print(
            "All grid positions are available; "
            "qualifying proxy was not required."
        )
        return out

    required = {
        "driver",
        "team",
        "grid_pos",
        "date",
    }

    missing = required.difference(train_df.columns)

    if missing:
        raise ValueError(
            "Training dataframe for qualifying proxy is missing: "
            f"{sorted(missing)}"
        )

    base = train_df.copy()

    base["driver"] = (
        base["driver"]
        .astype(str)
        .str.upper()
        .str.strip()
    )

    base = _normalize_team_names(base)

    base["grid_pos"] = pd.to_numeric(
        base["grid_pos"],
        errors="coerce",
    )

    base["date"] = pd.to_datetime(
        base["date"],
        errors="coerce",
    )

    base = (
        base
        .dropna(
            subset=[
                "driver",
                "team",
                "grid_pos",
                "date",
            ]
        )
        .sort_values(
            "date",
            kind="mergesort",
        )
    )

    out["driver"] = (
        out["driver"]
        .astype(str)
        .str.upper()
        .str.strip()
    )

    out = _normalize_team_names(out)

    driver_proxy = (
        base
        .groupby("driver", sort=False)
        .tail(window)
        .groupby("driver", as_index=False)["grid_pos"]
        .mean()
        .rename(columns={
            "grid_pos": "driver_qual_proxy",
        })
    )

    team_proxy = (
        base
        .groupby("team", sort=False)
        .tail(window * 2)
        .groupby("team", as_index=False)["grid_pos"]
        .mean()
        .rename(columns={
            "grid_pos": "team_qual_proxy",
        })
    )

    out = out.merge(
        driver_proxy,
        on="driver",
        how="left",
        validate="many_to_one",
    )

    out = out.merge(
        team_proxy,
        on="team",
        how="left",
        validate="many_to_one",
    )

    both_available = (
        out["driver_qual_proxy"].notna()
        & out["team_qual_proxy"].notna()
    )

    out["qual_proxy"] = np.where(
        both_available,
        driver_weight * out["driver_qual_proxy"]
        + (1.0 - driver_weight) * out["team_qual_proxy"],
        out["driver_qual_proxy"].fillna(
            out["team_qual_proxy"]
        ),
    )

    # Final fallback if both the driver and constructor are new.
    global_grid_median = base["grid_pos"].median(skipna=True)

    out["qual_proxy"] = out["qual_proxy"].fillna(
        global_grid_median
    )

    missing_grid = out["grid_pos"].isna()
    missing_count = int(missing_grid.sum())

    if missing_count:
        print(
            f"Missing {missing_count} grid positions; "
            "applying qualifying proxy."
        )

        out.loc[
            missing_grid,
            "grid_pos",
        ] = out.loc[
            missing_grid,
            "qual_proxy",
        ]

    return out.drop(
        columns=[
            "driver_qual_proxy",
            "team_qual_proxy",
            "qual_proxy",
        ],
        errors="ignore",
    )