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

try:
    from .config import HIGH_DF_TECHNICAL_GPS
except Exception:
    # Safe fallback until this set is added to config.py.
    HIGH_DF_TECHNICAL_GPS: set[str] = {
        "Hungarian Grand Prix",
        "Monaco Grand Prix",
    }


# -------------------------------------------------------------------
# Driver and team priors
#
# Hungarian GP / Hungaroring configuration
#
# These are current pre-race competitiveness priors, not pure talent
# ratings. They use:
#
# - 2026 championship position and points
# - recent races through the Belgian Grand Prix
# - team package strength
# - qualifying and race consistency
# - Hungary suitability
# - high-downforce and technical-circuit performance
# - tyre management and traffic management
#
# Freeze these before incorporating Hungarian GP qualifying or race data.
# -------------------------------------------------------------------

DRIVER_SKILL_PRIOR = {
    # ---------------------------------------------------------------
    # Leading championship group
    # ---------------------------------------------------------------

    # Championship leader, six wins and Belgian GP winner.
    # Mercedes is currently the strongest package.
    "ANT": 1.00,

    # Championship P2, multiple podiums and strong technical-track record.
    # Finished fourth in Belgium after a time penalty.
    "HAM": 0.97,

    # Championship P3. Austria winner and consistently competitive,
    # although Belgium ended with a Lap 1 retirement.
    "RUS": 0.95,

    # Consecutive strong races: Silverstone win and Belgium P2.
    # Ferrari's high-downforce pace gives him strong Hungary upside.
    "LEC": 0.96,

    # ---------------------------------------------------------------
    # Leading challengers
    # ---------------------------------------------------------------

    # Championship P5. Strong overall consistency and technical-track pace.
    "NOR": 0.91,

    # Championship P6 and Belgium P5.
    # Hungary should suit McLaren better than Spa.
    "PIA": 0.90,

    # Belgium podium and strong driver-level ability.
    # Current Red Bull package is below Mercedes and Ferrari.
    "VER": 0.92,

    # Championship P8 and recovered from the back to P6 in Belgium.
    "HAD": 0.87,

    # ---------------------------------------------------------------
    # Upper midfield
    # ---------------------------------------------------------------

    # Alpine's highest-ranked driver, though Belgium produced no points.
    "GAS": 0.81,

    # Championship P10. Strong recent consistency before Belgium P12.
    "LAW": 0.81,

    # Rookie with consecutive points at Silverstone and Belgium.
    "LIN": 0.80,

    # Belgium P10 and championship P12.
    "COL": 0.78,

    # Audi's only points scorer, with consecutive P8 finishes.
    "BOR": 0.79,

    # Championship P13, but Belgium P14 weakens recent form.
    "BEA": 0.75,

    # ---------------------------------------------------------------
    # Lower midfield
    # ---------------------------------------------------------------

    "SAI": 0.72,
    "ALB": 0.71,
    "OCO": 0.69,
    "HUL": 0.69,

    # Aston Martin remains weak, but Hungary may suit Alonso's driving
    # and the team's high-downforce upgrades better than Spa.
    "ALO": 0.71,

    # ---------------------------------------------------------------
    # Rear group
    # ---------------------------------------------------------------

    "STR": 0.62,
    "BOT": 0.64,
    "PER": 0.61,
}

DEFAULT_DRIVER_PRIOR = 0.73


ROOKIE_DRIVERS = {
    "LIN",
}


RETURNEE_DRIVERS = {
    "BOT",
    "PER",
}


# -------------------------------------------------------------------
# Team-name normalization
# -------------------------------------------------------------------

TEAM_ALIAS = {
    # Audi and historical Sauber names
    "Audi": "Audi",
    "Audi F1 Team": "Audi",
    "Sauber": "Audi",
    "Sauber Motorsport": "Audi",
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
    "Alpine F1 Team": "Alpine",
    "BWT Alpine F1 Team": "Alpine",
}


# -------------------------------------------------------------------
# Team current-performance priors
#
# Championship order after Belgium:
# Mercedes, Ferrari, McLaren, Red Bull, Alpine/Racing Bulls,
# Haas, Williams, Audi, Aston Martin, Cadillac.
#
# Hungary-specific suitability is only a small adjustment. Championship
# and recent race evidence remain the main basis.
# -------------------------------------------------------------------

