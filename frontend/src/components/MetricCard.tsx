type MetricCardProps = { label: string; value: string; subtext?: string; accent?: "red" | "yellow" | "green" | "pink" | "cyan" | "telemetry" };
const accentMap = { red: "bg-racing-red", yellow: "bg-monza-gold", pink: "bg-racing-red", green: "bg-italia-green", cyan: "bg-italia-green", telemetry: "bg-monza-ivory" };
export default function MetricCard({ label, value, subtext, accent = "telemetry" }: MetricCardProps) {
  return <article className="metric-card"><div className="metric-label"><p>{label}</p><i className={accentMap[accent]} /></div><h3 className="metric-value">{value}</h3>{subtext && <p className="metric-subtext">{subtext}</p>}</article>;
}
