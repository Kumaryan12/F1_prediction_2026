# F1_prediction_system/features.py
from __future__ import annotations
import pandas as pd
import numpy as np

from .config import (
    CIRCUIT_VOL,
    DEFAULT_SC,
    DEFAULT_VSC,
    DEFAULT_PIT_LOSS,
    CIRCUIT_EXTRAS,
    LOW_DF_GPS,
)

# Optional sets (safe fallbacks if not provided in config.py)
try:
    from .config import STREET_GPS
except Exception:
    STREET_GPS: set[str] = set()

try:
    from .config import LONG_STRAIGHT_GPS
except Exception:
    LONG_STRAIGHT_GPS: set[str] = set()


# -------------------------------------------------------------------
# Driver / team priors
# -------------------------------------------------------------------

DRIVER_SKILL_PRIOR = {
    "VER": 0.99,
    "NOR": 0.96,
    "PIA": 0.97,
    "LEC": 0.92,
    "RUS": 0.96,
    "SAI": 0.89,
    "ALO": 0.87,
    "ANT": 0.94,
    "HUL": 0.85,
    "GAS": 0.87,
    "OCO": 0.84,
    "ALB": 0.78,
    "HAM": 0.96,
    "LAW": 0.83,
    "BEA": 0.78,
    "COL": 0.75,
    "HAD": 0.77,
    "STR": 0.70,

    # 2026 additions / returns
    "PER": 0.83,
    "BOT": 0.79,
    "BOR": 0.79,
    "LIN": 0.72,
}

DEFAULT_DRIVER_PRIOR = 0.75

ROOKIE_DRIVERS = {"LIN"}
RETURNEE_DRIVERS = {"PER", "BOT"}

TEAM_ALIAS = {
    "Audi": "Kick Sauber",
    "Sauber": "Kick Sauber",
    "Stake F1 Team Kick Sauber": "Kick Sauber",
    "Stake Kick Sauber": "Kick Sauber",
    "Cadillac Formula 1 Team": "Cadillac",
}

TEAM_BASELINE_PRIOR = {
    "Red Bull Racing": 0.95,
    "McLaren": 0.93,
    "Ferrari": 0.91,
    "Mercedes": 0.90,
    "Aston Martin": 0.82,
    "Alpine": 0.80,
    "Williams": 0.79,
    "Racing Bulls": 0.78,
    "Haas F1 Team": 0.77,
    "Kick Sauber": 0.72,
    "Cadillac": 0.65,
}
DEFAULT_TEAM_PRIOR = 0.75




def _ensure_numeric(df: pd.DataFrame, cols: list[str]) -> None:
    """Coerce listed columns to numeric (in-place), if they exist."""
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")


