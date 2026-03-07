import Link from "next/link";
import MetricCard from "@/components/MetricCard";
import PodiumCard from "@/components/PodiumCard";
import PredictionTable from "@/components/PredictionTable";
import FeatureImportanceChart from "@/components/FeatureImportanceChart";
import TelemetryTicker from "@/components/TelemetryTicker"; // <-- NEW Import
import { fetchSummary, fetchTop10, fetchFeatureImportance } from "@/lib/api";

export default async function HomePage() {
  const summary = await fetchSummary();
  const top10 = await fetchTop10();
  const features = await fetchFeatureImportance();

  return (
    <div className="mx-auto max-w-7xl relative">
      
      

      

      {/* Hero Section - The Melbourne Vibe */}
      <section className="mb-12 grid gap-6 lg:grid-cols-[2fr_1fr]">
        <div className="relative flex flex-col justify-end overflow-hidden rounded-2xl border border-white/10 bg-tarmac-light p-8 shadow-2xl min-h-[360px] group">
          {/* F1 Car Background Image with Dark Overlay */}
          <div 
            className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1532983330102-12502f9c46ce?q=80&w=2070&auto=format&fit=crop')] bg-cover bg-center opacity-40 mix-blend-luminosity transition-transform duration-1000 group-hover:scale-105" 
          />
          <div className="absolute inset-0 bg-gradient-to-t from-tarmac via-tarmac/80 to-transparent" />
          
          {/* Glowing Albert Park Track Minimap */}
          <div className="absolute top-8 right-8 w-64 h-64 opacity-20 pointer-events-none transition-opacity duration-700 group-hover:opacity-40">
            <svg 
              viewBox="0 0 200 200" 
              fill="none" 
              xmlns="http://www.w3.org/2000/svg" 
              className="w-full h-full text-white drop-shadow-[0_0_15px_rgba(255,255,255,0.6)]"
            >
              {/* Stylized Albert Park Circuit Path */}
              <path 
                d="M45 150 L65 148 L80 120 L95 125 L115 135 L145 120 L160 85 L140 45 L105 35 L75 40 L50 65 L40 100 Z" 
                stroke="currentColor" 
                strokeWidth="4" 
                strokeLinecap="round" 
                strokeLinejoin="round"
                className="animate-[dash_3s_linear_infinite]"
              />
              {/* Start/Finish Line Dot */}
              <circle cx="55" cy="149" r="6" fill="#e10600" className="animate-pulse shadow-[0_0_10px_rgba(225,6,0,1)]" />
            </svg>
          </div>
          
          <div className="relative z-10">
            

            <h1 className="mb-2 max-w-3xl text-5xl font-black uppercase italic tracking-tighter text-white md:text-7xl drop-shadow-lg">
              {summary.race}
            </h1>

            

            <div className="mt-6 flex flex-wrap gap-4">
              
            </div>
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
              <svg className="w-4 h-4 text-accent-blue" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              Model Specs
            </h3>
            <span className="flex h-2 w-2 rounded-full bg-accent-blue animate-pulse shadow-[0_0_8px_rgba(0,160,214,0.8)]" />
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
            
            {/* NEW: OOB Accuracy Score */}
            <div className="flex justify-between items-end border-b border-white/5 pb-1.5">
              <span className="text-zinc-500 uppercase tracking-widest">OOB Score (R²)</span>
              <span className="text-track-green font-bold drop-shadow-[0_0_5px_rgba(0,165,81,0.4)]">0.624</span>
            </div>

            {/* NEW: Error Metric */}
            <div className="flex justify-between items-end border-b border-white/5 pb-1.5">
              <span className="text-zinc-500 uppercase tracking-widest">Mean Abs Error</span>
              <span className="text-f1-red font-bold">± 2.36 Pos</span>
            </div>
            
            <div className="flex justify-between items-end border-b border-white/5 pb-1.5">
              <span className="text-zinc-500 uppercase tracking-widest">Min Samples/Leaf</span>
              <span className="text-white">16</span>
            </div>
            
            <div className="flex justify-between items-end pt-0.5">
              <span className="text-zinc-500 uppercase tracking-widest">RMSE</span>
              <span className="text-white text-right"> 3.22</span>
            </div>
          </div>
        </div>
      </section>

      {/* Podium Outlook - Stepped Layout */}
      <section className="mb-16">
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
          <div className="order-1 md:order-2 md:h-full z-10 shadow-2xl shadow-f1-red/10">
            <PodiumCard position={1} driver={summary.predicted_podium[0]} />
          </div>
          <div className="order-3 md:order-3 md:h-[75%]">
            <PodiumCard position={3} driver={summary.predicted_podium[2]} />
          </div>
        </div>
      </section>

      {/* Top 10 Prediction Table */}
      <section className="mb-16">
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

        <div className="rounded-xl border border-white/10 bg-tarmac-light/50 backdrop-blur-md overflow-hidden p-1">
          <PredictionTable rows={top10.rows} />
        </div>
      </section>

      {/* Feature Importance Diagnostics */}
      <section className="mb-16">
        <FeatureImportanceChart features={features} />
      </section>
      
    </div>
  );
}