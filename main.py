# main.py  (package: F1_prediction_system)
from __future__ import annotations

import argparse
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
import fastf1

from .config import HIST_YEARS
from .data import build_training_until as build_until_data, get_target_drivers
from .features import (
    add_circuit_context_df,
    add_driver_team_form,
    merge_latest_forms,
    add_quali_proxy,
    add_live_strength_adjustments,
)
from .model import (
    train_model,
    predict_event_with_uncertainty,
    oob_errors,
    _prep_fe_matrix,
    _make_target,
    tree_importance_series,
    permutation_importance_series,
)

# Optional live-session feature builder
try:
    from .sessions import build_live_weekend_features
except Exception:
    build_live_weekend_features = None


# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------

def build_training_frame(target_year: int, target_gp: str) -> pd.DataFrame:
    """
    Build the historical training frame up to (but excluding) target race.
    """
    train_df = build_until_data(target_year, target_gp, hist_years=HIST_YEARS)
    train_df = add_driver_team_form(train_df)
    train_df = add_circuit_context_df(train_df)
    
    return train_df


def build_predict_frame(
    target_year: int,
    target_gp: str,
    train_df_with_forms: pd.DataFrame,
    use_sessions: bool = False,
) -> pd.DataFrame:
    """
    Build the prediction frame for the target race.

    Base flow:
      1) get target drivers
      2) add circuit context
      3) merge historical driver/team forms
      4) optionally merge live weekend features
      5) refresh blended live strength features
    """
    pred_df = get_target_drivers(target_year, target_gp)
    pred_df = add_circuit_context_df(pred_df)
    pred_df = merge_latest_forms(pred_df, train_df_with_forms)

    if use_sessions:
        if build_live_weekend_features is None:
            print("[WARN] --use_sessions was passed, but sessions.py is not available. Skipping live session features.")
        else:
            try:
                live_df = build_live_weekend_features(target_year, target_gp)

                if live_df is not None and not live_df.empty:
                    live_df = live_df.copy()

                    pred_df = pred_df.merge(
                        live_df,
                        on="driver",
                        how="left",
                        suffixes=("", "_live"),
                    )

                    if "team_live" in pred_df.columns:
                        pred_df["team"] = pred_df["team"].fillna(pred_df["team_live"])
                        pred_df = pred_df.drop(columns=["team_live"])

                    pred_df = add_live_strength_adjustments(pred_df)

                    preview_cols = [
                        c for c in [
                            "driver",
                            "team",
                            "driver_2026_session_strength",
                            "team_2026_strength",
                            "driver_strength_blend_2026",
                            "team_strength_blend_2026",
                        ]
                        if c in pred_df.columns
                    ]
                    if preview_cols:
                        print("\n[INFO] Live session calibration preview:")
                        print(
                            pred_df[preview_cols]
                            .sort_values(
                                by="team_strength_blend_2026"
                                if "team_strength_blend_2026" in pred_df.columns
                                else preview_cols[-1],
                                ascending=False,
                            )
                            .head(10)
                            .to_string(index=False)
                        )

                    print("[INFO] Added live weekend session features.")
                else:
                    print("[WARN] Live session feature frame is empty. Continuing without session features.")

            except Exception as e:
                print(f"[WARN] Failed to build live weekend session features: {e}")

    return pred_df


def _safe_load_model(path: str):
    """
    Try loading rich artifact first; fall back to plain joblib.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Model file not found: {p}")

    try:
        from .model import load_model_artifact
        model, meta = load_model_artifact(str(p))
        return model, meta
    except Exception:
        model = joblib.load(p)
        return model, {}


def _safe_save_model(model, path: str, meta: dict | None = None):
    """
    Try saving rich artifact; fall back to plain joblib.
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    try:
        from .model import save_model_artifact
        save_model_artifact(model, str(p), meta or {})
    except Exception:
        joblib.dump(model, p)
    return p.resolve()


def _zscore_series(s: pd.Series) -> pd.Series:
    """
    Safe z-score with NaN/zero-std handling.
    """
    s = pd.to_numeric(s, errors="coerce")
    mu = s.mean(skipna=True)
    sd = s.std(skipna=True)
    if pd.isna(sd) or sd == 0:
        return pd.Series(0.0, index=s.index)
    return ((s - mu) / sd).fillna(0.0)


