import MetricCard from "@/components/MetricCard";
import PodiumCard from "@/components/PodiumCard";
import PredictionTable from "@/components/PredictionTable";
import HeadToHead from "@/components/HeadToHead";
import FeatureImportanceChart from "@/components/FeatureImportanceChart";
import Simulator from "@/components/Simulator";
import {
  fetchSummary,
  fetchTop10,
  fetchLatestPredictions,
  fetchFeatureImportance,
} from "@/lib/api";

export default async function HomePage() {
  const [summary, top10, fullGrid, rawFeatures] = await Promise.all([
    fetchSummary(),
    fetchTop10(),
    fetchLatestPredictions(),
    fetchFeatureImportance(),
  ]);

  const validFeatures = rawFeatures.filter(
    (feature): feature is { name: string; value: number } => feature !== null
  );

  return (
    <div className="relative mx-auto max-w-7xl">
      <div
        className="pointer-events-none absolute -right-4 top-12 z-0 select-none text-[10rem] font-black italic leading-none tracking-[-0.1em] text-hungary-ivory/[0.018] sm:text-[17rem] lg:text-[23rem]"
        aria-hidden="true"
      >
        HUN
      </div>

      <header className="relative z-10 mb-5 flex flex-wrap items-center justify-between gap-4 px-1 py-3">
        <div className="flex items-center gap-3">
          <div className="grid h-10 w-10 place-items-center rounded-xl border border-hungary-red/30 bg-hungary-red/10">
            <span className="text-sm font-black italic text-hungary-red">F1</span>
          </div>
          <div>
            <p className="text-xs font-black uppercase italic tracking-tight text-white">
              Race Intelligence
            </p>
            <p className="font-mono text-[8px] uppercase tracking-[0.22em] text-zinc-600">
              Predictive paddock system
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="rounded-lg border border-white/10 bg-white/[0.03] px-3 py-2 font-mono text-[9px] uppercase tracking-[0.18em] text-zinc-400">
            Round forecast
          </span>
          <span className="rounded-lg border border-hungary-green/25 bg-hungary-green/10 px-3 py-2 font-mono text-[9px] font-bold uppercase tracking-[0.18em] text-hungary-green">
            2026
          </span>
        </div>
      </header>

      <section className="relative z-10 mb-7 overflow-hidden rounded-[2rem] border border-white/10 bg-tarmac-light shadow-2xl shadow-black/40">
        <div className="grid min-h-[500px] lg:grid-cols-[1.45fr_0.8fr]">
          <div className="relative flex flex-col justify-between overflow-hidden p-7 sm:p-10 lg:p-12">
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_12%_15%,rgba(206,41,57,0.2),transparent_32%),radial-gradient(circle_at_85%_80%,rgba(71,112,80,0.14),transparent_35%)]" />
            <div className="hungary-grid absolute inset-0 opacity-[0.04]" />
            <div className="absolute left-0 top-0 h-full w-1 bg-gradient-to-b from-hungary-red via-hungary-ivory to-hungary-green" />

            <div className="relative z-10 flex flex-wrap items-center gap-3">
              <span className="inline-flex items-center gap-2 rounded-full border border-hungary-red/30 bg-hungary-red/10 px-3 py-1.5 font-mono text-[9px] font-bold uppercase tracking-[0.22em] text-hungary-red">
                <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-hungary-red shadow-[0_0_8px_#ce2939]" />
                Model online
              </span>
              <span className="font-mono text-[9px] uppercase tracking-[0.22em] text-zinc-500">
                Mogyoród · Hungary
              </span>
            </div>

            <div className="relative z-10 max-w-3xl py-12">
              <p className="mb-4 font-mono text-[11px] font-bold uppercase tracking-[0.38em] text-hungary-green">
                Formula 1 · Budapest 2026
              </p>
              <h1 className="max-w-3xl text-5xl font-black uppercase italic leading-[0.86] tracking-[-0.06em] text-white sm:text-7xl lg:text-[5.65rem]">
                Hungarian
                <span className="block text-hungary-red">Grand Prix</span>
              </h1>
              <p className="mt-7 max-w-xl text-sm leading-6 text-zinc-400 sm:text-base">
                Predictive race intelligence for the Hungaroring&apos;s relentless
                sequence of technical corners—where qualifying position, tyre
                temperature and clean-air pace shape the entire Sunday.
              </p>
            </div>

            <div className="relative z-10 grid max-w-2xl grid-cols-3 gap-3">
              {[
                ["4.381 KM", "Lap length"],
                ["70 LAPS", "Race distance"],
                ["14", "Corners"],
              ].map(([value, label]) => (
                <div
                  key={label}
                  className="rounded-xl border border-white/8 bg-black/20 p-3 backdrop-blur-sm"
                >
                  <p className="text-lg font-black italic text-white sm:text-2xl">{value}</p>
                  <p className="mt-1 font-mono text-[8px] uppercase tracking-[0.18em] text-zinc-500">
                    {label}
                  </p>
                </div>
              ))}
            </div>
          </div>

          <div className="relative flex min-h-[340px] items-center justify-center overflow-hidden border-t border-white/10 bg-[#0b0d0e] p-8 lg:border-l lg:border-t-0">
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(206,41,57,0.11),transparent_55%)]" />
            <div className="absolute right-6 top-6 text-right">
              <p className="font-mono text-[8px] uppercase tracking-[0.25em] text-zinc-600">
                Circuit study
              </p>
              <p className="mt-1 text-xs font-black uppercase italic text-hungary-ivory">
                Hungaroring
              </p>
            </div>

            <svg
              viewBox="0 0 340 300"
              className="relative z-10 w-full max-w-[360px] overflow-visible text-hungary-red drop-shadow-[0_0_20px_rgba(206,41,57,0.32)]"
              role="img"
              aria-label="Stylised Hungaroring circuit map"
            >
              <path
                d="M63 198 C42 186 45 160 65 149 C85 138 109 150 124 134 C138 119 119 102 132 85 C143 71 162 79 175 67 C192 51 191 30 210 26 C231 22 239 43 230 59 C221 76 198 79 201 99 C203 116 225 115 238 125 C253 136 244 153 257 165 C269 177 294 166 300 184 C306 202 288 215 270 215 C249 216 234 203 215 211 C195 219 195 242 174 249 C151 257 139 232 119 227 C95 222 80 209 63 198 Z"
                fill="none"
                stroke="rgba(255,255,255,0.075)"
                strokeWidth="15"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              <path
                d="M63 198 C42 186 45 160 65 149 C85 138 109 150 124 134 C138 119 119 102 132 85 C143 71 162 79 175 67 C192 51 191 30 210 26 C231 22 239 43 230 59 C221 76 198 79 201 99 C203 116 225 115 238 125 C253 136 244 153 257 165 C269 177 294 166 300 184 C306 202 288 215 270 215 C249 216 234 203 215 211 C195 219 195 242 174 249 C151 257 139 232 119 227 C95 222 80 209 63 198 Z"
                fill="none"
                stroke="currentColor"
                strokeWidth="4"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="circuit-path"
              />
              <circle cx="63" cy="198" r="6" fill="#477050" className="animate-pulse" />
              <path d="M52 189l17 3-3 17-17-3z" fill="none" stroke="#f4f0e8" strokeWidth="2" />
            </svg>

            <div className="absolute bottom-6 left-7">
              <p className="text-3xl font-black italic tracking-tighter text-white">34.7 M</p>
              <p className="font-mono text-[8px] uppercase tracking-[0.2em] text-zinc-600">
                Elevation change
              </p>
            </div>
            <div className="absolute bottom-6 right-7 text-right">
              <p className="text-sm font-black uppercase italic text-hungary-green">
                High downforce
              </p>
              <p className="font-mono text-[8px] uppercase tracking-[0.2em] text-zinc-600">
                Technical circuit
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="relative z-10 mb-12 grid gap-3 sm:grid-cols-3">
        {[
          ["01", "Qualifying", "Track position is critical"],
          ["02", "Tyre Load", "High lateral energy"],
          ["03", "Race Style", "Rhythm over raw speed"],
        ].map(([index, label, detail]) => (
          <div
            key={label}
            className="flex items-center gap-4 rounded-xl border border-white/8 bg-white/[0.025] p-4"
          >
            <span className="font-mono text-[10px] font-bold text-hungary-red">{index}</span>
            <div>
              <p className="text-xs font-black uppercase italic text-white">{label}</p>
              <p className="mt-1 font-mono text-[8px] uppercase tracking-[0.16em] text-zinc-600">
                {detail}
              </p>
            </div>
          </div>
        ))}
      </section>

      <section className="relative z-10 mb-14 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <MetricCard label="Predicted Winner" value={summary.predicted_winner} subtext="Highest model rank" accent="red" />
        <MetricCard label="Constructor Edge" value={summary.best_team} subtext="Strongest aggregate" accent="green" />
        <MetricCard label="Grid Model" value={`${summary.total_drivers} Cars`} subtext="Full field processed" accent="red" />
        <MetricCard label="Forecast Spread" value={`±${Number(summary.avg_pred_std).toFixed(2)}`} subtext="Mean model deviation" accent="green" />
      </section>

      <section className="relative z-10 mb-16">
        <SectionHeading index="01" title="Podium Outlook" subtitle="Most likely top-three finishers" />
        <div className="grid gap-4 md:h-64 md:grid-cols-3 md:items-end">
          <div className="order-2 h-full md:order-1 md:h-[85%]"><PodiumCard position={2} driver={summary.predicted_podium[1]} /></div>
          <div className="order-1 h-full shadow-2xl shadow-hungary-red/10 md:order-2"><PodiumCard position={1} driver={summary.predicted_podium[0]} /></div>
          <div className="order-3 h-full md:h-[76%]"><PodiumCard position={3} driver={summary.predicted_podium[2]} /></div>
        </div>
      </section>

      <section className="relative z-10 mb-16">
        <SectionHeading index="02" title="Top 10 Forecast" subtitle="Predicted finishing order · 68% confidence intervals" />
        <div className="overflow-hidden rounded-2xl border border-white/10 bg-tarmac-light/60 p-1 shadow-2xl shadow-black/50 backdrop-blur-md">
          <PredictionTable rows={top10.rows} />
        </div>
      </section>

      <section className="relative z-10 mb-16"><HeadToHead predictions={fullGrid.rows} /></section>
      <section className="relative z-10 mb-16"><Simulator predictions={fullGrid.rows} /></section>
      <section className="relative z-10 mb-16"><FeatureImportanceChart features={validFeatures} /></section>

      <footer className="relative z-10 flex flex-col gap-2 border-t border-white/10 py-8 font-mono text-[9px] uppercase tracking-[0.2em] text-zinc-600 sm:flex-row sm:items-center sm:justify-between">
        <span>F1 Race Intelligence · Hungarian GP 2026</span>
        <span>Model outputs are probabilistic, not guarantees</span>
      </footer>
    </div>
  );
}

function SectionHeading({ index, title, subtitle }: { index: string; title: string; subtitle: string }) {
  return (
    <div className="mb-7 flex items-end gap-4">
      <span className="pb-1 font-mono text-xs font-bold text-hungary-red">{index}</span>
      <div>
        <h2 className="text-2xl font-black uppercase italic tracking-tight text-white sm:text-3xl">{title}</h2>
        <p className="mt-1 font-mono text-[10px] uppercase tracking-[0.2em] text-zinc-500">{subtitle}</p>
      </div>
      <div className="mb-2 h-px flex-1 bg-gradient-to-r from-hungary-red/35 to-transparent" />
    </div>
  );
}
