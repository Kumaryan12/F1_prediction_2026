type PodiumCardProps = { position: 1 | 2 | 3; driver: string };

const driverNames: Record<string, string> = {
  VER: "Max Verstappen", PER: "Sergio Perez", HAM: "Lewis Hamilton", RUS: "George Russell",
  LEC: "Charles Leclerc", SAI: "Carlos Sainz", NOR: "Lando Norris", PIA: "Oscar Piastri",
  ALO: "Fernando Alonso", STR: "Lance Stroll", GAS: "Pierre Gasly", OCO: "Esteban Ocon",
  ALB: "Alexander Albon", TSU: "Yuki Tsunoda", HUL: "Nico Hulkenberg", MAG: "Kevin Magnussen",
  BOT: "Valtteri Bottas", ZHO: "Zhou Guanyu", BEA: "Oliver Bearman", ANT: "Kimi Antonelli",
  DOO: "Jack Doohan", LAW: "Liam Lawson", COL: "Franco Colapinto", HAD: "Isack Hadjar",
  BOR: "Gabriel Bortoleto", LIN: "Arvid Lindblad",
};

const positionColor = { 1: "bg-dutch-orange text-black", 2: "bg-[#b9bdc3] text-black", 3: "bg-[#a66b3f] text-black" };

export default function PodiumCard({ position, driver }: PodiumCardProps) {
  const fullName = driverNames[driver] || driver;
  const [first, ...lastParts] = fullName.split(" ");
  return (
    <article className="relative min-h-56 overflow-hidden bg-[#111315] p-6">
      <div className="absolute right-4 top-1 select-none font-mono text-[7rem] font-bold leading-none text-white/[0.035]">{position}</div>
      <div className="relative flex h-full flex-col justify-between">
        <div className="flex items-start justify-between">
          <span className={`px-3 py-1.5 text-sm font-black italic ${positionColor[position]}`}>P{position}</span>
          <span className="font-mono text-[8px] uppercase tracking-[0.2em] text-zinc-600">Projected finish</span>
        </div>
        <div>
          <p className="font-mono text-[9px] font-bold uppercase tracking-[0.28em] text-dutch-orange">{driver}</p>
          <h3 className="mt-2 text-3xl font-black uppercase italic leading-[0.9] tracking-[-0.045em] text-white">
            <span className="block text-lg text-zinc-500">{first}</span>{lastParts.join(" ")}
          </h3>
        </div>
      </div>
    </article>
  );
}
