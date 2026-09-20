from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import ExtraTreesRegressor, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import ElasticNet
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .model import FEATS


# These columns currently contain 2026/manual information or values normalized
# using the complete frame. They are useful for the live forecast display, but
# are not safe inputs to a historical walk-forward model until they are
# versioned by race date.
TEMPORALLY_UNSAFE_FEATURES = {
    "driver_skill_prior",
    "team_prior_strength",
    "rookie_flag",
    "returnee_flag",
    "driver_hist_strength",
    "team_hist_strength",
    "driver_strength_blend_2026",
    "team_strength_blend_2026",
    "rain_prob_race",
    "wet_lap_fraction",
    "wet_start_prob",
    "mixed_conditions_risk",
}

# Grid is deliberately excluded from the ML learners. It enters exactly once
# as the explicit baseline component in the final model/grid blend.
ENSEMBLE_FEATS = [
    c for c in FEATS
    if c not in TEMPORALLY_UNSAFE_FEATURES and c != "grid_pos"
] + ["driver_skill_rating"]
ENSEMBLE_CAT_COLS = [c for c in ("team", "driver") if c in ENSEMBLE_FEATS]
ENSEMBLE_NUM_COLS = [c for c in ENSEMBLE_FEATS if c not in ENSEMBLE_CAT_COLS]

DEFAULT_MODEL_WEIGHTS = {
    "random_forest": 0.45,
    "extra_trees": 0.35,
    "elastic_net": 0.20,
}


