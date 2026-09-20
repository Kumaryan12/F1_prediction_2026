import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def calibration_table(
    df: pd.DataFrame,
    prob_col: str,
    event_col: str,
    n_bins: int = 10,
) -> pd.DataFrame:
    d = df[[prob_col, event_col]].dropna().copy()
    d["bin"] = pd.cut(d[prob_col], bins=np.linspace(0, 1, n_bins + 1), include_lowest=True)

    table = (
        d.groupby("bin", observed=False)
        .agg(
            mean_pred_prob=(prob_col, "mean"),
            observed_rate=(event_col, "mean"),
            count=(event_col, "size"),
        )
        .reset_index()
    )

    return table


def plot_calibration(
    df: pd.DataFrame,
    prob_col: str,
    event_col: str,
    output_path: str,
    title: str,
    n_bins: int = 10,
):
    table = calibration_table(df, prob_col, event_col, n_bins=n_bins)

    plt.figure(figsize=(7, 6))
    plt.plot([0, 1], [0, 1], linestyle="--", label="Perfect calibration")
    plt.plot(
        table["mean_pred_prob"],
        table["observed_rate"],
        marker="o",
        label=prob_col,
    )

    plt.xlabel("Mean predicted probability")
    plt.ylabel("Observed frequency")
    plt.title(title)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()

    return table