TEAM_BASELINE_PRIOR = {
    # 358 points and clear championship leader.
    "Mercedes": 1.00,

    # 285 points and consecutive strong races.
    # High-downforce Hungary should suit Ferrari.
    "Ferrari": 0.96,

    # 195 points. Hungary may suit McLaren better than Spa did.
    "McLaren": 0.90,

    # 151 points. Strong driver performance but inconsistent package.
    "Red Bull Racing": 0.84,

    # Both teams have 61 points.
    "Alpine": 0.73,
    "Racing Bulls": 0.73,

    # 21 points and inconsistent recent performance.
    "Haas F1 Team": 0.64,

    # 11 points and weak recent races.
    "Williams": 0.58,

    # 10 points, all from Bortoleto, with recent upward form.
    "Audi": 0.60,

    # Only one point, but Hungary-specific upgrades could improve the
    # package relative to the raw championship position.
    "Aston Martin": 0.53,

    # Scoreless and two weak Belgian GP results.
    "Cadillac": 0.46,
}

DEFAULT_TEAM_PRIOR = 0.69


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
            df[col] = pd.to_numeric(
                df[col],
                errors="coerce",
            )


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

    Best recent average finish approaches 1.0.
    Worst recent average finish approaches 0.0.
    """

    values = pd.to_numeric(
        series,
        errors="coerce",
    )

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

    return 1.0 - (
        (values - minimum)
        / (maximum - minimum)
    )


def _latest_by_entity(
    df: pd.DataFrame,
    entity_col: str,
    value_cols: list[str],
) -> pd.DataFrame:
    """
    Return the latest available non-null value for every entity-feature
    combination.

    Each feature is resolved independently, which is important because
    the latest technical-circuit observation may not be the latest race
    overall.
    """

    if entity_col not in df.columns:
        raise ValueError(
            f"_latest_by_entity requires column '{entity_col}'."
        )

    result = pd.DataFrame({
        entity_col: sorted(
            df[entity_col]
            .dropna()
            .unique()
        )
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
                ["date"],
                kind="mergesort",
            )

        latest = (
            valid
            .groupby(
                entity_col,
                as_index=False,
                sort=False,
            )
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
    Fill prediction features in this order:

    1. corresponding general form
    2. historical training median
    """

    if col not in out.columns:
        out[col] = np.nan

    if (
        general_col is not None
        and general_col in out.columns
        and general_col != col
    ):
        out[col] = out[col].fillna(
            out[general_col]
        )

    if (
        out[col].isna().any()
        and col in train.columns
    ):
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
    """Add current driver competitiveness and status flags."""

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
        .astype(float)
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
    """Add current constructor competitiveness prior."""

    out = _normalize_team_names(df)

    if "team" not in out.columns:
        out["team_prior_strength"] = DEFAULT_TEAM_PRIOR
        return out

    out["team_prior_strength"] = (
        out["team"]
        .map(TEAM_BASELINE_PRIOR)
        .fillna(DEFAULT_TEAM_PRIOR)
        .astype(float)
    )

    return out


# -------------------------------------------------------------------
# Historical and live-session strength blending
# -------------------------------------------------------------------

