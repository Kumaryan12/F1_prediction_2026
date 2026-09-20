from pathlib import Path
from datetime import datetime, timezone
import subprocess
import pandas as pd


REGISTRY_PATH = Path("prediction_logs/prediction_registry.csv")


def get_git_commit_hash() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            text=True,
        ).strip()
    except Exception:
        return "unknown"


def log_prediction_run(
    year: int,
    gp: str,
    stage: str,
    model_version: str,
    feature_set_version: str,
    data_cutoff: str,
    predicted_winner: str,
    prediction_file_path: str,
    dashboard_url: str = "",
):
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)

    timestamp_utc = datetime.now(timezone.utc).isoformat()

    row = {
        "prediction_id": f"{year}_{gp}_{stage}_{timestamp_utc}",
        "year": year,
        "gp": gp,
        "stage": stage,
        "timestamp_utc": timestamp_utc,
        "model_version": model_version,
        "feature_set_version": feature_set_version,
        "data_cutoff": data_cutoff,
        "git_commit_hash": get_git_commit_hash(),
        "predicted_winner": predicted_winner,
        "actual_winner": "",
        "winner_correct": "",
        "prediction_file_path": prediction_file_path,
        "dashboard_url": dashboard_url,
    }

    if REGISTRY_PATH.exists() and REGISTRY_PATH.stat().st_size > 0:
        df = pd.read_csv(REGISTRY_PATH)
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    else:
        df = pd.DataFrame([row])

    df.to_csv(REGISTRY_PATH, index=False)

    return row