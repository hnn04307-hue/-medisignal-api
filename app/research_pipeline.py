from __future__ import annotations
from dataclasses import dataclass
from datetime import date

REFERENCE_DATE=date(2026,10,1)
TH={"age":65,"sys":140.0,"dia":90.0,"bmi":30.0}
RANGES={"sys":(50.0,300.0),"dia":(30.0,200.0),"bmi":(10.0,80.0)}
TOL={"sys":10.0,"dia":10.0,"bmi":2.0}
LOINC={"sys":"8480-6","dia":"8462-4","bmi":"39156-5"}
DISCLAIMER=("Synthetic-data research prototype. Results quantify software behavior under "
            "predefined perturbations; they are not estimates of clinical performance, "
            "diagnostic accuracy, or real-world error prevalence.")

@dataclass
class M:
    kind:str
    oid:str
    value:float
    unit:str
    code:str|None=None

def _codes(x):
    return {str(c["code"]) for c in (x.get("code") or {}).get("coding",[]) if c.get("code")}

def _q(x):
    q=x.get("valueQuantity") or {}
    if q.get("value") is None:return None
    try:v=float(q["value"])
    except (TypeError,ValueError):return None
    return v,str(q.get("unit") or q.get("code") or ""),q.get("code")

def parse(bundle,reference_date=REFERENCE_DATE):
    if bundle.get("resourceType")!="Bundle":raise ValueError("Expected FHIR R4 Bundle.")
    rs=[e.get("resource") or {} for e in bundle.get("entry",[])]
    ps=[r for r in rs if r.get("resourceType")=="Patient"]
    if len(ps)!=1:raise ValueError("Synthetic study expects exactly one Patient.")
    p=ps[0]; pid=p.get("id")
    if not pid:raise ValueError("Patient.id is required.")
    age=None
    if p.get("birthDate"):
        born=date.fromisoformat(p["birthDate"][:10])
        if born>reference_date:raise ValueError("Patient.birthDate cannot be in the future.")
        age=reference_date.year-born.year-((reference_date.month,reference_date.day)<(born.month,born.day))
    ms={"sys":[],"dia":[],"bmi":[]}
    for o in rs:
        if o.get("resourceType")!="Observation" or o.get("status") not in {"final","amended","corrected"}:continue
        ref=(o.get("subject") or {}).get("reference")
        if ref and ref!=f"Patient/{pid}":continue
        oid=str(o.get("id") or "unnamed")
        if LOINC["bmi"] in _codes(o):
            q=_q(o)
            if q:ms["bmi"].append(M("bmi",oid,*q))
        for i,c in enumerate(o.get("component",[]) or []):
            q=_q(c)
            if not q:continue
            cc=_codes(c)
            if LOINC["sys"] in cc:ms["sys"].append(M("sys",f"{oid}#c{i}",*q))
            if LOINC["dia"] in cc:ms["dia"].append(M("dia",f"{oid}#c{i}",*q))
    return {"patient_id":pid,"age":age,"m":ms}

def norm(m):
    u=(m.code or m.unit or "").strip()
    out={"kind":m.kind,"observation_id":m.oid,"raw_value":m.value,"raw_unit":m.unit,
         "raw_code":m.code,"normalized_value":None,"normalized_unit":None,
         "status":"unsupported_unit","conversion":None}
    if m.kind in {"sys","dia"}:
        if u in {"mmHg","mm[Hg]"} or m.unit=="mmHg":
            out.update(normalized_value=m.value,normalized_unit="mmHg",status="identity",conversion="identity")
        elif u=="kPa" or m.unit=="kPa":
            out.update(normalized_value=m.value*7.50062,normalized_unit="mmHg",
                       status="converted",conversion="kPa × 7.50062 → mmHg")
    elif m.kind=="bmi" and (u in {"kg/m2","kg/m^2","kg/m²"} or m.unit in {"kg/m2","kg/m^2","kg/m²"}):
        out.update(normalized_value=m.value,normalized_unit="kg/m2",
                   status="identity",conversion="normalize BMI unit label")
    return out

