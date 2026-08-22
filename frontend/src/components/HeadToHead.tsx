"use client";

import { useState } from "react";

type DriverData = { driver: string; team: string; pred_rank?: number; pred_finish?: number; grid_pos?: number; predicted_pos?: number; position?: number; grid?: number };
type HeadToHeadProps = { predictions: DriverData[] };

export default function HeadToHead({ predictions }: HeadToHeadProps) {
  const [driverA, setDriverA] = useState(predictions[0]?.driver || "VER");
  const [driverB, setDriverB] = useState(predictions[1]?.driver || "NOR");
  const dataA = predictions.find((p) => p.driver === driverA) || predictions[0];
  const dataB = predictions.find((p) => p.driver === driverB) || predictions[1];
  const getPos = (d: DriverData) => d.pred_rank || (typeof d.pred_finish === "number" ? Math.round(d.pred_finish) : 0) || d.predicted_pos || d.position || 0;
  const getGrid = (d: DriverData) => d.grid_pos || d.grid || 0;
  const weightA = Math.max(20 - getPos(dataA), 1);
  const weightB = Math.max(20 - getPos(dataB), 1);
  const pctA = (weightA / (weightA + weightB)) * 100;

  return (
    <div className="border border-white/10 bg-[#111315]">
      <header className="flex flex-col gap-2 border-b border-white/10 p-5 sm:flex-row sm:items-end sm:justify-between">
        <div><p className="font-mono text-[8px] font-bold uppercase tracking-[0.22em] text-dutch-orange">Driver comparison</p><h2 className="mt-1 text-2xl font-black uppercase italic tracking-[-0.04em] text-white">Head to head</h2></div>
        <p className="font-mono text-[8px] uppercase tracking-[0.16em] text-zinc-600">Relative predicted race advantage</p>
      </header>
      <div className="grid md:grid-cols-[1fr_100px_1fr]">
        <DriverPanel side="A" driver={driverA} data={dataA} predictions={predictions} getPos={getPos} getGrid={getGrid} onChange={setDriverA} />
        <div className="grid place-items-center border-y border-white/10 bg-tarmac py-5 text-2xl font-black italic text-zinc-700 md:border-x md:border-y-0">VS</div>
        <DriverPanel side="B" driver={driverB} data={dataB} predictions={predictions} getPos={getPos} getGrid={getGrid} onChange={setDriverB} />
      </div>
      <div className="border-t border-white/10 p-5">
        <div className="mb-2 flex justify-between font-mono text-[8px] font-bold uppercase tracking-[0.16em]"><span className="text-dutch-orange">{driverA} advantage</span><span className="text-dutch-blue">{driverB} advantage</span></div>
        <div className="flex h-2 bg-black"><div className="bg-dutch-orange transition-[width] duration-500" style={{ width: `${pctA}%` }} /><div className="flex-1 bg-dutch-blue" /></div>
      </div>
    </div>
  );
}

function DriverPanel({ side, driver, data, predictions, getPos, getGrid, onChange }: { side: string; driver: string; data: DriverData; predictions: DriverData[]; getPos: (d: DriverData) => number; getGrid: (d: DriverData) => number; onChange: (value: string) => void }) {
  return <div className="p-5 sm:p-7"><span className="font-mono text-[8px] text-zinc-600">DRIVER {side}</span><select className="mt-3 w-full border border-white/15 bg-tarmac px-3 py-3 text-lg font-black uppercase italic text-white outline-none focus:border-dutch-orange" value={driver} onChange={(e) => onChange(e.target.value)}>{predictions.map((p) => <option key={`${side}-${p.driver}`} value={p.driver}>{p.driver} · {p.team}</option>)}</select><div className="mt-6 grid grid-cols-2 gap-px bg-white/10"><Stat label="Grid" value={`P${getGrid(data)}`} /><Stat label="Forecast" value={`P${getPos(data)}`} /></div></div>;
}

function Stat({ label, value }: { label: string; value: string }) {
  return <div className="bg-tarmac p-4"><p className="font-mono text-[8px] uppercase tracking-[0.16em] text-zinc-600">{label}</p><p className="mt-1 text-3xl font-black italic text-white">{value}</p></div>;
}