def add_live_strength_adjustments(
    df: pd.DataFrame,
    hist_team_weight: float = 0.45,
    live_team_weight: float = 0.55,
    hist_driver_weight: float = 0.45,
    live_driver_weight: float = 0.55,
) -> pd.DataFrame:
    """
    Create:

    - driver_hist_strength
    - team_hist_strength
    - driver_strength_blend_2026
    - team_strength_blend_2026

    Hungary is highly setup-sensitive, but practice results can be
    distorted by fuel load, tyre age, engine mode and traffic.

    Live performance therefore receives 55%, rather than the more
    aggressive 60-75% used previously.
    """

    if not np.isclose(
        hist_team_weight + live_team_weight,
        1.0,
    ):
        raise ValueError(
            "Team history and live weights must sum to 1."
        )

    if not np.isclose(
        hist_driver_weight + live_driver_weight,
        1.0,
    ):
        raise ValueError(
            "Driver history and live weights must sum to 1."
        )

    out = _normalize_team_names(df.copy())

    if "drv_form3" in out.columns:
        out["driver_hist_strength"] = (
            _inverse_minmax_strength(
                out["drv_form3"]
            )
        )
    else:
        out["driver_hist_strength"] = np.nan

    if "team_form3" in out.columns:
        out["team_hist_strength"] = (
            _inverse_minmax_strength(
                out["team_form3"]
            )
        )
    else:
        out["team_hist_strength"] = np.nan

    driver_history = pd.to_numeric(
        out["driver_hist_strength"],
        errors="coerce",
    )

    if "driver_2026_session_strength" in out.columns:
        driver_live = pd.to_numeric(
            out["driver_2026_session_strength"],
            errors="coerce",
        )

        out["driver_strength_blend_2026"] = np.where(
            driver_history.notna() & driver_live.notna(),
            (
                hist_driver_weight * driver_history
                + live_driver_weight * driver_live
            ),
            driver_history.fillna(driver_live),
        )
    else:
        out["driver_strength_blend_2026"] = (
            driver_history
        )

    team_history = pd.to_numeric(
        out["team_hist_strength"],
        errors="coerce",
    )

    if "team_2026_strength" in out.columns:
        team_live = pd.to_numeric(
            out["team_2026_strength"],
            errors="coerce",
        )

        out["team_strength_blend_2026"] = np.where(
            team_history.notna() & team_live.notna(),
            (
                hist_team_weight * team_history
                + live_team_weight * team_live
            ),
            team_history.fillna(team_live),
        )
    else:
        out["team_strength_blend_2026"] = (
            team_history
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

    def _lookup(gp_value: object) -> pd.Series:
        gp = str(gp_value).strip()

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

        is_long_straight = (
            gp in LONG_STRAIGHT_GPS
        )

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

    base = df.reset_index(drop=True).copy()

    context = (
        base["gp"]
        .apply(_lookup)
        .reset_index(drop=True)
    )

    # Prevent duplicate feature columns if context is added twice.
    overlapping = [
        col
        for col in context.columns
        if col in base.columns
    ]

    if overlapping:
        base = base.drop(
            columns=overlapping
        )

    out = pd.concat(
        [base, context],
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

    _ensure_numeric(
        out,
        numeric_cols,
    )

    return out


# -------------------------------------------------------------------
# Leakage-safe rolling forms
# -------------------------------------------------------------------

def add_driver_team_form(
    full_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Create leakage-safe general and circuit-archetype rolling forms.

    Every rolling calculation uses shift(1), so the current race result
    cannot be used to predict the same race.
    """

    required = {
        "year",
        "gp",
        "date",
        "driver",
        "team",
        "finish_pos",
    }

    missing = required.difference(
        full_df.columns
    )

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
        .groupby(
            "driver",
            sort=False,
        )["finish_pos"]
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
    # First reduce each team-race to one observation. Otherwise each
    # team's two drivers would incorrectly count as separate races.
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
        .groupby(
            "team",
            sort=False,
        )["team_event_finish"]
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
    # Frozen pre-Hungary manual priors
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
        Add driver and team form using only events in one circuit group.
        """

        df[driver_output_col] = np.nan
        df[team_output_col] = np.nan

        if not gps:
            return

        mask = df["gp"].isin(gps)

        if not mask.any():
            return

        # Driver form within the selected archetype.
        driver_subset = (
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

        driver_subset[driver_output_col] = (
            driver_subset
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
            driver_subset.index,
            driver_output_col,
        ] = driver_subset[driver_output_col]

        # Team form within the selected archetype.
        team_subset = (
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

        team_subset[team_output_col] = (
            team_subset
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

        lookup = team_subset[
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
                lookup,
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

    # Existing archetypes
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

    # Primary Hungarian GP archetype.
    _add_archetype_forms(
        gps=HIGH_DF_TECHNICAL_GPS,
        driver_output_col="highdf_driver_form3",
        team_output_col="highdf_team_form3",
    )

    # Use general form where an archetype-specific history is absent.
    driver_archetype_cols = [
        "lowdf_driver_form3",
        "street_driver_form3",
        "longstraight_driver_form3",
        "highdf_driver_form3",
    ]

    for col in driver_archetype_cols:
        df[col] = df[col].fillna(
            df["drv_form3"]
        )

    team_archetype_cols = [
        "lowdf_team_form3",
        "street_team_form3",
        "longstraight_team_form3",
        "highdf_team_form3",
    ]

    for col in team_archetype_cols:
        df[col] = df[col].fillna(
            df["team_form3"]
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
    Merge latest general and archetype form into the Hungary prediction
    dataframe.
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
        "driver_hist_strength",
    ]

    latest_driver = _latest_by_entity(
        train,
        entity_col="driver",
        value_cols=[
            col
            for col in driver_general_cols
            if col in train.columns
        ],
    )

    out = out.merge(
        latest_driver,
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
        (
            HIGH_DF_TECHNICAL_GPS,
            "highdf_driver_form3",
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
        "team_hist_strength",
    ]

    latest_team = _latest_by_entity(
        train,
        entity_col="team",
        value_cols=[
            col
            for col in team_general_cols
            if col in train.columns
        ],
    )

    out = out.merge(
        latest_team,
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
        (
            HIGH_DF_TECHNICAL_GPS,
            "highdf_team_form3",
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
    # Driver feature fallbacks
    # ---------------------------------------------------------------

    driver_fill_specs = {
        "drv_form3": None,
        "lowdf_driver_form3": "drv_form3",
        "street_driver_form3": "drv_form3",
        "longstraight_driver_form3": "drv_form3",
        "highdf_driver_form3": "drv_form3",
        "driver_hist_strength": None,
    }

    for col, fallback_col in driver_fill_specs.items():
        _fill_from_general_or_median(
            out=out,
            train=train,
            col=col,
            general_col=fallback_col,
        )

    # Refresh priors rather than carrying old pre-Belgium values.
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
    # Team feature fallbacks
    # ---------------------------------------------------------------

    team_fill_specs = {
        "team_form3": None,
        "lowdf_team_form3": "team_form3",
        "street_team_form3": "team_form3",
        "longstraight_team_form3": "team_form3",
        "highdf_team_form3": "team_form3",
        "team_hist_strength": None,
    }

    for col, fallback_col in team_fill_specs.items():
        _fill_from_general_or_median(
            out=out,
            train=train,
            col=col,
            general_col=fallback_col,
        )

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
        driver_weight * recent driver qualifying average
        + (1 - driver_weight) * recent team qualifying average

    This is only for pre-qualifying operation. Once the official
    Hungary grid is available, use the real grid.
    """

    if not 0.0 <= driver_weight <= 1.0:
        raise ValueError(
            "driver_weight must be between 0 and 1."
        )

    if window < 1:
        raise ValueError(
            "window must be at least 1."
        )

    required_predict = {
        "driver",
        "team",
    }

    missing_predict = required_predict.difference(
        predict_df.columns
    )

    if missing_predict:
        raise ValueError(
            "Prediction dataframe is missing: "
            f"{sorted(missing_predict)}"
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

    required_train = {
        "driver",
        "team",
        "grid_pos",
        "date",
    }

    missing_train = required_train.difference(
        train_df.columns
    )

    if missing_train:
        raise ValueError(
            "Training dataframe for qualifying proxy is missing: "
            f"{sorted(missing_train)}"
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
            [
                "date",
                "driver",
            ],
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
        .groupby(
            "driver",
            sort=False,
            group_keys=False,
        )
        .tail(window)
        .groupby(
            "driver",
            as_index=False,
        )["grid_pos"]
        .mean()
        .rename(columns={
            "grid_pos": "driver_qual_proxy",
        })
    )

    # Two drivers per team means roughly 2 * window rows correspond to
    # the same number of recent race weekends.
    team_proxy = (
        base
        .groupby(
            "team",
            sort=False,
            group_keys=False,
        )
        .tail(window * 2)
        .groupby(
            "team",
            as_index=False,
        )["grid_pos"]
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

    driver_values = pd.to_numeric(
        out["driver_qual_proxy"],
        errors="coerce",
    )

    team_values = pd.to_numeric(
        out["team_qual_proxy"],
        errors="coerce",
    )

    both_available = (
        driver_values.notna()
        & team_values.notna()
    )

    out["qual_proxy"] = np.where(
        both_available,
        (
            driver_weight * driver_values
            + (1.0 - driver_weight) * team_values
        ),
        driver_values.fillna(team_values),
    )

    global_grid_median = (
        base["grid_pos"]
        .median(skipna=True)
    )

    out["qual_proxy"] = (
        out["qual_proxy"]
        .fillna(global_grid_median)
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