# F1_prediction_system/sessions.py
from __future__ import annotations

import numpy as np
import pandas as pd
import fastf1


# -------------------------------------------------------------------
# Session loading
# -------------------------------------------------------------------

def load_session_safe(year: int, gp: str, session_code: str):
    """
    Safely load a FastF1 session.
    Returns None if loading fails.
    """
    try:
        sess = fastf1.get_session(year, gp, session_code)
        sess.load()
        return sess
    except Exception:
        return None


# -------------------------------------------------------------------
# Small helpers
# -------------------------------------------------------------------

def _empty_driver_df(cols: list[str]) -> pd.DataFrame:
    return pd.DataFrame(columns=["driver", *cols])


def _valid_laps(session) -> pd.DataFrame:
    """
    Return a cleaned laps dataframe.
    Drops null driver/laptime rows and removes obvious pit in/out laps when possible.
    """
    laps = session.laps.copy()
    if laps.empty:
        return laps

    if "Driver" in laps.columns:
        laps = laps.dropna(subset=["Driver"])
    if "LapTime" in laps.columns:
        laps = laps.dropna(subset=["LapTime"])

    # Exclude in/out laps if these columns exist
    if "PitOutTime" in laps.columns:
        laps = laps[laps["PitOutTime"].isna()]
    if "PitInTime" in laps.columns:
        laps = laps[laps["PitInTime"].isna()]

    return laps


def _to_score_from_delta(delta: pd.Series) -> pd.Series:
    """
    Convert pace delta (0 = best, higher = worse) to a score (1 = best, lower = worse).
    """
    delta = pd.to_numeric(delta, errors="coerce")
    return 1.0 / (1.0 + delta.clip(lower=0))


def _normalize_series_max(s: pd.Series) -> pd.Series:
    s = pd.to_numeric(s, errors="coerce")
    mx = s.max(skipna=True)
    if pd.isna(mx) or mx == 0:
        return pd.Series(np.nan, index=s.index)
    return s / mx


def _extract_driver_team_map(session) -> pd.DataFrame:
    """
    Build a driver -> team mapping from session results if possible,
    else fall back to laps.
    """
    # Prefer results
    try:
        res = session.results.copy()
        if res is not None and not res.empty:
            abbr_col = "Abbreviation" if "Abbreviation" in res.columns else "Driver"
            team_col = "TeamName" if "TeamName" in res.columns else "Team"
            if abbr_col in res.columns and team_col in res.columns:
                out = res[[abbr_col, team_col]].rename(columns={abbr_col: "driver", team_col: "team"})
                out["driver"] = out["driver"].astype(str).str.upper()
                out["team"] = out["team"].astype(str)
                return out.drop_duplicates(subset=["driver"])
    except Exception:
        pass

    # Fallback to laps
    laps = session.laps.copy()
    if laps.empty:
        return pd.DataFrame(columns=["driver", "team"])

    if "Driver" not in laps.columns or "Team" not in laps.columns:
        return pd.DataFrame(columns=["driver", "team"])

    tmp = laps.dropna(subset=["Driver", "Team"])[["Driver", "Team"]].copy()
    if tmp.empty:
        return pd.DataFrame(columns=["driver", "team"])

    tmp["Driver"] = tmp["Driver"].astype(str).str.upper()
    tmp["Team"] = tmp["Team"].astype(str)

    # Mode team per driver
    out = (
        tmp.groupby("Driver")["Team"]
        .agg(lambda s: s.mode().iloc[0] if not s.mode().empty else s.iloc[0])
        .reset_index()
        .rename(columns={"Driver": "driver", "Team": "team"})
    )
    return out


# -------------------------------------------------------------------
# Per-session raw features
# -------------------------------------------------------------------

