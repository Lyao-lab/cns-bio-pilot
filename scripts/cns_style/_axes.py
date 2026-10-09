"""_axes — cns_style sub-module"""

import matplotlib.pyplot as plt
import numpy as np
from ._constants import *


# ============================================================
# 2. polish_axes(ax) — per-panel finishing touch
# ============================================================
def polish_axes(ax, keep_spines=('left', 'bottom'), subtle_grid=False,
                variant=None, grid_axis='y'):
    """CNS-grade axis styling: hide top/right spines, tick/grid/label cleanup.

    Apply to EVERY panel after plotting. For UMAP/tSNE use clean_umap_axes() instead.
    Gridlines are OFF by default.

    variant='bar': bar-chart look（fetal_heart 76/79 脚本的高频形态）——只留
    底脊并染 GREY_SCALE['spine']；tick length 2、标签 #444444；值轴浅网格
    （grid_axis='y' 竖条 / 'x' barh）。此变体忽略 keep_spines/subtle_grid。
    """
    if variant == 'bar':
        for side in ('top', 'right', 'left'):
            ax.spines[side].set_visible(False)
        sp = ax.spines['bottom']
        sp.set_visible(True)
        sp.set_color(GREY_SCALE['spine'])
        sp.set_linewidth(0.8)
        ax.tick_params(direction='out', length=2, labelsize=7.5,
                       colors='#444444')
        ax.grid(axis=grid_axis, color=GREY_SCALE['grid'], lw=0.6, zorder=0)
        ax.set_axisbelow(True)
        if ax.get_xlabel():
            ax.set_xlabel(ax.get_xlabel(), labelpad=8)
        return

    # Hide top/right spines (CNS convention: only left + bottom)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Tick styling (no tick marks, label sizing)
    ax.tick_params(direction='out', length=0, labelsize=8, colors=NEAR_BLACK)

    # Gridlines OFF by default (CNS style: clean background)
    ax.grid(False)
    if subtle_grid:
        ax.yaxis.grid(True, linewidth=0.3, alpha=0.15, color=GREY)
        ax.set_axisbelow(True)

    # Label offset
    if ax.get_xlabel():
        ax.set_xlabel(ax.get_xlabel(), labelpad=10)
    if ax.get_ylabel():
        ax.set_ylabel(ax.get_ylabel(), labelpad=10)


# ============================================================
# 3. clean_umap_axes(ax) — Nature sc-paper convention
# ============================================================

# ============================================================
# 3. clean_umap_axes(ax) — Nature sc-paper convention
# ============================================================
def clean_umap_axes(ax, xlabel='UMAP1', ylabel='UMAP2'):
    """Remove all axes/ticks for UMAP/tSNE (Nature single-cell convention)."""
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlabel(xlabel, labelpad=4, fontsize=7, color=GREY)
    ax.set_ylabel(ylabel, labelpad=4, fontsize=7, color=GREY)


# ============================================================
# 4. add_elegant_colorbar(mappable, ax, label)
# ============================================================

