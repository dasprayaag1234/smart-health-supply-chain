import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"

facilities_df = pd.read_csv(DATA_DIR / "facilities.csv")
stock_df = pd.read_csv(DATA_DIR / "stock_records.csv")
medicines_df = pd.read_csv(DATA_DIR / "essential_medicines_list.csv")


def get_all_facilities():
    return facilities_df.to_dict(orient="records")


def get_facility_by_id(facility_id: str):
    row = facilities_df[facilities_df["facility_id"] == facility_id]
    if row.empty:
        return None
    return row.to_dict(orient="records")[0]


def get_stock_for_facility(facility_id: str):
    rows = stock_df[stock_df["facility_id"] == facility_id]
    return rows.to_dict(orient="records")


def get_critical_stock(limit: int = 50):
    rows = stock_df[stock_df["stock_status"] == "Critical"]
    return rows.head(limit).to_dict(orient="records")


def get_all_medicines():
    return medicines_df.to_dict(orient="records")

def get_summary_stats():
    total_facilities = len(facilities_df)
    total_states = facilities_df["state"].nunique()
    total_districts = facilities_df["district"].nunique()

    critical_count = len(stock_df[stock_df["stock_status"] == "Critical"])
    low_count = len(stock_df[stock_df["stock_status"] == "Low"])
    healthy_count = len(stock_df[stock_df["stock_status"] == "Healthy"])

    facilities_with_critical_stock = stock_df[stock_df["stock_status"] == "Critical"]["facility_id"].nunique()

    return {
        "total_facilities": total_facilities,
        "total_states": total_states,
        "total_districts": total_districts,
        "critical_stock_records": critical_count,
        "low_stock_records": low_count,
        "healthy_stock_records": healthy_count,
        "facilities_with_critical_stock": facilities_with_critical_stock,
    }
