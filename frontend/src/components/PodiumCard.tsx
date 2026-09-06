import type { CSSProperties } from "react";
import { ArrowUpRight, Crown } from "lucide-react";
import type { PredictionRow } from "@/lib/types";
import { driverName, percent, teamColor } from "@/lib/presentation";

export default function PodiumCard({ position, row }: { position: 1 | 2 | 3; row?: PredictionRow }) {
  const name = driverName(row?.driver || "Awaiting data");
  const [first, ...last] = name.split(" ");
  return <article className={`podium-card podium-${position}`} style={{ "--team-color": teamColor(row?.team || "") } as CSSProperties}>
    <div className="podium-top"><span className="podium-place">{position === 1 ? <Crown size={14} /> : <span className="small-square" />} {position === 1 ? "THE MODEL’S FAVOURITE" : position === 2 ? "THE CHALLENGER" : "THE PODIUM CONTENDER"}</span><span className="podium-rank">P{position}</span></div>
    <span className="podium-watermark" aria-hidden="true">0{position}</span>
    <div className="podium-driver"><span className="team-label"><i />{row?.team || "Team unavailable"}</span><h3><span>{first}</span>{last.join(" ")}</h3><span className="driver-tag">{row?.driver || "—"}<ArrowUpRight size={14} /></span></div>
    <div className="podium-footer"><span>Podium probability <strong>{percent(row?.p_podium)}</strong></span><span>Win probability <strong>{percent(row?.p_win)}</strong></span></div>
  </article>;
}
