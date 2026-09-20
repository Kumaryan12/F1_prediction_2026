export const driverNames: Record<string, string> = {
  VER: "Max Verstappen", PER: "Sergio Perez", HAM: "Lewis Hamilton", RUS: "George Russell",
  LEC: "Charles Leclerc", SAI: "Carlos Sainz", NOR: "Lando Norris", PIA: "Oscar Piastri",
  ALO: "Fernando Alonso", STR: "Lance Stroll", GAS: "Pierre Gasly", OCO: "Esteban Ocon",
  ALB: "Alexander Albon", TSU: "Yuki Tsunoda", HUL: "Nico Hulkenberg", MAG: "Kevin Magnussen",
  BOT: "Valtteri Bottas", ZHO: "Zhou Guanyu", BEA: "Oliver Bearman", ANT: "Kimi Antonelli",
  DOO: "Jack Doohan", LAW: "Liam Lawson", COL: "Franco Colapinto", HAD: "Isack Hadjar",
  BOR: "Gabriel Bortoleto", LIN: "Arvid Lindblad",
};
export const teamColors: Record<string, string> = {
  "Red Bull Racing": "#6d9aff", Ferrari: "#ff534d", McLaren: "#ffab52", Mercedes: "#6be5cd",
  "Aston Martin": "#64bba0", "Racing Bulls": "#95b5ff", RB: "#95b5ff", "Haas F1 Team": "#c6c8cf",
  Williams: "#74bdff", Alpine: "#eda2d2", Audi: "#ff7279", "Kick Sauber": "#8de570", Cadillac: "#c8c8cf",
};
export function driverName(code: string) { return driverNames[code] || code; }
export function teamColor(team: string) { return teamColors[team] || "#b7bdcc"; }
export function percent(value?: number | null) { return value == null || !Number.isFinite(value) ? "—" : `${(value * 100).toFixed(1)}%`; }
export function position(value?: number | null) { return value != null && value > 0 ? `P${Math.round(value)}` : "—"; }
