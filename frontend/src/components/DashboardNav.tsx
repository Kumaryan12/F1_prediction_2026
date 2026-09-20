"use client";
import { useEffect, useState } from "react";
import { Activity, Flag, FlaskConical, GitCompareArrows, Layers3 } from "lucide-react";
const sections = [
  { id: "overview", label: "Overview", icon: Flag }, { id: "forecast", label: "Predictions", icon: Activity },
  { id: "h2h", label: "Head to head", icon: GitCompareArrows }, { id: "simulator", label: "Simulator", icon: FlaskConical },
  { id: "model", label: "The model", icon: Layers3 },
];
export default function DashboardNav() {
  const [active, setActive] = useState("overview");
  useEffect(() => {
    const update = () => {
      let closestTop = -Infinity;
      let candidates = ["overview"];
      for (const { id } of sections) {
        const element = document.getElementById(id);
        if (!element) continue;
        const top = element.getBoundingClientRect().top;
        if (top > 180) continue;
        if (top > closestTop + 2) { closestTop = top; candidates = [id]; }
        else if (Math.abs(top - closestTop) <= 2) candidates.push(id);
      }
      setActive((current) => candidates.includes(current) ? current : candidates[0]);
    };
    update(); window.addEventListener("scroll", update, { passive: true });
    return () => window.removeEventListener("scroll", update);
  }, []);
  return <nav className="dashboard-nav" aria-label="Main navigation">{sections.map(({ id, label, icon: Icon }) => <a key={id} href={`#${id}`} aria-current={active === id ? "location" : undefined} onClick={() => setActive(id)}><Icon size={14} /><span>{label}</span></a>)}</nav>;
}
