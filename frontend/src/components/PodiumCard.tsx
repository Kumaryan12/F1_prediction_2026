type PodiumCardProps = {
  position: 1 | 2 | 3;
  driver: string;
};

const podiumStyle = {
  1: {
    glow: "shadow-[0_0_40px_rgba(255,215,0,0.15)] z-10",
    border: "border-t-4 border-t-[#FFD700] border-x-white/10 border-b-white/10",
    badge: "bg-[#FFD700] text-black",
    text: "text-white",
    bgNumber: "text-[#FFD700]/10",
  },
  2: {
    glow: "shadow-[0_0_20px_rgba(192,192,192,0.05)]",
    border: "border-t-4 border-t-[#C0C0C0] border-x-white/10 border-b-white/10",
    badge: "bg-[#C0C0C0] text-black",
    text: "text-zinc-200",
    bgNumber: "text-[#C0C0C0]/10",
  },
  3: {
    glow: "shadow-[0_0_20px_rgba(205,127,50,0.05)]",
    border: "border-t-4 border-t-[#CD7F32] border-x-white/10 border-b-white/10",
    badge: "bg-[#CD7F32] text-black",
    text: "text-zinc-300",
    bgNumber: "text-[#CD7F32]/10",
  },
};

// Map 3-letter initials to Full Driver Names
const driverNames: Record<string, string> = {
  "VER": "Max Verstappen",
  "PER": "Sergio Perez",
  "HAM": "Lewis Hamilton",
  "RUS": "George Russell",
  "LEC": "Charles Leclerc",
  "SAI": "Carlos Sainz",
  "NOR": "Lando Norris",
  "PIA": "Oscar Piastri",
  "ALO": "Fernando Alonso",
  "STR": "Lance Stroll",
  "GAS": "Pierre Gasly",
  "OCO": "Esteban Ocon",
  "ALB": "Alexander Albon",
  "TSU": "Yuki Tsunoda",
  "HUL": "Nico Hulkenberg",
  "MAG": "Kevin Magnussen",
  "BOT": "Valtteri Bottas",
  "ZHO": "Zhou Guanyu",
  "BEA": "Oliver Bearman",
  "ANT": "Kimi Antonelli",
  "DOO": "Jack Doohan",
  "LAW": "Liam Lawson",
  "COL": "Franco Colapinto",
  "BOR": "Gabriel Bortoleto"
};

export default function PodiumCard({ position, driver }: PodiumCardProps) {
  const style = podiumStyle[position];
  const fullName = driverNames[driver] || driver;

  return (
    <div
      className={`relative h-full w-full flex flex-col justify-between overflow-hidden rounded-xl bg-tarmac-light/80 backdrop-blur-md p-6 transition-transform duration-300 hover:-translate-y-1 ${style.border} ${style.glow}`}
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

      {/* Massive Background Number for Depth */}
      <div 
        className={`absolute -bottom-8 -right-4 text-[12rem] font-black italic leading-none select-none pointer-events-none ${style.bgNumber}`}
      >
        {position}
      </div>

      {/* Top: Position Badge */}
      <div className="relative z-10">
        <div
          className={`inline-flex items-center justify-center rounded-sm px-4 py-1 text-sm font-black italic tracking-widest ${style.badge}`}
        >
          P{position}
        </div>
      </div>

      {/* Bottom: Driver Info */}
      <div className="relative z-10 mt-auto pt-10">
        <div className="flex items-center gap-2 mb-1">
          <p className="text-xs font-mono uppercase tracking-[0.3em] text-zinc-500">
            Predicted Finisher
          </p>
          {/* Telemetry Tag for the 3-letter initial */}
          <span className="rounded bg-white/10 px-1.5 py-0.5 text-[0.6rem] font-mono text-zinc-400 not-italic tracking-widest border border-white/5">
            {driver}
          </span>
        </div>
        <h3 
          className={`text-3xl md:text-4xl font-black uppercase italic tracking-tighter drop-shadow-md leading-none mt-1 ${style.text}`}
        >
          {fullName}
        </h3>
      </div>
    </div>
  );
}