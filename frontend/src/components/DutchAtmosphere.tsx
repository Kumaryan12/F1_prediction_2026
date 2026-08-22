export default function DutchAtmosphere() {
  return (
    <div className="pointer-events-none fixed inset-0 z-0 overflow-hidden" aria-hidden="true">
      <div className="dashboard-grid absolute inset-0 opacity-60" />
      <div className="absolute left-0 top-0 h-full w-1 bg-dutch-orange" />
      <div className="dutch-dots absolute right-0 top-0 h-28 w-28 opacity-20" />
    </div>
  );
}
