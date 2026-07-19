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
    "Belgian Grand Prix": (0.63, 0.20, 18.8),
}


# -------------------------------------------------------------------
# 2026 completed/current race list
#
# British GP is retained as a completed event.
# Belgian GP is now the active prediction event, so it should not be
# added here until after the Belgian GP has been completed.
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
    ],
}


EXCLUDE_EVENTS: Dict[int, set[str]] = {}


# -------------------------------------------------------------------
# Track archetype groups
# -------------------------------------------------------------------

# Spa is power-sensitive and generally uses a relatively low-drag
# aerodynamic configuration. It is not as extreme as Monza, but it is
# appropriate to include Spa in the low-downforce archetype.
LOW_DF_GPS = {
    "Austrian Grand Prix",
    "Belgian Grand Prix",
}


# Spa is a permanent road circuit, not a street circuit.
STREET_GPS = {
    "Monaco Grand Prix",
}


# Spa strongly rewards straight-line speed, energy deployment and tow.
LONG_STRAIGHT_GPS = {
    "Spanish Grand Prix",
    "Austrian Grand Prix",
    "British Grand Prix",
    "Belgian Grand Prix",
}


# -------------------------------------------------------------------
# Circuit-specific feature priors
#
# Values between 0 and 1 are normalized engineering priors.
# Weather values are provisional climatological/race-week priors and
# should be replaced by forecast-derived values closer to the event.
# -------------------------------------------------------------------

CIRCUIT_EXTRAS = {
    "Belgian Grand Prix": {
        # -----------------------------------------------------------
        # Strategy and overtaking
        # -----------------------------------------------------------

        # Spa can support one-stop or two-stop strategies depending on
        # tyre compounds, degradation, weather and Safety Car timing.
        "expected_stops": 1.8,

        # Kemmel Straight and the long lap provide genuine overtaking
        # opportunities, although sector-two aero performance matters.
        "overtake_index": 0.76,

        # Slipstreaming is particularly important from Eau Rouge and
        # Raidillon onto the Kemmel Straight.
        "tow_importance": 0.88,

        # Spa is power-sensitive and relatively low drag, but not an
        # extreme minimum-downforce circuit like Monza.
        "is_low_df": 1,

        "is_street": 0,

        # One of the strongest long-straight profiles on the calendar.
        "long_straight_index": 0.91,

        # Heavy braking occurs at La Source and Les Combes, but much of
        # the circuit is dominated by medium/high-speed cornering.
        "braking_intensity": 0.62,

        # Low track temperatures and wet conditions can create tyre
        # warm-up difficulties.
        "warmup_penalty": 0.18,

        # Spa can produce moderate tyre degradation, but tyre stress is
        # strongly affected by setup and weather.
        "deg_rate": 0.58,

        # Approximate representative stint length over a 44-lap race.
        "stint_len_typical": 22,

        # -----------------------------------------------------------
        # Track and layout characteristics
        # -----------------------------------------------------------

        # The modern surface is not exceptionally bumpy, although the
        # circuit's elevation and compression zones load the car.
        "surface_bumpiness": 0.43,

        # Wind has a substantial effect because of the long lap, open
        # surroundings and high-speed cornering.
        "wind_sensitivity": 0.78,

        # Track limits can matter at Raidillon, Les Combes, Pouhon and
        # the exit of several high-speed corners.
        "track_limits_risk": 0.67,

        # Spa has one of the largest elevation profiles in Formula 1.
        "elevation_change_index": 0.96,

        # Long periods at high throttle and large mechanical loads
        # increase power-unit and reliability exposure.
        "mechanical_failure_risk": 0.68,

        # Official modern Spa layout.
        "corner_count": 19,

        # Representative race/qualifying-speed prior, not a guaranteed
        # measured value for the 2026 cars.
        "avg_speed_kph": 233,

        # -----------------------------------------------------------
        # Weather priors
        # -----------------------------------------------------------

        # Spa weather can change rapidly and conditions may differ
        # between different parts of the seven-kilometre circuit.
        "rain_prob_race": 0.42,

        # Expected fraction of laps potentially affected by wet or
        # intermediate conditions before race-week forecast updates.
        "wet_lap_fraction": 0.22,

        "wet_start_prob": 0.16,

        # High because localized rain can produce partially wet laps
        # and difficult tyre decisions.
        "mixed_conditions_risk": 0.48,
    },

    # ---------------------------------------------------------------
    # British Grand Prix
    # Retained for current-season and historical feature generation.
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