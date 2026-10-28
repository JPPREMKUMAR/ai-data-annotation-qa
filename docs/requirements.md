# Product requirements and acceptance criteria

## Problem and users

Annotation teams need a shared labeling guide, independent second review, correction history, and quality metrics to find inconsistent or incomplete work. Users are annotators, adjudicators, and dataset quality reviewers.

## MVP behavior

1. Import CSV, JSON, or JSONL data with required fields, valid labels, and unique record IDs.
2. Maintain a versioned five-label codebook with definitions and examples.
3. Record four response-quality scores and an explanation for each annotation.
4. Support a second reviewer with a different ID, adjudication, corrections, and before/after audit events.
5. Report label distribution, missingness, disagreement, and Cohen's kappa; export reviewed records and reports.

## Acceptance checks

- Duplicate IDs, invalid categories, missing explanations, and same-reviewer second reviews are rejected.
- Corrections preserve actor/time and before/after values.
- Small-sample agreement metrics include a sample count and are not described as truth.
- JSON/CSV export, workflow tests, and frontend build pass.

## Risks and limits

The app has no authentication or real role enforcement despite recording reviewer IDs. Cohen's kappa is unstable on small or imbalanced samples, and agreement does not prove labels are correct. Do not enter confidential data until identity, authorization, retention, and deployment storage are implemented.
