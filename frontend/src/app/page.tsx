import MetricCard from "@/components/MetricCard";
import PodiumCard from "@/components/PodiumCard";
import PredictionTable from "@/components/PredictionTable";
import HeadToHead from "@/components/HeadToHead";
import FeatureImportanceChart from "@/components/FeatureImportanceChart";
import Simulator from "@/components/Simulator";
import { fetchSummary, fetchTop10, fetchLatestPredictions, fetchFeatureImportance } from "@/lib/api";

const navItems = ["Overview", "Forecast", "H2H", "Simulator", "Model"];

export default async function HomePage() {
  const [summary, top10, fullGrid, rawFeatures] = await Promise.all([
    fetchSummary(), fetchTop10(), fetchLatestPredictions(), fetchFeatureImportance(),
  ]);
  const validFeatures = rawFeatures.filter(
    (feature): feature is { name: string; value: number } => feature !== null
  );

  return (
    <div className="relative">
      <header className="mb-4 flex min-h-14 items-center justify-between border-b border-white/10 bg-tarmac px-1 pb-4">
        <div className="flex items-center gap-4">
          <div className="flex h-9 w-14 items-center justify-center bg-dutch-orange text-lg font-black italic tracking-[-0.08em] text-black">F1</div>
          <div>
            <p className="text-sm font-black uppercase tracking-[-0.02em] text-white">Race Intelligence</p>
            <p className="font-mono text-[8px] uppercase tracking-[0.24em] text-zinc-500">Dutch GP · 2026</p>
          </div>
        </div>
        <nav className="hidden items-center gap-7 lg:flex" aria-label="Dashboard sections">
          {navItems.map((item, index) => (
            <a key={item} href={`#${item.toLowerCase()}`} className={`font-mono text-[9px] font-bold uppercase tracking-[0.2em] transition-colors hover:text-white ${index === 0 ? "text-dutch-orange" : "text-zinc-500"}`}>
              {item}
            </a>
          ))}
        </nav>
        <div className="flex items-center gap-2 border border-white/10 px-3 py-2 font-mono text-[9px] uppercase tracking-[0.16em] text-zinc-300">
          <span className="h-2 w-2 bg-[#31c46c]" /> Model ready
        </div>
      </header>

      <section id="overview" className="mb-4 grid border border-white/10 bg-[#111315] lg:grid-cols-[minmax(0,1.5fr)_minmax(360px,.75fr)]">
        <div className="relative min-h-[430px] overflow-hidden p-6 sm:p-9 lg:p-11">
          <div className="absolute right-5 top-2 select-none text-[9rem] font-black leading-none tracking-[-0.12em] text-white/[0.025] sm:text-[13rem]">NL</div>
          <div className="relative flex h-full flex-col justify-between">
            <div className="flex flex-wrap items-center gap-x-5 gap-y-2 font-mono text-[9px] uppercase tracking-[0.22em]">
              <span className="bg-dutch-orange px-2.5 py-1.5 font-bold text-black">Round 12</span>
              <span className="text-zinc-500">Zandvoort · Netherlands</span>
              <span className="text-zinc-500">21–23 August 2026</span>
            </div>
            <div className="py-10">
              <p className="mb-3 font-mono text-[10px] font-bold uppercase tracking-[0.38em] text-dutch-orange">Race forecast / Circuit Zandvoort</p>
              <h1 className="max-w-4xl text-5xl font-black uppercase italic leading-[0.84] tracking-[-0.065em] text-dutch-cream sm:text-7xl lg:text-[6.4rem]">Dutch<br />Grand Prix</h1>
              <p className="mt-7 max-w-2xl border-l-2 border-dutch-orange pl-4 text-sm leading-6 text-zinc-400 sm:text-base">A narrow, banked sprint through the dunes. Grid position matters, but tyre load through Scheivlak and the final corner will decide who can attack.</p>
            </div>
            <div className="grid max-w-3xl grid-cols-2 border-y border-white/10 sm:grid-cols-4">
              <TrackStat value="4.259" unit="km" label="Lap length" />
              <TrackStat value="72" unit="laps" label="Race distance" />
              <TrackStat value="14" unit="turns" label="Circuit layout" />
              <TrackStat value="18" unit="deg" label="Max banking" />
            </div>
          </div>
        </div>

        <div className="relative flex min-h-[360px] flex-col justify-between border-t border-white/10 bg-dutch-cream p-7 text-[#111315] lg:border-l lg:border-t-0">
          <div className="flex items-start justify-between">
            <div>
              <p className="font-mono text-[8px] font-bold uppercase tracking-[0.24em] text-[#6c685f]">Circuit profile</p>
              <h2 className="mt-1 text-2xl font-black uppercase italic tracking-[-0.04em]">Zandvoort</h2>
            </div>
            <span className="border border-[#111315] px-2 py-1 font-mono text-[8px] font-bold uppercase tracking-[0.18em]">High downforce</span>
          </div>
          <svg viewBox="0 0 390 260" className="mx-auto w-full max-w-[430px]" role="img" aria-label="Stylised Circuit Zandvoort map">
            <path d="M76 191 C52 181 43 155 58 133 C69 117 91 120 101 104 C111 88 95 70 107 53 C120 36 148 35 163 50 C178 65 161 86 174 100 C188 115 212 97 232 104 C252 111 254 133 271 143 C289 154 311 139 326 153 C343 169 334 197 312 204 C290 212 271 196 250 203 C225 211 218 232 192 231 C164 230 154 207 132 201 C111 196 94 199 76 191 Z" fill="none" stroke="#c8c1b3" strokeWidth="20" strokeLinecap="square" strokeLinejoin="round" />
            <path d="M76 191 C52 181 43 155 58 133 C69 117 91 120 101 104 C111 88 95 70 107 53 C120 36 148 35 163 50 C178 65 161 86 174 100 C188 115 212 97 232 104 C252 111 254 133 271 143 C289 154 311 139 326 153 C343 169 334 197 312 204 C290 212 271 196 250 203 C225 211 218 232 192 231 C164 230 154 207 132 201 C111 196 94 199 76 191 Z" fill="none" stroke="#111315" strokeWidth="5" strokeLinecap="square" strokeLinejoin="round" />
            <path d="M67 184l18 4-4 18-18-4z" fill="#ff5f00" />
            <circle cx="76" cy="191" r="4" fill="#111315" />
          </svg>
          <div className="grid grid-cols-3 border-t border-[#111315]/20 pt-4 font-mono text-[8px] uppercase tracking-[0.14em] text-[#6c685f]">
            <div><strong className="mb-1 block text-sm text-[#111315]">2</strong>DRS zones</div>
            <div><strong className="mb-1 block text-sm text-[#111315]">Clockwise</strong>Direction</div>
            <div><strong className="mb-1 block text-sm text-dutch-red">Dunes</strong>Surface risk</div>
          </div>
        </div>
      </section>

      <section className="mb-10 grid border-x border-b border-white/10 sm:grid-cols-3">
        <Insight index="01" label="Track position" detail="Overtaking window is narrow" />
        <Insight index="02" label="Tyre energy" detail="Sustained lateral loading" />
        <Insight index="03" label="Race variable" detail="Coastal wind and sand" />
      </section>

      <section className="mb-12 grid gap-px border border-white/10 bg-white/10 sm:grid-cols-2 lg:grid-cols-4">
        <MetricCard label="Predicted Winner" value={summary.predicted_winner} subtext="Highest model rank" accent="red" />
        <MetricCard label="Constructor Edge" value={summary.best_team} subtext="Best aggregate pace" accent="green" />
        <MetricCard label="Cars Modelled" value={`${summary.total_drivers}`} subtext="Full grid processed" accent="yellow" />
        <MetricCard label="Forecast Spread" value={`±${Number(summary.avg_pred_std).toFixed(2)}`} subtext="Mean deviation" accent="telemetry" />
      </section>

      <section id="forecast" className="mb-14">
        <SectionHeading index="01" title="Podium Outlook" subtitle="Highest probability top-three finishers" />
        <div className="grid gap-px border border-white/10 bg-white/10 md:grid-cols-3">
          <PodiumCard position={1} driver={summary.predicted_podium[0]} />
          <PodiumCard position={2} driver={summary.predicted_podium[1]} />
          <PodiumCard position={3} driver={summary.predicted_podium[2]} />
        </div>
      </section>

      <section className="mb-14">
        <SectionHeading index="02" title="Top 10 Forecast" subtitle="Predicted order · 68% confidence interval" />
        <div className="overflow-hidden border border-white/10 bg-[#111315]"><PredictionTable rows={top10.rows} /></div>
      </section>

      <section id="h2h" className="mb-14"><HeadToHead predictions={fullGrid.rows} /></section>
      <section id="simulator" className="mb-14"><Simulator predictions={fullGrid.rows} /></section>
      <section id="model" className="mb-14"><FeatureImportanceChart features={validFeatures} /></section>

      <footer className="flex flex-col gap-2 border-t border-white/10 py-7 font-mono text-[8px] uppercase tracking-[0.2em] text-zinc-600 sm:flex-row sm:items-center sm:justify-between">
        <span>Race Intelligence / Dutch GP 2026 / Zandvoort</span><span>Probabilistic forecast · not a guarantee of result</span>
      </footer>
    </div>
  );
}

