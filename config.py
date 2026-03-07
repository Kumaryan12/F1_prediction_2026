from pathlib import Path
from typing import Dict, Tuple

# Where FastF1 stores/cache data (inside this package folder)
CACHE_DIR: Path = Path(__file__).resolve().parent / "f1cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)  # ensure it exists

# Historical seasons to use for training
# For 2026 opener, include 2023–2025 history.
HIST_YEARS = list(range(2023, 2026))

# Defaults used when a circuit isn't in CIRCUIT_VOL
DEFAULT_SC = 0.5
DEFAULT_VSC = 0.5
DEFAULT_PIT_LOSS = 21.0

# Circuit parameters: (SC probability, VSC probability, pit loss seconds)
CIRCUIT_VOL: Dict[str, Tuple[float, float, float]] = {
    "Bahrain Grand Prix": (0.63, 0.50, 22.9),
    "Saudi Arabian Grand Prix": (1.00, 0.50, 19.2),

    # Australia 2026 official guide values
    "Australian Grand Prix": (0.67, 0.67, 19.30),

    "Japanese Grand Prix": (0.67, 0.50, 22.2),
    "Dutch Grand Prix": (0.60, 0.60, 21.5),
    "Singapore Grand Prix": (0.90, 0.40, 27.0),

    # Las Vegas Grand Prix
    "Las Vegas Grand Prix": (0.45, 0.35, 22.0),

    # Qatar Grand Prix (Lusail)
    "Qatar Grand Prix": (0.55, 0.40, 21.0),

    # Abu Dhabi Grand Prix (Yas Marina)
    "Abu Dhabi Grand Prix": (0.60, 0.35, 22.0),
}

FALLBACK_EVENTS: Dict[int, list[str]] = {
    2025: [
        "Bahrain Grand Prix",
        "Saudi Arabian Grand Prix",
        "Australian Grand Prix",
        "Japanese Grand Prix",
        "Chinese Grand Prix",
        "Miami Grand Prix",
        "Emilia Romagna Grand Prix",
        "Monaco Grand Prix",
        "Canadian Grand Prix",
        "Spanish Grand Prix",
        "Austrian Grand Prix",
        "British Grand Prix",
        "Hungarian Grand Prix",
        "Belgian Grand Prix",
        "Dutch Grand Prix",
        "Italian Grand Prix",
        "Singapore Grand Prix",
        "United States Grand Prix",
        "Mexico City Grand Prix",
        "Las Vegas Grand Prix",
        "Qatar Grand Prix",
        "Abu Dhabi Grand Prix",
    ],

    # Early 2026 schedule entries confirmed in the official schedule page
    2026: [
        "Australian Grand Prix",
        "Chinese Grand Prix",
        "Japanese Grand Prix",
    ],
}

# Races to exclude from training by year (tune as needed)
EXCLUDE_EVENTS: Dict[int, set[str]] = {
    # e.g. 2025: {"Hungarian Grand Prix"}
}

# Circuits that behave similarly to Monza (long straights, low drag reward)
LOW_DF_GPS = {
    "Italian Grand Prix",
    "Azerbaijan Grand Prix",
    "Canadian Grand Prix",
    "Saudi Arabian Grand Prix",
    # Australia is NOT low-DF in setup terms
}

# Street circuits
STREET_GPS = {
    "Monaco Grand Prix",
    "Singapore Grand Prix",
    "Azerbaijan Grand Prix",
    "Saudi Arabian Grand Prix",
    "Miami Grand Prix",
    "Las Vegas Grand Prix",
    # Australia is better modeled as a temporary circuit, not a true street circuit
}

# Long-straight bias circuits
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
    # Australia has decent straight effect, but it's more rhythm/evolution than long-straight dominated
}

