import type { CSSProperties } from "react";
import type { PredictionRow } from "@/lib/types";

type PredictionTableProps = { rows: PredictionRow[] };

const driverNames: Record<string, string> = {
  VER: "Max Verstappen", PER: "Sergio Perez", HAM: "Lewis Hamilton", RUS: "George Russell",
  LEC: "Charles Leclerc", SAI: "Carlos Sainz", NOR: "Lando Norris", PIA: "Oscar Piastri",
  ALO: "Fernando Alonso", STR: "Lance Stroll", GAS: "Pierre Gasly", OCO: "Esteban Ocon",
  ALB: "Alexander Albon", TSU: "Yuki Tsunoda", HUL: "Nico Hulkenberg", BOT: "Valtteri Bottas",
  BEA: "Oliver Bearman", ANT: "Kimi Antonelli", LAW: "Liam Lawson", COL: "Franco Colapinto",
  HAD: "Isack Hadjar", BOR: "Gabriel Bortoleto", LIN: "Arvid Lindblad",
};

const teamColors: Record<string, string> = {
  "Red Bull Racing": "#3671c6", Ferrari: "#ed1131", McLaren: "#ff8700",
  Mercedes: "#27f4d2", "Aston Martin": "#229971", "Racing Bulls": "#6692ff",
  "Haas F1 Team": "#b6babd", Williams: "#64c4ff", Alpine: "#ff87bc",
  Audi: "#f50537", Cadillac: "#d7b56d", "Kick Sauber": "#52e252",
};

function probability(value?: number | null) {
  return value == null ? "—" : `${Math.round(value * 100)}%`;
}

function decimal(value?: number | null) {
  return value == null ? "—" : value.toFixed(2);
}

function movement(row: PredictionRow) {
  if (row.grid_pos == null) return { label: "—", direction: "neutral" };
  const delta = row.grid_pos - row.pred_rank;
  if (delta > 0) return { label: `+${delta}`, direction: "gain" };
  if (delta < 0) return { label: String(delta), direction: "loss" };
  return { label: "—", direction: "neutral" };
}

export default function PredictionTable({ rows }: PredictionTableProps) {
  return (
    <div className="table-wrap">
      <table className="prediction-table">
        <thead><tr><th>Pred.</th><th>Driver</th><th>Team</th><th>Grid</th><th>Move</th><th>Finish score</th><th>Uncertainty</th><th>Win</th><th>Podium</th><th>Top 10</th></tr></thead>
        <tbody>
          {rows.map((row) => {
            const move = movement(row);
            const teamColor = teamColors[row.team] || "#7d8088";
            return (
              <tr key={row.driver}>
                <td className="rank-cell"><span className="rank">{String(row.pred_rank).padStart(2, "0")}</span></td>
                <td><div className="driver-cell"><span className="driver-code">{row.driver}</span><span><strong>{driverNames[row.driver] || row.driver}</strong><small>{row.driver}</small></span></div></td>
                <td><span className="team" style={{ "--team-color": teamColor } as CSSProperties}>{row.team}</span></td>
                <td className="numeric">P{row.grid_pos ?? "—"}</td>
                <td><span className={`movement ${move.direction}`}>{move.label}</span></td>
                <td className="numeric strong">{decimal(row.pred_finish)}</td>
                <td className="numeric muted">±{decimal(row.pred_std)}</td>
                <td><Probability value={row.p_win} /></td>
                <td><Probability value={row.p_podium} /></td>
                <td><Probability value={row.p_top10} /></td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

function Probability({ value }: { value?: number | null }) {
  const numeric = value ?? 0;
  return <div className="probability" aria-label={probability(value)}><span style={{ width: `${Math.min(100, Math.max(0, numeric * 100))}%` }} /><strong>{probability(value)}</strong></div>;
}
