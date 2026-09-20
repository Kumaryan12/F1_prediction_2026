from pathlib import Path
import argparse
import pandas as pd

from predictor.evaluation.metrics import summarize_metrics
from predictor.evaluation.baselines import (
    grid_baseline,
    pole_sitter_baseline,
    constructor_strength_baseline,
)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--predictions",
        required=True,
        help="CSV containing model predictions with actual finish_pos.",
    )

    parser.add_argument(
        "--output",
        default="reports/backtests/evaluation_summary.csv",
        help="Output CSV path.",
    )

    args = parser.parse_args()

    df = pd.read_csv(args.predictions)

    required_cols = {"year", "gp", "driver", "grid_pos", "finish_pos", "pred_finish", "pred_rank"}
    missing = required_cols - set(df.columns)

    if missing:
        raise KeyError(f"Missing required columns: {sorted(missing)}")

    rows = []

    rows.append(summarize_metrics(df, model_name="model"))

    grid_df = grid_baseline(df)
    rows.append(summarize_metrics(grid_df, model_name="grid_baseline"))

    pole_df = pole_sitter_baseline(df)
    rows.append(summarize_metrics(pole_df, model_name="pole_sitter_baseline"))

    try:
        constructor_df = constructor_strength_baseline(df)
        rows.append(summarize_metrics(constructor_df, model_name="constructor_strength_baseline"))
    except Exception as exc:
        print(f"[WARN] Constructor baseline skipped: {exc}")

    summary = pd.DataFrame(rows)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    summary.to_csv(output_path, index=False)

    print("\nEvaluation summary:")
    print(summary.to_string(index=False))

    print(f"\n[INFO] Saved evaluation summary to {output_path}")


if __name__ == "__main__":
    main()