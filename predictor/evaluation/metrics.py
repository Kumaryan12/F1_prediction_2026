import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, brier_score_loss


def add_actual_event_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["actual_win"] = (df["finish_pos"] == 1).astype(int)
    df["actual_podium"] = (df["finish_pos"] <= 3).astype(int)
    df["actual_top10"] = (df["finish_pos"] <= 10).astype(int)

    return df


def winner_accuracy(df: pd.DataFrame) -> float:
    races = df[["year", "gp"]].drop_duplicates()
    correct = 0

    for _, race in races.iterrows():
        r = df[(df["year"] == race["year"]) & (df["gp"] == race["gp"])]

        pred_winner = r.sort_values("pred_rank").iloc[0]["driver"]
        actual_winner = r.sort_values("finish_pos").iloc[0]["driver"]

        correct += int(pred_winner == actual_winner)

    return correct / len(races) if len(races) else np.nan


def podium_overlap_accuracy(df: pd.DataFrame) -> float:
    races = df[["year", "gp"]].drop_duplicates()
    scores = []

    for _, race in races.iterrows():
        r = df[(df["year"] == race["year"]) & (df["gp"] == race["gp"])]

        pred_podium = set(r.sort_values("pred_rank").head(3)["driver"])
        actual_podium = set(r.sort_values("finish_pos").head(3)["driver"])

        scores.append(len(pred_podium & actual_podium) / 3)

    return float(np.mean(scores)) if scores else np.nan


def podium_exact_order_accuracy(df: pd.DataFrame) -> float:
    races = df[["year", "gp"]].drop_duplicates()
    scores = []

    for _, race in races.iterrows():
        r = df[(df["year"] == race["year"]) & (df["gp"] == race["gp"])]

        pred = list(r.sort_values("pred_rank").head(3)["driver"])
        actual = list(r.sort_values("finish_pos").head(3)["driver"])

        scores.append(int(pred == actual))

    return float(np.mean(scores)) if scores else np.nan


def top10_overlap_accuracy(df: pd.DataFrame) -> float:
    races = df[["year", "gp"]].drop_duplicates()
    scores = []

    for _, race in races.iterrows():
        r = df[(df["year"] == race["year"]) & (df["gp"] == race["gp"])]

        k = min(10, len(r))

        pred_top10 = set(r.sort_values("pred_rank").head(k)["driver"])
        actual_top10 = set(r.sort_values("finish_pos").head(k)["driver"])

        scores.append(len(pred_top10 & actual_top10) / k)

    return float(np.mean(scores)) if scores else np.nan


def finishing_mae(df: pd.DataFrame) -> float:
    valid = df[["finish_pos", "pred_finish"]].dropna()
    if valid.empty:
        return np.nan

    return mean_absolute_error(valid["finish_pos"], valid["pred_finish"])


def brier_for_event(df: pd.DataFrame, prob_col: str, event_col: str) -> float:
    valid = df[[prob_col, event_col]].dropna()

    if valid.empty:
        return np.nan

    return brier_score_loss(
        valid[event_col].astype(int),
        valid[prob_col].astype(float),
    )


def summarize_metrics(df: pd.DataFrame, model_name: str = "model") -> dict:
    df = add_actual_event_columns(df)

    out = {
        "model": model_name,
        "races": df[["year", "gp"]].drop_duplicates().shape[0],
        "winner_accuracy": winner_accuracy(df),
        "podium_overlap_accuracy": podium_overlap_accuracy(df),
        "podium_exact_order_accuracy": podium_exact_order_accuracy(df),
        "top10_overlap_accuracy": top10_overlap_accuracy(df),
        "mae_finish_position": finishing_mae(df),
    }

    if "p_podium" in df.columns:
        out["brier_podium"] = brier_for_event(df, "p_podium", "actual_podium")

    if "p_top10" in df.columns:
        out["brier_top10"] = brier_for_event(df, "p_top10", "actual_top10")

    if "p_win" in df.columns:
        out["brier_win"] = brier_for_event(df, "p_win", "actual_win")

    return out