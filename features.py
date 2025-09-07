# F1_prediction_system/features.py
from __future__ import annotations
import pandas as pd
import numpy as np

from .config import (
    CIRCUIT_VOL,
    DEFAULT_SC,
    DEFAULT_VSC,
    DEFAULT_PIT_LOSS,
    CIRCUIT_EXTRAS,   # dict: gp -> {"expected_stops":..., "overtake_index":..., "tow_importance":..., "is_low_df":...} (any subset)
    LOW_DF_GPS        # set[str]: GPs considered low-downforce (e.g., {"Italian Grand Prix", "Azerbaijan Grand Prix", ...})
)

# ----------------------------- Helpers -----------------------------

def _is_monza(gp: str) -> bool:
    s = (gp or "").lower()
    return ("italian" in s) or ("monza" in s)

def _ensure_numeric(df: pd.DataFrame, cols: list[str]) -> None:
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

# ---------------------- Circuit context (Monza-safe) ----------------------

def add_circuit_context_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds per-GP context:
      - sc_prob, vsc_prob, pit_loss (from CIRCUIT_VOL with defaults)
      - expected_stops, overtake_index, tow_importance, is_low_df (from CIRCUIT_EXTRAS or sensible fallbacks)
    """
    def _lookup(gp: str) -> pd.Series:
        sc, vsc, pit = CIRCUIT_VOL.get(gp, (DEFAULT_SC, DEFAULT_VSC, DEFAULT_PIT_LOSS))
        extras = dict(CIRCUIT_EXTRAS.get(gp, CIRCUIT_EXTRAS.get("_default", {})))

        # Fallbacks if keys are missing in CIRCUIT_EXTRAS
        low_df_flag = extras.get("is_low_df", 1.0 if (gp in LOW_DF_GPS or _is_monza(gp)) else 0.0)
        extras.setdefault("is_low_df", float(low_df_flag))
        extras.setdefault("tow_importance", 0.90 if extras["is_low_df"] else 0.50)
        extras.setdefault("overtake_index", 0.70 if extras["is_low_df"] else 0.45)
        extras.setdefault("expected_stops", 1.10 if extras["is_low_df"] else 1.50)

        return pd.Series({
            "sc_prob": sc,
            "vsc_prob": vsc,
            "pit_loss": pit,
            **extras
        })

    ctx = df["gp"].apply(_lookup)
    out = pd.concat([df.reset_index(drop=True), ctx.reset_index(drop=True)], axis=1)

    _ensure_numeric(out, ["sc_prob", "vsc_prob", "pit_loss", "expected_stops", "overtake_index", "tow_importance", "is_low_df"])
    return out


# ---------------------- Leakage-safe forms ----------------------

def add_driver_team_form(full_df: pd.DataFrame) -> pd.DataFrame:
    """
    Base (leakage-safe) forms:
      - drv_form3: driver trailing mean of finish over last 3 races, shifted by 1
      - team_form3: team per-event mean, then trailing mean over last 3 races, shifted by 1
      - lowdf_driver_form3 / lowdf_team_form3: same but only on LOW_DF_GPS events (shifted)
      - monza_form_driver / monza_form_team: same but only on Italian GP/Monza (shifted)
    Requires: year, gp, date, driver, team, finish_pos
    """
    if "date" not in full_df.columns:
        raise ValueError("full_df must include a 'date' column to sort chronologically")

    df = full_df.sort_values(["date", "year", "gp"]).reset_index(drop=True).copy()

    # ---- Overall driver form (3, shifted)
    df["drv_form3"] = (
        df.groupby("driver", sort=False)["finish_pos"]
          .transform(lambda s: s.shift(1).rolling(3, min_periods=1).mean())
    )

    # ---- Team per-event mean -> rolling form (3, shifted)
    team_ev = (
        df.groupby(["year", "gp", "date", "team"])["finish_pos"]
          .mean()
          .reset_index(name="team_ev_mean")
    )
    df = df.merge(team_ev, on=["year", "gp", "date", "team"], how="left")
    df["team_form3"] = (
        df.groupby("team", sort=False)["team_ev_mean"]
          .transform(lambda s: s.shift(1).rolling(3, min_periods=1).mean())
    )

    # ---- Low-DF only forms (via LOW_DF_GPS)
    low_mask = df["gp"].isin(LOW_DF_GPS)

    df["lowdf_driver_form3"] = np.nan
    df.loc[low_mask, "lowdf_driver_form3"] = (
        df.loc[low_mask]
          .groupby("driver", sort=False)["finish_pos"]
          .transform(lambda s: s.shift(1).rolling(3, min_periods=1).mean())
    )

    low_team_ev = (
        df.loc[low_mask]
          .groupby(["year", "gp", "date", "team"])["finish_pos"]
          .mean()
          .reset_index(name="team_ev_low_mean")
    )
    df = df.merge(low_team_ev, on=["year", "gp", "date", "team"], how="left")
    df["lowdf_team_form3"] = (
        df.groupby("team", sort=False)["team_ev_low_mean"]
          .transform(lambda s: s.shift(1).rolling(3, min_periods=1).mean())
    )

    # Fallbacks to overall form when no low-DF history exists
    if "drv_form3" in df.columns:
        df["lowdf_driver_form3"] = df["lowdf_driver_form3"].fillna(df["drv_form3"])
    if "team_form3" in df.columns:
        df["lowdf_team_form3"] = df["lowdf_team_form3"].fillna(df["team_form3"])

    # ---- Monza-only forms (Italian GP / Monza)
    monza_mask = df["gp"].apply(_is_monza)

    df["monza_form_driver"] = np.nan
    df.loc[monza_mask, "monza_form_driver"] = (
        df.loc[monza_mask]
          .groupby("driver", sort=False)["finish_pos"]
          .transform(lambda s: s.shift(1).rolling(3, min_periods=1).mean())
    )

    monza_team_ev = (
        df.loc[monza_mask]
          .groupby(["year", "gp", "date", "team"])["finish_pos"]
          .mean()
          .reset_index(name="team_monza_ev_mean")
    )
    df = df.merge(monza_team_ev, on=["year", "gp", "date", "team"], how="left")
    df["monza_form_team"] = (
        df.groupby("team", sort=False)["team_monza_ev_mean"]
          .transform(lambda s: s.shift(1).rolling(3, min_periods=1).mean())
    )

    return df.drop(columns=["team_ev_mean", "team_ev_low_mean", "team_monza_ev_mean"], errors="ignore")


# ---------------------- Merge latest forms into prediction ----------------------

def merge_latest_forms(predict_df: pd.DataFrame, train_df_with_forms: pd.DataFrame) -> pd.DataFrame:
    """
    Merge the latest form-like features from training history into the prediction rows.
    Brings: drv_form3, team_form3, lowdf_driver_form3, lowdf_team_form3,
            monza_form_driver, monza_form_team
    """
    latest = (
        train_df_with_forms.sort_values("date")
        .groupby(["driver", "team"], as_index=False)
        .tail(1)
    )

    keep_cols = [
        "driver", "team",
        "drv_form3", "team_form3",
        "lowdf_driver_form3", "lowdf_team_form3",
        "monza_form_driver", "monza_form_team",
    ]
    keep_cols = [c for c in keep_cols if c in train_df_with_forms.columns]
    latest = latest[[c for c in keep_cols if c in latest.columns]]

    out = predict_df.merge(latest, on=["driver", "team"], how="left")

    # Conservative fallbacks: fill with global medians from train_df_with_forms
    for col in ("drv_form3", "team_form3", "lowdf_driver_form3", "lowdf_team_form3",
                "monza_form_driver", "monza_form_team"):
        if col in out.columns and out[col].isna().any() and (col in train_df_with_forms.columns):
            med = train_df_with_forms[col].median(skipna=True)
            out[col] = out[col].fillna(med)

    return out


# ---------------------- Qualifying proxy (EWM blend) ----------------------

def add_quali_proxy(predict_df: pd.DataFrame, train_df: pd.DataFrame, window: int = 3,
                    driver_weight: float = 0.7) -> pd.DataFrame:
    """
    Fill missing grid positions in predict_df using a rolling-mean proxy from train_df.
    - Uses driver-level rolling mean over the last `window` events.
    - If team info is available in both frames, blend driver and team proxies.
    """
    out = predict_df.copy()

    # Nothing to do if no missing grid positions
    if not out["grid_pos"].isna().any():
        print("All grid positions are available, no proxy needed")
        return out

    # Ensure required columns exist in the base
    required = {"driver", "grid_pos", "date"}
    missing_req = required.difference(train_df.columns)
    if missing_req:
        raise ValueError(f"train_df for quali proxy is missing columns: {sorted(missing_req)}")

    base = train_df.copy()
    # Coerce dtypes
    base["grid_pos"] = pd.to_numeric(base["grid_pos"], errors="coerce")
    base["date"] = pd.to_datetime(base["date"], errors="coerce")

    # Keep only rows we can use
    base = base.dropna(subset=["driver", "grid_pos", "date"]).sort_values("date")

    # Driver-level rolling mean of recent grids
    drv_proxy = (
        base.groupby("driver", sort=False)["grid_pos"]
            .apply(lambda s: s.tail(window).mean())
            .rename("drv_qual_proxy")
            .reset_index()
    )
    out = out.merge(drv_proxy, on="driver", how="left")

    # Optional team-level proxy (only if team exists in both frames)
    has_team = ("team" in out.columns) and ("team" in base.columns)
    if has_team:
        team_proxy = (
            base.groupby("team", sort=False)["grid_pos"]
                .apply(lambda s: s.tail(window).mean())
                .rename("team_qual_proxy")
                .reset_index()
        )
        out = out.merge(team_proxy, on="team", how="left")

        # Blend when both are available; otherwise use whichever exists
        out["qual_proxy"] = np.where(
            out["drv_qual_proxy"].notna() & out["team_qual_proxy"].notna(),
            driver_weight * out["drv_qual_proxy"] + (1 - driver_weight) * out["team_qual_proxy"],
            out["drv_qual_proxy"].fillna(out.get("team_qual_proxy"))
        )
    else:
        out["qual_proxy"] = out["drv_qual_proxy"]

    # Fill only the missing grid_pos with the proxy
    out["grid_pos"] = pd.to_numeric(out["grid_pos"], errors="coerce")
    mask = out["grid_pos"].isna()
    missing_count = int(mask.sum())
    if missing_count > 0:
        print(f"Missing {missing_count} grid positions, applying quali proxy")
        out.loc[mask, "grid_pos"] = out.loc[mask, "qual_proxy"]

    # Clean up helper columns if present
    return out.drop(columns=["drv_qual_proxy", "team_qual_proxy", "qual_proxy"], errors="ignore")

