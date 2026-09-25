from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from xgboost import XGBRanker

from .ensemble import (
    ENSEMBLE_FEATS,
    _add_dynamic_driver_skill,
    _feature_frame,
    _tree_preprocessor,
)


@dataclass
class RaceRanker:
    preprocessor: ColumnTransformer
    model: XGBRanker
    driver_skill_map_: Dict[str, float]
    default_driver_skill_: float

    def predict_score(self, df: pd.DataFrame) -> np.ndarray:
        enriched = df.copy()
        enriched["driver_skill_rating"] = (
            enriched["driver"].astype(str).map(self.driver_skill_map_)
            .fillna(self.default_driver_skill_)
        )
        return self.model.predict(self.preprocessor.transform(_feature_frame(enriched)))


def train_ranker(
    train_df: pd.DataFrame,
    n_estimators: int = 300,
    random_state: int = 42,
) -> RaceRanker:
    clean = train_df.dropna(subset=["finish_pos", "grid_pos"]).copy()
    clean, rating_map, default_rating = _add_dynamic_driver_skill(clean)
    clean = clean.sort_values(["date", "year", "gp", "driver"], kind="mergesort")

    groups = clean.groupby(["year", "gp"], sort=False)["driver"].transform("count")
    # Ranking relevance must be higher for a better finishing position.
    relevance = (groups - pd.to_numeric(clean["finish_pos"], errors="coerce") + 1).clip(0)
    group_sizes = clean.groupby(["year", "gp"], sort=False).size().to_numpy()

    preprocessor = _tree_preprocessor()
    X = preprocessor.fit_transform(_feature_frame(clean))
    model = XGBRanker(
        objective="rank:ndcg",
        eval_metric="ndcg@10",
        n_estimators=n_estimators,
        learning_rate=0.035,
        max_depth=4,
        min_child_weight=8,
        subsample=0.85,
        colsample_bytree=0.80,
        reg_lambda=5.0,
        reg_alpha=0.2,
        lambdarank_pair_method="mean",
        random_state=random_state,
        n_jobs=-1,
    )
    model.fit(X, relevance.to_numpy(float), group=group_sizes, verbose=False)
    return RaceRanker(preprocessor, model, rating_map, default_rating)


def predict_event_with_ranker(
    ranker: RaceRanker,
    features_df: pd.DataFrame,
    model_alpha: float = 0.50,
) -> pd.DataFrame:
    if not 0.0 <= model_alpha <= 1.0:
        raise ValueError("model_alpha must be between 0 and 1")
    score = ranker.predict_score(features_df)
    grid = pd.to_numeric(features_df["grid_pos"], errors="coerce").to_numpy(float)
    n = len(features_df)

    model_order = np.argsort(-score, kind="mergesort")
    model_ranks = np.empty(n, dtype=int)
    model_ranks[model_order] = np.arange(1, n + 1)
    grid_order = np.argsort(grid, kind="mergesort")
    grid_ranks = np.empty(n, dtype=int)
    grid_ranks[grid_order] = np.arange(1, n + 1)
    blend_score = model_alpha * model_ranks + (1.0 - model_alpha) * grid_ranks
    final_order = np.argsort(blend_score, kind="mergesort")
    final_ranks = np.empty(n, dtype=int)
    final_ranks[final_order] = np.arange(1, n + 1)

    out = features_df[["driver", "team", "grid_pos"]].copy()
    out["ranker_score"] = score
    out["pred_finish_model_ensemble"] = -score
    out["pred_rank_model_ensemble"] = model_ranks
    out["grid_rank_component"] = grid_ranks
    out["blend_rank_score"] = blend_score
    out["pred_finish"] = blend_score
    out["pred_rank"] = final_ranks
    out["ranking_mode_default"] = "xgboost_rank_grid_blend"
    return out.sort_values("pred_rank").reset_index(drop=True)
