---
name: omicverse-single-cell-pipeline
description: 单细胞全流程（ambient 去除→QC→doublet→降维聚类→注释→批次校正→通讯→轨迹）+ 多组学整合（MOFA+/GLUE/CITE-seq/代谢/SIMBA/CEFCON）基于 OmicVerse V2 统一 API，无需在 scanpy/Seurat/scVI/CellTypist 间切换。一个 import omicverse as ov 覆盖 90% 常规分析。当用户要做单细胞、scRNA、多组学、CITE-seq、scRNA+ATAC、代谢、MOFA、GLUE 时触发。
---

## When NOT to use this skill
- cell2location spatial deconvolution → use `spatial/deconvolution` (not registered in omicverse)
- R/Seurat environment or scop-only tools (CytoTRACE/Milo/SecAct/Giotto) → use `single-cell/scop`
- Predict unmeasured perturbations (unseen gene/drug KO) → use `single-cell/perturbation-prediction`
- Downstream analysis of measured Perturb-seq (differential perturbation response, Mixscape) → use `single-cell/perturb-seq`

# OmicVerse Single-Cell Pipeline

**Merged from prior skills:** the original preprocessing / doublet-detection / clustering / cell-annotation / batch-integration / cell-communication / trajectory-inference / scanpy / scvi-tools skills (these standalone skills no longer exist; functionality is unified in OmicVerse V2). This skill is the canonical entry point for all of them. RNA velocity lives in `single-cell/rna-velocity`; Perturb-seq in `single-cell/perturb-seq`.

`pip install omicverse` (V2 released). Examples below use the real `ov` API, flagging key parameters and pitfalls.

## 0. Init

```python
import omicverse as ov
ov.plot_set()  # unified global plotting style (font/palette/dpi)
import scanpy as sc   # ov is built on scanpy/anndata; a few ops still need sc
```

> **Dependency:** `ov.single.*` (find_markers, annotation, etc.) requires `ipywidgets`. If you hit `ModuleNotFoundError: No module named 'ipywidgets'`, run `pip install ipywidgets` first. Without a GPU, ov auto-falls back to CPU mode (works, but scVI/scGPT finetune is slow).

## 1. Load data (keep `layers['counts']`)

```python
adata = sc.read_10x_mtx('filtered_feature_bc_matrix/')   # or ov.read('data.h5ad')
adata.layers['counts'] = adata.X.copy()   # IMPORTANT: store raw counts BEFORE QC; DE/velocity depend on it
```

> Million-cell scale: `adata = ov.read('data.h5ad', backend='rust')` uses AnnDataOOM, ~170× memory savings.

> **Workflow order**: §1 load → **§1.5 ambient removal** (if FFPE/nuclei/high-background) → §2 QC → §3 preprocess. Ambient removal must come BEFORE QC — contaminated counts make mt%, doublet rate, and markers all misleading.

## 2. QC + doublet (two-step: diagnose first, then filter)

`ov.pp.qc` inlines mt/ribo fraction, cell/gene filtering, and doublet detection. **But mt% threshold is NOT a universal default** — it depends on tissue / platform / dissociation (liver hepatocytes legitimately hit 30%+; brain neurons die above 10%; sorted nuclei should be near 0%). **Never copy-paste a threshold — diagnose first, then choose.**

### Step 2a — Diagnose BEFORE filtering (mandatory)

```python
import scanpy as sc
# Compute QC metrics WITHOUT filtering first
adata.var['mt'] = adata.var_names.str.startswith('MT-')   # human; 'mt-' for mouse
sc.pp.calculate_qc_metrics(adata, qc_vars=['mt'], inplace=True)
# Plot per-sample distributions — find the knee/elbow, look for tissue-appropriate range
sc.pl.violin(adata, ['n_genes_by_counts','total_counts','pct_counts_mt'],
             groupby='sample', jitter=0.4, multi_panel=True)
sc.pl.scatter(adata, x='total_counts', y='pct_counts_mt')      # high-mt tail = dying cells?
sc.pl.scatter(adata, x='total_counts', y='n_genes_by_counts')   # knee = low-quality breakpoint?
```

> **Look at the plot, then decide.** The threshold comes from YOUR data's distribution + tissue biology, not a hardcoded number. See the tissue reference table below (§QC principles) for typical ranges — but verify against your actual violin/scatter.

