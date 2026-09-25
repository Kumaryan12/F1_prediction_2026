import numpy as np
import pandas as pd

from predictor.ensemble import (
    ENSEMBLE_FEATS,
    TEMPORALLY_UNSAFE_FEATURES,
    ensemble_feature_importance,
    predict_event_with_ensemble,
    train_ensemble,
)


def _frame(races: int = 12, drivers: int = 12) -> pd.DataFrame:
    rows = []
    for race in range(races):
        for driver in range(drivers):
            grid = driver + 1
            row = {
                    "year": 2024,
                    "gp": f"Race {race}",
                    "date": pd.Timestamp("2024-01-01") + pd.Timedelta(days=7 * race),
                    "driver": f"D{driver}",
                    "team": f"T{driver // 2}",
                    "grid_pos": grid,
                    "finish_pos": np.clip(grid + ((race + driver) % 3) - 1, 1, drivers),
                    "drv_form3": float(grid),
                    "team_form3": float(driver // 2 + 1),
                }
            for feature in ENSEMBLE_FEATS:
                if feature not in row and feature not in {"driver", "team"}:
                    row[feature] = 0.0
            rows.append(row)
    return pd.DataFrame(rows)


def test_ensemble_excludes_time_unsafe_features():
    assert not (set(ENSEMBLE_FEATS) & TEMPORALLY_UNSAFE_FEATURES)
    assert "grid_pos" not in ENSEMBLE_FEATS
    assert "driver_skill_rating" in ENSEMBLE_FEATS


def test_ensemble_probabilities_form_one_race():
    train = _frame()
    prediction_frame = train[train["gp"] == "Race 11"].drop(columns="finish_pos")
    model = train_ensemble(train)
    importance = ensemble_feature_importance(model)
    out = predict_event_with_ensemble(model, prediction_frame, mc_samples=200)

    assert np.isclose(importance["importance"].sum(), 1.0)
    assert np.isclose(importance.loc["grid_pos", "importance"], 0.35)
    assert np.isclose(importance.loc["grid_pos", "model_ensemble_importance"], 0.0)
    assert sorted(out["pred_rank"].tolist()) == list(range(1, len(out) + 1))
    assert np.isclose(out["p_win"].sum(), 1.0)
    assert np.isclose(out["p_podium"].sum(), 3.0)
    assert np.isclose(out["p_top10"].sum(), 10.0)
    assert (out["pred_finish"] == out["blend_rank_score"]).all()
    assert sorted(out["pred_rank_model_ensemble"].tolist()) == list(
        range(1, len(out) + 1)
    )
    assert (out["ranking_mode_default"] == "ensemble_grid_blend").all()


def test_feature_ablation_masks_requested_signal():
    train = _frame()
    model = train_ensemble(train, n_estimators=20, excluded_features={"driver_skill_rating"})
    assert model.excluded_features_ == {"driver_skill_rating"}
