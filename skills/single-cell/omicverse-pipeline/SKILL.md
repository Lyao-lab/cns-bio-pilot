---
name: omicverse-single-cell-pipeline
description: 单细胞全流程（QC→doublet→降维聚类→注释→批次校正→通讯→轨迹）+ 多组学整合（MOFA+/GLUE/CITE-seq/代谢/SIMBA/CEFCON）基于 OmicVerse V2 统一 API，无需在 scanpy/Seurat/scVI/CellTypist 间切换。一个 import omicverse as ov 覆盖 90% 常规分析。当用户要做单细胞、scRNA、多组学、CITE-seq、scRNA+ATAC、代谢、MOFA、GLUE 时触发。
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
    doublets_method='scrublet',     # 'scrublet' | 'scdblfinder' | 'doubletfinder'
    batch_key='sample',             # REQUIRED for multi-sample: detect doublets per batch
    filter_doublets=True,
    mt_thresh=<VALUE_FROM_DIAGNOSTIC>,   # YOU choose after Step 2a; see tissue table below
)
# adds to adata.obs: n_genes_by_counts, total_counts, pct_counts_mt, predicted_doublet
```

> **⚠️ Do NOT use `mt_thresh=20` blindly.** 20% is wrong for liver (too strict — kills real hepatocytes), wrong for brain (too loose — keeps dying neurons), wrong for nuclei (any mt% = contamination). The only honest workflow is: plot → find knee → check tissue table → document your choice.

> **Ambient RNA removal (FFPE / nuclei / low-quality runs)**: `ov.pp.qc` does **not** remove ambient RNA (cell-free mRNA contaminating droplets). For FFPE, nuclei, or high-background data, run **CellBender** (remove-background, [Cargnelli et al. 2026 7-tool benchmark](https://www.biorxiv.org/content/10.64898/2026.01.13.699237v1) — gold standard) on the raw feature-barcode matrix **before** loading into omicverse. SoupX / DecontX are faster alternatives. Skipping ambient removal → marker scores inflated, doublet rates misleading, DE contaminated.

Decision: scrublet default (fast, pure Python). doubletfinder (R engine, needs R) usually matches Seurat.

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

## 9b. Multi-omics integration (ov.single.* — all wrapped, no separate package needed)

Verified available in omicverse 2.2.3 (`sc` env). Pick by which modalities you have:

```python
import omicverse as ov

# === MOFA+ : multi-omics factor analysis (RNA + ATAC + protein, joint factor model) ===
mofa = ov.single.pyMOFA(omics=[adata_rna, adata_atac],
                        omics_name=['RNA','ATAC'])   # builds MuData internally
mofa.train(); mofa.save('mofa_model')
# Load a pretrained model: mofa = ov.single.pyMOFAART('mofa_model')

# === GLUE : RNA + ATAC regulatory inference (cross-modality GRN) ===
ov.single.GLUE_pair(adata_rna, adata_atac)   # or ov.single.glue_pair(...)

# === SIMBA : multi-omics embedding integration (gene/region/cell joint space) ===
simba = ov.single.pySIMBA(mdata, workdir='simba_result')

# === CITE-seq / multimodal annotation (ADT + RNA) ===
# ov.single.Annotation accepts multi-modal AnnData; CITE-seq protein markers sharpen labels
# For totalVI/MultiVI (scvi-tools), call via ov.single.lazy_step_scvi (lazy-loaded)

# === Metabolism + metabolite-based cell-cell communication ===
ov.single.MetaboliteCCC(adata)               # metabolite ligand-receptor CCC (note: Metabol**i**teCCC)
ov.single.Metabolism(adata)                  # per-cell metabolic flux scoring
ov.single.differential_metabolism(adata, ...) # condition-comparison metabolism

# === Causal GRN (multi-omics causal network inference) ===
ov.single.pyCEFCON(adata)                    # causal regulatory network

# === Bulk multi-omics (TCGA pan-cancer, cross-omics correlation) ===
ov.bulk.pyTCGA(...)                          # TCGA multi-omics download + integrate
ov.bulk.enrichment_multi_concat(...)         # cross-pathway / cross-omics enrichment concat
ov.bulk.geneset_plot_multi(...)              # multi-omics pathway heatmap
```

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

> **Muon / MuData**: omicverse does NOT expose `muon` / `MuData` at the top level (`ov.muon` / `ov.MuData` both return False). For direct MuData manipulation, `pip install muon` and use its native API; `ov.single.pyMOFA` builds MuData internally so you usually don't need to.

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

- `layers['counts']` MUST be saved **before** `ov.pp.qc`, otherwise DE/velocity have no raw counts.
- After scVI integration, recompute every neighbors/umap/leiden on `use_rep='X_scVI'`.
- `ov.pp.leiden(resolution='auto')` depends on an existing neighbors graph — make sure step 4 is done.
- For multi-sample doublet detection always pass `batch_key`, otherwise cross-sample false doublets explode.
