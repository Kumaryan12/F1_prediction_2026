from pathlib import Path
from typing import Dict, Tuple


# -------------------------------------------------------------------
# Cache configuration
# -------------------------------------------------------------------

CACHE_DIR: Path = Path(__file__).resolve().parent / "f1cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


# Historical training seasons
HIST_YEARS = list(range(2023, 2026))


# Default fallback values
DEFAULT_SC = 0.50
DEFAULT_VSC = 0.50
DEFAULT_PIT_LOSS = 21.0


# -------------------------------------------------------------------
# Race volatility configuration
#
# Tuple:
# (
#     Safety Car probability,
#     Virtual Safety Car probability,
#     estimated pit-loss seconds,
# )
# -------------------------------------------------------------------

CIRCUIT_VOL: Dict[str, Tuple[float, float, float]] = {
    "Dutch Grand Prix": (0.48, 0.32, 21.0),
}


# -------------------------------------------------------------------
# Completed 2026 races available for training/form generation
#
# Hungary is now completed and can be included.
# Dutch GP is the active prediction target and should remain excluded
# until the race has actually finished.
# -------------------------------------------------------------------

FALLBACK_EVENTS: Dict[int, list[str]] = {
    2026: [
        "Australian Grand Prix",
        "Chinese Grand Prix",
        "Japanese Grand Prix",
        "Miami Grand Prix",
        "Canadian Grand Prix",
        "Monaco Grand Prix",
        "Spanish Grand Prix",
        "Austrian Grand Prix",
        "British Grand Prix",
        "Belgian Grand Prix",
        "Hungarian Grand Prix",
    ],
}


EXCLUDE_EVENTS: Dict[int, set[str]] = {}


# -------------------------------------------------------------------
# Track archetype groups
# -------------------------------------------------------------------

# Low-downforce / power-sensitive circuits.
# Zandvoort is NOT low-downforce.
LOW_DF_GPS = {
    "Austrian Grand Prix",
    "Belgian Grand Prix",
}


# Street circuits.
# Zandvoort is a permanent purpose-built circuit.
STREET_GPS = {
    "Monaco Grand Prix",
}


# Long-straight / power-sensitive circuits.
# Zandvoort has a usable main straight but is primarily corner dominated.
LONG_STRAIGHT_GPS = {
    "Spanish Grand Prix",
    "Austrian Grand Prix",
    "British Grand Prix",
    "Belgian Grand Prix",
}


# High-downforce / technical circuits.
#
# Zandvoort fits this group well, although it is faster and more
# aero-sensitive than Hungary or Monaco.
HIGH_DF_TECHNICAL_GPS = {
    "Monaco Grand Prix",
    "Hungarian Grand Prix",
    "Dutch Grand Prix",
}


# -------------------------------------------------------------------
# Circuit-specific feature priors
#
# Values are engineering priors between 0 and 1.
# Weather values should be refreshed close to race start.
# -------------------------------------------------------------------

