---
name: cns-bio-pilot
description: 生信分析全流程技能库（空间转录组、单细胞、bulk 组学 + 绘图 + 论文/PPT 产出）。当用户要做生信分析、处理单细胞或空转数据、画发表级图表、写论文/PPT 时触发。核心原则：基于事实不懂就问不虚构；不重复造轮子（先检索 PubMed/GitHub/PyPI/R 库是否已有实现，实在没有才改造相似算法，GEO 下载用 GEOparse）；元方法论纪律（主动证伪、链式失效与熔断、环境依赖前置）。本 skill 是路由器——触发后读取它来确定走哪个子 skill，具体分析在子 skill 中进行。
---

# CNS Bio-Pilot

Single-cell + spatial transcriptomics (with bulk / other omics) bioinformatics skill library. Three engines: **OmicVerse** (Python, default) + **scop** (R/Seurat) + perturbation models (GEARS/CPA/scGPT, with mandatory linear baseline). This file is a **router** — read it to pick the right sub-skill; do not run analysis here.

## Loading Protocol (rationale flows through the rest)

1. **Always read only**: this SKILL.md + the **one** matched sub-skill + that sub-skill's declared references
2. **Never load multiple sub-skills at once** — context window gets consumed, both routing judgement and code quality degrade
3. Sub-skill paths live in `skill-index.json` (compact index) or the routing tables below
4. References/scripts inside a sub-skill are **read on demand**, not pre-loaded
5. **Path resolution for `references/X.md` / `scripts/X.py`**: a sub-skill may cite shared repo-root files (`references/figure_aesthetics.md`, `scripts/postcheck.py`, etc.) using a bare relative path. **Resolve these against the repo root**, not the sub-skill's own directory. A sub-skill's OWN references (e.g. `skills/single-cell/scop/references/run_verbs_reference.md`) sit inside that sub-skill folder. When ambiguous, the citation says "top-level" or "(repo root)" explicitly; otherwise check both locations and use whichever exists.

## Quick Route — read this first (6 steps)

```
① Identify data type   → see "Routing: data-type axis"
② Identify task        → see "Routing: task axis"
③ ①×② cross-match      → lock the sub-skill path
④ Pre-Routing Checks   → confirm environment / data prerequisites (below)
⑤ Read matched sub-skill SKILL.md → execute
⑥ Postcheck            → run scripts/postcheck.py to verify scientific rigor
```

## Pre-Routing Checks (run before routing)

### Environment prerequisites (conda env mapping)

Different tasks live in different conda envs; wrong env → `ModuleNotFoundError`. **Spatial work is split across two envs — read the package, not the task label** (squidpy-only analyses live in `st`; everything touching omicverse/tangram/spatialdata lives in `sc`):

| Task / package | conda env | Verified contents (2026-07-25 audit) | Activate |
|---|---|---|---|
| Single-cell (omicverse) | `sc` | omicverse (version: `compat.yaml`) · scanpy · scvelo · anndata · scvi · tangram · spatialdata | `conda activate sc` |
| Spatial — `ov.space.*` / Tangram / spatialdata / cell2location | `sc` | (same as above; **squidpy is NOT in sc**) | `conda activate sc` |
| Spatial — squidpy-only (`sq.gr.*` / `sq.im.*` / `sq.pl.*`) | `st` | squidpy 1.2.2 · scanpy 1.9.6 · anndata 0.9.2 (**older** than sc) | `conda activate st` |
| R / Seurat / scop | system R (not conda) | R 4.3.3 / R 4.5.1 at `D:\Program Files (x86)\R-*` — **scop 0.8.9 installed** (verified 2026-07-26: 314 exports / 133 Run\*); `scop_env` conda env exists but has no R, so use the system Rscript directly | `"D:\Program Files (x86)\R-4.3.3\bin\Rscript.exe"` |
| Packages NOT auto-installed in either env | per-analysis | `spatialdata-io` / `bin2cell` / `cellpose` / `scimap` — `pip install` into the env named by the example's header | — |