def _best_lap_delta_to_fastest(session) -> pd.DataFrame:
    """
    For each driver:
      bestlap_delta_pct = best lap / session-best lap - 1
    """
    try:
        laps = session.laps.pick_quicklaps().copy()
    except Exception:
        laps = _valid_laps(session)

    if laps.empty or "LapTime" not in laps.columns:
        return _empty_driver_df(["bestlap_delta_pct"])

    laps = laps.dropna(subset=["Driver", "LapTime"])
    if laps.empty:
        return _empty_driver_df(["bestlap_delta_pct"])

    best = (
        laps.groupby("Driver", as_index=False)["LapTime"]
        .min()
        .rename(columns={"Driver": "driver", "LapTime": "best_lap"})
    )

    fastest = best["best_lap"].min()
    if pd.isna(fastest):
        return _empty_driver_df(["bestlap_delta_pct"])

    best["bestlap_delta_pct"] = (
        best["best_lap"].dt.total_seconds() / fastest.total_seconds() - 1.0
    )
    best["driver"] = best["driver"].astype(str).str.upper()
    return best[["driver", "bestlap_delta_pct"]]


def _laps_completed(session) -> pd.DataFrame:
    """
    Count completed timed laps per driver.
    """
    laps = _valid_laps(session)
    if laps.empty:
        return _empty_driver_df(["laps_completed"])

    out = laps.groupby("Driver", as_index=False).size()
    out.columns = ["driver", "laps_completed"]
    out["driver"] = out["driver"].astype(str).str.upper()
    return out


def _speedtrap_rank(session) -> pd.DataFrame:
    """
    Rank drivers by max SpeedST (1 = fastest).
    """
    laps = _valid_laps(session)
    if laps.empty or "SpeedST" not in laps.columns:
        return _empty_driver_df(["speedtrap_rank"])

    tmp = laps.dropna(subset=["Driver", "SpeedST"])
    if tmp.empty:
        return _empty_driver_df(["speedtrap_rank"])

    tmp = tmp.groupby("Driver", as_index=False)["SpeedST"].max()
    tmp["speedtrap_rank"] = tmp["SpeedST"].rank(ascending=False, method="dense")
    tmp = tmp.rename(columns={"Driver": "driver"})
    tmp["driver"] = tmp["driver"].astype(str).str.upper()
    return tmp[["driver", "speedtrap_rank"]]


def _estimate_longrun_features(session) -> pd.DataFrame:
    """
    Approximate long-run pace from the slower portion of valid laps.
    This is a heuristic, but useful for FP1/FP2/FP3.

    Outputs:
      - longrun_delta_pct
      - longrun_laps
    """
    laps = _valid_laps(session)
    if laps.empty or "LapTime" not in laps.columns:
        return _empty_driver_df(["longrun_delta_pct", "longrun_laps"])

    laps = laps.dropna(subset=["Driver", "LapTime"]).copy()
    if laps.empty:
        return _empty_driver_df(["longrun_delta_pct", "longrun_laps"])

    laps["lap_s"] = laps["LapTime"].dt.total_seconds()
    out_rows = []

    for drv, grp in laps.groupby("Driver", sort=False):
        grp = grp.sort_values("lap_s").copy()

        # Too few laps -> not enough long-run signal
        if grp.shape[0] < 5:
            continue

        # Remove the quickest ~40% (quali-style / low-fuel-ish end)
        cut = max(1, int(np.floor(grp.shape[0] * 0.40)))
        longrun = grp.iloc[cut:].copy()

        if longrun.empty:
            continue

        out_rows.append(
            {
                "driver": str(drv).upper(),
                "longrun_med_s": float(longrun["lap_s"].median()),
                "longrun_laps": int(longrun.shape[0]),
            }
        )

    if not out_rows:
        return _empty_driver_df(["longrun_delta_pct", "longrun_laps"])

    out = pd.DataFrame(out_rows)
    fastest_longrun = out["longrun_med_s"].min()
    out["longrun_delta_pct"] = out["longrun_med_s"] / fastest_longrun - 1.0
    return out[["driver", "longrun_delta_pct", "longrun_laps"]]


# -------------------------------------------------------------------
# Per-session feature builder
# -------------------------------------------------------------------

