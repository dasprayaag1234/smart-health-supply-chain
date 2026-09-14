from fastapi import FastAPI, HTTPException
from app import data_loader
from app import risk_scorer
from app import redistribution

app = FastAPI(title="Smart Health & Supply Chain API")

@app.get("/")
def root():
    return {"message": "Smart Health & Supply Chain API is running"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/facilities")
def list_facilities():
    return data_loader.get_all_facilities()

@app.get("/facilities/{facility_id}")
def get_facility(facility_id: str):
    facility = data_loader.get_facility_by_id(facility_id)
    if facility is None:
        raise HTTPException(status_code=404, detail="Facility not found")
    return facility

@app.get("/facilities/{facility_id}/stock")
def get_facility_stock(facility_id: str):
    return data_loader.get_stock_for_facility(facility_id)

@app.get("/stock/critical")
def critical_stock(limit: int = 50):
    return data_loader.get_critical_stock(limit)

@app.get("/medicines")
def list_medicines():
    return data_loader.get_all_medicines()

@app.get("/risk/ranked")
def ranked_risk(limit: int = 100):
    return risk_scorer.get_risk_ranked_stockouts(limit)

@app.get("/redistribution/recommendations")
def redistribution_recommendations(limit: int = 50):
    return redistribution.get_redistribution_recommendations(limit)