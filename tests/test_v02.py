import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.research_pipeline import evaluate,provenance
from research.run_experiment import profiles,canonical,perturb,run_experiment,PERTURBATIONS

client=TestClient(app)

def test_health():assert client.get("/health").json()["version"]=="0.2.0"
def test_results():
    x=client.get("/v1/research/results").json()
    assert x["design"]["unique_patient_cases"]==112 and x["design"]["pipeline_evaluations"]==336
def test_trace():
    x=client.post("/v1/research/trace",json=perturb(profiles()[0],"duplicate_conflict")).json()
    assert x["quality_checks"]["decision"]=="hold"
def test_original_signal_endpoint():
    sample=json.loads((Path(__file__).parents[1]/"data"/"sample_fhir_bundle.json").read_text())
    assert client.post("/v1/signals/from-fhir",json=sample).status_code==200

@pytest.mark.parametrize("p",profiles(),ids=lambda p:p["id"])
def test_all_clean_profiles_stable(p):
    b=canonical(p)
    a=evaluate(b,"raw");s=evaluate(b,"standardized");v=evaluate(b,"validated")
    assert a["signals"]==s["signals"]==v["signals"] and v["decision"]=="proceed"

@pytest.mark.parametrize("c",["clean","unit_variation","duplicate_same"])
def test_processable_cases_proceed(c):
    p=next(x for x in profiles() if x["age"]==70 and x["sys"]==150 and x["dia"]==95 and x["bmi"]==32)
    assert evaluate(perturb(p,c),"validated")["decision"]=="proceed"

@pytest.mark.parametrize("c,fragment",[("missing","MISSING_BMI"),("unsupported_unit","UNSUPPORTED_UNIT"),
("duplicate_conflict","CONFLICTING_DUPLICATE"),("implausible","OUT_OF_TECHNICAL_RANGE")])
def test_quality_faults_hold(c,fragment):
    o=evaluate(perturb(profiles()[0],c),"validated")
    assert o["decision"]=="hold" and any(fragment in w["code"] for w in o["warnings"])

def test_unit_standardization_recovers_signal():
    p=next(x for x in profiles() if x["age"]==50 and x["sys"]==150 and x["dia"]==75 and x["bmi"]==24)
    b=perturb(p,"unit_variation")
    assert "BP_SIGNAL" not in evaluate(b,"raw")["signals"]
    assert "BP_SIGNAL" in evaluate(b,"standardized")["signals"]

def test_missing_is_silent_error_without_hold():
    p=next(x for x in profiles() if x["age"]==50 and x["sys"]==125 and x["dia"]==75 and x["bmi"]==32)
    b=perturb(p,"missing")
    assert "BMI_SIGNAL" not in evaluate(b,"standardized")["signals"]
    assert evaluate(b,"validated")["decision"]=="hold"

def test_provenance_has_all_stages():
    x=provenance(perturb(profiles()[0],"unit_variation"))
    assert x["raw_measurements"] and x["normalization"] and len(x["rule_evaluation"])==3
    assert set(x["pipeline_outputs"])=={"raw","standardized","validated"}

def test_experiment_metrics():
    x=run_experiment();by={s["pipeline"]:s for s in x["summary"]}
    assert by["raw"]["silent_error_rate"]==0.3214
    assert by["standardized"]["silent_error_rate"]==0.2143
    assert by["validated"]["silent_error_rate"]==0.0
    assert by["validated"]["hold_rate"]==0.5714
    assert by["validated"]["agreement_among_decided"]==1.0

@pytest.mark.parametrize("c",PERTURBATIONS)
def test_each_perturbation_has_sixteen_cases(c):
    x=run_experiment()
    for m in ("raw","standardized","validated"):
        row=next(b for b in x["breakdown"] if b["pipeline"]==m and b["perturbation"]==c)
        assert row["n"]==16

def test_three_pipeline_summaries_present():
    assert {x["pipeline"] for x in run_experiment()["summary"]}=={"raw","standardized","validated"}
