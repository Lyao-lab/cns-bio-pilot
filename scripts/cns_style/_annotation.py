"""_annotation — cns_style sub-module"""

import numpy as np
from ._constants import *


# ============================================================
# 9. add_cluster_labels() — on-plot labels with white halo (Nature 2024 style)
# ============================================================

def add_cluster_labels(ax, adata, basis='umap', groupby='celltype', fontsize=7,
                       palette=None):
    """Add cluster labels at median positions with white halo (no adjustText needed).

    This is the 2024-25 Nature/Cell convention: labels directly on the UMAP at
    cluster centroids, with a white stroke halo for readability over dense points.
    """
    import matplotlib.patheffects as pe
    basis_key = f'X_{basis}' if f'X_{basis}' in adata.obsm else basis
    coords = adata.obsm[basis_key]
    categories = adata.obs[groupby].cat.categories

    for i, cat in enumerate(categories):
        mask = (adata.obs[groupby] == cat).values
        if mask.sum() == 0:
            continue
        cx, cy = np.median(coords[mask], axis=0)
        color = NEAR_BLACK
        if palette and cat in palette:
            color = palette[cat]
        ax.text(cx, cy, str(cat), fontsize=fontsize, ha='center', va='center',
                color=color, fontweight='bold', fontfamily='Arial',
                path_effects=[pe.withStroke(linewidth=2.5, foreground='white')])


# ============================================================
# 9b. add_significance_bracket() — p-value annotation
# ============================================================


# ============================================================
# 9b. add_significance_bracket() — p-value annotation
# ============================================================

def add_significance_bracket(ax, x1, x2, pval, y=None, height_frac=0.03):
    """Add bracket + star between two groups. Auto-positions if y not given.

    Args:
        x1, x2: x positions of the two groups
        pval: p-value (determines star count)
        y: y position of bracket (auto = just above data max)
        height_frac: bracket height as fraction of y-range
    """
    if pval < 0.0001: star = '****'
    elif pval < 0.001: star = '***'
    elif pval < 0.01:  star = '**'
    elif pval < 0.05:  star = '*'
    else:              star = 'ns'

    ylim = ax.get_ylim()
    yrange = ylim[1] - ylim[0]
    if y is None:
        y = ylim[1] + yrange * 0.02
    h = yrange * height_frac

    ax.plot([x1, x1, x2, x2], [y, y+h, y+h, y],
            lw=0.8, color=NEAR_BLACK, clip_on=False)
    ax.text((x1+x2)/2, y+h, star, ha='center', va='bottom',
            fontsize=8, color=NEAR_BLACK)
    # Expand ylim to fit bracket
    ax.set_ylim(ylim[0], max(ylim[1], y+h+yrange*0.05))


# ============================================================
# 9c. Manifest functions (paper-level color consistency)
# ============================================================


def volcano_colors():
    """Return color dict for volcano plot (aligned with ov.pl.volcano defaults).

    Usage:
        colors = volcano_colors()
        ax.scatter(..., color=colors['up'])    # significant upregulated
        ax.scatter(..., color=colors['down'])  # significant downregulated
        ax.scatter(..., color=colors['ns'])    # not significant
    """
    return {
        'up': '#e25d5d',     # omicverse up_color (soft coral red)
        'down': '#7388c1',   # omicverse down_color (soft periwinkle blue)
        'ns': '#d7d7d7',     # omicverse normal_color (light grey)
        'ns_alpha': 0.6,     # slightly more visible than before
        'threshold': '#4C566A',  # threshold line color
    }



def gene_annotation_kwargs(fontsize=7):
    """Return annotation styling kwargs for gene labels (HGNC: italic).

    Usage: ax.annotate('CXCL12', ..., **gene_annotation_kwargs())
    """
    return {
        'fontsize': fontsize,
        'fontstyle': 'italic',   # gene names = italic (HGNC)
        'color': NEAR_BLACK,
        'arrowprops': dict(
            arrowstyle='-', lw=0.5, color=GREY,
            connectionstyle='arc3,rad=0.1'  # slight curve = elegant
        ),
    }


