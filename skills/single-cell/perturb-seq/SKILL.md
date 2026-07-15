---
name: bio-single-cell-perturb-seq
description: 分析【已经做好的】Perturb-seq / CROP-seq / CRISPR 筛选实验数据——基因功能鉴定、扰动响应差异、扰动一致性等下游分析。当用户已有 Perturb-seq 数据要做下游分析时触发。
tool_type: python
primary_tool: Pertpy
---

## When NOT to use this skill
- Predict perturbation response for **unmeasured** experiments (in-silico KO of unseen genes/drugs) → `single-cell/perturbation-prediction` (GEARS/CPA/scGPT)
- Only routine scRNA-seq preprocessing / clustering / annotation (no CRISPR guide) → `single-cell/omicverse-pipeline`
- Only gene essentiality / functional-module simulation (no measured Perturb-seq data) → `single-cell/scop` (`RunscTenifoldKnk`)
- bulk CRISPR screen (no single-cell readout) → out of scope (use bulk-screen tools such as MAGeCK)

## Version Compatibility

Verify installed versions match before running: `pip show <pkg>` / `help(func)` to check signatures; adapt examples to your actual API rather than retrying on errors.

# Perturb-seq Analysis

**"Analyze my Perturb-seq CRISPR screen"** → Link guide RNA assignments to transcriptional phenotypes in pooled CRISPR screens with single-cell readout to identify gene function.
- Python: `pertpy.tl.Mixscape(adata)` for perturbation classification, `pertpy.tl.Augur` for prioritization

## Load and Annotate Perturbations

```python
import scanpy as sc
import pertpy as pt

adata = sc.read_h5ad('perturb_seq.h5ad')

# Guide assignments typically stored in obs
# Format: cell barcode -> guide identity -> target gene
adata.obs['guide_id'] = guide_assignments['guide_id']
adata.obs['target_gene'] = guide_assignments['target_gene']

# Mark non-targeting controls
adata.obs['is_control'] = adata.obs['target_gene'] == 'non-targeting'
```

## Pertpy Analysis

```python
# Initialize perturbation analysis
ps = pt.tl.PerturbationSpace(adata)

# Differential expression per perturbation vs control
de = pt.tl.PseudobulkDE(adata)
de.fit(
    groupby='target_gene',
    control='non-targeting',
    n_threads=8
)
results = de.results()

# Filter significant genes
sig_results = results[results['pval_adj'] < 0.05]

# Perturbation signatures (effect sizes)
ps = pt.tl.PerturbationSignature(adata)
ps.compute(groupby='target_gene', control='non-targeting')

# Get signature matrix
signatures = ps.get_signature_matrix()
```

## Perturbation Embedding

```python
# Compute perturbation-level embeddings
pt.tl.perturbation_embedding(adata, groupby='target_gene', method='mean')

# Cluster perturbations by phenotype
pt.tl.cluster_perturbations(adata, resolution=0.5)

# Find functionally related perturbations
pt.pl.perturbation_heatmap(adata, groupby='perturbation_cluster')
```

## Mixscape (Seurat v5)

**Goal:** Classify cells in a CRISPR screen as successfully perturbed or escaped based on their transcriptional response relative to non-targeting controls.

**Approach:** Compute per-cell perturbation signatures against non-targeting controls using PCA-projected differences, then run Mixscape mixture model classification to separate knockout-responsive cells from escapees.

```r
library(Seurat)
library(SeuratObject)

# Load Perturb-seq data
seurat <- Read10X('filtered_feature_bc_matrix/')
seurat <- CreateSeuratObject(seurat)

# Add perturbation metadata
seurat <- AddMetaData(seurat, metadata = perturbation_calls)

# Standard preprocessing
seurat <- NormalizeData(seurat)
seurat <- FindVariableFeatures(seurat)
seurat <- ScaleData(seurat)
seurat <- RunPCA(seurat)
seurat <- RunUMAP(seurat, dims = 1:30)

# Mixscape: Classify perturbed vs non-perturbed cells
seurat <- CalcPerturbSig(
    seurat,
    assay = 'RNA',
    slot = 'data',
    new.assay.name = 'PRTB',
    gd.class = 'gene',
    nt.cell.class = 'NT',
    num.neighbors = 20,
    reduction = 'pca',
    ndims = 15
)

# Run Mixscape classification
seurat <- RunMixscape(
    seurat,
    assay = 'PRTB',
    slot = 'scale.data',
    labels = 'gene',
    nt.class.name = 'NT',
    min.de.genes = 5,
    iter.num = 10,
    de.assay = 'RNA',
    prtb.type = 'KO'
)

# View classification results
table(seurat$mixscape_class.global)
```

## Mixscape Visualization

```r
# UMAP colored by perturbation
DimPlot(seurat, reduction = 'umap', group.by = 'mixscape_class', label = TRUE)

# Perturbation score distribution
VlnPlot(seurat, features = 'mixscape_class_p_ko', group.by = 'gene')

# DE genes for each perturbation
MixscapeHeatmap(seurat, ident.1 = 'TP53', ident.2 = 'NT', balanced = TRUE)

# LDA projection
seurat <- MixscapeLDA(seurat, labels = 'gene', nt.class.name = 'NT')
LDAPlot(seurat)
```

