type Drop = {
  id: number;
  left: string;
  duration: string;
  delay: string;
  height: string;
  opacity: number;
};

const drops: Drop[] = Array.from({ length: 34 }, (_, id) => ({
  id,
  left: `${(id * 31.7) % 100}vw`,
  duration: `${2.8 + (id % 9) * 0.22}s`,
  delay: `-${(id * 0.47) % 7}s`,
  height: `${10 + (id % 5) * 3}px`,
  opacity: 0.12 + (id % 4) * 0.05,
}));

export default function BelgiumWeather() {
  return (
    <div className="pointer-events-none fixed inset-0 z-0 overflow-hidden" aria-hidden="true">
      <div className="absolute inset-0 bg-[linear-gradient(112deg,transparent_0%,rgba(255,255,255,0.018)_46%,transparent_75%)]" />
      {drops.map((drop) => (
        <span
          key={drop.id}
          className="absolute top-[-5vh] w-px rounded-full bg-zinc-300"
          style={{
            left: drop.left,
            height: drop.height,
            opacity: drop.opacity,
            animation: `fall ${drop.duration} linear infinite ${drop.delay}, sway ${drop.duration} ease-in-out infinite alternate ${drop.delay}`,
          }}
        />
      ))}
    </div>
  );
}
