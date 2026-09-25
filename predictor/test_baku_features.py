import pandas as pd

from predictor.config import BAKU_GPS
from predictor.features import add_circuit_context_df, add_driver_team_form
from predictor.model import FEATS


def test_baku_circuit_context_matches_track_profile():
    frame = add_circuit_context_df(
        pd.DataFrame({"gp": ["Azerbaijan Grand Prix"]})
    ).iloc[0]

    assert frame["is_low_df"] == 1.0
    assert frame["is_street"] == 1.0
    assert frame["long_straight_index"] >= 0.95
    assert frame["wind_sensitivity"] >= 0.90
    assert frame["deg_rate"] < 0.40
    assert frame["rain_prob_race"] == 0.0


def test_baku_model_features_use_relevant_archetypes():
    expected = {
        "lowdf_driver_form3",
        "street_driver_form3",
        "longstraight_driver_form3",
        "baku_driver_form3",
        "baku_team_form3",
    }
    assert expected.issubset(FEATS)
    assert "highdf_driver_form3" not in FEATS


def test_baku_form_is_shifted_before_current_race():
    rows = pd.DataFrame(
        [
            [2023, "Azerbaijan Grand Prix", "2023-04-30", "AAA", "Team A", 4],
            [2024, "Azerbaijan Grand Prix", "2024-09-15", "AAA", "Team A", 2],
            [2025, "Azerbaijan Grand Prix", "2025-09-21", "AAA", "Team A", 1],
        ],
        columns=["year", "gp", "date", "driver", "team", "finish_pos"],
    )

    enriched = add_driver_team_form(rows)
    current = enriched.sort_values("date").iloc[-1]

    assert BAKU_GPS == {"Azerbaijan Grand Prix"}
    assert current["baku_driver_form3"] == 3.0
    assert current["baku_team_form3"] == 3.0
