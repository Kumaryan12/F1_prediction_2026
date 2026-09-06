import { PredictionRow } from "@/lib/types";

type PredictionTableProps = { rows: PredictionRow[] };

function pct(value?: number | null) {
  return value === null || value === undefined ? "—" : `${(value * 100).toFixed(1)}%`;
}

function decimal(value?: number | null) {
  return value === null || value === undefined ? "—" : value.toFixed(3);
}

const teamColors: Record<string, string> = {
  "Red Bull Racing": "border-[#3671C6] text-[#3671C6]",
  Ferrari: "border-[#E80020] text-[#E80020]",
  McLaren: "border-[#FF8000] text-[#FF8000]",
  Mercedes: "border-[#27F4D2] text-[#27F4D2]",
  "Aston Martin": "border-[#229971] text-[#229971]",
  "Racing Bulls": "border-[#6692FF] text-[#6692FF]",
  RB: "border-[#6692FF] text-[#6692FF]",
  "Haas F1 Team": "border-[#B6BABD] text-[#B6BABD]",
  Williams: "border-[#64C4FF] text-[#64C4FF]",
  Alpine: "border-[#FF87BC] text-[#FF87BC]",
  Audi: "border-[#f50537] text-[#f50537]",
  "Kick Sauber": "border-[#52E252] text-[#52E252]",
};

const driverNames: Record<string, string> = {
  VER: "Max Verstappen", PER: "Sergio Perez", HAM: "Lewis Hamilton", RUS: "George Russell",
  LEC: "Charles Leclerc", SAI: "Carlos Sainz", NOR: "Lando Norris", PIA: "Oscar Piastri",
  ALO: "Fernando Alonso", STR: "Lance Stroll", GAS: "Pierre Gasly", OCO: "Esteban Ocon",
  ALB: "Alexander Albon", TSU: "Yuki Tsunoda", HUL: "Nico Hulkenberg", MAG: "Kevin Magnussen",
  BOT: "Valtteri Bottas", ZHO: "Zhou Guanyu", BEA: "Oliver Bearman", ANT: "Kimi Antonelli",
  DOO: "Jack Doohan", LAW: "Liam Lawson", COL: "Franco Colapinto", HAD: "Isack Hadjar",
  BOR: "Gabriel Bortoleto", LIN: "Arvid Lindblad",
};

export default function PredictionTable({ rows }: PredictionTableProps) {
  return (
    <div>
      <div className="flex items-center justify-between border-b border-white/10 bg-[#0b0c0e] px-4 py-3 font-mono text-[10px] uppercase tracking-[0.16em] text-zinc-400">
        <span>Complete raw model output</span>
        <span className="sm:hidden">Swipe horizontally →</span>
      </div>
      <div className="custom-scrollbar w-full overflow-x-auto">
        <table className="min-w-[1450px] border-collapse whitespace-nowrap text-left">
          <thead className="bg-tarmac font-mono uppercase">
            <tr className="border-b border-white/10 text-[10px] tracking-[0.16em] text-zinc-400">
              <th colSpan={3} className="sticky left-0 z-30 border-r border-white/10 bg-tarmac px-4 py-2 text-racing-red">Classification</th>
              <th colSpan={2} className="border-r border-white/10 px-4 py-2 text-racing-red">Model output</th>
              <th colSpan={3} className="border-r border-white/10 px-4 py-2 text-racing-red">Uncertainty</th>
              <th colSpan={4} className="px-4 py-2 text-racing-red">Probability</th>
            </tr>
            <tr className="border-b border-white/15 text-[10px] tracking-[0.12em] text-zinc-400">
              <Header className="sticky left-0 z-30 w-16 bg-tarmac">Rank</Header>
              <Header className="sticky left-16 z-30 w-52 bg-tarmac">Driver</Header>
              <Header className="border-r border-white/10">Team</Header>
              <Header>Pred. finish</Header><Header className="border-r border-white/10">Pred. rank</Header>
              <Header>Std dev</Header><Header>68% low</Header><Header className="border-r border-white/10">68% high</Header>
              <Header>Win</Header><Header>Top 10</Header><Header>Podium</Header><Header>Rank ±1</Header>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/[0.06] bg-[#111315]">
            {rows.map((row) => {
              const teamStyle = teamColors[row.team] || "border-white/20 text-zinc-400";
              const borderColor = teamStyle.split(" ")[0];
              const textColor = teamStyle.split(" ")[1];
              return (
                <tr key={row.driver} className="group font-mono text-[11px] text-zinc-400 hover:bg-white/[0.035]">
                  <td className={`sticky left-0 z-20 w-16 border-l-4 bg-[#111315] px-4 py-4 group-hover:bg-[#191b1e] ${borderColor}`}><span className="text-base font-black italic text-white">P{row.pred_rank}</span></td>
                  <td className="sticky left-16 z-20 w-52 bg-[#111315] px-4 py-4 group-hover:bg-[#191b1e]"><div className="font-sans text-sm font-black uppercase italic tracking-tight text-white">{driverNames[row.driver] || row.driver}</div><span className="mt-1 block text-[10px] tracking-[0.2em] text-zinc-400">{row.driver}</span></td>
                  <td className={`border-r border-white/10 px-4 py-4 font-sans text-xs font-bold uppercase ${textColor}`}>{row.team}</td>
                  <DataCell strong>{decimal(row.pred_finish)}</DataCell><DataCell className="border-r border-white/10" strong>P{row.pred_rank}</DataCell>
                  <DataCell>{decimal(row.pred_std)}</DataCell><DataCell>{decimal(row.pi68_low)}</DataCell><DataCell className="border-r border-white/10">{decimal(row.pi68_high)}</DataCell>
                  <Probability value={row.p_win} accent /><Probability value={row.p_top10} /><Probability value={row.p_podium} accent /><Probability value={row.p_rank_pm1} />
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function Header({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return <th className={`px-4 py-3 font-medium ${className}`}>{children}</th>;
}

function DataCell({ children, className = "", strong = false }: { children: React.ReactNode; className?: string; strong?: boolean }) {
  return <td className={`px-4 py-4 tabular-nums ${strong ? "font-bold text-white" : ""} ${className}`}>{children}</td>;
}

function Probability({ value, accent = false }: { value?: number | null; accent?: boolean }) {
  return <td className="px-4 py-4 tabular-nums"><span className={`inline-block min-w-14 border px-2 py-1 text-center font-bold ${accent ? "border-racing-red/40 bg-racing-red/10 text-racing-red" : "border-white/10 bg-white/[0.025] text-zinc-300"}`}>{pct(value)}</span></td>;
}
