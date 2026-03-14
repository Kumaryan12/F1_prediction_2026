import Link from "next/link";
import MetricCard from "@/components/MetricCard";
import PodiumCard from "@/components/PodiumCard";
import PredictionTable from "@/components/PredictionTable";
import HeadToHead from "@/components/HeadToHead";
import FeatureImportanceChart from "@/components/FeatureImportanceChart";
import TelemetryTicker from "@/components/TelemetryTicker";
import Simulator from "@/components/Simulator";
import { fetchSummary, fetchTop10, fetchLatestPredictions, fetchFeatureImportance } from "@/lib/api";

export default async function HomePage() {
  const summary = await fetchSummary();
  const top10 = await fetchTop10();
  const fullGrid = await fetchLatestPredictions();
  // 1. Fetch the raw data
  const rawFeatures = await fetchFeatureImportance();

  // 2. Filter out any 'null' values so TypeScript knows it's 100% safe
  const validFeatures = rawFeatures.filter(
    (feature): feature is { name: string; value: number } => feature !== null
  );

  return (
    <div className="mx-auto max-w-7xl relative">
      
      {/* NEW: Background Track Watermark */}
      <div 
        className="absolute top-20 right-[-10%] w-[800px] h-[800px] bg-no-repeat bg-contain opacity-5 pointer-events-none z-0"
        style={{ backgroundImage: 'url(/shanghai-track.png)' }}
      />

      {/* Hero Section - The Shanghai Neon Vibe */}
      <section className="mb-12 grid gap-6 lg:grid-cols-[2fr_1fr] relative z-10">
        <div className="relative flex flex-col justify-end overflow-hidden rounded-2xl border border-white/10 bg-tarmac-light p-8 shadow-2xl min-h-[360px] group">
          {/* F1 Car/Neon City Background Image with Dark Overlay */}
          <div 
            className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1549692520-acc6669e2f0c?q=80&w=2070&auto=format&fit=crop')] bg-cover bg-center opacity-30 mix-blend-luminosity transition-transform duration-1000 group-hover:scale-105" 
          />
          {/* Aggressive Red to Tarmac Gradient */}
          <div className="absolute inset-0 bg-gradient-to-t from-tarmac via-tarmac/90 to-shanghai-red/10" />
          
          {/* Glowing Shanghai Track Minimap */}
          <div className="absolute top-8 right-8 w-64 h-64 opacity-20 pointer-events-none transition-opacity duration-700 group-hover:opacity-50">
            <svg 
              viewBox="0 0 200 200" 
              fill="none" 
              xmlns="http://www.w3.org/2000/svg" 
              className="w-full h-full text-shanghai-red drop-shadow-[0_0_15px_rgba(238,28,37,0.8)]"
            >
              {/* Stylized Shanghai International Circuit Path (Snail + Back Straight) */}
              <path 
                d="M80 150 C 110 150, 130 110, 100 80 C 70 50, 40 100, 70 120 L 110 120 L 130 170 L 180 150 L 170 30 C 150 10, 130 20, 120 40 L 80 100 L 40 100 Z" 
                stroke="currentColor" 
                strokeWidth="4" 
                strokeLinecap="round" 
                strokeLinejoin="round"
                className="animate-[dash_4s_linear_infinite]"
              />
              {/* Start/Finish Line Dot */}
              <circle cx="80" cy="148" r="6" fill="#FFD700" className="animate-pulse shadow-[0_0_15px_rgba(255,215,0,1)]" />
            </svg>
          </div>
          
          <div className="relative z-10">
            <h1 className="mb-2 max-w-3xl text-5xl font-black uppercase italic tracking-tighter text-white md:text-7xl drop-shadow-lg">
  CHINESE GRAND PRIX 2026
</h1>

            <p className="max-w-xl text-sm font-medium leading-relaxed text-zinc-300">
              AI-powered telemetry dashboard featuring podium probabilities, 
              confidence intervals, and team-level race outlook for the Chinese Grand Prix.
            </p>
          </div>
        </div>

       {/* Model Architecture Specs Column */}
        <div className="relative flex flex-col overflow-hidden rounded-2xl border border-white/10 bg-tarmac-light/90 shadow-2xl backdrop-blur-md">
          {/* Pure CSS Carbon Fiber Weave */}
          <div 
            className="absolute inset-0 opacity-[0.2] pointer-events-none mix-blend-multiply"
            style={{
              backgroundImage: `
                linear-gradient(45deg, #000 25%, transparent 25%, transparent 75%, #000 75%, #000),
                linear-gradient(45deg, #000 25%, transparent 25%, transparent 75%, #000 75%, #000)
              `,
              backgroundPosition: `0 0, 4px 4px`,
              backgroundSize: `8px 8px`
            }}
          />

          {/* Header */}
          <div className="relative z-10 border-b border-white/10 bg-black/40 px-5 py-4 flex justify-between items-center">
            <h3 className="text-xs font-bold uppercase tracking-[0.2em] text-white flex items-center gap-2">
              Model Specs
            </h3>
          </div>

          {/* Specs List */}
          <div className="relative z-10 p-5 font-mono text-[11px] sm:text-xs flex flex-col gap-3 h-full text-zinc-300">
            <div className="flex justify-between items-end border-b border-white/5 pb-1.5">
              <span className="text-zinc-500 uppercase tracking-widest">Algorithm</span>
              <span className="text-white font-bold text-right">Random Forest Reg.</span>
            </div>
            
            <div className="flex justify-between items-end border-b border-white/5 pb-1.5">
              <span className="text-zinc-500 uppercase tracking-widest">Estimators</span>
              <span className="text-telemetry font-bold drop-shadow-[0_0_5px_rgba(0,255,0,0.4)]">1200 Trees</span>
            </div>
            
            <div className="flex justify-between items-end border-b border-white/5 pb-1.5">
              <span className="text-zinc-500 uppercase tracking-widest">Features</span>
              <span className="text-white text-right">41 <span className="text-zinc-500">(39 Num / 2 Cat)</span></span>
            </div>
            
            <div className="flex justify-between items-end border-b border-white/5 pb-1.5">
              <span className="text-zinc-500 uppercase tracking-widest">OOB Score (R²)</span>
              {/* Changed from track-green to imperial-gold for the new theme */}
              <span className="text-imperial-gold font-bold drop-shadow-[0_0_5px_rgba(255,215,0,0.4)]">0.627 </span>
            </div>

            <div className="flex justify-between items-end border-b border-white/5 pb-1.5">
              <span className="text-zinc-500 uppercase tracking-widest">Mean Abs Error</span>
              <span className="text-shanghai-red font-bold">2.34 </span>
            </div>
            
            <div className="flex justify-between items-end border-b border-white/5 pb-1.5">
              <span className="text-zinc-500 uppercase tracking-widest">Min Samples/Leaf</span>
              <span className="text-white">16</span>
            </div>
            
            <div className="flex justify-between items-end pt-0.5">
              <span className="text-zinc-500 uppercase tracking-widest">RMSE</span>
              <span className="text-white text-right">3.21</span>
            </div>
          </div>
        </div>
      </section>

      {/* Podium Outlook - Stepped Layout */}
      <section className="mb-16 relative z-10">
        <div className="mb-8 flex items-center gap-4">
          <h2 className="text-2xl font-black uppercase italic tracking-tight text-white">
            Podium Outlook
          </h2>
          <div className="h-px flex-1 bg-gradient-to-r from-white/20 to-transparent" />
        </div>

        <div className="grid gap-4 md:grid-cols-3 md:items-end md:h-64">
          <div className="order-2 md:order-1 md:h-[85%]">
            <PodiumCard position={2} driver={summary.predicted_podium[1]} />
          </div>
          <div className="order-1 md:order-2 md:h-full z-10 shadow-2xl shadow-shanghai-red/20">
            <PodiumCard position={1} driver={summary.predicted_podium[0]} />
          </div>
          <div className="order-3 md:order-3 md:h-[75%]">
            <PodiumCard position={3} driver={summary.predicted_podium[2]} />
          </div>
        </div>
      </section>

      {/* Top 10 Prediction Table */}
      <section className="mb-16 relative z-10">
        <div className="mb-6 flex flex-col md:flex-row md:items-end justify-between gap-4">
          <div>
            <h2 className="text-2xl font-black uppercase italic tracking-tight text-white">
              Top 10 Predictions
            </h2>
            <p className="mt-1 text-xs font-mono text-zinc-400 uppercase tracking-widest">
              Finishing order probability view // Live Delta
            </p>
          </div>
        </div>

        <div className="rounded-xl border border-white/10 bg-tarmac-light/50 backdrop-blur-md overflow-hidden p-1 shadow-2xl shadow-black/50">
          <PredictionTable rows={top10.rows} />
        </div>
      </section>

      {/* Head-to-Head Combat Terminal - NOW USING FULL GRID */}
      <section className="mb-16 relative z-10">
        <HeadToHead predictions={fullGrid.rows} />
      </section>

      {/* The What-If Simulator */}
      <section className="mb-16 relative z-10">
        <Simulator predictions={fullGrid.rows} />
      </section>

      {/* Feature Importance Chart */}
      <section className="mb-16 relative z-10">
        <FeatureImportanceChart features={validFeatures} />
      </section>
      
    </div>
  );
}