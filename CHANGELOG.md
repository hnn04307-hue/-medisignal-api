# Changelog

## v0.2.0 — Reproducible research portfolio

- Added formal research question and protocol.
- Added 112-case deterministic synthetic FHIR stress test.
- Added raw, standardized, and validated comparison pipelines.
- Added measured error, hold, and agreement metrics.
- Added provenance API showing raw values, normalization, quality warnings, rule evaluation, and all pipeline outputs.
- Added research-focused portfolio site with results table and failure cases.
- Added 39 automated tests and GitHub Actions CI.

Measured synthetic-study results:
- Raw silent error: 32.1%
- Standardized silent error: 21.4%
- Validated silent error: 0.0%
- Validated hold: 57.1%
- Validated agreement among decided: 100.0%

These percentages apply only to the deliberately fault-enriched synthetic cases in this repository.

## v0.1.0 — Initial public portfolio release

- FHIR R4 Bundle parsing
- Explainable demo signal rules
- FastAPI / OpenAPI
- Synthetic sample data
- Render deployment