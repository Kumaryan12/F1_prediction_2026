const markers = [
  ["8%", "18%", "5px"],
  ["22%", "68%", "3px"],
  ["41%", "12%", "4px"],
  ["64%", "74%", "5px"],
  ["82%", "28%", "3px"],
  ["93%", "61%", "4px"],
] as const;

export default function HungaryAtmosphere() {
  return (
    <div className="pointer-events-none fixed inset-0 z-0 overflow-hidden" aria-hidden="true">
      <div className="heat-orb absolute -left-48 top-24 h-[30rem] w-[30rem] rounded-full bg-hungary-red/[0.035] blur-3xl" />
      <div className="heat-orb absolute -right-40 top-[36rem] h-[26rem] w-[26rem] rounded-full bg-hungary-green/[0.025] blur-3xl [animation-delay:-4s]" />
      {markers.map(([left, top, size], index) => (
        <span
          key={`${left}-${top}`}
          className={`absolute rounded-full ${
            index % 2 === 0 ? "bg-hungary-red/25" : "bg-hungary-green/20"
          }`}
          style={{ left, top, width: size, height: size }}
        />
      ))}
    </div>
  );
}
