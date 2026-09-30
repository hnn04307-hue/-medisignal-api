import json
from pathlib import Path
from fastapi import Body,FastAPI,HTTPException
from fastapi.staticfiles import StaticFiles
from app.fhir_parser import extract_patient_features
from app.schemas import SignalResponse
from app.signal_engine import evaluate_signals
from app.research_pipeline import provenance
from research.run_experiment import run_experiment

BASE=Path(__file__).resolve().parent.parent
WEB=BASE/"web"
SAMPLE=json.loads((BASE/"data"/"sample_fhir_bundle.json").read_text(encoding="utf-8"))

app=FastAPI(
 title="MediSignal API",version="0.2.0",
 description="FHIR R4 synthetic-data research prototype with reproducible data-quality experiment and provenance trace. Not for clinical use."
)

@app.get("/health",tags=["System"])
def health():
    return {"status":"ok","service":"MediSignal API","version":"0.2.0","research_study":"medisignal-dq-001"}

@app.post("/v1/signals/from-fhir",response_model=SignalResponse,tags=["Signals"])
def signal_endpoint(bundle:dict=Body(...,openapi_examples={"synthetic":{"summary":"Synthetic FHIR R4 Bundle","value":SAMPLE}})):
    try:return evaluate_signals(extract_patient_features(bundle))
    except ValueError as e:raise HTTPException(status_code=422,detail=str(e)) from e

@app.get("/v1/research/results",tags=["Research"])
def research_results():
    return run_experiment()

@app.post("/v1/research/trace",tags=["Research"])
def research_trace(bundle:dict=Body(...,openapi_examples={"synthetic":{"summary":"Synthetic FHIR bundle for provenance tracing","value":SAMPLE}})):
    try:return provenance(bundle)
    except ValueError as e:raise HTTPException(status_code=422,detail=str(e)) from e

app.mount("/",StaticFiles(directory=str(WEB),html=True),name="web")
