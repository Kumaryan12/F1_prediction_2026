# F1_prediction_system/data.py
from __future__ import annotations
import pandas as pd
import fastf1
from typing import List, Dict, Tuple, Optional
from .config import CACHE_DIR, FALLBACK_EVENTS, EXCLUDE_EVENTS

fastf1.Cache.enable_cache(CACHE_DIR)

# ---------------- Hardcoded grids (optional, per-event) ----------------
# Keys are (year, gp_name) and values map DRIVER ABBREVIATION -> starting grid position (1..20)
HARDCODED_GRID: Dict[Tuple[int, str], Dict[str, int]] = {
    (2025, "Italian Grand Prix"): {
        "PIA": 3, "NOR": 2, "VER": 1, "HAD": 16, "RUS": 5, "LEC": 4, "HAM": 10,
        "LAW": 20, "SAI": 13, "ALO": 8, "ANT": 6, "TSU": 9, "BOR": 7, "GAS": 19,
        "ALB": 14, "COL": 18, "HUL": 12, "OCO": 15, "BEA": 11, "STR": 17
    },
    # Example (fill when you have the final quali): (2025, "Italian Grand Prix"): {...}
}

# ---------------- Schedule / helpers ----------------

def _event_schedule(year: int) -> pd.DataFrame:
    try:
        sch = fastf1.get_event_schedule(year)
        if "EventFormat" in sch.columns:
            sch = sch[sch["EventFormat"].str.lower() != "testing"]
        sch = sch[~sch["EventName"].str.contains("testing", case=False, na=False)]
        return sch[["EventName", "EventDate"]].rename(columns={"EventName": "gp", "EventDate": "date"})
    except Exception:
        events = FALLBACK_EVENTS.get(year, [])
        if not events:
            raise
        dates = pd.date_range(f"{year}-01-01", periods=len(events), freq="7D")
        return pd.DataFrame({"gp": events, "date": dates})

def _race_has_results(year: int, gp: str) -> bool:
    try:
        ses = fastf1.get_session(year, gp, "R")
        ses.load(telemetry=False, laps=False, weather=False, messages=False)
        res = ses.results
        return (res is not None) and (not res.empty)
    except Exception:
        return False

def _load_results_only(year: int, gp: str, sess_name: str) -> pd.DataFrame:
    ses = fastf1.get_session(year, gp, sess_name)
    try:
        ses.load(telemetry=False, laps=False, weather=False, messages=False)
    except TypeError:
        try:
            ses.load(telemetry=False, laps=False)
        except TypeError:
            ses.load()
    res = getattr(ses, "results", None)
    if res is None or res.empty:
        raise ValueError(f"{sess_name} results empty for {gp} {year}")
    return res

def list_gp_events(year: int) -> List[str]:
    return _event_schedule(year)["gp"].tolist()

def list_before_target(year: int, target_gp: str) -> List[str]:
    sch = _event_schedule(year)
    if target_gp not in sch["gp"].values:
        raise ValueError(f"Target gp {target_gp} not found in {year} schedule")
    tgt_date = sch.loc[sch['gp'] == target_gp, "date"].iloc[0]
    return sch.loc[sch["date"] < tgt_date, "gp"].tolist()

def _event_date(year: int, gp_name: str):
    sch = _event_schedule(year)
    row = sch.loc[sch["gp"] == gp_name]
    if row.empty:
        return None
    return row["date"].iloc[0]

def _last_completed_event(year: int, target_gp: str) -> Optional[str]:
    try:
        prior = list_before_target(year, target_gp)
    except Exception:
        return None
    for gp in reversed(prior):
        if _race_has_results(year, gp):
            return gp
    return None

def _get_roster_map(year: int, target_gp: str) -> pd.DataFrame:
    """
    Canonical roster = last completed race before the target.
    Returns: DataFrame with DriverNumber(str), driver (abbr), team
    """
    last_gp = _last_completed_event(year, target_gp)
    if not last_gp:
        raise RuntimeError(f"No completed race found before {target_gp} {year} to build roster map.")

    r_res = _load_results_only(year, last_gp, "R").copy()
    num_col = "DriverNumber"
    abbr_col = "Abbreviation" if "Abbreviation" in r_res.columns else "Driver"
    team_col = "TeamName"     if "TeamName" in r_res.columns     else "Team"

    roster = r_res[[num_col, abbr_col, team_col]].rename(
        columns={num_col: "DriverNumber", abbr_col: "driver", team_col: "team"}
    )
    roster["DriverNumber"] = roster["DriverNumber"].astype(str)
    roster["driver"] = roster["driver"].astype(str).str.upper()
    roster["team"] = roster["team"].astype(str)
    roster = roster.drop_duplicates(subset=["DriverNumber"])
    return roster[["DriverNumber", "driver", "team"]]

