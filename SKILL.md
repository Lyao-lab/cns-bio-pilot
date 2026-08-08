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

## ⚠️ Dispatch Injection (read before delegating ANY sub-task)

When you delegate any analysis/plotting/API-calling work to a sub-agent (worker/researcher/explore), the sub-agent does NOT load this skill and cannot see this conversation. **Rules not written into the dispatch prompt do not exist for the sub-agent.** Before every dispatch, append one of:

- **(default)** `开工前读 <skill根目录>/references/dispatch_cheatsheet.md 并遵守 A-D 全部硬规则。特别注意：[本任务最相关的 2-3 条编号]。`
- **(narrow task)** paste the 2-3 relevant rules directly (e.g. `[A2] pseudobulk DE; [A4] 批次校正后禁 DE`)
- **(needs decision table)** `开工前读 <skill根目录>/references/figure_guide.md §0.1 数据→图型决策表`

`dispatch_cheatsheet.md` condenses the 26 hard rules (A 分析严谨性 9 / B 绘图 7 / C API 4 / D 迭代 6) from 7 reference files into 75 lines — one reference replaces hand-writing 30 rules every time. **Skipping injection = the sub-agent will violate rules it never saw.**

## Quick Route（关键词→子skill 索引，borrowed from Biomni prompt-retriever）

用户说短句时按关键词快速命中，无需扫全表：

| 关键词 | 子skill |
|---|---|
| umap / tsne / 聚类 / 分群 / annotate / 注释 | `single-cell/omicverse-pipeline` §2-4 |
| 差异基因 / DE / volcano / marker / 筛选 | `omicverse-pipeline` §8.5 |
| 细胞比例 / 组成 / Milo / 丰度 / proportion | `omicverse-pipeline` §9c |
| 通讯 / CCC / CellChat / LR / ligand | `omicverse-pipeline` §9 |
| 空间 / Visium / 空转 / Xenium / spot / spatial | `spatial/omicverse-spatial` |
| 空间 domain / niche / 区域 / STAGATE / CAST | `spatial/omicverse-spatial` §domain |
| 共定位 / colocalization / 空间邻近 / 邻域富集 / nhood | `spatial/omicverse-spatial` §统计（nhood_enrichment/co_occurrence）|
| 空间变异基因 / SVG / spatial variable / Moran | `spatial/omicverse-spatial` §SVG（svg/spatial_autocorr/sepal）|
| 空间统计 / Ripley / centrality / 空间分布 | `spatial/omicverse-spatial` §统计（ripley/centrality_scores）|
| 去卷积 / cell2location / deconv / Tangram | `spatial/deconvolution` |
| 高分空转 / Visium HD / Stereo-seq / MERFISH | `spatial/multiomics` |
| 蛋白组 / CODEX / IMC / MIBI | `spatial/proteomics` |
| 速度 / velocity / RNA velocity / fate | `single-cell/rna-velocity` |
| 扰动 / Perturb-seq / perturbation | `single-cell/perturbation` |
| R / Seurat / scop | `single-cell/scop` |
| bulk / 路径 / 通路 / enrichment / 富集 | `general-bio/omicverse-bulk` |
| CNV / inferCNV / copykat | `omicverse-pipeline` |
| 转录因子 / TF / regulon / SCENIC / GRN | `omicverse-pipeline` §SCENIC（ov.single.SCENIC）|
| 生存分析 / survival / KM / Kaplan | `general-bio/omicverse-bulk`（ov.pl.kaplan_meier/survival）|
| 画图 / 绘图 / figure / panel / 拼图 | `visualization/figure-production` |
| 机制图 / 流程图 / schematic / 图形摘要 | `visualization/scientific-schematics` |
| PPT / 汇报 / 幻灯片 / slides / 答辩 | `presentation/scientific-slides` |
| 网页报告 / HTML / report / 在线分享 / web report | `presentation/web-report` |
| 论文 / manuscript / methods / 写作 | `presentation/manuscript-writing` |
| 研究设计 / 规划 / study design | `single-cell/research-planner` |

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
| Schematics / mechanism diagrams / graphical abstract | `visualization/scientific-schematics` | matplotlib + networkx (纯代码模板) |
| **Manuscript writing** (Methods / Results / Figure Legends) | `presentation/manuscript-writing` | LLM |
| Slides (lab meeting / conference / defense) | `presentation/scientific-slides` | python-pptx / Beamer |
| **Web report** / HTML report / 在线分享结果 | `presentation/web-report` | Python 标准库（自包含 HTML）|

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
4. **Postcheck is mandatory** *(automated, per-analysis)*. After any quantitative analysis (DE/deconvolution/CCC/composition), run `python scripts/postcheck.py`. FAIL must be resolved before proceeding. **Acceptance gate**: when the main agent accepts a worker's bioinformatics deliverable, it must confirm the matching machine-check has run and PASSED — `postcheck.py` after DE/deconv/CCC/composition; `qa_deck.py` + `validate_presentation.py` after PPT; `api_check.py --diff` after package upgrades. If the worker did not attach machine-check output, the main agent re-runs it before accepting. For the full rule set that workers must follow, see `references/dispatch_cheatsheet.md` (condensed hard rules A1-A9 / B1-B7 / C1-C4 / D1-D6) — inject it into dispatch prompts per the ⚠️ Dispatch Injection section at the top of this file.
5. **Save checkpoints.** After each major step (QC/cluster/annotation/DE), save `adata.write_h5ad('checkpoints/XX_step.h5ad')`. Upstream changes → re-run from last valid checkpoint.
6. **Runtime API self-adaptation.** Do NOT trust hardcoded version numbers or assume API signatures. Before calling any ov.*/pt.*/sc.* function for the first time, verify with `inspect.signature(func)`. Run `python scripts/api_check.py --diff` after any package upgrade.
7. **Step-gate + hypothesis ledger** *(agent self-check, per-step)*. Every analysis follows meta_methodology §7 (step-gate sanity checks after each step) and §8 (hypothesis ledger + provenance + conclusion grading).
   > *Rationale*: The planner-verifier dual loop is the proven-optimal pattern for bioinformatics agents (K-Dense Analyst outperforms single-model by 6 points on BixBench via per-step verification).
