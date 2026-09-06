"use client";
import { useState } from "react";
import { ArrowRight, FlaskConical, LoaderCircle, RotateCcw } from "lucide-react";
import type { PredictionRow } from "@/lib/types";
import { driverName, position } from "@/lib/presentation";

type SimulationResult = { new_predicted_rank: number; simulated_grid: number };
export default function Simulator({ predictions }: { predictions: PredictionRow[] }) {
  const [driver, setDriver] = useState(predictions[0]?.driver || "");
  const [grid, setGrid] = useState(Math.min(10, predictions.length || 1));
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<SimulationResult | null>(null);
  const baseline = predictions.find((row) => row.driver === driver);
  function clearResult() { setResult(null); setError(""); }
  async function run() {
    setLoading(true); clearResult();
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"}/simulate`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ driver, grid_pos: grid }) });
      const data = await response.json();
      if (!response.ok) throw new Error(typeof data.detail === "string" ? data.detail : "The simulation could not complete. Please try again.");
      setResult(data);
    } catch (error) { setError(error instanceof Error ? error.message : "Simulation unavailable. Please try again."); }
    finally { setLoading(false); }
  }
  return <div className="panel simulator-panel"><div className="panel-heading"><span className="eyebrow">YOUR STRATEGY CALL</span><FlaskConical size={17} /></div>
    <p className="tool-intro">A different start. A different finish?<br /><span>Move a driver on the grid and rerun the forecast.</span></p>
    <fieldset disabled={loading || !predictions.length} className="simulation-inputs"><label className="driver-select"><span>Choose your driver</span><select value={driver} onChange={(event) => { setDriver(event.target.value); clearResult(); }}>{predictions.map((row) => <option key={row.driver} value={row.driver}>{driverName(row.driver)} · {row.team}</option>)}</select></label>
    <label className="grid-slider"><span>New starting position <strong>P{grid}</strong></span><input type="range" min="1" max={predictions.length || 1} value={grid} onChange={(event) => { setGrid(Number(event.target.value)); clearResult(); }} style={{ background: `linear-gradient(to right, #f34b43 ${((grid - 1) / Math.max(1, predictions.length - 1)) * 100}%, #30323b 0%)` }} /><span className="slider-labels"><span>POLE POSITION</span><span>BACK OF THE GRID</span></span></label>
    <div className="simulation-buttons"><button className="button button-red" onClick={run}>{loading ? <LoaderCircle size={15} className="spin" /> : <FlaskConical size={15} />}{loading ? "Running the numbers…" : "Run simulation"}<ArrowRight size={15} /></button><button className="icon-button" aria-label="Reset simulation" onClick={() => { setGrid(Math.min(10, predictions.length || 1)); setDriver(predictions[0]?.driver || ""); clearResult(); }}><RotateCcw size={16} /></button></div></fieldset>
    {error && <p className="error-message" role="alert">{error}</p>}
    <div className={`simulation-output ${result ? "has-result" : ""}`} aria-live="polite" aria-busy={loading}><div><span>Baseline forecast</span><strong>{position(baseline?.pred_rank)}</strong><small>Grid {position(baseline?.grid_pos)}</small></div><ArrowRight size={21} /><div><span>Simulated forecast</span><strong>{result ? position(result.new_predicted_rank) : "—"}</strong><small>{result ? `From grid P${result.simulated_grid}` : "Your result appears here"}</small></div></div>
  </div>;
}
