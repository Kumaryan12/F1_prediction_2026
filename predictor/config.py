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
    "Hungarian Grand Prix": (0.13, 0.25, 20.56),
}


# -------------------------------------------------------------------
# Completed 2026 races available for training/form generation
#
# Belgium is now completed and may be included.
# Hungary is the active prediction target and must remain excluded
# until the Hungarian Grand Prix has finished.
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
    ],
}


EXCLUDE_EVENTS: Dict[int, set[str]] = {}


# -------------------------------------------------------------------
# Track archetype groups
# -------------------------------------------------------------------

# Low-downforce / power-sensitive circuits.
#
# Hungary is NOT included because the Hungaroring requires high
# downforce and mechanical grip.
LOW_DF_GPS = {
    "Austrian Grand Prix",
    "Belgian Grand Prix",
}


# Street circuits.
#
# Hungary is a permanent purpose-built circuit.
STREET_GPS = {
    "Monaco Grand Prix",
}


# Long-straight / power-sensitive circuits.
#
# Hungary has one meaningful main straight, but the lap is dominated
# by connected low-speed and medium-speed corners.
LONG_STRAIGHT_GPS = {
    "Spanish Grand Prix",
    "Austrian Grand Prix",
    "British Grand Prix",
    "Belgian Grand Prix",
}


# -------------------------------------------------------------------
# Circuit-specific feature priors
#
# Normalized values are engineering priors between 0 and 1.
# Weather values should be refreshed before the final prediction.
# -------------------------------------------------------------------

CIRCUIT_EXTRAS = {
    # ---------------------------------------------------------------
    # Hungarian Grand Prix
    # ---------------------------------------------------------------

    "Hungarian Grand Prix": {
        # -----------------------------------------------------------
        # Strategy and overtaking
        # -----------------------------------------------------------

        # One-stop and two-stop strategies can both be viable depending
        # on tyre compounds, degradation, track temperature and traffic.
        "expected_stops": 1.8,

        # Passing is possible into Turn 1, but following through the
        # technical middle sector is difficult.
        "overtake_index": 0.38,

        # Tow matters on the pit straight, but is less influential than
        # at Spa, Austria or other power-sensitive circuits.
        "tow_importance": 0.46,

        # Hungaroring is a high-downforce circuit.
        "is_low_df": 0,

        # Permanent circuit, not a street circuit.
        "is_street": 0,

        # Only one major straight; most of the lap is corner-dominated.
        "long_straight_index": 0.40,

        # Important braking zones exist at Turns 1, 2 and 12, but the
        # circuit is primarily defined by continuous corner sequences.
        "braking_intensity": 0.64,

        # Hot conditions usually reduce tyre warm-up difficulty.
        "warmup_penalty": 0.03,

        # High track temperatures and sustained cornering can create
        # meaningful thermal degradation.
        "deg_rate": 0.70,

        # Representative stint-length prior for a 70-lap race.
        "stint_len_typical": 25,

        # -----------------------------------------------------------
        # Track and layout characteristics
        # -----------------------------------------------------------

        # The surface is generally not extremely bumpy, although kerb
        # use and mechanical compliance remain important.
        "surface_bumpiness": 0.34,

        # Wind matters, but the compact enclosed layout is less
        # wind-sensitive than Silverstone or Spa.
        "wind_sensitivity": 0.42,

        # Track-limit exposure is moderate around corner exits.
        "track_limits_risk": 0.52,

        # The circuit contains noticeable elevation changes but is not
        # in the same category as Spa or Austria.
        "elevation_change_index": 0.43,

        # Lower full-throttle demand reduces power-unit stress relative
        # to Spa, although heat can affect cooling and reliability.
        "mechanical_failure_risk": 0.44,

        # Modern Hungaroring layout.
        "corner_count": 14,

        # Representative circuit-speed prior.
        "avg_speed_kph": 198,

        # -----------------------------------------------------------
        # Weather priors
        #
        # Current race-day forecast indicates hot, predominantly dry
        # conditions. Refresh immediately before the final prediction.
        # -----------------------------------------------------------

        "rain_prob_race": 0.05,
        "wet_lap_fraction": 0.01,
        "wet_start_prob": 0.02,
        "mixed_conditions_risk": 0.04,
    },

    # ---------------------------------------------------------------
    # Belgian Grand Prix
    # Retained for historical and current-season form generation.
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