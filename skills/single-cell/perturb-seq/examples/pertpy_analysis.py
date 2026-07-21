"""Perturb-seq end-to-end analysis with pertpy 1.0.x (canonical example).

Reference: pertpy 1.0.3+ | scanpy 1.10+ | decoupler 1.x (install separately) | Verify API if version differs
Data assumption: h5ad with raw counts + obs columns:
  - obs['target_gene'] : gene targeted by the guide ('TP53', ...); control = 'non-targeting'
  - obs['replicate']   : biological replicate id (recommended for pseudobulk)

API notes (pertpy 0.7 → 1.0 breaking changes):
  - pt.tl.PseudobulkDE       → PseudobulkSpace.compute() + PyDESeq2/EdgeR/Statsmodels (LinearModelBase)
  - pt.tl.PerturbationSignature → pt.tl.Mixscape().perturbation_signature(...) (writes layers['X_pert'])
  - pt.tl.perturbation_embedding / cluster_perturbations → CentroidSpace.compute() + scanpy sc.tl.leiden
  - pt.pl.* is EMPTY in 1.0  → use model.plot_volcano() / mixscape.plot_heatmap() or sc.pl.*
"""
import scanpy as sc
import pertpy as pt
import pandas as pd

# ---------------------------------------------------------------------------
# 1. Load + annotate perturbations
# ---------------------------------------------------------------------------
adata = sc.read_h5ad('perturb_seq.h5ad')
adata.layers['counts'] = adata.X.copy()   # raw counts retained for pseudobulk DE

# If a guide UMI matrix is available as a separate modality, assign single-guide
# cells via pertpy's GuideAssignment (1.0 replacement for hand-parsed CSV):
# ga = pt.pp.GuideAssignment()
# ga.assign_to_max_guide(mdata['gdo'], assignment_threshold=5)   # writes .obs['assigned_guide']
adata.obs['target_gene'] = adata.obs['target_gene'].fillna('non-targeting')

# ---------------------------------------------------------------------------
# 2. Guide QC (see SKILL.md Screen QC table)
# ---------------------------------------------------------------------------
guide_counts = adata.obs['target_gene'].value_counts()
print(f'Cells per guide: mean {guide_counts.mean():.1f}')
valid_guides = guide_counts[guide_counts >= 100].index   # drop guides with <100 cells
adata = adata[adata.obs['target_gene'].isin(valid_guides)].copy()

# ---------------------------------------------------------------------------
# 3. Standard preprocessing (keep raw counts layer untouched)
# ---------------------------------------------------------------------------
sc.pp.filter_cells(adata, min_genes=200)
sc.pp.filter_genes(adata, min_cells=3)
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)
sc.pp.highly_variable_genes(adata, n_top_genes=2000, flavor='seurat_v3', layer='counts')
sc.pp.pca(adata)
sc.pp.neighbors(adata)
sc.tl.umap(adata)

# ---------------------------------------------------------------------------
# 4. Pseudobulk DE per perturbation vs non-targeting
#    (MANDATORY: per-cell Wilcoxon = pseudoreplication, meta-methodology principle 3)
#    4a. Aggregate to pseudobulk (PseudobulkSpace.compute — no min_cells in 1.0.3).
# ---------------------------------------------------------------------------
ps = pt.tl.PseudobulkSpace()
pdata = ps.compute(
    adata,
    target_col='target_gene',
    groups_col='replicate',     # omit if you have no replicate column
    layer_key='counts',         # MUST be raw integer counts for DESeq2/EdgeR
    mode='sum',
)
# Filter tiny pseudobulks manually (compute() has no min_cells arg in 1.0.3)
group_cols = ['target_gene', 'replicate'] if 'replicate' in adata.obs else ['target_gene']
n_cells = adata.obs.groupby(group_cols).size()
pdata = pdata[pdata.obs_names.isin(n_cells[n_cells >= 30].index)].copy()

#    4b. Fit DE model. design MUST be a formula string for compare_groups to work.
model = pt.tl.PyDESeq2(pdata, design='~target_gene')   # or pt.tl.EdgeR / pt.tl.Statsmodels
model.fit()
de = model.compare_groups(                               # one-shot classmethod
    pdata,
    column='target_gene',
    baseline='non-targeting',
    groups_to_compare=[g for g in pdata.obs['target_gene'].unique()
                       if g != 'non-targeting'],
)
sig = de[de['adj_p_value'] < 0.05]
print(f'Significant DE genes across perturbations: {len(sig)}')

#    4c. Volcano — pt.pl is empty in 1.0; use the model's own plot method.
model.plot_volcano(de, log2fc_thresh=1.0)

# ---------------------------------------------------------------------------
# 5. Perturbation signature (per-cell, control-subtracted)
#    Old pt.tl.PerturbationSignature is gone; use Mixscape.perturbation_signature.
# ---------------------------------------------------------------------------
ms = pt.tl.Mixscape()
ms.perturbation_signature(
    adata,
    pert_key='target_gene',
    control='non-targeting',
    ref_selection_mode='split_by' if 'replicate' in adata.obs else 'nn',
    split_by='replicate' if 'replicate' in adata.obs else None,
)   # writes adata.layers['X_pert']

# Derive a per-perturbation signature matrix by averaging X_pert per perturbation.
sig_adata = ps.compute(adata, target_col='target_gene',
                       layer_key='X_pert', mode='mean')

# ---------------------------------------------------------------------------
# 6. Perturbation-space embedding + clustering
#    Old perturbation_embedding / cluster_perturbations are gone;
#    use CentroidSpace + scanpy clustering on the perturbation-space AnnData.
# ---------------------------------------------------------------------------
cs = pt.tl.CentroidSpace()
ps_emb = cs.compute(adata, target_col='target_gene', embedding_key='X_umap')
sc.pp.neighbors(ps_emb, use_rep='X_umap')
sc.tl.leiden(ps_emb, resolution=0.5, key_added='perturbation_cluster')

# Optional: perturbation-minus-control effect on pseudobulks.
diff = ps.compute_control_diff(pdata, target_col='target_gene',
                               reference_key='non-targeting')

# ---------------------------------------------------------------------------
# 7. Visualization (pt.pl is empty in 1.0 — use scanpy / Mixscape methods)
# ---------------------------------------------------------------------------
sc.pl.umap(adata, color='target_gene')
sc.pl.heatmap(sig_adata, var_names=sig_adata.var_names[:30],
              groupby='target_gene', swap_axes=True)
ms.plot_heatmap(adata, pert_key='target_gene', control='non-targeting')

# ---------------------------------------------------------------------------
# 8. Pathway enrichment (decoupler was removed from pertpy at 0.11.4 —
#    import it separately, or use pt.tl.Enrichment)
# ---------------------------------------------------------------------------
import decoupler as dc   # pip install decoupler
dc.run_ora(mat=de, net=dc.get_resource('MSigDB'), source='geneset', target='variable')
