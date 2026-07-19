import MetricCard from "@/components/MetricCard";
import PodiumCard from "@/components/PodiumCard";
import PredictionTable from "@/components/PredictionTable";
import HeadToHead from "@/components/HeadToHead";
import FeatureImportanceChart from "@/components/FeatureImportanceChart";
import TelemetryTicker from "@/components/TelemetryTicker";
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
        className="pointer-events-none absolute -right-5 top-4 z-0 select-none text-[11rem] font-black italic leading-none tracking-[-0.1em] text-belgian-yellow/[0.025] sm:text-[18rem] lg:text-[24rem]"
        aria-hidden="true"
      >
        SPA
      </div>

      <section className="relative z-10 mb-6 overflow-hidden rounded-[1.75rem] border border-white/10 bg-tarmac-light shadow-2xl">
        <div className="grid min-h-[470px] lg:grid-cols-[1.55fr_0.75fr]">
          <div className="relative flex flex-col justify-between overflow-hidden p-7 sm:p-10 lg:p-12">
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_78%_25%,rgba(253,218,36,0.16),transparent_34%),linear-gradient(120deg,rgba(239,51,64,0.16),transparent_45%)]" />
            <div className="absolute inset-0 opacity-[0.035] belgian-grid" />

            <div className="relative z-10 flex flex-wrap items-center gap-3">
              <span className="inline-flex items-center gap-2 rounded-full border border-belgian-yellow/30 bg-belgian-yellow/10 px-3 py-1.5 font-mono text-[10px] font-bold uppercase tracking-[0.22em] text-belgian-yellow">
                <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-belgian-yellow shadow-[0_0_8px_#fdda24]" />
                Race intelligence live
              </span>
              <span className="font-mono text-[10px] uppercase tracking-[0.2em] text-zinc-500">
                Spa-Francorchamps · Belgium
              </span>
            </div>

            <div className="relative z-10 max-w-3xl py-12">
              <p className="mb-4 font-mono text-xs font-bold uppercase tracking-[0.36em] text-belgian-red">
                Formula 1 · 2026
              </p>
              <h1 className="max-w-3xl text-5xl font-black uppercase italic leading-[0.88] tracking-[-0.055em] text-white sm:text-7xl lg:text-[5.75rem]">
                Belgian
                <span className="block text-belgian-yellow">Grand Prix</span>
              </h1>
              <p className="mt-6 max-w-xl text-sm leading-6 text-zinc-400 sm:text-base">
                Machine-learning race forecasts built for the longest lap on the
                calendar—where elevation, slipstream and Ardennes weather can
                rewrite the order in a single sector.
              </p>
            </div>

            <div className="relative z-10 grid max-w-2xl grid-cols-3 gap-3 border-t border-white/10 pt-5">
              {[
                ["7.004 KM", "Lap length"],
                ["44 LAPS", "Race distance"],
                ["19", "Corners"],
              ].map(([value, label]) => (
                <div key={label}>
                  <p className="text-lg font-black italic text-white sm:text-2xl">{value}</p>
                  <p className="mt-1 font-mono text-[9px] uppercase tracking-[0.18em] text-zinc-500">
                    {label}
                  </p>
                </div>
              ))}
            </div>
          </div>

          <div className="relative flex min-h-[320px] items-center justify-center overflow-hidden border-t border-white/10 bg-black/25 p-8 lg:border-l lg:border-t-0">
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(253,218,36,0.09),transparent_58%)]" />
            <div className="absolute right-5 top-5 font-mono text-[9px] uppercase tracking-[0.24em] text-zinc-600">
              Circuit de Spa-Francorchamps
            </div>
            <svg
              viewBox="0 0 340 300"
              className="relative z-10 w-full max-w-[360px] overflow-visible text-belgian-yellow drop-shadow-[0_0_18px_rgba(253,218,36,0.3)]"
              role="img"
              aria-label="Stylised Spa-Francorchamps circuit map"
            >
              <path
                d="M82 241 C57 228 49 201 64 181 C75 166 94 170 103 151 C111 134 103 114 116 99 C130 83 148 87 162 69 C178 48 187 21 208 25 C226 29 218 55 231 67 C245 80 271 68 286 84 C301 100 285 119 264 129 C245 138 231 149 231 169 C232 191 256 199 247 221 C239 241 217 239 199 229 C179 218 161 211 144 226 C126 243 105 253 82 241 Z"
                fill="none"
                stroke="rgba(255,255,255,0.08)"
                strokeWidth="14"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              <path
                d="M82 241 C57 228 49 201 64 181 C75 166 94 170 103 151 C111 134 103 114 116 99 C130 83 148 87 162 69 C178 48 187 21 208 25 C226 29 218 55 231 67 C245 80 271 68 286 84 C301 100 285 119 264 129 C245 138 231 149 231 169 C232 191 256 199 247 221 C239 241 217 239 199 229 C179 218 161 211 144 226 C126 243 105 253 82 241 Z"
                fill="none"
                stroke="currentColor"
                strokeWidth="4"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="circuit-path"
              />
              <circle cx="82" cy="241" r="6" fill="#ef3340" className="animate-pulse" />
              <path d="M72 231l16 4-4 16-16-4z" fill="none" stroke="#fff" strokeWidth="2" />
            </svg>
            <div className="absolute bottom-6 left-7">
              <p className="text-3xl font-black italic tracking-tighter text-white">102.2 M</p>
              <p className="font-mono text-[9px] uppercase tracking-[0.2em] text-zinc-500">
                Elevation change
              </p>
            </div>
            <div className="absolute bottom-6 right-7 text-right">
              <p className="text-sm font-black uppercase italic text-belgian-red">Eau Rouge</p>
              <p className="font-mono text-[9px] uppercase tracking-[0.2em] text-zinc-500">
                Sector one
              </p>
            </div>
          </div>
        </div>
      </section>

      <div className="relative z-10 mb-10 overflow-hidden rounded-xl border border-white/10">
        <TelemetryTicker rows={fullGrid.rows} />
      </div>

      <section className="relative z-10 mb-14 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <MetricCard
          label="Predicted Winner"
          value={summary.predicted_winner}
          subtext="Highest model rank"
          accent="yellow"
        />
        <MetricCard
          label="Constructor Edge"
          value={summary.best_team}
          subtext="Strongest aggregate"
          accent="red"
        />
        <MetricCard
          label="Grid Model"
          value={`${summary.total_drivers} Cars`}
          subtext="Full field processed"
          accent="yellow"
        />
        <MetricCard
          label="Forecast Spread"
          value={`±${Number(summary.avg_pred_std).toFixed(2)}`}
          subtext="Mean model deviation"
          accent="red"
        />
      </section>

      <section className="relative z-10 mb-16">
        <SectionHeading
          index="01"
          title="Podium Outlook"
          subtitle="Most likely top-three finishers"
        />
        <div className="grid gap-4 md:h-64 md:grid-cols-3 md:items-end">
          <div className="order-2 h-full md:order-1 md:h-[85%]">
            <PodiumCard position={2} driver={summary.predicted_podium[1]} />
          </div>
          <div className="order-1 h-full shadow-2xl shadow-belgian-yellow/10 md:order-2">
            <PodiumCard position={1} driver={summary.predicted_podium[0]} />
          </div>
          <div className="order-3 h-full md:h-[76%]">
            <PodiumCard position={3} driver={summary.predicted_podium[2]} />
          </div>
        </div>
      </section>

      <section className="relative z-10 mb-16">
        <SectionHeading
          index="02"
          title="Top 10 Forecast"
          subtitle="Predicted finishing order · 68% confidence intervals"
        />
        <div className="overflow-hidden rounded-2xl border border-white/10 bg-tarmac-light/60 p-1 shadow-2xl shadow-black/50 backdrop-blur-md">
          <PredictionTable rows={top10.rows} />
        </div>
      </section>

      <section className="relative z-10 mb-16">
        <HeadToHead predictions={fullGrid.rows} />
      </section>

      <section className="relative z-10 mb-16">
        <Simulator predictions={fullGrid.rows} />
      </section>

      <section className="relative z-10 mb-16">
        <FeatureImportanceChart features={validFeatures} />
      </section>

      <footer className="relative z-10 flex flex-col gap-2 border-t border-white/10 py-8 font-mono text-[9px] uppercase tracking-[0.2em] text-zinc-600 sm:flex-row sm:items-center sm:justify-between">
        <span>F1 Race Intelligence · Belgian GP 2026</span>
        <span>Model outputs are probabilistic, not guarantees</span>
      </footer>
    </div>
  );
}

function SectionHeading({
  index,
  title,
  subtitle,
}: {
  index: string;
  title: string;
  subtitle: string;
}) {
  return (
    <div className="mb-7 flex items-end gap-4">
      <span className="pb-1 font-mono text-xs font-bold text-belgian-red">{index}</span>
      <div>
        <h2 className="text-2xl font-black uppercase italic tracking-tight text-white sm:text-3xl">
          {title}
        </h2>
        <p className="mt-1 font-mono text-[10px] uppercase tracking-[0.2em] text-zinc-500">
          {subtitle}
        </p>
      </div>
      <div className="mb-2 h-px flex-1 bg-gradient-to-r from-belgian-yellow/35 to-transparent" />
    </div>
  );
}