CIRCUIT_EXTRAS = {
    # ---------------------------------------------------------------
    # Dutch Grand Prix - Zandvoort
    # ---------------------------------------------------------------

    "Dutch Grand Prix": {
        # -----------------------------------------------------------
        # Strategy and overtaking
        # -----------------------------------------------------------

        # Usually one-stop or two-stop depending on compound choice,
        # tyre degradation, Sprint-weekend learning and Safety Cars.
        "expected_stops": 1.7,

        # Overtaking is difficult because of the narrow, flowing layout.
        # Turn 1 provides the main conventional opportunity.
        "overtake_index": 0.34,

        # Tow matters on the pit straight but is much less dominant
        # than at Spa or Austria.
        "tow_importance": 0.42,

        # High-downforce circuit.
        "is_low_df": 0,

        # Permanent circuit.
        "is_street": 0,

        # Short main straight relative to the overall technical nature.
        "long_straight_index": 0.38,

        # Braking is important at Tarzan and several slower corners,
        # but much of the lap depends on flow and corner speed.
        "braking_intensity": 0.58,

        # Coastal conditions and cool tyre temperatures can make
        # preparation harder than at Hungary.
        "warmup_penalty": 0.10,

        # High lateral loads and repeated cornering make tyre management
        # important over a stint.
        "deg_rate": 0.64,

        # Representative stint length over a 72-lap race.
        "stint_len_typical": 25,

        # -----------------------------------------------------------
        # Track and layout characteristics
        # -----------------------------------------------------------

        # Modern surface is reasonably smooth but banking and compression
        # add substantial vertical loading.
        "surface_bumpiness": 0.38,

        # Coastal location makes Zandvoort notably wind-sensitive.
        "wind_sensitivity": 0.78,

        # Narrow circuit and aggressive corner exits create moderate
        # track-limits / mistake exposure.
        "track_limits_risk": 0.58,

        # Significant undulation through the dunes.
        "elevation_change_index": 0.62,

        # High lateral loads and repeated acceleration/braking impose
        # moderate mechanical stress.
        "mechanical_failure_risk": 0.50,

        # Current Zandvoort layout.
        "corner_count": 14,

        # Representative average-speed prior.
        "avg_speed_kph": 215,

        # -----------------------------------------------------------
        # Weather priors
        #
        # Coastal weather can change quickly. These should be updated
        # using the actual race-day forecast.
        # -----------------------------------------------------------

        "rain_prob_race": 0.24,
        "wet_lap_fraction": 0.09,
        "wet_start_prob": 0.06,
        "mixed_conditions_risk": 0.18,
    },

    # ---------------------------------------------------------------
    # Hungarian Grand Prix
    # ---------------------------------------------------------------

    "Hungarian Grand Prix": {
        "expected_stops": 1.8,
        "overtake_index": 0.38,
        "tow_importance": 0.46,
        "is_low_df": 0,
        "is_street": 0,
        "long_straight_index": 0.40,
        "braking_intensity": 0.64,
        "warmup_penalty": 0.03,
        "deg_rate": 0.70,
        "stint_len_typical": 25,

        "surface_bumpiness": 0.34,
        "wind_sensitivity": 0.42,
        "track_limits_risk": 0.52,
        "elevation_change_index": 0.43,
        "mechanical_failure_risk": 0.44,
        "corner_count": 14,
        "avg_speed_kph": 198,

        "rain_prob_race": 0.05,
        "wet_lap_fraction": 0.01,
        "wet_start_prob": 0.02,
        "mixed_conditions_risk": 0.04,
    },

    # ---------------------------------------------------------------
    # Belgian Grand Prix
    # ---------------------------------------------------------------

    "Belgian Grand Prix": {
        "expected_stops": 1.8,
        "overtake_index": 0.76,
        "tow_importance": 0.88,
        "is_low_df": 1,
        "is_street": 0,
        "long_straight_index": 0.91,
        "braking_intensity": 0.62,
        "warmup_penalty": 0.18,
        "deg_rate": 0.58,
        "stint_len_typical": 22,

        "surface_bumpiness": 0.43,
        "wind_sensitivity": 0.78,
        "track_limits_risk": 0.67,
        "elevation_change_index": 0.96,
        "mechanical_failure_risk": 0.68,
        "corner_count": 19,
        "avg_speed_kph": 233,

        "rain_prob_race": 0.42,
        "wet_lap_fraction": 0.22,
        "wet_start_prob": 0.16,
        "mixed_conditions_risk": 0.48,
    },

    # ---------------------------------------------------------------
    # British Grand Prix
    # ---------------------------------------------------------------

    "British Grand Prix": {
        "expected_stops": 2.0,
        "overtake_index": 0.60,
        "tow_importance": 0.66,
        "is_low_df": 0,
        "is_street": 0,
        "long_straight_index": 0.70,
        "braking_intensity": 0.52,
        "warmup_penalty": 0.08,
        "deg_rate": 0.72,
        "stint_len_typical": 20,

        "surface_bumpiness": 0.42,
        "wind_sensitivity": 0.82,
        "track_limits_risk": 0.56,
        "elevation_change_index": 0.28,
        "mechanical_failure_risk": 0.52,
        "corner_count": 18,
        "avg_speed_kph": 235,

        "rain_prob_race": 0.28,
        "wet_lap_fraction": 0.12,
        "wet_start_prob": 0.08,
        "mixed_conditions_risk": 0.22,
    },

    # ---------------------------------------------------------------
    # Austrian Grand Prix
    # ---------------------------------------------------------------

    "Austrian Grand Prix": {
        "expected_stops": 2.0,
        "overtake_index": 0.68,
        "tow_importance": 0.72,
        "is_low_df": 1,
        "is_street": 0,
        "long_straight_index": 0.78,
        "braking_intensity": 0.72,
        "warmup_penalty": 0.06,
        "deg_rate": 0.54,
        "stint_len_typical": 22,

        "surface_bumpiness": 0.38,
        "wind_sensitivity": 0.58,
        "track_limits_risk": 0.88,
        "elevation_change_index": 0.70,
        "mechanical_failure_risk": 0.48,
        "corner_count": 10,
        "avg_speed_kph": 230,

        "rain_prob_race": 0.18,
        "wet_lap_fraction": 0.06,
        "wet_start_prob": 0.04,
        "mixed_conditions_risk": 0.12,
    },

    # ---------------------------------------------------------------
    # Spanish Grand Prix
    # ---------------------------------------------------------------

    "Spanish Grand Prix": {
        "expected_stops": 2.0,
        "overtake_index": 0.52,
        "tow_importance": 0.58,
        "is_low_df": 0,
        "is_street": 0,
        "long_straight_index": 0.62,
        "braking_intensity": 0.58,
        "warmup_penalty": 0.08,
        "deg_rate": 0.68,
        "stint_len_typical": 20,

        "surface_bumpiness": 0.35,
        "wind_sensitivity": 0.62,
        "track_limits_risk": 0.62,
        "elevation_change_index": 0.35,
        "mechanical_failure_risk": 0.42,
        "corner_count": 14,
        "avg_speed_kph": 215,

        "rain_prob_race": 0.12,
        "wet_lap_fraction": 0.04,
        "wet_start_prob": 0.03,
        "mixed_conditions_risk": 0.08,
    },

    # ---------------------------------------------------------------
    # Monaco Grand Prix
    # ---------------------------------------------------------------

    "Monaco Grand Prix": {
        "expected_stops": 1.4,
        "overtake_index": 0.12,
        "tow_importance": 0.18,
        "is_low_df": 0,
        "is_street": 1,
        "long_straight_index": 0.18,
        "braking_intensity": 0.78,
        "warmup_penalty": 0.12,
        "deg_rate": 0.32,
        "stint_len_typical": 28,

        "surface_bumpiness": 0.82,
        "wind_sensitivity": 0.30,
        "track_limits_risk": 0.18,
        "elevation_change_index": 0.72,
        "mechanical_failure_risk": 0.60,
        "corner_count": 19,
        "avg_speed_kph": 160,

        "rain_prob_race": 0.22,
        "wet_lap_fraction": 0.08,
        "wet_start_prob": 0.06,
        "mixed_conditions_risk": 0.18,
    },

    # ---------------------------------------------------------------
    # Generic fallback
    # ---------------------------------------------------------------

    "_default": {
        "expected_stops": 2.0,
        "overtake_index": 0.50,
        "tow_importance": 0.50,
        "is_low_df": 0.0,
        "is_street": 0.0,
        "long_straight_index": 0.50,
        "braking_intensity": 0.50,
        "warmup_penalty": 0.05,
        "deg_rate": 0.50,
        "stint_len_typical": 18,

        "surface_bumpiness": 0.50,
        "wind_sensitivity": 0.50,
        "track_limits_risk": 0.50,
        "elevation_change_index": 0.30,
        "mechanical_failure_risk": 0.50,
        "corner_count": 16,
        "avg_speed_kph": 210,

        "rain_prob_race": 0.10,
        "wet_lap_fraction": 0.05,
        "wet_start_prob": 0.03,
        "mixed_conditions_risk": 0.08,
    },
}