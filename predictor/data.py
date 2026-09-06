from __future__ import annotations

from typing import Dict, List, Optional
import pandas as pd
import fastf1

from .config import CACHE_DIR, FALLBACK_EVENTS, EXCLUDE_EVENTS

fastf1.Cache.enable_cache(CACHE_DIR)


TARGET_DRIVER_COLUMNS = ["year", "gp", "date", "driver", "team", "grid_pos", "DriverNumber"]

GP_NAME_ALIASES = {
    "Austria Grand Prix": "Austrian Grand Prix",
}


MANUAL_GRID_YEAR = 2026
MANUAL_GRID_GP = "Italian Grand Prix"
MANUAL_STARTING_GRID: Dict[str, int] = {
    "RUS": 2,
    "LEC": 3,
    "HAM": 4,
    "ANT": 20,
    "VER": 5,
    "NOR": 8,
    "PIA": 6,
    "HAD": 99,
    "LAW": 22,
    "LIN": 9,
    "GAS": 1,
    "BOR": 10,
    "BEA": 11,
    "HUL": 12,
    "OCO": 14,
    "COL": 7,
    "SAI": 13,
    "ALB": 21,
    "PER": 17,
    "BOT": 16,
    "ALO": 18,
    "STR": 19,
}


def _canonical_gp_name(gp_name: str) -> str:
    return GP_NAME_ALIASES.get(gp_name, gp_name)


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


def list_gp_events(year: int) -> List[str]:
    return _event_schedule(year)["gp"].tolist()


def list_before_target(year: int, target_gp: str) -> List[str]:
    target_gp = _canonical_gp_name(target_gp)
    sch = _event_schedule(year)
    if target_gp not in sch["gp"].values:
        raise ValueError(f"Target gp {target_gp} not found in {year} schedule")
    tgt_date = sch.loc[sch["gp"] == target_gp, "date"].iloc[0]
    return sch.loc[sch["date"] < tgt_date, "gp"].tolist()


def _event_date(year: int, gp_name: str):
    gp_name = _canonical_gp_name(gp_name)
    sch = _event_schedule(year)
    row = sch.loc[sch["gp"] == gp_name]
    if row.empty:
        return None
    return row["date"].iloc[0]


def _active_manual_starting_grid(year: int, gp_name: str) -> Optional[Dict[str, int]]:
    if year != MANUAL_GRID_YEAR:
        return None
    if _canonical_gp_name(gp_name) != _canonical_gp_name(MANUAL_GRID_GP):
        return None
    return MANUAL_STARTING_GRID


def _format_target_driver_frame(df: pd.DataFrame, year: int, gp_name: str) -> pd.DataFrame:
    out = df.copy()

    if "driver" not in out.columns:
        raise KeyError("Target driver frame missing required column: driver")
    if "team" not in out.columns:
        out["team"] = pd.NA
    if "grid_pos" not in out.columns:
        out["grid_pos"] = pd.NA
    if "DriverNumber" not in out.columns:
        out["DriverNumber"] = pd.NA

    gp_name = _canonical_gp_name(gp_name)
    out.loc[:, "year"] = year
    out.loc[:, "gp"] = gp_name
    out.loc[:, "date"] = _event_date(year, gp_name)
    out.loc[:, "driver"] = out["driver"].astype(str).str.upper()
    out.loc[:, "team"] = out["team"].astype(str)
    out.loc[:, "DriverNumber"] = (
        out["DriverNumber"]
        .astype(str)
        .str.strip()
        .replace({"nan": pd.NA, "None": pd.NA, "<NA>": pd.NA})
    )

    return out[TARGET_DRIVER_COLUMNS].copy()


def _race_has_results(year: int, gp: str) -> bool:
    gp = _canonical_gp_name(gp)
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
    gp = _canonical_gp_name(gp)
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
    target_gp = _canonical_gp_name(target_gp)
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
    roster = _get_roster_map(year, gp_name).copy()
    roster.loc[:, "grid_pos"] = pd.NA
    return _format_target_driver_frame(roster, year, gp_name)


