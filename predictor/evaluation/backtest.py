from __future__ import annotations

import argparse
from pathlib import Path
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import fastf1

from predictor.main import build_training_frame, build_predict_frame
from predictor.model import train_model, predict_event_with_uncertainty


BASELINE_FEATURE_COLS = [
    "driver_skill_prior",
    "team_prior_strength",
    "drv_form3",
    "team_form3",
    "driver_hist_strength",
    "team_hist_strength",
    "driver_strength_blend_2026",
    "team_strength_blend_2026",
]

def clean_prediction_grid_positions(pred_df: pd.DataFrame, actuals: pd.DataFrame) -> pd.DataFrame:
    """
    Clean grid_pos before prediction.

    This is valid for post-qualifying/pre-race backtests because official grid
    position is available before race start. It must not use finish_pos.
    """
    out = pred_df.copy()

    out["grid_pos"] = pd.to_numeric(out["grid_pos"], errors="coerce")
    out.loc[~np.isfinite(out["grid_pos"]), "grid_pos"] = np.nan
    out.loc[out["grid_pos"] <= 0, "grid_pos"] = np.nan

    if "actual_grid_pos" in actuals.columns:
        grid_map = (
            actuals[["driver", "actual_grid_pos"]]
            .dropna(subset=["actual_grid_pos"])
            .drop_duplicates(subset=["driver"])
            .set_index("driver")["actual_grid_pos"]
            .to_dict()
        )

        fallback_grid = out["driver"].map(grid_map)
        out["grid_pos"] = out["grid_pos"].fillna(fallback_grid)

    # Remaining missing grids go to the back
    missing = out["grid_pos"].isna()
    if missing.any():
        max_grid = out["grid_pos"].max(skipna=True)
        if pd.isna(max_grid):
            max_grid = len(out)

        out.loc[missing, "grid_pos"] = range(
            int(max_grid) + 1,
            int(max_grid) + 1 + missing.sum()
        )

    out["grid_pos"] = out["grid_pos"].astype(float)

    return out


def get_completed_races(year: int) -> list[dict]:
    schedule = fastf1.get_event_schedule(year, include_testing=False)

    if schedule.empty:
        return []

    races = []

    now = pd.Timestamp(datetime.now(timezone.utc))

    for _, row in schedule.iterrows():
        gp = row.get("EventName", None)
        event_date = row.get("EventDate", None)

        if gp is None or pd.isna(gp):
            continue

        if event_date is not None and not pd.isna(event_date):
            event_date_ts = pd.to_datetime(event_date, utc=True, errors="coerce")

            if pd.notna(event_date_ts) and event_date_ts > now:
                continue

        races.append({
            "year": int(year),
            "gp": str(gp),
            "date": str(event_date) if event_date is not None else "",
        })

    return races


def load_actual_results(year: int, gp: str) -> pd.DataFrame:
    session = fastf1.get_session(year, gp, "R")

    try:
        session.load(telemetry=False, weather=False, messages=False)
    except TypeError:
        session.load()

    results = session.results.copy()

    if results is None or results.empty:
        raise RuntimeError(f"No race results available for {gp} {year}")

    out = pd.DataFrame()

    if "Abbreviation" in results.columns:
        out["driver"] = results["Abbreviation"].astype(str)
    elif "Driver" in results.columns:
        out["driver"] = results["Driver"].astype(str)
    else:
        raise KeyError(f"Could not find driver abbreviation column in results for {gp} {year}")

    if "TeamName" in results.columns:
        out["actual_team"] = results["TeamName"].astype(str)

    if "Position" in results.columns:
        out["finish_pos"] = pd.to_numeric(results["Position"], errors="coerce")
    else:
        out["finish_pos"] = np.arange(1, len(results) + 1)

    if "GridPosition" in results.columns:
        out["actual_grid_pos"] = pd.to_numeric(results["GridPosition"], errors="coerce")

    out = out.dropna(subset=["finish_pos"]).copy()
    out["finish_pos"] = out["finish_pos"].astype(int)

    return out


