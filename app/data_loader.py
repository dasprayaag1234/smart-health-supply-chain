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