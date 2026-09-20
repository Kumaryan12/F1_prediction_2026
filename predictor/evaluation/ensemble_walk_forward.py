from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from predictor.data import build_training_min
from predictor.ensemble import predict_event_with_ensemble, train_ensemble
from predictor.evaluation.metrics import summarize_metrics
from predictor.features import add_circuit_context_df, add_driver_team_form


def apply_rank_blend(predictions: pd.DataFrame, alpha: float) -> pd.DataFrame:
    """Apply one frozen ML/grid rank weight independently within each race."""
    out = predictions.copy()
    out["pred_finish"] = (
        alpha * pd.to_numeric(out["pred_rank_model_ensemble"], errors="coerce")
        + (1.0 - alpha) * pd.to_numeric(out["grid_rank_component"], errors="coerce")
    )
    out["pred_rank"] = (
        out.groupby(["year", "gp"])["pred_finish"]
        .rank(method="first", ascending=True)
        .astype(int)
    )
    out["rank_blend_alpha"] = alpha
    return out


def mean_race_spearman(df: pd.DataFrame) -> float:
    scores = []
    for _, race in df.groupby(["year", "gp"], sort=False):
        valid = race[["pred_rank", "finish_pos"]].dropna()
        if len(valid) > 1:
            scores.append(float(spearmanr(valid["pred_rank"], valid["finish_pos"]).statistic))
    return float(np.mean(scores)) if scores else np.nan


def score_alphas(predictions: pd.DataFrame, alphas: list[float]) -> pd.DataFrame:
    rows = []
    for alpha in alphas:
        blended = apply_rank_blend(predictions, alpha)
        # Probabilities in the cached walk-forward rows belong to the original
        # simulation setting. They must not be scored after changing alpha
        # unless the simulations are rerun with that frozen blend.
        point_only = blended.drop(
            columns=["p_win", "p_podium", "p_top10"], errors="ignore"
        )
        metrics = summarize_metrics(point_only, model_name=f"rank_blend_{alpha:.2f}")
        metrics["spearman"] = mean_race_spearman(blended)
        metrics["alpha"] = alpha
        rows.append(metrics)
    return pd.DataFrame(rows)


def build_walk_forward_predictions(
    years: list[int],
    min_train_races: int = 12,
    n_estimators: int = 250,
    mc_samples: int = 250,
) -> pd.DataFrame:
    """Generate predictions where every model sees only earlier race dates."""
    raw = build_training_min(years)
    featured = add_circuit_context_df(add_driver_team_form(raw))
    featured["date"] = pd.to_datetime(featured["date"], errors="coerce")

    events = (
        featured[["year", "gp", "date"]]
        .drop_duplicates()
        .sort_values(["date", "year", "gp"])
        .reset_index(drop=True)
    )
    predictions = []

    for event_index, event in events.iterrows():
        if event_index < min_train_races:
            continue
        train = featured.loc[featured["date"] < event["date"]].copy()
        test = featured.loc[
            (featured["year"] == event["year"]) & (featured["gp"] == event["gp"])
        ].copy()
        if train.empty or test.empty:
            continue

        model = train_ensemble(train, n_estimators=n_estimators)
        forecast = predict_event_with_ensemble(
            model,
            test.drop(columns=["finish_pos"], errors="ignore"),
            grid_alpha=1.0,
            mc_samples=mc_samples,
            random_state=42 + int(event_index),
        )
        actual = test[["driver", "finish_pos"]].drop_duplicates("driver")
        forecast = forecast.merge(actual, on="driver", how="inner")
        forecast["year"] = int(event["year"])
        forecast["gp"] = str(event["gp"])
        forecast["date"] = event["date"]
        predictions.append(forecast)
        print(
            f"[WALK-FORWARD] {event['year']} {event['gp']}: "
            f"train={train[['year', 'gp']].drop_duplicates().shape[0]} races, "
            f"predict={len(forecast)} drivers"
        )

    if not predictions:
        raise RuntimeError("No walk-forward predictions were produced.")
    return pd.concat(predictions, ignore_index=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Leakage-safe ensemble walk-forward benchmark")
    parser.add_argument("--years", nargs="+", type=int, default=[2023, 2024, 2025])
    parser.add_argument("--tune_through_year", type=int, default=2024)
    parser.add_argument("--test_year", type=int, default=2025)
    parser.add_argument("--min_train_races", type=int, default=12)
    parser.add_argument("--n_estimators", type=int, default=250)
    parser.add_argument("--mc", type=int, default=250)
    parser.add_argument("--output_dir", default="reports/walk_forward")
    args = parser.parse_args()

    if args.test_year <= args.tune_through_year:
        raise ValueError("test_year must be later than tune_through_year")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    predictions = build_walk_forward_predictions(
        years=args.years,
        min_train_races=args.min_train_races,
        n_estimators=args.n_estimators,
        mc_samples=args.mc,
    )
    predictions.to_csv(output_dir / "walk_forward_predictions.csv", index=False)

    development = predictions[predictions["year"] <= args.tune_through_year].copy()
    test = predictions[predictions["year"] == args.test_year].copy()
    if development.empty or test.empty:
        raise RuntimeError("Development or test split is empty; adjust years and split options.")

    alphas = [round(value, 2) for value in np.arange(0.0, 1.01, 0.05)]
    search = score_alphas(development, alphas)
    search.to_csv(output_dir / "alpha_search_development.csv", index=False)
    best_alpha = float(search.sort_values("mae_finish_position").iloc[0]["alpha"])

    frozen_test = apply_rank_blend(test, best_alpha)
    frozen_test.to_csv(output_dir / "frozen_test_predictions.csv", index=False)
    test_summary = score_alphas(test, [best_alpha])
    test_summary["selected_on"] = f"years <= {args.tune_through_year}"
    test_summary.to_csv(output_dir / "frozen_test_summary.csv", index=False)
    test_comparison = score_alphas(test, sorted({0.0, best_alpha, 1.0}))
    test_comparison.to_csv(output_dir / "test_grid_blend_model_comparison.csv", index=False)

    print("\n[DEVELOPMENT] Best rank-blend weights by MAE")
    print(search.sort_values("mae_finish_position").head(10).to_string(index=False))
    print(f"\n[FROZEN TEST] {args.test_year}, alpha={best_alpha:.2f}")
    print(test_summary.to_string(index=False))
    print("\n[TEST COMPARISON] Grid vs frozen blend vs grid-free ML")
    print(test_comparison.to_string(index=False))


if __name__ == "__main__":
    main()
