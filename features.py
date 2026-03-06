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


DRIVER_SKILL_PRIOR = {
    
    "VER": 1.00,  

   
    "HAM": 0.81,
    "NOR": 0.98,
    "PIA": 0.95,
    "LEC": 0.92,

    "RUS": 0.91,
    "SAI": 0.89,
    "ALO": 0.88,
    "ANT": 0.86,
     

   
    "GAS": 0.84,
    "OCO": 0.84,
    "ALB": 0.82,
    "TSU": 0.83,
    "LAW": 0.80, 

   
    "HUL": 0.85,
    "COL": 0.75,
    "HAD": 0.75,
    "STR": 0.7,
    "BEA": 0.78,  
      
}

DEFAULT_DRIVER_PRIOR = 0.75


try:
    from .config import STREET_GPS
except Exception:
    STREET_GPS: set[str] = set()

try:
    from .config import LONG_STRAIGHT_GPS
except Exception:
    LONG_STRAIGHT_GPS: set[str] = set()





def _ensure_numeric(df: pd.DataFrame, cols: list[str]) -> None:
    """Coerce listed columns to numeric (in-place), if they exist."""
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")





def add_circuit_context_df(df: pd.DataFrame) -> pd.DataFrame:
 

    def _lookup(gp: str) -> pd.Series:
        
        sc, vsc, pit = CIRCUIT_VOL.get(
            gp, (DEFAULT_SC, DEFAULT_VSC, DEFAULT_PIT_LOSS)
        )

        
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

        return pd.Series(
            {
                "sc_prob": sc,
                "vsc_prob": vsc,
                "pit_loss": pit,
                **extras,
            }
        )

    
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

        
        "rain_prob_race", "wet_lap_fraction", "wet_start_prob",
        "mixed_conditions_risk",
    ]
    _ensure_numeric(out, EXTRA_NUMERIC_COLS)
    return out





def add_driver_team_form(full_df: pd.DataFrame) -> pd.DataFrame:
   
    required = {"year", "gp", "date", "driver", "team", "finish_pos"}
    missing = required.difference(full_df.columns)
    if missing:
        raise ValueError(f"add_driver_team_form: missing columns: {sorted(missing)}")

    #
    df = full_df.copy()
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

    def _subset_forms(mask: pd.Series,
                      drv_col_out: str, team_col_mean: str, team_col_out: str):
    
        if mask.any():
            sub = df.loc[mask].copy()
            sub = sub.sort_values(["date", "year", "gp"], kind="mergesort")
            drv_series = (
                sub.groupby("driver", sort=False)["finish_pos"]
                   .transform(lambda s: s.shift(1).rolling(3, min_periods=1).mean())
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
                  .transform(lambda s: s.shift(1).rolling(3, min_periods=1).mean())
        )
        df[team_col_out] = team_roll

    low_mask = df["gp"].isin(LOW_DF_GPS)
    _subset_forms(low_mask, "lowdf_driver_form3", "team_ev_low_mean", "lowdf_team_form3")
    df["lowdf_driver_form3"] = df["lowdf_driver_form3"].fillna(df["drv_form3"])
    df["lowdf_team_form3"]   = df["lowdf_team_form3"].fillna(df["team_form3"])
    df["driver_skill_prior"] = df["driver"].map(DRIVER_SKILL_PRIOR).fillna(DEFAULT_DRIVER_PRIOR)


    
    street_mask = df["gp"].isin(STREET_GPS)
    _subset_forms(
        street_mask, "street_driver_form3",
        "team_ev_street_mean", "street_team_form3"
    )
    df["street_driver_form3"] = df["street_driver_form3"].fillna(df["drv_form3"])
    df["street_team_form3"]   = df["street_team_form3"].fillna(df["team_form3"])

    ls_mask = df["gp"].isin(LONG_STRAIGHT_GPS)
    _subset_forms(
        ls_mask, "longstraight_driver_form3",
        "team_ev_ls_mean", "longstraight_team_form3"
    )
    df["longstraight_driver_form3"] = df["longstraight_driver_form3"].fillna(df["drv_form3"])
    df["longstraight_team_form3"]   = df["longstraight_team_form3"].fillna(df["team_form3"])

    return df.drop(
        columns=[
            "team_ev_mean", "team_ev_low_mean",
            "team_ev_street_mean", "team_ev_ls_mean",
        ],
        errors="ignore",
    )





def merge_latest_forms(
    predict_df: pd.DataFrame,
    train_df_with_forms: pd.DataFrame
) -> pd.DataFrame:
    latest = (
        train_df_with_forms.sort_values("date")
        .groupby(["driver", "team"], as_index=False)
        .tail(1)
    )

    keep_cols = [
        "driver", "team",
        "drv_form3", "team_form3",
        "lowdf_driver_form3", "lowdf_team_form3",
        "street_driver_form3", "street_team_form3",
        "longstraight_driver_form3", "longstraight_team_form3",
        "driver_skill_prior",
    ]
    keep_cols = [c for c in keep_cols if c in train_df_with_forms.columns]
    latest = latest[[c for c in keep_cols if c in latest.columns]]

    out = predict_df.merge(latest, on=["driver", "team"], how="left")

 
    for col in keep_cols:
        if col in out.columns and out[col].isna().any():
            med = train_df_with_forms[col].median(skipna=True)
            out[col] = out[col].fillna(med)

    return out




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
    base["grid_pos"] = pd.to_numeric(base["grid_pos"], errors="coerce")
    base["date"] = pd.to_datetime(base["date"], errors="coerce")
    base = base.dropna(subset=["driver", "grid_pos", "date"]).sort_values("date")

    drv_proxy = (
        base.groupby("driver", sort=False)["grid_pos"]
            .apply(lambda s: s.tail(window).mean())
            .rename("drv_qual_proxy")
            .reset_index()
    )
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
            driver_weight * out["drv_qual_proxy"]
            + (1 - driver_weight) * out["team_qual_proxy"],
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
