# Validation and Figure Delivery Reference

> 整合验证与图表产出阶段的规则。

## Validation Evidence Hierarchy

Single-cell studies should separate discovery from validation.

| Evidence Layer | What It Shows | Typical Strength |
|---|---|---|
| Within-dataset consistency | Signal exists internally under the chosen contrasts | Basic |
| Alternative analytic robustness | Signal is not dependent on one threshold or one method | Basic to Moderate |
| Cross-dataset replication | Similar signal appears in an independent cohort | Moderate |
| Orthogonal modality support | Bulk, protein, histology, spatial, or clinical data support the signal | Moderate to Strong |
| Experimental perturbation / functional testing | Biological intervention changes the relevant signal or phenotype | Strong |
| Translational performance evidence | Marker/target works in clinically meaningful stratification or prediction | Highest but hardest |

### Important Rule
Do not present within-dataset discovery as external validation.
Do not present inferred communication or trajectory as experimental proof.
Do not claim clinical readiness without at least one orthogonal or external validation layer.

## Figure and Deliverable Plan

Figures should mirror the study logic.

### Typical Figure Sequence
1. Study overview, cohort / dataset logic, and workflow
2. QC, clustering, and annotation overview
3. Main biological signal (composition / DEG / state score / key cell)
4. Mechanism layer (trajectory / communication / regulon) if justified
5. Validation layer
6. Translational or extension figure if applicable

### Deliverable Expectations
A good plan should specify:
- likely main figures
- supplemental analysis buckets
- minimal result package for the Lite version
- which figures depend on advanced-only modules