def _build_one_session_features(session, label: str) -> pd.DataFrame:
    """
    Build one session's per-driver feature table.

    Produces:
      - <label>_bestlap_delta_pct
      - <label>_laps_completed
      - <label>_speedtrap_rank
      - <label>_longrun_delta_pct, <label>_longrun_laps  (for practice only)
      - team
      - <label>_session_score
      - <label>_reliability_score
    """
    team_map = _extract_driver_team_map(session)

    best = _best_lap_delta_to_fastest(session).rename(
        columns={"bestlap_delta_pct": f"{label}_bestlap_delta_pct"}
    )
    laps = _laps_completed(session).rename(
        columns={"laps_completed": f"{label}_laps_completed"}
    )
    spd = _speedtrap_rank(session).rename(
        columns={"speedtrap_rank": f"{label}_speedtrap_rank"}
    )

    df = best.merge(laps, on="driver", how="outer").merge(spd, on="driver", how="outer")

    # Practice sessions get long-run features
    if label in {"fp1", "fp2", "fp3"}:
        lr = _estimate_longrun_features(session).rename(
            columns={
                "longrun_delta_pct": f"{label}_longrun_delta_pct",
                "longrun_laps": f"{label}_longrun_laps",
            }
        )
        df = df.merge(lr, on="driver", how="outer")

    # Add team mapping
    if not team_map.empty:
        df = df.merge(team_map, on="driver", how="left")
    else:
        df["team"] = pd.NA

    # Reliability score
    rel = _normalize_series_max(df.get(f"{label}_laps_completed"))
    df[f"{label}_reliability_score"] = rel

    # Pace scores
    bestlap_score = _to_score_from_delta(df.get(f"{label}_bestlap_delta_pct"))
    longrun_score = _to_score_from_delta(df.get(f"{label}_longrun_delta_pct")) if label in {"fp1", "fp2", "fp3"} else pd.Series(np.nan, index=df.index)

    # Composite session score
    # FP1/FP2 carry highest weight in the weekend-level blend later.
    # Within a session, emphasize long-run pace more than one-lap pace for practices.
    if label in {"fp1", "fp2", "fp3"}:
        # practice score = 35% bestlap + 45% longrun + 20% reliability
        arr = np.vstack([
            bestlap_score.to_numpy(dtype=float),
            longrun_score.to_numpy(dtype=float),
            df[f"{label}_reliability_score"].to_numpy(dtype=float),
        ])
        weights = np.array([0.35, 0.45, 0.20], dtype=float)
    else:
        # quali score = 80% bestlap + 20% reliability
        arr = np.vstack([
            bestlap_score.to_numpy(dtype=float),
            df[f"{label}_reliability_score"].to_numpy(dtype=float),
        ])
        weights = np.array([0.80, 0.20], dtype=float)

    valid = ~np.isnan(arr)
    weighted_sum = np.nansum(arr * weights[:, None], axis=0)
    weight_sum = np.sum(valid * weights[:, None], axis=0)
    session_score = np.where(weight_sum > 0, weighted_sum / weight_sum, np.nan)

    df[f"{label}_session_score"] = session_score

    return df


# -------------------------------------------------------------------
# Weekend strength builder
# -------------------------------------------------------------------