def signals(age,sys=None,dia=None,bmi=None):
    s=set()
    if age is not None and age>=TH["age"]:s.add("AGE_CONTEXT")
    if (sys is not None and sys>=TH["sys"]) or (dia is not None and dia>=TH["dia"]):s.add("BP_SIGNAL")
    if bmi is not None and bmi>=TH["bmi"]:s.add("BMI_SIGNAL")
    return sorted(s)

def std_values(raw):
    vals={}; trace=[]
    for k,items in raw["m"].items():
        ns=[norm(x) for x in items];trace.extend(ns)
        ok=[x["normalized_value"] for x in ns if x["normalized_value"] is not None]
        vals[k]=ok[0] if ok else None
    return vals,trace

def warnings(raw,trace):
    by={k:[] for k in raw["m"]}
    for x in trace:by[x["kind"]].append(x)
    ws=[]
    for k in ("sys","dia","bmi"):
        if not raw["m"][k]:
            ws.append({"code":f"MISSING_{k.upper()}","detail":f"No {k} observation found."});continue
        if any(x["normalized_value"] is None for x in by[k]):
            ws.append({"code":f"UNSUPPORTED_UNIT_{k.upper()}","detail":f"{k} could not be normalized."})
        vs=[x["normalized_value"] for x in by[k] if x["normalized_value"] is not None]
        if not vs:continue
        lo,hi=RANGES[k]
        if any(v<lo or v>hi for v in vs):
            ws.append({"code":f"OUT_OF_TECHNICAL_RANGE_{k.upper()}","detail":f"{k} violates the synthetic-study processability range."})
        if len(vs)>1 and max(vs)-min(vs)>TOL[k]:
            ws.append({"code":f"CONFLICTING_DUPLICATE_{k.upper()}","detail":f"Duplicate {k} values disagree beyond tolerance."})
    return ws

def evaluate(bundle,mode,reference_date=REFERENCE_DATE):
    raw=parse(bundle,reference_date)
    if mode=="raw":
        v={k:(xs[0].value if xs else None) for k,xs in raw["m"].items()}
        return {"mode":mode,"decision":"proceed","signals":signals(raw["age"],v["sys"],v["dia"],v["bmi"]),"warnings":[]}
    v,t=std_values(raw)
    if mode=="standardized":
        return {"mode":mode,"decision":"proceed","signals":signals(raw["age"],v["sys"],v["dia"],v["bmi"]),"warnings":[],"normalization":t}
    if mode!="validated":raise ValueError("mode must be raw, standardized, or validated")
    ws=warnings(raw,t)
    return {"mode":mode,"decision":"hold" if ws else "proceed",
            "signals":[] if ws else signals(raw["age"],v["sys"],v["dia"],v["bmi"]),
            "warnings":ws,"normalization":t}

def provenance(bundle,reference_date=REFERENCE_DATE):
    raw=parse(bundle,reference_date); v,t=std_values(raw); ws=warnings(raw,t)
    rms=[{"kind":k,"observation_id":m.oid,"value":m.value,"unit":m.unit,"code":m.code}
         for k,xs in raw["m"].items() for m in xs]
    rules=[
      {"rule":"AGE_CONTEXT","input":raw["age"],"threshold":f">= {TH['age']}",
       "triggered":raw["age"] is not None and raw["age"]>=TH["age"]},
      {"rule":"BP_SIGNAL","input":{"sys":v["sys"],"dia":v["dia"]},
       "threshold":f"sys >= {TH['sys']} OR dia >= {TH['dia']}",
       "triggered":(v["sys"] is not None and v["sys"]>=TH["sys"]) or (v["dia"] is not None and v["dia"]>=TH["dia"])},
      {"rule":"BMI_SIGNAL","input":v["bmi"],"threshold":f">= {TH['bmi']}",
       "triggered":v["bmi"] is not None and v["bmi"]>=TH["bmi"]}]
    return {"patient_id":raw["patient_id"],"reference_date":reference_date.isoformat(),
            "raw_measurements":rms,"normalization":t,
            "quality_checks":{"decision":"hold" if ws else "proceed","warnings":ws},
            "rule_evaluation":rules,
            "pipeline_outputs":{m:evaluate(bundle,m,reference_date) for m in ("raw","standardized","validated")},
            "disclaimer":DISCLAIMER}
