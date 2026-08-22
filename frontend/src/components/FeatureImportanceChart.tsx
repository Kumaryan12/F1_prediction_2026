type FeatureData = { name: string; value: number };

export default function FeatureImportanceChart({ features }: { features: FeatureData[] }) {
  const sorted = [...features].sort((a, b) => b.value - a.value).slice(0, 10);
  const max = Math.max(...sorted.map((item) => item.value), 0.01);
  return (
    <div className="border border-white/10 bg-[#111315]">
      <header className="flex flex-col gap-2 border-b border-white/10 p-5 sm:flex-row sm:items-end sm:justify-between"><div><p className="font-mono text-[8px] font-bold uppercase tracking-[0.22em] text-dutch-orange">Model diagnostics</p><h2 className="mt-1 text-2xl font-black uppercase italic tracking-[-0.04em] text-white">Feature importance</h2></div><span className="font-mono text-[8px] uppercase tracking-[0.16em] text-zinc-600">Relative decision weight</span></header>
      <div className="grid gap-x-10 gap-y-5 p-5 sm:p-7 lg:grid-cols-2">
        {sorted.map((item, idx) => {
          const label = item.name?.replace(/_/g, " ").toUpperCase() || "UNKNOWN";
          return <div key={item.name || idx}><div className="mb-2 flex items-end justify-between gap-4 font-mono text-[9px] uppercase tracking-[0.12em]"><span className="truncate text-zinc-400"><b className="mr-2 text-zinc-700">{String(idx + 1).padStart(2, "0")}</b>{label}</span><strong className="text-dutch-orange">{(item.value * 100).toFixed(1)}%</strong></div><div className="h-1.5 bg-black"><div className="h-full bg-dutch-orange" style={{ width: `${(item.value / max) * 100}%` }} /></div></div>;
        })}
      </div>
    </div>
  );
}