def _normalize_team_names(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize team naming so historical and 2026 rows map cleanly."""
    out = df.copy()
    if "team" in out.columns:
        out["team"] = out["team"].astype(str).replace(TEAM_ALIAS)
    return out


def _inverse_minmax_strength(s: pd.Series) -> pd.Series:
    """
    Convert a 'lower is better' metric (like avg finish position)
    into a 'higher is better' strength score in [0, 1].
    """
    s = pd.to_numeric(s, errors="coerce")
    s_min = s.min(skipna=True)
    s_max = s.max(skipna=True)

    if pd.isna(s_min) or pd.isna(s_max) or s_max == s_min:
        return pd.Series(np.nan, index=s.index)

    return 1.0 - (s - s_min) / (s_max - s_min)


def add_driver_skill_prior(df: pd.DataFrame) -> pd.DataFrame:
    """Attach a static driver skill prior + rookie/returnee flags."""
    out = df.copy()
    if "driver" in out.columns:
        out["driver"] = out["driver"].astype(str).str.upper()
        out["driver_skill_prior"] = out["driver"].map(DRIVER_SKILL_PRIOR).fillna(DEFAULT_DRIVER_PRIOR)
        out["rookie_flag"] = out["driver"].isin(ROOKIE_DRIVERS).astype(int)
        out["returnee_flag"] = out["driver"].isin(RETURNEE_DRIVERS).astype(int)
    else:
        out["driver_skill_prior"] = DEFAULT_DRIVER_PRIOR
        out["rookie_flag"] = 0
        out["returnee_flag"] = 0
    return out


def add_team_prior_strength(df: pd.DataFrame) -> pd.DataFrame:
    """Attach a simple baseline prior for new/renamed teams."""
    out = _normalize_team_names(df)
    if "team" in out.columns:
        out["team_prior_strength"] = out["team"].map(TEAM_BASELINE_PRIOR).fillna(DEFAULT_TEAM_PRIOR)
    else:
        out["team_prior_strength"] = DEFAULT_TEAM_PRIOR
    return out


def add_live_strength_adjustments(
    df: pd.DataFrame,
    hist_team_weight: float = 0.15,
    live_team_weight: float = 0.90,
    hist_driver_weight: float = 0.20,
    live_driver_weight: float = 0.80,
) -> pd.DataFrame:
    """
    Build 2026-style blended strength features by combining:
      - historical rolling form (converted to strength)
      - live FP/session-based strength from sessions.py

    Expected live columns if available:
      - driver_2026_session_strength
      - driver_2026_reliability
      - team_2026_strength
      - team_2026_reliability
    """
    out = _normalize_team_names(df.copy())

    if "drv_form3" in out.columns:
        out["driver_hist_strength"] = _inverse_minmax_strength(out["drv_form3"])
    else:
        out["driver_hist_strength"] = np.nan

    if "team_form3" in out.columns:
        out["team_hist_strength"] = _inverse_minmax_strength(out["team_form3"])
    else:
        out["team_hist_strength"] = np.nan

    if "driver_2026_session_strength" in out.columns:
        hist = pd.to_numeric(out["driver_hist_strength"], errors="coerce")
        live = pd.to_numeric(out["driver_2026_session_strength"], errors="coerce")
        out["driver_strength_blend_2026"] = np.where(
            live.notna() & hist.notna(),
            hist_driver_weight * hist + live_driver_weight * live,
            hist.fillna(live),
        )
    else:
        out["driver_strength_blend_2026"] = out["driver_hist_strength"]

    if "team_2026_strength" in out.columns:
        hist = pd.to_numeric(out["team_hist_strength"], errors="coerce")
        live = pd.to_numeric(out["team_2026_strength"], errors="coerce")
        out["team_strength_blend_2026"] = np.where(
            live.notna() & hist.notna(),
            hist_team_weight * hist + live_team_weight * live,
            hist.fillna(live),
        )
    else:
        out["team_strength_blend_2026"] = out["team_hist_strength"]

    return out


# -------------------------------------------------------------------
# Circuit context
# -------------------------------------------------------------------

def add_circuit_context_df(df: pd.DataFrame) -> pd.DataFrame:
    def _lookup(gp: str) -> pd.Series:
        sc, vsc, pit = CIRCUIT_VOL.get(gp, (DEFAULT_SC, DEFAULT_VSC, DEFAULT_PIT_LOSS))
        extras = dict(CIRCUIT_EXTRAS.get(gp, CIRCUIT_EXTRAS.get("_default", {})))

        low_df_flag = extras.get("is_low_df", 1.0 if gp in LOW_DF_GPS else 0.0)
        extras.setdefault("is_low_df", float(low_df_flag))

        is_street = extras.get("is_street", 1.0 if gp in STREET_GPS else 0.0)
        extras.setdefault("is_street", float(is_street))

        extras.setdefault("long_straight_index", 0.90 if extras["is_low_df"] else 0.60)
        extras.setdefault("tow_importance", 0.50)
        extras.setdefault("overtake_index", 0.45)
        extras.setdefault("braking_intensity", 0.55)
        extras.setdefault("warmup_penalty", 0.05)
        extras.setdefault("expected_stops", 1.5)
        extras.setdefault("deg_rate", 0.50)
        extras.setdefault("stint_len_typical", extras.get("stint_len_typical", np.nan))

        return pd.Series({"sc_prob": sc, "vsc_prob": vsc, "pit_loss": pit, **extras})

    ctx = df["gp"].apply(_lookup)
    out = pd.concat([df.reset_index(drop=True), ctx.reset_index(drop=True)], axis=1)

    EXTRA_NUMERIC_COLS = [
        "sc_prob", "vsc_prob", "pit_loss",
        "expected_stops", "overtake_index", "tow_importance",
        "is_low_df", "is_street", "long_straight_index",
        "braking_intensity", "warmup_penalty", "deg_rate", "stint_len_typical",

        "surface_bumpiness", "wind_sensitivity", "track_limits_risk",
        "elevation_change_index", "mechanical_failure_risk",
        "corner_count", "avg_speed_kph",

        "rain_prob_race", "wet_lap_fraction", "wet_start_prob", "mixed_conditions_risk",

        "driver_2026_session_strength", "driver_2026_reliability",
        "team_2026_strength", "team_2026_reliability",

        "driver_hist_strength", "team_hist_strength",
        "driver_strength_blend_2026", "team_strength_blend_2026",
        "team_prior_strength",

        "rookie_flag", "returnee_flag",
    ]
    _ensure_numeric(out, EXTRA_NUMERIC_COLS)
    return out


# -------------------------------------------------------------------
# Leakage-safe rolling forms
# -------------------------------------------------------------------

def add_driver_team_form(full_df: pd.DataFrame) -> pd.DataFrame:
    required = {"year", "gp", "date", "driver", "team", "finish_pos"}
    missing = required.difference(full_df.columns)
    if missing:
        raise ValueError(f"add_driver_team_form: missing columns: {sorted(missing)}")

    df = full_df.copy()
    df["driver"] = df["driver"].astype(str).str.upper()
    df = _normalize_team_names(df)

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["finish_pos"] = pd.to_numeric(df["finish_pos"], errors="coerce")
    df = df.dropna(subset=["date", "finish_pos"])
    df = df.sort_values(["date", "year", "gp"], kind="mergesort").reset_index(drop=True)

    df["drv_form3"] = (
        df.groupby("driver", sort=False)["finish_pos"]
          .transform(lambda s: s.shift(1).rolling(3, min_periods=1).mean())
    )

    team_ev = (
        df.groupby(["year", "gp", "date", "team"], sort=False)["finish_pos"]
          .mean()
          .reset_index(name="team_ev_mean")
    )
    df = df.merge(
        team_ev, on=["year", "gp", "date", "team"],
        how="left", validate="many_to_one"
    )

    df["team_form3"] = (
        df.groupby("team", sort=False)["team_ev_mean"]
          .transform(lambda s: s.shift(1).rolling(3, min_periods=1).mean())
    )

    df["driver_skill_prior"] = df["driver"].map(DRIVER_SKILL_PRIOR).fillna(DEFAULT_DRIVER_PRIOR)
    df["team_prior_strength"] = df["team"].map(TEAM_BASELINE_PRIOR).fillna(DEFAULT_TEAM_PRIOR)
    df["rookie_flag"] = df["driver"].isin(ROOKIE_DRIVERS).astype(int)
    df["returnee_flag"] = df["driver"].isin(RETURNEE_DRIVERS).astype(int)

    def _subset_forms(mask: pd.Series, drv_col_out: str, team_col_mean: str, team_col_out: str, window: int = 3):
        if mask.any():
            sub = df.loc[mask].copy().sort_values(["date", "year", "gp"], kind="mergesort")
            drv_series = (
                sub.groupby("driver", sort=False)["finish_pos"]
                   .transform(lambda s: s.shift(1).rolling(window, min_periods=1).mean())
            )
            df.loc[mask, drv_col_out] = drv_series.values
        else:
            df[drv_col_out] = np.nan

        team_ev_sub = (
            df.loc[mask]
              .groupby(["year", "gp", "date", "team"], sort=False)["finish_pos"]
              .mean()
              .reset_index(name=team_col_mean)
        )
        df_tmp = df.merge(
            team_ev_sub, on=["year", "gp", "date", "team"],
            how="left", validate="many_to_one"
        )
        team_roll = (
            df_tmp.groupby("team", sort=False)[team_col_mean]
                  .transform(lambda s: s.shift(1).rolling(window, min_periods=1).mean())
        )
        df[team_col_out] = team_roll

    low_mask = df["gp"].isin(LOW_DF_GPS)
    _subset_forms(low_mask, "lowdf_driver_form3", "team_ev_low_mean", "lowdf_team_form3")
    df["lowdf_driver_form3"] = df["lowdf_driver_form3"].fillna(df["drv_form3"])
    df["lowdf_team_form3"] = df["lowdf_team_form3"].fillna(df["team_form3"])

    street_mask = df["gp"].isin(STREET_GPS)
    _subset_forms(street_mask, "street_driver_form3", "team_ev_street_mean", "street_team_form3")
    df["street_driver_form3"] = df["street_driver_form3"].fillna(df["drv_form3"])
    df["street_team_form3"] = df["street_team_form3"].fillna(df["team_form3"])

    ls_mask = df["gp"].isin(LONG_STRAIGHT_GPS)
    _subset_forms(ls_mask, "longstraight_driver_form3", "team_ev_ls_mean", "longstraight_team_form3")
    df["longstraight_driver_form3"] = df["longstraight_driver_form3"].fillna(df["drv_form3"])
    df["longstraight_team_form3"] = df["longstraight_team_form3"].fillna(df["team_form3"])

    df = add_live_strength_adjustments(df)

    return df.drop(
        columns=[
            "team_ev_mean",
            "team_ev_low_mean",
            "team_ev_street_mean",
            "team_ev_ls_mean",
        ],
        errors="ignore",
    )


# -------------------------------------------------------------------
# Merge latest forms into prediction frame
# -------------------------------------------------------------------

def merge_latest_forms(
    predict_df: pd.DataFrame,
    train_df_with_forms: pd.DataFrame,
) -> pd.DataFrame:
    out = predict_df.copy()
    out["driver"] = out["driver"].astype(str).str.upper()
    out = _normalize_team_names(out)

    train = train_df_with_forms.copy()
    train["driver"] = train["driver"].astype(str).str.upper()
    train = _normalize_team_names(train)

    latest_driver = (
        train.sort_values("date")
        .groupby("driver", as_index=False)
        .tail(1)
    )

    driver_cols = [
        "driver",
        "drv_form3",
        "lowdf_driver_form3",
        "street_driver_form3",
        "longstraight_driver_form3",
        "driver_skill_prior",
        "driver_hist_strength",
        "rookie_flag",
        "returnee_flag",
    ]
    driver_cols = [c for c in driver_cols if c in latest_driver.columns]
    latest_driver = latest_driver[driver_cols]

    out = out.merge(latest_driver, on="driver", how="left")

    latest_team = (
        train.sort_values("date")
        .groupby("team", as_index=False)
        .tail(1)
    )

    team_cols = [
        "team",
        "team_form3",
        "lowdf_team_form3",
        "street_team_form3",
        "longstraight_team_form3",
        "team_prior_strength",
        "team_hist_strength",
    ]
    team_cols = [c for c in team_cols if c in latest_team.columns]
    latest_team = latest_team[team_cols]

    out = out.merge(latest_team, on="team", how="left")

    for col in [
        "drv_form3",
        "lowdf_driver_form3",
        "street_driver_form3",
        "longstraight_driver_form3",
        "driver_hist_strength",
    ]:
        if col in out.columns and out[col].isna().any():
            med = train[col].median(skipna=True)
            out[col] = out[col].fillna(med)

    out["driver_skill_prior"] = out.get("driver_skill_prior", pd.Series(index=out.index)).fillna(
        out["driver"].map(DRIVER_SKILL_PRIOR).fillna(DEFAULT_DRIVER_PRIOR)
    )
    out["rookie_flag"] = out.get("rookie_flag", pd.Series(index=out.index)).fillna(
        out["driver"].isin(ROOKIE_DRIVERS).astype(int)
    )
    out["returnee_flag"] = out.get("returnee_flag", pd.Series(index=out.index)).fillna(
        out["driver"].isin(RETURNEE_DRIVERS).astype(int)
    )

    for col in [
        "team_form3",
        "lowdf_team_form3",
        "street_team_form3",
        "longstraight_team_form3",
        "team_hist_strength",
    ]:
        if col in out.columns and out[col].isna().any():
            med = train[col].median(skipna=True)
            out[col] = out[col].fillna(med)

    out["team_prior_strength"] = out.get("team_prior_strength", pd.Series(index=out.index)).fillna(
        out["team"].map(TEAM_BASELINE_PRIOR).fillna(DEFAULT_TEAM_PRIOR)
    )

    out = add_live_strength_adjustments(out)
    return out


# -------------------------------------------------------------------
# Qualifying proxy
# -------------------------------------------------------------------

def add_quali_proxy(
    predict_df: pd.DataFrame,
    train_df: pd.DataFrame,
    window: int = 3,
    driver_weight: float = 0.7,
) -> pd.DataFrame:
    out = predict_df.copy()

    if not out["grid_pos"].isna().any():
        print("All grid positions are available, no proxy needed")
        return out

    required = {"driver", "grid_pos", "date"}
    missing_req = required.difference(train_df.columns)
    if missing_req:
        raise ValueError(
            f"train_df for quali proxy is missing columns: {sorted(missing_req)}"
        )

    base = train_df.copy()
    base["driver"] = base["driver"].astype(str).str.upper()
    base["grid_pos"] = pd.to_numeric(base["grid_pos"], errors="coerce")
    base["date"] = pd.to_datetime(base["date"], errors="coerce")
    base = base.dropna(subset=["driver", "grid_pos", "date"]).sort_values("date")

    drv_proxy = (
        base.groupby("driver", sort=False)["grid_pos"]
            .apply(lambda s: s.tail(window).mean())
            .rename("drv_qual_proxy")
            .reset_index()
    )
    out["driver"] = out["driver"].astype(str).str.upper()
    out = _normalize_team_names(out)
    base = _normalize_team_names(base)

    out = out.merge(drv_proxy, on="driver", how="left")

    has_team = ("team" in out.columns) and ("team" in base.columns)
    if has_team:
        team_proxy = (
            base.groupby("team", sort=False)["grid_pos"]
                .apply(lambda s: s.tail(window).mean())
                .rename("team_qual_proxy")
                .reset_index()
        )
        out = out.merge(team_proxy, on="team", how="left")
        out["qual_proxy"] = np.where(
            out["drv_qual_proxy"].notna() & out["team_qual_proxy"].notna(),
            driver_weight * out["drv_qual_proxy"] + (1 - driver_weight) * out["team_qual_proxy"],
            out["drv_qual_proxy"].fillna(out.get("team_qual_proxy")),
        )
    else:
        out["qual_proxy"] = out["drv_qual_proxy"]

    out["grid_pos"] = pd.to_numeric(out["grid_pos"], errors="coerce")
    mask = out["grid_pos"].isna()
    missing_count = int(mask.sum())
    if missing_count > 0:
        print(f"Missing {missing_count} grid positions, applying quali proxy")
        out.loc[mask, "grid_pos"] = out.loc[mask, "qual_proxy"]

    return out.drop(
        columns=["drv_qual_proxy", "team_qual_proxy", "qual_proxy"],
        errors="ignore",
    )