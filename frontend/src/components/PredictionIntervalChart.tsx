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
    <div className="rounded-3xl border border-white/10 bg-zinc-900/70 p-5 shadow-[0_10px_40px_rgba(0,0,0,0.35)] backdrop-blur-xl">
      <div className="mb-4">
        <h3 className="text-xl font-semibold text-white">
          Prediction Interval View
        </h3>
        <p className="text-sm text-zinc-400">
          Lower predicted finish is better. Error bars show the 68% range.
        </p>
      </div>

      <div className="h-[420px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 10 }}>
            <CartesianGrid stroke="rgba(255,255,255,0.08)" />
            <XAxis
              type="number"
              dataKey="pred_rank"
              domain={[1, 10]}
              tick={{ fill: "#a1a1aa", fontSize: 12 }}
              tickLine={false}
              axisLine={{ stroke: "rgba(255,255,255,0.12)" }}
              label={{
                value: "Predicted Rank",
                position: "insideBottom",
                offset: -10,
                fill: "#a1a1aa",
              }}
            />
            <YAxis
              type="number"
              dataKey="pred_finish"
              reversed
              domain={[10, 1]}
              tick={{ fill: "#a1a1aa", fontSize: 12 }}
              tickLine={false}
              axisLine={{ stroke: "rgba(255,255,255,0.12)" }}
              label={{
                value: "Predicted Finish",
                angle: -90,
                position: "insideLeft",
                fill: "#a1a1aa",
              }}
            />
            <Tooltip
  cursor={{ stroke: "rgba(255,255,255,0.15)" }}
  contentStyle={{
    background: "#111827",
    border: "1px solid rgba(255,255,255,0.1)",
    borderRadius: 16,
    color: "white",
  }}
  formatter={(value, name) => [
    typeof value === "number" ? value.toFixed(2) : String(value ?? "-"),
    String(name),
  ]}
  labelFormatter={(_, payload) => {
    if (!payload || !payload.length) return "";
    return payload[0].payload.driver;
  }}
/>
            <Scatter data={chartData} fill="#60a5fa">
              <ErrorBar dataKey="lowError" width={0} strokeWidth={2} stroke="#93c5fd" direction="y" />
              <ErrorBar dataKey="highError" width={0} strokeWidth={2} stroke="#93c5fd" direction="y" />
            </Scatter>
          </ScatterChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}