function TrackStat({ value, unit, label }: { value: string; unit: string; label: string }) {
  return <div className="border-r border-white/10 px-3 py-3 last:border-r-0"><p className="text-2xl font-black italic tracking-[-0.04em] text-white">{value} <span className="text-xs text-dutch-orange">{unit}</span></p><p className="mt-1 font-mono text-[8px] uppercase tracking-[0.16em] text-zinc-600">{label}</p></div>;
}

function Insight({ index, label, detail }: { index: string; label: string; detail: string }) {
  return <div className="flex items-center gap-4 border-r border-white/10 bg-[#111315] px-5 py-4 last:border-r-0"><span className="font-mono text-[9px] font-bold text-dutch-orange">{index}</span><div><p className="text-xs font-black uppercase italic text-white">{label}</p><p className="mt-1 font-mono text-[8px] uppercase tracking-[0.13em] text-zinc-600">{detail}</p></div></div>;
}

function SectionHeading({ index, title, subtitle }: { index: string; title: string; subtitle: string }) {
  return <div className="mb-5 flex items-end gap-4 border-b border-white/10 pb-4"><span className="bg-dutch-orange px-2 py-1 font-mono text-[9px] font-bold text-black">{index}</span><div><h2 className="text-2xl font-black uppercase italic tracking-[-0.035em] text-white sm:text-3xl">{title}</h2><p className="mt-1 font-mono text-[8px] uppercase tracking-[0.2em] text-zinc-500">{subtitle}</p></div></div>;
}
