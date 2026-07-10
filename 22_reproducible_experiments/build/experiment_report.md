# EOIR Altitude Experiment Report

Generated: 2026-07-10T18:25:18
Question: How does UAV altitude affect EOIR detection outcomes in the reference geometry?
Hypothesis: Changing altitude changes line-of-sight geometry, range, and EOIR detection outcomes.
Quality gate: `PASS`
Seed variation observed: `False`

| Altitude (ft) | Runs | Mean detections | Mean success rate | Mean targets | Mean first detection (s) |
|---:|---:|---:|---:|---:|---:|
| 30000 | 3 | 99.0 | 6.04% | 8.0 | 146.0 |
| 45000 | 3 | 98.0 | 5.98% | 8.0 | 146.0 |
| 60000 | 3 | 90.0 | 5.49% | 7.0 | 146.0 |

## Interpretation Boundary

This sweep demonstrates a reproducible controlled experiment. Three seeds per altitude are enough for learning the workflow, not enough for a high-confidence operational conclusion. Increase repetitions and justify the statistical method before using results for decisions.

All three seeds produced identical metrics at each altitude in this run. The likely explanation is that the selected EOIR path is deterministic under these conditions. Setting a seed controls stochastic behavior; it does not guarantee that the chosen model contains randomness.
