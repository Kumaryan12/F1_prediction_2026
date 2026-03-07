# F1_prediction_system/data.py
from __future__ import annotations

from typing import List, Dict, Tuple, Optional
import pandas as pd
import fastf1

from .config import CACHE_DIR, FALLBACK_EVENTS, EXCLUDE_EVENTS

fastf1.Cache.enable_cache(CACHE_DIR)


# -------------------------------------------------------------------
# Hardcoded race entry lists
# -------------------------------------------------------------------
# Use this for season openers / lineup resets / new teams.
# DriverNumber values can be refreshed automatically from live FP2/FP1/Q.

HARDCODED_ENTRYLISTS: Dict[Tuple[int, str], List[Dict[str, object]]] = {
    (2026, "Australian Grand Prix"): [
        {"driver": "VER", "team": "Red Bull Racing", "grid_pos": 20, "DriverNumber": "3"},
        {"driver": "HAD", "team": "Red Bull Racing", "grid_pos": 2, "DriverNumber": "6"},

        {"driver": "NOR", "team": "McLaren", "grid_pos": 3, "DriverNumber": "1"},
        {"driver": "PIA", "team": "McLaren", "grid_pos": 4, "DriverNumber": "81"},

        {"driver": "LEC", "team": "Ferrari", "grid_pos": 5, "DriverNumber": "16"},
        {"driver": "HAM", "team": "Ferrari", "grid_pos": 6, "DriverNumber": "44"},

        {"driver": "RUS", "team": "Mercedes", "grid_pos": 7, "DriverNumber": "63"},
        {"driver": "ANT", "team": "Mercedes", "grid_pos": 8, "DriverNumber": "12"},

        {"driver": "ALO", "team": "Aston Martin", "grid_pos": 9, "DriverNumber": "14"},
        {"driver": "STR", "team": "Aston Martin", "grid_pos": 10, "DriverNumber": "18"},

        {"driver": "GAS", "team": "Alpine", "grid_pos": 11, "DriverNumber": "10"},
        {"driver": "COL", "team": "Alpine", "grid_pos": 12, "DriverNumber": "43"},

        {"driver": "SAI", "team": "Williams", "grid_pos": 13, "DriverNumber": "55"},
        {"driver": "ALB", "team": "Williams", "grid_pos": 14, "DriverNumber": "23"},

        {"driver": "LAW", "team": "Racing Bulls", "grid_pos": 15, "DriverNumber": "30"},
        {"driver": "LIN", "team": "Racing Bulls", "grid_pos": 16, "DriverNumber": "41"},

        {"driver": "HUL", "team": "Audi", "grid_pos": 17, "DriverNumber": "27"},
        {"driver": "BOR", "team": "Audi", "grid_pos": 18, "DriverNumber": "5"},

        {"driver": "PER", "team": "Cadillac", "grid_pos": 19, "DriverNumber": "11"},
        {"driver": "BOT", "team": "Cadillac", "grid_pos": 20, "DriverNumber": "77"},

        {"driver": "OCO", "team": "Haas F1 Team", "grid_pos": 21, "DriverNumber": "87"},
        {"driver": "BEA", "team": "Haas F1 Team", "grid_pos": 22, "DriverNumber": "31"},
    ],
}


# -------------------------------------------------------------------
# Hardcoded Sunday starting grids
# -------------------------------------------------------------------
# This remains the single source of truth for final Sunday start order.

STARTING_GRIDS: Dict[Tuple[int, str], Dict[str, int]] = {
    (2025, "Abu Dhabi Grand Prix"): {
        "PIA": 3, "NOR": 2, "VER": 20, "HAD": 9, "RUS": 4, "LEC": 5, "HAM": 16,
        "LAW": 13, "SAI": 12, "ALO": 6, "ANT": 14, "TSU": 10, "BOR": 7, "GAS": 19,
        "ALB": 17, "COL": 20, "HUL": 18, "OCO": 8, "BEA": 11, "STR": 15
    },
    # Example:
    # (2026, "Australian Grand Prix"): {
    #     "NOR": 1,
    #     "VER": 2,
    #     ...
    # },
}


