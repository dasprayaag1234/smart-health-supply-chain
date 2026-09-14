"""
Rule-based redistribution recommender.

For each facility with Critical or Low stock of a medicine, finds the
best candidate facility (same state, healthy surplus of that medicine)
to redistribute units from - prioritizing facilities with the largest
surplus first.

This is deliberately rule-based rather than a full linear-programming
optimizer (e.g. PuLP), given project time constraints - it's simpler to
build, easier to explain in a demo, and still produces genuinely useful,
defensible recommendations.
"""

import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"


def get_redistribution_recommendations(limit: int = 50):
    stock_df = pd.read_csv(DATA_DIR / "stock_records.csv")
    facilities_df = pd.read_csv(DATA_DIR / "facilities.csv")

    merged = stock_df.merge(
        facilities_df[["facility_id", "facility_name", "district", "state"]],
        on="facility_id", how="left"
    )

    needy = merged[merged["stock_status"].isin(["Critical", "Low"])].copy()
    needy["shortfall"] = needy["reorder_threshold"] - needy["current_quantity"]

    # surplus = healthy facilities with quantity well above their own threshold
    healthy = merged[merged["stock_status"] == "Healthy"].copy()
    healthy["surplus"] = healthy["current_quantity"] - healthy["reorder_threshold"]
    healthy = healthy[healthy["surplus"] > 0]

    recommendations = []
    # sort needy by biggest shortfall first (most urgent gets matched first)
    needy = needy.sort_values("shortfall", ascending=False)

    for _, need_row in needy.iterrows():
        candidates = healthy[
            (healthy["medicine_name"] == need_row["medicine_name"]) &
            (healthy["state"] == need_row["state"]) &
            (healthy["facility_id"] != need_row["facility_id"])
        ].sort_values("surplus", ascending=False)

        if candidates.empty:
            continue

        best = candidates.iloc[0]
        transfer_qty = int(min(best["surplus"], need_row["shortfall"]))
        if transfer_qty <= 0:
            continue

        recommendations.append({
            "medicine_name": need_row["medicine_name"],
            "from_facility_id": best["facility_id"],
            "from_facility_name": best["facility_name"],
            "from_district": best["district"],
            "to_facility_id": need_row["facility_id"],
            "to_facility_name": need_row["facility_name"],
            "to_district": need_row["district"],
            "state": need_row["state"],
            "recommended_transfer_quantity": transfer_qty,
            "to_facility_stock_status": need_row["stock_status"],
        })

        if len(recommendations) >= limit:
            break

    return recommendations