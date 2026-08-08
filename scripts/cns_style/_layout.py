"""_layout — cns_style sub-module"""

import numpy as np
import matplotlib.pyplot as plt


# Global figure scale factor — set by set_cns_style_journal()
# 1.0 = generic (notebook/report), 0.7 = nature/cell (compact print)
_FIG_SCALE = 1.0


def _fs(w, h):
    """Apply global figure scale to a (width, height) tuple."""
    return (w * _FIG_SCALE, h * _FIG_SCALE)


# ============================================================
# 1. set_cns_style() — one-shot rcParams (call ONCE per script)
# ============================================================

# ============================================================
# 9d. Recipe helpers (figure_guide.md — high-frequency decisions)
# ============================================================

def point_size_for_n(n_obs):
    """Return scatter point size appropriate for cell count (prevents blob/faint).

    Usage: sc.pl.umap(adata, size=point_size_for_n(adata.n_obs), ...)
    """
    if n_obs < 10_000:
        return 8
    elif n_obs < 50_000:
        return 3
    elif n_obs < 200_000:
        return 1
    else:
        return 0.3



def recipe_figsize(chart_type, n_x=None, n_y=None, journal='generic'):
    """Compute figsize for common chart types (proportional to content).

    Args:
        chart_type: 'umap' | 'volcano' | 'heatmap' | 'dotplot' | 'violin' | 'bar' | 'spatial'
        n_x: number of x-axis categories (genes for heatmap, groups for violin/bar)
        n_y: number of y-axis categories (cell types for heatmap/dotplot)
        journal: scales down for 'nature'/'science' (smaller column width)

    Returns:
        (width, height) tuple in inches
    """
    scale = 0.8 if journal in ('nature', 'science', 'cell') else 1.0

    recipes = {
        'umap': (3.0, 3.0),
        'volcano': (3.0, 2.5),
        'feature': (2.0, 2.0),
        'spatial': (3.0, 2.8),
        'chord': (3.0, 3.0),
        'paga': (2.5, 2.2),
    }

    if chart_type in recipes:
        w, h = recipes[chart_type]
        return (w * scale, h * scale)
    elif chart_type == 'heatmap' and n_x and n_y:
        cell = 0.4  # 正方形单元格
        w = n_x * cell + 1.0   # +1.0" colorbar
        h = n_y * cell + 0.5
        return (w * scale, h * scale)
    elif chart_type == 'dotplot' and n_x and n_y:
        w = n_x * 0.5 + 1.0   # 每列 0.5"（点需要空间）+ 1.0" legend/colorbar
        h = n_y * 0.35 + 0.5
        return (w * scale, h * scale)
    elif chart_type in ('violin', 'bar') and n_x:
        w = n_x * 0.6 + 0.8   # 每组 0.6"
        h = 2.5
        return (w * scale, h * scale)
    else:
        return (3.0 * scale, 2.5 * scale)


# ============================================================
# 10. JOURNAL_PRESETS — journal-specific figure dimensions
# ============================================================
# Absorbed from SciencePlots' approach: declarative, journal-targeted presets.
# Dimensions from Nature/Science/Cell official author guidelines.

# ============================================================
# 15. figure_for_journal(journal, ncols, nrows) — sized figure
# ============================================================
def figure_for_journal(journal='generic', ncols=1, nrows=1, panel_width=1.0,
                       panel_height=1.0, wspace=0.35, hspace=0.4):
    """Create a figure sized for a specific journal's column width.

    Computes total figure size from journal column width × panel layout,
    so each panel is the right physical size for print.

    Args:
        journal: 'nature' | 'science' | 'cell' | 'generic'
        ncols, nrows: panel grid
        panel_width: width multiplier per panel (1.0 = full column / ncols)
        panel_height: height multiplier per panel
        wspace, hspace: GridSpec spacing

    Returns:
        (fig, axes) tuple

    Usage:
        fig, axes = figure_for_journal('nature', ncols=3, nrows=1)
        # 3 panels across Nature's 88mm column
    """
    preset = JOURNAL_PRESETS.get(journal, JOURNAL_PRESETS['generic'])
    col_width = preset['figure.figsize'][0]  # single column width in inches

    # Each panel gets col_width/ncols, adjusted by panel_width multiplier
    pw = (col_width / ncols) * panel_width
    ph = pw * panel_height  # default square-ish panels

    fig_w = pw * ncols + wspace * (ncols - 1) * pw
    fig_h = ph * nrows + hspace * (nrows - 1) * ph

    fig, axes = plt.subplots(nrows, ncols, figsize=(fig_w, fig_h),
                             squeeze=False)
    return fig, axes


# ============================================================
# 16. assert_anndata_keys(adata, ...) — defensive validation
# ============================================================

# ============================================================
# 17. cohort_params(n_cells) — size + alpha + figsize 联动
# ============================================================
def cohort_params(n_cells):
    """Return point size + alpha + figsize for a cohort of n_cells.

    替代仅有 size 的 point_size_for_n()（旧函数保留兼容，不删）：
    同一映射外加 alpha 与 figsize，避免大 cohort 糊成团或浅到看不见。

    映射表（数值参考 omicverse-skills plot1cell 经验；100k+ 档为梯度推断，
    按数据微调）:
        <10k      → point_size=8,   alpha=0.70, figsize=(4.5, 4.5)
        10k-50k   → point_size=3,   alpha=0.50, figsize=(5.0, 5.0)
        50k-100k  → point_size=1,   alpha=0.35, figsize=(5.5, 5.5)
        100k-200k → point_size=0.6, alpha=0.30, figsize=(6.0, 6.0)   # 推断值
        >200k     → point_size=0.3, alpha=0.25, figsize=(6.5, 6.5)   # 推断值

    Usage:
        p = cohort_params(adata.n_obs)
        sc.pl.umap(adata, size=p['point_size'], alpha=p['alpha'])
        fig.set_size_inches(*p['figsize'])
    """
    if n_cells < 10_000:
        return dict(point_size=6, alpha=0.7, figsize=(3.0, 3.0))
    elif n_cells < 50_000:
        return dict(point_size=3, alpha=0.5, figsize=(3.5, 3.5))
    elif n_cells < 100_000:
        return dict(point_size=1, alpha=0.35, figsize=(4.0, 4.0))
    elif n_cells < 200_000:
        # 数值参考 omicverse-skills plot1cell 经验；100k+ 档为梯度推断，按数据微调
        return dict(point_size=0.6, alpha=0.3, figsize=(6, 6))
    else:
        # 同上，推断值
        return dict(point_size=0.3, alpha=0.25, figsize=(6.5, 6.5))


# ============================================================
# 18. ForbiddenCityBridge + palette_from_names — 命名色板
# ============================================================
