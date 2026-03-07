export type PredictionRow = {
  driver: string;
  team: string;
  grid_pos?: number | null;
  pred_finish: number;
  pred_std: number;
  pred_rank: number;
  pi68_low?: number | null;
  pi68_high?: number | null;
  pi95_low?: number | null;
  pi95_high?: number | null;
  p_top10?: number | null;
  p_podium?: number | null;
  p_rank_pm1?: number | null;
  pred_finish_model?: number | null;
  pred_rank_model?: number | null;
  session_boost?: number | null;
};

export type PredictionsResponse = {
  race: string;
  total_rows: number;
  rows: PredictionRow[];
};

export type SummaryResponse = {
  race: string;
  total_drivers: number;
  predicted_winner: string;
  predicted_podium: string[];
  best_team: string;
  avg_pred_std: number;
};