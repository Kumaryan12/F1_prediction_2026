from pathlib import Path
from typing import Dict, Tuple

CACHE_DIR: Path = Path(__file__).resolve().parent / "f1cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

HIST_YEARS = list(range(2023, 2026))

DEFAULT_SC = 0.5
DEFAULT_VSC = 0.5
DEFAULT_PIT_LOSS = 21.0


# -------------------------------------------------------------------
# Active race volatility configuration
# Tuple = (SC probability, VSC probability, pit loss seconds)
# -------------------------------------------------------------------

CIRCUIT_VOL: Dict[str, Tuple[float, float, float]] = {
    "Austrian Grand Prix": (0.50, 0.40, 20.0),
}


# -------------------------------------------------------------------
# 2026 fallback completed/current race list
# Add Austrian GP after Spanish GP because we are moving to Austria.
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
    ],
}


EXCLUDE_EVENTS: Dict[int, set[str]] = {}


# -------------------------------------------------------------------
# Track archetype groups
# -------------------------------------------------------------------

# Red Bull Ring is power-sensitive / medium-low downforce.
# It is not Monza-level low downforce, but low-DF features are relevant.
LOW_DF_GPS = {
    "Austrian Grand Prix",
}


# Keep Monaco as street for historical feature generation.
# Austria is NOT street.
STREET_GPS = {
    "Monaco Grand Prix",
}


# Austria has several full-throttle sections and DRS zones.
LONG_STRAIGHT_GPS = {
    "Spanish Grand Prix",
    "Austrian Grand Prix",
}


# -------------------------------------------------------------------
# Circuit-specific feature priors
# Values are normalized/manual priors for model features.
# -------------------------------------------------------------------

CIRCUIT_EXTRAS = {
    "Austrian Grand Prix": {
        # Race strategy / overtaking profile
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

        # Track / layout extras
        "surface_bumpiness": 0.38,
        "wind_sensitivity": 0.58,
        "track_limits_risk": 0.88,
        "elevation_change_index": 0.70,
        "mechanical_failure_risk": 0.48,
        "corner_count": 10,
        "avg_speed_kph": 230,

        # Weather priors
        # Update these closer to race day if you have a real forecast.
        "rain_prob_race": 0.18,
        "wet_lap_fraction": 0.06,
        "wet_start_prob": 0.04,
        "mixed_conditions_risk": 0.12,
    },

    # Keep Spanish GP extras for historical/current-season feature generation.
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

    # Keep Monaco extras for historical feature generation/debugging.
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