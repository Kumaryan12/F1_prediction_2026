"use client";

import { useState } from "react";

// Updated to match your EXACT Python JSON output
type DriverData = {
  driver: string;
  team: string;
  pred_rank?: number;
  pred_finish?: number;
  grid_pos?: number;
  // Fallbacks in case your API uses slightly different names
  predicted_pos?: number; 
  position?: number;
  grid?: number;
  win_prob?: number;
  probability?: number;
};

type HeadToHeadProps = {
  predictions: DriverData[];
};

export default function HeadToHead({ predictions }: HeadToHeadProps) {
  // Set default rivals (e.g., top 2 predicted drivers)
  const [driverA, setDriverA] = useState(predictions[0]?.driver || "VER");
  const [driverB, setDriverB] = useState(predictions[1]?.driver || "NOR");

  const dataA = predictions.find((p) => p.driver === driverA) || predictions[0];
  const dataB = predictions.find((p) => p.driver === driverB) || predictions[1];

  // EXACT JSON KEYS MAPPED HERE:
  const getPos = (d: any) => d.pred_rank || Math.round(d.pred_finish) || d.predicted_pos || d.position || 0;
  const getGrid = (d: any) => d.grid_pos || d.grid || 0;
  const getProb = (d: any) => d.win_prob || d.probability || 0;

  // Calculate the "Clash Bar" width based on predicted position
  // Lower position = better. We invert it for the progress bar weight.
  const weightA = Math.max(20 - getPos(dataA), 1);
  const weightB = Math.max(20 - getPos(dataB), 1);
  const totalWeight = weightA + weightB;
  const pctA = (totalWeight > 0) ? (weightA / totalWeight) * 100 : 50; // Added a safe fallback

  return (
    <div className="relative overflow-hidden rounded-2xl border border-white/10 bg-tarmac-light/90 shadow-2xl backdrop-blur-md p-6 sm:p-8">
      {/* Background Styling - Sakura Pink vs Suzuka Red */}
      <div className="absolute top-0 left-0 w-1/2 h-full bg-gradient-to-r from-sakura-pink/10 to-transparent pointer-events-none" />
      <div className="absolute top-0 right-0 w-1/2 h-full bg-gradient-to-l from-suzuka-red/10 to-transparent pointer-events-none" />

      {/* Header */}
      <div className="mb-8 text-center relative z-10">
        <h2 className="text-2xl font-black uppercase italic tracking-tight text-white flex items-center justify-center gap-3">
          <svg className="w-6 h-6 text-zinc-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
          H2H Combat Terminal
          <svg className="w-6 h-6 text-zinc-400 transform scale-x-[-1]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
        </h2>
        <p className="mt-1 text-xs font-mono text-zinc-400 uppercase tracking-widest">
          Machine Learning Matchup Analysis
        </p>
      </div>

      {/* Driver Selection & Stats */}
      <div className="flex flex-col md:flex-row items-center justify-between gap-6 relative z-10">
        
        {/* Driver A Side - Sakura Pink Focus */}
        <div className="w-full md:w-5/12 flex flex-col items-center md:items-start text-center md:text-left">
          <select 
            className="mb-4 w-full max-w-[200px] rounded border border-sakura-pink/30 bg-black/50 px-3 py-2 text-xl font-black italic uppercase text-white outline-none focus:border-sakura-pink focus:ring-1 focus:ring-sakura-pink transition-colors"
            value={driverA}
            onChange={(e) => setDriverA(e.target.value)}
          >
            {predictions.map((p) => (
              <option key={`A-${p.driver}`} value={p.driver}>{p.driver} - {p.team}</option>
            ))}
          </select>
          <div className="space-y-2 w-full max-w-[200px]">
            <div className="flex justify-between border-b border-white/10 pb-1 font-mono text-sm">
              <span className="text-zinc-500 uppercase">Pred. Finish</span>
              <span className="text-white font-bold text-lg">P{getPos(dataA)}</span>
            </div>
            <div className="flex justify-between border-b border-white/10 pb-1 font-mono text-sm">
              <span className="text-zinc-500 uppercase">Grid Pos</span>
              <span className="text-white font-bold">P{getGrid(dataA)}</span>
            </div>
          </div>
        </div>

        {/* The VS Clash Graphic */}
        <div className="w-full md:w-2/12 flex flex-col items-center justify-center">
          <div className="text-3xl font-black italic text-zinc-600 mb-2 drop-shadow-md">VS</div>
        </div>

        {/* Driver B Side - Suzuka Red Focus */}
        <div className="w-full md:w-5/12 flex flex-col items-center md:items-end text-center md:text-right">
          <select 
            className="mb-4 w-full max-w-[200px] rounded border border-suzuka-red/30 bg-black/50 px-3 py-2 text-xl font-black italic uppercase text-white outline-none focus:border-suzuka-red focus:ring-1 focus:ring-suzuka-red transition-colors"
            value={driverB}
            onChange={(e) => setDriverB(e.target.value)}
          >
            {predictions.map((p) => (
              <option key={`B-${p.driver}`} value={p.driver}>{p.driver} - {p.team}</option>
            ))}
          </select>
          <div className="space-y-2 w-full max-w-[200px]">
            <div className="flex justify-between border-b border-white/10 pb-1 font-mono text-sm flex-row-reverse">
              <span className="text-zinc-500 uppercase">Pred. Finish</span>
              <span className="text-white font-bold text-lg">P{getPos(dataB)}</span>
            </div>
            <div className="flex justify-between border-b border-white/10 pb-1 font-mono text-sm flex-row-reverse">
              <span className="text-zinc-500 uppercase">Grid Pos</span>
              <span className="text-white font-bold">P{getGrid(dataB)}</span>
            </div>
          </div>
        </div>
      </div>

      {/* The Advantage Power Bar */}
      <div className="mt-8 relative z-10">
        <div className="flex justify-between text-[10px] font-mono uppercase text-zinc-500 mb-2 tracking-widest">
          <span className="text-sakura-pink/80">{driverA} Advantage</span>
          <span className="text-suzuka-red/80">{driverB} Advantage</span>
        </div>
        <div className="h-3 w-full rounded-full bg-black/60 shadow-inner flex overflow-hidden border border-white/5">
          <div 
            className="h-full bg-sakura-pink shadow-[0_0_12px_rgba(255,20,147,0.9)] transition-all duration-700 ease-out"
            style={{ width: `${pctA}%` }}
          />
          <div 
            className="h-full bg-suzuka-red shadow-[0_0_12px_rgba(225,6,0,0.9)] transition-all duration-700 ease-out flex-1"
          />
        </div>
      </div>
    </div>
  );
}