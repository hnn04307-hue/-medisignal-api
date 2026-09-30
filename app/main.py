from pathlib import Path

from fastapi import Body, FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles

from app.fhir_parser import extract_patient_features
from app.schemas import SignalResponse
from app.signal_engine import evaluate_signals

BASE_DIR = Path(__file__).resolve().parent.parent
WEB_DIR = BASE_DIR / "web"

app = FastAPI(
    title="MediSignal API",
    version="0.1.0",
    description=(
        "FHIR R4 synthetic-data signal stratification prototype. "
        "Research/education only; not for diagnosis or clinical use."
    ),
)

EXAMPLE = {
    "resourceType": "Bundle",
    "type": "collection",
    "entry": [
        {"resource": {
            "resourceType": "Patient",
            "id": "synthetic-patient-001",
            "gender": "female",
            "birthDate": "1958-03-10"
        }},
        {"resource": {
            "resourceType": "Observation",
            "id": "bp-001",
            "status": "final",
            "subject": {"reference": "Patient/synthetic-patient-001"},
            "code": {"coding": [{"system": "http://loinc.org", "code": "85354-9"}]},
            "component": [
                {
                    "code": {"coding": [{"system": "http://loinc.org", "code": "8480-6"}]},
                    "valueQuantity": {"value": 152, "unit": "mmHg"}
                },
                {
                    "code": {"coding": [{"system": "http://loinc.org", "code": "8462-4"}]},
                    "valueQuantity": {"value": 92, "unit": "mmHg"}
                }
            ]
        }},
        {"resource": {
            "resourceType": "Observation",
            "id": "bmi-001",
            "status": "final",
            "subject": {"reference": "Patient/synthetic-patient-001"},
            "code": {"coding": [{"system": "http://loinc.org", "code": "39156-5"}]},
            "valueQuantity": {"value": 31.2, "unit": "kg/m2"}
        }}
    ]
}

@app.get("/health", tags=["System"])
def health():
    return {"status": "ok", "service": "MediSignal API", "version": "0.1.0"}

@app.post("/v1/signals/from-fhir", response_model=SignalResponse, tags=["Signals"])
def signals_from_fhir(
    bundle: dict = Body(
        ...,
        openapi_examples={
            "synthetic_patient": {
                "summary": "Synthetic FHIR R4 Bundle",
                "description": "A non-clinical demonstration patient.",
                "value": EXAMPLE,
            }
        },
    )
):
    try:
        features = extract_patient_features(bundle)
        return evaluate_signals(features)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

# Mount the portfolio UI last so API and docs routes take precedence.
app.mount("/", StaticFiles(directory=str(WEB_DIR), html=True), name="web")