> **2026-07 correction**: cell2location + scvi + omicverse coexist in the `sc` env — **no separate c2l env needed** (the early anndata 0.10.x pin conflict is resolved since omicverse ≥2.2). Deconvolution uses `ov.space.Deconvolution.deconvolution(method='cell2location')`.

> **st env is squidpy-only and older** (scanpy 1.9.6 / anndata 0.9.2) — if a squidpy example also imports scanpy APIs newer than 1.9, prefer running squidpy inside `sc` after `pip install squidpy` there. The split exists for dependency isolation, not as a hard rule.

> **R/scop runs via system R, not conda**: `scop_env` (conda) has no R installed; the working scop installation is in **system R** at `D:\Program Files (x86)\R-4.3.3\` and `R-4.5.1\` (scop 0.8.9 in R-4.3.3's library; R-4.5.1 may have an older/broken scop due to GenomeInfoDb incompatibility — prefer R-4.3.3). Invoke scop scripts with the full Rscript path, e.g. `"D:\Program Files (x86)\R-4.3.3\bin\Rscript.exe" scripts/scop_api_check.R`. Verified 2026-07-26: scop_api_check.R green on 0.8.9.

> postcheck.py must also run in an env **with anndata installed** (e.g. `sc`), otherwise "anndata not found".

### Data / code prerequisites

Surface landmines **before** routing — these are the root cause of most bioinformatics errors:

| Check | How | If not satisfied |
|---|---|---|
| **Raw counts preserved?** | `'counts' in adata.layers` | **Life-or-death for DE / velocity** — back up first via `adata.layers['counts']=adata.X.copy()`; once normalization overwrites `.X`, DESeq2 / NB models and velocity inference both break |
| **Multiple batches?** | `adata.obs['batch'].nunique()>1` | Decides whether batch_correction is needed; **never DE on batch-corrected embedding** — it removes real biological signal, including disease signal |
| **Data size** | `adata.n_obs` | >100k → consider AnnDataOOM (`ov.read(backend='rust')`) |
| **Env ready** | `python -c "import omicverse"` | Missing package → see sub-skill's install section |
| **GPU** (DL tasks) | `torch.cuda.is_available()` | scGPT/GEARS finetune need GPU; otherwise fall back to CPU or switch methods |
| **spliced/unspliced** (velocity) | `'spliced' in adata.layers` | scvelo requires it; missing → run velocyto/kb_python first |

## Routing: data-type axis (judge this first)

```
Data has spatial coords / tissue image?
├─ YES → spatial transcriptomics route (spatial/)
└─ NO → has cell × gene matrix?
        ├─ YES (single-cell level) → single-cell route (single-cell/)
        └─ NO  (sample-level matrix) → general bioinformatics route (general-bio/)
