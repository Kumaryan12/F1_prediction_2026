"use client";

import { useState } from "react";

// 1. Moved the fetch function here so it safely runs in the browser!
async function runSimulation(driver: string, gridPos: number) {
  const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
  
  const res = await fetch(`${API_BASE}/simulate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ driver: driver, grid_pos: gridPos }),
  });

  if (!res.ok) {
    // This grabs the exact error message from FastAPI
    const errorData = await res.json().catch(() => ({}));
    console.error("Backend Error:", errorData);
    throw new Error(errorData.detail || "Simulation failed");
  }
  
  return res.json();
}

type DriverData = {
  driver: string;
  team: string;
  pred_rank?: number;
  grid_pos?: number;
};

type SimulatorProps = {
  predictions: DriverData[];
};

export default function Simulator({ predictions }: SimulatorProps) {
  const [selectedDriver, setSelectedDriver] = useState(predictions[0]?.driver || "VER");
  const [customGrid, setCustomGrid] = useState<number>(10);
  const [isSimulating, setIsSimulating] = useState(false);
  const [simResult, setSimResult] = useState<{ new_predicted_rank: number; simulated_grid: number } | null>(null);

  const currentData = predictions.find((p) => p.driver === selectedDriver) || predictions[0];
  const originalRank = currentData?.pred_rank || 0;
  const originalGrid = currentData?.grid_pos || 0;

  const handleSimulate = async () => {
    setIsSimulating(true);
    setSimResult(null);
    try {
      // 2. Calls the function we defined at the top of this file
      const result = await runSimulation(selectedDriver, customGrid);
      setSimResult(result);
    } catch (error) {
      console.error("Failed to run simulation", error);
    } finally {
      setIsSimulating(false);
    }
  };

  return (
    <div className="relative overflow-hidden rounded-2xl border border-accent-blue/20 bg-tarmac-light/90 shadow-[0_0_30px_rgba(0,160,214,0.1)] backdrop-blur-md p-6 sm:p-8 group">
      {/* Tech Background Grid */}
      <div className="absolute inset-0 opacity-[0.02] pointer-events-none"
        style={{ backgroundImage: 'linear-gradient(#fff 1px, transparent 1px), linear-gradient(90deg, #fff 1px, transparent 1px)', backgroundSize: '20px 20px' }} />

      <div className="mb-6 border-b border-white/10 pb-4 relative z-10 flex justify-between items-end">
        <div>
          <h2 className="text-2xl font-black uppercase italic tracking-tight text-white flex items-center gap-3">
            <span className="h-3 w-3 rounded-full bg-accent-blue animate-pulse shadow-[0_0_10px_rgba(0,160,214,0.8)]" />
            "What-If" Engine
          </h2>
          <p className="mt-1 text-xs font-mono text-zinc-400 uppercase tracking-widest">Live ML Prediction Sandbox</p>
        </div>
      </div>

      <div className="grid gap-8 md:grid-cols-2 relative z-10">
        {/* Left Column: Controls */}
        <div className="flex flex-col gap-6">
          
          {/* Driver Select */}
          <div>
            <label className="block text-xs font-mono text-zinc-500 uppercase tracking-widest mb-2">Target Driver</label>
            <select 
              className="w-full rounded border border-white/20 bg-black/60 px-4 py-3 text-lg font-bold italic uppercase text-white outline-none focus:border-accent-blue"
              value={selectedDriver}
              onChange={(e) => setSelectedDriver(e.target.value)}
            >
              {predictions.map((p) => (
                <option key={p.driver} value={p.driver}>{p.driver} - {p.team}</option>
              ))}
            </select>
          </div>

          {/* Grid Slider */}
          <div>
            <div className="flex justify-between items-end mb-2">
              <label className="block text-xs font-mono text-zinc-500 uppercase tracking-widest">Simulate Grid Position</label>
              <span className="text-xl font-black text-accent-blue italic drop-shadow-[0_0_8px_rgba(0,160,214,0.6)]">P{customGrid}</span>
            </div>
            <input 
              type="range" 
              min="1" max="20" 
              value={customGrid} 
              onChange={(e) => setCustomGrid(Number(e.target.value))}
              className="w-full h-2 bg-black rounded-lg appearance-none cursor-pointer accent-accent-blue"
            />
            <div className="flex justify-between text-[10px] text-zinc-600 mt-1 font-mono font-bold">
              <span>POLE (P1)</span>
              <span>BACK (P20)</span>
            </div>
          </div>

          <button 
            onClick={handleSimulate}
            disabled={isSimulating}
            className="mt-2 w-full rounded border border-accent-blue bg-accent-blue/20 py-4 font-black uppercase italic tracking-widest text-accent-blue transition-all hover:bg-accent-blue hover:text-black disabled:opacity-50 disabled:cursor-not-allowed shadow-[0_0_15px_rgba(0,160,214,0.3)] hover:shadow-[0_0_25px_rgba(0,160,214,0.6)]"
          >
            {isSimulating ? "Running Telemetry..." : "Run Simulation"}
          </button>
        </div>

        {/* Right Column: Results Panel */}
        <div className="rounded-xl border border-white/5 bg-black/40 p-6 flex flex-col justify-center">
          <h3 className="text-xs font-mono text-zinc-500 uppercase tracking-widest mb-4 border-b border-white/10 pb-2">Simulation Results</h3>
          
          <div className="grid grid-cols-2 gap-4">
            {/* Original Stats */}
            <div className="flex flex-col gap-1 opacity-50">
              <span className="text-[10px] uppercase tracking-wider text-zinc-400 font-mono">Original Grid</span>
              <span className="text-xl font-black text-white italic">P{originalGrid}</span>
              <span className="text-[10px] uppercase tracking-wider text-zinc-400 font-mono mt-2">Original Finish</span>
              <span className="text-2xl font-black text-white italic">P{originalRank}</span>
            </div>

            {/* Simulated Stats */}
            <div className="flex flex-col gap-1 border-l border-white/10 pl-4">
              <span className="text-[10px] uppercase tracking-wider text-accent-blue font-mono">Simulated Grid</span>
              <span className="text-xl font-black text-white italic">{simResult ? `P${simResult.simulated_grid}` : "--"}</span>
              <span className="text-[10px] uppercase tracking-wider text-accent-blue font-mono mt-2">New Predicted Finish</span>
              <span className={`text-4xl font-black italic drop-shadow-[0_0_10px_rgba(255,255,255,0.3)] ${simResult ? 'text-white' : 'text-zinc-700'}`}>
                {simResult ? `P${simResult.new_predicted_rank}` : "--"}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}