def _recompute_rank_probs(out: pd.DataFrame, mc_samples: int = 0, random_state: int = 42) -> pd.DataFrame:
    """
    Recompute pred_rank and MC probabilities using the current pred_finish / pred_std.
    This is used after the live FP1/FP2 adjustment shifts pred_finish.
    """
    out = out.sort_values("pred_finish", ascending=True).reset_index(drop=True)
    out["pred_rank"] = np.arange(1, len(out) + 1)

    if mc_samples and mc_samples > 0 and "pred_std" in out.columns:
        rng = np.random.default_rng(random_state)
        mu = pd.to_numeric(out["pred_finish"], errors="coerce").to_numpy(dtype=float)
        sd = pd.to_numeric(out["pred_std"], errors="coerce").fillna(1.0).to_numpy(dtype=float)
        sd = np.maximum(sd, 1e-6)

        n = len(mu)
        samples = rng.normal(loc=mu[:, None], scale=sd[:, None], size=(n, mc_samples))
        samples = np.clip(samples, 1, max(n, 20))

        idx_sorted = np.argsort(samples, axis=0)
        ranks = np.empty_like(idx_sorted)
        ranks[idx_sorted, np.arange(mc_samples)] = np.arange(1, n + 1)[:, None]

        out["p_top10"] = (ranks <= min(10, n)).mean(axis=1)
        out["p_podium"] = (ranks <= min(3, n)).mean(axis=1)

        pr = out["pred_rank"].to_numpy()[:, None]
        out["p_rank_pm1"] = ((ranks >= (pr - 1)) & (ranks <= (pr + 1))).mean(axis=1)

    return out


def _apply_live_session_adjustment(
    out: pd.DataFrame,
    pred_df: pd.DataFrame,
    target_year: int,
    target_gp: str,
    use_sessions: bool,
    mc_samples: int,
) -> pd.DataFrame:
    """
    Australia-2026 one-off adjustment layer:
    use current-year FP1/FP2 live strength to calibrate the base RF output.

    This does NOT retrain the RF on raw FP columns.
    It adjusts the prediction after the RF has produced a base estimate.

    Intended use:
    - only for 2026 Australia
    - only when live sessions were requested
    """
    should_apply = (
        use_sessions
        and target_year == 2026
        and str(target_gp).strip().lower() == "australian grand prix"
    )
    if not should_apply:
        return out

    session_cols = [
        c for c in [
            "driver",
            "team",
            "driver_2026_session_strength",
            "team_2026_strength",
            "driver_strength_blend_2026",
            "team_strength_blend_2026",
        ]
        if c in pred_df.columns
    ]
    if "driver" not in session_cols:
        return out

    calib = pred_df[session_cols].drop_duplicates(subset=["driver"]).copy()
    out = out.merge(calib, on=["driver", "team"], how="left")

    # Preserve the pure model output for comparison
    if "pred_finish_model" not in out.columns:
        out["pred_finish_model"] = out["pred_finish"]
    if "pred_rank_model" not in out.columns:
        out["pred_rank_model"] = out["pred_rank"]

    team_live_z = _zscore_series(out["team_2026_strength"]) if "team_2026_strength" in out.columns else pd.Series(0.0, index=out.index)
    driver_live_z = _zscore_series(out["driver_2026_session_strength"]) if "driver_2026_session_strength" in out.columns else pd.Series(0.0, index=out.index)
    team_blend_z = _zscore_series(out["team_strength_blend_2026"]) if "team_strength_blend_2026" in out.columns else pd.Series(0.0, index=out.index)
    driver_blend_z = _zscore_series(out["driver_strength_blend_2026"]) if "driver_strength_blend_2026" in out.columns else pd.Series(0.0, index=out.index)

    # Australia-2026 calibration:
    # team pace matters most for a new-regs opener,
    # then driver-specific session pace,
    # then the blended historical/live strength.
    session_boost = (
        0.90 * team_live_z
        + 0.55 * driver_live_z
        + 0.35 * team_blend_z
        + 0.20 * driver_blend_z
    ).clip(lower=-2.5, upper=2.5)

    out["session_boost"] = session_boost

    # Lower finish position is better, so strong session pace reduces pred_finish
    max_pos = max(len(out), 20)
    out["pred_finish"] = (pd.to_numeric(out["pred_finish"], errors="coerce") - out["session_boost"]).clip(1, max_pos)

    # Shift intervals by the same deterministic adjustment
    for lo_col, hi_col in [("pi68_low", "pi68_high"), ("pi95_low", "pi95_high"), ("pred_low", "pred_high")]:
        if lo_col in out.columns:
            out[lo_col] = (pd.to_numeric(out[lo_col], errors="coerce") - out["session_boost"]).clip(1, max_pos)
        if hi_col in out.columns:
            out[hi_col] = (pd.to_numeric(out[hi_col], errors="coerce") - out["session_boost"]).clip(1, max_pos)

    out = _recompute_rank_probs(out, mc_samples=mc_samples, random_state=42)

    print("\n[INFO] Applied Australia-2026 FP1/FP2 session adjustment.")
    preview_cols = [
        c for c in [
            "driver",
            "team",
            "pred_finish_model",
            "pred_finish",
            "session_boost",
            "pred_rank_model",
            "pred_rank",
        ]
        if c in out.columns
    ]
    print(out[preview_cols].head(10).to_string(index=False))

    return out