```

## Routing: task axis (then this)

| Task | single-cell | spatial | bulk / general |
|---|---|---|---|
| QC + clustering + annotation | `single-cell/omicverse-pipeline` | `spatial/omicverse-spatial` | — |
| Batch integration | `single-cell/omicverse-pipeline` (Harmony/scVI) | — | `general-bio/omicverse-bulk` |
| Cell-type annotation | `single-cell/omicverse-pipeline` (CellTypist/SingleR/scmulan) | — | — |
| Pseudobulk DE | `single-cell/omicverse-pipeline` | — | `general-bio/omicverse-bulk` (pyDESeq2) |
| Trajectory / fate | `single-cell/omicverse-pipeline` (CellRank 2) → `single-cell/rna-velocity` if S/U available | — | — |
| Cell-cell communication | `single-cell/omicverse-pipeline` (LIANA consensus / CellPhoneDB v5) | `spatial/omicverse-spatial` (COMMOT) | — |
| Perturbation prediction (in silico) | `single-cell/perturbation-prediction` | — | — |
| Perturb-seq analysis (real data) | `single-cell/perturb-seq` | — | — |
| Deconvolution | — | `spatial/deconvolution` (cell2location/Tangram/RCTD/Starfysh/flashdeconv) | — |
| Spatial domains / SVG | — | `spatial/omicverse-spatial` (STAGATE/MENDER/BANKSY/SpatialGlue) | — |
| High-resolution platforms | — | `spatial/multiomics` (cellpose / SpatialData) | — |
| Spatial proteomics (CODEX/IMC) | — | `spatial/proteomics` (scimap) | — |
| Pathway / enrichment | — | — | `general-bio/omicverse-bulk` (GSEApy/decoupler) |

> **Figure production pipeline (run in this order, not in parallel)**:
> ① **`presentation/figure-architect`** — FIRST, after all analysis is done. Designs the narrative spine + panel logic + pre-build review → produces `outline.json`.
> ② **`visualization/omicverse-plotting`** — renders EACH panel **independently** (one `plt.figure()` per panel → `savefig` → `plt.close()`). Each panel verified for aesthetics/proportions **before** assembly. If a panel looks wrong, re-render THAT panel (not the whole figure).
> ③ **`visualization/multi-panel-figures`** — assembles the **pre-rendered, pre-verified** panel files (PDF/PNG) into a 6-panel A–F composite. Assembly is a layout operation on finished images — it does NOT draw or modify panel content.
> A single panel only → ② directly (skip ①③). A full main figure → ①→②→③. **Never skip ②'s independent verification** — "draw-and-assemble simultaneously" locks bad proportions into the composite.

| Plotting (UMAP / volcano / heatmap / dot / violin) | `visualization/omicverse-plotting` (ov.pl.*) | same | same |
| Multi-panel A–F assembly | `visualization/multi-panel-figures` | same | same |
| **Main figure deep design** (summarize results → narrative spine → panel design → pre-build review → outline.json) | `presentation/figure-architect` | same | same |
| Schematic / mechanism / graphical abstract | `visualization/scientific-schematics` | same | same |
| Lab meeting / progress deck | `presentation/scientific-slides` (lab-meeting mode) | same | same |
| Formal talk (conference / defense) | `presentation/scientific-slides` | same | same |
| Methods / Results / Legend writing | `presentation/{methods,results,figure-legend}-writer` | same | same |
| Study design (pre-analysis) | `single-cell/research-planner` | same | same |
| R / Seurat pipeline, or scop-wrapped tools (CytoTRACE/Palantir/CellChat/Monocle3/SCVELO) | `single-cell/scop` | `single-cell/scop` | — |

### Special Routing Rules (override the table above)

- **Any DE** → first confirm `layers['counts']` exists; single-cell DE uses pseudobulk, **not** per-cell Wilcoxon — per-cell assumes independence and inflates degrees of freedom, systematically understating p-values (false positives ↑)
- **cell2location deconvolution** → `spatial/deconvolution` (`ov.space.Deconvolution.deconvolution(method='cell2location')` — 5 methods unified; no separate env needed since 2026-07)
- **After batch correction** → embedding (`X_scVI` / `X_harmony`) is for visualization / clustering only — it removes real biological signal, using it for DE / enrichment also strips disease signal
- **RNA velocity** → requires spliced/unspliced layers; missing → run velocyto first; without splice kinetics you can only do pseudotime
- **Foundation models (scGPT/Geneformer/UCE)** → not yet wrapped in omicverse (`ov.fm` does **not** exist as of `compat.yaml` verified version); use as standalone packages; **always run a linear baseline** for perturbation prediction (Nature Methods 2025)

## When to Use / When NOT to Use (engine choice)

| Use engine | When |
|---|---|
| **OmicVerse** (Python default) | 90% of routine analyses; `ov.pp.*` / `ov.single.*` / `ov.bulk.*` / `ov.pl.*` cover QC → batch → annotation → DE → trajectory → comm → plotting |
| **scop** (R/Seurat) | R ecosystem. Since **0.8.9 scop wraps 133 Run\* verbs** covering nearly all common tools (CytoTRACE/Palantir/CellChat/Monocle3/SCVELO/WOT/Slingshot/PAGA, **plus newly-wrapped SCENIC+/Milo/scCODA/RCTD/BANKSY/SecAct/EcoTyper/Giotto/SmoothClust/CARD/SPOTlight/CNV/GSVA/Dorothea/Augur/scTenifoldKnk and more**). Remaining NOT-wrapped: moscot / CellOracle / SpatialGlue / MENDER / BINARY / GraphST / COMMOT / Baysor / bin2cell / cellpose → standalone |
| **Perturbation models** | Predicting unseen perturbations via two routes — `single-cell/perturbation-prediction`: (A) ML-based GEARS/CPA/scGPT/scGen needs Perturb-seq training, **linear baseline mandatory**; (B) GRN-based virtual KO via CellOracle/SCENIC+/scTenifoldKnk needs only WT scRNA-seq, infers GRN then simulates KO. Pick by data availability |

## Core Principles (rationale flows through; ✅ = postcheck.py machine-checkable)

1. **Fact-based; ask when unsure; never fabricate**: every dataset name / accession / sample size / cell-type label / tool parameter / biological conclusion must have a source — from the data itself, official docs, or literature. **Ask the user when uncertain, never guess.** Never fabricate dataset metadata, accession numbers, sample availability, citations, API signatures, or analysis results. Verify uncertain API parameters via `inspect.signature(func)` or `help()`, never call from memory ✅
2. **Don't reinvent the wheel; search before implementing**: before implementing any method, **first search** for existing implementations — check PubMed, GitHub (`awesome-single-cell` / topic awesome lists), PyPI (use [libraries.io](https://libraries.io) / Bioconda), CRAN/Bioconductor, and whether omicverse/scop already wraps it. Search order: **omicverse/scop wrapper > mature standalone package > R/Bioconductor > adapt similar algorithm > from-scratch implementation**. Only when no existing method is confirmed, adapt the most similar algorithm; document "adapted from X" + differences in the report. **From-scratch is the last resort — explain why no existing method fits**. Use GEOparse for GEO downloads, never self-write a downloader
3. **Real data first**: mocks for testing only
4. **Statistical rigor**: single-cell DE uses pseudobulk ✅; FDR correction (BH) ✅; report total tests
5. **Strict thresholds**: DE Padj<0.05 & |Log2FC|>1.0 ✅; correlation Padj<0.05 & |r|>0.5
6. **Association ≠ causation**: use "associated with" ✅; no "regulates/causes" without experimental evidence
7. **Python first**: omicverse (already ports Monocle/WGCNA/DoubletFinder); R only when no equivalent — paired with Principle 2: first check omicverse/scop wrapping
8. **Batch correction discipline**: corrected embedding never used for DE / enrichment — correction aims to remove batch, but also removes real biological signal, so feeding it back to DE strips disease signal too ✅
9. **Conservative wording**: biomarkers require validation cohort; prefer "potential candidate"
10. **Reproducibility**: keep `layers['counts']` ✅; record versions and seeds ✅
11. **Spatial-specific**: deconvolution must report quality assessment ✅; spatial domains require biological validation
12. **Publication-grade figure aesthetics**: follow CNS figure guidelines — 300 DPI+, Arial/Helvetica, dual-track palette (discrete = Morlandi Nord soft; continuous expression = Morlandized blue-yellow-red, low saturation, low=blue / mid=cream / high=dark red; divergent log2FC = blue-white-red), vector PDF preferred, color consistency across panels. See `references/figure_aesthetics.md`. After `ov.plot_set()`, manually add DPI=300 + dual-track palette + font.type=42 ✅
13. **Meta-methodology discipline (how to find & solve problems)**: code "runs" ≠ result correct; LLM output is draft, not answer. Six meta-rules to self-check throughout — ① **Verify prerequisites** (every method/API/LLM conclusion has hidden assumptions; verify before use), ② **Make semantic boundaries explicit** (the same data has different semantics in different uses; corrected matrix ≠ raw counts, normalized ≠ count, inference ≠ measurement), ③ **What is N** (cell ≠ donor; pseudoreplication is the most common single-cell DE error), ④ **Report the path, not just the endpoint** (sensitivity analysis + report total attempts; method choice based on independent objective criteria), ⑤ **Chain failure & circuit-breaker** (one upstream change → recompute all downstream; same step retried ≥3 times → stop and root-cause; lock versions + verify external deps in real time), ⑥ **Design prerequisites up front** (are batch/condition separable? does reference match? enough replicates? deps installed? — design problems cannot be rescued at analysis stage). See `references/meta_methodology.md` — **six self-check questions after each analysis step**.

> ✅ = `scripts/postcheck.py` auto-checks; the rest are manual. **Always run postcheck after analysis.**

## Version & architecture

- **Version**: 18.0.0 (version management architecture — **never hardcode package versions again**. Three mechanisms: ① `compat.yaml` — single source of truth for all package versions (replaces 30 scattered "2.2.4" strings); ② `api_check.py --diff` — version mismatch detection that reports exactly what changed (removed/new APIs + files to update) in one command; ③ routing-layer de-versioning — SKILL.md/references/examples no longer pin versions, they reference `compat.yaml`. Also includes: omicverse upgraded 2.2.4→2.3.1 (verified 0 breaking changes via --diff; new modules ov.agent/ov.airr are out of skill scope); advanced figure aesthetics v17.1-17.2 (positive design layer + cns_style.py with journal presets/mplstyle export/seaborn integration, absorbed from SciencePlots 9k★ + Rougier 11k★ philosophy).)

<!-- v18.0: 2026-07-31, version management architecture (compat.yaml + api_check --diff + de-versioning) + omicverse 2.3.1 -->
<!-- v17.2: 2026-07-26, deep-integrate SciencePlots/Rougier into cns_style (journal presets + mplstyle + seaborn) -->
<!-- v17.1: 2026-07-26, advanced figure aesthetics — positive design layer (color narrative / polish_axes / anchor panels) -->
<!-- v17.0: 2026-07-26, scop 0.8.0→0.8.9 — 133 Run* verbs, rewrote scop skill + 7 cross-refs -->
<!-- v16.0.1: 2026-07-25, correct v16.0 R/scop search-method error — scop IS installed in system R -->
<!-- v16.0: 2026-07-25, deep audit — 3-round review fixed 3 P0 code bugs + env honesty + doc consistency -->
<!-- v15.2: 2026-07-24, omicverse 2.2.3→2.2.4 upgrade + GASTON wrapper added -->
<!-- v15.1: 2026-07-21, narrative+API audit patch (scope: surface files + 3 surviving fabricated APIs + checker hardening) -->
<!-- v15.0: 2026-07-21, capability honesty — scop 40-verb truth + pertpy 1.0 + postcheck D4/L2/C1 + compositional §9c + scop_api_check.R -->
<!-- v14.0: 2026-07-21, code externalization — SKILL.md → examples/ + references/ -->
- **Engines**: [OmicVerse V2](https://github.com/Starlitnightly/omicverse) (Python primary) + [scop](https://github.com/mengxu98/scop) (R/Seurat) + perturbation models (GEARS/CPA/scGPT, mandatory linear baseline)
- **Sub-skills**: 19 (see `skill-index.json` compact index)
- **Architecture evolution**: v8 (42 standalone) → v9 (omicverse unification + scop + perturbation track) → v10 (structural engineering: routing / closed-loop / protocol) → v11 (consolidation + meta-methodology + English rewrite) → v12–v13 (annotation principles / QC two-step / figure-architect) → **v14 (code externalization — SKILL.md back to routing + decisions, code to examples/, API references to references/)**

### Refactor / dedup record (v8 → v11 merge history)

| Conflict / original skill | Decision |
|---|---|
| scanpy + preprocessing/doublet/clustering/annotation/integration/communication/trajectory + scvi-tools | **All merged into** `single-cell/omicverse-pipeline` (OmicVerse V2 `ov.pp.*`/`ov.single.*` unified) |
| scvelo | **Rewritten as** `single-cell/rna-velocity` (`ov.single.Velo` 5 engines + CellRank + 6 fallbacks) |
| spatial preprocessing/io/domains/neighbors/stats/viz/comm/image | **Merged into** `spatial/omicverse-spatial` (deconvolution split out as `spatial/deconvolution`) |
| DE/gokegg/gsea/wgcna/ppi/batch-correction(-de) | **Merged into** `general-bio/omicverse-bulk` (pure Python, no R) |
| heatmap/volcano/specialized/interactive | **Merged into** `visualization/omicverse-plotting` (`ov.pl.*`) |
| **v11 new merge**: graphical-abstract | into `visualization/scientific-schematics` (graphical-abstract mode + reference) |
| **v11 new merge**: lab-meeting-slides | into `presentation/scientific-slides` (lab-meeting mode + 9 steps + 7 rules) |
| **v14 code externalization**: SKILL.md → examples/ + references/ | `perturb-seq`/`multiomics` code → `examples/`; `scop` Run\* enumeration → `skills/single-cell/scop/references/run_verbs_reference.md`; `omicverse-pipeline` §1.5 ambient + §9b multi-omics → `skills/single-cell/omicverse-pipeline/references/ambient_removal.md` + `skills/single-cell/omicverse-pipeline/references/multiomics_integration.md`. SKILL.md keeps only canonical entry snippets + decision tables + pitfalls. |
| Irreplaceable (kept standalone) | deconvolution / multiomics / proteomics / perturb-seq / perturbation-prediction / research-planner / multi-panel-figures / scientific-schematics / scientific-slides / methods-writer / results-writer / figure-legend-writer |

## Index file roles

| File | Role | When to read |
|---|---|---|
| `SKILL.md` (this file) | **Routing authority** | Always read first |
| `skill-index.json` | Compact index (name/triggers/engine/path/data_type) | When you need to locate a sub-skill quickly |
| `compat.yaml` | **Single source of truth for package versions** (omicverse/pertpy/scop/squidpy/scanpy/anndata/spatialdata) | Check before any "which version" question; update after any package upgrade |
| `references/workflow_routing.md` | Routing decision tree + Signal Patterns trap table | When the routing table match is ambiguous and needs refinement |
| `references/omicverse_guide.md` | OmicVerse API cheat-sheet (task → API mapping) | When using ov.* |
| `references/figure_aesthetics.md` | CNS publication-grade plotting spec (size / font / dual-track palette / CJK fallback / title & legend non-overlap) | **Must read before any plotting** |
| `references/figure_layout.md` | Multi-panel composition (omicverse 5 signature decisions / shared legend / panel labels / 5 composite templates) | **When assembling multi-panel figures** |
| `references/figure_design.md` | Chart-type selection + information hierarchy + statistics visualization (what to plot, take-home message, error bars, n, self-contained legend) | **Must read before any plotting — the design layer above aesthetics** |
| `references/figure_aesthetics_advanced.md` | **Positive design layer** (color narrative / saturation hierarchy / 5+1 rule / `polish_axes()` / anchor panels / whitespace philosophy / typographic rhythm / report-level narrative arc / manifest.yaml) | **When making figures beautiful, not just compliant** |
| `references/figure_recipes.md` | **Visual recipe book** — exact specs (figsize/point size/alpha/colors/labels) + runnable code for each bio figure type (UMAP / volcano / heatmap / dotplot / violin / spatial / bar / chord / trajectory / feature plot) | **When drawing a specific figure type — "how should this concretely look?"** |
| `references/meta_methodology.md` | **Meta-methodology 6 rules** (verify prerequisites / semantic boundaries / what is N / report the path / chain failure / design up front) | Self-check checklist after each analysis step |
| `references/preoutput_checklist.md` | Shared 5-bullet core pre-output checklist (numeric integrity / citation / no speculation / association≠causation / no fabrication) | **Before delivering any result** (referenced by 6+ output skills) |
| `scripts/postcheck.py` | Scientific rigor auto-check (counts / Padj / pseudobulk / CCC hypothesis / compositional / deconv quality) | **Must run after analysis** |
| `scripts/api_check.py` | API existence self-check (verify all `ov.*` and `pt.*` in skill docs actually exist in current env) | **Run after installing/updating omicverse or pertpy** |
| `scripts/scop_api_check.R` | scop API existence self-check (R; verify Run\* verbs against installed scop) | **Run after installing/updating scop** |
| `scripts/cns_style.py` | One-shot CNS aesthetics (`set_cns_style()` / `polish_axes()` / `add_elegant_colorbar()` / `safe_scanpy_plot()` / `apply_5plus1_palette()` / `clean_umap_axes()` / `optical_margin()` / `add_panel_label()`) | **Import at top of every plotting script** |
