# Response-quality examples

The six blind records and gold file demonstrate these response classes. Reviewers should label from the codebook definition and record why; gold labels are separated from the blind data.

| Category | Sample record | Expected annotation |
|---|---|---|
| Correct | `annotation-001`: “What is 2 + 2?” → “4.” | `correct`; arithmetic is accurate. |
| Incorrect | `annotation-002`: “What is 2 + 2?” → “5.” | `incorrect`; 2 + 2 equals 4. |
| Incomplete | `annotation-003`: asks for the boiling point and its condition; response gives only “100 °C.” | `incomplete`; omits the condition. |
| Misleading | `annotation-004`: “Are all bacteria harmful?” → “Yes, all bacteria cause disease.” | `misleading`; an absolute claim overgeneralizes. |
| Ambiguous | `annotation-005`: asks which answer is better without supplying candidates or criteria. | `ambiguous`; the comparison cannot be resolved from the context. |
| Poorly formatted | `annotation-006`: requests exactly three numbered steps; response is one paragraph. | `incomplete` with an instruction-adherence rationale; formatting failure is evidence for the label, not a separate allowed codebook label. |

Disagreement should be adjudicated with a reason. The metrics describe consistency for the available sample; agreement does not establish that either label is correct.
