from pydantic import BaseModel
from typing import List, Dict, Any


class DriverStats(BaseModel):
    year: int
    points: float
    wins: int
    podiums: int

class TrackHistory(BaseModel):
    track: str
    races_entered: int
    wins: int
    podiums: int

class FastestLap(BaseModel):
    year: int
    fastest_lap_time: str
    compound: str

class YearSummary(BaseModel):
    year: int
    points: float
    races_data: List[Dict[str, Any]]