def _canonicalize_pred_entrylist(pred_df: pd.DataFrame, year: int, target_gp: str) -> pd.DataFrame:
    """
    Overwrite pred_df['driver','team'] using canonical roster keyed by DriverNumber.
    Drop non-roster FP/test entries; dedupe by DriverNumber.
    """
    out = pred_df.copy()
    if "DriverNumber" not in out.columns:
        return out

    out["DriverNumber"] = out["DriverNumber"].astype(str)
    roster = _get_roster_map(year, target_gp)

    out = out.merge(roster, on="DriverNumber", how="left", suffixes=("", "_canon"))
    out["driver"] = out["driver_canon"].fillna(out["driver"])
    out["team"]   = out["team_canon"].fillna(out["team"])

    keep = out["driver_canon"].notna()
    dropped = int((~keep).sum())
    if dropped > 0:
        print(f"[INFO] Filtering to season roster: dropped {dropped} FP/test entries")

    out = out.loc[keep].drop(columns=["driver_canon", "team_canon"]).copy()
    out = out.drop_duplicates(subset=["DriverNumber"]).reset_index(drop=True)
    # Normalize abbr casing
    out["driver"] = out["driver"].astype(str).str.upper()
    return out

def _apply_hardcoded_grid(df: pd.DataFrame, year: int, gp_name: str) -> pd.DataFrame:
    """
    If a hardcoded grid exists for (year, gp_name), filter to those drivers and set grid_pos.
    """
    mapping = HARDCODED_GRID.get((year, gp_name))
    if not mapping:
        return df

    out = df.copy()
    out["driver"] = out["driver"].astype(str).str.upper()

    # Filter to only the mapped drivers (keeps prediction clean/complete)
    before = len(out)
    out = out[out["driver"].isin(mapping.keys())].copy()
    kept = len(out)
    print(f"[INFO] Hardcoded grid applied for {gp_name} {year}: kept {kept}/{before} drivers")

    # Set grid positions from mapping
    out["grid_pos"] = out["driver"].map(mapping).astype("Int64")

    # Sort by grid_pos if all present
    if out["grid_pos"].notna().all():
        out = out.sort_values("grid_pos").reset_index(drop=True)

    # Warn if any mapped drivers were not found in pred_df (typo protection)
    missing = sorted(set(mapping.keys()) - set(out["driver"].unique()))
    if missing:
        print(f"[WARN] Drivers in hardcoded grid not in entry list: {missing}")

    return out

# ---------------- Build event rows for training ----------------

