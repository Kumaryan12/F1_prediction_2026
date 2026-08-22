"use client";

import { useState } from "react";

async function runSimulation(driver: string, gridPos: number) {
  const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
  const res = await fetch(`${API_BASE}/simulate`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ driver, grid_pos: gridPos }) });
  if (!res.ok) { const errorData = await res.json().catch(() => ({})); throw new Error(errorData.detail || "Simulation failed"); }
  return res.json();
}

type DriverData = { driver: string; team: string; pred_rank?: number; grid_pos?: number };

export default function Simulator({ predictions }: { predictions: DriverData[] }) {
  const [selectedDriver, setSelectedDriver] = useState(predictions[0]?.driver || "VER");
  const [customGrid, setCustomGrid] = useState(10);
  const [isSimulating, setIsSimulating] = useState(false);
  const [error, setError] = useState("");
  const [simResult, setSimResult] = useState<{ new_predicted_rank: number; simulated_grid: number } | null>(null);
  const currentData = predictions.find((p) => p.driver === selectedDriver) || predictions[0];

  const handleSimulate = async () => {
    setIsSimulating(true); setSimResult(null); setError("");
    try { setSimResult(await runSimulation(selectedDriver, customGrid)); }
    catch (e) { setError(e instanceof Error ? e.message : "Simulation failed"); }
    finally { setIsSimulating(false); }
  };

  return (
    <div className="border border-white/10 bg-[#111315]">
      <header className="border-b border-white/10 p-5"><p className="font-mono text-[8px] font-bold uppercase tracking-[0.22em] text-dutch-orange">Scenario tool</p><h2 className="mt-1 text-2xl font-black uppercase italic tracking-[-0.04em] text-white">What-if simulator</h2></header>
      <div className="grid lg:grid-cols-[1.2fr_.8fr]">
        <div className="space-y-7 p-5 sm:p-7 lg:border-r lg:border-white/10">
          <label className="block"><span className="mb-2 block font-mono text-[8px] uppercase tracking-[0.18em] text-zinc-500">Target driver</span><select className="w-full border border-white/15 bg-tarmac px-4 py-3 text-lg font-black uppercase italic text-white outline-none focus:border-dutch-orange" value={selectedDriver} onChange={(e) => setSelectedDriver(e.target.value)}>{predictions.map((p) => <option key={p.driver} value={p.driver}>{p.driver} · {p.team}</option>)}</select></label>
          <label className="block"><span className="mb-3 flex justify-between font-mono text-[8px] uppercase tracking-[0.18em] text-zinc-500"><span>Simulated grid position</span><strong className="text-xl text-dutch-orange">P{customGrid}</strong></span><input type="range" min="1" max="20" value={customGrid} onChange={(e) => setCustomGrid(Number(e.target.value))} className="h-2 w-full cursor-pointer appearance-none bg-black" /><span className="mt-2 flex justify-between font-mono text-[8px] text-zinc-700"><span>POLE / P1</span><span>BACK / P20</span></span></label>
          <button onClick={handleSimulate} disabled={isSimulating} className="w-full bg-dutch-orange py-4 text-sm font-black uppercase italic tracking-[0.14em] text-black transition-colors hover:bg-white disabled:cursor-not-allowed disabled:bg-zinc-700">{isSimulating ? "Calculating…" : "Run scenario"}</button>
          {error && <p role="alert" className="border border-dutch-red bg-dutch-red/10 p-3 font-mono text-[9px] uppercase text-red-300">{error}</p>}
        </div>
        <div className="bg-tarmac p-5 sm:p-7"><p className="mb-5 font-mono text-[8px] uppercase tracking-[0.2em] text-zinc-600">Scenario output</p><div className="grid grid-cols-2 gap-px bg-white/10"><Result label="Baseline grid" value={`P${currentData?.grid_pos || 0}`} /><Result label="Baseline finish" value={`P${currentData?.pred_rank || 0}`} muted /><Result label="New grid" value={simResult ? `P${simResult.simulated_grid}` : "—"} /><Result label="New forecast" value={simResult ? `P${simResult.new_predicted_rank}` : "—"} accent /></div></div>
      </div>
    </div>
  );
}

function Result({ label, value, muted, accent }: { label: string; value: string; muted?: boolean; accent?: boolean }) {
  return <div className="bg-[#111315] p-4"><p className="font-mono text-[8px] uppercase tracking-[0.14em] text-zinc-600">{label}</p><p className={`mt-2 text-3xl font-black italic ${accent ? "text-dutch-orange" : muted ? "text-zinc-500" : "text-white"}`}>{value}</p></div>;
}
