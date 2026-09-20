from pathlib import Path
import argparse
import pandas as pd

from predictor.evaluation.metrics import summarize_metrics
from predictor.evaluation.blend_config import FROZEN_BLEND_ALPHA


def apply_blend(df: pd.DataFrame, alpha: float) -> pd.DataFrame:
    out = df.copy()

    out["raw_pred_finish"] = pd.to_numeric(out["pred_finish"], errors="coerce")
    out["raw_pred_rank"] = out["pred_rank"]

    out["grid_pos"] = pd.to_numeric(out["grid_pos"], errors="coerce")

    out["calibrated_pred_finish"] = (
        alpha * out["raw_pred_finish"]
        + (1.0 - alpha) * out["grid_pos"]
    )

    all_races = []

    for (year, gp), r in out.groupby(["year", "gp"]):
        r = r.copy()
        r = r.sort_values("calibrated_pred_finish", ascending=True)
        r["pred_finish"] = r["calibrated_pred_finish"]
        r["pred_rank"] = range(1, len(r) + 1)
        r["calibrated_pred_rank"] = r["pred_rank"]
        r["blend_alpha"] = alpha
        all_races.append(r)

    return pd.concat(all_races, ignore_index=True)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--predictions", required=True)
    parser.add_argument("--output-predictions", required=True)
    parser.add_argument("--output-summary", required=True)

    args = parser.parse_args()

    df = pd.read_csv(args.predictions)

    blended = apply_blend(df, alpha=FROZEN_BLEND_ALPHA)

    Path(args.output_predictions).parent.mkdir(parents=True, exist_ok=True)
    blended.to_csv(args.output_predictions, index=False)

    summary = pd.DataFrame([
        summarize_metrics(blended, model_name=f"frozen_blend_alpha_{FROZEN_BLEND_ALPHA}")
    ])

    Path(args.output_summary).parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(args.output_summary, index=False)

    print(summary.to_string(index=False))
    print(f"\n[INFO] Saved blended predictions to {args.output_predictions}")
    print(f"[INFO] Saved blended summary to {args.output_summary}")


if __name__ == "__main__":
    main()