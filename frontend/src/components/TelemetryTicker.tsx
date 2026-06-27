import { PredictionRow } from "@/lib/types";

type TelemetryTickerProps = {
  rows: PredictionRow[];
};

export default function TelemetryTicker({ rows }: TelemetryTickerProps) {
  // Format the ML predictions into authentic timing screen strings
  // Example: "VER: P1 [1.0 - 1.2]"
  const predictionStrings = rows.map((row) => {
    const low = row.pi68_low?.toFixed(1) ?? "-";
    const high = row.pi68_high?.toFixed(1) ?? "-";
    return `${row.driver}: P${row.pred_rank} [${low} - ${high}]`;
  });

  // Inject some live race control data for the Austrian GP vibe
  // Spielberg is known for high-speed undulations, changeable mountain weather, and intense kerb usage!
  const tickerItems = [
    "RACE CONTROL: DRS ENABLED",
    "TRACK TEMP: 28.2°C",
    "AIR TEMP: 19.5°C",
    "WIND: 5 KM/H NW (ALPINE BREEZE)",
    "HUMIDITY: 55%",
    "WEATHER: OVERCAST / HIGH ALTITUDE",
    "TRACK LIMITS: TURNS 1, 4, 9, 10",
    ...predictionStrings,
  ];

  // Join them with the classic triple-slash F1 separator
  const tickerText = tickerItems.join(" /// ") + " /// ";

  return (
    <div className="relative flex w-full overflow-hidden border-y border-spielberg-red/20 bg-tarmac/95 py-2 shadow-[0_0_15px_rgba(227,34,25,0.15)] backdrop-blur-md">
      
      {/* We render two identical blocks side-by-side. 
        As the first one scrolls entirely out of view, the second one perfectly replaces it!
      */}
      <div className="flex animate-ticker whitespace-nowrap">
        {/* Swapped to Spielberg Red with an intense Austrian drop-shadow */}
        <span className="mx-4 text-xs font-mono font-bold uppercase tracking-[0.2em] text-spielberg-red drop-shadow-[0_0_5px_rgba(227,34,25,0.5)]">
          {tickerText}
        </span>
      </div>
      
      <div className="flex animate-ticker whitespace-nowrap">
        {/* Duplicate block for the infinite scroll */}
        <span className="mx-4 text-xs font-mono font-bold uppercase tracking-[0.2em] text-spielberg-red drop-shadow-[0_0_5px_rgba(227,34,25,0.5)]">
          {tickerText}
        </span>
      </div>

      {/* Edge Gradients to make the text smoothly fade in and out of the screen */}
      <div className="absolute top-0 left-0 h-full w-16 bg-gradient-to-r from-tarmac to-transparent z-10" />
      <div className="absolute top-0 right-0 h-full w-16 bg-gradient-to-l from-tarmac to-transparent z-10" />
    </div>
  );
}