## Guide Assignment from CRISPR Feature Barcode

```python
import pandas as pd

# From Cell Ranger output (CRISPR Guide Capture)
guides = pd.read_csv('crispr_analysis/protospacer_calls_per_cell.csv')

# Clean up guide calls
guides['cell_barcode'] = guides['cell_barcode'].str.replace('-1', '')
guides = guides[guides['num_features'] == 1]  # Single guide per cell

# Merge with expression data
adata.obs = adata.obs.merge(
    guides[['cell_barcode', 'feature_call', 'target_gene']],
    left_index=True,
    right_on='cell_barcode',
    how='left'
)
```

## Guide Quality Control

```python
# Check guide representation
guide_counts = adata.obs['target_gene'].value_counts()
print(f'Guides per target: {guide_counts.mean():.1f}')
print(f'Cells per guide: {adata.obs.groupby("guide_id").size().mean():.1f}')

# Filter low-representation guides
# Standard: keep guides with >= 100 cells
min_cells = 100
valid_guides = guide_counts[guide_counts >= min_cells].index
adata = adata[adata.obs['target_gene'].isin(valid_guides)]

# Check for guide bias
sc.pl.violin(adata, keys='n_genes_by_counts', groupby='target_gene', rotation=90)
```

## Multi-Guide Analysis

```python
# Cells with multiple guides (MOI > 1)
multi_guide = adata.obs[adata.obs['num_guides'] > 1]
print(f'Multi-guide cells: {len(multi_guide) / len(adata):.1%}')

# Options:
# 1. Remove multi-guide cells
adata = adata[adata.obs['num_guides'] == 1]

# 2. Keep only cells where guides target same gene
# 3. Analyze combinatorial effects
```

## Pseudobulk Differential Expression

```python
# Aggregate to pseudobulk for robust DE
from pertpy.tools import PseudobulkDE

pb = PseudobulkDE(adata)
pb.fit(
    groupby='target_gene',
    control='non-targeting',
    method='deseq2',  # or 'edger', 'wilcoxon'
    min_cells=50
)

# Get results for specific perturbation
tp53_de = pb.results('TP53')
sig_genes = tp53_de[tp53_de['padj'] < 0.05].sort_values('log2FoldChange')
```

## Pathway Enrichment

```python
import decoupler as dc

# Get DE genes per perturbation
de_results = pb.results()

# Run pathway enrichment
dc.run_ora(
    mat=de_results,
    net=dc.get_resource('MSigDB'),
    source='geneset',
    target='gene'
)

# Visualize top pathways
dc.plot_barplot(de_results, 'TP53', top_n=20)
```

## Screen QC Metrics

| Metric | Good | Acceptable | Poor |
|--------|------|------------|------|
| Cells per guide | >200 | 100-200 | <100 |
| Guide detection rate | >90% | 80-90% | <80% |
| Non-targeting cells | 5-15% | 15-25% | >25% |
| Mixscape KO fraction | >50% | 30-50% | <30% |

## Related Skills

- **Upstream**: routine scRNA-seq preprocessing (QC / clustering / annotation) → `single-cell/omicverse-pipeline`
- **Downstream 1**: predict perturbation response for **unmeasured** experiments → `single-cell/perturbation-prediction` (GEARS/CPA/scGPT, **linear baseline mandatory**)
- **Downstream 2**: perturbation-response DE / enrichment → `general-bio/omicverse-bulk` (pyDEG/pyGSEA)
- bulk CRISPR screen (no single-cell readout) → out of scope; use MAGeCK etc.

## Prerequisites (where data comes from)

- **Perturb-seq / CROP-seq raw data** (guides already mapped) → h5ad with an `obs['guide']` or `obs['perturbation']` column
- **Guide QC passed**: guide detection rate >80%, non-targeting fraction 5–25%, ≥100 cells per guide
- **`layers['counts']`** must be retained (perturbation DE uses pseudobulk + DESeq2)
- Tools: `pertpy` (primary) + `decoupler` (pathways) + optional Seurat Mixscape (via R)

## When to leave this skill (where to go)

- Predict **unmeasured** perturbations (unseen genes / drugs) → `single-cell/perturbation-prediction`
- Write Methods describing the Perturb-seq workflow → `presentation/methods-writer`
- Build a publication-grade figure from perturbation heatmap / dotplot → `visualization/multi-panel-figures`

## Key pitfalls

- **Wrong guide assignment corrupts everything downstream** — first use Mixscape to check that the KO signature is clear and that non-targeting vs targeting distributions are separated.
- **<100 cells per guide** makes pseudobulk DE unstable; report n per guide.
- **Perturbation DE must be pseudobulk** (aggregate by guide × sample), not per-cell Wilcoxon (pseudoreplication, meta-methodology principle ③).
- **MAGeCK RRA is for bulk screens** — do not treat Perturb-seq as a bulk screen.
- After finishing, run `scripts/postcheck.py` to verify: DE used pseudobulk, Padj reported, guide QC passed.
