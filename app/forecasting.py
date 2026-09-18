"""
Lightweight demand/depletion forecasting.

IMPORTANT: No public dataset provides real historical stock-level time
series for Indian PHCs/CHCs (confirmed during data collection phase).
This module generates an illustrative 14-day trend leading up to today's
known (simulated) stock level, and projects a depletion date using a
simple linear consumption-rate estimate. This is clearly not a trained
ML forecasting model - it's a transparent, explainable projection, and
is labeled as such in every response.
"""

import random
from datetime import datetime, timedelta

random.seed(7)


def generate_trend_and_projection(current_quantity: int, reorder_threshold: int,
                                    facility_id: str, medicine_name: str):
    """Generates a 14-day illustrative trend ending at current_quantity,
    plus a simple depletion projection."""
    # seed randomness per facility+medicine so results are stable across calls
    seed_val = hash(f"{facility_id}-{medicine_name}") % (10**6)
    rng = random.Random(seed_val)

    # estimate a plausible daily consumption rate from the reorder threshold
    # (thresholds are typically set at ~25% of a facility's baseline stock,
    # so we back-calculate a rough daily usage figure from that)
    daily_consumption = max(1, round(reorder_threshold / 30))

    trend = []
    quantity = current_quantity + daily_consumption * 13
    today = datetime.now()
    for i in range(14):
        day = today - timedelta(days=13 - i)
        noise = rng.randint(-2, 2)
        quantity = max(0, quantity - daily_consumption + noise)
        trend.append({
            "date": day.strftime("%Y-%m-%d"),
            "quantity": int(quantity) if i < 13 else current_quantity
        })

    # project days remaining until stock hits zero at current consumption rate
    days_remaining = round(current_quantity / daily_consumption, 1) if daily_consumption > 0 else None
    projected_stockout_date = (today + timedelta(days=days_remaining)).strftime("%Y-%m-%d") if days_remaining is not None else None

    return {
        "trend": trend,
        "estimated_daily_consumption": daily_consumption,
        "projected_days_remaining": days_remaining,
        "projected_stockout_date": projected_stockout_date,
        "methodology_note": "Illustrative projection based on reorder-threshold-derived consumption rate. Not based on real historical stock data, as no public dataset provides facility-level time-series stock records.",
    }
