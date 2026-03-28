import { PredictionRow } from "@/lib/types";

type PredictionTableProps = {
  rows: PredictionRow[];
};

function pct(value?: number | null) {
  if (value === null || value === undefined) return "-";
  return `${(value * 100).toFixed(1)}%`;
}

// Map F1 teams to their exact official hex colors
const teamColors: Record<string, string> = {
  "Red Bull Racing": "border-[#3671C6] text-[#3671C6]",
  "Ferrari": "border-[#E80020] text-[#E80020]",
  "McLaren": "border-[#FF8000] text-[#FF8000]",
  "Mercedes": "border-[#27F4D2] text-[#27F4D2]",
  "Aston Martin": "border-[#229971] text-[#229971]",
  "RB": "border-[#6692FF] text-[#6692FF]",
  "Haas F1 Team": "border-[#B6BABD] text-[#B6BABD]",
  "Williams": "border-[#64C4FF] text-[#64C4FF]",
  "Alpine": "border-[#FF87BC] text-[#FF87BC]",
  "Kick Sauber": "border-[#52E252] text-[#52E252]"
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
  "HAD": "Isack Hadjar",
  "BOR": "Gabriel Bortoleto"
};

export default function PredictionTable({ rows }: PredictionTableProps) {
  return (
    <div className="w-full overflow-x-auto">
      <table className="min-w-full border-collapse text-left text-sm whitespace-nowrap">
        <thead className="border-b border-white/20 bg-tarmac/80 backdrop-blur-md">
          <tr>
            <th className="px-4 py-3 text-xs font-mono uppercase tracking-[0.2em] text-zinc-500">Pos</th>
            <th className="px-4 py-3 text-xs font-mono uppercase tracking-[0.2em] text-zinc-500">Driver</th>
            <th className="px-4 py-3 text-xs font-mono uppercase tracking-[0.2em] text-zinc-500">Constructor</th>
            <th className="px-4 py-3 text-xs font-mono uppercase tracking-[0.2em] text-zinc-500">Grid</th>
            <th className="px-4 py-3 text-xs font-mono uppercase tracking-[0.2em] text-zinc-500">Pred. Finish</th>
            <th className="px-4 py-3 text-xs font-mono uppercase tracking-[0.2em] text-zinc-500">68% Interval</th>
            <th className="px-4 py-3 text-xs font-mono uppercase tracking-[0.2em] text-zinc-500">Podium %</th>
            <th className="px-4 py-3 text-xs font-mono uppercase tracking-[0.2em] text-zinc-500">Top 10 %</th>
          </tr>
        </thead>
        
        <tbody className="divide-y divide-white/5 bg-tarmac-light/30">
          {rows.map((row, idx) => {
            const teamStyle = teamColors[row.team] || "border-white/20 text-white/50";
            
            // Look up the full name. If it's not in our dictionary, fallback to whatever the API sent.
            const fullName = driverNames[row.driver] || row.driver;
            
            return (
              <tr
                key={row.driver}
                className="group transition-colors hover:bg-white/10"
              >
                <td className={`px-4 py-3 border-l-4 ${teamStyle.split(' ')[0]}`}>
                  <span className="inline-flex h-6 w-6 items-center justify-center bg-white/10 font-mono text-xs font-bold text-white shadow-inner">
                    {row.pred_rank}
                  </span>
                </td>
                
                {/* Driver */}
                <td className="px-4 py-3 text-base font-black uppercase italic tracking-wider text-white drop-shadow-sm transition-colors flex items-center gap-3">
                  {fullName}
                  <span className="hidden sm:inline-block rounded bg-white/10 px-1.5 py-0.5 text-[0.6rem] font-mono text-zinc-400 not-italic tracking-widest border border-white/5">
                    {row.driver}
                  </span>
                </td>
                
                <td className={`px-4 py-3 text-xs font-bold uppercase tracking-widest drop-shadow-sm ${teamStyle.split(' ')[1]}`}>
                  {row.team}
                </td>
                
                <td className="px-4 py-3 font-mono text-zinc-300">
                  {row.grid_pos ?? "-"}
                </td>
                
                <td className="px-4 py-3 font-mono font-bold text-white">
                  {row.pred_finish.toFixed(2)}
                </td>
                
                <td className="px-4 py-3 font-mono text-zinc-400">
                  [{row.pi68_low?.toFixed(2) ?? "-"} <span className="text-zinc-600 mx-1">↔</span> {row.pi68_high?.toFixed(2) ?? "-"}]
                </td>
                
                {/* Podium % - Now Sakura Pink */}
                <td className="px-4 py-3">
                  <span className="inline-block border border-sakura-pink/30 bg-sakura-pink/10 px-2 py-0.5 font-mono text-xs font-bold text-sakura-pink shadow-[0_0_8px_rgba(255,20,147,0.2)]">
                    {pct(row.p_podium)}
                  </span>
                </td>
                
                {/* Top 10 % - Now Suzuka Red */}
                <td className="px-4 py-3">
                  <span className="inline-block border border-suzuka-red/30 bg-suzuka-red/10 px-2 py-0.5 font-mono text-xs font-bold text-suzuka-red shadow-[0_0_8px_rgba(225,6,0,0.2)]">
                    {pct(row.p_top10)}
                  </span>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}