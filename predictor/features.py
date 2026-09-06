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
    HIGH_DF_TECHNICAL_GPS: set[str] = {
        "Monaco Grand Prix",
        "Hungarian Grand Prix",
        "Dutch Grand Prix",
    }


# -------------------------------------------------------------------
# Driver / team priors
#
# Italian GP / Monza configuration
#
# These represent CURRENT PRE-RACE COMPETITIVENESS, not pure immutable
# driver talent.
#
# Evidence:
# - 2026 championship standings after Zandvoort
# - Dutch GP race result
# - Dutch GP Sprint result
# - recent Hungary / Netherlands trend
# - current constructor performance
# - Monza suitability
#
# Monza-specific emphasis:
# - low-drag efficiency
# - straight-line performance
# - heavy-braking confidence
# - traction
# - racecraft in tow/DRS trains
# - tyre management
#
# IMPORTANT:
# Do not manually update these using Monza FP1/FP2/FP3/Qualifying.
# Current-weekend information should enter through:
#
# driver_2026_session_strength
# team_2026_strength
# grid_pos
#
# This prevents session information being counted twice.
# -------------------------------------------------------------------

DRIVER_SKILL_PRIOR = {

    # ---------------------------------------------------------------
    # Championship benchmark group
    # ---------------------------------------------------------------

    # Championship leader: 242 points.
    # Zandvoort P2 + Sprint P4.
    # Mercedes remains benchmark package.
    "ANT": 1.00,

    # Championship P2 on countback / tied 183 pts with Hamilton.
    # Zandvoort Sprint winner + race P3.
    # Excellent current form.
    "RUS": 0.98,

    # 183 pts.
    # Zandvoort P4 and consistently strong front-running season.
    # Ferrari should also be well suited to Monza.
    "HAM": 0.97,

    # ---------------------------------------------------------------
    # Strongest current-form challengers
    # ---------------------------------------------------------------

    # Back-to-back winner:
    # Hungary P1
    # Netherlands P1
    #
    # This is now too strong a trend to keep Norris below ~0.95.
    "NOR": 0.98,

    # Sprint P2 and race P5 at Zandvoort.
    # Strong recent Ferrari form and good Monza profile.
    "LEC": 0.96,

    # ---------------------------------------------------------------
    # Front-running group
    # ---------------------------------------------------------------

    # Zandvoort P6 and Sprint P5.
    # McLaren package is currently very strong.
    "PIA": 0.91,

    # Hungary P2 but Zandvoort Lap-1 retirement.
    #
    # We do NOT heavily punish the retirement because it provides
    # little evidence regarding underlying race pace.
    #
    # Red Bull itself is weaker than Mercedes/Ferrari/McLaren.
    "VER": 0.90,

    # ---------------------------------------------------------------
    # Upper midfield
    # ---------------------------------------------------------------

    # Zandvoort P7 in Red Bull.
    # Strong recent progression and is again driving the Red Bull
    # at Monza while Hadjar recovers.
    "LAW": 0.85,

    # Historical/current-season value retained even though Hadjar is
    # not expected to contest Monza.
    "HAD": 0.84,

    # Zandvoort P10 and Sprint P8.
    "GAS": 0.80,

    # Excellent Zandvoort P8.
    # Audi now has two drivers capable of challenging for points.
    "HUL": 0.80,

    # Rookie continues to show reasonable midfield consistency.
    "LIN": 0.77,

    # Bortoleto's Silverstone/Belgium P8s remain meaningful even though
    # Zandvoort was only P13.
    "BOR": 0.77,

    # ---------------------------------------------------------------
    # Midfield
    # ---------------------------------------------------------------

    # Zandvoort P9.
    # Aston Martin remains weak overall, but Alonso continues extracting
    # substantially more from the package.
    "ALO": 0.76,

    "COL": 0.73,

    # Returning to Racing Bulls in the current lineup.
    # Zandvoort P11 was respectable given the late substitution.
    "TSU": 0.72,

    "BEA": 0.70,

    # Monza can reward Williams' straight-line efficiency,
    # but current-season results remain weak.
    "SAI": 0.70,
    "ALB": 0.68,

    "OCO": 0.67,

    # ---------------------------------------------------------------
    # Lower current-performance group
    # ---------------------------------------------------------------

    "STR": 0.62,

    # Cadillac remains scoreless.
    "BOT": 0.59,
    "PER": 0.58,
}


