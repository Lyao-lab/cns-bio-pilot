---
name: cns-bio-pilot
description: 生信分析全流程技能库（空间转录组、单细胞、bulk 组学 + 绘图 + 论文/PPT 产出）。当用户要做生信分析、处理单细胞或空转数据、画发表级图表、写论文/PPT/汇报、构建生物学故事时触发。触发后读取 SKILL.md 路由到具体子 skill。
compatibility: Requires Python 3.11+ with omicverse/scanpy/scvelo (conda env 'sc'), squidpy (env 'st'), R 4.5.3 with scop 0.8.9. See compat.yaml for version details.
license: GPL-3.0
metadata:
  version: "22.3"
  author: Lyao-lab
---

# CNS Bio-Pilot — Router

Read this file → pick ONE sub-skill → read that sub-skill's SKILL.md → execute (honoring Core Rule 8 batch checkpoints — do not auto-run a pipeline end-to-end). Never load multiple sub-skills at once.

## Routing Table

| Task | Sub-skill | Engine |
|---|---|---|
| scRNA-seq full pipeline (QC→cluster→annotate→DE→CCC→trajectory) | `single-cell/omicverse-pipeline` | omicverse (Python) |
| R/Seurat pipeline or scop-wrapped tools (133 Run\* verbs) | `single-cell/scop` | scop (R) |
| RNA velocity / fate inference | `single-cell/rna-velocity` | omicverse + scvelo |
| Perturbation (measured Perturb-seq OR in silico prediction) | `single-cell/perturbation` | pertpy / CellOracle / scop |
| Study design / research planning (pre-analysis) | `single-cell/research-planner` | zero-code methodology |
| Spatial transcriptomics (Visium/Xenium/Stereo-seq; domains/SVG/CCC) | `spatial/omicverse-spatial` | omicverse ov.space |
| Spatial deconvolution (cell2location/RCTD/Tangram/SPOTlight/CARD) | `spatial/deconvolution` | omicverse / scop |
| High-res spatial (Visium HD/Slide-seq/MERFISH; segmentation/binning) | `spatial/multiomics` | squidpy + spatialdata |
| Spatial proteomics (CODEX/IMC/MIBI) | `spatial/proteomics` | scimap |
| Bulk RNA-seq / pathway / enrichment | `general-bio/omicverse-bulk` | omicverse ov.bulk |
| Cell-type proportion / differential abundance (Milo/scCODA/propeller) | `single-cell/omicverse-pipeline` §9c (or scop RunMilo/RunscCODA) | omicverse / scop |
| CNV inference / inferCNV / copykat | `single-cell/omicverse-pipeline` (or scop RunCNV) | omicverse / scop |
| **Figures** (iterative: design A → look → adjust B → ... → assemble) | `visualization/figure-production` | cns_style.py + ov.pl |
| Schematics / mechanism diagrams / graphical abstract | `visualization/scientific-schematics` | AI + matplotlib |
| **Manuscript writing** (Methods / Results / Figure Legends) | `presentation/manuscript-writing` | LLM |
| Slides (lab meeting / conference / defense) | `presentation/scientific-slides` | python-pptx / Beamer |

## Environments

| Env | Contents | Activate |
|---|---|---|
| `sc` | omicverse (see `compat.yaml`) + scanpy + scvelo + scvi + tangram + spatialdata + pertpy + decoupler | `conda activate sc` |
| `st` | squidpy (older scanpy) | `conda activate st` |
| `scop_env` (conda) | R 4.5.3 + scop 0.8.9 + Seurat | `~/miniforge3/envs/scop_env/bin/Rscript` |

Package versions: **`compat.yaml`** (single source of truth). After any upgrade: `python scripts/api_check.py --diff`.

## Core Rules (stated once — sub-skills do not repeat these)

1. **Fact-based; ask when unsure; never fabricate.** Every number/dataset/accession/API must have a source. Missing info → `[AUTHOR TO SPECIFY]`.
2. **Pseudobulk for single-cell DE.** Per-cell Wilcoxon inflates false positives. Aggregate by sample×celltype → DESeq2/edgeR.
3. **Search before implementing.** omicverse/scop wrapper → standalone package → R/Bioconductor → adapt → from-scratch (last resort). GEO → GEOparse.
4. **Postcheck is mandatory** *(automated, per-analysis)*. After any quantitative analysis (DE/deconvolution/CCC/composition), run `python scripts/postcheck.py`. FAIL must be resolved before proceeding.
5. **Save checkpoints.** After each major step (QC/cluster/annotation/DE), save `adata.write_h5ad('checkpoints/XX_step.h5ad')`. Upstream changes → re-run from last valid checkpoint.
6. **Runtime API self-adaptation.** Do NOT trust hardcoded version numbers or assume API signatures. Before calling any ov.*/pt.*/sc.* function for the first time, verify with `inspect.signature(func)`. Run `python scripts/api_check.py --diff` after any package upgrade.
7. **Step-gate + hypothesis ledger** *(agent self-check, per-step)*. Every analysis follows meta_methodology §7 (step-gate sanity checks after each step) and §8 (hypothesis ledger + provenance + conclusion grading).
   > *Rationale*: The planner-verifier dual loop is the proven-optimal pattern for bioinformatics agents (K-Dense Analyst outperforms single-model by 6 points on BixBench via per-step verification).
8. **Result-driven iteration** *(human gate, per-batch)*. Biology is evidence-driven, NOT linear like software. After each analysis batch: review results → **discuss direction with researcher** → revise plan → next batch. Pause for researcher input on decisions that need human judgment (cell-type naming, which signal to chase, threshold calibration). Full procedure: `research-planner` Phase R.
   > *Rationale*: A pipeline that auto-runs QC→cluster→DE→CCC→figures without pausing to interpret results produces data dredging, not science.

## Key Files

| File | When to read |
|---|---|
| `compat.yaml` | Version questions; after any package upgrade |
| `references/figure_guide.md` | Before ANY plotting — visual specs, three iron rules, real-world lessons (no code) |
| `references/plotting_reference.md` | When writing plotting code — runnable templates for every chart type (§0 quick card → §2/§3 templates) |
| `references/omicverse_skills_examples.md` | External reference — curated patterns from omicverse-skills repo (marked "absorbed" vs "reference") |
| `references/story_builder.md` | **After analysis, before drawing/writing** — how to turn results into a biological story (5-step method: findings → causal chain → main message → figure mapping → story arc) |
| `references/discovery_miner.md` | **Right after analysis** — scan each result type (DE/proportion/CCC/trajectory/niche) for candidate discoveries, score priority, exclude false positives, determine story level |
| `scripts/cns_style.py` | Import at top of every plotting script (26 helpers + 18 smart_plot entry points: plot_umap/volcano/dotplot/...) |
| `scripts/postcheck.py` | After any analysis (scientific rigor auto-check) |
| `scripts/api_check.py` | After installing/updating omicverse or pertpy |
| `scripts/scop_api_check.R` | After installing/updating scop |
| `references/meta_methodology.md` | Self-check after each analysis step (8 rules + step-gate + hypothesis ledger) |
| `references/omicverse_guide.md` | When using ov.* APIs (task → API cheat-sheet) |
