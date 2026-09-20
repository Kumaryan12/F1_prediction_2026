"use client";
import { useState } from "react";
import { ArrowLeftRight, ArrowUpRight } from "lucide-react";
import type { PredictionRow } from "@/lib/types";
import { driverName, percent, position, teamColor } from "@/lib/presentation";

export default function HeadToHead({ predictions }: { predictions: PredictionRow[] }) {
  const [driverA, setDriverA] = useState(predictions[0]?.driver || "");
  const [driverB, setDriverB] = useState(predictions[1]?.driver || "");
  const a = predictions.find((row) => row.driver === driverA);
  const b = predictions.find((row) => row.driver === driverB);
  if (!a || !b) return <div className="panel empty-state">At least two drivers are needed for a comparison.</div>;
  const gap = Math.abs(a.pred_rank - b.pred_rank);
  const favourite = a.pred_rank < b.pred_rank ? a : b;
  return <div className="panel comparison-panel">
    <div className="panel-heading"><span className="eyebrow">THE MATCHUP</span><button className="icon-button" aria-label="Swap drivers" onClick={() => { setDriverA(driverB); setDriverB(driverA); }}><ArrowLeftRight size={16} /></button></div>
    <div className="matchup-selectors"><DriverSelect label="First driver" selected={driverA} other={driverB} predictions={predictions} onChange={setDriverA} /><span className="versus">VS</span><DriverSelect label="Second driver" selected={driverB} other={driverA} predictions={predictions} onChange={setDriverB} /></div>
    <div className="matchup-names"><div><small>{driverName(a.driver).split(" ")[0]}</small><h3>{driverName(a.driver).split(" ").slice(1).join(" ")}</h3><span style={{ color: teamColor(a.team) }}>{a.team}</span></div><div><small>{driverName(b.driver).split(" ")[0]}</small><h3>{driverName(b.driver).split(" ").slice(1).join(" ")}</h3><span style={{ color: teamColor(b.team) }}>{b.team}</span></div></div>
    <div className="comparison-stats"><Compare label="Starting grid" a={position(a.grid_pos)} b={position(b.grid_pos)} /><Compare label="Predicted finish" a={position(a.pred_rank)} b={position(b.pred_rank)} /><Compare label="Podium probability" a={percent(a.p_podium)} b={percent(b.p_podium)} /><Compare label="Win probability" a={percent(a.p_win)} b={percent(b.p_win)} /></div>
    <div className="comparison-verdict" aria-live="polite"><ArrowUpRight size={18} /><p>{gap ? <><strong>{favourite.driver} has the edge.</strong> Projected {gap} {gap === 1 ? "position" : "positions"} ahead.</> : "The model projects the same finishing position."}<small>Based on predicted rank, not a head-to-head win probability.</small></p></div>
  </div>;
}
function DriverSelect({ label, selected, other, predictions, onChange }: { label: string; selected: string; other: string; predictions: PredictionRow[]; onChange: (value: string) => void }) {
  return <label className="driver-select"><span>{label}</span><select value={selected} onChange={(event) => onChange(event.target.value)}>{predictions.map((row) => <option key={row.driver} value={row.driver} disabled={row.driver === other}>{row.driver} · {driverName(row.driver)}</option>)}</select></label>;
}
function Compare({ label, a, b }: { label: string; a: string; b: string }) { return <div><strong>{a}</strong><span>{label}</span><strong>{b}</strong></div>; }