def _add_weekend_strengths(merged: pd.DataFrame) -> pd.DataFrame:
    """
    Build 2026-oriented driver/team strength scores from available sessions.

    Weekend weights (highest priority to FP1/FP2 as requested):
      FP1 = 0.35
      FP2 = 0.50
      FP3 = 0.10
      Q   = 0.05

    Outputs:
      - driver_2026_session_strength
      - driver_2026_reliability
      - team_2026_strength
      - team_2026_reliability
    """
    df = merged.copy()

    weekend_weights = {
        "fp1": 0.35,
        "fp2": 0.50,
        "fp3": 0.10,
        "q": 0.05,
    }

    # Driver-level weighted session strength
    score_cols = []
    rel_cols = []
    score_w = []
    rel_w = []

    for label, w in weekend_weights.items():
        s_col = f"{label}_session_score"
        r_col = f"{label}_reliability_score"

        if s_col in df.columns:
            score_cols.append(s_col)
            score_w.append(w)

        if r_col in df.columns:
            rel_cols.append(r_col)
            rel_w.append(w)

    # Weighted average with missing-value handling
    if score_cols:
        score_arr = np.vstack([pd.to_numeric(df[c], errors="coerce").to_numpy(dtype=float) for c in score_cols])
        score_w = np.array(score_w, dtype=float)
        valid = ~np.isnan(score_arr)
        num = np.nansum(score_arr * score_w[:, None], axis=0)
        den = np.sum(valid * score_w[:, None], axis=0)
        df["driver_2026_session_strength"] = np.where(den > 0, num / den, np.nan)
    else:
        df["driver_2026_session_strength"] = np.nan

    if rel_cols:
        rel_arr = np.vstack([pd.to_numeric(df[c], errors="coerce").to_numpy(dtype=float) for c in rel_cols])
        rel_w = np.array(rel_w, dtype=float)
        valid = ~np.isnan(rel_arr)
        num = np.nansum(rel_arr * rel_w[:, None], axis=0)
        den = np.sum(valid * rel_w[:, None], axis=0)
        df["driver_2026_reliability"] = np.where(den > 0, num / den, np.nan)
    else:
        df["driver_2026_reliability"] = np.nan

    # Team-level versions: average the driver-level numbers within each team
    if "team" in df.columns:
        team_strength = (
            df.groupby("team", dropna=True)["driver_2026_session_strength"]
            .mean()
            .rename("team_2026_strength")
        )
        team_reliability = (
            df.groupby("team", dropna=True)["driver_2026_reliability"]
            .mean()
            .rename("team_2026_reliability")
        )

        df = df.merge(team_strength, on="team", how="left")
        df = df.merge(team_reliability, on="team", how="left")
    else:
        df["team_2026_strength"] = np.nan
        df["team_2026_reliability"] = np.nan

    return df


# -------------------------------------------------------------------
# Public entry point
# -------------------------------------------------------------------

def build_live_weekend_features(year: int, gp: str) -> pd.DataFrame:
    """
    Builds per-driver live weekend features from FP1 / FP2 / FP3 / Q.

    Core backwards-compatible outputs:
      - fp1_bestlap_delta_pct, fp1_laps_completed, fp1_speedtrap_rank
      - fp2_bestlap_delta_pct, fp2_laps_completed, fp2_speedtrap_rank
      - fp3_bestlap_delta_pct, fp3_laps_completed, fp3_speedtrap_rank
      - q_bestlap_delta_pct, q_laps_completed, q_speedtrap_rank

    Extra outputs:
      - fp1_longrun_delta_pct, fp1_longrun_laps
      - fp2_longrun_delta_pct, fp2_longrun_laps
      - fp3_longrun_delta_pct, fp3_longrun_laps
      - driver_2026_session_strength
      - driver_2026_reliability
      - team_2026_strength
      - team_2026_reliability
    """
    session_map = {
        "fp1": "FP1",
        "fp2": "FP2",
        "fp3": "FP3",
        "q": "Q",
    }

    merged: pd.DataFrame | None = None

    for label, code in session_map.items():
        sess = load_session_safe(year, gp, code)
        if sess is None:
            continue

        one = _build_one_session_features(sess, label)

        if merged is None:
            merged = one
        else:
            # If multiple sessions carry team, keep left team then fill from right
            if "team" in merged.columns and "team" in one.columns:
                merged = merged.merge(one, on=["driver"], how="outer", suffixes=("", f"_{label}"))
                if f"team_{label}" in merged.columns:
                    merged["team"] = merged["team"].fillna(merged[f"team_{label}"])
                    merged = merged.drop(columns=[f"team_{label}"])
            else:
                merged = merged.merge(one, on="driver", how="outer")

    if merged is None:
        return pd.DataFrame(columns=["driver"])

    merged["driver"] = merged["driver"].astype(str).str.upper()

    # Add weekend strength features
    merged = _add_weekend_strengths(merged)

    return merged