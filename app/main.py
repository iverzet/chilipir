from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Literal

app = FastAPI(title="Chilipir", version="0.1.0")

class Listing(BaseModel):
    source: Literal["olx"] = "olx"
    url: str
    title: str
    category: Literal["arta", "foto"]
    price_ron: float = Field(ge=0)
    reference_price_ron: float = Field(gt=0)
    confidence: float = Field(ge=0, le=1)

@app.get("/health")
def health():
    return {"status": "ok", "collector": "not_configured"}

@app.post("/evaluate")
def evaluate(item: Listing):
    discount = max(0, (item.reference_price_ron - item.price_ron) / item.reference_price_ron)
    score = round(100 * min(1, discount) * item.confidence)
    return {
        "url": item.url,
        "discount_pct": round(100 * discount, 1),
        "score": score,
        "candidate": score >= 25 and item.confidence >= 0.6,
        "warning": "Reference price is supplied, not independently verified; this is not an appraisal.",
    }

@app.get("/deals")
def deals():
    return {"items": [], "status": "no_authorized_olx_feed", "note": "No live OLX access is configured."}