def extract_event_qr(year: int, gp_name: str) -> pd.DataFrame:
    """
    Return one row per driver with grid_pos and finish_pos.
    Prefer both from Race results; fall back to Quali for grid only if needed.
    NOTE: Do NOT apply hardcoded grids here (keep training leakage-safe).
    """
    r_res = _load_results_only(year, gp_name, "R")
    if r_res is None or len(r_res) == 0:
        raise RuntimeError("race results empty")

    r_res = r_res.copy()
    r_res["DriverNumber"] = r_res["DriverNumber"].astype(str).str.strip()
    fin_col = "ClassifiedPosition" if "ClassifiedPosition" in r_res.columns else "Position"

    df = None

    # 1) Use race grid if available
    if "GridPosition" in r_res.columns and r_res["GridPosition"].notna().any():
        need = ["DriverNumber", "Abbreviation", "TeamName", "GridPosition", fin_col]
        if all(c in r_res.columns for c in need):
            df = r_res[need].rename(
                columns={
                    "Abbreviation": "driver",
                    "TeamName": "team",
                    "GridPosition": "grid_pos",
                    fin_col: "finish_pos",
                }
            )

    # 2) Otherwise: grid from Quali + finish from Race
    if df is None:
        q_res = _load_results_only(year, gp_name, "Q")
        q_res = q_res.copy()
        q_res["DriverNumber"] = q_res["DriverNumber"].astype(str).str.strip()
        q_grid_col = "GridPosition" if "GridPosition" in q_res.columns else "Position"

        need_q = ["DriverNumber", "Abbreviation", "TeamName", q_grid_col]
        need_r = ["DriverNumber", fin_col]
        if not all(c in q_res.columns for c in need_q) or not all(c in r_res.columns for c in need_r):
            raise KeyError("Missing columns for Q/R merge")

        qi = q_res[need_q].rename(
            columns={q_grid_col: "grid_pos", "Abbreviation": "driver", "TeamName": "team"}
        )
        ri = r_res[need_r].rename(columns={fin_col: "finish_pos"})
        df = qi.merge(ri, on="DriverNumber", how="inner")

    # Clean
    df = df.copy()
    df["grid_pos"] = pd.to_numeric(df["grid_pos"], errors="coerce")
    df["finish_pos"] = pd.to_numeric(df["finish_pos"], errors="coerce")
    df = df.dropna(subset=["grid_pos", "finish_pos"])
    if df.empty:
        raise RuntimeError("positions all NA after coercion")

    df.loc[:, "year"] = year
    df.loc[:, "gp"] = gp_name
    df.loc[:, "date"] = _event_date(year, gp_name)
    df.loc[:, "DriverNumber"] = df["DriverNumber"].astype(str)

    return df[["year", "gp", "date", "driver", "team", "grid_pos", "finish_pos", "DriverNumber"]]

def build_training_min(years: List[int]) -> pd.DataFrame:
    out, errors = [], []
    for y in years:
        for gp in list_gp_events(y):
            try:
                df_ev = extract_event_qr(y, gp)
                if df_ev.empty or df_ev["grid_pos"].isna().all() or df_ev["finish_pos"].isna().all():
                    raise ValueError("empty/NaN results")
                out.append(df_ev)
            except Exception as e:
                errors.append((y, gp, str(e)))
    if not out:
        raise RuntimeError(f"No events Loaded. Sample Errors: {errors[:3]}")
    return pd.concat(out, ignore_index=True)

def build_training_until(target_year: int, target_gp: str, hist_years=range(2023, 2025)) -> pd.DataFrame:
    from time import perf_counter

    EXC = globals().get("EXCLUDE_EVENTS", {})
    def _not_excluded(year: int, gp: str) -> bool:
        return gp not in EXC.get(year, set())

    rows = []

    # History years
    for y in hist_years:
        try:
            events_all = list_gp_events(y)
            events = [gp for gp in events_all if _not_excluded(y, gp)]
            print(f"[INFO] {y}: {len(events)} events to load (of {len(events_all)} total)")
        except Exception as e:
            print(f"[SKIP-YEAR] {y}: schedule error: {e}")
            continue

        for gp in events:
            try:
                t0 = perf_counter()
                df_ev = extract_event_qr(y, gp)
                if df_ev.empty or df_ev["grid_pos"].isna().all() or df_ev["finish_pos"].isna().all():
                    raise ValueError("empty/NaN results")
                rows.append(df_ev)
                print(f"[LOAD] {y} {gp} ({len(df_ev)} rows) in {perf_counter() - t0:.1f}s")
            except Exception as e:
                print(f"[SKIP] {y} {gp}: {e}")
                continue

    # Current season up to target
    try:
        pre_events_raw_all = list_before_target(target_year, target_gp)
        pre_events_raw = [gp for gp in pre_events_raw_all if _not_excluded(target_year, gp)]
        pre_events = [gp for gp in pre_events_raw if _race_has_results(target_year, gp)]
        if not pre_events and pre_events_raw:
            print("[WARN] No verified race results found; falling back to unverified pre-events list.")
            pre_events = pre_events_raw
        print(f"[INFO] {target_year} before '{target_gp}': {len(pre_events)} events (filtered from {len(pre_events_raw_all)})")
    except Exception as e:
        print(f"[SKIP-SEASON] {target_year}: schedule error: {e}")
        pre_events = []

    for gp in pre_events:
        try:
            from time import perf_counter
            t0 = perf_counter()
            df_ev = extract_event_qr(target_year, gp)
            if df_ev.empty or df_ev["grid_pos"].isna().all() or df_ev["finish_pos"].isna().all():
                raise ValueError("empty/NaN results")
            rows.append(df_ev)
            print(f"[LOAD] {target_year} {gp} ({len(df_ev)} rows) in {perf_counter() - t0:.1f}s")
        except Exception as e:
            print(f"[SKIP] {target_year} {gp}: {e}")
            continue

    if not rows:
        raise RuntimeError("No training data found before target.")

    full = pd.concat(rows, ignore_index=True)
    full = full.drop_duplicates(subset=["year", "gp", "DriverNumber"])
    if "date" in full.columns:
        full = full.sort_values(["date", "year", "gp", "DriverNumber"]).reset_index(drop=True)
    return full