def _feature_frame(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in ENSEMBLE_FEATS:
        if col not in out.columns:
            out[col] = np.nan
    for col in ENSEMBLE_NUM_COLS:
        out[col] = pd.to_numeric(out[col], errors="coerce")
    for col in ENSEMBLE_CAT_COLS:
        out[col] = out[col].fillna("unknown").astype(str)
    return out[ENSEMBLE_FEATS]


def _mask_features(df: pd.DataFrame, excluded_features: set[str]) -> pd.DataFrame:
    out = df.copy()
    for col in excluded_features:
        if col in ENSEMBLE_CAT_COLS:
            out[col] = "__excluded__"
        elif col in ENSEMBLE_FEATS:
            out[col] = 0.0
    return out


def _add_dynamic_driver_skill(
    df: pd.DataFrame,
    span: int = 12,
) -> tuple[pd.DataFrame, Dict[str, float], float]:
    """
    Build a pre-race driver rating without future information.

    Race performance combines normalized finishing strength (65%) with a
    teammate-relative score (35%). Each training row receives the driver's
    exponentially weighted rating *before* that race. The returned mapping is
    the rating after the latest completed race and is used for prediction.
    """
    out = df.copy()
    out["date"] = pd.to_datetime(out.get("date"), errors="coerce")
    out["finish_pos"] = pd.to_numeric(out["finish_pos"], errors="coerce")
    out["driver"] = out["driver"].astype(str)
    out["team"] = out["team"].astype(str)
    out = out.sort_values(["date", "year", "gp", "driver"], kind="mergesort")

    event_keys = ["year", "gp"]
    field_size = out.groupby(event_keys)["driver"].transform("count").clip(lower=2)
    out["_finish_strength"] = 1.0 - (
        (out["finish_pos"] - 1.0) / (field_size - 1.0)
    )
    team_strength = out.groupby(event_keys + ["team"])["_finish_strength"].transform("mean")
    out["_teammate_score"] = (
        0.5 + out["_finish_strength"] - team_strength
    ).clip(0.0, 1.0)
    out["_driver_performance"] = (
        0.65 * out["_finish_strength"] + 0.35 * out["_teammate_score"]
    )

    grouped = out.groupby("driver", sort=False)["_driver_performance"]
    out["driver_skill_rating"] = grouped.transform(
        lambda values: values.shift(1).ewm(
            span=span,
            adjust=False,
            min_periods=3,
        ).mean()
    )
    out["_post_race_driver_rating"] = grouped.transform(
        lambda values: values.ewm(
            span=span,
            adjust=False,
            min_periods=1,
        ).mean()
    )

    latest = (
        out.dropna(subset=["_post_race_driver_rating"])
        .groupby("driver", sort=False)
        .tail(1)
    )
    rating_map = dict(
        zip(latest["driver"], latest["_post_race_driver_rating"].astype(float))
    )
    default_rating = float(out["_post_race_driver_rating"].median(skipna=True))
    if not np.isfinite(default_rating):
        default_rating = 0.5
    out["driver_skill_rating"] = out["driver_skill_rating"].fillna(default_rating)
    return out, rating_map, default_rating


def _tree_preprocessor() -> ColumnTransformer:
    return ColumnTransformer(
        [
            ("num", SimpleImputer(strategy="median"), ENSEMBLE_NUM_COLS),
            ("cat", OneHotEncoder(handle_unknown="ignore"), ENSEMBLE_CAT_COLS),
        ]
    )


def _linear_preprocessor() -> ColumnTransformer:
    return ColumnTransformer(
        [
            (
                "num",
                Pipeline(
                    [
                        ("impute", SimpleImputer(strategy="median")),
                        ("scale", StandardScaler()),
                    ]
                ),
                ENSEMBLE_NUM_COLS,
            ),
            ("cat", OneHotEncoder(handle_unknown="ignore"), ENSEMBLE_CAT_COLS),
        ]
    )


@dataclass
class RaceEnsemble:
    models: Dict[str, Pipeline]
    weights: Dict[str, float]
    feature_list_: list[str]
    driver_skill_map_: Dict[str, float]
    default_driver_skill_: float
    excluded_features_: set[str]

    def component_predictions(self, df: pd.DataFrame) -> Dict[str, np.ndarray]:
        enriched = df.copy()
        enriched["driver_skill_rating"] = (
            enriched["driver"].astype(str).map(self.driver_skill_map_)
            .fillna(self.default_driver_skill_)
        )
        enriched = _mask_features(enriched, self.excluded_features_)
        X = _feature_frame(enriched)
        return {name: model.predict(X) for name, model in self.models.items()}

    def predict(self, df: pd.DataFrame) -> np.ndarray:
        components = self.component_predictions(df)
        return sum(self.weights[name] * pred for name, pred in components.items())


def train_ensemble(
    train_df: pd.DataFrame,
    model_weights: Dict[str, float] | None = None,
    random_state: int = 42,
    n_estimators: int = 800,
    excluded_features: set[str] | None = None,
) -> RaceEnsemble:
    """Train three deliberately different regressors on leakage-safe features."""
    clean = train_df.dropna(subset=["finish_pos", "grid_pos"]).copy()
    clean, driver_skill_map, default_driver_skill = _add_dynamic_driver_skill(clean)
    excluded = set(excluded_features or set())
    unknown_exclusions = excluded - set(ENSEMBLE_FEATS)
    if unknown_exclusions:
        raise ValueError(f"Unknown excluded features: {sorted(unknown_exclusions)}")
    clean = _mask_features(clean, excluded)
    X = _feature_frame(clean)
    y = pd.to_numeric(clean["finish_pos"], errors="coerce").astype(float)

    weights = dict(model_weights or DEFAULT_MODEL_WEIGHTS)
    total = float(sum(weights.values()))
    if total <= 0:
        raise ValueError("Ensemble model weights must sum to a positive value.")
    weights = {name: float(value) / total for name, value in weights.items()}

    models: Dict[str, Pipeline] = {
        "random_forest": Pipeline(
            [
                ("prep", _tree_preprocessor()),
                (
                    "regressor",
                    RandomForestRegressor(
                        n_estimators=n_estimators,
                        min_samples_leaf=8,
                        max_features=0.70,
                        bootstrap=True,
                        random_state=random_state,
                        n_jobs=-1,
                    ),
                ),
            ]
        ),
        "extra_trees": Pipeline(
            [
                ("prep", _tree_preprocessor()),
                (
                    "regressor",
                    ExtraTreesRegressor(
                        n_estimators=n_estimators,
                        min_samples_leaf=6,
                        max_features=0.80,
                        bootstrap=False,
                        random_state=random_state + 1,
                        n_jobs=-1,
                    ),
                ),
            ]
        ),
        "elastic_net": Pipeline(
            [
                ("prep", _linear_preprocessor()),
                (
                    "regressor",
                    ElasticNet(
                        alpha=0.05,
                        l1_ratio=0.15,
                        max_iter=20_000,
                        random_state=random_state,
                    ),
                ),
            ]
        ),
    }

    unknown = set(weights) - set(models)
    if unknown:
        raise ValueError(f"Unknown ensemble models: {sorted(unknown)}")
    models = {name: models[name] for name in weights}
    for model in models.values():
        model.fit(X, y)

    return RaceEnsemble(
        models=models,
        weights=weights,
        feature_list_=list(ENSEMBLE_FEATS),
        driver_skill_map_=driver_skill_map,
        default_driver_skill_=default_driver_skill,
        excluded_features_=excluded,
    )


def _tree_prediction_matrix(model: Pipeline, X: pd.DataFrame) -> np.ndarray:
    transformed = model.named_steps["prep"].transform(X)
    estimators = model.named_steps["regressor"].estimators_
    return np.column_stack([tree.predict(transformed) for tree in estimators])


def _aggregate_transformed_importance(
    model: Pipeline,
    values: np.ndarray,
) -> pd.Series:
    """Aggregate one-hot levels back to their original feature columns."""
    names = model.named_steps["prep"].get_feature_names_out()
    aggregated = pd.Series(0.0, index=ENSEMBLE_FEATS, dtype=float)

    for transformed_name, value in zip(names, np.asarray(values, dtype=float)):
        raw_name = transformed_name.split("__", 1)[-1]
        if raw_name in aggregated.index:
            feature = raw_name
        else:
            feature = next(
                (col for col in ENSEMBLE_CAT_COLS if raw_name.startswith(f"{col}_")),
                None,
            )
        if feature is not None:
            aggregated.loc[feature] += abs(float(value))

    total = aggregated.sum()
    return aggregated / total if total > 0 else aggregated


def ensemble_feature_importance(
    ensemble: RaceEnsemble,
    grid_alpha: float = 0.65,
) -> pd.DataFrame:
    """
    Return normalized, model-native ensemble importance.

    Tree impurity importance and absolute standardized Elastic Net
    coefficients are each normalized before applying ensemble weights. The
    starting grid is not an ML input; its direct share of the final blend is
    assigned to ``grid_pos``. Values describe model influence, not causal
    effects.
    """
    if not 0.0 <= grid_alpha <= 1.0:
        raise ValueError("grid_alpha must be between 0 and 1.")

    component_series: Dict[str, pd.Series] = {}
    for name, model in ensemble.models.items():
        regressor = model.named_steps["regressor"]
        if hasattr(regressor, "feature_importances_"):
            raw_values = regressor.feature_importances_
        else:
            raw_values = np.abs(np.ravel(regressor.coef_))
        component_series[name] = _aggregate_transformed_importance(model, raw_values)

    model_importance = sum(
        ensemble.weights[name] * importance
        for name, importance in component_series.items()
    )
    report_index = list(ENSEMBLE_FEATS) + ["grid_pos"]
    model_importance = model_importance.reindex(report_index, fill_value=0.0)
    component_series = {
        name: importance.reindex(report_index, fill_value=0.0)
        for name, importance in component_series.items()
    }
    final_importance = grid_alpha * model_importance
    final_importance.loc["grid_pos"] = 1.0 - grid_alpha

    report = pd.DataFrame(
        {
            "importance": final_importance,
            "model_ensemble_importance": model_importance,
            **{
                f"{name}_importance": importance
                for name, importance in component_series.items()
            },
        }
    )
    return report.sort_values("importance", ascending=False)


def predict_event_with_ensemble(
    ensemble: RaceEnsemble,
    features_df: pd.DataFrame,
    grid_alpha: float = 0.65,
    mc_samples: int = 1000,
    random_state: int = 42,
) -> pd.DataFrame:
    """
    Predict a coherent race order.

    Each Monte Carlo draw uses one complete RF tree and one complete Extra
    Trees tree for every driver. This retains race-level dependence and makes
    win/podium/top-10 probabilities agree with the final grid-blended ranking.
    """
    if not 0.0 <= grid_alpha <= 1.0:
        raise ValueError("grid_alpha must be between 0 and 1.")

    enriched = features_df.copy()
    enriched["driver_skill_rating"] = (
        enriched["driver"].astype(str).map(ensemble.driver_skill_map_)
        .fillna(ensemble.default_driver_skill_)
    )
    enriched = _mask_features(enriched, ensemble.excluded_features_)
    X = _feature_frame(enriched)
    components = ensemble.component_predictions(features_df)
    model_prediction = sum(
        ensemble.weights[name] * values for name, values in components.items()
    )
    grid = pd.to_numeric(features_df["grid_pos"], errors="coerce").to_numpy(float)
    if not np.isfinite(grid).all():
        fallback = np.nanmax(grid) + 1 if np.isfinite(grid).any() else len(grid)
        grid = np.where(np.isfinite(grid), grid, fallback)

    n = len(features_df)

    # Blend comparable within-race ranks, not raw position estimates. Tree
    # regressors shrink predictions toward the field mean, while the grid spans
    # the complete field; blending those raw values makes even a modest grid
    # weight dominate the final order.
    model_order = np.argsort(model_prediction, kind="mergesort")
    model_ranks = np.empty(n, dtype=int)
    model_ranks[model_order] = np.arange(1, n + 1)
    grid_order = np.argsort(grid, kind="mergesort")
    grid_ranks = np.empty(n, dtype=int)
    grid_ranks[grid_order] = np.arange(1, n + 1)
    blend_score = grid_alpha * model_ranks + (1.0 - grid_alpha) * grid_ranks

    out = features_df[["driver", "team", "grid_pos"]].copy()
    out["pred_finish_rf"] = components["random_forest"]
    out["pred_finish_extra_trees"] = components["extra_trees"]
    out["pred_finish_elastic_net"] = components["elastic_net"]
    out["pred_finish_model_ensemble"] = model_prediction
    out["pred_rank_model_ensemble"] = model_ranks
    out["grid_rank_component"] = grid_ranks
    out["blend_rank_score"] = blend_score
    # Keep the established column name for API/backtest compatibility. This is
    # now a rank score on the finishing-position scale.
    out["pred_finish"] = blend_score

    rng = np.random.default_rng(random_state)
    draws = max(int(mc_samples), 1)
    simulated_model = np.zeros((n, draws), dtype=float)

    for name, model in ensemble.models.items():
        weight = ensemble.weights[name]
        if name in {"random_forest", "extra_trees"}:
            tree_predictions = _tree_prediction_matrix(model, X)
            chosen = rng.integers(0, tree_predictions.shape[1], size=draws)
            simulated_model += weight * tree_predictions[:, chosen]
        else:
            simulated_model += weight * components[name][:, None]

    simulated_model_order = np.argsort(simulated_model, axis=0, kind="mergesort")
    simulated_model_ranks = np.empty_like(simulated_model_order)
    simulated_model_ranks[
        simulated_model_order, np.arange(draws)
    ] = np.arange(1, n + 1)[:, None]
    simulated_blend_scores = (
        grid_alpha * simulated_model_ranks
        + (1.0 - grid_alpha) * grid_ranks[:, None]
    )

    order = np.argsort(blend_score, kind="mergesort")
    ranks = np.empty(n, dtype=int)
    ranks[order] = np.arange(1, n + 1)
    out["pred_rank"] = ranks

    sample_order = np.argsort(simulated_blend_scores, axis=0, kind="mergesort")
    sample_ranks = np.empty_like(sample_order)
    sample_ranks[sample_order, np.arange(draws)] = np.arange(1, n + 1)[:, None]
    out["pred_std"] = sample_ranks.std(axis=1, ddof=1) if draws > 1 else 0.0
    out["pi68_low"] = np.quantile(sample_ranks, 0.16, axis=1)
    out["pi68_high"] = np.quantile(sample_ranks, 0.84, axis=1)
    out["pi95_low"] = np.quantile(sample_ranks, 0.025, axis=1)
    out["pi95_high"] = np.quantile(sample_ranks, 0.975, axis=1)
    out["pred_low"] = out["pi68_low"]
    out["pred_high"] = out["pi68_high"]
    out["p_win"] = (sample_ranks == 1).mean(axis=1)
    out["p_podium"] = (sample_ranks <= min(3, n)).mean(axis=1)
    out["p_top10"] = (sample_ranks <= min(10, n)).mean(axis=1)
    out["p_rank_pm1"] = (
        (sample_ranks >= ranks[:, None] - 1) & (sample_ranks <= ranks[:, None] + 1)
    ).mean(axis=1)
    out["ensemble_grid_alpha"] = grid_alpha
    out["ranking_mode_default"] = "ensemble_grid_blend"

    return out.sort_values("pred_rank").reset_index(drop=True)
