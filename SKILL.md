---
name: cns-bio-pilot
description: 生信分析全流程技能库（空间转录组、单细胞、bulk 组学 + 绘图 + 论文/PPT 产出）。当用户要做生信分析、处理单细胞或空转数据、画发表级图表、写论文/PPT 时触发。核心原则：基于事实不懂就问不虚构；不重复造轮子（先检索 PubMed/GitHub/PyPI/R 库是否已有实现，实在没有才改造相似算法，GEO 下载用 GEOparse）；元方法论纪律（主动证伪、链式失效与熔断、环境依赖前置）。本 skill 是路由器——触发后读取它来确定走哪个子 skill，具体分析在子 skill 中进行。
---

# CNS Bio-Pilot — Router

Read this file → pick ONE sub-skill → read that sub-skill's SKILL.md → execute. Never load multiple sub-skills at once.

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
| system R | R-4.3.3 + scop 0.8.9 + Seurat | `"D:\Program Files (x86)\R-4.3.3\bin\Rscript.exe"` |

Package versions: **`compat.yaml`** (single source of truth). After any upgrade: `python scripts/api_check.py --diff`.

## Core Rules (stated once — sub-skills do not repeat these)

1. **Fact-based; ask when unsure; never fabricate.** Every number/dataset/accession/API must have a source. Missing info → `[AUTHOR TO SPECIFY]`.
2. **Pseudobulk for single-cell DE.** Per-cell Wilcoxon inflates false positives. Aggregate by sample×celltype → DESeq2/edgeR.
3. **Search before implementing.** omicverse/scop wrapper → standalone package → R/Bioconductor → adapt → from-scratch (last resort). GEO → GEOparse.
4. **Postcheck is mandatory.** After any quantitative analysis (DE/deconvolution/CCC/composition), run `python scripts/postcheck.py`. FAIL must be resolved before proceeding.
5. **Save checkpoints.** After each major step (QC/cluster/annotation/DE), save `adata.write_h5ad('checkpoints/XX_step.h5ad')`. Upstream changes → re-run from last valid checkpoint.

## Key Files

| File | When to read |
|---|---|
| `compat.yaml` | Version questions; after any package upgrade |
| `references/figure_guide.md` | Before ANY plotting (the only figure reference needed) |
| `references/story_builder.md` | **After analysis, before drawing/writing** — how to turn results into a biological story (5-step method: findings → causal chain → main message → figure mapping → story arc) |
| `references/discovery_miner.md` | **Right after analysis** — scan each result type (DE/proportion/CCC/trajectory/niche) for candidate discoveries, score priority, exclude false positives, determine story level |
| `scripts/cns_style.py` | Import at top of every plotting script |
| `scripts/postcheck.py` | After any analysis (scientific rigor auto-check) |
| `scripts/api_check.py` | After installing/updating omicverse or pertpy |
| `scripts/scop_api_check.R` | After installing/updating scop |
| `references/meta_methodology.md` | Self-check after each analysis step (6 rules) |
| `references/omicverse_guide.md` | When using ov.* APIs (task → API cheat-sheet) |
