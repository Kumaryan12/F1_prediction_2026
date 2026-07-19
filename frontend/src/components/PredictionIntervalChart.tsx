"use client";

import {
  CartesianGrid,
  ResponsiveContainer,
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  Tooltip,
  ErrorBar,
} from "recharts";
import { PredictionRow } from "@/lib/types";

type PredictionIntervalChartProps = {
  rows: PredictionRow[];
};

type ChartRow = {
  driver: string;
  pred_rank: number;
  pred_finish: number;
  lowError: number;
  highError: number;
};

export default function PredictionIntervalChart({
  rows,
}: PredictionIntervalChartProps) {
  const chartData: ChartRow[] = rows.map((row) => ({
    driver: row.driver,
    pred_rank: row.pred_rank,
    pred_finish: row.pred_finish,
    lowError: Math.max(0, row.pred_finish - (row.pi68_low ?? row.pred_finish)),
    highError: Math.max(0, (row.pi68_high ?? row.pred_finish) - row.pred_finish),
  }));

  return (
    <div className="relative overflow-hidden rounded-2xl border border-white/10 bg-tarmac-light/90 shadow-[0_0_30px_rgba(0,210,127,0.1)] backdrop-blur-md p-6 sm:p-8">
      {/* Background Austria Glow */}
      <div className="absolute top-0 right-0 w-1/2 h-full bg-gradient-to-l from-styrian-green/5 to-transparent pointer-events-none" />
      <div className="absolute top-0 left-0 w-1/2 h-full bg-gradient-to-r from-spielberg-red/5 to-transparent pointer-events-none" />

      {/* Header */}
      <div className="mb-8 border-b border-white/10 pb-4 relative z-10 flex justify-between items-end">
        <div>
          <h2 className="text-2xl font-black uppercase italic tracking-tight text-white flex items-center gap-3">
            <span className="h-3 w-3 rounded-full bg-spielberg-red animate-pulse shadow-[0_0_10px_rgba(227,34,25,0.8)]" />
            Prediction Intervals
          </h2>
          <p className="mt-1 text-xs font-mono text-zinc-400 uppercase tracking-widest">
            68% Confidence Range // Lower is better
          </p>
        </div>
      </div>

      <div className="h-[420px] w-full relative z-10">
        <ResponsiveContainer width="100%" height="100%">
          <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 10 }}>
            {/* Subtle Grid Lines */}
            <CartesianGrid stroke="rgba(255,255,255,0.05)" strokeDasharray="3 3" />
            
            <XAxis
              type="number"
              dataKey="pred_rank"
              domain={[1, 10]}
              tick={{ fill: "#a1a1aa", fontSize: 10, fontFamily: "monospace" }}
              tickLine={false}
              axisLine={{ stroke: "rgba(255,255,255,0.1)" }}
              label={{
                value: "PREDICTED RANK",
                position: "insideBottom",
                offset: -10,
                fill: "#E32219", // Spielberg Red
                fontSize: 10,
                fontFamily: "monospace",
                letterSpacing: "0.2em",
              }}
            />
            
            <YAxis
              type="number"
              dataKey="pred_finish"
              reversed
              domain={[10, 1]}
              tick={{ fill: "#a1a1aa", fontSize: 10, fontFamily: "monospace" }}
              tickLine={false}
              axisLine={{ stroke: "rgba(255,255,255,0.1)" }}
              label={{
                value: "PREDICTED FINISH",
                angle: -90,
                position: "insideLeft",
                fill: "#FDDA24",
                fontSize: 10,
                fontFamily: "monospace",
                letterSpacing: "0.2em",
              }}
            />
            
            <Tooltip
              cursor={{ stroke: "rgba(239,51,64,0.15)", strokeWidth: 2 }}
              contentStyle={{
                background: "#08090B",
                border: "1px solid rgba(239,51,64,0.3)",
                borderRadius: "8px",
                boxShadow: "0 0 15px rgba(239,51,64,0.2)",
                color: "white",
                fontFamily: "monospace",
                textTransform: "uppercase",
                fontSize: "12px",
              }}
              formatter={(value, name) => [
                typeof value === "number" ? (
                  <span key="value" style={{ color: "#FDDA24", fontWeight: "bold" }}>{value.toFixed(2)}</span>
                ) : (
                  String(value ?? "-")
                ),
                <span key="name" style={{ color: "#a1a1aa" }}>{String(name)}</span>,
              ]}
              labelFormatter={(_, payload) => {
                if (!payload || !payload.length) return "";
                return (
                  <div style={{ color: "#EF3340", fontWeight: "900", marginBottom: "4px", fontSize: "14px" }}>
                    {payload[0].payload.driver}
                  </div>
                );
              }}
            />
            
            <Scatter data={chartData} fill="#EF3340">
              <ErrorBar 
                dataKey="lowError" 
                width={4} 
                strokeWidth={2} 
                stroke="#FDDA24"
                direction="y" 
              />
              <ErrorBar 
                dataKey="highError" 
                width={4} 
                strokeWidth={2} 
                stroke="#00D27F" 
                direction="y" 
              />
            </Scatter>
          </ScatterChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
