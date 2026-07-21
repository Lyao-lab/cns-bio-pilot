---
name: perturb-seq-analysis
description: 分析【已经做好的】Perturb-seq / CROP-seq / CRISPR 筛选实验数据——基因功能鉴定、扰动响应差异、扰动一致性等下游分析。当用户已有 Perturb-seq 数据要做下游分析时触发。
tool_type: python
primary_tool: Pertpy
---

## When NOT to use this skill
- Predict perturbation response for **unmeasured** experiments (in-silico KO of unseen genes/drugs) → `single-cell/perturbation-prediction` (GEARS/CPA/scGPT)
- Only routine scRNA-seq preprocessing / clustering / annotation (no CRISPR guide) → `single-cell/omicverse-pipeline`
- Only gene essentiality / functional-module simulation (no measured Perturb-seq data) → `single-cell/perturbation-prediction` Route B (scTenifoldKnk via standalone R package — NOT wrapped in scop 0.8.0)
- bulk CRISPR screen (no single-cell readout) → out of scope (use bulk-screen tools such as MAGeCK)

# Perturb-seq Analysis

**"Analyze my Perturb-seq CRISPR screen"** → Link guide RNA assignments to transcriptional phenotypes in pooled CRISPR screens with single-cell readout to identify gene function.

**Engines**: Python `pertpy` 1.0+ (primary; `pt.tl.PseudobulkSpace` + `pt.tl.PyDESeq2` / `pt.tl.Mixscape` / `pt.tl.CentroidSpace`); R `Seurat` Mixscape (alternative classification path).

## Workflow (5 steps)

| Step | What | Tool | Key discipline |
|---|---|---|---|
| 1 | Load + annotate guides | pandas + Cell Ranger CRISPR output | keep only single-guide cells (`num_features==1`); label NT controls `'non-targeting'` (Python) / `'NT'` (Mixscape R) |
| 2 | Guide QC | value_counts + filter | drop guides with <100 cells; check non-targeting fraction 5–25% |
| 3 | Pseudobulk DE per perturbation | `pt.tl.PseudobulkSpace` → `pt.tl.PyDESeq2` (1.0+ API) | **MANDATORY pseudobulk** — per-cell Wilcoxon = pseudoreplication (meta-methodology principle 3) |
| 4 | Perturbation signature + embedding | `pt.tl.Mixscape().perturbation_signature` → `pt.tl.CentroidSpace.compute` → scanpy `sc.tl.leiden` (1.0+ API) | cluster perturbations by phenotype similarity |
| 5 | Pathway enrichment | `decoupler.run_ora` on MSigDB | per-perturbation gene sets |

**Canonical entry** (Python — pseudobulk DE is the core path; the discipline lives here):
```python
import pertpy as pt
# pertpy 1.0+ API: PseudobulkSpace aggregates, PyDESeq2 fits the model
ps = pt.tl.PseudobulkSpace()
pdata = ps.compute(adata, target_col='target_gene', groups_col='replicate',
                   layer_key='counts', mode='sum')
model = pt.tl.PyDESeq2(pdata, design='~target_gene')
model.fit()
de = model.compare_groups(pdata, column='target_gene',
                          baseline='non-targeting',
                          groups_to_compare=[g for g in pdata.obs['target_gene'].unique()
                                             if g != 'non-targeting'])   # pseudobulk, NOT per-cell
```

> **pertpy 0.7 → 1.0 breaking changes** (most online examples are 0.7, now broken):
> - `pt.tl.PseudobulkDE` → `PseudobulkSpace.compute()` + `PyDESeq2`/`EdgeR`/`Statsmodels`
> - `pt.tl.PerturbationSignature` → `pt.tl.Mixscape().perturbation_signature(...)` (writes `layers['X_pert']`)
> - `pt.tl.perturbation_embedding` / `cluster_perturbations` → `CentroidSpace.compute()` + scanpy `sc.tl.leiden`
> - `pt.pl.*` is EMPTY in 1.0 → use `model.plot_volcano()` / `mixscape.plot_heatmap()` or `sc.pl.*`

> **Full runnable workflow** (load → QC → preprocess → pseudobulk DE → signature → embedding → enrichment): see `examples/pertpy_analysis.py`.
> **Mixscape classification** (perturbed vs escaped cells, R/Seurat v5): see `examples/mixscape_analysis.R`.

## Screen QC Metrics

| Metric | Good | Acceptable | Poor |
|--------|------|------------|------|
| Cells per guide | >200 | 100-200 | <100 |
| Guide detection rate | >90% | 80-90% | <80% |
| Non-targeting cells | 5-15% | 15-25% | >25% |
| Mixscape KO fraction | >50% | 30-50% | <30% |

## Related Skills

- **Upstream**: routine scRNA-seq preprocessing (QC / clustering / annotation) → `single-cell/omicverse-pipeline`
- **Downstream 1**: predict perturbation response for **unmeasured** experiments → `single-cell/perturbation-prediction` (GEARS/CPA/scGPT, **linear baseline mandatory**)
- **Downstream 2**: perturbation-response DE / enrichment → `general-bio/omicverse-bulk` (pyDEG/pyGSEA)
- bulk CRISPR screen (no single-cell readout) → out of scope; use MAGeCK etc.

## Prerequisites (where data comes from)

- **Perturb-seq / CROP-seq raw data** (guides already mapped) → h5ad with an `obs['guide']` or `obs['perturbation']` column
- **Guide QC passed**: guide detection rate >80%, non-targeting fraction 5–25%, ≥100 cells per guide
- **`layers['counts']`** must be retained (perturbation DE uses pseudobulk + DESeq2)
- Tools: `pertpy` (primary) + `decoupler` (pathways) + optional Seurat Mixscape (via R)

## When to leave this skill (where to go)

- Predict **unmeasured** perturbations (unseen genes / drugs) → `single-cell/perturbation-prediction`
- Write Methods describing the Perturb-seq workflow → `presentation/methods-writer`
- Build a publication-grade figure from perturbation heatmap / dotplot → `visualization/multi-panel-figures`

## Key pitfalls

- **Wrong guide assignment corrupts everything downstream** — first use Mixscape to check that the KO signature is clear and that non-targeting vs targeting distributions are separated.
- **<100 cells per guide** makes pseudobulk DE unstable; report n per guide.
- **Perturbation DE must be pseudobulk** (aggregate by guide × sample), not per-cell Wilcoxon (pseudoreplication, meta-methodology principle 3).
- **MAGeCK RRA is for bulk screens** — do not treat Perturb-seq as a bulk screen.
- After finishing, run `scripts/postcheck.py` (repo root) to verify: DE used pseudobulk, Padj reported, guide QC passed.

## Resources
- `examples/pertpy_analysis.py` — Python end-to-end Pertpy workflow (load → QC → pseudobulk DE → signature → embedding → enrichment)
- `examples/mixscape_analysis.R` — R/Seurat v5 Mixscape classification (perturbed vs escaped cells)
