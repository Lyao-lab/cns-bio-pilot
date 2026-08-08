"""plots_embedding — cns_style sub-module"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from ._constants import *
from ._axes import *
from ._layout import *
from ._save import *
from ._annotation import *
from ._helpers import *
from ._helpers import _check_ov, _adata_to_tidy, _resolve_group_mask, _resolve_signal
from ._layout import _fs, _FIG_SCALE


# ============================================================
# 20.1 plot_umap — UMAP/tSNE（ov.pl.embedding → mpl scatter）
# ============================================================

def plot_umap(adata, color='celltype', basis='X_umap', ax=None, figsize=None,
              save=None, labels=True, show=None, **kwargs):
    """UMAP/tSNE：ov.pl.embedding 优先，mpl scatter 兜底。"""
    if ax is None:
        p = cohort_params(adata.n_obs)
        fig, ax = plt.subplots(figsize=figsize or p['figsize'])
    else:
        fig = ax.figure
        p = cohort_params(adata.n_obs)
    if _check_ov():
        try:
            import omicverse as ov
            ov.pl.embedding(adata, basis=basis, color=color, ax=ax, show=False,
                            size=p['point_size'], alpha=p['alpha'], **kwargs)
            if labels:
                label_basis = basis.replace('X_', '') if basis.startswith('X_') else basis
                add_cluster_labels(ax, adata, basis=label_basis, groupby=color)
        except Exception as e:
            print(f"[smart_plot] ov.pl.embedding failed ({e}), mpl fallback")
            _umap_mpl(adata, color, basis, ax, p, labels, **kwargs)
    else:
        _umap_mpl(adata, color, basis, ax, p, labels, **kwargs)
    clean_umap_axes(ax)
    optical_margin(ax, 0.12)
    if save:
        save_panel(fig, save, show=show)
    return fig, ax


def _umap_mpl(adata, color, basis, ax, p, labels, **kwargs):
    """mpl UMAP: scatter by category + optional on-plot labels."""
    coords = np.asarray(adata.obsm[basis])
    cats = adata.obs[color].astype('category')
    for i, cat in enumerate(cats.cat.categories):
        mask = (cats == cat).values
        ax.scatter(coords[mask, 0], coords[mask, 1], s=p['point_size'],
                   alpha=p['alpha'], color=MORLANDI[i % len(MORLANDI)],
                   edgecolor='none', rasterized=True, label=str(cat))
    if labels:
        # 传原始 basis 给 add_cluster_labels（它内部有 X_ 前缀智能匹配），
        # 不做 replace/lower——数据可能用 UMAP/X_umap/umap 等不同 key
        label_basis = basis.replace('X_', '') if basis.startswith('X_') else basis
        add_cluster_labels(ax, adata, basis=label_basis, groupby=color)


# ============================================================
# 20.2 plot_volcano — 火山图（ov.pl.volcano → mpl 三色）
# ============================================================


# ============================================================
# 20.6 plot_spatial — 空间图（ov → squidpy → mpl scatter）
# ============================================================

def plot_spatial(adata_sp, color, ax=None, figsize=None, save=None,
                 alpha_img=1.0, spot_alpha=0.85, show=None, **kwargs):
    """Spatial：ov.pl.plot_spatial / sq.pl.spatial_scatter 优先，mpl scatter 兜底。"""
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize or recipe_figsize('spatial'))
    else:
        fig = ax.figure
    routed = False
    if _check_ov():
        try:
            import omicverse as ov
            ov.pl.plot_spatial(adata_sp, color=color, ax=ax, show=False,
                              alpha_img=alpha_img, alpha=spot_alpha, **kwargs)
            routed = True
        except Exception:
            pass
    if not routed:
        try:
            import squidpy as sq
            sq.pl.spatial_scatter(adata_sp, color=color, ax=ax, show=False,
                                  alpha_img=alpha_img, alpha=spot_alpha, **kwargs)
            routed = True
        except Exception:
            pass
    if not routed:
        print("[smart_plot] ov/sq spatial unavailable, mpl scatter fallback")
        _spatial_mpl(adata_sp, color, ax, spot_alpha)
    clean_umap_axes(ax, xlabel='', ylabel='')
    if save:
        save_panel(fig, save, show=show)
    return fig, ax


def _spatial_mpl(adata_sp, color, ax, spot_alpha):
    """mpl spatial: scatter on x/y coords + scale bar + colorbar."""
    # get coordinates
    if 'spatial' in adata_sp.obsm:
        coords = adata_sp.obsm['spatial']
    elif 'X_spatial' in adata_sp.obsm:
        coords = adata_sp.obsm['X_spatial']
    else:
        raise ValueError("No spatial coordinates in adata.obsm")
    # get expression
    if color in adata_sp.var_names:
        expr = adata_sp[:, color].X
        if hasattr(expr, 'toarray'):
            expr = expr.toarray()
        expr = np.asarray(expr).ravel()
    elif color in adata_sp.obs.columns:
        expr = adata_sp.obs[color].values
    else:
        raise ValueError(f"'{color}' not in var_names or obs")
    p99 = np.percentile(expr[expr > 0] if (expr > 0).any() else expr, 99)
    sc = ax.scatter(coords[:, 0], coords[:, 1], c=expr, cmap=EXPR_CMAP,
                    vmin=0, vmax=p99, s=1.5, alpha=spot_alpha,
                    edgecolor='none', rasterized=True)
    add_scale_bar(ax, length_um=200, px_per_um=1.0)  # adjust per platform
    add_elegant_colorbar(sc, ax, label=color, orientation='horizontal')
    ax.set_aspect('equal')


# ============================================================
# 20.7 plot_bar — 比例柱（ov 无，直接 mpl）
# ============================================================


# ============================================================
# 20.10 plot_feature_matrix — 多基因 UMAP 矩阵（ov 优先，mpl 兜底）
# ============================================================

def plot_feature_matrix(adata, genes, basis='X_umap', ax=None, figsize=None,
                        save=None, ncols=3, show=None, **kwargs):
    """Feature matrix：ov.pl.embedding 多 color 优先，mpl 多 subplot 兜底。"""
    if _check_ov():
        try:
            import omicverse as ov
            axs = ov.pl.embedding(adata, basis=basis, color=genes, ncols=ncols,
                                  show=False, **kwargs)
            axs = np.atleast_1d(axs).ravel()
            for a in axs:
                clean_umap_axes(a)
            fig = plt.gcf()
            n_genes = len(genes)
            nrows = int(np.ceil(n_genes / ncols))
            fig.set_size_inches(min(ncols * 2.0 + 0.5, 7.0), nrows * 2.0 + 0.3)
            if save:
                save_panel(fig, save, show=show)
            return fig, list(axs)
        except Exception as e:
            print(f"[smart_plot] ov.pl.embedding failed ({e}), mpl fallback")
    return _feature_matrix_mpl(adata, genes, basis, ncols, save, show)



def _feature_matrix_mpl(adata, genes, basis, ncols, save, show):
    """mpl feature matrix: multi-subplot scatter, shared vmax=99th pct."""
    import math
    coords = np.asarray(adata.obsm[basis])
    nrows = math.ceil(len(genes) / ncols)
    # 子图用 set_box_aspect(1) 保证正方形；figsize 按正方形子图算
    cell_w = 3.0
    cell_h = 3.0   # 正方形子图，宽=高
    fig, axes = plt.subplots(nrows, ncols, figsize=(ncols*cell_w, nrows*cell_h),
                             constrained_layout=True)
    axes = np.atleast_1d(axes).ravel()
    # shared vmax
    all_expr = []
    for g in genes:
        if g in adata.var_names:
            e = adata[:, g].X
            if hasattr(e, 'toarray'):
                e = e.toarray()
            all_expr.append(np.asarray(e).ravel())
    all_vals = np.concatenate(all_expr) if all_expr else np.array([0])
    vmax = np.percentile(all_vals[all_vals > 0] if (all_vals > 0).any() else all_vals, 99)
    for i, g in enumerate(genes):
        a = axes[i]
        if g in adata.var_names and i < len(all_expr):
            a.scatter(coords[:, 0], coords[:, 1], c=all_expr[i], cmap=EXPR_CMAP,
                      vmin=0, vmax=vmax, s=1.5, alpha=0.7, edgecolor='none',
                      rasterized=True)
        a.set_title(g, fontstyle='italic', fontsize=10, pad=4)
        a.set_box_aspect(1)   # matplotlib 3.2+ 正方形（比 set_aspect 在 constrained_layout 下更可靠）
        clean_umap_axes(a)
    # hide unused
    for j in range(len(genes), len(axes)):
        axes[j].set_visible(False)
    if save:
        save_panel(fig, save, show=show)
    return fig, list(axes)


# ============================================================
# 20.11 plot_paga — PAGA 轨迹抽象图（sc.pl.paga 优先，networkx 兜底）
# ============================================================

