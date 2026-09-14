"""
Rule-based risk scoring for facility stock levels.

Combines three signals into a single risk score (0-100, higher = more urgent):
1. Stock ratio       - how far current quantity is below the reorder threshold
2. Medicine criticality - some medicines matter more if they run out
   (e.g. Oxytocin, Insulin, vaccines) than others (e.g. general antiseptics)
3. Facility size      - a stock-out at a larger facility (more patients served)
   is weighted slightly more urgent than the same stock-out at a tiny PHC

This is a transparent, explainable scoring rule - not a black-box model -
which is a deliberate choice: it's honest about being rule-based AI logic,
easy to justify to judges, and doesn't require training data we don't have
(a single stock snapshot, not a time series).
"""

import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"

# Medicines where a stock-out is especially dangerous (maternal health,
# emergency/critical care, vaccines) get a higher criticality weight
HIGH_CRITICALITY_MEDICINES = {
    "Oxytocin", "Magnesium Sulphate", "Misoprostol",  # maternal emergencies
    "Insulin (Soluble)", "Adrenaline" , "Hydrocortisone",  # emergency/chronic
    "BCG Vaccine", "DPT Vaccine", "Measles Vaccine",
    "Oral Polio Vaccine", "Hepatitis B Vaccine", "Tetanus Toxoid",  # vaccines
    "Oxygen", "Normal Saline (0.9% NaCl)", "Ringer's Lactate",  # life support
}


def compute_risk_score(current_quantity: int, reorder_threshold: int,
                        medicine_name: str, bed_count: int) -> float:
    """Returns a risk score from 0 (no risk) to 100 (most urgent)."""
    # 1. Stock ratio component (0-60 points): how depleted relative to threshold
    if reorder_threshold <= 0:
        stock_component = 0
    else:
        ratio = current_quantity / reorder_threshold
        # ratio 0 -> full 60 points; ratio >= 1 -> 0 points
        stock_component = max(0, min(60, (1 - ratio) * 60))

    # 2. Medicine criticality component (0-25 points)
    criticality_component = 25 if medicine_name in HIGH_CRITICALITY_MEDICINES else 10

    # 3. Facility size component (0-15 points): bigger facility = slightly higher urgency
    size_component = min(15, (bed_count / 300) * 15)

    total = stock_component + criticality_component + size_component
    return round(min(100, total), 1)


def get_risk_ranked_stockouts(limit: int = 100):
    """Returns the highest-risk stock records, scored and sorted."""
    stock_df = pd.read_csv(DATA_DIR / "stock_records.csv")
    facilities_df = pd.read_csv(DATA_DIR / "facilities.csv")

    # only score records that are Low or Critical - Healthy stock has no risk
    at_risk = stock_df[stock_df["stock_status"].isin(["Low", "Critical"])].copy()

    merged = at_risk.merge(
        facilities_df[["facility_id", "facility_name", "facility_type",
                        "district", "state", "bed_count"]],
        on="facility_id", how="left"
    )

    merged["risk_score"] = merged.apply(
        lambda row: compute_risk_score(
            row["current_quantity"], row["reorder_threshold"],
            row["medicine_name"], row["bed_count"]
        ),
        axis=1
    )

    merged = merged.sort_values("risk_score", ascending=False)
    return merged.head(limit).to_dict(orient="records")