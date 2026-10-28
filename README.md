# AI Data Annotation, Rubric Scoring, and Quality Assurance Dashboard

Independent portfolio project for annotation consistency and dataset QA. It is not affiliated with Handshake or any AI lab.

Status: **Implemented, tested, and frontend build verified.** Not deployed. Public GitHub repository: https://github.com/JPPREMKUMAR/ai-data-annotation-qa.

## Features

- Import CSV, JSON, and JSONL with required-field, category, and duplicate-ID validation.
- Versioned five-label codebook and four-dimension quality scoring.
- Independent primary annotation and second review with a different reviewer ID.
- Adjudication, reasoned corrections, and an append-only audit log.
- Label counts, missingness, disagreement rate, and Cohen's kappa with limitations.
- CSV and JSON dataset exports.
- Blind synthetic records and separate gold labels.

## Run locally

Use Python 3.12 and Node.js 22 or compatible versions. Copy `.env.example` to `.env` if you need to change `DATABASE_PATH`; the default writes the local SQLite database. The dotenv file is loaded by the API and must remain uncommitted.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` for the API. To run the React interface, use `npm ci` and `npm run dev` from `frontend/` in a second terminal.

## Rubric and data

The codebook labels are correct, incorrect, incomplete, misleading, and ambiguous. Each annotation scores correctness, completeness, instruction adherence, and evidence quality on a 1–5 scale and requires an explanation. `data/records.jsonl` is the blind sample set; `data/gold_labels.jsonl` stores expected labels separately for QA.

## Verification and interpretation

Run `python -m pytest -q`; build the UI with `npm run build` in `frontend/`. The QA report includes sample counts. Agreement is a consistency measure and never proof that labels are true. See `docs/annotation-methodology.md` and `docs/test-report.md`.

## Limitations

This local-first demo has no authentication, role access control, or production data retention policy. Do not use it for confidential datasets without adding those controls. Cohen's kappa is unstable on small or imbalanced samples.

See [`docs/requirements.md`](docs/requirements.md) for MVP acceptance criteria, [`docs/architecture.md`](docs/architecture.md) for the data flow, [`docs/demo.md`](docs/demo.md) for a short walkthrough, [`docs/response-quality-examples.md`](docs/response-quality-examples.md) for labeled cases, and [`docs/deployment.md`](docs/deployment.md) for the current hosting assessment.

## License

MIT. See `LICENSE`.

