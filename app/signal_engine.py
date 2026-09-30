from app.schemas import ExtractedFeatures, SignalResponse, TriggeredSignal

# Educational demonstration thresholds, not a validated medical scoring rule.
THRESHOLDS = {"age_context": 65, "systolic": 140, "diastolic": 90, "bmi": 30}
DISCLAIMER = (
    "Research/education prototype using synthetic data and illustrative rules only. "
    "This output is not a diagnosis, validated risk score, treatment recommendation, "
    "or clinical decision-support result."
)

def evaluate_signals(features: dict) -> SignalResponse:
    f = ExtractedFeatures(**features)
    flags = []
    if f.age is not None and f.age >= THRESHOLDS["age_context"]:
        flags.append(TriggeredSignal(
            code="AGE_CONTEXT", label="Age context",
            reason=f"Age {f.age} meets the illustrative 65+ context flag."))
    if ((f.systolic_bp is not None and f.systolic_bp >= THRESHOLDS["systolic"])
        or (f.diastolic_bp is not None and f.diastolic_bp >= THRESHOLDS["diastolic"])):
        flags.append(TriggeredSignal(
            code="BP_SIGNAL", label="Blood pressure signal",
            reason="At least one extracted BP value meets an illustrative threshold."))
    if f.bmi is not None and f.bmi >= THRESHOLDS["bmi"]:
        flags.append(TriggeredSignal(
            code="BMI_SIGNAL", label="BMI signal",
            reason="Extracted BMI meets the illustrative demo threshold."))
    # Missing measurements are reported in extracted_features, not interpreted as normal.
    level = "no-flags-observed" if len(flags) == 0 else (
        "one-demo-flag" if len(flags) == 1 else "multiple-demo-flags")
    return SignalResponse(
        patient_id=f.patient_id, signal_level=level, signal_count=len(flags),
        extracted_features=f, triggered_signals=flags, disclaimer=DISCLAIMER)
