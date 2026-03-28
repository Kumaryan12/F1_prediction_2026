type MetricCardProps = {
  label: string;
  value: string;
  subtext?: string;
  // Upgraded the types to include pink
  accent?: "red" | "green" | "pink" | "telemetry";
};

// Map our custom Suzuka theme colors to the border and text highlights
const accentMap = {
  red: {
    border: "border-l-suzuka-red",
    text: "text-suzuka-red",
    glow: "shadow-[0_0_20px_rgba(225,6,0,0.1)]",
    dot: "bg-suzuka-red shadow-[0_0_5px_rgba(225,6,0,0.8)]",
  },
  // Safely map any old "green" props directly to the new Sakura Pink theme
  green: {
    border: "border-l-sakura-pink",
    text: "text-sakura-pink",
    glow: "shadow-[0_0_20px_rgba(255,20,147,0.1)]",
    dot: "bg-sakura-pink shadow-[0_0_5px_rgba(255,20,147,0.8)]",
  },
  pink: {
    border: "border-l-sakura-pink",
    text: "text-sakura-pink",
    glow: "shadow-[0_0_20px_rgba(255,20,147,0.1)]",
    dot: "bg-sakura-pink shadow-[0_0_5px_rgba(255,20,147,0.8)]",
  },
  telemetry: {
    border: "border-l-telemetry",
    text: "text-telemetry",
    glow: "shadow-[0_0_20px_rgba(0,255,0,0.1)]",
    dot: "bg-telemetry shadow-[0_0_5px_rgba(0,255,0,0.8)]",
  },
};

export default function MetricCard({
  label,
  value,
  subtext,
  accent = "telemetry",
}: MetricCardProps) {
  const style = accentMap[accent];

  return (
    <div
      className={`relative flex flex-col justify-between overflow-hidden rounded-r-xl rounded-l-sm bg-tarmac-light/90 backdrop-blur-md border-y border-r border-white/5 border-l-4 p-5 transition-all hover:bg-tarmac-light ${style.border} ${style.glow}`}
    >
      {/* Pure CSS Carbon Fiber Weave */}
      <div 
        className="absolute inset-0 opacity-[0.25] pointer-events-none mix-blend-multiply"
        style={{
          backgroundImage: `
            linear-gradient(45deg, #000 25%, transparent 25%, transparent 75%, #000 75%, #000),
            linear-gradient(45deg, #000 25%, transparent 25%, transparent 75%, #000 75%, #000)
          `,
          backgroundPosition: `0 0, 4px 4px`,
          backgroundSize: `8px 8px`
        }}
      />

      {/* Live Data Pulse Dot */}
      <div className="absolute top-4 right-4 flex h-3 w-3 items-center justify-center z-10">
        <span className={`absolute inline-flex h-full w-full animate-ping rounded-full opacity-75 ${style.dot}`} />
        <span className={`relative inline-flex h-2 w-2 rounded-full ${style.dot}`} />
      </div>

      {/* Content wrapper with z-10 so it sits on top of the carbon fiber */}
      <div className="relative z-10">
        <p className="text-xs font-mono uppercase tracking-[0.2em] text-zinc-500 mb-1">
          {label}
        </p>
        
        <h3 className="text-3xl md:text-4xl font-black uppercase italic tracking-tighter text-white drop-shadow-sm">
          {value}
        </h3>
        
        {subtext ? (
          <div className="mt-3 flex items-center gap-2 border-t border-white/10 pt-3">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className={`w-4 h-4 ${style.text}`}>
              <path fillRule="evenodd" d="M2 10a8 8 0 1116 0 8 8 0 01-16 0zm8-6a.75.75 0 01.75.75v4.5a.75.75 0 01-1.5 0v-4.5A.75.75 0 0110 4zm0 10a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd" />
            </svg>
            <p className="text-xs font-mono text-zinc-400 uppercase tracking-wider">{subtext}</p>
          </div>
        ) : null}
      </div>

      {/* Subtle tech background pattern */}
      <div className="absolute right-0 bottom-0 opacity-10 pointer-events-none z-0">
        <svg width="60" height="60" viewBox="0 0 60 60" xmlns="http://www.w3.org/2000/svg">
          <g fill="none" fillRule="evenodd">
            <g fill="currentColor" className={style.text}>
              <path d="M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z"/>
            </g>
          </g>
        </svg>
      </div>
    </div>
  );
}