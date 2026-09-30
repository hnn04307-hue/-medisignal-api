from typing import Optional
from pydantic import BaseModel, Field

class ExtractedFeatures(BaseModel):
    patient_id: str
    age: Optional[int] = None
    systolic_bp: Optional[float] = None
    diastolic_bp: Optional[float] = None
    bmi: Optional[float] = None

class TriggeredSignal(BaseModel):
    code: str
    label: str
    reason: str

class SignalResponse(BaseModel):
    project: str = "MediSignal API"
    ruleset_version: str = "demo-0.1"
    patient_id: str
    signal_level: str = Field(description="Illustrative, non-clinical signal grouping")
    signal_count: int
    extracted_features: ExtractedFeatures
    triggered_signals: list[TriggeredSignal]
    disclaimer: str
