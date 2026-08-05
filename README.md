# CNS Bio-Pilot

[![version](https://img.shields.io/badge/version-19.0-blue)](#) [![skills](https://img.shields.io/badge/sub--skills-14-green)](#) [![engine](https://img.shields.io/badge/engine-OmicVerse%20V2%20%2B%20scop%20%2B%20perturbation-orange)](#)

Single-cell + spatial transcriptomics bioinformatics skill library. Router architecture: read `SKILL.md` → pick ONE sub-skill → execute.

## Quick Start

```bash
# Environment (see compat.yaml for versions)
conda activate sc          # omicverse + scanpy + scvelo + pertpy + spatialdata
conda activate st          # squidpy (spatial stats)
# R/scop: ~/miniforge3/envs/scop_env/bin/Rscript  (conda scop_env, R 4.5.3, scop 0.8.9)

# After any package upgrade:
python scripts/api_check.py --diff    # see what changed
python scripts/api_check.py           # full verification
```

## Architecture

```
SKILL.md (router)
├── compat.yaml (package versions — single source of truth)
├── references/
│   ├── figure_guide.md (the ONLY figure reference — specs + recipes)
│   ├── meta_methodology.md (6 self-check rules)
│   ├── omicverse_guide.md (ov.* API cheat-sheet)
│   ├── figure_guide.md (visual specs + recipes)
│   ├── meta_methodology.md (6 self-check rules)
│   ├── omicverse_guide.md (ov.* API cheat-sheet)
│   ├── story_builder.md (results → biological narrative)
│   └── discovery_miner.md (analysis → candidate discoveries)
├── scripts/
│   ├── cns_style.py (one-shot aesthetics: set_cns_style_journal/polish_axes/...)
│   ├── api_check.py (API verification + --diff mode)
│   ├── postcheck.py (scientific rigor auto-check)
│   └── scop_api_check.R (scop API verification)
└── skills/ (14 sub-skills)
    ├── single-cell/
    │   ├── omicverse-pipeline (QC→cluster→annotate→DE→CCC→trajectory)
    │   ├── scop (R/Seurat, 133 Run* verbs)
    │   ├── rna-velocity (scvelo + CellRank)
    │   ├── perturbation (measured Perturb-seq + in silico prediction)
    │   └── research-planner (study design, zero-code)
    ├── spatial/
    │   ├── omicverse-spatial (domains/SVG/CCC)
    │   ├── deconvolution (cell2location/RCTD/Tangram/SPOTlight/CARD)
    │   ├── multiomics (Visium HD/Stereo-seq/segmentation)
    │   └── proteomics (CODEX/IMC)
    ├── general-bio/
    │   └── omicverse-bulk (DE/GSEA/WGCNA/PPI)
    ├── visualization/
    │   ├── figure-production (design→render→assemble, ALL figure types)
    │   └── scientific-schematics (mechanism diagrams/graphical abstract)
    └── presentation/
        ├── manuscript-writing (Methods/Results/Legends)
        └── scientific-slides (PPT/Beamer)
```

## Figure Production Pipeline

```
Phase 1: DESIGN (narrative spine → outline.json)
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
