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
#
# Official 2026 Monza race-week statistics:
# SC  = 50%
# VSC = 38%
# Pit loss = 24.14 s
# -------------------------------------------------------------------

CIRCUIT_VOL: Dict[str, Tuple[float, float, float]] = {
    "Italian Grand Prix": (0.50, 0.38, 24.14),
}


# -------------------------------------------------------------------
# Completed 2026 races available for training/form generation
#
# Dutch GP is now completed and may be included.
#
# Italian GP is the ACTIVE prediction target, therefore it must NOT
# be added here until the race has finished.
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
        "Dutch Grand Prix",
    ],
}


EXCLUDE_EVENTS: Dict[int, set[str]] = {}


# -------------------------------------------------------------------
# Track archetype groups
# -------------------------------------------------------------------

# ---------------------------------------------------------------
# Low-downforce / power-sensitive circuits
#
# Monza is the strongest example of this archetype in the current
# feature system.
# ---------------------------------------------------------------

LOW_DF_GPS = {
    "Austrian Grand Prix",
    "Belgian Grand Prix",
    "Italian Grand Prix",
}


# ---------------------------------------------------------------
# Street circuits
#
# Monza is a permanent purpose-built circuit.
# ---------------------------------------------------------------

STREET_GPS = {
    "Monaco Grand Prix",
}


# ---------------------------------------------------------------
# Long-straight / power-sensitive circuits
#
# Monza must be included because straight-line efficiency,
# energy deployment, drag and tow are fundamental there.
# ---------------------------------------------------------------

LONG_STRAIGHT_GPS = {
    "Spanish Grand Prix",
    "Austrian Grand Prix",
    "British Grand Prix",
    "Belgian Grand Prix",
    "Italian Grand Prix",
}


# ---------------------------------------------------------------
# High-downforce / technical circuits
#
# Monza must NOT be included.
# ---------------------------------------------------------------

HIGH_DF_TECHNICAL_GPS = {
    "Monaco Grand Prix",
    "Hungarian Grand Prix",
    "Dutch Grand Prix",
}


# -------------------------------------------------------------------
# Circuit-specific feature priors
#
# Normalized values are model priors between 0 and 1.
#
# For Monza the most important dimensions are:
#
# - very low drag / low downforce
# - straight-line speed
# - tow / slipstream
# - energy deployment
# - traction
# - braking stability
# - rear tyre overheating
# - power-unit reliability
# -------------------------------------------------------------------

CIRCUIT_EXTRAS = {

    # ---------------------------------------------------------------
    # Italian Grand Prix - Monza
    # ---------------------------------------------------------------

    "Italian Grand Prix": {

        # -----------------------------------------------------------
        # Strategy
        # -----------------------------------------------------------

        # Pirelli expects a one-stop race to be the most likely.
        "expected_stops": 1.2,

        # Genuine overtaking opportunities exist at Turns 1 and 4,
        # plus through DRS/tow effects on the long straights.
        "overtake_index": 0.80,

        # Slipstreaming is extremely important at Monza.
        "tow_importance": 0.95,

        # Monza is the calendar's classic low-downforce venue.
        "is_low_df": 1,

        "is_street": 0,

        # Among the strongest long-straight profiles of any circuit.
        "long_straight_index": 0.98,

        # Heavy stops into the Rettifilo and Roggia chicanes make
        # braking stability very important.
        "braking_intensity": 0.84,

        # Current hot weather should make tyre warm-up relatively easy.
        "warmup_penalty": 0.02,

        # Degradation is expected to remain manageable despite high
        # rear-axle temperatures.
        "deg_rate": 0.38,

        # 53 laps with a likely one-stop strategy.
        "stint_len_typical": 27,

        # -----------------------------------------------------------
        # Track / layout
        # -----------------------------------------------------------

        # Circuit was resurfaced in 2024 and is generally smooth,
        # although Ascari retains some bump sensitivity.
        "surface_bumpiness": 0.30,

        # Wind matters for braking and aero stability but Monza is less
        # wind-sensitive than Spa, Silverstone or Zandvoort.
        "wind_sensitivity": 0.40,

        # Moderate exposure at chicanes and corner exits.
        "track_limits_risk": 0.50,

        # Very limited elevation variation.
        "elevation_change_index": 0.10,

        # High full-throttle percentage, new-2026 PU energy demands,
        # traction events and sustained high speed increase reliability
        # exposure.
        "mechanical_failure_risk": 0.72,

        # Official current circuit configuration.
        "corner_count": 11,

        # Representative circuit-speed feature prior.
        "avg_speed_kph": 250,

        # -----------------------------------------------------------
        # Current 2026 race-weather priors
        #
        # Official forecast:
        # - hot
        # - sunny
        # - approximately 34 C maximum
        # - essentially dry during race hours
        #
        # A low residual probability is retained rather than forcing
        # exactly zero.
        # -----------------------------------------------------------

        "rain_prob_race": 0.02,
        "wet_lap_fraction": 0.00,
        "wet_start_prob": 0.01,
        "mixed_conditions_risk": 0.02,
    },


    # ---------------------------------------------------------------
    # Dutch Grand Prix - Zandvoort
    #
    # Retained because the completed 2026 Dutch GP can now contribute
    # to rolling and current-season form.
    # ---------------------------------------------------------------

    "Dutch Grand Prix": {
        "expected_stops": 1.7,
        "overtake_index": 0.34,
        "tow_importance": 0.42,
        "is_low_df": 0,
        "is_street": 0,
        "long_straight_index": 0.38,
        "braking_intensity": 0.58,
        "warmup_penalty": 0.10,
        "deg_rate": 0.64,
        "stint_len_typical": 25,

        "surface_bumpiness": 0.38,
        "wind_sensitivity": 0.78,
        "track_limits_risk": 0.58,
        "elevation_change_index": 0.62,
        "mechanical_failure_risk": 0.50,
        "corner_count": 14,
        "avg_speed_kph": 215,

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