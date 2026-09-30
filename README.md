# MediSignal API

**FHIR-based Clinical Data Signal Stratification API Prototype**

MediSignal is a portfolio-oriented research prototype that demonstrates how structured
FHIR R4 clinical data can be validated, transformed into features, evaluated with an
explainable rule engine, and exposed through a REST API.

> Research/education prototype only. Synthetic data and illustrative demo rules.
> Not for diagnosis, treatment, triage, or clinical use.

## What this repository demonstrates

`FHIR R4 input → validation → feature extraction → signal engine → explainable JSON → REST API`

The repository includes:

- FastAPI backend
- OpenAPI / Swagger documentation
- FHIR R4 synthetic sample data
- Explainable signal results
- Web MVP
- Automated API tests
- Render deployment configuration
- Version history in `CHANGELOG.md`

## API endpoints

### `GET /health`
Service health check.

### `POST /v1/signals/from-fhir`
Accepts a FHIR R4 Bundle containing a Patient and supported Observation resources.

Example output fields:

- `patient_id`
- `signal_level`
- `signal_count`
- `extracted_features`
- `triggered_signals`
- `disclaimer`

## Run locally

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Install and run:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open:

- Web MVP: `http://127.0.0.1:8000/`
- Swagger: `http://127.0.0.1:8000/docs`
- Health: `http://127.0.0.1:8000/health`

## Deploy on Render

Build command:

```text
pip install -r requirements.txt
```

Start command:

```text
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

A `render.yaml` file is included.

## Repository structure

```text
.
├── app/
│   ├── main.py
│   ├── fhir_parser.py
│   ├── schemas.py
│   └── signal_engine.py
├── data/
│   └── sample_fhir_bundle.json
├── tests/
│   └── test_api.py
├── web/
│   ├── index.html
│   ├── app.js
│   ├── data.js
│   ├── config.js
│   └── styles.css
├── CHANGELOG.md
├── README.md
├── render.yaml
├── requirements.txt
└── .python-version
```

## Portfolio statement

**Korean**

합성 FHIR R4 의료데이터를 구조화하여 주요 관찰값을 추출하고,
설명 가능한 규칙 기반 신호 분류 결과를 REST API/OpenAPI로 제공하는
연구용 프로토타입을 구현했습니다.

**English**

Built a research prototype that parses synthetic FHIR R4 clinical data,
extracts structured observations, and exposes explainable signal-stratification
outputs through a REST API with OpenAPI documentation.

## Limitations

- Synthetic data only in the public portfolio.
- Demo thresholds are not presented as clinical guidelines.
- No diagnostic or treatment claims.
- A production/research-grade implementation would require validated clinical rules,
  terminology and unit validation, governance, security, and appropriate clinical validation.