### Step 2b — Filter with the threshold you chose from the diagnostic

```python
import omicverse as ov
ov.pp.qc(
    adata,
    mode='seurat',                       # 'seurat' (tresh dict) | 'mads' (5×MAD auto)
    doublets_method='scdblfinder',       # DEFAULT in ov 2.2.3 — Python port of R scDblFinder
                                         # (xgboost on kNN+cxds). Alt: 'scrublet' / 'doubletfinder' / 'sccomposite'
    batch_key='sample',                  # REQUIRED for multi-sample: detect doublets per sample
    filter_doublets=True,
    tresh={                              # NOTE: param name is 'tresh' (typo, omicverse's actual API)
        'mito_perc': <VALUE_FROM_DIAGNOSTIC>,   # e.g. 0.15 for 15%; YOU choose after Step 2a
        'nUMIs': 500,                            # min total counts
        'detected_genes': 250,                   # min genes detected
    },
)
# adds to adata.obs: n_genes_by_counts, total_counts, pct_counts_mt, predicted_doublet
```

> **⚠️ Do NOT pass `mt_thresh=20` — that parameter does NOT exist on `ov.pp.qc`** (it is silently swallowed by `**kwargs` and ignored). The correct API is `tresh={'mito_perc': <frac>, ...}` (seurat mode) or `mode='mads', nmads=5` (auto-threshold from the distribution, 5 median-absolute-deviations — good when you don't want to hand-pick).
>
> **⚠️ Never copy-paste a mito threshold.** 20% is wrong for liver (too strict — kills real hepatocytes), wrong for brain (too loose — keeps dying neurons), wrong for nuclei (any mt% = contamination). The only honest workflow is: plot → find knee → check tissue table → document your choice (or use `mode='mads'`).

> **Ambient RNA removal happens BEFORE `ov.pp.qc`** (see §1.5 below). Do not run QC on contaminated counts — ambient RNA inflates mt%, inflates marker scores, and makes doublet rates misleading.

Decision: `scdblfinder` default (Python port of R scDblFinder via `pyscdblfinder`, xgboost on kNN+cxds features — [Germain et al. 2021 F1000](https://f1000research.com/articles/10-979), matches Seurat's DoubletFinder accuracy without the R roundtrip). `scrublet` is the legacy pure-Python fallback (faster but slightly lower recall); `doubletfinder` requires R. `sccomposite` (scvi-tools, Bayesian) is the heavy alternative.

## 1.5 Ambient RNA removal (run BEFORE §2 QC)

Ambient ("soup") RNA = cell-free mRNA from lysed cells that contaminates every droplet. Left uncorrected it inflates marker genes in cell types that never expressed them and biases DE, annotation, and trajectory inference. **For FFPE, nuclei, and any run with visible background, ambient removal is NOT optional** — skipping it is a silent landmine.

**Canonical entry** (6-backend dispatcher, omicverse 2.2.3):
```python
import omicverse as ov
ov.pp.ambient.remove_ambient(adata, method='soupx', raw=raw_adata)   # or 'fastcar' / 'decontx' / 'sccdc' / 'cellbender' / 'scar'
```

> **Full backend decision table + run options + diagnostics** (`contamination_report` / `plot_contamination` / `ambient_negative_marker_check` / `count_integrity_check`) + when NOT to run: see `references/ambient_removal.md`.
>
> **Ordering discipline (non-negotiable)**: ambient removal runs BEFORE §2 QC. Contaminated counts make mt%, doublet rate, and markers all misleading. After removal, **re-store `layers['counts']` from corrected `.X`** so downstream DE/velocity use cleaned counts.

### QC principles (threshold selection — the part reviewers actually probe)

QC thresholds are **experimental design choices, not universal defaults**. A threshold that works for brain tissue kills metabolically active hepatocytes; a threshold for FACS-sorted nuclei makes no sense for whole-tissue dissociation. CNS reviewers routinely ask "what is the justification for your mt% cutoff?" — have an answer.

**1. Per-sample QC, not per-batch**. Run QC and doublet detection **per sample** (pass `batch_key='sample'`), then merge. Running on merged data produces cross-sample false doublets and hides sample-specific quality drift. (Heumos et al. 2023 Nat Rev Genet; [Seurat discussion #6171](https://github.com/satijalab/seurat/discussions/6171))

**2. Thresholds depend on tissue / platform / dissociation** — never copy-paste:

| Tissue / sample type | mt% typical | n_genes min | Notes |
|---|---|---|---|
| Brain / neuron | 5–10 | ≥500 | low mt; dead neurons lose fast |
| Liver / hepatocyte | 15–30 (even 50 acceptable) | ≥1000 | hepatocytes are mitochondria-rich — strict mt% **kills real cells** |
| Heart / cardiomyocyte | 15–25 | ≥800 | similar — high metabolic tissue |
| Cultured cell line | ≤10–15 | ≥500 | should be clean; high mt = dying |
| Sorted nuclei (snRNA) | mito gene count near 0 (nuclei have almost no mt) | ≥400 | high mt% in nuclei = cell contamination — flag, don't just raise cutoff |
| FFPE | variable, often higher background | ≥300 | CellBender first (ambient dominates) |
| PBMC | 5–15 | ≥300 | 10x default-ish |

> If unsure: **plot the distribution first** (Step 2a above), look for the knee/elbow, and document the choice. There is no universal mt% default.

**3. Filter-stringency trade-off (meta-methodology)**: filtering shapes the conclusion.
- **Too strict** (e.g. blanket mt% < 10 on liver) → systematically removes real metabolically-active cells, leaving a **biased** population. The remaining "clean" cells are not representative.
- **Too loose** → dying/damaged cells + doublets + ambient inflate noise, creating spurious clusters and DE.
- The honest move: report the threshold, show before/after cell counts per sample, and do a **sensitivity check** (±1档 threshold, does the main conclusion hold?).

**4. Doublet rate sanity**: expected ~1% per 1000 cells loaded (10x). >15% doublet rate suggests either poor loading or a doublet-tool false positive (check cell-cycle — cycling cells can masquerade as doublets).

**5. Post-QC audit (must report)**: per-sample cell counts before/after QC; if any sample drops >60%, investigate (batch effect, dissociation failure, library prep). A sample quietly losing 70% of cells and being kept silently is a reviewer landmine.

> References: Heumos et al. 2023 *Nat Rev Genet* 24:550 (sc-best-practices.org QC chapter); Luecken & Theis 2019 *Mol Syst Biol* (foundational best-practices); [10x Genomics QC considerations](https://www.10xgenomics.com/analysis-guides/common-considerations-for-quality-control-filters-for-single-cell-rna-seq-data).

## 3. Preprocess (normalize + HVG + scale)

```python
ov.pp.preprocess(adata, mode='shiftlog', n_HVGs=2000)
# mode='shiftlog'  → classic log1p (default)
# mode='pearson'   → Pearson residuals (no explicit HVG/scale, more robust)
ov.pp.scale(adata)   # result stored in adata.layers['scaled']
```

Decision: shiftlog for routine plots; pearson residuals more stable against mt/cell-cycle contamination but slightly worse DE interpretability.

## 4. Dim reduction + neighbors + UMAP/TSNE

```python
ov.pp.pca(adata, layer='scaled', n_pcs=50)
ov.pp.neighbors(adata, n_neighbors=15, use_rep='X_pca', n_pcs=30)
ov.pp.umap(adata)
ov.pp.tsne(adata)   # optional, on demand
```

## 5. Clustering (auto resolution)

```python
ov.pp.leiden(adata, resolution='auto')   # auto invokes ov.single.auto_resolution
# manual equivalent:
# ov.single.auto_resolution(adata); ov.pp.leiden(adata, resolution=res)
# result in adata.obs['leiden']
```

> **Cluster stability is part of the evidence** (meta-methodology ④). `resolution='auto'` is a starting point, not proof. For clusters that anchor key conclusions:
> - Bootstrap / sub-sampling stability (re-cluster on 80% subsamples × 10 runs, Jaccard similarity per cluster; >0.7 = stable)
> - Resolution sensitivity (does the main conclusion hold at resolution ±1 step?)
> - Optional statistical significance of clusters: `scSHC` (Python/R) tests cluster separation rigorously
> Reporting a single clustering at a single resolution without stability check = hidden fork-in-the-path.

## 6. Cell cycle scoring

```python
ov.pp.score_genes_cell_cycle(adata, species='human')  # 'human' | 'mouse'
# adata.obs: S_score, G2M_score, phase
```

## 7. Batch correction / integration

```python
# Lightweight: Harmony (in PCA space, seconds)
ov.single.batch_correction(adata, method='harmony', batch_key='sample')

# Deep: scVI (generative model, captures non-linear batch effects)
ov.single.batch_correction(adata, method='scvi', batch_key='sample')
# NOTE: after scVI, recompute neighbors/umap using adata.obsm['X_scVI'] as use_rep
ov.pp.neighbors(adata, use_rep='X_scVI'); ov.pp.umap(adata)
```

Decision: Harmony for shallow batch / fast iteration; scVI for complex batch and CNS main figures (original scvi-tools is now merged in, params pass through).

> **Integration diagnostics are mandatory** (meta-methodology ④). Correction without diagnosis = blind trust. After any integration, report **both**:
> - **Batch mixing**: iLISI / kBET / ASW_batch — higher = better batch mixing
> - **Bio conservation**: cLISI / ASW_celltype / iso-label F1 — higher = better biological signal retention
> - **Over-correction signal**: bio conservation drops sharply → downgrade method (scVI → Harmony → or no integration if batch is small)
>
> Install: `pip install scib-metrics` (Luecken et al. 2022 Nat Methods), then:
> ```python
> from scib_metrics.benchmark import Benchmarker
> # compute iLISI/cLISI/ASW_batch/ASW_celltype on X_pca vs X_scVI vs X_harmony
> ```
> A corrected embedding with great batch mixing but poor bio conservation has **erased real biology** — your DE / trajectory / annotation downstream will be silently wrong.

> **Time-series / spatial alignment** (multi-timepoint development, spatial OT registration): Harmony/scVI are not optimal — **moscot** (optimal transport, Nature 2024) is SOTA here. But moscot **is not installed in the sc env and not wrapped by omicverse**. If needed: `pip install moscot`, then call native per [moscot.readthedocs.io](https://moscot.readthedocs.io/); output feeds CellRank's RealTimeKernel. Routine batch correction does NOT need moscot.

## 8. Markers + annotation

```python
# markers
ov.single.find_markers(adata, method='wilcoxon')   # 'wilcoxon' | 't-test' | 'cosg'
# COSG is more robust for rare populations but slower

# annotation (pick as needed)
ov.single.pySCSA(adata)             # reference-free, marker → auto annotation
ov.single.AnnotationRef(adata, ref='...')  # with reference (CellTypist/SingleR engine)
# or ov.single.Annotation(adata).annotate(..., ref='scmulan')  # scmulan: FM-based annotator new in ov
ov.single.gptcelltype(adata)        # LLM-assisted, needs API key
```

> ⚠️ **Foundation-model reality check (2025)**: scGPT / Geneformer / scFoundation / UCE do **not** dominate annotation or perturbation prediction. Ahlmann-Eltze et al. *Nat Methods* 2025 ([s41592-025-02772-6](https://www.nature.com/articles/s41592-025-02772-6)) showed 5 FMs all lose to a linear baseline for perturbation; Kedzierska et al. *Genome Biol* 2025 ([s13059-025-03574-x](https://link.springer.com/article/10.1186/s13059-025-03574-x), 107+ citations) and Wu et al. *Genome Biol* 2025 ([s13059-025-03781-6](https://link.springer.com/article/10.1186/s13059-025-03781-6), 22-tissue benchmark) show Geneformer/scGPT zero-shot annotation is brittle and simple methods (CellTypist/SingleR/scVI) often win. **Rule: always benchmark any FM against a simple baseline (CellTypist / SingleR / scVI + logistic) and only adopt the FM if it clearly wins for your specific task.** `ov.fm` does **not** exist in omicverse 2.2.3 — use FMs as standalone packages. Frontier options: **scNET** (Nat Methods 2025, PPI-enhanced gene embedding), **TranscriptFormer** (CZI 2025, first generative multi-species FM), **UCE** (cross-species embedding) — all experimental, baseline first.

### Annotation principles (not just API — how to assign labels responsibly)

Annotation labels are **hypotheses, not ground truth**. Every label is a prediction from an imperfect reference or marker set — CNS reviewers routinely ask "what is the evidence for calling this cluster X?". Have a defensible answer.

**1. Reference must match tissue / species / disease state / resolution**. A blood CellTypist reference applied to brain tissue will confidently produce wrong labels. Always state: reference organism, tissue, healthy vs disease, and lineage-level vs subtype-level. Mismatch → only annotate to broad lineage, not subtype. (Huang et al. 2021 benchmark, 10 methods; Fu et al. 2024, 18 methods — subtype accuracy drops cliff vs lineage-level)

**2. Hierarchical annotation (broad lineage → subtype, never one-step to subtype)**:
- First assign broad lineages (T / B / Myeloid / Fibro / Epi / Endo / SMC) via canonical markers
- Then sub-cluster within each lineage for subtype resolution
- One-step clustering at high resolution + auto-annotation to 30 subtypes → unstable, irreproducible labels

**3. Multi-method cross-validation (mandatory for key cell types)**:
```python
# Run ≥2 methods, build a cross-tab, inspect disagreement
ov.single.AnnotationRef(adata, ref='celltypist_immune')   # method 1
adata.obs['anno_singleR'] = <SingleR labels>               # method 2
# Cross-tabulate: where do they disagree?
import pandas as pd
pd.crosstab(adata.obs['celltypist'], adata.obs['anno_singleR'])
# Clusters with low agreement → label 'Unknown' or resolve with manual markers
```
The disagreement rate IS your uncertainty. Don't hide it — report it.

**4. Canonical-marker manual validation (the ground-truth backstop)**:
```python
# After auto-annotation, confirm key labels with known markers
ov.pl.dotplot(adata, var_names={'T cell':['CD3D','CD3E','CD2'],
                                  'B cell':['CD79A','MS4A1'],
                                  'Macro':['LYZ','CD68','AIF1'],
                                  'Fibro':['DCN','COL1A1'],
                                  'Endo':['VWF','PECAM1'],
                                  'SMC':['ACTA2','MYH11','TAGLN']},
              groupby='celltypist')
# A cluster called "T cell" with zero CD3D expression = annotation failure
```
Auto-annotation without marker validation = trusting an unverified black box.

**5. Label low-confidence clusters 'Unknown' — never force-fit**:
- If a cluster has no clear marker signature, or 2+ methods disagree, label it `Unknown` / `Unresolved`
- Do NOT assign the "closest" label just to have a name — this creates downstream errors (DE, communication, proportion analysis all inherit wrong labels)
- Unknown clusters are honest science; mislabeled clusters are silent landmines

**6. Annotation-method sensitivity (meta-methodology — POP project lesson)**:
- Switching annotation method (e.g. marker-score → lineage-threshold) can **reverse** the dominant cell type (POP project: Fibroblast 60.6% → SmoothMuscle 66.0% when method changed)
- For any cell-type-proportion conclusion, **report which annotation method was used + do a sensitivity check** (does the conclusion hold with a second method?)
- This is meta-methodology principle ④ (report the path, not just the endpoint)

> References: Huang et al. 2021 *Genomics Proteomics Bioinformatics* (10-method benchmark); Fu et al. 2024 *Brief Bioinform* (18-method benchmark); [sc-best-practices annotation](https://www.sc-best-practices.org/cellular_structure/annotation.html); [ScPCA nonsense-reference test](https://www.ccdatalab.org/blog/a-behind-the-scenes-look-at-how-we-selected-cell-type-annotation-platforms-for-the-scpca-portal) (annotation tools give confident labels even with wrong references).

## 9. Downstream: communication / trajectory

```python
# Cell-cell communication (LIANA+ consensus recommended — Dimitrov et al. Mol Syst Biol 2024, 251+ citations;
# multi-method + multi-resource aggregation, the 2024 mainstream consensus path; supersedes single-tool CellChat/CellPhoneDB)
ov.single.run_liana(adata, scope='shortcode')   # consensus, runs multiple methods
ov.single.run_cellphonedb_v5(adata)             # alternative: CellPhoneDB v5 (multi-omics/spatial)
ov.pl.ccc_heatmap(adata)
# Spatial communication → spatial/omicverse-spatial (COMMOT/FlowSig)

# Trajectory / fate inference (CellRank 2 is now primary, Nat Methods 2024; supersedes plain Monocle/Slingshot)
ov.single.cellrank_fate(adata, cluster_key='celltype')   # unified kernel framework, probabilistic fate
ov.single.Fate(adata, pseudotime='dpt_pseudotime')       # pseudotime-based fate
# classic py-monocle2 still available (simple pseudotime)
ov.single.Monocle(adata)
```

> **Trajectory choice:**
> - **CellRank 2** (Nat Methods 2024) is the default for **continuous fate mapping** (velocity / pseudotime / metabolic-labeling kernels unified). Velocity-driven trajectory → `single-cell/rna-velocity` (incl. `cellrank_fate`).
> - **moscot** (Nature 2025, optimal transport) is the SOTA for **discrete timepoints / spatial time series** (e.g. 4sU/SLAM multi-timepoint, spatial snapshots). Not installed in `sc` env / not wrapped in omicverse — install standalone; its output feeds CellRank's RealTimeKernel.
> - **LEMUR** (Ahlmann-Eltze & Huber, Nat Genet 2025, [s41588-024-01996-0](https://www.nature.com/articles/s41588-024-01996-0)) — cluster-free multi-condition DE on a Grassmann manifold; same lab as the linear-baseline paper; new paradigm for "does condition X shift cells along trajectory Y" without pre-clustering.
> - Standalone Monocle3/Slingshot/Palantir: legacy/teaching fallback, not first choice.
> - Diffusion map / DPT: obsolete, only as pseudotime input to CellRank.

### Discipline for §9 outputs (non-negotiable writing rules)

- **CCC results are hypotheses, not mechanism**: mRNA co-expression of ligand–receptor ≠ protein activity ≠ pathway activation. When writing about CCC outputs, use **"associated with" / "enriched for"**, never **"regulates" / "activates" / "drives"** without orthogonal protein/functional evidence. (Meta-methodology principle ①③; enforced in `scripts/postcheck.py` L2 check.)
- **Pseudotime is ordering, not time**: `latent_time` / `dpt_pseudotime` / `monocle3_pseudotime` are relative ordering along the learned graph — they do **not** measure real duration, rate, or physical time. Never write "cells transition at rate V" or "the process takes T hours" from pseudotime alone. Real time requires metabolic labeling (4sU/SLAM-seq) or pulse-chase data. (See `single-cell/rna-velocity` benchmark caveats.)

## 9c. Differential abundance / cell-type composition (NOT in omicverse — use standalone)

> omicverse has `ov.pl.cellproportion` / `ov.pl.bardotplot` for **visualization only**. There is no omicverse wrapper for compositional-aware statistical testing. Do NOT apply plain chi-square / Fisher / t-test to cell-type proportions — they violate the compositional constraint (sum to 1) and inflate false positives.

| Method | Language | When to use | Install |
|---|---|---|---|
| **Milo** (`miloR`) | R | Neighborhood-level DA — does not depend on annotation labels; handles continuous shifts | `install.packages("miloR")` |
| **scCODA** | Python/R | Bayesian compositional analysis; requires a reference cell type | `pip install scCODA` |
| **propeller** | R | Cell-type proportion test with sample-level replicate (limma-backed) | `propeller` (GitHub) |

> R-side `scop::RunProportionTest` is a basic proportion test — use it only for quick looks, not publication. For CNS-grade composition claims, **always** use Milo / scCODA / propeller. (Meta-methodology principle ③ — "who is my N"; enforced in `scripts/postcheck.py` C1 check.)

## 9b. Multi-omics integration (ov.single.* — all wrapped, no separate package needed)

Verified available in omicverse 2.2.3 (`sc` env). Pick by which modalities you have.

### Method selection by modality combination

| You have... | First choice | Notes |
|---|---|---|
| **scRNA + scATAC** (paired Multiome) | `ov.single.GLUE_pair` (regulatory) + SCENIC+ (`single-cell/perturbation-prediction` Route B) | GLUE for cross-modality GRN; SCENIC+ for enhancer-level eRegulons |
| **scRNA + protein (CITE-seq)** | `ov.single.Annotation` (multimodal) + totalVI via `lazy_step_scvi` | WNN alternative in scop: `WNN_integrate` |
| **scRNA + ATAC + protein (≥3 modalities)** | `ov.single.pyMOFA` (joint factor model) | MOFA+ gives shared + modality-specific factors |
| **scRNA + metabolomics** | `ov.single.Metabolism` + `ov.single.MetaboliteCCC` | Metabolic flux + metabolite-based CCC |
| **Bulk RNA + miRNA + methylation (TCGA-style)** | `ov.bulk.pyTCGA` + `ov.bulk.enrichment_multi_concat` | Pan-cancer multi-omics |
| **Multi-omics embedding (any modalities, exploratory)** | `ov.single.pySIMBA` | Joint gene/region/cell embedding; new, use for integration visualization |
| **Causal GRN (any)** | `ov.single.pyCEFCON` | Causal network inference (complements SCENIC+ correlation GRN) |

> **Full per-modality API code** (MOFA+ / GLUE / SIMBA / CITE-seq / Metabolism / CEFCON / TCGA bulk multi-omics) + MuData notes: see `references/multiomics_integration.md`.

> **Spatial multi-omics** (Stereo-seq/Visium HD with multiple modalities) → `spatial/multiomics` (cellpose + SpatialData), not this section.

## 10. Visualization (see visualization/omicverse-plotting)

```python
ov.pl.embedding(adata, basis='X_umap', color='celltype')
ov.pl.dotplot(adata, var_names=markers, groupby='celltype')
ov.pl.violin(adata, keys=['CD3D'], groupby='celltype')
```

## Prerequisites (where inputs come from)

- **Raw single-cell data** (10x MatrixMarket / h5ad / loom) → `ov.read()`
- **Sample metadata** (`obs['sample']`, `obs['batch']`, `obs['condition']`) — required for pseudobulk DE and batch correction
- For multi-sample studies: `batch_key` must be set before QC, otherwise doublet detection across samples explodes false positives

## Decision aid: when to leave this skill

| Need | Go to |
|---|---|
| RNA velocity | `single-cell/rna-velocity` |
| Perturb-seq / CRISPR | `single-cell/perturb-seq` |
| Predict unseen perturbations (in silico) | `single-cell/perturbation-prediction` (linear baseline mandatory) |
| R/Seurat pipeline or scop-only tools (CytoTRACE/Milo/SCENIC+) | `single-cell/scop` |
| Bulk RNA-seq DE / enrichment | `general-bio/omicverse-bulk` |
| Study methodology design | `single-cell/research-planner` |
| Multi-panel figures / graphic summary | `visualization/*` |

## Key pitfalls

- `layers['counts']` MUST be saved **before** `ov.pp.qc`, otherwise DE/velocity have no raw counts. After ambient removal (§1.5), re-store it from the corrected `.X` (`adata.layers['counts'] = adata.X.copy()`) so downstream steps use cleaned counts.
- **Ambient removal order**: §1.5 must run BEFORE §2 QC. Contaminated counts make mt%, doublet rate, and markers misleading. SoupX/FastCAR run on raw counts directly; DecontX/scCDC need a throwaway clustering first (§2-§5 once → decontaminate → re-run §3-§5 on cleaned counts).
- **`tresh` not `mt_thresh`**: `ov.pp.qc` has NO `mt_thresh` parameter — passing it is silently swallowed by `**kwargs`. Use `tresh={'mito_perc': <frac>, ...}` (seurat mode) or `mode='mads', nmads=5` (auto).
- **Default doublet method is `scdblfinder`** (not scrublet) in omicverse 2.2.3 — requires `pyscdblfinder` (auto-falls back to `scrublet` if missing). No need to specify unless you want a different method.
- After scVI integration, recompute every neighbors/umap/leiden on `use_rep='X_scVI'`.
- `ov.pp.leiden(resolution='auto')` depends on an existing neighbors graph — make sure step 4 is done.
- For multi-sample doublet detection always pass `batch_key`, otherwise cross-sample false doublets explode.

## Resources
- `references/ambient_removal.md` — 6-backend ambient RNA removal (soupx/fastcar/decontx/sccdc/cellbender/scar) + diagnostics + when NOT to run
- `references/multiomics_integration.md` — per-modality multi-omics API (MOFA+/GLUE/SIMBA/CITE-seq/Metabolism/CEFCON/TCGA bulk)
- Repo-level: `scripts/api_check.py` (repo root, post-install API self-check), `scripts/postcheck.py` (repo root, scientific-rigor auto-check), `references/preoutput_checklist.md` (repo root)
