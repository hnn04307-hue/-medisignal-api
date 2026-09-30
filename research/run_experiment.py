import json
from copy import deepcopy
from itertools import product
from app.research_pipeline import REFERENCE_DATE,DISCLAIMER,evaluate

PERTURBATIONS=("clean","unit_variation","duplicate_same","duplicate_conflict","missing","unsupported_unit","implausible")
MODES=("raw","standardized","validated")

def profiles():
    return [dict(id=f"P{i:02d}",age=a,sys=s,dia=d,bmi=b)
            for i,(a,s,d,b) in enumerate(product((50,70),(125.,150.),(75.,95.),(24.,32.)),1)]

def q(v,u,c=None):
    return {"value":v,"unit":u,"system":"http://unitsofmeasure.org","code":c or u}

def canonical(p):
    pid=p["id"]
    return {"resourceType":"Bundle","type":"collection","entry":[
      {"resource":{"resourceType":"Patient","id":pid,"birthDate":f"{REFERENCE_DATE.year-p['age']}-01-01"}},
      {"resource":{"resourceType":"Observation","id":f"{pid}-bp-1","status":"final",
        "subject":{"reference":f"Patient/{pid}"},"code":{"coding":[{"system":"http://loinc.org","code":"85354-9"}]},
        "component":[
          {"code":{"coding":[{"system":"http://loinc.org","code":"8480-6"}]},"valueQuantity":q(p["sys"],"mmHg","mm[Hg]")},
          {"code":{"coding":[{"system":"http://loinc.org","code":"8462-4"}]},"valueQuantity":q(p["dia"],"mmHg","mm[Hg]")}] }},
      {"resource":{"resourceType":"Observation","id":f"{pid}-bmi-1","status":"final",
        "subject":{"reference":f"Patient/{pid}"},"code":{"coding":[{"system":"http://loinc.org","code":"39156-5"}]},
        "valueQuantity":q(p["bmi"],"kg/m2")}}]}

def perturb(p,c):
    b=canonical(p);pid=p["id"];bp=b["entry"][1]["resource"];bmi=b["entry"][2]["resource"]
    if c=="unit_variation":
        bp["component"][0]["valueQuantity"]=q(p["sys"]/7.50062,"kPa")
        bp["component"][1]["valueQuantity"]=q(p["dia"]/7.50062,"kPa")
        bmi["valueQuantity"]=q(p["bmi"],"kg/m^2")
    elif c=="duplicate_same":
        b["entry"] += [deepcopy(b["entry"][1]),deepcopy(b["entry"][2])]
        b["entry"][3]["resource"]["id"]=f"{pid}-bp-duplicate"
        b["entry"][4]["resource"]["id"]=f"{pid}-bmi-duplicate"
    elif c=="duplicate_conflict":
        b["entry"] += [deepcopy(b["entry"][1]),deepcopy(b["entry"][2])]
        b["entry"][3]["resource"]["id"]=f"{pid}-bp-conflict"
        b["entry"][4]["resource"]["id"]=f"{pid}-bmi-conflict"
        b["entry"][3]["resource"]["component"][0]["valueQuantity"]=q(120. if p["sys"]>=140 else 160.,"mmHg","mm[Hg]")
        b["entry"][4]["resource"]["valueQuantity"]=q(24. if p["bmi"]>=30 else 34.,"kg/m2")
    elif c=="missing": b["entry"]=b["entry"][:2]
    elif c=="unsupported_unit":
        bp["component"][0]["valueQuantity"]=q(p["sys"]/51.7149,"psi","[psi]")
        bp["component"][1]["valueQuantity"]=q(p["dia"]/51.7149,"psi","[psi]")
    elif c=="implausible": bp["component"][0]["valueQuantity"]=q(450.,"mmHg","mm[Hg]")
    elif c!="clean": raise ValueError(c)
    return b

def run_experiment():
    ps=profiles();rows=[]
    for p in ps:
        truth=evaluate(canonical(p),"validated")["signals"]
        for c in PERTURBATIONS:
            b=perturb(p,c)
            for m in MODES:
                o=evaluate(b,m)
                outcome="hold" if o["decision"]=="hold" else ("correct" if o["signals"]==truth else "error")
                rows.append({"patient_id":p["id"],"perturbation":c,"pipeline":m,"decision":o["decision"],
                             "reference_signals":"|".join(truth),"output_signals":"|".join(o["signals"]),
                             "outcome":outcome,"warning_codes":"|".join(w["code"] for w in o.get("warnings",[]))})
    n=len(ps)*len(PERTURBATIONS);summary=[]
    for m in MODES:
        s=[r for r in rows if r["pipeline"]==m]
        cor=sum(r["outcome"]=="correct" for r in s);err=sum(r["outcome"]=="error" for r in s);hold=sum(r["outcome"]=="hold" for r in s)
        summary.append({"pipeline":m,"n":n,"correct_n":cor,"error_n":err,"hold_n":hold,
          "overall_correct_rate":round(cor/n,4),"silent_error_rate":round(err/n,4),
          "hold_rate":round(hold/n,4),"agreement_among_decided":round(cor/(cor+err),4)})
    breakdown=[]
    for m in MODES:
        for c in PERTURBATIONS:
            s=[r for r in rows if r["pipeline"]==m and r["perturbation"]==c]
            breakdown.append({"pipeline":m,"perturbation":c,"n":len(s),
              "correct_n":sum(r["outcome"]=="correct" for r in s),
              "error_n":sum(r["outcome"]=="error" for r in s),
              "hold_n":sum(r["outcome"]=="hold" for r in s)})
    wanted=[("unit_variation","raw","error"),("missing","standardized","error"),
            ("duplicate_conflict","validated","hold"),("implausible","validated","hold")]
    failures=[next(r for r in rows if r["perturbation"]==c and r["pipeline"]==m and r["outcome"]==o) for c,m,o in wanted]
    return {"study_id":"medisignal-dq-001","study_version":"1.0","reference_date":REFERENCE_DATE.isoformat(),
      "research_question":"How much can unit standardization and data-quality validation reduce silent signal-extraction errors from unit differences, missingness, and duplicates in a synthetic FHIR R4 stress test?",
      "design":{"base_profiles":len(ps),"perturbations_per_profile":len(PERTURBATIONS),"unique_patient_cases":n,
        "pipeline_evaluations":len(rows),"perturbations":PERTURBATIONS,
        "important_limitation":"Deliberately fault-enriched synthetic cases. Rates describe software behavior in this constructed set, not hospital-data or clinical-performance estimates."},
      "summary":summary,"breakdown":breakdown,"failure_examples":failures,"disclaimer":DISCLAIMER}

if __name__=="__main__":
    print(json.dumps(run_experiment(),ensure_ascii=False,indent=2))