def attach_actuals_and_features(
    pred_out: pd.DataFrame,
    pred_features: pd.DataFrame,
    actuals: pd.DataFrame,
    year: int,
    gp: str,
    date: str,
) -> pd.DataFrame:
    out = pred_out.copy()

    extra_cols = ["driver"] + [c for c in BASELINE_FEATURE_COLS if c in pred_features.columns]
    extra = pred_features[extra_cols].drop_duplicates(subset=["driver"]).copy()

    out = out.merge(extra, on="driver", how="left")
    out = out.merge(actuals, on="driver", how="left")

    out["year"] = year
    out["gp"] = gp
    out["date"] = date

    out = out.dropna(subset=["finish_pos"]).copy()
    out["finish_pos"] = out["finish_pos"].astype(int)

    ordered_cols = [
        "year",
        "gp",
        "date",
        "driver",
        "team",
        "grid_pos",
        "actual_grid_pos",
        "finish_pos",
        "pred_finish",
        "pred_rank",
        "pred_std",
        "p_win",
        "p_podium",
        "p_top10",
        "p_rank_pm1",
    ]

    ordered_cols = [c for c in ordered_cols if c in out.columns]
    remaining_cols = [c for c in out.columns if c not in ordered_cols]

    return out[ordered_cols + remaining_cols]


def backtest_one_race(
    year: int,
    gp: str,
    date: str,
    mc_samples: int,
) -> pd.DataFrame:
    print("\n" + "=" * 100)
    print(f"[BACKTEST] {year} - {gp}")
    print("=" * 100)

    print("[INFO] Building leakage-safe training frame...")
    train_df = build_training_frame(year, gp)

    if train_df.empty:
        raise RuntimeError(f"Training frame empty for {gp} {year}")

    print(f"[INFO] Training rows: {train_df.shape[0]}")

    print("[INFO] Training model without saving backend artifact...")
    model = train_model(train_df, save_model=False)

    print("[INFO] Building prediction frame...")
    pred_df = build_predict_frame(
        year,
        gp,
        train_df,
        use_sessions=False,
    )

    if pred_df.empty:
        raise RuntimeError(f"Prediction frame empty for {gp} {year}")

    print("[INFO] Loading actual race results/grid...")
    actuals = load_actual_results(year, gp)

    print("[INFO] Cleaning prediction grid positions...")
    pred_df = clean_prediction_grid_positions(pred_df, actuals)

    print("[INFO] Predicting...")
    pred_out = predict_event_with_uncertainty(
        model,
        pred_df,
        add_intervals=True,
        mc_samples=mc_samples,
        save_features=False,
    )

    final = attach_actuals_and_features(
        pred_out=pred_out,
        pred_features=pred_df,
        actuals=actuals,
        year=year,
        gp=gp,
        date=date,
    )

    if final.empty:
        raise RuntimeError(f"No joined prediction/actual rows for {gp} {year}")

    pred_winner = final.sort_values("pred_rank").iloc[0]["driver"]
    actual_winner = final.sort_values("finish_pos").iloc[0]["driver"]

    print(f"[RESULT] Pred winner: {pred_winner} | Actual winner: {actual_winner}")

    return final


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--years",
        nargs="+",
        type=int,
        default=[2023, 2024, 2025, 2026],
    )

    parser.add_argument(
        "--mc",
        type=int,
        default=500,
    )

    parser.add_argument(
        "--max_races_per_year",
        type=int,
        default=None,
        help="Use small value like 1 or 2 for testing.",
    )

    parser.add_argument(
        "--output",
        default="reports/backtests/historical_predictions_2023_2026.csv",
    )

    args = parser.parse_args()

    all_predictions = []
    failures = []

    for year in args.years:
        races = get_completed_races(year)

        if args.max_races_per_year is not None:
            races = races[: args.max_races_per_year]

        print(f"\n[INFO] Year {year}: found {len(races)} completed/scheduled-past races.")

        for race in races:
            try:
                result = backtest_one_race(
                    year=race["year"],
                    gp=race["gp"],
                    date=race["date"],
                    mc_samples=args.mc,
                )

                all_predictions.append(result)

            except Exception as exc:
                print(f"[WARN] Failed backtest for {year} {race['gp']}: {exc}")

                failures.append({
                    "year": year,
                    "gp": race["gp"],
                    "error": str(exc),
                })

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if all_predictions:
        final = pd.concat(all_predictions, ignore_index=True)
        final.to_csv(output_path, index=False)
        print(f"\n[INFO] Saved historical backtest predictions to {output_path}")
        print(f"[INFO] Shape: {final.shape}")
    else:
        print("\n[ERROR] No successful backtest predictions were generated.")

    if failures:
        failure_path = output_path.with_name(output_path.stem + "_failures.csv")
        pd.DataFrame(failures).to_csv(failure_path, index=False)
        print(f"[WARN] Saved failures to {failure_path}")


if __name__ == "__main__":
    main()