# -------------------------------------------------------------------
# Schedule helpers
# -------------------------------------------------------------------

def _event_schedule(year: int) -> pd.DataFrame:
    """
    Return event schedule with columns: gp, date.
    Falls back to FALLBACK_EVENTS if live schedule is unavailable.
    """
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


def list_gp_events(year: int) -> List[str]:
    return _event_schedule(year)["gp"].tolist()


def list_before_target(year: int, target_gp: str) -> List[str]:
    sch = _event_schedule(year)
    if target_gp not in sch["gp"].values:
        raise ValueError(f"Target gp {target_gp} not found in {year} schedule")
    tgt_date = sch.loc[sch["gp"] == target_gp, "date"].iloc[0]
    return sch.loc[sch["date"] < tgt_date, "gp"].tolist()


def _event_date(year: int, gp_name: str):
    sch = _event_schedule(year)
    row = sch.loc[sch["gp"] == gp_name]
    if row.empty:
        return None
    return row["date"].iloc[0]


# -------------------------------------------------------------------
# Session / result loaders
# -------------------------------------------------------------------

def _race_has_results(year: int, gp: str) -> bool:
    try:
        ses = fastf1.get_session(year, gp, "R")
        ses.load(telemetry=False, laps=False, weather=False, messages=False)
        res = ses.results
        return (res is not None) and (not res.empty)
    except Exception:
        return False


def _load_results_only(year: int, gp: str, sess_name: str) -> pd.DataFrame:
    """
    Load session results only, robustly.
    """
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


# -------------------------------------------------------------------
# Live driver-number helpers
# -------------------------------------------------------------------

def _get_live_driver_map(
    year: int,
    gp_name: str,
    session_codes: tuple[str, ...] = ("FP2", "FP1", "Q"),
) -> pd.DataFrame:
    """
    Build current-event driver -> DriverNumber -> team map from live sessions.
    Priority: FP2, then FP1, then Q.
    """
    for code in session_codes:
        try:
            sess = fastf1.get_session(year, gp_name, code)
            sess.load()

            laps = getattr(sess, "laps", None)
            if laps is None or laps.empty:
                continue

            need = {"Driver", "DriverNumber"}
            if not need.issubset(laps.columns):
                continue

            cols = ["Driver", "DriverNumber"]
            if "Team" in laps.columns:
                cols.append("Team")

            tmp = laps[cols].dropna(subset=["Driver", "DriverNumber"]).copy()
            if tmp.empty:
                continue

            tmp["driver"] = tmp["Driver"].astype(str).str.upper()
            tmp["DriverNumber_live"] = tmp["DriverNumber"].astype(str).str.strip()
            if "Team" in tmp.columns:
                tmp["team_live"] = tmp["Team"].astype(str)
            else:
                tmp["team_live"] = pd.NA

            tmp = (
                tmp[["driver", "DriverNumber_live", "team_live"]]
                .drop_duplicates(subset=["driver"])
                .reset_index(drop=True)
            )
            return tmp

        except Exception:
            continue

    return pd.DataFrame(columns=["driver", "DriverNumber_live", "team_live"])


def _hydrate_entrylist_driver_numbers(df: pd.DataFrame, year: int, gp_name: str) -> pd.DataFrame:
    """
    Refresh DriverNumber in a hardcoded entry list using current live session data.
    Prefer live numbers if available.
    """
    out = df.copy()
    if "driver" not in out.columns:
        return out

    live_map = _get_live_driver_map(year, gp_name)
    if live_map.empty:
        return out

    out = out.merge(live_map, on="driver", how="left")

    if "DriverNumber" not in out.columns:
        out["DriverNumber"] = pd.NA

    out["DriverNumber"] = (
        out["DriverNumber_live"]
        .fillna(out["DriverNumber"])
        .astype(str)
        .replace("nan", pd.NA)
    )

    if "team_live" in out.columns:
        out["team"] = out["team"].fillna(out["team_live"])

    out = out.drop(columns=["DriverNumber_live", "team_live"], errors="ignore")
    return out