# ============================================================
# 4. add_elegant_colorbar(mappable, ax, label)
# ============================================================
def add_elegant_colorbar(mappable, ax, label='', ticks=None, **kw):
    """CNS-grade colorbar: slim, no border, few ticks, labelled.

    Replaces the ugly default plt.colorbar() which is too wide and has a border box.
    """
    cb = plt.colorbar(mappable, ax=ax,
                      fraction=0.025,    # narrow
                      pad=0.04,
                      aspect=15,
                      **kw)
    cb.outline.set_visible(False)       # no border box
    cb.ax.tick_params(direction='out', length=0, labelsize=7)
    if label:
        cb.set_label(label, fontsize=8, labelpad=6)
    # Reduce to ≤5 ticks for mini colorbar
    if ticks is not None:
        cb.set_ticks(ticks)
    else:
        existing = cb.get_ticks()
        if len(existing) > 5:
            step = max(1, len(existing) // 3)
            cb.set_ticks(existing[::step])
    return cb


# ============================================================
# 5. safe_scanpy_plot(func, *args, **kwargs)
# ============================================================

# ============================================================
# 7. optical_margin(ax, pad_fraction=0.15)
# ============================================================
def optical_margin(ax, pad_fraction=0.15):
    """Expand axes limits for circular/irregular data (optical compensation).

    UMAP/tSNE scatter looks smaller than square data at the same bounding box.
    Expand by 15% (not 10%) to appear "centered" to the human eye.
    """
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    xpad = (xlim[1] - xlim[0]) * pad_fraction
    ypad = (ylim[1] - ylim[0]) * pad_fraction
    ax.set_xlim(xlim[0] - xpad, xlim[1] + xpad)
    ax.set_ylim(ylim[0] - ypad, ylim[1] + ypad)


# ============================================================
# 8. add_panel_label(ax, label, offset=(-0.12, 1.08))
# ============================================================

# ============================================================
# 8. add_panel_label(ax, label, offset=(-0.12, 1.08))
# ============================================================
def add_panel_label(ax, label, offset=(-0.12, 1.08), fontsize=12):
    """Panel letter, Nature 流派：小写加粗 a/b/c、左上绘图区外、无句点（2026 原图实测）。

    fontsize 为画布尺度（12pt 画布 ≈ 终稿 8pt，按缩放比反推）；Cell 投稿传大写并
    可另叠 stamp_panel 陈述句标题。panel 字母 ≈ 轴标签 ×1.15-1.3、距图 2-5pt。
    """
    ax.text(offset[0], offset[1], label,
            transform=ax.transAxes,
            fontsize=fontsize, fontweight='bold',
            va='top', ha='right',
            fontfamily='Arial', color=NEAR_BLACK)


def label_panel(ax, letter, offset=(-0.12, 1.08), fontsize=12):
    """label_panel = add_panel_label 短名（Nature 小写加粗默认，如 label_panel(ax, 'a')）。"""
    add_panel_label(ax, letter, offset=offset, fontsize=fontsize)


# ============================================================
# 8b. finalize_figure(fig) — mandatory pre-save layout check
# ============================================================


# ============================================================
# 9c2. add_scale_bar() — spatial figure scale bar (mandatory)
# ============================================================

def add_scale_bar(ax, length_um=200, px_per_um=1.0, color=None,
                  fontsize=7, y_frac=0.05, x_frac=0.05):
    """Add a scale bar to a spatial plot (mandatory for spatial figures).

    Args:
        ax: matplotlib axes
        length_um: bar length in micrometers (pick from 100/200/500 closest to 1/5 figure width)
        px_per_um: pixels per micrometer (coordinate units per μm)
        color: bar/text color。**None（默认）= 按背景亮度自适应**（CNS 2026 实测：
            白底空间图=黑条黑字〔胎心 Fig2 '1 mm'〕；组织/H&E 深底=白条〔胚胎 Fig1、IF〕）；
            显式传色则强制
        fontsize: label font size
        y_frac: vertical position as fraction of axes height (from bottom)
        x_frac: horizontal position as fraction of axes width (from left)
    """
    import matplotlib.patheffects as pe
    if color is None:
        bg = ax.get_facecolor()
        lum = (0.299 * bg[0] + 0.587 * bg[1] + 0.114 * bg[2]) \
            if len(bg) > 3 and bg[3] > 0 else 1.0   # 透明背景按白处理
        color = '#2E3440' if lum > 0.5 else 'white'
    length_px = length_um * px_per_um
    xlim = ax.get_xlim(); ylim = ax.get_ylim()
    xdir = 1.0 if xlim[1] > xlim[0] else -1.0        # 翻转轴安全（fetal_heart 实测）
    xmin, xmax = (xlim[0], xlim[1]) if xdir > 0 else (xlim[1], xlim[0])
    ymin, ymax = min(ylim), max(ylim)
    span_x, span_y = xmax - xmin, ymax - ymin
    x0 = xmin + x_frac * span_x
    y0 = ymin + y_frac * span_y
    ax.plot([x0, x0 + xdir * length_px], [y0, y0], color=color, lw=2.5,
            solid_capstyle='butt', zorder=10, clip_on=False)
    ax.text(x0 + xdir * length_px / 2, y0 + 0.02 * span_y,
            f'{length_um:g} μm', ha='center', va='bottom', fontsize=fontsize,
            color=color, zorder=10, clip_on=False,
            path_effects=[pe.withStroke(linewidth=2,
                         foreground='black' if color == 'white' else 'white')])


# ============================================================
# 9d. Recipe helpers (figure_guide.md — high-frequency decisions)
# ============================================================

