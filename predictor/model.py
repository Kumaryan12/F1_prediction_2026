from __future__ import annotations
from typing import Dict, List, Tuple
from pathlib import Path
import joblib

import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error


# -------------------------------------------------------------------
# Save path
# -------------------------------------------------------------------
DATA_DIR = Path(r"C:\Users\Aryan\F1_prediction_system\backend\app\data")


# -------------------------------------------------------------------
# Feature list (China-ready, Australia-specific features removed)
# -------------------------------------------------------------------
FEATS = [
    # Sunday starting order
    "grid_pos",

    # Core circuit priors
    "sc_prob", "vsc_prob", "pit_loss",
    "expected_stops", "overtake_index", "tow_importance",
    "is_low_df", "is_street", "long_straight_index",
    "braking_intensity", "warmup_penalty", "deg_rate", "stint_len_typical",

    # Track / layout extras
    "surface_bumpiness",
    "wind_sensitivity",
    "track_limits_risk",
    "elevation_change_index",
    "mechanical_failure_risk",
    "corner_count",
    "avg_speed_kph",

    # Weather
    "rain_prob_race",
    "wet_lap_fraction",
    "wet_start_prob",
    "mixed_conditions_risk",

    # Driver / team priors and historical form
    "driver_skill_prior",
    "team_prior_strength",
    "rookie_flag",
    "returnee_flag",

    "drv_form3",
    "team_form3",
    "longstraight_driver_form3",
    "longstraight_team_form3",

    # Historical-strength helper columns
    "driver_hist_strength",
    "team_hist_strength",

    # Blended 2026-adjusted strength
    "driver_strength_blend_2026",
    "team_strength_blend_2026",

    # Categoricals
    "team",
    "driver",
]

CAT_COLS = ["team", "driver"]
NUM_COLS = [c for c in FEATS if c not in CAT_COLS]

# Train on finish_pos - grid_pos
USE_DELTA_TARGET = True


# -------------------------------------------------------------------
# Preprocessing helpers
# -------------------------------------------------------------------

