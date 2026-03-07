# F1_prediction_system/priors.py
from __future__ import annotations

DRIVER_SKILL_PRIOR = {
    "VER": 1.00,
    "HAM": 0.97,
    "NOR": 0.96,
    "LEC": 0.95,
    "RUS": 0.94,
    "SAI": 0.94,
    "ALO": 0.93,
    "PIA": 0.92,
    "PER": 0.92,
    "GAS": 0.88,
    "OCO": 0.88,
    "ALB": 0.88,
    "TSU": 0.87,
    "LAW": 0.87,
    "STR": 0.86,
    "HUL": 0.86,
    "MAG": 0.84,
    "BOT": 0.84,
    "ZHO": 0.82,
    "SAR": 0.80,
    "ANT": 0.89,
    "BEA": 0.87,
    "BOR": 0.85,
}
DEFAULT_DRIVER_PRIOR = 0.82


def reg_era(year: int) -> str:
    return "2026_plus" if year >= 2026 else "2023_2025"