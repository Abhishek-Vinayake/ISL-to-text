from pydantic import BaseModel
from typing import List, Optional


class Landmark(BaseModel):
    x: float
    y: float
    z: float


class PredictionResponse(BaseModel):
    type: str = "prediction"
    label: Optional[str]
    confidence: float
    landmarks: List[Landmark]
