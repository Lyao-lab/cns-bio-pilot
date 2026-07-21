# Reference: Seurat v5+ | SeuratObject 5+ | Verify API if version differs
# Perturb-seq classification with Seurat Mixscape (perturbed vs escaped cells)
#
# Data assumption: 10x feature-barcode matrix + guide calls in metadata.
# Canonical naming: guide identity column 'gene' holds the target gene name;
#                   non-targeting cells are labeled 'NT' (Mixscape convention).

library(Seurat)
library(SeuratObject)

# ---------------------------------------------------------------------------
# 1. Load + attach guide metadata
# ---------------------------------------------------------------------------
mat <- Read10X('filtered_feature_bc_matrix/')
seurat <- CreateSeuratObject(counts = mat, project = 'perturb_seq')

guide_calls <- read.csv('guide_calls.csv', row.names = 1)
seurat <- AddMetaData(seurat, metadata = guide_calls)

# ---------------------------------------------------------------------------
# 2. Standard preprocessing
# ---------------------------------------------------------------------------
seurat <- NormalizeData(seurat)
seurat <- FindVariableFeatures(seurat, nfeatures = 2000)
seurat <- ScaleData(seurat)
seurat <- RunPCA(seurat)
seurat <- RunUMAP(seurat, dims = 1:30)

# ---------------------------------------------------------------------------
# 3. Compute perturbation signature against non-targeting controls
#    (PCA-projected difference between each cell and its k-nearest NT cells)
# ---------------------------------------------------------------------------
seurat <- CalcPerturbSig(
    seurat,
    assay = 'RNA',
    slot = 'data',
    new.assay.name = 'PRTB',
    gd.class = 'gene',           # target gene column
    nt.cell.class = 'NT',        # non-targeting label
    num.neighbors = 20,
    reduction = 'pca',
    ndims = 15
)

# ---------------------------------------------------------------------------
# 4. Mixscape classification: perturbed (KO) vs escaped (NP)
# ---------------------------------------------------------------------------
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

table(seurat$mixscape_class.global)   # KO / NP / NT

# ---------------------------------------------------------------------------
# 5. Visualization
# ---------------------------------------------------------------------------
DimPlot(seurat, reduction = 'umap', group.by = 'mixscape_class', label = TRUE)
ggsave('mixscape_umap.pdf')

VlnPlot(seurat, features = 'mixscape_class_p_ko', group.by = 'gene')
ggsave('mixscape_pko_violin.pdf')

# LDA projection separates perturbed from escaped
seurat <- MixscapeLDA(seurat, labels = 'gene', nt.class.name = 'NT')
LDAPlot(seurat)
ggsave('mixscape_lda.pdf')

# ---------------------------------------------------------------------------
# 6. Perturbation vs NT differential expression for a target gene
# ---------------------------------------------------------------------------
de_results <- FindMarkers(
    seurat,
    ident.1 = 'TP53',     # target gene knockout
    ident.2 = 'NT',
    group.by = 'gene'
)
write.csv(de_results, 'de_TP53_vs_NT.csv')