def _prep_fe_matrix(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    """
    Coerce dtypes, add missing FEATS as NaN, and return (X, feat_list).
    """
    df = df.copy()

    for col in FEATS:
        if col not in df.columns:
            df[col] = np.nan

    for col in NUM_COLS:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    for col in CAT_COLS:
        df[col] = df[col].astype(str)

    feat_list = list(FEATS)
    return df[feat_list], feat_list


def _make_target(df: pd.DataFrame) -> Tuple[pd.Series, pd.Series | None]:
    """
    Return (y_target, anchor).

    If using delta target:
        y = finish_pos - grid_pos
        anchor = grid_pos
    else:
        y = finish_pos
        anchor = None
    """
    if USE_DELTA_TARGET:
        y = (
            pd.to_numeric(df["finish_pos"], errors="coerce")
            - pd.to_numeric(df["grid_pos"], errors="coerce")
        ).astype(float)
        anchor = pd.to_numeric(df["grid_pos"], errors="coerce").astype(float)
        return y, anchor
    else:
        return pd.to_numeric(df["finish_pos"], errors="coerce").astype(float), None


# -------------------------------------------------------------------
# Training
# -------------------------------------------------------------------

def train_model(train_df: pd.DataFrame) -> Pipeline:
    """
    Fit a RandomForest pipeline with imputation + one-hot for categoricals.
    """
    df = train_df.copy().dropna(subset=["finish_pos", "grid_pos"])

    X, feat_list = _prep_fe_matrix(df)
    y, _ = _make_target(df)

    pre = ColumnTransformer(
        transformers=[
            ("num", SimpleImputer(strategy="median"), NUM_COLS),
            ("cat", OneHotEncoder(handle_unknown="ignore"), CAT_COLS),
        ]
    )

    rf = RandomForestRegressor(
        n_estimators=1200,
        min_samples_leaf=16,
        max_depth=None,
        random_state=42,
        n_jobs=-1,
        oob_score=True,
        bootstrap=True,
    )

    model = Pipeline([
        ("prep", pre),
        ("rf", rf),
    ])

    model.fit(X, y)

    model.feature_list_ = feat_list
    model.use_delta_target_ = USE_DELTA_TARGET
    model.target_name_ = "finish_minus_grid" if USE_DELTA_TARGET else "finish_pos"

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    model_path = DATA_DIR / "random_forest_model.pkl"
    joblib.dump(model, model_path)
    print(f"✅ Model successfully saved to: {model_path}")

    return model


# -------------------------------------------------------------------
# Evaluation
# -------------------------------------------------------------------

def oob_errors(model: Pipeline, train_df: pd.DataFrame) -> Dict[str, float]:
    """
    Return OOB R², MAE, RMSE on finish-position scale.
    """
    if "rf" not in model.named_steps:
        return {}

    rf = model.named_steps["rf"]
    if not getattr(rf, "oob_score", False) or not hasattr(rf, "oob_prediction_"):
        return {}

    df = train_df.copy().dropna(subset=["finish_pos", "grid_pos"])
    y_true_finish = pd.to_numeric(df["finish_pos"], errors="coerce").to_numpy()
    y_oob = rf.oob_prediction_

    if y_oob is None or len(y_oob) != len(y_true_finish):
        return {}

    if getattr(model, "use_delta_target_", False):
        anchor = pd.to_numeric(df["grid_pos"], errors="coerce").to_numpy()
        y_oob_finish = anchor + y_oob
    else:
        y_oob_finish = y_oob

    oob_r2 = float(r2_score(y_true_finish, y_oob_finish))
    oob_mae = float(mean_absolute_error(y_true_finish, y_oob_finish))
    mse = float(mean_squared_error(y_true_finish, y_oob_finish))
    oob_rmse = float(np.sqrt(mse))

    return {
        "oob_r2": oob_r2,
        "oob_mae": oob_mae,
        "oob_rmse": oob_rmse,
    }


# -------------------------------------------------------------------
# Prediction + uncertainty
# -------------------------------------------------------------------

def predict_event_with_uncertainty(
    model: Pipeline,
    features_df: pd.DataFrame,
    add_intervals: bool = True,
    mc_samples: int = 0,
    random_state: int = 42,
) -> pd.DataFrame:
    """
    Predict finish positions and uncertainty bands.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    features_path = DATA_DIR / "current_race_features.csv"
    features_df.to_csv(features_path, index=False)
    print(f"✅ Features successfully saved to: {features_path}")

    X_raw, _ = _prep_fe_matrix(features_df.copy())
    prep = model.named_steps["prep"]
    rf = model.named_steps["rf"]

    grid_anchor = pd.to_numeric(features_df["grid_pos"], errors="coerce").to_numpy()

    pred_raw = model.predict(X_raw)

    if getattr(model, "use_delta_target_", False):
        pred_finish = grid_anchor + pred_raw
    else:
        pred_finish = pred_raw

    Xp = prep.transform(X_raw)
    tree_preds_raw = np.column_stack([est.predict(Xp) for est in rf.estimators_])

    if getattr(model, "use_delta_target_", False):
        tree_preds_finish = grid_anchor[:, None] + tree_preds_raw
    else:
        tree_preds_finish = tree_preds_raw

    pred_std = tree_preds_finish.std(axis=1, ddof=1)

    out = features_df[["driver", "team", "grid_pos"]].copy()
    out["pred_finish"] = pred_finish
    out["pred_std"] = pred_std

    out = out.sort_values("pred_finish", ascending=True).reset_index(drop=True)
    out["pred_rank"] = np.arange(1, len(out) + 1)

    if add_intervals:
        lo68 = np.clip(out["pred_finish"] - 1.00 * out["pred_std"], 1, 20)
        hi68 = np.clip(out["pred_finish"] + 1.00 * out["pred_std"], 1, 20)
        lo95 = np.clip(out["pred_finish"] - 1.96 * out["pred_std"], 1, 20)
        hi95 = np.clip(out["pred_finish"] + 1.96 * out["pred_std"], 1, 20)

        out["pi68_low"] = lo68
        out["pi68_high"] = hi68
        out["pi95_low"] = lo95
        out["pi95_high"] = hi95

        out["pred_low"] = lo68
        out["pred_high"] = hi68

    if mc_samples and mc_samples > 0:
        rng = np.random.default_rng(random_state)
        mu = out["pred_finish"].to_numpy()
        sd = np.maximum(out["pred_std"].to_numpy(), 1e-6)

        n = len(mu)
        samples = rng.normal(loc=mu[:, None], scale=sd[:, None], size=(n, mc_samples))
        samples = np.clip(samples, 1, 20)

        idx_sorted = np.argsort(samples, axis=0)
        ranks = np.empty_like(idx_sorted)
        ranks[idx_sorted, np.arange(mc_samples)] = np.arange(1, n + 1)[:, None]

        out["p_top10"] = (ranks <= 10).mean(axis=1)
        out["p_podium"] = (ranks <= 3).mean(axis=1)

        pr = out["pred_rank"].to_numpy()[:, None]
        out["p_rank_pm1"] = ((ranks >= (pr - 1)) & (ranks <= (pr + 1))).mean(axis=1)

    return out


# -------------------------------------------------------------------
# Importance helpers
# -------------------------------------------------------------------

def permutation_importance_series(
    model: Pipeline,
    X_df: pd.DataFrame,
    y: pd.Series,
    n_repeats: int = 10,
) -> pd.Series:
    from sklearn.inspection import permutation_importance

    r = permutation_importance(
        model,
        X_df,
        y,
        n_repeats=n_repeats,
        random_state=42,
        scoring="neg_mean_absolute_error",
    )
    return pd.Series(r.importances_mean, index=X_df.columns).sort_values(ascending=False)


def model_feature_names(model: Pipeline) -> List[str]:
    pre: ColumnTransformer = model.named_steps["prep"]
    try:
        in_feats = getattr(model, "feature_list_", None)
        names = pre.get_feature_names_out(in_feats if in_feats is not None else None)
        return list(names)
    except Exception:
        return []


def tree_importance_series(model: Pipeline) -> pd.Series:
    rf: RandomForestRegressor = model.named_steps["rf"]
    names = model_feature_names(model)
    imp = pd.Series(rf.feature_importances_, index=names if names else None)

    if names:
        imp.index = [n.split("__", 1)[-1] for n in imp.index]

    return imp.sort_values(ascending=False)