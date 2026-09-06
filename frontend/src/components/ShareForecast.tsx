"use client";
import { useState } from "react";
import { Check, Download, Link2 } from "lucide-react";
import type { PredictionRow } from "@/lib/types";
import { driverName, percent, teamColor } from "@/lib/presentation";

export default function ShareForecast({ race, rows }: { race: string; rows: PredictionRow[] }) {
  const [message, setMessage] = useState("");
  async function copyLink() {
    try { await navigator.clipboard.writeText(`${window.location.origin}${window.location.pathname}#forecast`); setMessage("Link copied"); }
    catch { setMessage("Copy the page address from your browser to share."); }
  }
  function download() {
    try {
      const canvas = document.createElement("canvas"); canvas.width = 1080; canvas.height = 1350;
      const ctx = canvas.getContext("2d"); if (!ctx) throw new Error("Canvas unavailable");
      ctx.fillStyle = "#0d0e12"; ctx.fillRect(0, 0, 1080, 1350);
      ctx.fillStyle = "#f34b43"; ctx.fillRect(0, 0, 1080, 9);
      ctx.font = "bold 52px Arial"; ctx.fillStyle = "#faf9f5"; ctx.fillText("AK_predicts", 70, 110);
      ctx.font = "20px monospace"; ctx.fillStyle = "#a6a6b1"; ctx.fillText("THE RACE, BEFORE THE RACE.", 70, 153);
      ctx.font = "bold 74px Arial"; ctx.fillStyle = "#faf9f5"; ctx.fillText("PODIUM", 70, 280); ctx.fillStyle = "#f34b43"; ctx.fillText("PREDICTION.", 70, 357);
      ctx.font = "26px Arial"; ctx.fillStyle = "#a6a6b1"; ctx.fillText(race, 70, 418, 930);
      rows.slice(0, 3).forEach((row, index) => {
        const y = 485 + index * 218;
        ctx.fillStyle = "#191b21"; ctx.fillRect(70, y, 940, 195);
        ctx.fillStyle = teamColor(row.team); ctx.fillRect(70, y, 5, 195);
        ctx.font = "bold 62px Arial"; ctx.fillText(`0${index + 1}`, 105, y + 85);
        ctx.fillStyle = "#faf9f5"; ctx.font = "bold 40px Arial"; ctx.fillText(driverName(row.driver), 220, y + 65, 740);
        ctx.fillStyle = "#a6a6b1"; ctx.font = "23px Arial"; ctx.fillText(row.team, 220, y + 105);
        ctx.font = "21px monospace"; ctx.fillText(`PODIUM ${percent(row.p_podium)}   WIN ${percent(row.p_win)}`, 220, y + 151);
      });
      ctx.font = "bold 27px Arial"; ctx.fillStyle = "#faf9f5"; ctx.fillText("Follow @AK_predicts on Instagram", 70, 1220);
      ctx.font = "18px Arial"; ctx.fillStyle = "#a6a6b1"; ctx.fillText("Model forecast · Estimates, not guaranteed results", 70, 1265);
      canvas.toBlob((blob) => {
        if (!blob) { setMessage("Could not create the card. Please try again."); return; }
        const url = URL.createObjectURL(blob); const link = document.createElement("a");
        link.href = url; link.download = `AK_predicts-${race.replace(/[^a-z0-9]+/gi, "-")}-podium.png`; link.click();
        window.setTimeout(() => URL.revokeObjectURL(url), 1000); setMessage("1080 × 1350 card downloaded");
      }, "image/png");
    } catch { setMessage("Could not create the card. Please try again."); }
  }
  return <div className="share-controls"><button className="button button-quiet" onClick={copyLink} aria-label="Copy forecast link">{message === "Link copied" ? <Check size={14} /> : <Link2 size={14} />}<span>Copy link</span></button><button className="button button-light" onClick={download}><Download size={14} />Save prediction</button><span className="share-status" role="status">{message}</span></div>;
}