# -------------------------------------------------------------------
# Main
# -------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="F1 Race Predictor (RF + engineered features)")

    parser.add_argument("--year", type=int, default=2025)
    parser.add_argument("--gp", type=str, required=True)

    # Weekend mode
    parser.add_argument(
        "--use_sessions",
        action="store_true",
        help="Augment prediction frame with live weekend session features (FP/Q) if sessions.py is available.",
    )
    parser.add_argument(
        "--preweekend",
        action="store_true",
        help="Force pre-weekend mode (ignore live session features and qualifying data).",
    )

    # Quali proxy controls
    parser.add_argument(
        "--preq",
        action="store_true",
        help="Force pre-qualifying mode (ignore Q and use quali proxy if grid is unavailable).",
    )
    parser.add_argument(
        "--proxy_window",
        type=int,
        default=3,
        help="Window for quali proxy rolling mean (when --preq or grid unknown).",
    )

    # Uncertainty controls
    parser.add_argument(
        "--mc",
        type=int,
        default=500,
        help="Monte Carlo samples for rank probabilities (0 disables).",
    )
    parser.add_argument(
        "--interval",
        type=int,
        choices=(68, 95),
        default=68,
        help="Confidence interval width to display in console (68 or 95).",
    )

    # Model persistence / reuse
    parser.add_argument(
        "--load_model",
        type=str,
        default=None,
        help="Path to a saved model .joblib (artifact or plain Pipeline).",
    )
    parser.add_argument(
        "--save_model",
        type=str,
        default=None,
        help="Where to save the trained model .joblib.",
    )
    parser.add_argument(
        "--auto_retrain",
        action="store_true",
        help="If a loaded model is stale (newer data or feature mismatch), retrain.",
    )
    parser.add_argument(
        "--force_load",
        action="store_true",
        help="Use the loaded model even if features changed (not recommended).",
    )

    # Reserved / target control
    parser.add_argument(
        "--use_conformal",
        action="store_true",
        help="Add split-conformal PIs (reserved; not wired yet).",
    )
    parser.add_argument(
        "--alpha",
        type=float,
        default=0.20,
        help="Conformal alpha (default 0.20 ~ 80% PI).",
    )
    parser.add_argument(
        "--delta_target",
        action="store_true",
        help="Train on finish-grid delta (positions gained/lost).",
    )
    parser.add_argument(
        "--absolute_target",
        action="store_true",
        help="Train on absolute finish_pos (overrides --delta_target).",
    )

    # Recency weighting
    parser.add_argument(
        "--half_life",
        type=int,
        default=None,
        help="Override recency half-life in days (exponential decay).",
    )

    # Feature importance
    parser.add_argument(
        "--show_importance",
        action="store_true",
        help="Print top-20 tree-based feature importances after training.",
    )
    parser.add_argument(
        "--perm_importance",
        type=int,
        default=0,
        help="If >0, compute permutation importance with N repeats (slower).",
    )

    args = parser.parse_args()
    target_year, target_gp = args.year, args.gp

    # ---------------------------------------------------------------
    # Build training frame
    # ---------------------------------------------------------------
    print(f"[INFO] Building training frame up to {target_gp} {target_year}…")
    train_df = build_training_frame(target_year, target_gp)
    print(f"[INFO] Training rows: {train_df.shape[0]}")
    print(
        train_df.sort_values("date")[["year", "gp", "date"]]
        .drop_duplicates("gp", keep="last")
        .tail(5)
    )
    print("Latest event in training:", train_df["gp"].iloc[train_df["date"].idxmax()])

    # ---------------------------------------------------------------
    # Load or train model
    # ---------------------------------------------------------------
    model = None
    loaded_meta = {}

    if args.load_model:
        try:
            model, loaded_meta = _safe_load_model(args.load_model)
            print(f"[INFO] Loaded model from {Path(args.load_model).resolve()}")

            try:
                train_clean = train_df.dropna(subset=["finish_pos"]).copy()
                _, feat_list_now = _prep_fe_matrix(train_clean)

                feat_list_saved = set(loaded_meta.get("feat_list", []))
                train_end_saved = pd.to_datetime(loaded_meta.get("train_end_date"))
                train_end_now = pd.to_datetime(train_df["date"]).max()

                feature_mismatch = bool(feat_list_saved) and (feat_list_saved != set(feat_list_now))
                data_stale = (
                    pd.notna(train_end_saved)
                    and pd.notna(train_end_now)
                    and train_end_now > train_end_saved
                )

                if feature_mismatch:
                    msg = "[WARN] Loaded model feature set differs from current pipeline."
                    if args.force_load:
                        print(msg + " Proceeding due to --force_load.")
                    elif args.auto_retrain:
                        print(msg + " Retraining due to --auto_retrain.")
                        model = None
                    else:
                        print(msg + " Consider retraining (or pass --auto_retrain).")

                if model is not None and data_stale and args.auto_retrain:
                    print("[INFO] Newer training data exists. Retraining due to --auto_retrain.")
                    model = None

            except Exception as e:
                print(f"[WARN] Could not fully validate loaded model metadata: {e}")

        except Exception as e:
            print(f"[WARN] Failed to load model: {e}. Will train a fresh model.")

    if model is None:
        print("[INFO] Training model…")
        model = train_model(train_df)

        errs = oob_errors(model, train_df)
        if errs:
            print(f"[OOB] R2={errs['oob_r2']:.3f} | MAE={errs['oob_mae']:.2f} | RMSE={errs['oob_rmse']:.2f}")
        else:
            print("[OOB] Not available")

        if args.show_importance:
            try:
                imp = tree_importance_series(model)
                print("\n[FEATURE IMPORTANCE] (tree-based, top 20)")
                print(imp.head(20).to_string())
                imp.to_csv("feature_importance_tree.csv", header=["importance"])
                print("[INFO] Saved tree feature importance to feature_importance_tree.csv")
            except Exception as e:
                print(f"[WARN] Could not compute tree-based importance: {e}")

        if args.perm_importance and args.perm_importance > 0:
            try:
                train_clean = train_df.dropna(subset=["finish_pos"]).copy()
                X_imp, _ = _prep_fe_matrix(train_clean)
                y_imp, _ = _make_target(train_clean)
                p = permutation_importance_series(
                    model,
                    X_imp,
                    y_imp,
                    n_repeats=args.perm_importance,
                )
                print("\n[PERMUTATION IMPORTANCE] (neg MAE impact, top 20)")
                print(p.head(20).to_string())
                p.to_csv("feature_importance_permutation.csv", header=["importance"])
                print("[INFO] Saved permutation feature importance to feature_importance_permutation.csv")
            except Exception as e:
                print(f"[WARN] Permutation importance failed: {e}")

        if args.save_model:
            try:
                train_clean = train_df.dropna(subset=["finish_pos"]).copy()
                _, feat_list_now = _prep_fe_matrix(train_clean)
            except Exception:
                feat_list_now = []

            meta = {
                "feat_list": feat_list_now,
                "train_rows": int(train_df.dropna(subset=["finish_pos"]).shape[0]),
                "train_start_date": str(pd.to_datetime(train_df["date"]).min()),
                "train_end_date": str(pd.to_datetime(train_df["date"]).max()),
                "hist_years": list(HIST_YEARS),
                "target_context": {"year": target_year, "gp": target_gp},
                "oob": oob_errors(model, train_df) or {},
                "model": "RandomForestRegressor",
                "code_version": "v4_australia_fp_adjustment",
            }
            saved_path = _safe_save_model(model, args.save_model, meta)
            print(f"[INFO] Saved model to {saved_path}")

    else:
        errs = oob_errors(model, train_df)
        if errs:
            print(f"[OOB] R2={errs['oob_r2']:.3f} | MAE={errs['oob_mae']:.2f} | RMSE={errs['oob_rmse']:.2f}")

    # ---------------------------------------------------------------
    # Build prediction frame
    # ---------------------------------------------------------------
    print(f"[INFO] Building prediction frame for {target_gp} {target_year}…")
    pred_df = build_predict_frame(
        target_year,
        target_gp,
        train_df,
        use_sessions=(args.use_sessions and not args.preweekend),
    )

    # ---------------------------------------------------------------
    # Qualifying / grid handling
    # ---------------------------------------------------------------
    if args.preq:
        try:
            session = fastf1.get_session(args.year, args.gp, "Q")
            session.load()

            if session.laps.empty:
                raise ValueError(f"No qualifying data available for {args.gp} {args.year}.")

            pred_df = pred_df.copy()
            pred_df["grid_pos"] = pred_df["driver"].map(
                dict(zip(session.laps["Driver"], session.laps["GridPosition"]))
            )

        except Exception as e:
            print(f"[WARNING] Failed to load qualifying data for {args.gp} {args.year}. Error: {e}")
            print(f"[INFO] Using qualifying proxy for {args.gp} {args.year}.")
            proxy_base = train_df[["driver", "team", "date", "grid_pos"]].dropna()
            pred_df = add_quali_proxy(pred_df, proxy_base, window=args.proxy_window)

    # ---------------------------------------------------------------
    # Sanity checks
    # ---------------------------------------------------------------
    if pred_df.empty:
        raise RuntimeError("Prediction frame is empty; no driver list available.")

    for col in ("driver", "team", "grid_pos"):
        if col not in pred_df.columns:
            raise RuntimeError(f"Prediction frame missing required column: {col}")

    # ---------------------------------------------------------------
    # Predict
    # ---------------------------------------------------------------
    print("[INFO] Predicting order…")
    out = predict_event_with_uncertainty(
        model,
        pred_df,
        add_intervals=True,
        mc_samples=args.mc,
    )

    # ---------------------------------------------------------------
    # Australia-2026 live FP1/FP2 adjustment layer
    # ---------------------------------------------------------------
    out = _apply_live_session_adjustment(
        out=out,
        pred_df=pred_df,
        target_year=target_year,
        target_gp=target_gp,
        use_sessions=(args.use_sessions and not args.preweekend),
        mc_samples=args.mc,
    )

    lo_col, hi_col = ("pi95_low", "pi95_high") if args.interval == 95 else ("pi68_low", "pi68_high")

    cols_to_print = [
        c for c in (
            "driver", "team", "grid_pos",
            "pred_finish", "pred_rank", "pred_std",
            lo_col, hi_col,
            "p_top10", "p_podium", "p_rank_pm1",
            "session_boost",
            "pred_finish_model",
            "pred_rank_model",
        ) if c in out.columns
    ]

    print("\nPredicted Top 10:")
    print(out[cols_to_print].head(10).to_string(index=False))

    # ---------------------------------------------------------------
    # Save output
    # ---------------------------------------------------------------
    out.to_csv("predicted_order.csv", index=False)
    print("\n[INFO] Saved full predictions to predicted_order.csv")


if __name__ == "__main__":
    main()