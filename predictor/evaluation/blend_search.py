from pathlib import Path
import argparse
import numpy as np
import pandas as pd

from predictor.evaluation.metrics import summarize_metrics


def apply_blend(df: pd.DataFrame, alpha: float) -> pd.DataFrame:
    out = df.copy()

    out["grid_pos"] = pd.to_numeric(out["grid_pos"], errors="coerce")
    out["pred_finish"] = pd.to_numeric(out["pred_finish"], errors="coerce")

    out["blend_pred_finish"] = (
        alpha * out["pred_finish"]
        + (1.0 - alpha) * out["grid_pos"]
    )

    all_races = []

    for (year, gp), r in out.groupby(["year", "gp"]):
        r = r.copy()
        r = r.sort_values("blend_pred_finish", ascending=True)
        r["pred_rank"] = range(1, len(r) + 1)
        r["pred_finish"] = r["blend_pred_finish"]
        all_races.append(r)

    return pd.concat(all_races, ignore_index=True)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--predictions",
        required=True,
        help="Historical prediction CSV.",
    )

    parser.add_argument(
        "--output",
        default="reports/backtests/blend_search_summary.csv",
    )

    args = parser.parse_args()

    df = pd.read_csv(args.predictions)

    rows = []

    for alpha in np.round(np.arange(0.0, 1.01, 0.05), 2):
        blended = apply_blend(df, alpha)
        metrics = summarize_metrics(blended, model_name=f"blend_alpha_{alpha:.2f}")
        metrics["alpha"] = alpha
        rows.append(metrics)

    summary = pd.DataFrame(rows)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(output_path, index=False)

    print(summary.sort_values("mae_finish_position").head(10).to_string(index=False))
    print(f"\n[INFO] Saved blend search to {output_path}")


if __name__ == "__main__":
    main()