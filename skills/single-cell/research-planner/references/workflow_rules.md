# Workflow Rules Reference

> 整合分析流程阶段的规则。

## Analysis Modules

Choose only modules that serve the study question.

| Module | Purpose | Use Level | Main Constraints |
|---|---|---|---|
| QC and filtering | Remove low-quality cells and artifacts | Necessary | Thresholds must match platform and tissue |
| Batch assessment / correction | Evaluate technical structure and, if needed, reduce batch effects | Necessary or Recommended | Do not over-correct away biology |
| Cell-type annotation | Label major populations and key states | Necessary | Annotation confidence must be checked |
| Composition analysis | Compare cell-type abundance | Recommended | Patient-level design matters |
| DEG / pathway analysis | Identify condition-associated programs | Necessary or Recommended | Must match data structure and contrast logic |
| Module scoring | Quantify curated programs per cell | Recommended | Gene set quality matters |
| Key-cell prioritization | Identify most relevant populations | Recommended | Needs explicit prioritization criteria |
| Trajectory / pseudotime | Model ordered state change | Optional | Only if a progression hypothesis is credible |
| RNA velocity | Dynamic direction inference | Optional | Requires suitable splicing information and assumptions |
| Cell-cell communication | Infer sender-receiver signaling | Optional | Inference only, not direct proof |
| Regulon / TF activity | Infer regulatory programs | Optional | Interpretation should remain cautious |
| CNV inference | Approximate malignant programs in cancer contexts | Optional | Context-specific; not a universal module |
| Pseudobulk / sample-aware analysis | Recover replicate-aware inference | Recommended to Advanced | Requires sample-level mapping |
| External validation | Cross-check in another dataset or orthogonal modality | Recommended | Must not be framed as guaranteed availability |
| Translational extension | Connect to biomarker, target, or clinical relevance | Optional | Must not overclaim readiness |

## Workflow Step Template

### Dataset Disclaimer Rule
If any workflow step mentions a dataset, cohort, database, repository, accession, or public resource, the workflow section must begin with the following line exactly once before the first step:

> **Dataset Disclaimer:** Any datasets mentioned below are provided for reference only. Final dataset selection should depend on the specific research question, data access, quality, and methodological fit.

### Recommended Workflow Skeleton
1. Clarify biological question and dominant study pattern
2. Define sample grouping and metadata requirements
3. Identify example dataset directions / repositories / candidate cohorts
4. Perform QC, filtering, and batch assessment
5. Build clustering and annotation framework
6. Run the main biological module(s)
7. Add one justified extension module if needed
8. Perform validation / robustness checks
9. Translate the signal into the intended biological or translational conclusion

### Important Rule
Do not include downstream steps that require sample-level replicate structure, outcome labels, treatment metadata, or paired design unless those dependencies were already specified.