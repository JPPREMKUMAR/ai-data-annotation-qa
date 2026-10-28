# Annotation methodology and QA metrics

## Versioned codebook

The initial codebook defines:

- **correct** — accurate and supported.
- **incorrect** — contains a material error.
- **incomplete** — omits requested or necessary information.
- **misleading** — creates a false impression or omits critical context.
- **ambiguous** — the available context does not support one confident label.

Each annotation stores the selected codebook version. New versions must define all labels. Keep gold labels in a separate file so annotators do not see the expected answer while reviewing.

## Review workflow

1. Import validated records with unique IDs.
2. A primary annotator records one label, four quality scores (1–5), and an explanation.
3. An independent reviewer uses a different reviewer ID and submits a blind second label.
4. Resolve disagreements with an adjudication and rationale.
5. Correct a prior annotation only with a reason; the before and after values are recorded in the audit log.

## Metrics

- **Missingness rate:** records without any annotations divided by all records.
- **Disagreement rate:** different labels among the first two saved reviews divided by records with at least two reviews.
- **Cohen's kappa:** observed pair agreement adjusted for expected chance agreement from reviewer label marginals. Undefined when there is no pair or expected agreement is 1.
- **Label distribution:** counts of annotation labels (not final adjudications).

Agreement measures consistency, not correctness. Small samples, class imbalance, ambiguous codebook examples, or changing the codebook can make kappa unstable or misleading. Inspect disagreements and report counts and sample size alongside it.
