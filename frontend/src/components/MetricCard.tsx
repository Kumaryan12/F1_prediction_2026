type MetricCardProps = {
  label: string;
  value: string;
  subtext?: string;
  accent?: "red" | "yellow" | "green" | "pink" | "cyan" | "telemetry";
};

const accentMap = {
  red: "bg-dutch-orange",
  yellow: "bg-dutch-sand",
  pink: "bg-dutch-red",
  green: "bg-dutch-blue",
  cyan: "bg-dutch-blue",
  telemetry: "bg-dutch-orange",
};

export default function MetricCard({ label, value, subtext, accent = "telemetry" }: MetricCardProps) {
  return (
    <article className="relative min-h-36 bg-[#111315] p-5">
      <span className={`absolute left-0 top-0 h-1 w-12 ${accentMap[accent]}`} />
      <div className="flex h-full flex-col justify-between">
        <div className="flex items-center justify-between">
          <p className="font-mono text-[8px] font-bold uppercase tracking-[0.2em] text-zinc-500">{label}</p>
          <span className="font-mono text-[8px] text-zinc-700">DATA/26</span>
        </div>
        <h3 className="my-4 break-words text-3xl font-black uppercase italic leading-none tracking-[-0.05em] text-white">{value}</h3>
        {subtext && <p className="border-t border-white/10 pt-2 font-mono text-[8px] uppercase tracking-[0.14em] text-zinc-600">{subtext}</p>}
      </div>
    </article>
  );
}
