import pandas as pd


def apply_grid_model_blend(
    df: pd.DataFrame,
    alpha: float = 0.45,
    model_col: str = "pred_finish",
    grid_col: str = "grid_pos",
) -> pd.DataFrame:
    """
    Blend model prediction with grid position.

    alpha = 1.0 -> pure model
    alpha = 0.0 -> pure grid
    """
    out = df.copy()

    out[model_col] = pd.to_numeric(out[model_col], errors="coerce")
    out[grid_col] = pd.to_numeric(out[grid_col], errors="coerce")

    out["pred_finish_raw_model"] = out[model_col]

    out["pred_finish"] = (
        alpha * out[model_col]
        + (1.0 - alpha) * out[grid_col]
    )

    all_races = []

    group_cols = ["year", "gp"] if {"year", "gp"}.issubset(out.columns) else None

    if group_cols:
        groups = out.groupby(group_cols)
    else:
        groups = [(None, out)]

    for _, r in groups:
        r = r.copy()
        r = r.sort_values("pred_finish", ascending=True)
        r["pred_rank"] = range(1, len(r) + 1)
        all_races.append(r)

    return pd.concat(all_races, ignore_index=True)