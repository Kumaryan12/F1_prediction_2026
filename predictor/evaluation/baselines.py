import pandas as pd


def grid_baseline(df: pd.DataFrame) -> pd.DataFrame:
    """
    Baseline: predicted finish order = starting grid order.
    """
    out = df.copy()
    out["pred_rank"] = out["grid_pos"].rank(method="first").astype(int)
    out["pred_finish"] = out["grid_pos"].astype(float)

    out["p_podium"] = (out["pred_rank"] <= 3).astype(float)
    out["p_top10"] = (out["pred_rank"] <= 10).astype(float)
    out["p_win"] = (out["pred_rank"] == 1).astype(float)

    return out


def pole_sitter_baseline(df: pd.DataFrame) -> pd.DataFrame:
    """
    Same ranking as grid baseline, but mainly used for winner accuracy:
    pole sitter is predicted winner.
    """
    return grid_baseline(df)


def constructor_strength_baseline(df: pd.DataFrame) -> pd.DataFrame:
    """
    Baseline: rank by team strength first, then driver strength, then grid.
    Requires:
    team_prior_strength or team_form3
    driver_skill_prior or drv_form3
    """
    out = df.copy()

    team_col = "team_prior_strength" if "team_prior_strength" in out.columns else "team_form3"
    driver_col = "driver_skill_prior" if "driver_skill_prior" in out.columns else "drv_form3"

    out = out.sort_values(
        ["year", "gp", team_col, driver_col, "grid_pos"],
        ascending=[True, True, False, False, True],
    )

    out["pred_rank"] = out.groupby(["year", "gp"]).cumcount() + 1
    out["pred_finish"] = out["pred_rank"].astype(float)

    out["p_podium"] = (out["pred_rank"] <= 3).astype(float)
    out["p_top10"] = (out["pred_rank"] <= 10).astype(float)
    out["p_win"] = (out["pred_rank"] == 1).astype(float)

    return out


def previous_race_winner_baseline(df: pd.DataFrame) -> pd.DataFrame:
    """
    Simple baseline:
    previous race winner is predicted P1.
    Others are ranked by grid.
    Requires chronological data with date/year/gp.
    """
    out = df.copy()
    race_order = (
        out[["year", "gp", "date"]]
        .drop_duplicates()
        .sort_values("date")
        .reset_index(drop=True)
    )

    previous_winner = {}

    for i in range(1, len(race_order)):
        prev = race_order.iloc[i - 1]
        curr = race_order.iloc[i]

        prev_race = out[(out["year"] == prev["year"]) & (out["gp"] == prev["gp"])]
        winner = prev_race.sort_values("finish_pos").iloc[0]["driver"]

        previous_winner[(curr["year"], curr["gp"])] = winner

    all_races = []

    for _, race in race_order.iterrows():
        r = out[(out["year"] == race["year"]) & (out["gp"] == race["gp"])].copy()
        key = (race["year"], race["gp"])

        r["baseline_score"] = -r["grid_pos"]

        if key in previous_winner:
            r.loc[r["driver"] == previous_winner[key], "baseline_score"] = 999

        r = r.sort_values("baseline_score", ascending=False)
        r["pred_rank"] = range(1, len(r) + 1)
        r["pred_finish"] = r["pred_rank"].astype(float)

        r["p_podium"] = (r["pred_rank"] <= 3).astype(float)
        r["p_top10"] = (r["pred_rank"] <= 10).astype(float)
        r["p_win"] = (r["pred_rank"] == 1).astype(float)

        all_races.append(r)

    return pd.concat(all_races, ignore_index=True)