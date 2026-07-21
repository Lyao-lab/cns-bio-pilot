# cns-bio-pilot

> A bioinformatics skill library for ZCode agents — single-cell + spatial transcriptomics (with bulk / other omics) + publication-grade plotting + paper/PPT writing.
>
> **Three engines**: OmicVerse V2 (Python, default) · scop (R/Seurat) · perturbation models (GEARS/CPA/scGPT + GRN-based virtual KO).
>
> **19 sub-skills** · router architecture · meta-methodology discipline · publication-grade aesthetics.

[![version](https://img.shields.io/badge/version-14.0-blue)](#) [![skills](https://img.shields.io/badge/sub--skills-19-green)](#) [![engine](https://img.shields.io/badge/engine-OmicVerse%20V2%20%2B%20scop%20%2B%20perturbation-orange)](#)

---

## Why this skill

Most bioinformatics "skills" are either a flat list of commands or a knowledge dump. `cns-bio-pilot` is different:

- **Router, not encyclopedia** — the top `SKILL.md` routes your request to exactly one of 19 sub-skills; you never load irrelevant context.
- **Fact-based, never fabricate** — core principle #1. No invented accessions, PMIDs, API signatures, or results. Verify before calling.
- **Don't reinvent the wheel** — core principle #2. Before writing any method, search omicverse/scop → PyPI → R/Bioconductor → adapt similar → from-scratch (last resort).
- **Meta-methodology discipline** — 6 self-check rules (verify prerequisites / semantic boundaries / what is N / report the path / chain-failure & circuit-breaker / design up front). See `references/meta_methodology.md`.
- **Publication-grade by default** — CNS figure aesthetics baked in (300 DPI, Arial, dual-track Morlandi palette, CJK font fallback, title/legend non-overlap).
- **Honest about algorithm freshness** — 2024-2026 benchmarks cited (FM controversy, cell2fate, LEMUR, LIANA+, cell2location 5-method unification). Things that don't work are labeled as such.

---

## Quick install

### Option A — Install as a ZCode user-level skill (recommended)

```bash
# 1. Clone into the ZCode user skills directory
git clone https://github.com/Lyao-lab/cns-bio-pilot.git ~/.agents/skills/cns-bio-pilot
```

That's it. The skill is auto-discovered on next ZCode session — just ask in natural language and the trigger words in each `description:` field route the request.

**Default path by OS** (create the dir first if missing):

| OS | User-level skills path |
|---|---|
| Windows | `C:\Users\<you>\.agents\skills\` |
| macOS / Linux | `~/.agents/skills/` |

### Option B — Workspace-level skill (per-project)

```bash
# Inside your project root (where you run ZCode)
mkdir -p .agents/skills
git clone https://github.com/Lyao-lab/cns-bio-pilot.git .agents/skills/cns-bio-pilot
```

Workspace skills override user-level skills of the same name — useful for project-specific forks.

### Option C — Just browse / fork

```bash
git clone https://github.com/Lyao-lab/cns-bio-pilot.git
```

The repo contains no binary blobs (data/images are gitignored), so the clone is ~1 MB.

---

## Environment setup (the real prerequisite)

The skill itself is plain Markdown — **no install needed**. What needs installing is the **bioinformatics stack** it drives. Three conda envs cover 90% of tasks:

### Env 1 — `sc` (single-cell, primary)

```bash
conda create -n sc python=3.11 -y
conda activate sc
pip install omicverse scanpy scvelo anndata
# Verified working versions (2026-07):
#   omicverse 2.2.3 · scanpy 1.11.5 · scvelo 0.3.4 · anndata 0.12.19
# cell2location + scvi (deconvolution & integration, coexist since omicverse 2.2.3):
pip install cell2location scvi-tools
#   cell2location 0.1.5 · scvi-tools 1.4.2
# CellRank 2 (trajectory/fate) + LIANA+ (communication):
pip install cellrank liana
#   cellrank 2.0.7 · liana 1.7.3
# Optional but recommended:
pip install ipywidgets decoupler gseapy pydeseq2
```

### Env 2 — `st` (spatial, squidpy)

```bash
conda create -n st python=3.11 -y
conda activate st
pip install squidpy scanpy
#   squidpy 1.2.2 · scanpy 1.9.6
```

### Env 3 — `scop_env` (R / Seurat / scop)

```r
# In R (>= 4.4):
if (!require("scop")) remotes::install_github("mengxu98/scop")
# scop provides 200+ Run* verbs wrapping Seurat, CellChat, SCENIC+, CytoTRACE, Milo, etc.
```

### Which env for which task?

| Task | Env | Key packages |
|---|---|---|
| Single-cell QC / clustering / annotation / DE / trajectory / communication | `sc` | omicverse, scanpy, cellrank, liana |
| Batch integration (Harmony/scVI) | `sc` | omicverse (wraps scvi-tools) |
| Spatial deconvolution (cell2location/Tangram/RCTD) | `sc` | `ov.space.Deconvolution` (5 methods unified) |
| Spatial domains / SVG / spatial communication | `st` | squidpy, omicverse |
| R/Seurat pipeline, CytoTRACE, Milo, SCENIC+, Giotto | `scop_env` | scop (R) |
| Perturbation prediction (GEARS/CPA/scGPT) | `sc` | pertpy + GPU |
| GRN-based virtual KO (CellOracle/SCENIC+) | `sc` | standalone `pip install celloracle scenicplus` |

> **GPU**: scGPT/GEARS/CPA finetune need CUDA. Without GPU, fall back to linear baseline (perturbation) or scTenifoldKnk/CellOracle-base-GRN (virtual KO).

---

## How to use

Just talk to ZCode naturally — the skill triggers on Chinese or English keywords:

```
你帮我把这个 PBMC 单细胞数据跑一下 QC + 聚类 + 注释
→ routes to single-cell/omicverse-pipeline

预测一下敲除 TP53 后的转录组变化
→ routes to single-cell/perturbation-prediction (Route B: GRN-based virtual KO)

我的 Visium 数据要去卷积，估每个 spot 的细胞类型
→ routes to spatial/deconvolution (cell2location via ov.space.Deconvolution)

画一张发表级的 UMAP，按细胞类型着色
→ routes to visualization/omicverse-plotting (dual-track Morlandi palette)

帮我做组会 PPT，汇报上周进度
→ routes to presentation/scientific-slides (lab-meeting mode)
```

The router (`SKILL.md`) reads your request, picks **one** sub-skill, loads only that one + its declared references — context stays lean.

### What the agent will do for you

1. **Pre-Routing Checks** — verify env, raw counts, batch, GPU, spliced/unspliced *before* touching data
2. **Execute** the matched sub-skill's workflow (real code, real API calls)
3. **Postcheck** — run `scripts/postcheck.py` to verify scientific rigor (raw counts preserved, Padj reported, pseudobulk used, deconv quality assessed)

---

## The 18 sub-skills

| # | Category | Sub-skill | What it does |
|---|---|---|---|
| 1 | single-cell | `omicverse-pipeline` | Full pipeline: QC → doublet → cluster → annotate → batch → comm → trajectory |
| 2 | single-cell | `scop` | R/Seurat 200+ Run* verbs; CytoTRACE/Milo/SCENIC+/Giotto (no omicverse equivalent) |
| 3 | single-cell | `perturbation-prediction` | Two routes: (A) ML-based GEARS/CPA/scGPT (needs Perturb-seq); (B) GRN-based virtual KO CellOracle/SCENIC+/scTenifoldKnk (needs only WT scRNA) |
| 4 | single-cell | `perturb-seq` | Analyze existing Perturb-seq/CROP-seq: Mixscape, differential perturbation, guide QC |
| 5 | single-cell | `rna-velocity` | 5 engines (scvelo/dynamo/latentvelo/graphvelo/regvelo) + cell2fate/cellDancer/pyro-Velocity fallbacks + CellRank 2 |
| 6 | single-cell | `research-planner` | Zero-code study design: question → pattern → samples → modules → validation ladder |
| 7 | spatial | `omicverse-spatial` | Full spatial pipeline: IO → spatial neighbors → SVG → domains → comm → viz |
| 8 | spatial | `deconvolution` | `ov.space.Deconvolution` 5 methods: cell2location/Tangram/RCTD/Starfysh/flashdeconv |
| 9 | spatial | `multiomics` | High-res platforms (Stereo-seq/Visium HD/Slide-seq): cellpose, SpatialData |
| 10 | spatial | `proteomics` | Spatial proteomics (CODEX/IMC/MIBI): scimap phenotyping + gating |
| 11 | general-bio | `omicverse-bulk` | Bulk DE → enrichment → WGCNA → PPI, pure Python (pyDESeq2/GSEApy/decoupler) |
| 12 | visualization | `omicverse-plotting` | `ov.pl.*` 80+ functions; dual-track Morlandi palette; CNS aesthetics |
| 13 | visualization | `multi-panel-figures` | 6-panel (A-F) publication figure assembly CLI |
| 14 | visualization | `scientific-schematics` | AI generate → review → refine loop; includes graphical-abstract mode |
| 15 | presentation | `scientific-slides` | Dual mode: formal talk (python-pptx/Beamer) + lab meeting (discussion-driven) |
| 16 | presentation | `methods-writer` | Protocol → publication-grade Methods text (CONSORT/STROBE/PRISMA/TRIPOD/ARRIVE/STARD) |
| 17 | presentation | `results-writer` | Results → narrative prose; Results ≠ Discussion; no fabricated PMIDs |
| 18 | presentation | `figure-legend-writer` | Self-contained publication legends for any figure type |

---

## Repository structure

```
cns-bio-pilot/
├── SKILL.md                      # Router (read first; routes to one sub-skill)
├── skill-index.json              # Compact machine-readable index (18 skills)
├── scripts/
│   └── postcheck.py              # Scientific rigor auto-check (run after analysis)
├── references/                   # Top-level references (loaded on demand)
│   ├── workflow_routing.md       # Routing decision tree + Signal Patterns trap table
│   ├── omicverse_guide.md        # OmicVerse API cheat-sheet (task → API)
│   ├── figure_aesthetics.md      # CNS publication spec (palette / fonts / non-overlap)
│   └── meta_methodology.md       # 6 meta-methodology principles + self-check
└── skills/                       # 18 sub-skills (load only the matched one)
    ├── single-cell/   (6 skills)
    ├── spatial/       (4 skills)
    ├── general-bio/   (1 skill)
    ├── visualization/ (3 skills)
    └── presentation/  (4 skills)
```

Each sub-skill has the same 4-piece handoff structure:
- **When NOT to use** — anti-triggers (prevents mis-routing)
- **Prerequisites** — where inputs come from
- **When to leave** — where to go next
- **Key pitfalls** — LLM-common mistakes to avoid

---

## 13 core principles (the skill's constitution)

1. **Fact-based; ask when unsure; never fabricate**
2. **Don't reinvent the wheel** — search PubMed/GitHub/PyPI/R before implementing
3. **Real data first** — mocks for testing only
4. **Statistical rigor** — pseudobulk DE, FDR, report total tests
5. **Strict thresholds** — DE Padj<0.05 & |Log2FC|>1.0
6. **Association ≠ causation**
7. **Python first** (omicverse); R only when no equivalent
8. **Batch-corrected embedding never for DE**
9. **Conservative wording** — biomarkers need validation cohort
10. **Reproducibility** — keep `layers['counts']`, record versions & seeds
11. **Spatial-specific** — deconvolution quality assessment mandatory
12. **Publication-grade aesthetics** — CNS figure guidelines
13. **Meta-methodology discipline** — 6 self-check rules (see `references/meta_methodology.md`)

---

## Migrating to another server

The skill is **self-contained Markdown + one Python script** — no build step, no runtime deps for the skill itself.

```bash
# 1. On the new server, install ZCode (if not already)
# 2. Clone the skill
git clone https://github.com/Lyao-lab/cns-bio-pilot.git ~/.agents/skills/cns-bio-pilot

# 3. Set up the three conda envs (see "Environment setup" above)
#    This is the only heavyweight step — the skill is useless without the bio stack.

# 4. Verify
cd ~/.agents/skills/cns-bio-pilot
conda run -n sc python scripts/api_check.py   # API existence self-check (run after every omicverse update)
python scripts/postcheck.py --help            # should print usage (needs anndata)
conda run -n sc python -c "import omicverse; print(omicverse.__version__)"  # 2.2.3
```

> **After every `pip install --upgrade omicverse`**, re-run `api_check.py` — it scans all skill docs for `ov.*` API calls and verifies each one still exists in the new version. If omicverse renames/removes an API, the script flags it with a fix suggestion.

### Offline / air-gapped servers

```bash
# On a machine with internet:
git clone https://github.com/Lyao-lab/cns-bio-pilot.git
cd cns-bio-pilot && git bundle create ../cns-bio-pilot.bundle --all

# Transfer cns-bio-pilot.bundle to the air-gapped server, then:
git clone cns-bio-pilot.bundle ~/.agents/skills/cns-bio-pilot
```

For conda envs offline, use `conda-pack`:
```bash
# On internet machine:
conda pack -n sc -o sc.tar.gz
# Transfer + unpack on target:
mkdir -p ~/envs/sc && tar -xzf sc.tar.gz -C ~/envs/sc
conda activate ~/envs/sc
```

---

## Algorithm freshness (2024-2026)

This skill is current as of **July 2026**. Key positions:

| Topic | Position |
|---|---|
| **Foundation models (scGPT/Geneformer)** | Not default — 2025 benchmarks show they don't beat linear baselines for perturbation; zero-shot annotation brittle. Always benchmark vs simple baseline. |
| **Perturbation prediction** | Two routes: ML-based (GEARS/CPA, needs Perturb-seq, **linear baseline mandatory**) + GRN-based virtual KO (CellOracle/SCENIC+, needs only WT scRNA) |
| **Trajectory** | CellRank 2 primary (Nat Methods 2024); moscot for discrete timepoints (Nature 2025); LEMUR for cluster-free multi-condition DE (Nat Genet 2025) |
| **RNA velocity** | scVelo-stochastic default (most stable per 17-study benchmark); cell2fate (Nat Methods 2025) for Bayesian modular; pyro-Velocity for uncertainty |
| **Spatial deconvolution** | `ov.space.Deconvolution` unifies cell2location/Tangram/RCTD/Starfysh/flashdeconv — no separate c2l env since omicverse 2.2.3 |
| **Cell communication** | LIANA+ consensus (Mol Syst Biol 2024) for single-cell; COMMOT for spatial |
| **Bulk DE** | DESeq2/edgeR/limma unchanged; PyDESeq2 now scverse-maintained |

---

## License & citation

MIT License. If this skill helps your research, cite the underlying tools (OmicVerse, scop, scvi-tools, CellRank, etc.) — each sub-skill's `SKILL.md` lists the primary references.

## Contributing

This is a personal research skill. Issues and PRs welcome at [github.com/Lyao-lab/cns-bio-pilot](https://github.com/Lyao-lab/cns-bio-pilot).
