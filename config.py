from pathlib import Path
from typing import Dict, Tuple

# Where FastF1 stores/cache data (inside this package folder)
CACHE_DIR: Path = Path(__file__).resolve().parent / "f1cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)  # ensure it exists

# Historical seasons to use for training (2023–2024)
HIST_YEARS = list(range(2023, 2025))

# Defaults used when a circuit isn't in CIRCUIT_VOL
DEFAULT_SC = 0.5
DEFAULT_VSC = 0.5
DEFAULT_PIT_LOSS = 21.0

# Circuit parameters: (SC probability, VSC probability, pit loss seconds)
CIRCUIT_VOL: Dict[str, Tuple[float, float, float]] = {
    "Bahrain Grand Prix": (0.63, 0.50, 22.9),
    "Saudi Arabian Grand Prix": (1.00, 0.50, 19.2),
    "Australian Grand Prix": (0.67, 0.50, 20.0),
    "Japanese Grand Prix": (0.67, 0.50, 22.2),
    "Dutch Grand Prix": (0.60, 0.60, 21.5),
    "Singapore Grand Prix": (0.90, 0.40, 27.0),

    # Las Vegas Grand Prix
    "Las Vegas Grand Prix": (0.45, 0.35, 22.0),

    # Qatar Grand Prix (Lusail) — medium SC, standard-ish pit delta
    "Qatar Grand Prix": (0.55, 0.40, 21.0),

    # Abu Dhabi Grand Prix (Yas Marina) — moderate SC, slightly above-average pit loss
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
        "United States Grand Prix",  # Austin
        "Mexico City Grand Prix",
        "Las Vegas Grand Prix",
        "Qatar Grand Prix",
        "Abu Dhabi Grand Prix",      # NEW
    ],
}

# Races to exclude from training by year (tune as needed)
EXCLUDE_EVENTS: Dict[int, set[str]] = {
    # e.g. 2025: {"Hungarian Grand Prix"}
}

# Circuits that behave similarly to Monza (long straights, low drag reward)
LOW_DF_GPS = {
    "Italian Grand Prix",      # Monza
    "Azerbaijan Grand Prix",   # Baku
    "Canadian Grand Prix",     # Montreal
    "Saudi Arabian Grand Prix" # Jeddah
    # Las Vegas, Qatar, Abu Dhabi: not pure "Monza-style" low-DF in setup terms
}

# Street circuits (Las Vegas is a street track; Qatar & Abu Dhabi are NOT)
STREET_GPS = {
    "Monaco Grand Prix",
    "Singapore Grand Prix",
    "Azerbaijan Grand Prix",
    "Saudi Arabian Grand Prix",
    "Miami Grand Prix",
    "Las Vegas Grand Prix",
}

# Long-straight bias circuits (activates longstraight_* rolling forms)
LONG_STRAIGHT_GPS = {
    "Italian Grand Prix",
    "Azerbaijan Grand Prix",
    "Saudi Arabian Grand Prix",
    "Canadian Grand Prix",
    "United States Grand Prix",   # Austin
    "Mexico City Grand Prix",
    "Las Vegas Grand Prix",
    "Qatar Grand Prix",           # Lusail main straight
    "Abu Dhabi Grand Prix",       # Yas Marina back straight + T5–T6
}

# Extra per-circuit priors (config-first). "_default" is optional but handy.
CIRCUIT_EXTRAS = {
    # --- Las Vegas Grand Prix ---
    "Las Vegas Grand Prix": {
        "expected_stops": 1.8,       # Likely 1–2 stops
        "overtake_index": 0.70,
        "tow_importance": 0.75,
        "is_low_df": 0,
        "is_street": 1,
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

        # Weather / chaos knobs (you can ignore in FEATS if not used)
        "rain_prob_race": 0.60,
        "wet_lap_fraction": 0.30,
        "wet_start_prob": 0.20,
        "mixed_conditions_risk": 0.55,
    },

    # --- Qatar Grand Prix (Lusail International Circuit) ---
    # Fast, flowing, high-deg circuit with a massive main straight,
    # open desert exposure (wind/sand), almost always dry.
    "Qatar Grand Prix": {
        "expected_stops": 2.3,       # 2–3 stops common due to tyre wear
        "overtake_index": 0.55,      # Overtaking mainly via DRS into T1
        "tow_importance": 0.65,      # Big DRS + tow on pit straight
        "is_low_df": 0,
        "is_street": 0,
        "long_straight_index": 0.78,
        "braking_intensity": 0.58,   # Heavy braking into T1; flowing elsewhere
        "warmup_penalty": 0.04,      # Night race, but warm climate
        "deg_rate": 0.70,            # Very high tyre deg from long loaded corners
        "stint_len_typical": 15,

        # Track / environment flavour
        "surface_bumpiness": 0.35,   # Fairly smooth
        "wind_sensitivity": 0.65,    # Open desert, gusty / sand
        "track_limits_risk": 0.65,   # Lots of track limit violations historically
        "elevation_change_index": 0.20,  # Mostly flat
        "mechanical_failure_risk": 0.50,
        "corner_count": 16,
        "avg_speed_kph": 215,        # Fast flowing layout

        # Weather: realistically very low rain probability
        "rain_prob_race": 0.05,
        "wet_lap_fraction": 0.05,
        "wet_start_prob": 0.02,
        "mixed_conditions_risk": 0.05,
    },

    # --- Abu Dhabi Grand Prix (Yas Marina Circuit) ---
    # Twilight/night finale, moderate tyre deg, one very long straight,
    # heavy traction zones and some awkward corner sequences.
    "Abu Dhabi Grand Prix": {
        "expected_stops": 1.9,       # Typically 1–2 stops, often 2 if deg is higher
        "overtake_index": 0.52,      # Overtaking mainly into T6 chicane / final sector
        "tow_importance": 0.68,      # Big DRS impact on long back straight
        "is_low_df": 0,
        "is_street": 0,
        "long_straight_index": 0.72, # Strong but not Monza/Mexico-level
        "braking_intensity": 0.60,   # T5/T6 heavy braking + big traction zones
        "warmup_penalty": 0.05,      # Night race, track temp falls
        "deg_rate": 0.52,            # Medium tyre wear
        "stint_len_typical": 18,

        # Track / environment flavour
        "surface_bumpiness": 0.40,   # Modern, relatively smooth
        "wind_sensitivity": 0.45,
        "track_limits_risk": 0.55,   # Exit kerbs / last sector track limits
        "elevation_change_index": 0.25,
        "mechanical_failure_risk": 0.50,
        "corner_count": 16,
        "avg_speed_kph": 200,

        # Night race, very low rain probability
        "rain_prob_race": 0.03,
        "wet_lap_fraction": 0.03,
        "wet_start_prob": 0.01,
        "mixed_conditions_risk": 0.03,
    },

    # Optional generic default if a GP is missing above
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
    },
}
