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
# IMPORTANT:
# Madring is a brand-new circuit in 2026.
#
# Official historical values are therefore unavailable:
# - Safety Car probability: N/A
# - VSC probability: N/A
# - Pit-loss history: N/A
#
# The values below are MODEL PRIORS, not historical statistics.
# They reflect:
# - first-year circuit uncertainty
# - hybrid street/permanent layout
# - several wall-lined / confined sections
# - new low-grip asphalt
# - relatively high incident uncertainty
# -------------------------------------------------------------------

CIRCUIT_VOL: Dict[str, Tuple[float, float, float]] = {
    "Spanish Grand Prix": (0.55, 0.35, 21.5),
}


# -------------------------------------------------------------------
# Completed 2026 races available for training / recent-form generation
#
# Italian GP is now completed and can be included.
#
# Spanish GP at Madring is the ACTIVE prediction event and therefore
# must NOT be included here until the race has actually finished.
#
# IMPORTANT NAMING:
#
# June:
#     Barcelona-Catalunya Grand Prix
#
# September:
#     Spanish Grand Prix (Madrid / Madring)
# -------------------------------------------------------------------

FALLBACK_EVENTS: Dict[int, list[str]] = {
    2026: [
        "Australian Grand Prix",
        "Chinese Grand Prix",
        "Japanese Grand Prix",
        "Miami Grand Prix",
        "Canadian Grand Prix",
        "Monaco Grand Prix",

        # June Catalunya race
        "Barcelona-Catalunya Grand Prix",

        "Austrian Grand Prix",
        "British Grand Prix",
        "Belgian Grand Prix",
        "Hungarian Grand Prix",
        "Dutch Grand Prix",
        "Italian Grand Prix",
    ],
}


EXCLUDE_EVENTS: Dict[int, set[str]] = {}


# -------------------------------------------------------------------
# Track archetype groups
# -------------------------------------------------------------------

# ---------------------------------------------------------------
# Low-downforce / power-sensitive circuits
#
# Madrid has long straights, but it is NOT a Monza-style low-downforce
# track. The circuit also contains high-energy aero sections,
# La Monumental and numerous medium-speed corners.
# ---------------------------------------------------------------

LOW_DF_GPS = {
    "Austrian Grand Prix",
    "Belgian Grand Prix",
    "Italian Grand Prix",
}


# ---------------------------------------------------------------
# Street circuits
#
# Madring is a HYBRID circuit using both public roads and purpose-built
# sections.
#
# We deliberately do NOT classify it as a full STREET_GPS member,
# because Monaco-style street form would be too strong an analogy.
#
# The fractional street character is represented using:
#
#     is_street = 0.5
#
# inside CIRCUIT_EXTRAS.
# ---------------------------------------------------------------

STREET_GPS = {
    "Monaco Grand Prix",
}


# ---------------------------------------------------------------
# Long-straight / high-speed / energy-sensitive circuits
#
# Madrid belongs here:
# - high-speed first sector
# - significant straight-line sections
# - speeds approximately 340 km/h
# - strong energy-deployment demand
# ---------------------------------------------------------------

LONG_STRAIGHT_GPS = {
    "Barcelona-Catalunya Grand Prix",
    "Austrian Grand Prix",
    "British Grand Prix",
    "Belgian Grand Prix",
    "Italian Grand Prix",

    # Madring
    "Spanish Grand Prix",
}


# ---------------------------------------------------------------
# High-downforce / technical circuits
#
# Madrid also belongs here because it is not purely a straight-line
# circuit:
#
# - 22 corners
# - medium / low-speed technical second sector
# - 90-degree corners later in the lap
# - very high lateral loads
# - La Monumental banking
#
# Therefore Madrid is intentionally represented by TWO archetypes:
#
# HIGH_DF_TECHNICAL_GPS + LONG_STRAIGHT_GPS
# ---------------------------------------------------------------

HIGH_DF_TECHNICAL_GPS = {
    "Monaco Grand Prix",
    "Hungarian Grand Prix",
    "Dutch Grand Prix",

    # Madrid / Madring
    "Spanish Grand Prix",
}


# -------------------------------------------------------------------
# Circuit-specific feature priors
# -------------------------------------------------------------------