# -------------------------------------------------------------------
# Roster / entry-list helpers
# -------------------------------------------------------------------

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
    Canonical season roster = last completed race before the target.

    Returns columns:
      DriverNumber (str), driver (abbr), team
    """
    last_gp = _last_completed_event(year, target_gp)
    if not last_gp:
        raise RuntimeError(f"No completed race found before {target_gp} {year} to build roster map.")

    r_res = _load_results_only(year, last_gp, "R").copy()
    num_col = "DriverNumber"
    abbr_col = "Abbreviation" if "Abbreviation" in r_res.columns else "Driver"
    team_col = "TeamName" if "TeamName" in r_res.columns else "Team"

    roster = r_res[[num_col, abbr_col, team_col]].rename(
        columns={num_col: "DriverNumber", abbr_col: "driver", team_col: "team"}
    ).copy()
    roster.loc[:, "DriverNumber"] = roster["DriverNumber"].astype(str)
    roster.loc[:, "driver"] = roster["driver"].astype(str).str.upper()
    roster.loc[:, "team"] = roster["team"].astype(str)
    roster = roster.drop_duplicates(subset=["DriverNumber"]).reset_index(drop=True)

    return roster[["DriverNumber", "driver", "team"]]


def _build_from_roster(year: int, gp_name: str) -> pd.DataFrame:
    """
    Build a prediction entry list from the latest known season roster.
    Used when hardcoded Sunday grid is present for a non-opener.
    """
    roster = _get_roster_map(year, gp_name).copy()
    roster.loc[:, "grid_pos"] = pd.NA
    roster.loc[:, "year"] = year
    roster.loc[:, "gp"] = gp_name
    roster.loc[:, "date"] = _event_date(year, gp_name)

    return roster[["year", "gp", "date", "driver", "team", "grid_pos", "DriverNumber"]]


def _build_from_hardcoded_entrylist(year: int, gp_name: str) -> pd.DataFrame:
    """
    Build target entry list directly from HARDCODED_ENTRYLISTS.
    Correct path for season openers / lineup resets.
    """
    rows = HARDCODED_ENTRYLISTS[(year, gp_name)]
    df = pd.DataFrame(rows).copy()

    df.loc[:, "driver"] = df["driver"].astype(str).str.upper()
    df.loc[:, "team"] = df["team"].astype(str)

    if "grid_pos" not in df.columns:
        df.loc[:, "grid_pos"] = pd.NA
    if "DriverNumber" not in df.columns:
        df.loc[:, "DriverNumber"] = pd.NA

    df.loc[:, "year"] = year
    df.loc[:, "gp"] = gp_name
    df.loc[:, "date"] = _event_date(year, gp_name)

    df = df[["year", "gp", "date", "driver", "team", "grid_pos", "DriverNumber"]].copy()

    # Refresh DriverNumbers from live FP2/FP1/Q if available
    df = _hydrate_entrylist_driver_numbers(df, year, gp_name)

    return df


def _canonicalize_pred_entrylist(pred_df: pd.DataFrame, year: int, target_gp: str) -> pd.DataFrame:
    """
    Overwrite pred_df['driver','team'] using canonical roster keyed by DriverNumber.
    Drop non-roster FP/test entries; dedupe by DriverNumber.

    If DriverNumber is missing for hardcoded entrylists, this function becomes a no-op.
    """
    out = pred_df.copy()
    if "DriverNumber" not in out.columns:
        return out

    if out["DriverNumber"].isna().all():
        return out

    out.loc[:, "DriverNumber"] = out["DriverNumber"].astype(str)
    roster = _get_roster_map(year, target_gp)

    out = out.merge(roster, on="DriverNumber", how="left", suffixes=("", "_canon"))
    out.loc[:, "driver"] = out["driver_canon"].fillna(out["driver"])
    out.loc[:, "team"] = out["team_canon"].fillna(out["team"])

    keep = out["driver_canon"].notna()
    dropped = int((~keep).sum())
    if dropped > 0:
        print(f"[INFO] Filtering to season roster: dropped {dropped} FP/test entries")

    out = out.loc[keep].drop(columns=["driver_canon", "team_canon"]).copy()
    out = out.drop_duplicates(subset=["DriverNumber"]).reset_index(drop=True)
    out.loc[:, "driver"] = out["driver"].astype(str).str.upper()

    return out


# -------------------------------------------------------------------
# Hardcoded grid application
# -------------------------------------------------------------------

def _apply_hardcoded_grid(df: pd.DataFrame, year: int, gp_name: str) -> pd.DataFrame:
    """
    If a hardcoded Sunday grid exists for (year, gp_name), filter to those drivers
    and overwrite grid_pos from STARTING_GRIDS.
    """
    mapping = STARTING_GRIDS.get((year, gp_name))
    if not mapping:
        return df

    out = df.copy()
    out.loc[:, "driver"] = out["driver"].astype(str).str.upper()

    before = len(out)
    out = out[out["driver"].isin(mapping.keys())].copy()
    kept = len(out)
    print(f"[INFO] Hardcoded grid applied for {gp_name} {year}: kept {kept}/{before} drivers")

    out.loc[:, "grid_pos"] = out["driver"].map(mapping).astype("Int64")

    if out["grid_pos"].notna().all():
        out = out.sort_values("grid_pos").reset_index(drop=True)

    missing = sorted(set(mapping.keys()) - set(out["driver"].unique()))
    if missing:
        print(f"[WARN] Drivers in hardcoded grid not found in entry list: {missing}")

    return out


# -------------------------------------------------------------------
# Training event extraction
# -------------------------------------------------------------------

def extract_event_qr(year: int, gp_name: str) -> pd.DataFrame:
    """
    Return one row per driver with grid_pos and finish_pos.
    Prefer both from Race results; fall back to Quali for grid only if needed.

    IMPORTANT:
    - Do NOT apply hardcoded Sunday grids here
    - Keep training leakage-safe
    """
    r_res = _load_results_only(year, gp_name, "R")
    if r_res is None or len(r_res) == 0:
        raise RuntimeError("race results empty")

    r_res = r_res.copy()
    r_res.loc[:, "DriverNumber"] = r_res["DriverNumber"].astype(str).str.strip()

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
            ).copy()

    # 2) Otherwise: grid from Quali + finish from Race
    if df is None:
        q_res = _load_results_only(year, gp_name, "Q").copy()
        q_res.loc[:, "DriverNumber"] = q_res["DriverNumber"].astype(str).str.strip()
        q_grid_col = "GridPosition" if "GridPosition" in q_res.columns else "Position"

        need_q = ["DriverNumber", "Abbreviation", "TeamName", q_grid_col]
        need_r = ["DriverNumber", fin_col]
        if not all(c in q_res.columns for c in need_q) or not all(c in r_res.columns for c in need_r):
            raise KeyError("Missing columns for Q/R merge")

        qi = q_res[need_q].rename(
            columns={q_grid_col: "grid_pos", "Abbreviation": "driver", "TeamName": "team"}
        ).copy()
        ri = r_res[need_r].rename(columns={fin_col: "finish_pos"}).copy()
        df = qi.merge(ri, on="DriverNumber", how="inner").copy()

    df = df.copy()
    df.loc[:, "driver"] = df["driver"].astype(str).str.upper()
    df.loc[:, "grid_pos"] = pd.to_numeric(df["grid_pos"], errors="coerce")
    df.loc[:, "finish_pos"] = pd.to_numeric(df["finish_pos"], errors="coerce")
    df = df.dropna(subset=["grid_pos", "finish_pos"]).copy()

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
        raise RuntimeError(f"No events loaded. Sample errors: {errors[:3]}")

    return pd.concat(out, ignore_index=True)


def build_training_until(
    target_year: int,
    target_gp: str,
    hist_years=range(2023, 2025),
) -> pd.DataFrame:
    """
    Build training data from historical years + current season races before target.
    """
    from time import perf_counter

    def _not_excluded(year: int, gp: str) -> bool:
        return gp not in EXCLUDE_EVENTS.get(year, set())

    rows = []

    # Historical years
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


# -------------------------------------------------------------------
# Target drivers for prediction
# -------------------------------------------------------------------

def get_target_drivers(year: int, gp_name: str) -> pd.DataFrame:
    """
    Return driver/team/grid for the target event.

    Preference:
      1) If hardcoded full entry list exists -> use it
      2) Otherwise if hardcoded Sunday grid exists -> build from latest season roster and apply it
      3) Otherwise try Qualifying results
      4) Otherwise fallback to latest completed race before target
    """
    # 1) Prefer hardcoded full entry list
    if (year, gp_name) in HARDCODED_ENTRYLISTS:
        df = _build_from_hardcoded_entrylist(year, gp_name)
        df = _apply_hardcoded_grid(df, year, gp_name)
        return df

    # 2) Prefer hardcoded Sunday grid if present
    if (year, gp_name) in STARTING_GRIDS:
        try:
            df = _build_from_roster(year, gp_name)
            df = _apply_hardcoded_grid(df, year, gp_name)
            return df
        except Exception as e:
            print(f"[WARN] Failed to build target drivers from hardcoded grid for {gp_name} {year}: {e}")
            print("[INFO] Falling back to dynamic entry-list logic.")

    df: Optional[pd.DataFrame] = None

    # 3) Try Qualifying
    try:
        q_res = _load_results_only(year, gp_name, "Q").copy()
        q_res.loc[:, "DriverNumber"] = q_res["DriverNumber"].astype(str).str.strip()
        grid_col = "GridPosition" if "GridPosition" in q_res.columns else "Position"

        need = ["DriverNumber", "Abbreviation", "TeamName", grid_col]
        if all(c in q_res.columns for c in need):
            df = q_res[need].rename(
                columns={grid_col: "grid_pos", "Abbreviation": "driver", "TeamName": "team"}
            ).copy()
            df.loc[:, "driver"] = df["driver"].astype(str).str.upper()
            df.loc[:, "year"] = year
            df.loc[:, "gp"] = gp_name
            df.loc[:, "date"] = _event_date(year, gp_name)
            df = df[["year", "gp", "date", "driver", "team", "grid_pos", "DriverNumber"]]
    except Exception:
        df = None

    # 4) Fallback: latest completed race before target
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

                r_res.loc[:, "DriverNumber"] = r_res["DriverNumber"].astype(str).str.strip()
                need = ["DriverNumber", "Abbreviation", "TeamName"]
                if all(c in r_res.columns for c in need):
                    ref = r_res[need].rename(
                        columns={"Abbreviation": "driver", "TeamName": "team"}
                    ).copy()
                    ref.loc[:, "driver"] = ref["driver"].astype(str).str.upper()
                    break
            except Exception:
                continue

        if ref is None or ref.empty:
            raise RuntimeError(
                f"No entry list available for {gp_name} {year}: no hardcoded entrylist/grid, Q unavailable, and no prior race roster."
            )

        ref.loc[:, "grid_pos"] = pd.NA
        ref.loc[:, "year"] = year
        ref.loc[:, "gp"] = gp_name
        ref.loc[:, "date"] = _event_date(year, gp_name)
        df = ref[["year", "gp", "date", "driver", "team", "grid_pos", "DriverNumber"]]

    # Canonicalize to season roster if possible
    try:
        df = _canonicalize_pred_entrylist(df, year, gp_name)
    except Exception as e:
        print(f"[WARN] Could not canonicalize roster for {gp_name} {year}: {e}")

    # Apply hardcoded grid if available
    df = _apply_hardcoded_grid(df, year, gp_name)
    return df