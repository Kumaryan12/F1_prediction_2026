"use client";
import { useMemo, useState } from "react";
import { ArrowDown, ArrowUp, Search, SlidersHorizontal } from "lucide-react";
import PredictionTable from "@/components/PredictionTable";
import { driverName, percent, position, teamColor } from "@/lib/presentation";
import type { PredictionRow } from "@/lib/types";

export default function ForecastExplorer({ rows }: { rows: PredictionRow[] }) {
  const [view, setView] = useState("overview");
  const [search, setSearch] = useState("");
  const [sort, setSort] = useState("rank");
  const filtered = useMemo(() => rows.filter((row) => `${driverName(row.driver)} ${row.driver} ${row.team}`.toLowerCase().includes(search.toLowerCase())).sort((a, b) => sort === "win" ? (b.p_win ?? -1) - (a.p_win ?? -1) : a.pred_rank - b.pred_rank), [rows, search, sort]);
  return <div className="forecast-explorer panel">
    <div className="table-toolbar"><div className="segmented-control" aria-label="Prediction detail level">{["overview", "all metrics"].map((label) => <button key={label} aria-pressed={view === label} onClick={() => setView(label)}>{label}</button>)}</div><label className="search-field"><Search size={14} /><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Find a driver or team" aria-label="Find a driver or team" /></label><label className="sort-control"><SlidersHorizontal size={13} /><select aria-label="Sort predictions" value={sort} onChange={(event) => setSort(event.target.value)}><option value="rank">Predicted order</option><option value="win">Win probability</option></select></label></div>
    {filtered.length === 0 ? <div className="empty-state"><Search size={23} /><h3>No drivers found</h3><p>Try a driver name, abbreviation, or team.</p><button className="button button-light" onClick={() => setSearch("")}>Clear search</button></div> : view === "all metrics" ? <PredictionTable rows={filtered} /> : <div className="table-scroll" tabIndex={0} role="region" aria-label="Predicted race classification"><table className="overview-table"><thead><tr><th scope="col">Pos.</th><th scope="col">Driver</th><th scope="col">Movement</th><th scope="col">Win chance</th><th scope="col">Podium</th><th scope="col">68% interval</th></tr></thead><tbody>{filtered.map((row) => {
      const movement = row.grid_pos != null && row.grid_pos > 0 ? row.grid_pos - row.pred_rank : null;
      return <tr key={row.driver}><td><span className={`rank-pill ${row.pred_rank <= 3 ? "rank-top" : ""}`}>{String(row.pred_rank).padStart(2, "0")}</span></td><td><div className="table-driver"><i style={{ background: teamColor(row.team) }} /><div><strong>{driverName(row.driver)}</strong><small>{row.team} <span> / {row.driver}</span></small></div></div></td><td><span className={`movement ${movement && movement > 0 ? "positive" : movement && movement < 0 ? "negative" : ""}`}>{movement == null ? "—" : movement === 0 ? "— Hold" : <>{movement > 0 ? <ArrowUp size={12} /> : <ArrowDown size={12} />}{Math.abs(movement)}</>}</span></td><td><div className="probability-cell"><strong>{percent(row.p_win)}</strong><div><i style={{ width: `${Math.min(100, Math.max(0, (row.p_win ?? 0) * 100))}%` }} /></div></div></td><td className="numeric">{percent(row.p_podium)}</td><td className="numeric interval-cell">{position(row.pi68_low)}<span> — </span>{position(row.pi68_high)}</td></tr>;
    })}</tbody></table></div>}
    <div className="table-footnote"><span><i className="status-dot" />{filtered.length} of {rows.length} drivers</span><span>Movement from grid · Intervals rounded to positions</span></div>
  </div>;
}