# Extra per-circuit priors
CIRCUIT_EXTRAS = {
    # --- Australian Grand Prix (Albert Park) ---
    "Australian Grand Prix": {
        # Strategy / race shape
        "expected_stops": 1.8,
        "overtake_index": 0.62,
        "tow_importance": 0.58,
        "is_low_df": 0,
        "is_street": 0,
        "temporary_circuit_flag": 1.0,
        "long_straight_index": 0.56,
        "braking_intensity": 0.60,
        "warmup_penalty": 0.18,
        "deg_rate": 0.48,
        "stint_len_typical": 19,

        # Australia-specific handling / layout traits
        "surface_bumpiness": 0.72,
        "weekend_track_evolution": 0.88,
        "reactive_front_end_demand": 0.80,

        # Generic shape / risk
        "track_limits_risk": 0.35,
        "elevation_change_index": 0.18,
        "mechanical_failure_risk": 0.45,
        "corner_count": 14,
        "avg_speed_kph": 250,

        # Weather placeholders (can be overwritten race-week)
        "rain_prob_race": 0.20,
        "wet_lap_fraction": 0.08,
        "wet_start_prob": 0.08,
        "mixed_conditions_risk": 0.18,
    },

    # --- Las Vegas Grand Prix ---
    "Las Vegas Grand Prix": {
        "expected_stops": 1.8,
        "overtake_index": 0.70,
        "tow_importance": 0.75,
        "is_low_df": 0,
        "is_street": 1,
        "temporary_circuit_flag": 1.0,
        "long_straight_index": 0.80,
        "braking_intensity": 0.55,
        "warmup_penalty": 0.05,
        "deg_rate": 0.40,
        "stint_len_typical": 20,

        "surface_bumpiness": 0.50,
        "wind_sensitivity": 0.60,
        "track_limits_risk": 0.40,
        "elevation_change_index": 0.30,
        "mechanical_failure_risk": 0.60,
        "corner_count": 16,
        "avg_speed_kph": 210,
        "weekend_track_evolution": 0.70,
        "reactive_front_end_demand": 0.55,

        "rain_prob_race": 0.60,
        "wet_lap_fraction": 0.30,
        "wet_start_prob": 0.20,
        "mixed_conditions_risk": 0.55,
    },

    # --- Qatar Grand Prix ---
    "Qatar Grand Prix": {
        "expected_stops": 2.3,
        "overtake_index": 0.55,
        "tow_importance": 0.65,
        "is_low_df": 0,
        "is_street": 0,
        "temporary_circuit_flag": 0.0,
        "long_straight_index": 0.78,
        "braking_intensity": 0.58,
        "warmup_penalty": 0.04,
        "deg_rate": 0.70,
        "stint_len_typical": 15,

        "surface_bumpiness": 0.35,
        "wind_sensitivity": 0.65,
        "track_limits_risk": 0.65,
        "elevation_change_index": 0.20,
        "mechanical_failure_risk": 0.50,
        "corner_count": 16,
        "avg_speed_kph": 215,
        "weekend_track_evolution": 0.55,
        "reactive_front_end_demand": 0.60,

        "rain_prob_race": 0.05,
        "wet_lap_fraction": 0.05,
        "wet_start_prob": 0.02,
        "mixed_conditions_risk": 0.05,
    },

    # --- Abu Dhabi Grand Prix ---
    "Abu Dhabi Grand Prix": {
        "expected_stops": 1.9,
        "overtake_index": 0.52,
        "tow_importance": 0.68,
        "is_low_df": 0,
        "is_street": 0,
        "temporary_circuit_flag": 0.0,
        "long_straight_index": 0.72,
        "braking_intensity": 0.60,
        "warmup_penalty": 0.05,
        "deg_rate": 0.52,
        "stint_len_typical": 18,

        "surface_bumpiness": 0.40,
        "wind_sensitivity": 0.45,
        "track_limits_risk": 0.55,
        "elevation_change_index": 0.25,
        "mechanical_failure_risk": 0.50,
        "corner_count": 16,
        "avg_speed_kph": 200,
        "weekend_track_evolution": 0.45,
        "reactive_front_end_demand": 0.52,

        "rain_prob_race": 0.03,
        "wet_lap_fraction": 0.03,
        "wet_start_prob": 0.01,
        "mixed_conditions_risk": 0.03,
    },

    # Generic defaults for any missing GP
    "_default": {
        "expected_stops": 2.0,
        "overtake_index": 0.50,
        "tow_importance": 0.50,
        "is_low_df": 0.0,
        "is_street": 0.0,
        "temporary_circuit_flag": 0.0,
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
        "weekend_track_evolution": 0.50,
        "reactive_front_end_demand": 0.50,

        "rain_prob_race": 0.10,
        "wet_lap_fraction": 0.05,
        "wet_start_prob": 0.03,
        "mixed_conditions_risk": 0.08,
    },
}