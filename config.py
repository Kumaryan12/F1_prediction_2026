
from pathlib import Path
from typing import Dict, Tuple  

# Where FastF1 stores/cache data (inside this package folder)
CACHE_DIR: Path = Path(__file__).resolve().parent / "f1cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)  # ensure it exists

# Historical seasons to use for training (2021–2024)
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
"Italian Grand Prix"
],
}

# Races to exclude from training by year
EXCLUDE_EVENTS = {
    2025: {"Hungarian Grand Prix"},   # add others here if needed
}

# --- Monza / low-downforce helpers ---

# Circuits that behave similarly to Monza (long straights, low drag reward)
LOW_DF_GPS = {
    "Italian Grand Prix",     # Monza
    "Azerbaijan Grand Prix",  # Baku
    "Canadian Grand Prix",    # Montreal
    "Saudi Arabian Grand Prix" # Jeddah
}

# Extra per-circuit priors. You can tune these over time.
# (_default is used when a GP isn't listed explicitly.)
CIRCUIT_EXTRAS = {
    "Italian Grand Prix": {
        "expected_stops": 1,   # Monza is typically one-stop
        "overtake_index": 0.7, # 0..1; higher = easier passing
        "tow_importance": 0.8, # 0..1; quali tow matters at Monza
        "is_low_df": 1,
        "deg_index": 0.3,
        "stint_len_typical": 22,        # mark Monza as low-downforce
    },
    "_default": {
        "expected_stops": 2,
        "overtake_index": 0.5,
        "tow_importance": 0.3,
        "is_low_df": 0,           
        "deg_index": 0.5,          # 0..1 tyre degradation severity
        "stint_len_typical": 18,
    }
}


