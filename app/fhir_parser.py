from datetime import date
from typing import Any

LOINC_BP_SYS = "8480-6"
LOINC_BP_DIA = "8462-4"
LOINC_BMI = "39156-5"

def codes(item: dict[str, Any]) -> set[str]:
    return {str(x["code"]) for x in (item.get("code") or {}).get("coding", [])
            if x.get("system") == "http://loinc.org" and x.get("code")}

def quantity(item: dict[str, Any], expected_unit: str | None = None) -> float | None:
    q = item.get("valueQuantity") or {}
    if q.get("value") is None:
        return None
    if expected_unit and q.get("unit") != expected_unit:
        return None
    try:
        return float(q["value"])
    except (TypeError, ValueError):
        return None

def extract_patient_features(bundle: dict[str, Any]) -> dict[str, Any]:
    if bundle.get("resourceType") != "Bundle":
        raise ValueError("Expected a FHIR R4 Bundle resource.")
    resources = [e.get("resource", {}) for e in bundle.get("entry", [])]
    patients = [r for r in resources if r.get("resourceType") == "Patient"]
    if len(patients) != 1:
        raise ValueError("This demo expects exactly one Patient in the Bundle.")
    p = patients[0]
    pid = p.get("id")
    if not pid:
        raise ValueError("Patient.id is required.")
    age = None
    if p.get("birthDate"):
        try:
            born = date.fromisoformat(p["birthDate"])
            today = date.today()
            if born > today:
                raise ValueError("Patient.birthDate cannot be in the future.")
            age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
        except (TypeError, ValueError) as exc:
            raise ValueError("Invalid Patient.birthDate.") from exc
    result = dict(patient_id=pid, age=age, systolic_bp=None, diastolic_bp=None, bmi=None)
    for obs in resources:
        if obs.get("resourceType") != "Observation" or obs.get("status") not in {"final", "amended", "corrected"}:
            continue
        reference = (obs.get("subject") or {}).get("reference")
        if reference != f"Patient/{pid}":
            continue
        if LOINC_BMI in codes(obs):
            result["bmi"] = quantity(obs, "kg/m2")
        # Blood pressure is represented by component measurements in FHIR R4.
        for component in obs.get("component", []) or []:
            cc = codes(component)
            if LOINC_BP_SYS in cc:
                result["systolic_bp"] = quantity(component, "mmHg")
            if LOINC_BP_DIA in cc:
                result["diastolic_bp"] = quantity(component, "mmHg")
    return result
