# Demonstration script

1. Start the API and frontend using the README instructions.
2. Inspect the six blind records; the separate gold-label file is not shown as record content.
3. For one record, submit a primary annotation and a second review with a different reviewer ID and a different label.
4. Adjudicate with a reason, then inspect the audit history and quality report.
5. Export JSON and CSV and compare the reviewed record count.

**Expected behavior:** The report exposes the test disagreement, adjudication, and audit actions; exports contain the six seeded records. A one-record disagreement can produce a 1.0 disagreement rate and a 0.0 kappa in this mechanics fixture. These tiny synthetic metrics are not a meaningful estimate of real annotator agreement, and agreement does not establish correctness.
