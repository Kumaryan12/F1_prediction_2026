from __future__ import annotations
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

FEATS = [
    "grid_pos",
    "sc_prob", "vsc_prob", "pit_loss",
    "expected_stops", "overtake_index", "tow_importance",
    "is_low_df", "is_street", "long_straight_index",
    "braking_intensity", "warmup_penalty", "deg_rate", "stint_len_typical",

    # Track-shape / Abu Dhabi-oriented extras
    "surface_bumpiness", "wind_sensitivity", "track_limits_risk",
    "elevation_change_index", "mechanical_failure_risk",
    "corner_count", "avg_speed_kph",

    
    "rain_prob_race", "wet_lap_fraction", "wet_start_prob", "mixed_conditions_risk",

    
    "drv_form3", "team_form3",
    "driver_skill_prior",
    "street_driver_form3", "street_team_form3",
    "longstraight_driver_form3", "longstraight_team_form3",

    "team", "driver",
]








USE_DELTA_TARGET = True 

def _prep_fe_matrix(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    df = df.copy()

    num_maybe = [
        "grid_pos", "drv_form3", "team_form3", "sc_prob", "vsc_prob", "pit_loss",
    ]
    for c in num_maybe:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    for c in ("team", "driver"):
        if c in df.columns:
            df[c] = df[c].astype(str)

    present = [c for c in FEATS if c in df.columns]
    missing = [c for c in FEATS if c not in df.columns]
    for m in missing:
        df[m] = np.nan

    feat_list = present + missing  
    return df[feat_list], feat_list


def train_model(train_df: pd.DataFrame) -> Pipeline:
    df = train_df.copy().dropna(subset=["finish_pos"])

    X, feat_list = _prep_fe_matrix(df)
    y = df["finish_pos"].astype(float)

    cat_cols = [c for c in feat_list if c in ("team", "driver")]
    num_cols = [c for c in feat_list if c not in cat_cols]

    pre = ColumnTransformer(
        transformers=[
            ("num", SimpleImputer(strategy="median"), num_cols),
            ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols),
        ]
    )

    rf = RandomForestRegressor(
        n_estimators=8000,
        min_samples_leaf=16,
        max_depth=None,
        random_state=42,
        n_jobs=-1,
        oob_score=True,     
        bootstrap=True
    )

    model = Pipeline([
        ("prep", pre),
        ("rf", rf),
    ])
    model.fit(X, y)
    return model

def oob_errors(model, train_df: pd.DataFrame) -> Dict[str, float]:
    if "rf" not in model.named_steps:
        return {}

    rf = model.named_steps["rf"]
    if not getattr(rf, "oob_score", False) or not hasattr(rf, "oob_prediction_"):
        return {}

    df = train_df.copy().dropna(subset=["finish_pos"])
    y_true = df["finish_pos"].astype(float).to_numpy()
    y_oob = rf.oob_prediction_

    if y_oob is None or len(y_oob) != len(y_true):
        return {}

    oob_r2  = float(r2_score(y_true, y_oob))
    oob_mae = float(mean_absolute_error(y_true, y_oob))
    mse = float(mean_squared_error(y_true, y_oob))  
    oob_rmse = float(np.sqrt(mse))
    return {"oob_r2": oob_r2, "oob_mae": oob_mae, "oob_rmse": oob_rmse}



def predict_event_with_uncertainty(
    model: Pipeline,
    features_df: pd.DataFrame,
    add_intervals: bool = True,
    mc_samples: int = 0,
    random_state: int = 42
) -> pd.DataFrame:
    
    X_raw, _ = _prep_fe_matrix(features_df.copy())
    prep = model.named_steps["prep"]
    rf = model.named_steps["rf"]

    pred_mean = model.predict(X_raw)

    
    Xp = prep.transform(X_raw)  
    tree_preds = np.column_stack([est.predict(Xp) for est in rf.estimators_])  # (n, n_trees)
    pred_std = tree_preds.std(axis=1, ddof=1)

    # Assemble output
    out = features_df[["driver", "team", "grid_pos"]].copy()
    out["pred_finish"] = pred_mean
    out["pred_std"] = pred_std

    # Rank by expected finish (lower is better)
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
        sd = np.maximum(out["pred_std"].to_numpy(), 1e-6)  # avoid zero std

        n = len(mu)
        samples = rng.normal(loc=mu[:, None], scale=sd[:, None], size=(n, mc_samples))

        
        idx_sorted = np.argsort(samples, axis=0)               # (n, mc)
        ranks = np.empty_like(idx_sorted)
        ranks[idx_sorted, np.arange(mc_samples)] = np.arange(1, n + 1)[:, None]

        out["p_top10"] = (ranks <= 10).mean(axis=1)
        out["p_podium"] = (ranks <= 3).mean(axis=1)

        pr = out["pred_rank"].to_numpy()[:, None]
        out["p_rank_pm1"] = ((ranks >= (pr - 1)) & (ranks <= (pr + 1))).mean(axis=1)

    return out

def permutation_importance_series(model: Pipeline, X_df: pd.DataFrame, y: pd.Series, n_repeats: int = 10):
    from sklearn.inspection import permutation_importance
    r = permutation_importance(model, X_df, y, n_repeats=n_repeats,
                               random_state=42, scoring="neg_mean_absolute_error")
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
        # strip transformer prefixes like 'num__'/'cat__' for readability
        imp.index = [n.split("__", 1)[-1] for n in imp.index]
    return imp.sort_values(ascending=False)

def _make_target(df: pd.DataFrame) -> Tuple[pd.Series, pd.Series | None]:
    if USE_DELTA_TARGET:
        y = (df["finish_pos"] - df["grid_pos"]).astype(float)  # positions gained/lost
        anchor = df["grid_pos"].astype(float)
        return y, anchor
    else:
        return df["finish_pos"].astype(float), None
