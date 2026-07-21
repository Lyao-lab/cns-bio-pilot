# Multi-omics Integration (omicverse 2.2.3 — verified API)

> Companion to `SKILL.md` §9b. This file holds the full per-modality API code; SKILL.md keeps the modality-selection table (the decision logic) and a pointer here.

All APIs below verified available in omicverse 2.2.3 (`sc` env). Pick by which modalities you have.

## MOFA+ — multi-omics factor analysis (RNA + ATAC + protein, joint factor model)

```python
import omicverse as ov
mofa = ov.single.pyMOFA(omics=[adata_rna, adata_atac],
                        omics_name=['RNA','ATAC'])   # builds MuData internally
mofa.train()
mofa.save('mofa_model')
# Load a pretrained model: mofa = ov.single.pyMOFAART('mofa_model')
```

## GLUE — RNA + ATAC regulatory inference (cross-modality GRN)

```python
ov.single.GLUE_pair(adata_rna, adata_atac)   # or ov.single.glue_pair(...)
```

## SIMBA — multi-omics embedding integration (gene/region/cell joint space)

```python
simba = ov.single.pySIMBA(mdata, workdir='simba_result')
```

## CITE-seq / multimodal annotation (ADT + RNA)

```python
# ov.single.Annotation accepts multi-modal AnnData; CITE-seq protein markers sharpen labels
# For totalVI/MultiVI (scvi-tools), call via ov.single.lazy_step_scvi (lazy-loaded)
```

## Metabolism + metabolite-based cell-cell communication

```python
ov.single.MetaboliteCCC(adata)                # metabolite ligand-receptor CCC (note: Metabol**i**teCCC)
ov.single.Metabolism(adata)                   # per-cell metabolic flux scoring
ov.single.differential_metabolism(adata, ...) # condition-comparison metabolism
```

## Causal GRN (multi-omics causal network inference)

```python
ov.single.pyCEFCON(adata)                     # causal regulatory network
```

## Bulk multi-omics (TCGA pan-cancer, cross-omics correlation)

```python
ov.bulk.pyTCGA(...)                           # TCGA multi-omics download + integrate
ov.bulk.enrichment_multi_concat(...)          # cross-pathway / cross-omics enrichment concat
ov.bulk.geneset_plot_multi(...)               # multi-omics pathway heatmap
```

## Notes

- **Muon / MuData**: omicverse does NOT expose `muon` / `MuData` at the top level (`ov.muon` / `ov.MuData` both return False). For direct MuData manipulation, `pip install muon` and use its native API; `ov.single.pyMOFA` builds MuData internally so you usually don't need to.
- **Spatial multi-omics** (Stereo-seq/Visium HD with multiple modalities) → `spatial/multiomics` (cellpose + SpatialData), not this file.