DEFAULT_DRIVER_PRIOR = 0.72


ROOKIE_DRIVERS = {
    "LIN",
}


RETURNEE_DRIVERS = {
    "BOT",
    "PER",
}


# -------------------------------------------------------------------
# Team name normalization
# -------------------------------------------------------------------

TEAM_ALIAS = {

    # Audi / historical Sauber names
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
# Official post-Zandvoort standings:
#
# Mercedes          425
# Ferrari           338
# McLaren           263
# Red Bull Racing   186
# Racing Bulls       66
# Alpine             63
# Haas               21
# Audi               16
# Williams           11
# Aston Martin        3
# Cadillac            0
#
# Monza circuit suitability is only a secondary adjustment.
# -------------------------------------------------------------------

TEAM_BASELINE_PRIOR = {

    # Championship benchmark.
    "Mercedes": 1.00,

    # Strong season, currently P2.
    # Monza's braking/traction/efficiency profile should be competitive.
    "Ferrari": 0.96,

    # Very strong recent trajectory:
    # Hungary win + Zandvoort win
    # 43-point Zandvoort weekend.
    "McLaren": 0.94,

    # Clearly behind the leading three constructors.
    # Zandvoort produced only nine team points.
    "Red Bull Racing": 0.84,

    # ---------------------------------------------------------------
    # Upper midfield
    # ---------------------------------------------------------------

    "Racing Bulls": 0.74,
    "Alpine": 0.72,

    # Recent Audi trajectory is substantially better than early season.
    "Audi": 0.68,

    # ---------------------------------------------------------------
    # Lower midfield
    # ---------------------------------------------------------------

    "Haas F1 Team": 0.61,

    # Monza's power-sensitive layout may help relative to high-DF tracks,
    # but results remain weak.
    "Williams": 0.59,

    "Aston Martin": 0.54,

    # ---------------------------------------------------------------
    # Rear
    # ---------------------------------------------------------------

    "Cadillac": 0.45,
}


DEFAULT_TEAM_PRIOR = 0.69


# -------------------------------------------------------------------
# General helpers
# -------------------------------------------------------------------

def _ensure_numeric(
    df: pd.DataFrame,
    cols: list[str],
) -> None:
    """
    Convert available columns to numeric values in place.
    """

    for col in cols:
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col],
                errors="coerce",
            )


