# Test report — 2026-10-28

Environment: Windows host, bundled Python 3.12.14, pytest 8.3.5, Node.js 22, npm 10.9.x, Vite 6.4.5.

| Check | Result | Evidence |
|---|---|---|
| Backend unit and workflow tests | **7 passed, 0 failed, 0 skipped** | `python -m pytest -q` |
| CSV / JSONL validation | **Passed** | Parser tests cover accepted formats and invalid category rejection |
| Duplicate IDs | **Passed** | Duplicate IDs within a batch and existing records are rejected |
| Independent review and kappa | **Passed** | Different reviewers' conflicting labels produce a disagreement rate of 1.0 and kappa 0.0 for the one-record fixture |
| Correction and adjudication audit | **Passed** | Tests verify action order and stored before/after annotation values |
| Frontend production build | **Passed** | `npm run build`; TypeScript and Vite succeeded |
| Lint / type check | **No separate lint configured; TypeScript type check passed** | `tsc -b` runs as part of the production build; no Python static type checker is configured |
| API live smoke check | **Passed** | Six records seeded; two ratings, disagreement metrics, adjudication, JSON export, and CSV HTTP 200 verified |
| Manual browser workflow | **Passed at the current browser viewport** | Displayed six seeded records, saved a reasoned `correct` annotation, and showed the updated annotation count/history |
| Deployment / GitHub publication | **Not done** | No deployment; local repository is committed, but remote repository creation and push remain pending |

The kappa result is a deliberately tiny synthetic example to test the calculation path, not a meaningful estimate of annotator agreement.

Known gaps: no systematic desktop/mobile breakpoint matrix or deployed smoke test has been completed.
