# Study Design Reference

> 本文件整合研究设计阶段的 5 类规则模块。research-planner 的 SKILL.md 按章节号引用。

## Study Patterns

Use one dominant pattern. A secondary pattern may be added only as a supporting layer.

### Pattern A — Cell Atlas / Composition Mapping
Use when the user mainly wants to characterize major cell populations, composition shifts, or disease-vs-control cellular architecture.

Best for:
- first-pass disease landscape
- tissue microenvironment description
- cell-type proportion change questions

Do not overextend this pattern into mechanism unless additional modules justify it.

### Pattern B — Key Cell / Key State Prioritization
Use when the user wants to identify which cell type or state most strongly aligns with disease biology, phenotype severity, or a mechanism theme.

Best for:
- prioritizing driver-like cell populations
- linking cell programs to disease intensity
- focusing downstream validation

### Pattern C — State Transition / Trajectory
Use when the question is inherently about progression, differentiation, exhaustion, activation, fibrosis transition, or lineage-like change.

Requirements:
- sufficient state diversity
- biologically credible ordering hypothesis
- adequate cell numbers in relevant populations

Do not force trajectory analysis in static or weakly ordered systems.

### Pattern D — Cell-Cell Communication / Microenvironment Crosstalk
Use when the user cares about intercellular signaling, niche remodeling, stromal-immune interaction, or tumor microenvironment crosstalk.

Requirements:
- biologically distinct interacting populations
- sufficient abundance of sender and receiver groups
- communication interpreted as inferred signaling, not proven contact biology

### Pattern E — Translational Biomarker / Target Discovery
Use when the user wants clinically relevant markers, stratification signals, therapeutic targets, or actionable cell-state programs.

This pattern requires explicit separation of:
- descriptive discovery
- prioritization logic
- validation logic
- translational extension

### Pattern F — Treatment Response / Resistance Mechanism
Use when the user wants to compare responder/non-responder states, pre/post treatment differences, or resistance-associated cell programs.

Must define whether signals are:
- predictive baseline features
- treatment-emergent features
- resistance-associated descriptive signals

Do not blur these categories.

## Workload Configurations

Always output all four configurations. Recommend one as the primary plan.

| Configuration | Typical Scope | Data Expectation | Core Modules | Validation Level |
|---|---|---|---|---|
| Lite | Fast, bounded, public-data-first | 1 suitable dataset | QC, annotation, composition, focused DEG/pathway | Within-dataset consistency |
| Standard | Conventional publishable single-cell paper | 1–2 datasets or 1 strong dataset + orthogonal validation | Lite + key-cell prioritization + focused state analysis + external expression/biology support | Within-dataset + one external layer |
| Advanced | Stronger mechanism and robustness | 2+ datasets and/or richer metadata | Standard + pseudobulk/sample-aware analysis + communication or trajectory + deeper robustness checks | Cross-dataset + orthogonal validation |
| Publication+ | High-ambition, multi-layer manuscript | Multiple datasets and substantial validation support | Advanced + stronger translational or experimental extension | Multi-layer validation and extension |

### Recommendation Logic
- **Lite** = minimum executable version.
- **Standard** = default best-fit unless user constraints are extremely tight or the ambition is unusually high.
- **Advanced** = use when robustness or mechanism depth materially improves the project.
- **Publication+** = use only when data, time, and validation resources plausibly support it.

### Subset Rule
Each higher configuration must extend the lower one. Do not introduce a completely different project at higher tiers.

## Dataset Recommendation and Disclaimer

### Mandatory Dataset Disclaimer
If any workflow step mentions a dataset, cohort, database, repository, accession, or public resource, the workflow section must begin with the following line exactly once before the first step:

> **Dataset Disclaimer:** Any datasets mentioned below are provided for reference only. Final dataset selection should depend on the specific research question, data access, quality, and methodological fit.

This disclaimer is mandatory and must not be omitted.

### Dataset Recommendation Rules
When recommending datasets or repositories:
- present them as **reference candidates only**
- state why they might fit the question
- state what must be checked before final selection
- distinguish **verified resource name** from **assumed suitability**
- do not invent accession IDs or metadata details

### What to State for Each Dataset Direction
Whenever possible, specify:
- tissue / disease relevance
- likely platform type or modality
- disease-control or subgroup structure needed
- metadata requirements (sample ID, treatment status, outcome, batch, timepoint)
- main risk (small sample size, weak metadata, no replicate structure, post-treatment only, etc.)

### Repository-Level Suggestions
It is acceptable to recommend repository types such as GEO, ArrayExpress, CellxGene, Human Cell Atlas, TISCH, or disease-focused atlases **as examples only** if direct dataset verification has not been done.

Never imply that the repository automatically contains a suitable dataset for the specific question.

## Method Library

Select methods according to data structure and the biological question.

### Core Frameworks
| Need | Preferred Options | Notes |
|---|---|---|
| scRNA processing / analysis | Seurat, Scanpy | Use one coherent framework unless there is a clear reason to mix |
| Annotation | marker-based curation, SingleR, CellTypist, reference mapping | Automated labels need manual biological review |
| DEG (cell-level, exploratory) | Wilcoxon, MAST | Match method to sparsity and model needs |
| Pseudobulk DEG with counts | DESeq2 | Preferred when replicate-aware count matrices are available |
| Pseudobulk DEG with non-count normalized data | limma | Preferred when the matrix is not raw counts |
| Pathway / enrichment | fgsea, GSVA, AUCell, UCell | Match gene-set and single-cell use case |
| Batch integration | Harmony, Seurat integration, BBKNN, scVI | Use only if necessary for the biological question |
| Trajectory | Monocle3, Slingshot | Choose based on topology and interpretability |
| RNA velocity | scVelo, velocyto-based workflows | Only for suitable data |
| Communication | CellChat, CellPhoneDB, LIANA, NicheNet | Interpret as inferred signaling |
| Regulon / TF activity | SCENIC, pySCENIC, DoRothEA/Viper-style approaches | Optional, not default |
| CNV inference | inferCNV, CopyKAT | Mostly context-specific for tumor studies |

### Method Selection Rule
Do not list multiple tools for every module unless comparison is necessary.
Prefer one default recommendation plus one reasonable alternative.

## Literature Retrieval and Citation

### Core Rule
Never fabricate references.

### When Formal References Are Listed
Only include references that have been directly verified through a trustworthy source.
Each formal reference should include at least one stable identifier or resolvable path, such as DOI, PMID, PMCID, PubMed page, PMC page, or official journal landing page.

### If Direct Verification Is Not Available
Do not invent placeholder references.
Instead, clearly state:
- that formal references are not yet verified
- which evidence categories should be searched
- example search targets (disease background, single-cell precedent, method support, validation precedent)

### Reference Types to Separate
- disease / mechanism background
- method-support references
- same-disease or neighboring-disease single-cell precedent
- translational or validation precedent