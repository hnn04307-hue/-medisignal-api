# MediSignal DQ-001 — Synthetic Data-Quality Study

## Research question

How much can unit standardization and explicit data-quality validation reduce silent signal-extraction errors caused by unit variation, missingness, duplicates, unsupported units, and implausible values in a reproducible synthetic FHIR R4 stress test?

## Design

- Fixed reference date: 2026-10-01
- 16 deterministic base profiles
- 7 perturbations per profile
- 112 unique synthetic patient cases
- 3 processing pipelines per case
- 336 total pipeline evaluations

Perturbations: clean, unit variation, duplicate same value, conflicting duplicate, missing BMI, unsupported pressure unit, and a deliberately corrupted out-of-range value.

## Pipelines

- Raw: first numeric value, unit ignored, no quality hold.
- Standardized: supported units normalized, first usable value selected, no quality hold.
- Validated: standardization plus missing/unit/range/duplicate checks; unsafe cases are held instead of silently classified.

## Metrics

- Silent error rate = incorrect proceed outputs / all cases
- Hold rate = hold outputs / all cases
- Overall correct rate = correct proceed outputs / all cases
- Agreement among decided = correct / (correct + error)

## Scope

This is a deliberately fault-enriched synthetic software stress test. Percentages are not estimates of real hospital data quality, clinical prevalence, diagnostic accuracy, or patient outcomes.

## Background

- HL7 FHIR R4 Observation / Quantity: https://hl7.org/fhir/R4/observation.html
- Weiskopf NG, Weng C. Methods and dimensions of electronic health record data quality assessment: enabling reuse for clinical research. J Am Med Inform Assoc. 2013;20(1):144-151. doi:10.1136/amiajnl-2011-000681