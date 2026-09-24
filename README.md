# CNS Bio-Pilot

[![version](https://img.shields.io/badge/version-22.6-blue)](#) [![skills](https://img.shields.io/badge/sub--skills-15-green)](#) [![engine](https://img.shields.io/badge/engine-OmicVerse%20V2%20%2B%20scop%20%2B%20perturbation-orange)](#)

Single-cell + spatial transcriptomics bioinformatics skill library. Router architecture: read `SKILL.md` → pick ONE sub-skill → execute.（版本以 SKILL.md metadata 为唯一源）

## Quick Start

```bash
# Environment (see compat.yaml for versions)
conda activate sc          # omicverse + scanpy + pertpy + spatialdata + tangram
conda activate regvelo     # scvelo（sc env 无 scvelo，2026-09-21 实测）
conda activate st          # squidpy (spatial stats) + decoupler 2.x
# R/scop: ~/miniforge3/envs/scop_env/bin/Rscript  (conda scop_env, R 4.5.3, scop 0.8.9)

# After any package upgrade:
python scripts/api_check.py --diff    # see what changed
python scripts/api_check.py           # full verification
```

## Architecture

```
SKILL.md (router)
├── compat.yaml (package versions — single source of truth)
├── evals/               # 路由/触发回归测试 + 结构 lint（改 SKILL.md 后必跑 sync_prompts.py）
├── references/
│   ├── figure_guide.md (visual specs + three iron rules + real-world lessons)
│   ├── figure_templates.md (主图顺序模板库：领域卡 C1-C15 × 研究型 T1-T6，506 篇 CNS 泛化)
│   ├── plotting_reference.md (runnable code templates for every chart type)
│   ├── dispatch_cheatsheet.md (A1-A10/B1-B9/C1-C4/D1-D6/E1-E6 硬规则——派发子任务必注入)
│   ├── tool_registry.md (cns_style 51 个 plot_* + 校验脚本统一索引)
│   ├── bigfig_deck_playbook.md (大 fig/PPT 组合体管线与验收门)
│   ├── omicverse_skills_examples.md (external patterns from omicverse-skills repo)
│   ├── meta_methodology.md (8 self-check principles + step-gate + hypothesis ledger)
│   ├── omicverse_guide.md (ov.* API cheat-sheet)
│   ├── analysis_reference.md (analysis code templates index)
│   ├── story_builder.md (results → biological narrative)
│   ├── discovery_miner.md (analysis → candidate discoveries)
│   └── analysis/         # 知识层（decision_guide/analysis_flow/paper_paradigms/paper_directions/discipline/stats_convention）
│       └── templates/    # 模板层（可执行分析代码：setup/sc_basic/sc_annotation/sc_downstream/sc_perturbation_state/spatial/bulk）
├── scripts/
│   ├── cns_style/ 包 (one-shot aesthetics + smart_plot plot_* 统一入口，51 个)
│   ├── api_check.py (API verification + --diff mode)
│   ├── postcheck.py (scientific rigor auto-check)
│   ├── nb_log.py (CLI 模式代码落 ipynb 台账，规则 A10)
│   └── scop_api_check.R (scop API verification)
└── skills/ (15 sub-skills)
    ├── single-cell/
    │   ├── omicverse-pipeline (QC→cluster→annotate→DE→CCC→trajectory)
    │   ├── scop (R/Seurat, 133 Run* verbs)
    │   ├── rna-velocity (scvelo + CellRank)
    │   ├── perturbation (measured Perturb-seq + in silico prediction)
    │   └── research-planner (study design, zero-code)
    ├── spatial/
    │   ├── omicverse-spatial (domains/SVG/CCC)
    │   ├── deconvolution (Python 五法 + scop R 系 SPOTlight/CARD)
    │   ├── multiomics (Visium HD/Stereo-seq/segmentation)
    │   └── proteomics (CODEX/IMC)
    ├── general-bio/
    │   └── omicverse-bulk (DE/GSEA/WGCNA/PPI)
    ├── visualization/
    │   ├── figure-production (design→render→assemble, ALL figure types)
    │   └── scientific-schematics (mechanism diagrams/graphical abstract)
    └── presentation/
        ├── manuscript-writing (Methods/Results/Legends)
        ├── scientific-slides (PPT/Beamer)
        └── web-report (自包含 HTML 报告)
```

## Figure Production Pipeline

```
Phase 1: DESIGN (narrative spine → outline.json；整篇顺序先查 references/figure_templates.md §0 路由)
Phase 2: RENDER (each panel independently → save PDF → verify aesthetics)
Phase 3: ASSEMBLE (pre-verified PDFs → composite figure)
```

Never draw-and-assemble simultaneously. Each panel must be independently rendered and verified before assembly.

## Core Rules

1. **Fact-based; never fabricate.** Missing info → `[AUTHOR TO SPECIFY]`.
2. **Pseudobulk for single-cell DE.** Per-cell Wilcoxon inflates false positives.
3. **Search before implementing.** omicverse/scop → standalone → adapt → from-scratch (last resort).

## Version Management

Package versions declared in `compat.yaml`. After upgrading:
```bash
python scripts/api_check.py --diff   # reports exact changes in one command
```
Update `compat.yaml` verified_against, fix any removed APIs. No more hardcoded version strings scattered across files.
