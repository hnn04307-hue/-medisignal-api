# MediSignal API — Research Portfolio v0.2

FHIR R4 synthetic data-quality experiment + explainable provenance API.

> Synthetic data only. This project does not claim clinical accuracy, diagnosis, treatment benefit, real-world hospital error rates, or medical-device performance.

## Research question

How much can unit standardization and explicit data-quality validation reduce silent signal-extraction errors caused by unit variation, missingness, duplicates, unsupported units, and implausible values in a reproducible synthetic FHIR R4 stress test?

## Reproducible experiment

- 16 deterministic base profiles
- 7 perturbations per profile
- 112 unique synthetic patient cases
- 3 pipelines per case
- 336 pipeline evaluations

| Pipeline | Correct | Silent error | Hold | Agreement among decided |
|---|---:|---:|---:|---:|
| Raw | 67.9% | 32.1% | 0.0% | 67.9% |
| Standardized | 78.6% | 21.4% | 0.0% | 78.6% |
| Validated | 42.9% | 0.0% | 57.1% | 100.0% |

Interpretation: supported unit standardization reduced silent errors by 10.7 percentage points in this constructed stress test. Adding data-quality validation converted the remaining constructed unsafe cases into explicit hold outcomes. The 57.1% hold rate reflects deliberate fault enrichment and is not a real-world prevalence estimate.

## Evidence layers

1. Software verification: 39 automated tests in GitHub Actions.
2. Research evidence: deterministic 112-case comparison with measured error, hold, and agreement rates.
3. Provenance: raw measurement -> normalization -> quality warning -> rule evaluation -> output.

## Live

- Portfolio: https://medisignal-api-2z8j.onrender.com/
- Swagger: https://medisignal-api-2z8j.onrender.com/docs
- Results API: https://medisignal-api-2z8j.onrender.com/v1/research/results
- Provenance API: POST /v1/research/trace

## Reproduce

Install dependencies, then run:

    pytest -q
    python -m research.run_experiment
    uvicorn app.main:app --reload

Expected v0.2 test result: 39 passed.

Full research protocol: research/PROTOCOL.md

## Background references

- HL7 FHIR R4 Observation: https://hl7.org/fhir/R4/observation.html
- HL7 FHIR R4 Quantity datatype: https://hl7.org/fhir/R4/datatypes.html
- Weiskopf NG, Weng C. Methods and dimensions of electronic health record data quality assessment: enabling reuse for clinical research. J Am Med Inform Assoc. 2013;20(1):144-151. doi:10.1136/amiajnl-2011-000681

## Limitations

- Synthetic, fault-enriched dataset
- Demo rule fixture, not a validated clinical model
- Limited unit-conversion table
- Technical processability bounds, not clinical reference ranges
- No real patient data and no claims about clinical performance