8. **Result-driven iteration** *(human gate, per-batch)*. Biology is evidence-driven, NOT linear like software. After each analysis batch: review results → **discuss direction with researcher** → revise plan → next batch. Pause for researcher input on decisions that need human judgment (cell-type naming, which signal to chase, threshold calibration). Full procedure: `research-planner` Phase R. **Autopilot exception**: if the user explicitly authorizes "just run it through, don't stop at every step", agent may merge batches into a continuous run, but MUST do one full Phase R review (R1 ledger update + R2 decision-point retro) before final delivery, and record the authorization in `analysis_log.md`.
   > *Rationale*: A pipeline that auto-runs QC→cluster→DE→CCC→figures without pausing to interpret results produces data dredging, not science. But a rule that ignores real usage ("跑完别停") gets silently bypassed — the autopilot exception keeps the ledger alive while respecting user autonomy.
9. **Notebook-organized workflow** *(ipynb per task)*. Analysis and plotting code lives in Jupyter notebooks (.ipynb), one task per notebook. Structure: Cell 1 = shared setup (imports + `set_cns_style` + load data, run once); subsequent cells = one logical step each (one QC step, one panel, one DE round). Re-run only the cell you change — data stays in memory across cells. `save_panel` auto-displays figures in notebook output (`show=None` detects Jupyter → figure shows in cell + PDF saved to disk). **CLI fallback** (no Jupyter kernel): save double format — `save_panel(fig, name, fmt='png')` for self-inspection (Read the PNG to check before next panel) + `fig.savefig(name + '.pdf')` for vector delivery. Checkpoints (Rule 5) and `analysis_log` (meta §8b) are the persistence layer; notebooks are the workflow layer.
10. **Deliverable gate** *(mandatory, post-convergence)*. When the analysis story converges (Phase R loop done + researcher agrees, Rule 8), the agent MUST produce at least one deliverable package — not just leave figures on disk. Default outputs: PPT (`scientific-slides`, for meeting/defense) or HTML report (`web-report`, for online sharing — no PowerPoint needed to view). Choose based on audience: lab meeting → PPT; remote collaborator → HTML; both if the user wants. The deliverable embeds real figures + key findings (with source labels `[实测]/[文献]/[推断]`) + hypothesis ledger + method/reproducibility info. **Skipping this = analysis done but nothing delivered.**

## Key Files

| File | When to read |
|---|---|
| `compat.yaml` | Version questions; after any package upgrade |
| `references/figure_guide.md` | Before ANY plotting — visual specs, three iron rules, real-world lessons (no code) |
| `references/plotting_reference.md` | When writing plotting code — runnable templates for every chart type (§0 quick card → §2/§3 templates) |
| `references/omicverse_skills_examples.md` | External reference — curated patterns from omicverse-skills repo (marked "absorbed" vs "reference") |
| `references/story_builder.md` | **After analysis, before drawing/writing** — how to turn results into a biological story (5-step method: findings → causal chain → main message → figure mapping → story arc) |
| `references/discovery_miner.md` | **Right after analysis** — scan each result type (DE/proportion/CCC/trajectory/niche) for candidate discoveries, score priority, exclude false positives, determine story level |
| `scripts/cns_style.py` | Import at top of every plotting script (26+ helpers + 40 smart_plot entry points: plot_umap/volcano/dotplot/plot_ccc/plot_ridge/plot_upset/...) |
| `scripts/postcheck.py` | After any analysis (scientific rigor auto-check) |
| `references/analysis_reference.md` | Analysis code templates (QC/DE/CCC/spatial/bulk) — the plotting_reference equivalent for analysis |
| `references/plotting_reference.md` | Plotting code templates (18 chart types) |
| `scripts/api_check.py` | After installing/updating omicverse or pertpy |
| `scripts/scop_api_check.R` | After installing/updating scop |
| `references/meta_methodology.md` | Self-check after each analysis step (8 rules + step-gate + hypothesis ledger) |
| `references/omicverse_guide.md` | When using ov.* APIs (task → API cheat-sheet) |
