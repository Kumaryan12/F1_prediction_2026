type FeatureData = {
  name: string;
  value: number;
};

type FeatureImportanceProps = {
  features: FeatureData[];
};

export default function FeatureImportanceChart({ features }: FeatureImportanceProps) {
  // Sort by importance and grab the Top 10 to keep the UI clean
  const sorted = [...features].sort((a, b) => b.value - a.value).slice(0, 10);

  return (
    <div className="relative flex flex-col overflow-hidden rounded-2xl border border-white/10 bg-tarmac-light/80 p-6 shadow-2xl backdrop-blur-md">
      {/* Background Tech Grid */}
      <div 
        className="absolute inset-0 opacity-[0.03] pointer-events-none mix-blend-screen"
        style={{
          backgroundImage: 'linear-gradient(rgba(255, 255, 255, 0.5) 1px, transparent 1px), linear-gradient(90deg, rgba(255, 255, 255, 0.5) 1px, transparent 1px)',
          backgroundSize: '20px 20px'
        }}
      />

      {/* Header */}
      <div className="mb-8 flex items-end justify-between border-b border-white/10 pb-4 relative z-10">
        <div>
          <h3 className="text-2xl font-black uppercase italic tracking-tight text-white drop-shadow-md">
            Model Diagnostics
          </h3>
          <p className="mt-1 text-xs font-mono uppercase tracking-[0.3em] text-telemetry">
            Feature Importance Weighting
          </p>
        </div>
        
        {/* Decorative Diagnostic Icon */}
        <div className="flex h-10 w-10 items-center justify-center rounded bg-telemetry/10 border border-telemetry/30 shadow-[0_0_15px_rgba(0,255,0,0.15)] animate-pulse">
          <svg className="w-5 h-5 text-telemetry" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
        </div>
      </div>

      {/* Data Rows */}
      <div className="flex flex-col gap-5 relative z-10">
        {sorted.map((item, idx) => {
          // Changed to absolute percentage (1.0 = 100%)
          const pct = item.value ? item.value * 100 : 0;
          
          // Clean up the CSV column names and handle undefined cases safely
          const label = item.name ? item.name.replace(/_/g, ' ').toUpperCase() : 'UNKNOWN';

          return (
            <div key={item.name || idx} className="group relative flex flex-col gap-2">
              <div className="flex justify-between items-end text-xs font-mono uppercase tracking-widest text-zinc-400 group-hover:text-white transition-colors duration-300">
                <span className="truncate pr-4">
                  <span className="text-white/30 mr-2">{String(idx + 1).padStart(2, '0')}</span> 
                  {label}
                </span>
                <span className="text-telemetry font-bold drop-shadow-[0_0_8px_rgba(0,255,0,0.6)]">
                  {item.value ? (item.value * 100).toFixed(1) : "0.0"}%
                </span>
              </div>
              
              {/* The Glowing Bar - Fixed Absolute Scaling */}
              <div className="h-1.5 w-full overflow-hidden rounded-r-full bg-black/60 shadow-inner">
                <div
                  className="h-full rounded-r-full bg-gradient-to-r from-[rgba(0,255,0,0.3)] to-[#00ff00] shadow-[0_0_12px_rgba(0,255,0,0.8)] transition-all duration-1000 ease-out"
                  style={{ width: `${pct}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}