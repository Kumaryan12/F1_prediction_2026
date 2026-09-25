from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from predictor.data import build_training_min
from predictor.evaluation.ensemble_walk_forward import (
    build_walk_forward_predictions,
    score_alphas,
)
from predictor.features import add_circuit_context_df, add_driver_team_form


ABLATIONS: dict[str, set[str]] = {
    "full_model": set(),
    "without_driver_skill": {"driver_skill_rating"},
    "without_identities": {"driver", "team"},
    "without_recent_form": {"drv_form3", "team_form3"},
    "without_archetype_form": {
        "highdf_driver_form3",
        "highdf_team_form3",
        "longstraight_driver_form3",
        "longstraight_team_form3",
    },
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Walk-forward feature-block ablation study")
    parser.add_argument("--years", nargs="+", type=int, default=[2023, 2024])
    parser.add_argument("--min_train_races", type=int, default=12)
    parser.add_argument("--n_estimators", type=int, default=100)
    parser.add_argument("--output_dir", default="reports/walk_forward/ablations")
    args = parser.parse_args()

    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    raw = build_training_min(args.years)
    featured = add_circuit_context_df(add_driver_team_form(raw))
    alphas = [round(value, 2) for value in np.arange(0.0, 1.01, 0.05)]
    summary_rows = []

    for name, excluded in ABLATIONS.items():
        print(f"\n[ABLATION] {name}: excluded={sorted(excluded)}")
        predictions = build_walk_forward_predictions(
            years=args.years,
            min_train_races=args.min_train_races,
            n_estimators=args.n_estimators,
            mc_samples=1,
            excluded_features=excluded,
            featured_df=featured,
        )
        predictions.to_csv(output / f"{name}_predictions.csv", index=False)
        search = score_alphas(predictions, alphas)
        search.to_csv(output / f"{name}_alpha_search.csv", index=False)
        best = search.sort_values("mae_finish_position").iloc[0].to_dict()
        best["ablation"] = name
        best["excluded_features"] = "|".join(sorted(excluded))
        summary_rows.append(best)

    summary = pd.DataFrame(summary_rows).sort_values("mae_finish_position")
    summary.to_csv(output / "ablation_summary.csv", index=False)
    print("\n[ABLATION SUMMARY]")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
