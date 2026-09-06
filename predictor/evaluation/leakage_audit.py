import pandas as pd


FEATURE_AVAILABILITY = {
    "grid_pos": {
        "pre_fp1": False,
        "post_fp3": False,
        "post_qualifying": True,
        "pre_race": True,
        "notes": "Available only after qualifying/grid confirmation.",
    },

    "sc_prob": {
        "pre_fp1": True,
        "post_fp3": True,
        "post_qualifying": True,
        "pre_race": True,
        "notes": "Historical/circuit prior.",
    },

    "vsc_prob": {
        "pre_fp1": True,
        "post_fp3": True,
        "post_qualifying": True,
        "pre_race": True,
        "notes": "Historical/circuit prior.",
    },

    "pit_loss": {
        "pre_fp1": True,
        "post_fp3": True,
        "post_qualifying": True,
        "pre_race": True,
        "notes": "Circuit prior.",
    },

    "driver_skill_prior": {
        "pre_fp1": True,
        "post_fp3": True,
        "post_qualifying": True,
        "pre_race": True,
        "notes": "Manual/pre-race prior. Must not be edited after result.",
    },

    "team_prior_strength": {
        "pre_fp1": True,
        "post_fp3": True,
        "post_qualifying": True,
        "pre_race": True,
        "notes": "Manual/pre-race prior. Must not be edited after result.",
    },

    "drv_form3": {
        "pre_fp1": True,
        "post_fp3": True,
        "post_qualifying": True,
        "pre_race": True,
        "notes": "Safe only if computed using shift(1).",
    },

    "team_form3": {
        "pre_fp1": True,
        "post_fp3": True,
        "post_qualifying": True,
        "pre_race": True,
        "notes": "Safe only if computed using shift(1).",
    },

    "finish_pos": {
        "pre_fp1": False,
        "post_fp3": False,
        "post_qualifying": False,
        "pre_race": False,
        "notes": "Target variable. Never allowed as input feature.",
    },
}


def build_leakage_audit_table(feature_list: list[str]) -> pd.DataFrame:
    rows = []

    for feat in feature_list:
        info = FEATURE_AVAILABILITY.get(feat, None)

        if info is None:
            rows.append({
                "feature": feat,
                "pre_fp1": "UNKNOWN",
                "post_fp3": "UNKNOWN",
                "post_qualifying": "UNKNOWN",
                "pre_race": "UNKNOWN",
                "risk": "REVIEW_REQUIRED",
                "notes": "Feature not registered in leakage audit table.",
            })
        else:
            rows.append({
                "feature": feat,
                "pre_fp1": info["pre_fp1"],
                "post_fp3": info["post_fp3"],
                "post_qualifying": info["post_qualifying"],
                "pre_race": info["pre_race"],
                "risk": "BLOCK" if feat == "finish_pos" else "OK",
                "notes": info["notes"],
            })

    return pd.DataFrame(rows)


def save_leakage_audit(feature_list: list[str], output_csv: str):
    df = build_leakage_audit_table(feature_list)
    df.to_csv(output_csv, index=False)
    return df