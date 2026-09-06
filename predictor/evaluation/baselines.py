import numpy as np
import pandas as pd


def _clean_grid_positions(df: pd.DataFrame) -> pd.DataFrame:
    """
    Make grid positions safe for baseline ranking.

    Rules:
    1. Convert grid_pos to numeric.
    2. Treat NaN, inf, and <=0 as missing.
    3. If actual_grid_pos exists, use it as fallback.
    4. Remaining missing values are placed at the back of that race.
    """
    out = df.copy()

    out["grid_pos"] = pd.to_numeric(out["grid_pos"], errors="coerce")
    out.loc[~np.isfinite(out["grid_pos"]), "grid_pos"] = np.nan
    out.loc[out["grid_pos"] <= 0, "grid_pos"] = np.nan

    if "actual_grid_pos" in out.columns:
        out["actual_grid_pos"] = pd.to_numeric(out["actual_grid_pos"], errors="coerce")
        out.loc[~np.isfinite(out["actual_grid_pos"]), "actual_grid_pos"] = np.nan
        out.loc[out["actual_grid_pos"] <= 0, "actual_grid_pos"] = np.nan

        out["grid_pos"] = out["grid_pos"].fillna(out["actual_grid_pos"])

    # Any remaining missing grid values go to the back within each race
    def fill_group(g: pd.DataFrame) -> pd.DataFrame:
        g = g.copy()
        max_grid = g["grid_pos"].max(skipna=True)

        if pd.isna(max_grid):
            max_grid = len(g)

        missing_count = g["grid_pos"].isna().sum()

        if missing_count > 0:
            filler = range(int(max_grid) + 1, int(max_grid) + 1 + missing_count)
            g.loc[g["grid_pos"].isna(), "grid_pos"] = list(filler)

        return g

    out = out.groupby(["year", "gp"], group_keys=False).apply(fill_group)

    out["grid_pos"] = out["grid_pos"].astype(float)

    return out


def grid_baseline(df: pd.DataFrame) -> pd.DataFrame:
    """
    Baseline: predicted finish order = cleaned starting grid order.
    """
    out = _clean_grid_positions(df)

    out["pred_rank"] = (
        out.groupby(["year", "gp"])["grid_pos"]
        .rank(method="first", ascending=True)
        .astype(int)
    )

    out["pred_finish"] = out["pred_rank"].astype(float)

    out["p_win"] = (out["pred_rank"] == 1).astype(float)
    out["p_podium"] = (out["pred_rank"] <= 3).astype(float)
    out["p_top10"] = (out["pred_rank"] <= 10).astype(float)

    return out


def pole_sitter_baseline(df: pd.DataFrame) -> pd.DataFrame:
    """
    Baseline: pole sitter predicted winner, rest follows grid order.
    Same ranking as grid baseline.
    """
    return grid_baseline(df)


def constructor_strength_baseline(df: pd.DataFrame) -> pd.DataFrame:
    """
    Baseline: rank by constructor/team strength first,
    then driver strength, then cleaned grid position.
    """
    out = _clean_grid_positions(df)

    if "team_prior_strength" in out.columns:
        team_col = "team_prior_strength"
    elif "team_form3" in out.columns:
        team_col = "team_form3"
    else:
        raise KeyError("Need team_prior_strength or team_form3 for constructor baseline.")

    if "driver_skill_prior" in out.columns:
        driver_col = "driver_skill_prior"
    elif "drv_form3" in out.columns:
        driver_col = "drv_form3"
    else:
        driver_col = "grid_pos"

    out[team_col] = pd.to_numeric(out[team_col], errors="coerce").fillna(0.0)

    if driver_col != "grid_pos":
        out[driver_col] = pd.to_numeric(out[driver_col], errors="coerce").fillna(0.0)

    all_races = []

    for (year, gp), r in out.groupby(["year", "gp"]):
        r = r.copy()

        r = r.sort_values(
            [team_col, driver_col, "grid_pos"],
            ascending=[False, False, True],
        )

        r["pred_rank"] = range(1, len(r) + 1)
        r["pred_finish"] = r["pred_rank"].astype(float)

        r["p_win"] = (r["pred_rank"] == 1).astype(float)
        r["p_podium"] = (r["pred_rank"] <= 3).astype(float)
        r["p_top10"] = (r["pred_rank"] <= 10).astype(float)

        all_races.append(r)

    return pd.concat(all_races, ignore_index=True)