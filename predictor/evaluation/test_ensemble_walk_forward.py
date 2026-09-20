import numpy as np
import pandas as pd

from predictor.evaluation.ensemble_walk_forward import apply_rank_blend, score_alphas


def _predictions() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "year": [2024] * 4,
            "gp": ["Test GP"] * 4,
            "driver": ["A", "B", "C", "D"],
            "grid_rank_component": [1, 2, 3, 4],
            "pred_rank_model_ensemble": [4, 1, 2, 3],
            "finish_pos": [2, 1, 3, 4],
        }
    )


def test_rank_blend_endpoints():
    predictions = _predictions()
    pure_grid = apply_rank_blend(predictions, 0.0)
    pure_model = apply_rank_blend(predictions, 1.0)
    assert pure_grid.sort_values("pred_rank")["driver"].tolist() == ["A", "B", "C", "D"]
    assert pure_model.sort_values("pred_rank")["driver"].tolist() == ["B", "C", "D", "A"]


def test_alpha_search_reports_ranking_metric():
    summary = score_alphas(_predictions(), [0.0, 1.0])
    assert summary["alpha"].tolist() == [0.0, 1.0]
    assert np.isfinite(summary["spearman"]).all()