# ---------------- Target drivers for prediction ----------------

def get_target_drivers(year: int, gp_name: str) -> pd.DataFrame:
    """
    Return driver/team/grid for the target event.
    Preference:
      1) Qualifying results (with grid)
      2) FP1 results (entry list; no grid)
      3) Latest completed race before target (entry list; no grid)
    After building the list:
      - Canonicalize to roster (drop placeholders)
      - Apply HARDCODED_GRID (if present) and filter to those drivers
    """
    df: Optional[pd.DataFrame] = None

    # 1) Try Qualifying
    try:
        q_res = _load_results_only(year, gp_name, "Q").copy()
        q_res["DriverNumber"] = q_res["DriverNumber"].astype(str).str.strip()
        grid_col = "GridPosition" if "GridPosition" in q_res.columns else "Position"
        need = ["DriverNumber", "Abbreviation", "TeamName", grid_col]
        if all(c in q_res.columns for c in need):
            df = q_res[need].rename(
                columns={grid_col: "grid_pos", "Abbreviation": "driver", "TeamName": "team"}
            ).copy()
            df.loc[:, "year"] = year
            df.loc[:, "gp"] = gp_name
            df.loc[:, "date"] = _event_date(year, gp_name)
            df = df[["year", "gp", "date", "driver", "team", "grid_pos", "DriverNumber"]]
    except Exception:
        df = None  # fall through

    # 2) Try FP1 if Q missing
    if df is None:
        try:
            fp_res = _load_results_only(year, gp_name, "FP1").copy()
            fp_res["DriverNumber"] = fp_res["DriverNumber"].astype(str).str.strip()
            need = ["DriverNumber", "Abbreviation", "TeamName"]
            if all(c in fp_res.columns for c in need):
                df = fp_res[need].rename(columns={"Abbreviation": "driver", "TeamName": "team"}).copy()
                df.loc[:, "grid_pos"] = pd.NA
                df.loc[:, "year"] = year
                df.loc[:, "gp"] = gp_name
                df.loc[:, "date"] = _event_date(year, gp_name)
                df = df[["year", "gp", "date", "driver", "team", "grid_pos", "DriverNumber"]]
        except Exception:
            df = None  # fall through

    # 3) Fallback: latest completed race before target
    if df is None:
        ref = None
        try:
            prior_events = list_before_target(year, gp_name)
        except Exception:
            prior_events = []
        for prev_gp in reversed(prior_events):
            try:
                r_res = _load_results_only(year, prev_gp, "R").copy()
                if r_res is None or len(r_res) == 0:
                    continue
                r_res["DriverNumber"] = r_res["DriverNumber"].astype(str).str.strip()
                need = ["DriverNumber", "Abbreviation", "TeamName"]
                if all(c in r_res.columns for c in need):
                    ref = r_res[need].rename(
                        columns={"Abbreviation": "driver", "TeamName": "team"}
                    ).copy()
                    break
            except Exception:
                continue

        if ref is None or ref.empty:
            raise RuntimeError(
                f"No entry list available for {gp_name} {year}: Q/FP1 empty and no prior race with results."
            )

        ref.loc[:, "grid_pos"] = pd.NA
        ref.loc[:, "year"] = year
        ref.loc[:, "gp"] = gp_name
        ref.loc[:, "date"] = _event_date(year, gp_name)
        df = ref[["year", "gp", "date", "driver", "team", "grid_pos", "DriverNumber"]]

    # ---- Canonicalize to roster (removes placeholders from FP) ----
    try:
        df = _canonicalize_pred_entrylist(df, year, gp_name)
    except Exception as e:
        print(f"[WARN] Could not canonicalize roster for {gp_name} {year}: {e}")

    # ---- Apply hardcoded grid for this event if provided ----
    df = _apply_hardcoded_grid(df, year, gp_name)

    return df