def _normalize_team_names(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Normalize historical and current constructor names.
    """

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
    Convert lower-is-better finishing-position form into
    higher-is-better normalized strength.

    Better recent finishing average -> closer to 1.
    Worse recent finishing average -> closer to 0.
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
    Return latest available non-null values for each entity.

    Each feature is resolved independently because an entity's latest
    low-downforce race may not be its latest race overall.
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
            subset=[
                entity_col,
                col,
            ],
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
            .groupby(
                entity_col,
                as_index=False,
                sort=False,
            )
            .tail(1)[
                [
                    entity_col,
                    col,
                ]
            ]
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

    1. general recent form
    2. training median
    """

    if col not in out.columns:
        out[col] = np.nan

    if (
        general_col is not None
        and general_col in out.columns
        and col != general_col
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
            out[col] = out[col].fillna(
                median
            )


# -------------------------------------------------------------------
# Manual priors
# -------------------------------------------------------------------

def add_driver_skill_prior(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Add current driver competitiveness and status flags.
    """

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
    """
    Add current constructor competitiveness.
    """

    out = _normalize_team_names(df)

    if "team" not in out.columns:

        out["team_prior_strength"] = (
            DEFAULT_TEAM_PRIOR
        )

        return out

    out["team_prior_strength"] = (
        out["team"]
        .map(TEAM_BASELINE_PRIOR)
        .fillna(DEFAULT_TEAM_PRIOR)
        .astype(float)
    )

    return out


# -------------------------------------------------------------------
# Historical + live session strength blending
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

    driver_hist_strength
    team_hist_strength
    driver_strength_blend_2026
    team_strength_blend_2026

    Monza is strongly setup-sensitive because of:

    - drag level
    - top speed
    - energy deployment
    - braking stability
    - traction
    - rear tyre temperature
    - tow effectiveness

    Weekend data is useful, but live strength remains limited to 55%
    because practice programmes, fuel loads and tyre programmes differ.

    grid_pos independently captures qualifying performance.
    """

    if not np.isclose(
        hist_team_weight + live_team_weight,
        1.0,
    ):
        raise ValueError(
            "Team historical/live weights must sum to 1."
        )

    if not np.isclose(
        hist_driver_weight + live_driver_weight,
        1.0,
    ):
        raise ValueError(
            "Driver historical/live weights must sum to 1."
        )

    out = _normalize_team_names(
        df.copy()
    )

    # ---------------------------------------------------------------
    # Historical driver strength
    # ---------------------------------------------------------------

    if "drv_form3" in out.columns:

        out["driver_hist_strength"] = (
            _inverse_minmax_strength(
                out["drv_form3"]
            )
        )

    else:

        out["driver_hist_strength"] = np.nan

    # ---------------------------------------------------------------
    # Historical team strength
    # ---------------------------------------------------------------

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

    # ---------------------------------------------------------------
    # Driver live blend
    # ---------------------------------------------------------------

    if "driver_2026_session_strength" in out.columns:

        driver_live = pd.to_numeric(
            out["driver_2026_session_strength"],
            errors="coerce",
        )

        out["driver_strength_blend_2026"] = np.where(

            driver_history.notna()
            & driver_live.notna(),

            (
                hist_driver_weight
                * driver_history
                +
                live_driver_weight
                * driver_live
            ),

            driver_history.fillna(
                driver_live
            ),
        )

    else:

        out["driver_strength_blend_2026"] = (
            driver_history
        )


    team_history = pd.to_numeric(
        out["team_hist_strength"],
        errors="coerce",
    )

    # ---------------------------------------------------------------
    # Team live blend
    # ---------------------------------------------------------------

    if "team_2026_strength" in out.columns:

        team_live = pd.to_numeric(
            out["team_2026_strength"],
            errors="coerce",
        )

        out["team_strength_blend_2026"] = np.where(

            team_history.notna()
            & team_live.notna(),

            (
                hist_team_weight
                * team_history
                +
                live_team_weight
                * team_live
            ),

            team_history.fillna(
                team_live
            ),
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
    """
    Add circuit, strategy, volatility and weather features.
    """

    if "gp" not in df.columns:
        raise ValueError(
            "add_circuit_context_df requires a 'gp' column."
        )

    def _lookup(
        gp_value: object,
    ) -> pd.Series:

        gp = str(
            gp_value
        ).strip()

        sc_prob, vsc_prob, pit_loss = (
            CIRCUIT_VOL.get(
                gp,
                (
                    DEFAULT_SC,
                    DEFAULT_VSC,
                    DEFAULT_PIT_LOSS,
                ),
            )
        )

        extras = dict(
            CIRCUIT_EXTRAS.get(
                gp,
                CIRCUIT_EXTRAS.get(
                    "_default",
                    {},
                ),
            )
        )

        extras.setdefault(
            "is_low_df",
            float(
                gp in LOW_DF_GPS
            ),
        )

        extras.setdefault(
            "is_street",
            float(
                gp in STREET_GPS
            ),
        )

        is_long_straight = (
            gp in LONG_STRAIGHT_GPS
        )

        if "long_straight_index" not in extras:

            if extras["is_low_df"]:

                extras[
                    "long_straight_index"
                ] = 0.85

            elif is_long_straight:

                extras[
                    "long_straight_index"
                ] = 0.70

            else:

                extras[
                    "long_straight_index"
                ] = 0.50


        extras.setdefault(
            "tow_importance",
            (
                0.65
                if is_long_straight
                else 0.50
            ),
        )

        extras.setdefault(
            "overtake_index",
            (
                0.58
                if is_long_straight
                else 0.50
            ),
        )

        extras.setdefault(
            "braking_intensity",
            0.55,
        )

        extras.setdefault(
            "warmup_penalty",
            0.07,
        )

        extras.setdefault(
            "expected_stops",
            2.0,
        )

        extras.setdefault(
            "deg_rate",
            0.65,
        )

        extras.setdefault(
            "stint_len_typical",
            np.nan,
        )

        return pd.Series({
            "sc_prob": sc_prob,
            "vsc_prob": vsc_prob,
            "pit_loss": pit_loss,
            **extras,
        })

    base = (
        df
        .reset_index(drop=True)
        .copy()
    )

    context = (
        base["gp"]
        .apply(_lookup)
        .reset_index(drop=True)
    )

    # Prevent duplicate circuit columns when context is accidentally
    # added more than once.
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
        [
            base,
            context,
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
    Create general and archetype rolling form.

    shift(1) is applied before every rolling window, preventing the
    current race result from predicting itself.
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


    df = _normalize_team_names(
        df
    )


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
    ).reset_index(
        drop=True
    )


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
    # One team observation per race prevents the two drivers being
    # interpreted as two independent chronological events.
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
        .rename(
            columns={
                "finish_pos":
                    "team_event_finish",
            }
        )
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
    # Frozen pre-Monza manual priors
    # ---------------------------------------------------------------

    df["driver_skill_prior"] = (
        df["driver"]
        .map(
            DRIVER_SKILL_PRIOR
        )
        .fillna(
            DEFAULT_DRIVER_PRIOR
        )
    )


    df["team_prior_strength"] = (
        df["team"]
        .map(
            TEAM_BASELINE_PRIOR
        )
        .fillna(
            DEFAULT_TEAM_PRIOR
        )
    )


    df["rookie_flag"] = (
        df["driver"]
        .isin(
            ROOKIE_DRIVERS
        )
        .astype(int)
    )


    df["returnee_flag"] = (
        df["driver"]
        .isin(
            RETURNEE_DRIVERS
        )
        .astype(int)
    )


    # ---------------------------------------------------------------
    # Archetype rolling helper
    # ---------------------------------------------------------------

    def _add_archetype_forms(
        gps: set[str],
        driver_output_col: str,
        team_output_col: str,
        window: int = 3,
    ) -> None:

        df[
            driver_output_col
        ] = np.nan

        df[
            team_output_col
        ] = np.nan


        if not gps:
            return


        mask = df[
            "gp"
        ].isin(
            gps
        )


        if not mask.any():
            return


        # -----------------------------------------------------------
        # Driver archetype form
        # -----------------------------------------------------------

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


        driver_subset[
            driver_output_col
        ] = (
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
        ] = driver_subset[
            driver_output_col
        ]


        # -----------------------------------------------------------
        # Team archetype form
        # -----------------------------------------------------------

        team_subset = (
            df.loc[
                mask
            ]
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
            .rename(
                columns={
                    "finish_pos":
                        "team_archetype_finish"
                }
            )
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


        team_subset[
            team_output_col
        ] = (
            team_subset
            .groupby(
                "team",
                sort=False,
            )[
                "team_archetype_finish"
            ]
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
        ] = matched[
            team_output_col
        ].to_numpy()


    # ---------------------------------------------------------------
    # Low-downforce / power-sensitive form
    #
    # PRIMARY Monza archetype.
    # ---------------------------------------------------------------

    _add_archetype_forms(
        gps=LOW_DF_GPS,
        driver_output_col="lowdf_driver_form3",
        team_output_col="lowdf_team_form3",
    )


    # ---------------------------------------------------------------
    # Street form
    #
    # Generated for historical consistency but not used as a primary
    # Monza model feature.
    # ---------------------------------------------------------------

    _add_archetype_forms(
        gps=STREET_GPS,
        driver_output_col="street_driver_form3",
        team_output_col="street_team_form3",
    )


    # ---------------------------------------------------------------
    # Long-straight / power-sensitive form
    #
    # PRIMARY Monza archetype.
    # ---------------------------------------------------------------

    _add_archetype_forms(
        gps=LONG_STRAIGHT_GPS,
        driver_output_col="longstraight_driver_form3",
        team_output_col="longstraight_team_form3",
    )


    # ---------------------------------------------------------------
    # High-downforce technical form
    #
    # Retained for future races / historical feature availability.
    # It should NOT be included in the Monza FEATS list.
    # ---------------------------------------------------------------

    _add_archetype_forms(
        gps=HIGH_DF_TECHNICAL_GPS,
        driver_output_col="highdf_driver_form3",
        team_output_col="highdf_team_form3",
    )


    # ---------------------------------------------------------------
    # Fallback to general recent form
    # ---------------------------------------------------------------

    driver_archetype_cols = [
        "lowdf_driver_form3",
        "street_driver_form3",
        "longstraight_driver_form3",
        "highdf_driver_form3",
    ]


    for col in driver_archetype_cols:

        df[col] = (
            df[col]
            .fillna(
                df["drv_form3"]
            )
        )


    team_archetype_cols = [
        "lowdf_team_form3",
        "street_team_form3",
        "longstraight_team_form3",
        "highdf_team_form3",
    ]


    for col in team_archetype_cols:

        df[col] = (
            df[col]
            .fillna(
                df["team_form3"]
            )
        )


    df = add_live_strength_adjustments(
        df
    )


    return df


# -------------------------------------------------------------------
# Merge latest forms into prediction frame
# -------------------------------------------------------------------

def merge_latest_forms(
    predict_df: pd.DataFrame,
    train_df_with_forms: pd.DataFrame,
) -> pd.DataFrame:

    """
    Merge latest general and archetype form into the Italian GP
    prediction dataframe.
    """

    required_predict = {
        "driver",
        "team",
    }


    missing_predict = (
        required_predict.difference(
            predict_df.columns
        )
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


    missing_train = (
        required_train.difference(
            train_df_with_forms.columns
        )
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


    out = _normalize_team_names(
        out
    )


    train = (
        train_df_with_forms
        .copy()
    )


    train["driver"] = (
        train["driver"]
        .astype(str)
        .str.upper()
        .str.strip()
    )


    train = _normalize_team_names(
        train
    )


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


    latest_driver = (
        _latest_by_entity(
            train,
            entity_col="driver",
            value_cols=[
                col
                for col
                in driver_general_cols
                if col in train.columns
            ],
        )
    )


    out = out.merge(
        latest_driver,
        on="driver",
        how="left",
        validate="many_to_one",
    )


    # ---------------------------------------------------------------
    # Driver archetypes
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
            train["gp"].isin(
                gp_set
            )
        ].copy()


        if subset.empty:

            out[col] = np.nan
            continue


        latest = _latest_by_entity(
            subset,
            entity_col="driver",
            value_cols=[
                col
            ],
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


    latest_team = (
        _latest_by_entity(
            train,
            entity_col="team",
            value_cols=[
                col
                for col
                in team_general_cols
                if col in train.columns
            ],
        )
    )


    out = out.merge(
        latest_team,
        on="team",
        how="left",
        validate="many_to_one",
    )


    # ---------------------------------------------------------------
    # Team archetypes
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
            train["gp"].isin(
                gp_set
            )
        ].copy()


        if subset.empty:

            out[col] = np.nan
            continue


        latest = _latest_by_entity(
            subset,
            entity_col="team",
            value_cols=[
                col
            ],
        )


        out = out.merge(
            latest,
            on="team",
            how="left",
            validate="many_to_one",
        )


    # ---------------------------------------------------------------
    # Driver fallback handling
    # ---------------------------------------------------------------

    driver_fill_specs = {

        "drv_form3":
            None,

        "lowdf_driver_form3":
            "drv_form3",

        "street_driver_form3":
            "drv_form3",

        "longstraight_driver_form3":
            "drv_form3",

        "highdf_driver_form3":
            "drv_form3",

        "driver_hist_strength":
            None,
    }


    for col, fallback_col in (
        driver_fill_specs.items()
    ):

        _fill_from_general_or_median(
            out=out,
            train=train,
            col=col,
            general_col=fallback_col,
        )


    # Always refresh current priors for target race.
    out["driver_skill_prior"] = (
        out["driver"]
        .map(
            DRIVER_SKILL_PRIOR
        )
        .fillna(
            DEFAULT_DRIVER_PRIOR
        )
    )


    out["rookie_flag"] = (
        out["driver"]
        .isin(
            ROOKIE_DRIVERS
        )
        .astype(int)
    )


    out["returnee_flag"] = (
        out["driver"]
        .isin(
            RETURNEE_DRIVERS
        )
        .astype(int)
    )


    # ---------------------------------------------------------------
    # Team fallback handling
    # ---------------------------------------------------------------

    team_fill_specs = {

        "team_form3":
            None,

        "lowdf_team_form3":
            "team_form3",

        "street_team_form3":
            "team_form3",

        "longstraight_team_form3":
            "team_form3",

        "highdf_team_form3":
            "team_form3",

        "team_hist_strength":
            None,
    }


    for col, fallback_col in (
        team_fill_specs.items()
    ):

        _fill_from_general_or_median(
            out=out,
            train=train,
            col=col,
            general_col=fallback_col,
        )


    out["team_prior_strength"] = (
        out["team"]
        .map(
            TEAM_BASELINE_PRIOR
        )
        .fillna(
            DEFAULT_TEAM_PRIOR
        )
    )


    out = add_live_strength_adjustments(
        out
    )


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

    proxy =
        driver_weight * driver recent qualifying
        +
        (1-driver_weight) * team recent qualifying

    Monza is more overtaking-friendly than Zandvoort or Monaco, so the
    starting grid is slightly less deterministic, but it remains one of
    the strongest features in a pre-race model.

    Once the official grid exists, this proxy MUST NOT be used.
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


    missing_predict = (
        required_predict.difference(
            predict_df.columns
        )
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


    if not out[
        "grid_pos"
    ].isna().any():

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


    missing_train = (
        required_train.difference(
            train_df.columns
        )
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


    base = _normalize_team_names(
        base
    )


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


    out = _normalize_team_names(
        out
    )


    # ---------------------------------------------------------------
    # Driver qualifying proxy
    # ---------------------------------------------------------------

    driver_proxy = (
        base
        .groupby(
            "driver",
            sort=False,
            group_keys=False,
        )
        .tail(
            window
        )
        .groupby(
            "driver",
            as_index=False,
        )["grid_pos"]
        .mean()
        .rename(
            columns={
                "grid_pos":
                    "driver_qual_proxy",
            }
        )
    )


    # ---------------------------------------------------------------
    # Team qualifying proxy
    #
    # Approx. two drivers per race -> 2 * window observations.
    # ---------------------------------------------------------------

    team_proxy = (
        base
        .groupby(
            "team",
            sort=False,
            group_keys=False,
        )
        .tail(
            window * 2
        )
        .groupby(
            "team",
            as_index=False,
        )["grid_pos"]
        .mean()
        .rename(
            columns={
                "grid_pos":
                    "team_qual_proxy",
            }
        )
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
        &
        team_values.notna()
    )


    out["qual_proxy"] = np.where(

        both_available,

        (
            driver_weight
            * driver_values
            +
            (
                1.0
                - driver_weight
            )
            * team_values
        ),

        driver_values.fillna(
            team_values
        ),
    )


    global_grid_median = (
        base[
            "grid_pos"
        ]
        .median(
            skipna=True
        )
    )


    out["qual_proxy"] = (
        out["qual_proxy"]
        .fillna(
            global_grid_median
        )
    )


    missing_grid = (
        out["grid_pos"]
        .isna()
    )


    missing_count = int(
        missing_grid.sum()
    )


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