def _canonicalize_pred_entrylist(pred_df: pd.DataFrame, year: int, target_gp: str) -> pd.DataFrame:
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


def _validate_manual_starting_grid(mapping: Dict[str, int], year: int, gp_name: str) -> None:
    positions = list(mapping.values())
    duplicate_positions = sorted({pos for pos in positions if positions.count(pos) > 1})
    invalid_positions = sorted(pos for pos in positions if int(pos) < 1)

    if duplicate_positions:
        raise ValueError(
            f"Manual starting grid for {gp_name} {year} has duplicate positions: {duplicate_positions}"
        )
    if invalid_positions:
        raise ValueError(
            f"Manual starting grid for {gp_name} {year} has invalid positions: {invalid_positions}"
        )


def _apply_manual_starting_grid(df: pd.DataFrame, year: int, gp_name: str) -> pd.DataFrame:
    gp_name = _canonical_gp_name(gp_name)
    mapping = _active_manual_starting_grid(year, gp_name)
    if not mapping:
        return df

    _validate_manual_starting_grid(mapping, year, gp_name)

    out = df.copy()
    out.loc[:, "driver"] = out["driver"].astype(str).str.upper()

    before = len(out)
    out = out[out["driver"].isin(mapping.keys())].copy()
    kept = len(out)
    print(f"[INFO] Manual starting grid applied for {gp_name} {year}: kept {kept}/{before} drivers")

    out.loc[:, "grid_pos"] = out["driver"].map(mapping).astype("Int64")

    if out["grid_pos"].notna().all():
        out = out.sort_values("grid_pos").reset_index(drop=True)

    missing = sorted(set(mapping.keys()) - set(out["driver"].unique()))
    if missing:
        print(f"[WARN] Drivers in manual starting grid not found in roster: {missing}")

    return out


def extract_event_qr(year: int, gp_name: str) -> pd.DataFrame:
    gp_name = _canonical_gp_name(gp_name)
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


def get_target_drivers(
    year: int,
    gp_name: str,
    use_qualifying: bool = True,
    use_manual_grid: bool = True,
) -> pd.DataFrame:
    gp_name = _canonical_gp_name(gp_name)

    # 1) If the active manual grid matches this race, combine it with the latest season roster.
    if use_manual_grid and _active_manual_starting_grid(year, gp_name):
        try:
            df = _build_from_roster(year, gp_name)
            df = _apply_manual_starting_grid(df, year, gp_name)
            return df
        except Exception as e:
            print(f"[WARN] Failed to build target drivers from manual grid for {gp_name} {year}: {e}")
            print("[INFO] Falling back to dynamic entry-list logic.")

    df: Optional[pd.DataFrame] = None

    # 2) Try Qualifying
    if use_qualifying:
        try:
            q_res = _load_results_only(year, gp_name, "Q").copy()
            q_res.loc[:, "DriverNumber"] = q_res["DriverNumber"].astype(str).str.strip()
            grid_col = "GridPosition" if "GridPosition" in q_res.columns else "Position"

            need = ["DriverNumber", "Abbreviation", "TeamName", grid_col]
            if all(c in q_res.columns for c in need):
                df = q_res[need].rename(
                    columns={grid_col: "grid_pos", "Abbreviation": "driver", "TeamName": "team"}
                ).copy()
                df = _format_target_driver_frame(df, year, gp_name)
        except Exception:
            df = None

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
                f"No roster available for {gp_name} {year}: manual grid could not be matched, Q unavailable, and no prior race roster."
            )

        ref.loc[:, "grid_pos"] = pd.NA
        df = _format_target_driver_frame(ref, year, gp_name)

    # Canonicalize to season roster if possible
    try:
        df = _canonicalize_pred_entrylist(df, year, gp_name)
    except Exception as e:
        print(f"[WARN] Could not canonicalize roster for {gp_name} {year}: {e}")

    # Apply manual grid if available
    if use_manual_grid:
        df = _apply_manual_starting_grid(df, year, gp_name)
    return df
