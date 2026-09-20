type FeatureData = { name: string; value: number };

export default function FeatureImportanceChart({ features }: { features: FeatureData[] }) {
  const sorted = [...features].filter((item) => Number.isFinite(item.value) && item.value >= 0).sort((a, b) => b.value - a.value).slice(0, 12);
  const max = Math.max(...sorted.map((item) => item.value), 0.01);
  if (!sorted.length) return <div className="importance-empty">Feature importance is currently unavailable.</div>;

  return (
    <div className="importance-surface">
      <div className="importance-summary"><p>Relative influence across the race ensemble.</p><strong>{(sorted[0].value * 100).toFixed(1)}%</strong><span>Top feature contribution</span></div>
      <ol className="importance-list">
        {sorted.map((item, index) => <li key={item.name}><span className="feature-rank">{String(index + 1).padStart(2, "0")}</span><div className="feature-data"><div className="feature-label"><span>{item.name.replace(/_/g, " ")}</span><strong>{(item.value * 100).toFixed(1)}%</strong></div><div className="feature-track" aria-hidden="true"><span style={{ width: `${(item.value / max) * 100}%` }} /></div></div></li>)}
      </ol>
    </div>
  );
}
