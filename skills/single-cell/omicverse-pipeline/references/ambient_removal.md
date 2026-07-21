# Ambient RNA Removal (omicverse 2.2.3 — verified API)

Ambient ("soup") RNA = cell-free mRNA from lysed cells that contaminates every droplet. Left uncorrected it inflates marker genes in cell types that never expressed them and biases DE, annotation, and trajectory inference. **For FFPE, nuclei, and any run with visible background, ambient removal is NOT optional** — skipping it is a silent landmine.

> Companion to `SKILL.md` §1.5. This file holds the full API reference + decision table + diagnostics; SKILL.md keeps the ordering discipline (ambient BEFORE QC) and the canonical entry snippet.

## Unified API

omicverse 2.2.3 unifies 6 backends under one dispatcher:

```python
ov.pp.ambient.remove_ambient(adata, method=..., raw=..., cluster_key=..., **kwargs)
```

Pure-Python R-parity backends: `pysoupx` / `pyfastcar` / `pydecontx` / `pysccdc` (install: `pip install omicverse[ambient]`).
DL backends (optional, install standalone): `cellbender` / `scar`.

Output written to the AnnData:
- `adata.X` — decontaminated counts (replaces original)
- `adata.obs['ambient_contamination']` — per-cell contamination fraction
- `adata.layers['ambient_raw']` — pre-correction counts (when `keep_raw_layer=True`, default)
- `adata.uns['ambient']` — method metadata + count-integrity stats

## Backend decision table

| You have… | First choice | Alt | Input requirement |
|---|---|---|---|
| **Raw unfiltered matrix** (incl. empty droplets) | `method='soupx'` (SoupX, [Young et al. 2020](https://academic.oup.com/gigascience/article/9/12/giaa151/6047051)) | `method='fastcar'` | `raw=raw_adata` (unfiltered) required |
| **Only filtered matrix, already clustered** | `method='decontx'` (DecontX, [Yang et al. 2020](https://f1000research.com/articles/9-1170)) | `method='sccdc'` | `cluster_key='leiden'` required |
| **FFPE / very high background / CNS main figure** | `method='cellbender'` (DL, [Fleming et al. 2023](https://www.nature.com/articles/s41467-023-36794-y), [7-tool benchmark gold standard — Cargnelli et al. 2026](https://www.biorxiv.org/content/10.64898/2026.01.13.699237v1)) | `method='scar'` | GPU helps; install `cellbender` standalone |

> **Decision rule**: if you have the raw unfiltered matrix → SoupX (fast, robust, best-documented). If only filtered+clustered → DecontX. For FFPE or CNS-grade cleaning → CellBender (heaviest, but the 2026 7-tool benchmark ranks it gold). Always cross-check the result with `ambient_negative_marker_check` (below).

## Run removal

```python
import omicverse as ov

# --- Option A: SoupX / FastCAR (need raw unfiltered droplet matrix) ---
raw_adata = sc.read_10x_h5('raw_feature_bc_matrix.h5')   # the UNFILTERED matrix w/ empty droplets
ov.pp.ambient.remove_ambient(
    adata,                       # the FILTERED real-cells object
    method='soupx',
    raw=raw_adata,               # required for soupx/fastcar — builds ambient profile from empty droplets
    keep_raw_layer=True,         # store pre-correction counts in layers['ambient_raw'] (default)
)

# --- Option B: DecontX / scCDC (need clustered filtered matrix) ---
# Run §2-§5 first to get a quick clustering, THEN decontaminate, THEN redo §3-§5 on cleaned counts.
ov.pp.ambient.remove_ambient(adata, method='decontx', cluster_key='leiden')

# --- Option C: CellBender (heaviest, CNS-grade; install: pip install cellbender) ---
ov.pp.ambient.remove_ambient(adata, method='cellbender', raw=raw_adata)
```

> **Workflow ordering trap**: SoupX/FastCAR can run on raw counts (before §2 QC). DecontX/scCDC need a quick clustering first → run §2-§5 once to get a throwaway clustering, decontaminate, then re-run §3-§5 on the cleaned counts. **Always re-store `layers['counts']` from the corrected `.X` after ambient removal** — otherwise downstream DE/velocity will still use contaminated counts.

## Diagnostics (mandatory — confirm the correction worked)

```python
# 1. Per-cell contamination distribution (should be a unimodal long-tail, median <0.1)
ov.pp.ambient.contamination_report(adata)                    # single-row summary
ov.pp.ambient.plot_contamination(adata, groupby='sample')    # boxplot per sample

# 2. NEGATIVE-marker check (the real test): a marker specific to cell type X
#    should DROP toward 0 in cell types that biologically do NOT express it.
ov.pp.ambient.ambient_negative_marker_check(
    adata, marker='CD79A', celltype_key='celltype',
    positive_celltypes=['B cell'],   # expected: B cells keep it; everyone else → ~0 after correction
)

# 3. Count integrity (corrected counts shouldn't drift wildly from raw)
ov.pp.ambient.count_integrity_check(adata.layers['ambient_raw'], adata.X)
```

**What to look for**:
1. median per-cell contamination 0.05–0.20 (higher = worse library quality)
2. markers cleanly drop in non-expressing cells
3. no sample with >2× median contamination (points to a bad library — investigate, don't just clean)

A contamination fraction >0.5 means the cell is mostly soup — flag or remove.

## When NOT to run ambient removal

- **10x fresh-frozen, clean dissociation, visible background low** — optional, document if you skip.
- **Already CellBender-cleaned upstream** (some data providers ship pre-cleaned) — don't double-clean, you'll over-correct and erase real signal.
- **Spatial transcriptomics** — see `spatial/omicverse-spatial` (spatial ambient models differ; `ov.pp.ambient` is droplet-only).
