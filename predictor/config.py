from pathlib import Path
from typing import Dict, Tuple

CACHE_DIR: Path = Path(__file__).resolve().parent / "f1cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

HIST_YEARS = list(range(2023, 2026))

DEFAULT_SC = 0.5
DEFAULT_VSC = 0.5
DEFAULT_PIT_LOSS = 21.0

CIRCUIT_VOL: Dict[str, Tuple[float, float, float]] = {
    "Canadian Grand Prix": (0.78, 0.48, 18.5),
}

FALLBACK_EVENTS: Dict[int, list[str]] = {
    2026: [
        "Australian Grand Prix",
        "Chinese Grand Prix",
        "Japanese Grand Prix",
        "Miami Grand Prix",
        "Canadian Grand Prix",
    ],
}

EXCLUDE_EVENTS: Dict[int, set[str]] = {}

LOW_DF_GPS = {
    "Canadian Grand Prix",
}

STREET_GPS = set()

LONG_STRAIGHT_GPS = {
    "Canadian Grand Prix",
}

CIRCUIT_EXTRAS = {
    "Canadian Grand Prix": {
        "expected_stops": 1.9,
        "overtake_index": 0.82,
        "tow_importance": 0.76,
        "is_low_df": 1,
        "is_street": 0,
        "long_straight_index": 0.88,
        "braking_intensity": 0.92,
        "warmup_penalty": 0.04,
        "deg_rate": 0.38,
        "stint_len_typical": 24,

        "surface_bumpiness": 0.62,
        "wind_sensitivity": 0.36,
        "track_limits_risk": 0.22,
        "elevation_change_index": 0.12,
        "mechanical_failure_risk": 0.52,
        "corner_count": 14,
        "avg_speed_kph": 215,

        "rain_prob_race": 0.30,
        "wet_lap_fraction": 0.12,
        "wet_start_prob": 0.08,
        "mixed_conditions_risk": 0.24,
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