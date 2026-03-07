from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .schemas import (
    HealthResponse,
    PredictionRow,
    PredictionsResponse,
    DriverResponse,
    SummaryResponse,
)

app = FastAPI(title="F1 Prediction API", version="1.1.0")

# Allow frontend during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this later for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

PREDICTIONS_PATH = DATA_DIR / "predicted_order.csv"
TREE_IMPORTANCE_PATH = DATA_DIR / "feature_importance_tree.csv"
PERM_IMPORTANCE_PATH = DATA_DIR / "feature_importance_permutation.csv"
METRICS_PATH = DATA_DIR / "model_metrics.json"

DEFAULT_RACE_NAME = "Australian Grand Prix 2026"


# -------------------------------------------------------------------
# Loaders
# -------------------------------------------------------------------

def load_predictions() -> pd.DataFrame:
    if not PREDICTIONS_PATH.exists():
        raise HTTPException(status_code=404, detail=f"Prediction file not found: {PREDICTIONS_PATH}")

    df = pd.read_csv(PREDICTIONS_PATH)
    df = df.where(pd.notnull(df), None)

    if "pred_rank" in df.columns:
        df = df.sort_values("pred_rank", ascending=True).reset_index(drop=True)

    return df


def load_importance_csv(path: Path, label: str) -> pd.DataFrame:
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"{label} file not found: {path}")

    df = pd.read_csv(path)

    # Handle either:
    # 1) index column unnamed + importance column
    # 2) explicit feature/importance columns
    if "feature" not in df.columns:
        unnamed_cols = [c for c in df.columns if str(c).startswith("Unnamed:")]
        if unnamed_cols:
            df = df.rename(columns={unnamed_cols[0]: "feature"})
        elif len(df.columns) >= 2:
            df = df.rename(columns={df.columns[0]: "feature", df.columns[1]: "importance"})
        else:
            raise HTTPException(status_code=500, detail=f"Could not parse {label} CSV")

    if "importance" not in df.columns:
        non_feature_cols = [c for c in df.columns if c != "feature"]
        if non_feature_cols:
            df = df.rename(columns={non_feature_cols[0]: "importance"})
        else:
            raise HTTPException(status_code=500, detail=f"Missing importance column in {label} CSV")

    df["importance"] = pd.to_numeric(df["importance"], errors="coerce")
    df = df.dropna(subset=["importance"]).sort_values("importance", ascending=False).reset_index(drop=True)
    return df[["feature", "importance"]]


def load_metrics() -> dict:
    """
    Preferred source: model_metrics.json
    Fallback: minimal metrics derived from predictions.
    """
    if METRICS_PATH.exists():
        try:
            with open(METRICS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to parse metrics JSON: {e}")

    # Fallback if no JSON exists yet
    df = load_predictions()
    avg_pred_std = float(pd.to_numeric(df["pred_std"], errors="coerce").mean()) if "pred_std" in df.columns else None

    return {
        "race": DEFAULT_RACE_NAME,
        "train_rows": None,
        "latest_event": None,
        "oob_r2": None,
        "oob_mae": None,
        "oob_rmse": None,
        "avg_pred_std": avg_pred_std,
        "note": "model_metrics.json not found; returning fallback metrics only",
    }


# -------------------------------------------------------------------
# Basic endpoints
# -------------------------------------------------------------------

@app.get("/")
def root():
    return {
        "message": "F1 Prediction API is running",
        "docs": "/docs",
        "race": DEFAULT_RACE_NAME,
    }


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse()


# -------------------------------------------------------------------
# Prediction endpoints
# -------------------------------------------------------------------

@app.get("/predictions/latest", response_model=PredictionsResponse)
def get_latest_predictions() -> PredictionsResponse:
    df = load_predictions()
    rows = [PredictionRow(**row) for row in df.to_dict(orient="records")]
    return PredictionsResponse(
        race=DEFAULT_RACE_NAME,
        total_rows=len(rows),
        rows=rows,
    )


@app.get("/predictions/top10", response_model=PredictionsResponse)
def get_top10_predictions() -> PredictionsResponse:
    df = load_predictions().head(10)
    rows = [PredictionRow(**row) for row in df.to_dict(orient="records")]
    return PredictionsResponse(
        race=DEFAULT_RACE_NAME,
        total_rows=len(rows),
        rows=rows,
    )


@app.get("/drivers/{driver_code}", response_model=DriverResponse)
def get_driver_prediction(driver_code: str) -> DriverResponse:
    df = load_predictions()
    driver_code = driver_code.upper().strip()

    match = df[df["driver"].astype(str).str.upper() == driver_code]
    if match.empty:
        raise HTTPException(status_code=404, detail=f"Driver '{driver_code}' not found")

    row = match.iloc[0].to_dict()
    return DriverResponse(row=PredictionRow(**row))


@app.get("/summary", response_model=SummaryResponse)
def get_summary() -> SummaryResponse:
    df = load_predictions()

    if df.empty:
        raise HTTPException(status_code=404, detail="No predictions available")

    podium_df = df.sort_values("pred_rank").head(3)
    winner = podium_df.iloc[0]["driver"]

    team_scores = (
        df.groupby("team", dropna=False)["pred_finish"]
        .mean()
        .sort_values()
    )
    best_team = str(team_scores.index[0])

    avg_pred_std = float(pd.to_numeric(df["pred_std"], errors="coerce").mean())

    return SummaryResponse(
        race=DEFAULT_RACE_NAME,
        total_drivers=len(df),
        predicted_winner=str(winner),
        predicted_podium=podium_df["driver"].astype(str).tolist(),
        best_team=best_team,
        avg_pred_std=avg_pred_std,
    )


@app.get("/predictions/search", response_model=PredictionsResponse)
def search_predictions(
    team: Optional[str] = Query(default=None),
    min_podium: Optional[float] = Query(default=None, ge=0.0, le=1.0),
) -> PredictionsResponse:
    df = load_predictions()

    if team:
        df = df[df["team"].astype(str).str.lower() == team.lower()]

    if min_podium is not None and "p_podium" in df.columns:
        df = df[pd.to_numeric(df["p_podium"], errors="coerce") >= min_podium]

    rows = [PredictionRow(**row) for row in df.to_dict(orient="records")]
    return PredictionsResponse(
        race=DEFAULT_RACE_NAME,
        total_rows=len(rows),
        rows=rows,
    )


# -------------------------------------------------------------------
# Metrics + feature importance endpoints
# -------------------------------------------------------------------

@app.get("/metrics")
def get_metrics():
    return load_metrics()


@app.get("/feature-importance/tree")
def get_tree_importance(top_n: int = Query(default=20, ge=1, le=200)):
    df = load_importance_csv(TREE_IMPORTANCE_PATH, "tree feature importance")
    df = df.head(top_n)

    return {
        "race": DEFAULT_RACE_NAME,
        "kind": "tree",
        "total_rows": int(len(df)),
        "rows": df.to_dict(orient="records"),
    }


@app.get("/feature-importance/permutation")
def get_permutation_importance(top_n: int = Query(default=20, ge=1, le=200)):
    df = load_importance_csv(PERM_IMPORTANCE_PATH, "permutation feature importance")
    df = df.head(top_n)

    return {
        "race": DEFAULT_RACE_NAME,
        "kind": "permutation",
        "total_rows": int(len(df)),
        "rows": df.to_dict(orient="records"),
    }