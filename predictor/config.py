from pathlib import Path
from typing import Dict, Tuple

# Where FastF1 stores/cache data
CACHE_DIR: Path = Path(__file__).resolve().parent / "f1cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Historical seasons used for training
HIST_YEARS = list(range(2023, 2026))

# Default circuit values
DEFAULT_SC = 0.5
DEFAULT_VSC = 0.5
DEFAULT_PIT_LOSS = 21.0

# (SC probability, VSC probability, pit loss seconds)
CIRCUIT_VOL: Dict[str, Tuple[float, float, float]] = {
    "Japanese Grand Prix": (0.58, 0.34, 21.8),
}

# Fallback calendar
FALLBACK_EVENTS: Dict[int, list[str]] = {
    2026: [
        "Australian Grand Prix",
        "Chinese Grand Prix",
        "Japanese Grand Prix",
    ],
}

# Events to exclude if needed
EXCLUDE_EVENTS: Dict[int, set[str]] = {}

# Low downforce circuits
LOW_DF_GPS = {
    "Italian Grand Prix",
    "Azerbaijan Grand Prix",
    "Canadian Grand Prix",
    "Saudi Arabian Grand Prix",
}

# Street circuits
STREET_GPS = {
    "Monaco Grand Prix",
    "Singapore Grand Prix",
    "Azerbaijan Grand Prix",
    "Saudi Arabian Grand Prix",
    "Miami Grand Prix",
    "Las Vegas Grand Prix",
}

# Circuits with long-straight performance bias
LONG_STRAIGHT_GPS = {
    "Italian Grand Prix",
    "Azerbaijan Grand Prix",
    "Saudi Arabian Grand Prix",
    "Canadian Grand Prix",
    "United States Grand Prix",
    "Mexico City Grand Prix",
    "Las Vegas Grand Prix",
    "Qatar Grand Prix",
    "Abu Dhabi Grand Prix",
}

# Circuit characteristics used by the ML model
CIRCUIT_EXTRAS = {
    "Japanese Grand Prix": {
        "expected_stops": 1.7,
        "overtake_index": 0.40,
        "tow_importance": 0.46,
        "is_low_df": 0,
        "is_street": 0,
        "long_straight_index": 0.58,
        "braking_intensity": 0.70,
        "warmup_penalty": 0.08,
        "deg_rate": 0.54,
        "stint_len_typical": 20,

        "surface_bumpiness": 0.44,
        "wind_sensitivity": 0.72,
        "track_limits_risk": 0.28,
        "elevation_change_index": 0.62,
        "mechanical_failure_risk": 0.47,
        "corner_count": 18,
        "avg_speed_kph": 223,

        "rain_prob_race": 0.24,
        "wet_lap_fraction": 0.10,
        "wet_start_prob": 0.07,
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