CIRCUIT_EXTRAS = {

    # ===============================================================
    # SPANISH GRAND PRIX - MADRING, MADRID
    # ===============================================================

    "Spanish Grand Prix": {

        # -----------------------------------------------------------
        # Strategy
        # -----------------------------------------------------------

        # First race at the venue means uncertainty is intrinsically
        # higher than at established circuits.
        #
        # C2 / C3 / C4 compounds are available.
        "expected_stops": 1.7,

        # Long straights and several significant braking zones should
        # create overtaking opportunities, although the exact raceability
        # is unknown because F1 has never raced here.
        "overtake_index": 0.65,

        # Slipstream matters on the faster sections but Madrid is not
        # as tow-dominated as Monza or Spa.
        "tow_importance": 0.72,

        # Not a Monza-style low-downforce circuit.
        "is_low_df": 0,

        # Hybrid public-road / permanent facility.
        #
        # Fractional rather than forcing Madrid into the same category
        # as Monaco.
        "is_street": 0.50,

        # Significant straight-line component.
        "long_straight_index": 0.78,

        # Several heavy braking events combined with slower 90-degree
        # corners.
        "braking_intensity": 0.72,

        # Very hot race conditions should make basic tyre warm-up easy.
        #
        # Low-grip new asphalt still introduces some preparation
        # uncertainty, so this is not exactly zero.
        "warmup_penalty": 0.04,

        # High lateral-energy demand + very hot track surface can create
        # meaningful thermal tyre management.
        "deg_rate": 0.62,

        # Representative modelling prior for 57 laps.
        "stint_len_typical": 22,

        # -----------------------------------------------------------
        # Track / layout characteristics
        # -----------------------------------------------------------

        # Newly laid surface is officially described as very smooth.
        "surface_bumpiness": 0.20,

        # Madrid is not as wind-sensitive as Silverstone or Zandvoort,
        # but the exposed high-speed sectors still matter.
        "wind_sensitivity": 0.52,

        # First-year track + technical exits + new asphalt create
        # moderate track-limit / mistake risk.
        "track_limits_risk": 0.60,

        # F1 explicitly describes significant elevation changes.
        "elevation_change_index": 0.68,

        # Madrid ranks among the five most demanding circuits in terms
        # of tyre/vehicle energy according to Pirelli.
        #
        # New circuit + high loads justify an above-average reliability
        # prior, although this is not as PU-dominant as Monza.
        "mechanical_failure_risk": 0.60,

        # Official Madring layout.
        "corner_count": 22,

        # Representative model prior.
        #
        # Do not treat this as a measured 2026 race average.
        "avg_speed_kph": 218,

        # -----------------------------------------------------------
        # Weather
        #
        # Official current forecast for Sunday:
        #
        # - clear
        # - approximately 32 C maximum
        # - approximately 17 C minimum
        # - track temperature potentially around 53 C
        # - 0% rain forecast
        #
        # Tiny residual values are retained to avoid hard-zero behaviour
        # in downstream probabilistic modelling.
        # -----------------------------------------------------------

        "rain_prob_race": 0.01,
        "wet_lap_fraction": 0.00,
        "wet_start_prob": 0.00,
        "mixed_conditions_risk": 0.01,
    },


    # ===============================================================
    # ITALIAN GRAND PRIX - MONZA
    # Completed 2026 race retained for recent/archetype form.
    # ===============================================================

    "Italian Grand Prix": {

        "expected_stops": 1.2,
        "overtake_index": 0.80,
        "tow_importance": 0.95,

        "is_low_df": 1,
        "is_street": 0,
        "long_straight_index": 0.98,

        "braking_intensity": 0.84,
        "warmup_penalty": 0.02,
        "deg_rate": 0.38,
        "stint_len_typical": 27,

        "surface_bumpiness": 0.30,
        "wind_sensitivity": 0.40,
        "track_limits_risk": 0.50,
        "elevation_change_index": 0.10,
        "mechanical_failure_risk": 0.72,

        "corner_count": 11,
        "avg_speed_kph": 250,

        "rain_prob_race": 0.02,
        "wet_lap_fraction": 0.00,
        "wet_start_prob": 0.01,
        "mixed_conditions_risk": 0.02,
    },


    # ===============================================================
    # DUTCH GRAND PRIX - ZANDVOORT
    # ===============================================================

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


    # ===============================================================
    # HUNGARIAN GRAND PRIX
    # ===============================================================

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


    # ===============================================================
    # BELGIAN GRAND PRIX
    # ===============================================================

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


    # ===============================================================
    # BRITISH GRAND PRIX
    # ===============================================================

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


    # ===============================================================
    # AUSTRIAN GRAND PRIX
    # ===============================================================

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


    # ===============================================================
    # BARCELONA-CATALUNYA GRAND PRIX
    #
    # IMPORTANT:
    # This was previously incorrectly stored as "Spanish Grand Prix".
    # The 2026 event was renamed Barcelona-Catalunya Grand Prix because
    # Madrid now holds the Spanish Grand Prix name.
    # ===============================================================

    "Barcelona-Catalunya Grand Prix": {

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


    # ===============================================================
    # MONACO GRAND PRIX
    # ===============================================================

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


    # ===============================================================
    # Generic fallback
    # ===============================================================

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