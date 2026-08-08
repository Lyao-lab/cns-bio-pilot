#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
cns-bio-pilot cns_style — One-shot CNS-grade matplotlib aesthetics.

Usage:
    import sys; sys.path.insert(0, 'scripts/')
    from cns_style import set_cns_style, polish_axes, add_elegant_colorbar, \
                          safe_scanpy_plot, clean_umap_axes, apply_5plus1_palette, \
                          assert_anndata_keys, cohort_params, \
                          ForbiddenCityBridge, palette_from_names, save_panel

    set_cns_style()          # call ONCE at the top of every plotting script
    polish_axes(ax)          # apply to each panel after plotting
    add_elegant_colorbar(mappable, ax, label='log2 Expression')
    safe_scanpy_plot(sc.pl.umap, adata, color='ct', ax=ax, show=False)

    # 16-19: defensive validation + cohort-aware plotting + named palette + save
    assert_anndata_keys(adata, obs_cols=['celltype'], obsm_keys=['X_umap'])
    p = cohort_params(adata.n_obs)         # size/alpha/figsize 联动
    sc.pl.umap(adata, size=p['point_size'], alpha=p['alpha'])
    fig.set_size_inches(*p['figsize'])
    palette_from_names(['T_cell', 'B_cell'], ['霁蓝', '藤黄'])   # 命名色板
    save_panel(fig, 'A_umap')              # finalize → panels/A_umap.pdf

Philosophy:
    figure_guide.md = visual specs (the only figure reference needed)
    THIS file = the code that implements those specs.

All colors follow the Morlandi Nord palette (low-saturation, refined).
All font sizes follow a 1.2x modular scale from 7pt base.
"""
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.colors import LinearSegmentedColormap
import numpy as np

# ============================================================
# Palette definitions (Morlandi Nord — user-selected default)
# ============================================================
# Base 8 (for ≤8 categories; #D8DEE9 removed — too light on white background)
MORLANDI = ['#88C0D0', '#BF616A', '#A3BE8C', '#D08770',
            '#B48EAD', '#EBCB8B', '#5E81AC', '#81A1C1']

# Extended 20 (for atlas figures with 10-20+ cell types; low-saturation, harmonious)
MORLANDI_EXTENDED = MORLANDI + [
    '#7B9E89', '#C9ADA7', '#9A8C98', '#6D6875',
    '#B5838D', '#E5989B', '#8ECAE6', '#83C5BE',
    '#A2836E', '#C6DABF', '#B8B8FF', '#F4ACB7',
]

OKABE_ITO = ['#E69F00', '#56B4E9', '#009E73', '#F0E442',
             '#0072B2', '#D55E00', '#CC79A7', '#000000']

MUTED = '#C8CDD3'          # non-focus clusters
NEAR_BLACK = '#2E3440'     # axis/text color (Morlandi polar-night)
GREY = '#4C566A'           # annotation/subtle text (Morlandi grey)

# Condition colors (reserved for Normal/Disease narrative — NOT for cell types)
CONDITION_COLORS = {
    'Normal': '#88C0D0',    # cool = quiet (reserved)
    'Disease': '#BF616A',   # warm = active (reserved)
    'Treated': '#A3BE8C',   # recovery
    'Control': '#88C0D0',
    'Stimulated': '#D08770',
}

# Sequential: blue-yellow-red (low-saturation, bioinformatics consensus)
EXPR_CMAP = LinearSegmentedColormap.from_list('byr_morlandi',
    ['#5E81AC', '#8FBCD4', '#ECEFF4', '#D08770', '#9B5A5A'], N=256)

# Diverging: blue-white-red (0=white midpoint)
DIVERGING_CMAP = LinearSegmentedColormap.from_list('log2fc',
    ['#2C5F8D', '#88C0D0', '#FFFFFF', '#D08770', '#8B2C2C'], N=256)

# ForbiddenCity 命名色板 fallback（供函数 18 ForbiddenCityBridge 降级使用）
# fallback hex 为近似值，精确值需安装 omicverse 后 ov.pl.ForbiddenCity
FORBIDDEN_CITY_FALLBACK = {
    '凝夜紫': '#3D3B5A',
    '霁蓝': '#2E5C8A',
    '石英粉红': '#E8B4B8',
    '胭脂紫': '#9D5C6D',
    '藤黄': '#E8B835',
    '青矾绿': '#5C8D5C',
    '朱砂': '#C73E3A',
    '月白': '#B8CCE0',
    '黛色': '#4A4A4A',
    '牙色': '#F0E6D2',
}


# Global figure scale factor — set by set_cns_style_journal()
# 1.0 = generic (notebook/report), 0.7 = nature/cell (compact print)
_FIG_SCALE = 1.0

def _fs(w, h):
    """Apply global figure scale to a (width, height) tuple."""
    return (w * _FIG_SCALE, h * _FIG_SCALE)


# ============================================================
# 1. set_cns_style() — one-shot rcParams (call ONCE per script)
# ============================================================
def set_cns_style(base_fontsize=8, scale=1.2, palette='morlandi'):
    """One function call → CNS-grade matplotlib aesthetics.

    Args:
        base_fontsize: minimum readable size at print (default 8pt)
        scale: modular scale ratio (default 1.2 → sizes: 7/8/10/12/14)
        palette: 'morlandi' (default, soft) or 'okabe_ito' (colorblind gold)
    """
    colors = MORLANDI if palette == 'morlandi' else OKABE_ITO
    F = base_fontsize
    S = scale

    # Snap to modular scale [7, 8, 10, 12, 14] — never 9pt or 11pt
    _STEPS = [7, 8, 10, 12, 14]
    def _snap(v): return min(_STEPS, key=lambda x: abs(x - v))

    plt.rcParams.update({
        # --- Font (modular scale, snapped to 7/8/10/12/14) ---
        'font.family': 'sans-serif',
        'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
        'font.size': F,                              # 8pt (tick labels)
        'axes.titlesize': _snap(F * S**2),           # → 12
        'axes.labelsize': _snap(F * S**2),           # → 10
        'xtick.labelsize': F,                        # 8pt
        'ytick.labelsize': F,                        # 8pt
        'legend.fontsize': _snap(F * S),             # → 10
        'figure.titlesize': _snap(F * S**3),         # → 14

        # --- Color (Morlandi near-black, not pure #000) ---
        'axes.prop_cycle': plt.cycler(color=colors),
        'axes.edgecolor': NEAR_BLACK,
        'text.color': NEAR_BLACK,
        'axes.labelcolor': NEAR_BLACK,
        'xtick.color': NEAR_BLACK,
        'ytick.color': NEAR_BLACK,

        # --- Spines & ticks (L-frame, outward, no tick marks) ---
        'axes.linewidth': 0.8,
        'xtick.direction': 'out',
        'ytick.direction': 'out',
        'xtick.major.size': 0,       # no tick marks (label-only, ultra-clean)
        'ytick.major.size': 0,
        'xtick.major.pad': 4,        # gap between axis and label
        'ytick.major.pad': 4,

        # --- Grid (off by default; enable per-axis with alpha) ---
        'axes.grid': False,

        # --- Figure ---
        'figure.dpi': 150,            # display (lightweight for notebook)
        'figure.facecolor': 'white',
        'axes.facecolor': 'white',

        # --- Save (publication) ---
        'savefig.dpi': 300,
        'savefig.bbox': 'tight',
        'savefig.pad_inches': 0.1,   # breathing room (prevents legend clip)
        'savefig.format': 'pdf',
        'pdf.fonttype': 42,           # TrueType embedding (editable in Illustrator)
        'ps.fonttype': 42,
        'svg.fonttype': 'none',

        # --- Legend (compact, omicverse-style) ---
        'legend.frameon': False,
        'legend.borderaxespad': 0.3,
        'legend.numpoints': 1,
        'legend.scatterpoints': 1,
        'legend.handlelength': 0.5,
        'legend.handletextpad': 0.4,

        # --- Title ---
        'axes.titlepad': 8,
    })


# ============================================================
# 2. polish_axes(ax) — per-panel finishing touch
# ============================================================
def polish_axes(ax, keep_spines=('left', 'bottom'), subtle_grid=False):
    """CNS-grade axis styling: hide top/right spines, tick/grid/label cleanup.

    Apply to EVERY panel after plotting. For UMAP/tSNE use clean_umap_axes() instead.
    Gridlines are OFF by default.
    """
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
def safe_scanpy_plot(plot_func, *args, **kwargs):
    """Wrap sc.pl.* calls to prevent rcParams corruption.

    scanpy's plotting functions modify global rcParams (figure.figsize, etc).
    This saves and restores them around the call (try/finally ensures restore
    even if the plot function raises an exception).
    """
    saved = plt.rcParams.copy()
    try:
        result = plot_func(*args, **kwargs)
    finally:
        plt.rcParams.update(saved)
    return result


# ============================================================
# 6. apply_5plus1_palette(categories, focus_list)
# ============================================================
def apply_5plus1_palette(categories, focus_list, base_palette=None, accent=None):
    """≤5 named colors + 1 accent; everything else = grey.

    Args:
        categories: list of all category names (e.g. cell types)
        focus_list: which categories to highlight (≤6)
        base_palette: color list (default MORLANDI)
        accent: accent color for 6th focus item (default '#BF616A')

    Returns:
        dict {category: color} ready for sc.pl.* palette= argument
    """
    if base_palette is None:
        base_palette = MORLANDI
    if accent is None:
        accent = '#BF616A'

    result = {}
    for i, cat in enumerate(focus_list[:5]):
        result[cat] = base_palette[i % len(base_palette)]
    if len(focus_list) > 5:
        result[focus_list[5]] = accent
    for cat in categories:
        if cat not in result:
            result[cat] = MUTED
    return result


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
def add_panel_label(ax, label, offset=(-0.12, 1.08), fontsize=12):
    """Add A/B/C panel label in CNS style (bold, optically positioned)."""
    ax.text(offset[0], offset[1], label,
            transform=ax.transAxes,
            fontsize=fontsize, fontweight='bold',
            va='top', ha='right',
            fontfamily='Arial', color=NEAR_BLACK)


# ============================================================
# 8b. finalize_figure(fig) — mandatory pre-save layout check
# ============================================================

def finalize_figure(fig, move_legend_right=True, check_overlap=True,
                    check_rasterize=True, verbose=True):
    """Mandatory pre-save check: fix legend, detect text overlap, check rasterization.

    Call this BEFORE every fig.savefig(). It:
    1. Moves any in-axes legend to outside-right (铁律1)
    2. Detects text bounding-box overlaps and warns (铁律2)
    3. Warns if large scatter not rasterized (PDF bloat)

    Args:
        fig: matplotlib Figure
        move_legend_right: relocate legends to outside-right
        check_overlap: detect text overlaps (requires rendering)
        check_rasterize: warn if >50k points not rasterized
        verbose: print warnings
    """
    issues = []

    # Ensure figure is rendered (needed for bbox calculations)
    try:
        fig.draw_without_rendering()
        renderer = fig.canvas.get_renderer()
    except Exception:
        renderer = None

    for ax in fig.axes:
        # --- 铁律 1: Legend outside-right ---
        if move_legend_right and ax.get_legend() is not None:
            leg = ax.get_legend()
            if renderer:
                try:
                    leg_bb = leg.get_window_extent(renderer)
                    ax_bb = ax.get_window_extent(renderer)
                    if leg_bb.overlaps(ax_bb):
                        leg.set_bbox_to_anchor((1.02, 0.5), transform=ax.transAxes)
                        leg._loc = 6  # center left
                        issues.append("Legend moved to outside-right (was overlapping data)")
                except Exception:
                    pass
            else:
                # No renderer: conservatively move all legends outside
                leg.set_bbox_to_anchor((1.02, 0.5), transform=ax.transAxes)

        # --- 铁律 2: Text overlap detection ---
        if check_overlap and renderer:
            text_elements = []
            # Collect: title, xlabel, ylabel, tick labels, annotations
            if ax.title.get_text():
                text_elements.append(('title', ax.title))
            if ax.xaxis.label.get_text():
                text_elements.append(('xlabel', ax.xaxis.label))
            if ax.yaxis.label.get_text():
                text_elements.append(('ylabel', ax.yaxis.label))
            for txt in ax.texts:
                if txt.get_text().strip():
                    text_elements.append(('annotation', txt))

            # Check pairwise overlaps
            for i in range(len(text_elements)):
                for j in range(i+1, len(text_elements)):
                    try:
                        bb_i = text_elements[i][1].get_window_extent(renderer)
                        bb_j = text_elements[j][1].get_window_extent(renderer)
                        if bb_i.overlaps(bb_j):
                            issues.append(
                                f"Text overlap: '{text_elements[i][1].get_text()[:20]}' "
                                f"({text_elements[i][0]}) ↔ "
                                f"'{text_elements[j][1].get_text()[:20]}' "
                                f"({text_elements[j][0]}). Increase spacing or reduce text.")
                            break  # one warning per element pair is enough
                    except Exception:
                        pass

        # --- Rasterization check ---
        if check_rasterize:
            for coll in ax.collections:
                try:
                    n_pts = len(coll.get_offsets())
                    if n_pts > 50000 and not coll.get_rasterized():
                        issues.append(
                            f"Large scatter ({n_pts} points) not rasterized — "
                            f"PDF will be huge. Add rasterized=True.")
                        break
                except Exception:
                    pass

    if issues and verbose:
        print("⚠️  finalize_figure warnings:")
        for issue in issues:
            print(f"   - {issue}")

    return fig


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

def init_manifest(celltypes, conditions=None, path='manifest.yaml', palette=None):
    """Create manifest.yaml locking cell-type and condition colors for a paper.

    Call ONCE at project start. All figure scripts then use load_manifest().
    """
    import yaml
    if palette is None:
        palette = MORLANDI_EXTENDED if len(celltypes) > 8 else MORLANDI

    ct_colors = {ct: palette[i % len(palette)] for i, ct in enumerate(celltypes)}
    cond_colors = conditions or {}

    manifest = {
        'cell_type_colors': ct_colors,
        'condition_colors': cond_colors if cond_colors else CONDITION_COLORS,
        'sequential_cmap': 'byr_morlandi',
        'diverging_cmap': 'log2fc',
        'font_base': 8,
        'scale_ratio': 1.2,
    }
    with open(path, 'w') as f:
        yaml.dump(manifest, f, default_flow_style=False, allow_unicode=True)
    print(f"Manifest saved: {path} ({len(ct_colors)} cell types)")
    return manifest


def load_manifest(path='manifest.yaml'):
    """Load manifest.yaml and apply colors globally. Returns color dicts.

    Usage:
        ct_colors, cond_colors = load_manifest('manifest.yaml')
        sc.pl.umap(adata, color='celltype', palette=ct_colors)
    """
    import yaml
    with open(path) as f:
        m = yaml.safe_load(f)
    ct_colors = m.get('cell_type_colors', {})
    cond_colors = m.get('condition_colors', CONDITION_COLORS)
    # Apply to matplotlib prop_cycle
    if ct_colors:
        plt.rcParams['axes.prop_cycle'] = plt.cycler(color=list(ct_colors.values()))
    return ct_colors, cond_colors


# ============================================================
# 9c2. add_scale_bar() — spatial figure scale bar (mandatory)
# ============================================================

def add_scale_bar(ax, length_um=200, px_per_um=1.0, color='white',
                  fontsize=7, y_frac=0.05, x_frac=0.05):
    """Add a scale bar to a spatial plot (mandatory for spatial figures).

    Args:
        ax: matplotlib axes
        length_um: bar length in micrometers (pick from 100/200/500 closest to 1/5 figure width)
        px_per_um: pixels per micrometer (coordinate units per μm)
        color: bar/text color (white on dark tissue, #2E3440 on light)
        fontsize: label font size
        y_frac: vertical position as fraction of axes height (from bottom)
        x_frac: horizontal position as fraction of axes width (from left)
    """
    import matplotlib.patheffects as pe
    length_px = length_um * px_per_um
    xlim = ax.get_xlim(); ylim = ax.get_ylim()
    x0 = xlim[0] + (xlim[1] - xlim[0]) * x_frac
    y0 = ylim[0] + (ylim[1] - ylim[0]) * y_frac
    ax.plot([x0, x0 + length_px], [y0, y0], color=color, lw=2.5,
            solid_capstyle='butt', zorder=10)
    ax.text(x0 + length_px / 2, y0 + (ylim[1] - ylim[0]) * 0.02,
            f'{length_um} μm', ha='center', va='bottom', fontsize=fontsize,
            color=color, zorder=10,
            path_effects=[pe.withStroke(linewidth=2, foreground='black'
                         if color == 'white' else 'white')])


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
JOURNAL_PRESETS = {
    'nature': {
        'figure.figsize': (3.46, 2.6),      # 88mm single column (inches)
        'font.size': 7,
        'axes.labelsize': 7,
        'axes.titlesize': 8,
        'xtick.labelsize': 6,
        'ytick.labelsize': 6,
        'legend.fontsize': 6,
        'figure.titlesize': 8,
        'savefig.dpi': 600,                   # Nature requires 600 for line art
        'lines.linewidth': 0.8,
        'axes.linewidth': 0.6,
    },
    'nature_double': {
        'figure.figsize': (7.09, 5.0),      # 180mm double column
        'font.size': 7,
        'axes.labelsize': 7,
        'axes.titlesize': 8,
        'xtick.labelsize': 6,
        'ytick.labelsize': 6,
        'legend.fontsize': 6,
        'figure.titlesize': 8,
        'savefig.dpi': 600,
        'lines.linewidth': 0.8,
        'axes.linewidth': 0.6,
    },
    'science': {
        'figure.figsize': (3.35, 2.5),      # 85mm single column
        'font.size': 7,
        'axes.labelsize': 7,
        'axes.titlesize': 8,
        'xtick.labelsize': 6.5,
        'ytick.labelsize': 6.5,
        'legend.fontsize': 6,
        'figure.titlesize': 8,
        'savefig.dpi': 300,
        'lines.linewidth': 0.75,
        'axes.linewidth': 0.5,
    },
    'cell': {
        'figure.figsize': (3.35, 2.6),      # ~85mm single column
        'font.size': 7,
        'axes.labelsize': 7,
        'axes.titlesize': 8,
        'xtick.labelsize': 6,
        'ytick.labelsize': 6,
        'legend.fontsize': 6,
        'figure.titlesize': 8,
        'savefig.dpi': 300,
        'lines.linewidth': 0.8,
        'axes.linewidth': 0.6,
    },
    'generic': {
        'figure.figsize': (5, 4),           # general-purpose (notebook/report)
        'font.size': 8,
        'axes.labelsize': 10,
        'axes.titlesize': 12,
        'xtick.labelsize': 8,
        'ytick.labelsize': 8,
        'legend.fontsize': 8,
        'figure.titlesize': 14,
        'savefig.dpi': 300,
        'lines.linewidth': 1.0,
        'axes.linewidth': 0.8,
    },
}


# ============================================================
# 11. set_cns_style(journal=...) — now with journal presets
# ============================================================
def set_cns_style_journal(journal='generic', palette='morlandi'):
    """Apply CNS style + journal-specific dimensions/fonts.

    Combines the base set_cns_style() aesthetic decisions with journal-specific
    figure size and font scaling. Use this instead of set_cns_style() when
    targeting a specific journal.

    Args:
        journal: 'nature' | 'nature_double' | 'science' | 'cell' | 'generic'
        palette: 'morlandi' (default) | 'okabe_ito'

    Usage:
        set_cns_style_journal('nature')   # for Nature single-column figures
        set_cns_style_journal('cell')     # for Cell figures
    """
    set_cns_style(palette=palette)  # base aesthetics
    preset = JOURNAL_PRESETS.get(journal, JOURNAL_PRESETS['generic'])
    plt.rcParams.update(preset)
    # 设置全局 figure 缩放因子（顶刊紧凑，通用正常）
    global _FIG_SCALE
    _FIG_SCALE = 0.72 if journal in ('nature', 'science', 'cell', 'nature_double') else 1.0


# ============================================================
# 12. save_cns_mplstyle(path, journal) — declarative export
# ============================================================
def save_cns_mplstyle(path='cns_style.mplstyle', journal='generic', palette='morlandi'):
    """Export CNS style as a .mplstyle file (declarative, composable).

    Absorbed from SciencePlots' philosophy: styles should be declarative files
    that can be loaded with plt.style.use() and COMPOSED with other styles
    (e.g. plt.style.use(['cns_nature.mplstyle', 'seaborn-v0_8-whitegrid'])).

    Args:
        path: output .mplstyle file path
        journal: 'nature' | 'science' | 'cell' | 'generic'
        palette: 'morlandi' | 'okabe_ito'

    Usage:
        save_cns_mplstyle('cns_nature.mplstyle', journal='nature')
        # Then in any script:
        plt.style.use('cns_nature.mplstyle')
    """
    colors = MORLANDI if palette == 'morlandi' else OKABE_ITO
    preset = JOURNAL_PRESETS.get(journal, JOURNAL_PRESETS['generic'])
    F = preset['font.size']

    lines = [
        "# CNS Bio-Pilot style (Morlandi Nord palette)",
        f"# Journal preset: {journal}",
        f"# Generated by cns_style.py — composable with plt.style.use()",
        "",
        "# --- Font (modular scale, Arial/Helvetica) ---",
        "font.family: sans-serif",
        "font.sans-serif: Arial, Helvetica, DejaVu Sans",
        f"font.size: {F}",
        f"axes.titlesize: {preset['axes.titlesize']}",
        f"axes.labelsize: {preset['axes.labelsize']}",
        f"xtick.labelsize: {preset['xtick.labelsize']}",
        f"ytick.labelsize: {preset['ytick.labelsize']}",
        f"legend.fontsize: {preset['legend.fontsize']}",
        f"figure.titlesize: {preset['figure.titlesize']}",
        "",
        "# --- Color (Morlandi near-black, not pure #000) ---",
        f"axes.prop_cycle: cycler('color', {colors})",
        f"axes.edgecolor: {NEAR_BLACK}",
        f"text.color: {NEAR_BLACK}",
        f"axes.labelcolor: {NEAR_BLACK}",
        f"xtick.color: {NEAR_BLACK}",
        f"ytick.color: {NEAR_BLACK}",
        "",
        "# --- Spines & ticks (L-frame, outward, no tick marks) ---",
        f"axes.linewidth: {preset['axes.linewidth']}",
        "xtick.direction: out",
        "ytick.direction: out",
        "xtick.major.size: 0",
        "ytick.major.size: 0",
        "xtick.major.pad: 4",
        "ytick.major.pad: 4",
        "",
        "# --- Grid (off; enable per-axis with alpha) ---",
        "axes.grid: False",
        "",
        "# --- Figure ---",
        f"figure.figsize: {preset['figure.figsize']}",
        "figure.facecolor: white",
        "axes.facecolor: white",
        f"lines.linewidth: {preset['lines.linewidth']}",
        "",
        "# --- Save (publication) ---",
        f"savefig.dpi: {preset['savefig.dpi']}",
        "savefig.bbox: tight",
        "savefig.pad_inches: 0.1",
        "savefig.format: pdf",
        "pdf.fonttype: 42",
        "ps.fonttype: 42",
        "",
        "# --- Legend ---",
        "legend.frameon: False",
        "legend.borderaxespad: 0.3",
        "",
        "# --- Title ---",
        "axes.titlepad: 8",
    ]
    with open(path, 'w') as f:
        f.write('\n'.join(lines) + '\n')
    print(f"Saved: {path} (journal={journal}, palette={palette})")


# ============================================================
# 13. cns_style() context manager — temporary style application
# ============================================================
class cns_style:
    """Context manager for temporary CNS style (like plt.style.context).

    Usage:
        with cns_style('nature'):
            fig, ax = plt.subplots()
            # ... plot with Nature dimensions/fonts ...
        # rcParams restored after the block
    """
    def __init__(self, journal='generic', palette='morlandi'):
        self.journal = journal
        self.palette = palette
        self._saved = None

    def __enter__(self):
        self._saved = plt.rcParams.copy()
        set_cns_style_journal(self.journal, self.palette)
        return self

    def __exit__(self, *args):
        plt.rcParams.update(self._saved)


# ============================================================
# 14. cns_seaborn_context() — seaborn integration
# ============================================================
def cns_seaborn_context(journal='generic', palette='morlandi'):
    """Configure seaborn to match CNS style (preserves Morlandi palette).

    Call AFTER set_cns_style() or set_cns_style_journal(). Sets seaborn's
    context to 'paper' with our font scale, and sets the color palette to
    Morlandi (or Okabe-Ito).

    Usage:
        set_cns_style_journal('nature')
        cns_seaborn_context('nature')
        sns.boxplot(data=df, x='group', y='value')  # uses Morlandi colors
    """
    try:
        import seaborn as sns
    except ImportError:
        print("seaborn not installed — skip. pip install seaborn")
        return

    preset = JOURNAL_PRESETS.get(journal, JOURNAL_PRESETS['generic'])
    font_scale = preset['font.size'] / 8.0  # relative to seaborn's default 8pt

    colors = MORLANDI if palette == 'morlandi' else OKABE_ITO

    # Order matters: set_context first (sets sizes), then palette (sets colors)
    sns.set_context('paper', font_scale=font_scale, rc={
        'font.family': 'sans-serif',
        'axes.edgecolor': NEAR_BLACK,
        'axes.linewidth': preset['axes.linewidth'],
        'grid.linewidth': 0.3,
        'grid.alpha': 0.15,
    })
    sns.set_palette(colors)


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
def assert_anndata_keys(adata, obs_cols=None, obsm_keys=None, var_names=None):
    """Defensive validation: assert required keys exist in an AnnData object.

    对标 omicverse-skills 的防御校验模式：缺失即 raise ValueError，
    报错信息列出可用选项，调用方一眼就能修正。纯校验，成功返回 None。

    Usage:
        assert_anndata_keys(adata, obs_cols=['celltype'], obsm_keys=['X_umap'])
    """
    obs_cols = list(obs_cols or [])
    obsm_keys = list(obsm_keys or [])
    var_names = list(var_names or [])

    for col in obs_cols:
        if col not in adata.obs.columns:
            raise ValueError(
                f"Column '{col}' not found in adata.obs. "
                f"Available: {list(adata.obs.columns)}")
    for key in obsm_keys:
        if key not in adata.obsm.keys():
            raise ValueError(
                f"Key '{key}' not found in adata.obsm. "
                f"Available: {list(adata.obsm.keys())}")
    for name in var_names:
        if name not in adata.var_names:
            # var_names 可能很大，只列前 10 个避免刷屏
            avail = list(adata.var_names[:10]) + ['...'] if len(adata.var_names) > 10 \
                else list(adata.var_names)
            raise ValueError(
                f"Gene '{name}' not found in adata.var_names "
                f"({len(adata.var_names)} total). Available: {avail}")
    return None


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
class ForbiddenCityBridge:
    """ov.pl.ForbiddenCity() 命名色板桥：omicverse 可用则用精确色，否则降级 fallback。

    设计目标：脚本在最小环境（无 omicverse）中不因色板缺失而崩溃。
    fallback hex 为近似值，精确值需 ov.pl.ForbiddenCity（omicverse）。

    Usage:
        b = ForbiddenCityBridge()
        color = b.get('霁蓝')          # fallback 为 '#2E5C8A'
        names = b.available_names      # 中文色名列表（优先 ov，否则 fallback）
    """
    def __init__(self):
        self._fb = None
        try:
            import omicverse as ov
            self._fb = ov.pl.ForbiddenCity()
        except Exception:
            self._fb = None  # 无 omicverse → 走 FORBIDDEN_CITY_FALLBACK

    def get(self, name):
        """Return hex (str) for a Chinese color name (ov exact, else fallback).

        ov 2.3.1 的 get_color() 返回 1 行 DataFrame（含 color_html 列），
        这里统一提取为 hex 字符串；ov 版本 API 差异则降级 fallback。
        """
        if self._fb is not None:
            try:
                res = self._fb.get_color(name)
                if hasattr(res, 'iloc'):          # DataFrame → 取 color_html
                    return str(res['color_html'].iloc[0])
                if isinstance(res, str):
                    return res
            except Exception:
                pass  # ov 版本 API 差异 → 降级 fallback
        if name in FORBIDDEN_CITY_FALLBACK:
            return FORBIDDEN_CITY_FALLBACK[name]
        raise KeyError(
            f"Color '{name}' not found. Available: {self.available_names}")

    @property
    def available_names(self):
        """List of Chinese color names (ov first, else fallback keys)."""
        if self._fb is not None:
            for attr in ('color_pd', 'color'):
                try:
                    res = getattr(self._fb, attr)
                    if hasattr(res, 'iloc') and 'name' in res.columns:
                        return list(res['name'])
                    if isinstance(res, dict):
                        return [v['name'] for v in res.values()]
                except Exception:
                    continue
        return list(FORBIDDEN_CITY_FALLBACK.keys())


def palette_from_names(celltypes, color_names):
    """Map cell types to named-palette hex → {celltype: hex}.

    内部实例化 ForbiddenCityBridge（omicverse 可用则精确色，否则近似 fallback）。

    Usage:
        palette_from_names(['T_cell', 'B_cell'], ['霁蓝', '藤黄'])
        # → {'T_cell': '#2E5C8A', 'B_cell': '#E8B835'}   (fallback 近似值)
    """
    bridge = ForbiddenCityBridge()
    if len(color_names) < len(celltypes):
        print(f"⚠️  palette_from_names: {len(color_names)} colors for "
              f"{len(celltypes)} cell types — 不足部分未映射，请补齐 color_names.")
    return {ct: bridge.get(name) for ct, name in zip(celltypes, color_names)}


# ============================================================
# 19. save_panel(fig, name, ...) — 统一 save 入口
# ============================================================
def save_panel(fig, name, outdir='panels', journal=True, fmt='pdf', show=None):
    """Unified save entry: finalize_figure → mkdir → savefig → close/display → print path.

    流程：强制 finalize_figure（铁律 1 图例 / 铁律 2 文字重叠 / 栅格化检查）
    → 建目录 → savefig → 按 show 决定是否 close → 打印保存路径。

    Args:
        fig: matplotlib Figure
        name: 文件名（不含扩展名）
        outdir: 输出目录（默认 'panels'，自动创建）
        journal: True → dpi 走 rcParams['savefig.dpi']；False → 固定 300
        fmt: 'pdf' | 'png' | 'svg'（默认 'pdf'）
        show: None（默认）→ 自动检测：Jupyter notebook 中为 True（savefig 后不 close，
              figure 在 cell 输出显示）；纯脚本中为 False（savefig 后 close）。
              True → 强制保留显示（notebook 场景）；
              False → 强制 close（脚本批处理场景）

    Returns:
        str: 保存的完整路径

    Usage:
        save_panel(fig, 'A_umap')   # → 保存到 panels/A_umap.pdf，返回路径
    """
    import os
    if show is None:
        try:
            from IPython import get_ipython
            ip = get_ipython()
            show = ip is not None and 'ZMQ' in type(ip).__name__
        except Exception:
            show = False
    finalize_figure(fig)  # 强制 pre-save 检查（铁律 1/2 + 栅格化）
    # name 含路径分隔符 → 视为完整路径（不再拼 outdir）；否则拼 outdir/name
    if '/' in name or '\\' in name:
        path = f'{name}.{fmt}'
        out_dir = os.path.dirname(path)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
    else:
        os.makedirs(outdir, exist_ok=True)
        path = f'{outdir}/{name}.{fmt}'

    dpi = plt.rcParams['savefig.dpi'] if journal else 300
    fig.savefig(path, dpi=dpi, bbox_inches='tight', pad_inches=0.1)
    if not show:
        plt.close(fig)
    print(f"Saved: {path} (dpi={dpi})" + (" [figure displayed in notebook]" if show else ""))
    return path


# ============================================================
# Quick demo (run directly to see the style)
# ============================================================
if __name__ == '__main__':
    set_cns_style()
    print("CNS style applied. Current rcParams:")
    print(f"  font.size = {plt.rcParams['font.size']}")
    print(f"  axes.edgecolor = {plt.rcParams['axes.edgecolor']}")
    print(f"  savefig.dpi = {plt.rcParams['savefig.dpi']}")
    print(f"  xtick.direction = {plt.rcParams['xtick.direction']}")
    print("\nPalette (Morlandi Nord):")
    for i, c in enumerate(MORLANDI):
        print(f"  [{i}] {c}")
    print("\nJournal presets available:", list(JOURNAL_PRESETS.keys()))
    print("\nUsage:")
    print("  from cns_style import set_cns_style_journal, save_cns_mplstyle, cns_style")
    print("  set_cns_style_journal('nature')          # apply Nature preset")
    print("  save_cns_mplstyle('cns.mplstyle')        # export as declarative file")
    print("  with cns_style('nature'): ...            # temporary style block")
    print("  fig, axes = figure_for_journal('nature', ncols=3)  # sized panels")

    # --- 16-19: new functions demo ---
    print("\n--- 16. assert_anndata_keys (fake adata, no anndata needed) ---")
    import types
    fake_adata = types.SimpleNamespace(
        obs=types.SimpleNamespace(columns=['celltype', 'sample']),
        obsm=types.SimpleNamespace(keys=lambda: ['X_umap', 'X_pca']),
        var_names=['CD3D', 'CD79A'],
    )
    assert_anndata_keys(fake_adata, obs_cols=['celltype'], obsm_keys=['X_umap'])
    print("  OK: all requested keys present")

    print("\n--- 17. cohort_params ---")
    for n in (5_000, 30_000, 75_000, 150_000, 300_000):
        print(f"  n={n:>7} → {cohort_params(n)}")

    print("\n--- 18. ForbiddenCityBridge + palette_from_names ---")
    b = ForbiddenCityBridge()
    print("  available[:3]:", b.available_names[:3])
    print("  get('霁蓝'):", b.get('霁蓝'))
    print("  palette_from_names:",
          palette_from_names(['T_cell', 'B_cell'], ['霁蓝', '藤黄']))

    print("\n--- 19. save_panel (to /tmp/agent_out/cns_demo) ---")
    try:
        fig, ax = plt.subplots(figsize=(2, 1.5))
        ax.scatter([0, 1], [0, 1], s=20)
        path = save_panel(fig, 'demo_save_panel', outdir='/tmp/agent_out/cns_demo',
                          journal=False, fmt='png')
        print("  save_panel path:", path)
    except Exception as e:
        print(f"  save_panel demo skipped (no renderer): {e}")


# ============================================================
# 20. Smart plot — 统一入口 + ov/mpl 自动降级
# ============================================================
# 每个图型一个 plot_xxx()：ov.pl 优先，mpl 兜底，API 失败也降级。
# 用户/agent 只调一个函数，不需要判断走哪条路。
# ============================================================

_HAS_OV = None
def _check_ov():
    """检测 omicverse 是否可用（缓存）。"""
    global _HAS_OV
    if _HAS_OV is None:
        try:
            import omicverse as ov  # noqa
            _HAS_OV = True
        except Exception:
            _HAS_OV = False
    return _HAS_OV

def _lighten_color(hex_color, amount=0.8):
    """Lighten hex toward white（交替背景带用）。"""
    from matplotlib.colors import to_rgb
    r, g, b = to_rgb(hex_color)
    return (r + (1-r)*amount, g + (1-g)*amount, b + (1-b)*amount)


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

def plot_volcano(de, pval_name='padj', fc_name='log2FC', ax=None, figsize=None,
                 save=None, annotate_top=10, sig_pval=0.05, sig_fc=1.0, show=None, **kwargs):
    """Volcano：ov.pl.volcano 优先，mpl 三色兜底（优化版：up+down 都标注）。"""
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize or recipe_figsize('volcano'))
    else:
        fig = ax.figure
    if _check_ov():
        try:
            import omicverse as ov
            ov.pl.volcano(de, pval_name=pval_name, fc_name=fc_name,
                         pval_max=sig_pval, FC_max=sig_fc,
                         plot_genes_num=annotate_top)
            fig_ov = plt.gcf()
            fig_ov.set_size_inches(*recipe_figsize('volcano'))
            ax = fig_ov.axes[0] if fig_ov.axes else ax
            fig = fig_ov
            if save:                          # 修复：ov 路径也要走 save_panel
                save_panel(fig, save, show=show)
            return fig, ax  # ov 自建 figure，直接返回
        except Exception as e:
            print(f"[smart_plot] ov.pl.volcano failed ({e}), mpl fallback")
    _volcano_mpl(de, pval_name, fc_name, ax, annotate_top, sig_pval, sig_fc)
    polish_axes(ax)
    if save:
        save_panel(fig, save, show=show)
    return fig, ax

def _volcano_mpl(de, pval_name, fc_name, ax, annotate_top, sig_pval, sig_fc):
    """mpl volcano: 三色 + up/down 都标注 + 阈值标签。"""
    vc = volcano_colors()
    up = (de[pval_name] < sig_pval) & (de[fc_name] > sig_fc)
    dn = (de[pval_name] < sig_pval) & (de[fc_name] < -sig_fc)
    ns = ~(up | dn)
    logp = -np.log10(de[pval_name].clip(lower=1e-300))
    ax.scatter(de.loc[ns, fc_name], logp[ns], s=4, alpha=0.3, color=vc['ns'],
               edgecolor='none', rasterized=True, label='NS')
    ax.scatter(de.loc[up, fc_name], logp[up], s=6, color=vc['up'],
               edgecolor='none', label='Up')
    ax.scatter(de.loc[dn, fc_name], logp[dn], s=6, color=vc['down'],
               edgecolor='none', label='Down')
    ax.axhline(-np.log10(sig_pval), color=vc['threshold'], ls='--', lw=0.5, alpha=0.3)
    ax.text(ax.get_xlim()[0], -np.log10(sig_pval)+0.3, f'p={sig_pval}',
            fontsize=6, color=GREY)
    for v in (sig_fc, -sig_fc):
        ax.axvline(v, color=vc['threshold'], ls='--', lw=0.5, alpha=0.3)
    # up + down 都标注 top N
    gene_col = 'gene' if 'gene' in de.columns else de.index.name or 'index'
    for mask, direction in [(up, 'up'), (dn, 'down')]:
        sub = de.loc[mask]
        if len(sub) == 0:
            continue
        n = min(annotate_top, len(sub))
        if direction == 'up':
            top = sub.nlargest(n, fc_name)
        else:
            top = sub.nsmallest(n, fc_name)
        for _, r in top.iterrows():
            gene = r['gene'] if 'gene' in r else r.name
            ax.annotate(gene, xy=(r[fc_name], -np.log10(max(r[pval_name], 1e-300))),
                        **gene_annotation_kwargs())
    ax.set_xlabel(r'log$_2$(Fold Change)')
    ax.set_ylabel(r'$-$log$_{10}$(adjusted P)')


# ============================================================
# 20.3 plot_dotplot — 点图（ov.pl.dotplot → mpl scatter 矩阵）
# ============================================================

def plot_dotplot(adata, var_names, groupby='celltype', ax=None, figsize=None,
                 save=None, standard_scale='var', show=None, **kwargs):
    """Dotplot：ov.pl.dotplot 优先，mpl scatter 矩阵兜底（含 size legend）。"""
    if _check_ov():
        try:
            import omicverse as ov
            ov.pl.dotplot(adata, var_names=var_names, groupby=groupby,
                          standard_scale=standard_scale, dendrogram=False, show=False)
            fig_ov = plt.gcf()
            n_genes = len(var_names) if not isinstance(var_names, dict) else sum(len(v) for v in var_names.values())
            n_groups = adata.obs[groupby].nunique()
            fig_ov.set_size_inches(*recipe_figsize('dotplot', n_x=n_groups, n_y=n_genes))
            ax = fig_ov.axes[0] if fig_ov.axes else ax
            if save:
                save_panel(fig_ov, save, show=show)
            return fig_ov, ax
        except Exception as e:
            print(f"[smart_plot] ov.pl.dotplot failed ({e}), mpl fallback")
    if ax is None:
        n_groups = adata.obs[groupby].nunique()
        fig, ax = plt.subplots(figsize=figsize or (min(n_groups*0.35+0.8, 3.5), len(var_names)*0.3+0.8))
    else:
        fig = ax.figure
    _dotplot_mpl(adata, var_names, groupby, ax, standard_scale)
    polish_axes(ax, subtle_grid=False)
    if save:
        save_panel(fig, save, show=show)
    return fig, ax

def _dotplot_mpl(adata, var_names, groupby, ax, standard_scale):
    """mpl dotplot: scatter matrix (size=%expr, color=mean expr)."""
    groups = adata.obs[groupby].astype('category').cat.categories
    fracs = []  # fraction expressed
    means = []  # mean expression (scaled)
    for g in var_names:
        if g not in adata.var_names:
            fracs.append([0]*len(groups)); means.append([0]*len(groups)); continue
        expr = adata[:, g].X
        if hasattr(expr, 'toarray'):
            expr = expr.toarray()
        expr = np.asarray(expr).ravel()
        f_row = []; m_row = []
        for grp in groups:
            mask = (adata.obs[groupby] == grp).values
            vals = expr[mask]
            f_row.append((vals > 0).mean() if len(vals) > 0 else 0)
            m_row.append(vals.mean() if len(vals) > 0 else 0)
        fracs.append(f_row); means.append(m_row)
    fracs = np.array(fracs); means = np.array(means)
    # scale means per gene (row) if standard_scale='var'
    if standard_scale == 'var' and means.max() > 0:
        row_max = means.max(axis=1, keepdims=True)
        row_max[row_max == 0] = 1
        means = means / row_max
    # plot
    for i, g in enumerate(var_names):
        for j, grp in enumerate(groups):
            size = 20 + fracs[i, j] * 180  # s ∈ [20, 200]
            ax.scatter(j, i, s=size, c=means[i, j], cmap=EXPR_CMAP,
                       vmin=0, vmax=1, edgecolor=NEAR_BLACK, linewidth=0.3, zorder=3)
    ax.set_xticks(range(len(groups)))
    ax.set_xticklabels(groups, fontsize=7, rotation=45 if len(groups) > 12 else 0,
                       ha='right' if len(groups) > 12 else 'center')
    ax.set_yticks(range(len(var_names)))
    ax.set_yticklabels(var_names, fontsize=8, fontstyle='italic')
    ax.invert_yaxis()
    # colorbar for expression
    sm = plt.cm.ScalarMappable(cmap=EXPR_CMAP, norm=plt.Normalize(0, 1))
    sm.set_array([])
    add_elegant_colorbar(sm, ax, label='Mean expression (scaled)')
    # size legend
    for frac_ref, label in [(0.25, '25%'), (0.5, '50%'), (1.0, '100%')]:
        ax.scatter([], [], s=20+frac_ref*180, c='lightgray', edgecolor=NEAR_BLACK,
                   linewidth=0.3, label=label)
    ax.legend(title='% expressed', loc='upper left', bbox_to_anchor=(1.15, 1.0),
              frameon=False, fontsize=6, title_fontsize=7, labelspacing=1.2)


# ============================================================
# 20.4 plot_violin — 小提琴（ov.pl.violin → mpl violinplot）
# ============================================================

def plot_violin(adata, keys, groupby='celltype', ax=None, figsize=None,
                save=None, show=None, show_stats=False, **kwargs):
    """Violin：ov.pl.violin 优先（交替背景），mpl 兜底。

    Args:
        show_stats: 是否显示 pairwise wilcox p 值标注（bracket）。
                    默认 False——CNS 正文 violin 一般不放 bracket，p 值写图注。
                    组数 >4 时强制 False（pairwise 太多会挡图）。
    """
    groups = adata.obs[groupby].astype('category').cat.categories
    n_groups = len(groups)
    # 组数 >4 时 pairwise 太多（C(5,2)=10+），bracket 必然挡图 → 强制关闭
    if n_groups > 4:
        show_stats = False
    n_genes = len(keys) if isinstance(keys, list) else 1
    if isinstance(keys, str):
        keys = [keys]
    if ax is None:
        fig, axes = plt.subplots(n_genes, 1, figsize=figsize or
                                 (min(len(groups)*0.45+0.8, 4.5), n_genes*1.6), sharex=True)
        if n_genes == 1:
            axes = [axes]
    else:
        fig = ax.figure
        axes = [ax]
        keys = keys[:1]  # 单 ax 只画第一个
    if _check_ov() and len(axes) == 1:
        try:
            import omicverse as ov
            ov_kwargs = dict(
                stripplot=True, jitter=True, size=1, jitter_alpha=0.4,
                violin_alpha=0.8, alternating_background=True,
                spine_color='#b4aea9', grid_lines=False)
            if show_stats:
                ov_kwargs['statistical_tests'] = 'wilcox'
            ov.pl.violin(adata, keys=keys, groupby=groupby, ax=axes[0], show=False,
                         figsize=(min(len(groups)*0.45+0.8, 4.5), 2.2),
                         **ov_kwargs, **kwargs)
            fig_ov = plt.gcf()
            if save:
                save_panel(fig_ov, save, show=show)
            return fig_ov, axes[0]
        except Exception as e:
            print(f"[smart_plot] ov.pl.violin failed ({e}), mpl fallback")
    for row, g in enumerate(keys):
        _violin_mpl(adata, g, groupby, axes[row])
    fig = axes[0].figure
    polish_axes(axes[-1])
    if save:
        save_panel(fig, save, show=show)
    return fig, axes if n_genes > 1 else axes[0]

def _violin_mpl(adata, gene, groupby, ax):
    """mpl violin: alternating bg + small strip + warm grey spine."""
    groups = adata.obs[groupby].astype('category').cat.categories
    data_per = []
    if gene in adata.var_names:
        expr = adata[:, gene].X
        if hasattr(expr, 'toarray'):
            expr = expr.toarray()
        expr = np.asarray(expr).ravel()
    else:
        expr = np.zeros(adata.n_obs)
    for grp in groups:
        mask = (adata.obs[groupby] == grp).values
        data_per.append(expr[mask])
    # alternating background
    for i, grp in enumerate(groups):
        color = MORLANDI[i % len(MORLANDI)]
        ax.axvspan(i-0.5, i+0.5, color=_lighten_color(color, 0.85), alpha=0.5, zorder=0)
    parts = ax.violinplot(data_per, positions=range(len(groups)),
                          showmedians=False, showextrema=False)
    for i, pc in enumerate(parts['bodies']):
        c = MORLANDI[i % len(MORLANDI)]
        pc.set_facecolor(c); pc.set_alpha(0.8)
        pc.set_edgecolor(c); pc.set_linewidth(1)
    for i, d in enumerate(data_per):  # strip
        jit = np.random.uniform(-0.15, 0.15, len(d))
        ax.scatter(np.full(len(d), i)+jit, d, s=1, alpha=0.4,
                   color=MORLANDI[i % len(MORLANDI)], edgecolor='none',
                   rasterized=True, zorder=3)
    for sp in ax.spines.values():
        sp.set_color('#b4aea9'); sp.set_linewidth(0.8)
    ax.set_ylabel('Expression', fontsize=9, labelpad=8)
    ax.set_title(gene, fontstyle='italic', fontsize=11, pad=8)
    ax.set_xticks(range(len(groups)))
    ax.set_xticklabels(groups, fontsize=7,
                       rotation=45 if len(groups) > 8 else 0)


# ============================================================
# 20.5 plot_heatmap — 热图（ov 无独立函数，直接 mpl imshow）
# ============================================================

def plot_heatmap(adata, var_names, groupby='celltype', ax=None, figsize=None,
                 save=None, z_score=0, cmap=None, show=None, **kwargs):
    """Heatmap：mpl imshow（正方形单元格，Z-score per row）。"""
    if ax is None:
        n_groups = adata.obs[groupby].nunique()
        n_genes = len(var_names) if not isinstance(var_names, dict) else sum(len(v) for v in var_names.values())
        cell = 0.25  # 正方形单元格边长
        fig, ax = plt.subplots(figsize=figsize or
                               (n_groups * cell + 1.0, n_genes * cell + 0.8))
    else:
        fig = ax.figure
    import pandas as pd
    # aggregate mean per group
    expr = adata[:, var_names].to_df()
    expr[groupby] = adata.obs[groupby].values
    mean_expr = expr.groupby(groupby).mean().T  # rows=genes, cols=groups
    # Z-score per row
    mean_z = mean_expr.apply(lambda r: (r - r.mean()) / (r.std() + 1e-10), axis=1)
    im = ax.imshow(mean_z.values, aspect='equal', cmap=cmap or EXPR_CMAP,
                   vmin=-2, vmax=2, interpolation='nearest')
    ax.set_xticks(range(len(mean_z.columns)))
    ax.set_xticklabels(mean_z.columns, fontsize=7,
                       rotation=45, ha='center', va='top', rotation_mode='anchor')
    ax.tick_params(axis='x', pad=10)  # x 轴标签下移
    ax.set_yticks(range(len(mean_z.index)))
    ax.set_yticklabels(mean_z.index, fontsize=8, fontstyle='italic')
    # white separators
    ax.set_xticks(np.arange(-0.5, len(mean_z.columns), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(mean_z.index), 1), minor=True)
    ax.grid(which='minor', color='white', linewidth=0.5)
    ax.tick_params(which='minor', length=0)
    add_elegant_colorbar(im, ax, label='Scaled expression (z-score)')
    # 热图不需要坐标轴线
    for sp in ax.spines.values():
        sp.set_visible(False)
    if save:
        save_panel(fig, save, show=show)
    return fig, ax


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

def plot_bar(props, ax=None, figsize=None, save=None, groupby=None, celltype_col='celltype',
             show=None, **kwargs):
    """Bar (proportions)：ov.pl.barplot 优先，mpl 兜底（带 95% CI error bars + per-sample dots）。

    可直接传 adata（AnnData）+ groupby 自动算比例，或传已算好的 props DataFrame。
    """
    import pandas as pd
    if _check_ov() and isinstance(props, pd.DataFrame):
        try:
            import omicverse as ov
            # ov.pl.barplot 需要 data 参数为 DataFrame
            # 如果 props 是宽格式（index=样本, columns=celltype），转成长格式
            if groupby is None:
                # 宽格式 props：index=样本 columns=celltype → 转长格式
                long_df = props.reset_index()
                id_col = long_df.columns[0]  # 第一列是样本名
                long_df = long_df.melt(id_vars=id_col, var_name=celltype_col,
                                       value_name='proportion')
                ov.pl.barplot(data=long_df, x=celltype_col, y='proportion',
                              dots=True, figsize=figsize or (3.0, 2.5))
            else:
                ov.pl.barplot(data=props, x=groupby, y=celltype_col,
                              dots=True, figsize=figsize or (3.0, 2.5))
            fig = plt.gcf()
            fig.set_size_inches(*(figsize or (3.0, 2.5)))
            if save:
                save_panel(fig, save, show=show)
            return fig, fig.axes[0] if fig.axes else None
        except Exception as e:
            print(f"[smart_plot] ov.pl.barplot failed ({e}), mpl fallback")
    # 如传 AnnData + groupby，自动算比例
    if hasattr(props, 'obs') and groupby is not None:
        adata = props
        props = (adata.obs.groupby(['sample' if 'sample' in adata.obs.columns else groupby,
                                     celltype_col])
                 .size().unstack(fill_value=0)
                 .apply(lambda r: r / r.sum(), axis=1))
    elif hasattr(props, 'obs'):
        raise ValueError("plot_bar: AnnData 需同时传 groupby 参数")
    n = len(props.columns)
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize or recipe_figsize('bar', n_x=n))
    else:
        fig = ax.figure
    for i, ct in enumerate(props.columns):
        mean, sem = props[ct].mean(), props[ct].sem()
        ax.bar(i, mean, yerr=1.96*sem, capsize=3, width=0.6,
               color=MORLANDI[i % len(MORLANDI)], edgecolor='white', linewidth=0.5,
               label=ct, error_kw=dict(lw=1, ecolor=NEAR_BLACK))
        ax.scatter(np.full(len(props), i) + np.random.uniform(-0.05, 0.05, len(props)),
                   props[ct], s=15, alpha=0.7, color=NEAR_BLACK,
                   edgecolor='none', zorder=3)
    ax.set_xticks(range(len(props.columns)))
    ax.set_xticklabels(props.columns, rotation=30, ha='right')
    ax.set_ylabel('Proportion')
    ax.set_ylim(0, ax.get_ylim()[1])
    ax.legend(bbox_to_anchor=(1.02, 0.5), loc='center left', frameon=False)
    polish_axes(ax)
    if save:
        save_panel(fig, save, show=show)
    return fig, ax


# ============================================================
# 20.8 plot_enrichment — GO/KEGG 富集条形（ov 无，直接 mpl）
# ============================================================

def plot_enrichment(enr, ax=None, figsize=None, save=None, top_n=15,
                    term_col='Term', fdr_col='FDR', count_col='Gene_count', show=None, **kwargs):
    """Enrichment barh：-log10(FDR) 降序，条右标 gene count，通路名截断。"""
    terms = enr.nsmallest(top_n, fdr_col)
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize or (3.0, 0.22*len(terms)+0.6))
    else:
        fig = ax.figure
    y_pos = range(len(terms))
    bars = ax.barh(y_pos, -np.log10(terms[fdr_col]), color='#BF616A', height=0.6,
                   edgecolor='none')
    ax.set_yticks(y_pos)
    ax.set_yticklabels([str(t)[:40] for t in terms[term_col]], fontsize=7)
    ax.set_xlabel(r'$-$log$_{10}$(FDR)', labelpad=10)
    ax.invert_yaxis()
    for b, n in zip(bars, terms[count_col]):
        ax.text(b.get_width()+0.1, b.get_y()+b.get_height()/2, str(n),
                va='center', fontsize=6, color=GREY)
    polish_axes(ax, subtle_grid=False)
    if save:
        save_panel(fig, save, show=show)
    return fig, ax


# ============================================================
# 20.9 plot_lr_bubble — L-R Bubble（ov 无，直接 mpl）
# ============================================================

def plot_lr_bubble(pair_labels, pathway_labels, sizes, mean_expr,
                   x_idx=None, y_idx=None, ax=None, figsize=None, save=None, show=None, **kwargs):
    """L-R Bubble：ov.pl.scatterplot 优先（size=-log10(p), color=mean expr），mpl 兜底。"""
    import pandas as pd
    n_pairs = len(pair_labels); n_path = len(pathway_labels)
    if _check_ov():
        try:
            import omicverse as ov
            # 矩阵转 tidy DataFrame
            sizes_arr = np.asarray(sizes).reshape(n_path, n_pairs).T  # (n_pairs, n_path)
            expr_arr = np.asarray(mean_expr).reshape(n_path, n_pairs).T
            rows = []
            for pi in range(n_pairs):
                for ti in range(n_path):
                    rows.append({'x': pi, 'y': ti, 'size': sizes_arr[pi, ti],
                                 'expr': expr_arr[pi, ti]})
            df_bubble = pd.DataFrame(rows)
            ov.pl.scatterplot(data=df_bubble, x='x', y='y', size='size', hue='expr',
                              cmap='YlOrRd', alpha=0.85,
                              figsize=figsize or (min(n_pairs*0.8+1, 3.5), min(n_path*0.6+1, 3.0)))
            fig = plt.gcf()
            ax_ov = fig.axes[0] if fig.axes else ax
            if ax_ov:
                # x/y 轴设为 pair/pathway 名，去掉数值标签
                ax_ov.set_xticks(range(n_pairs))
                ax_ov.set_xticklabels(pair_labels, rotation=45, ha='right', fontsize=7)
                ax_ov.set_yticks(range(n_path))
                ax_ov.set_yticklabels(pathway_labels, fontsize=7)
                ax_ov.set_xlabel('')
                ax_ov.set_ylabel('')
                # dot size legend（用虚拟点）
                s_min, s_max = float(sizes_arr.min()), float(sizes_arr.max())
                for frac, label in [(0.25, f'{s_min+(s_max-s_min)*0.25:.0f}'),
                                    (0.5, f'{s_min+(s_max-s_min)*0.5:.0f}'),
                                    (1.0, f'{s_max:.0f}')]:
                    ax_ov.scatter([], [], s=frac * 200, c='lightgray', edgecolor=NEAR_BLACK,
                                  linewidth=0.3, label=label)
                ax_ov.legend(title='-log10(p)', loc='upper left', bbox_to_anchor=(1.15, 1.0),
                             frameon=False, fontsize=6, title_fontsize=7, labelspacing=1.2,
                             scatterpoints=1)
            if save:
                save_panel(fig, save, show=show)
            return fig, ax_ov
        except Exception as e:
            print(f"[smart_plot] ov.pl.scatterplot failed ({e}), mpl fallback")
    n_pairs = len(pair_labels); n_path = len(pathway_labels)
    if x_idx is None:
        x_idx = np.arange(n_pairs)
    if y_idx is None:
        y_idx = np.arange(n_path)
    # broadcast to full grid if needed
    if np.asarray(sizes).size == n_pairs * n_path:
        # sizes shape (n_path, n_pairs) → 转置为 (n_pairs, n_path)
        sizes_mat = np.asarray(sizes).reshape(n_path, n_pairs).T
        expr_mat = np.asarray(mean_expr).reshape(n_path, n_pairs).T
        # 生成 n_pairs × n_path 的坐标网格（展平后共 n_pairs*n_path 个点）
        xs, ys = np.meshgrid(x_idx, y_idx, indexing='ij')
        x_idx_plot = xs.ravel(); y_idx_plot = ys.ravel()
        sizes_plot = sizes_mat.ravel(); expr_plot = expr_mat.ravel()
    else:
        x_idx_plot = x_idx; y_idx_plot = y_idx; sizes_plot = sizes; expr_plot = mean_expr
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize or
                               (min(n_pairs*0.45+1.0, 3.5), min(n_path*0.3+1.0, 3.0)))
    else:
        fig = ax.figure
    scatter = ax.scatter(x_idx_plot, y_idx_plot, s=sizes_plot, c=expr_plot,
                         cmap=EXPR_CMAP, edgecolor=NEAR_BLACK, linewidth=0.3,
                         alpha=0.85, vmin=0)
    ax.set_xticks(np.arange(n_pairs))
    ax.set_xticklabels(pair_labels, rotation=45, ha='right', fontsize=6)
    ax.set_yticks(np.arange(n_path))
    ax.set_yticklabels(pathway_labels, fontsize=7)
    add_elegant_colorbar(scatter, ax, label='Mean expression')
    polish_axes(ax, subtle_grid=False)
    if save:
        save_panel(fig, save, show=show)
    return fig, ax


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

def plot_paga(adata, ax=None, figsize=None, save=None, threshold=0.05,
              color=None, show=None, **kwargs):
    """PAGA：ov.pl.trajectory_graph 优先，sc.pl.paga/mpl+networkx 兜底。"""
    if _check_ov():
        try:
            import omicverse as ov
            ov.pl.trajectory_graph(adata, method='paga',
                                   cluster_key='leiden' if 'leiden' in adata.obs else None,
                                   basis='X_umap' if 'X_umap' in adata.obsm else None,
                                   figsize=figsize or (2.5, 2.2), show=False)
            fig = plt.gcf()
            if save:
                save_panel(fig, save, show=show)
            return fig, fig.axes[0] if fig.axes else None
        except Exception as e:
            print(f"[smart_plot] ov.pl.trajectory_graph failed ({e}), fallback")
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize or recipe_figsize('paga'))
    else:
        fig = ax.figure
    routed = False
    try:
        import scanpy as sc
        color_arg = color or 'leiden'
        sc.pl.paga(adata, colors=color_arg, ax=ax, show=False,
                   threshold=threshold, **kwargs)
        routed = True
    except Exception as e:
        print(f"[smart_plot] sc.pl.paga failed ({e}), mpl+networkx fallback")
    if not routed:
        _paga_mpl(adata, ax, threshold)
    polish_axes(ax)
    ax.set_aspect('equal')   # PAGA 用 embedding 坐标定位节点，必须正方形
    if save:
        save_panel(fig, save, show=show)
    return fig, ax


def _paga_mpl(adata, ax, threshold):
    """mpl PAGA: networkx graph, node pos from UMAP means, edge width ∝ weight."""
    import networkx as nx
    if 'paga' not in adata.uns:
        raise ValueError("Run sc.tl.paga(adata) first")
    adj = adata.uns['paga']['connectivities'].toarray()
    groups = list(adata.obs[adata.uns['paga']['groups']].astype('category').cat.categories)
    G = nx.Graph()
    for i, g in enumerate(groups):
        G.add_node(i, label=g)
    for i in range(len(groups)):
        for j in range(i+1, len(groups)):
            w = adj[i, j]
            if w > threshold:
                G.add_edge(i, j, weight=w)
    # node positions from UMAP means
    basis = 'X_umap' if 'X_umap' in adata.obsm else list(adata.obsm.keys())[0]
    coords = adata.obsm[basis]
    grp_col = adata.uns['paga']['groups']
    pos = {}
    for i, g in enumerate(groups):
        mask = (adata.obs[grp_col] == g).values
        pos[i] = coords[mask].mean(axis=0)
    # draw
    for n in G.nodes:
        x, y = pos[n]
        ax.scatter(x, y, s=800, color=MORLANDI[n % len(MORLANDI)],
                   edgecolor='white', linewidth=1.5, zorder=5)
        ax.text(x, y, groups[n], ha='center', va='center', fontsize=7,
                color='white', zorder=6)
    maxw = max((d['weight'] for _, _, d in G.edges(data=True)), default=1)
    for u, v, d in G.edges(data=True):
        w = d['weight']
        x1, y1 = pos[u]; x2, y2 = pos[v]
        ax.plot([x1, x2], [y1, y2], color=GREY, alpha=0.6,
                lw=0.5 + 5*w/maxw, solid_capstyle='round', zorder=2)


# ============================================================
# 20.12 plot_ccc — 统一细胞通讯可视化（chord/network，对齐 ov.pl.ccc_network_plot 的 plot_type 路由）
# ============================================================

def plot_ccc(weight_matrix, layout='chord', labels=None, ax=None, figsize=None,
             save=None, show=None, **kwargs):
    """统一细胞通讯/互作可视化——一个入口，layout 路由到不同布局。

    对齐 omicverse ``ov.pl.ccc_network_plot`` 的 ``plot_type`` 设计哲学
    （一个函数支持 chord/circle/diff_network 等十几种布局）。

    Args:
        weight_matrix: 2D array/DataFrame，方阵 N×N，值=互作强度（0=无）。
        layout: ``'chord'`` → 环形弦图（≤8 类型，展示"谁给谁收信号"）
                ``'network'`` → 力导向网络图（复杂拓扑，节点大小=加权度）
        labels: 节点标签（None=用 matrix index/行列名）
        ax/figsize/save/show: 标准
        **kwargs: 透传给对应布局的函数
    Returns: (fig, ax)
    """
    if layout == 'chord':
        return plot_chord(weight_matrix, ax=ax, figsize=figsize,
                          save=save, show=show, **kwargs)
    elif layout == 'network':
        return plot_ccc_network(weight_matrix, labels=labels, ax=ax,
                                figsize=figsize, save=save, show=show, **kwargs)
    else:
        raise ValueError(
            f"layout='{layout}' unsupported. Use 'chord' or 'network'. "
            f"(Maps to ov.pl.ccc_network_plot plot_type='chord'/'diff_network')")


# ============================================================
# 20.12a plot_chord — Chord/CCC 细胞通讯弦图（plot_ccc 的 chord 布局实现）
# ============================================================

def plot_chord(weight_matrix, ax=None, figsize=None, save=None, show=None, **kwargs):
    """Chord/CCC：ov.pl.CellChatViz 优先，mpl+networkx 兜底。"""
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize or recipe_figsize('chord'))
    else:
        fig = ax.figure
    if _check_ov():
        try:
            import omicverse as ov
            viz = ov.pl.CellChatViz(weight_matrix, palette=None)
            # 下游签名随 ov 版本而异——尝试常见方法
            for method in ['netVisual_chord_cell', 'netVisual_chord']:
                if hasattr(viz, method):
                    getattr(viz, method)(ax=ax, show=False, **kwargs)
                    routed = True
                    break
            else:
                raise AttributeError("No chord method found in CellChatViz")
            if save:
                save_panel(fig, save, show=show)
            return fig, ax
        except Exception as e:
            print(f"[smart_plot] ov chord failed ({e}), mpl+networkx fallback")
    _chord_mpl(weight_matrix, ax)
    ax.set_aspect('equal')
    ax.axis('off')
    if save:
        save_panel(fig, save, show=show)
    return fig, ax


def _chord_mpl(weight_matrix, ax):
    """mpl chord: circular layout, source-colored arcs."""
    import networkx as nx
    if hasattr(weight_matrix, 'values'):
        wm = weight_matrix.values
        labels = list(weight_matrix.index)
    else:
        wm = np.asarray(weight_matrix)
        labels = [f'C{i}' for i in range(len(wm))]
    n = min(len(labels), 8)  # ≤8 cell types
    wm = wm[:n, :n]; labels = labels[:n]
    G = nx.DiGraph()
    for i in range(n):
        G.add_node(i)
    for i in range(n):
        for j in range(n):
            if i != j and wm[i, j] > 0:
                G.add_edge(i, j, weight=wm[i, j])
    pos = nx.circular_layout(G)
    palette = {i: MORLANDI[i % len(MORLANDI)] for i in range(n)}
    for i in range(n):
        x, y = pos[i]
        ax.scatter(x, y, s=800, color=palette[i], edgecolor='white',
                   linewidth=1.5, zorder=5)
        ax.text(x, y, labels[i][:8], ha='center', va='center', fontsize=7,
                color='white', zorder=6)
    maxw = max((d['weight'] for _, _, d in G.edges(data=True)), default=1)
    for u, v, d in G.edges(data=True):
        w = d['weight']
        x1, y1 = pos[u]; x2, y2 = pos[v]
        ax.plot([x1, x2], [y1, y2], color=palette[u], alpha=0.5,
                lw=0.5 + 3*w/maxw, solid_capstyle='round', zorder=2)


# ============================================================
# 20.13 plot_pseudotime — 基因沿轨迹表达（直接 mpl LOESS）
# ============================================================

def plot_pseudotime(adata, genes, pseudotime_col='pseudotime', ax=None,
                    figsize=None, save=None, frac=0.3, show=None, **kwargs):
    """Pseudotime：mpl LOESS 平滑 + 95% CI 带。"""
    if isinstance(genes, str):
        genes = [genes]
    if ax is None:
        fig, axes = plt.subplots(len(genes), 1, figsize=figsize or
                                 (3.5, 1.8*len(genes)), sharex=True)
        if len(genes) == 1:
            axes = [axes]
    else:
        fig = ax.figure; axes = [ax]; genes = genes[:1]
    # LOESS function
    try:
        import statsmodels.api as sm
        def _loess(x, y, frac=0.3):
            res = sm.nonparametric.lowess(y, x, frac=frac, it=1, return_sorted=True)
            return res[:, 0], res[:, 1]
    except ImportError:
        def _loess(x, y, frac=0.3):
            order = np.argsort(x)
            xs = x[order]
            yhat = np.polyval(np.polyfit(x, y, 3), xs)
            return xs, yhat
    pt = adata.obs[pseudotime_col].values
    for row, g in enumerate(genes):
        a = axes[row]
        if g in adata.var_names:
            expr = adata[:, g].X
            if hasattr(expr, 'toarray'):
                expr = expr.toarray()
            y = np.asarray(expr).ravel()
        else:
            y = np.zeros(adata.n_obs)
        a.scatter(pt, y, s=3, alpha=0.3, color=GREY, edgecolor='none', rasterized=True)
        xs, yh = _loess(pt, y, frac)
        resid = y[np.argsort(pt)] - yh
        se = np.sqrt(np.convolve(resid**2, np.ones(50)/50, mode='same'))
        a.plot(xs, yh, lw=1.2, color='#BF616A')
        a.fill_between(xs, yh - 1.96*se, yh + 1.96*se, alpha=0.15, color='#BF616A', lw=0)
        a.set_ylabel(g, fontstyle='italic', fontsize=8, labelpad=6)
        polish_axes(a)
    axes[-1].set_xlabel('Pseudotime')
    if save:
        save_panel(fig, save, show=show)
    return fig, axes if len(genes) > 1 else axes[0]


# ============================================================
# 20.14 plot_cellproportion — 细胞比例堆叠柱（ov 优先，mpl 兜底）
# ============================================================

def plot_cellproportion(adata, groupby='condition', celltype_col='celltype',
                        ax=None, figsize=None, save=None, show=None, **kwargs):
    """Cell proportion stacked bar：ov.pl.cellproportion 优先，mpl 兜底。"""
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize or
                               recipe_figsize('bar', n_x=adata.obs[groupby].nunique()))
    else:
        fig = ax.figure
    if _check_ov():
        try:
            import omicverse as ov
            # ov.pl.cellproportion 的 legend 默认 False —— 堆叠柱必须显式开图例
            kwargs.setdefault('legend', True)
            ov.pl.cellproportion(adata, celltype_clusters=celltype_col,
                                 groupby=groupby, figsize=(3.0, 2.5), **kwargs)
            fig_ov = plt.gcf()
            if save:
                save_panel(fig_ov, save, show=show)
            return fig_ov, ax
        except Exception as e:
            print(f"[smart_plot] ov.pl.cellproportion failed ({e}), mpl fallback")
    _cellproportion_mpl(adata, groupby, celltype_col, ax)
    polish_axes(ax)
    if save:
        save_panel(fig, save, show=show)
    return fig, ax


def _cellproportion_mpl(adata, groupby, celltype_col, ax):
    """mpl stacked proportion bar."""
    import pandas as pd
    props = (adata.obs.groupby(groupby)[celltype_col]
             .value_counts(normalize=True).unstack(fill_value=0))
    cats = list(props.columns)
    palette = {ct: MORLANDI[i % len(MORLANDI)] for i, ct in enumerate(cats)}
    bottom = np.zeros(len(props))
    x = range(len(props))
    for ct in cats:
        ax.bar(x, props[ct], bottom=bottom, width=0.6,
               color=palette[ct], edgecolor='white', linewidth=0.5, label=ct)
        bottom += props[ct].values
    ax.set_xticks(x)
    ax.set_xticklabels(props.index, fontsize=8)
    ax.set_ylabel('Cell proportion')
    ax.set_ylim(0, 1)
    ax.legend(bbox_to_anchor=(1.02, 0.5), loc='center left', frameon=False, fontsize=6)


# ============================================================
# 20.15 plot_de_scatter — DE 多时点/多条件分组散点（ov 无，直接 mpl）
# ============================================================

def plot_de_scatter(de_dict, ax=None, figsize=None, save=None,
                    pval_name='padj', fc_name='log2FC', sig_pval=0.05, sig_fc=1.0,
                    annotate_top=3, show=None, **kwargs):
    """DE 分组散点（多时点/多条件）：x=组别, y=logFC, 每点=一个基因。

    火山图在多时点/多组比较时不可读（标注重叠、灰点密集）；分组散点直接可比。
    ov 无对应函数，直接 mpl。

    Args:
        de_dict: {组别名: DataFrame}，每个 DataFrame 含 gene + pval_name + fc_name
        ax/figsize/save: 标准
        sig_pval/sig_fc: 显著性阈值
        annotate_top: 每组标注 top N 基因
    Returns: (fig, ax)
    """
    import pandas as pd
    if _check_ov():
        try:
            import omicverse as ov
            rows = []
            for gname, de in de_dict.items():
                for _, r in de.iterrows():
                    rows.append({'group': gname, 'logFC': r[fc_name],
                                 'padj': r[pval_name]})
            df_de = pd.DataFrame(rows)
            n_groups = len(de_dict)
            group_names = list(de_dict.keys())
            group_map = {g: i for i, g in enumerate(group_names)}
            df_de['x_num'] = df_de['group'].map(group_map)
            ov.pl.scatterplot(data=df_de, x='x_num', y='logFC', hue='padj',
                              cmap='coolwarm_r', alpha=0.7, s=15,
                              figsize=figsize or (min(n_groups * 0.8 + 0.5, 4.0), 2.5))
            fig = plt.gcf()
            ax_ov = fig.axes[0] if fig.axes else None
            if ax_ov:
                ax_ov.set_xticks(range(n_groups))
                ax_ov.set_xticklabels(group_names, fontsize=7)
            if save:
                save_panel(fig, save, show=show)
            return fig, ax_ov
        except Exception as e:
            print(f"[smart_plot] ov.pl.scatterplot failed ({e}), mpl fallback")
    comparisons = list(de_dict.keys())
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize or recipe_figsize('bar', n_x=len(comparisons)))
    else:
        fig = ax.figure
    UP = '#e25d5d'; DOWN = '#7388c1'; NS = '#d7d7d7'
    for i, comp in enumerate(comparisons):
        de = de_dict[comp]
        sig = (de[pval_name] < sig_pval) & (de[fc_name].abs() > sig_fc)
        ns = ~sig
        # ns: 灰小点
        ax.scatter(np.full(ns.sum(), i) + np.random.uniform(-0.15, 0.15, ns.sum()),
                   de.loc[ns, fc_name], s=8, alpha=0.3, color=NS,
                   edgecolor='none', rasterized=True, zorder=2)
        # sig: 彩色大点（up=红, down=蓝）
        colors = np.where(de.loc[sig, fc_name] > 0, UP, DOWN)
        ax.scatter(np.full(sig.sum(), i) + np.random.uniform(-0.15, 0.15, sig.sum()),
                   de.loc[sig, fc_name], s=20, alpha=0.7, c=colors,
                   edgecolor='white', linewidth=0.3, zorder=3)
        # top N 标注
        top = de.loc[sig].reindex(
            de.loc[sig, fc_name].abs().sort_values(ascending=False).index[:annotate_top])
        for _, r in top.iterrows():
            gene = r['gene'] if 'gene' in r else r.name
            ax.annotate(gene, xy=(i, r[fc_name]),
                        xytext=(i+0.15, r[fc_name]+0.2),
                        fontsize=6, fontstyle='italic', color=NEAR_BLACK,
                        arrowprops=dict(arrowstyle='-', lw=0.4, color=GREY))
    ax.axhline(0, color=GREY, lw=0.5)
    for v in (sig_fc, -sig_fc):
        ax.axhline(v, color=GREY, lw=0.4, ls='--', alpha=0.3)
    ax.set_xticks(range(len(comparisons)))
    ax.set_xticklabels(comparisons, fontsize=8, rotation=20, ha='right')
    ax.set_ylabel(r'log$_2$(Fold Change)', fontsize=10, labelpad=10)
    polish_axes(ax)
    if save:
        save_panel(fig, save, show=show)
    return fig, ax


# ============================================================
# 20.16 plot_spatial_ccc — 空间细胞通讯共表达面板（ov 无，直接 mpl）
# ============================================================

def plot_spatial_ccc(adata_sp, ligand, receptor, ax=None, figsize=None, save=None,
                     niche_col=None, show=None, **kwargs):
    """空间 CCC：ov.pl.spatial_value 优先（双面板），mpl 兜底。"""
    if _check_ov() and 'spatial' in getattr(adata_sp, 'uns', {}):
        try:
            import omicverse as ov
            lib_id = list(adata_sp.uns['spatial'].keys())[0]
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize or (5.0, 2.5))
            ov.pl.spatial_value(adata_sp, color=ligand, library_id=lib_id, ax=ax1)
            ov.pl.spatial_value(adata_sp, color=receptor, library_id=lib_id, ax=ax2)
            if save:
                save_panel(fig, save, show=show)
            return fig, (ax1, ax2)
        except Exception as e:
            print(f"[smart_plot] ov.pl.spatial_value failed ({e}), mpl fallback")
    if 'spatial' not in adata_sp.obsm and 'X_spatial' not in adata_sp.obsm:
        raise ValueError("adata_sp needs obsm['spatial'] or obsm['X_spatial']")
    coords = adata_sp.obsm.get('spatial', adata_sp.obsm.get('X_spatial'))
    if ax is None:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize or (5.0, 2.5),
                                       gridspec_kw={'wspace': 0.35})
    else:
        raise ValueError("plot_spatial_ccc creates its own 2-panel layout; pass ax=None")
    # shared vmax
    vals = []
    for gene in [ligand, receptor]:
        if gene in adata_sp.var_names:
            v = adata_sp[:, gene].X
            if hasattr(v, 'toarray'):
                v = v.toarray()
            vals.append(np.asarray(v).ravel())
    all_v = np.concatenate(vals) if vals else np.array([0])
    vmax = np.percentile(all_v[all_v > 0] if (all_v > 0).any() else all_v, 99)
    for ax_i, gene, title in [(ax1, ligand, ligand), (ax2, receptor, receptor)]:
        if gene in adata_sp.var_names:
            v = adata_sp[:, gene].X
            if hasattr(v, 'toarray'):
                v = v.toarray()
            v = np.asarray(v).ravel()
        else:
            v = np.zeros(adata_sp.n_obs)
        sc = ax_i.scatter(coords[:, 0], coords[:, 1], c=v, cmap=EXPR_CMAP,
                          vmin=0, vmax=vmax, s=1.5, alpha=0.85,
                          edgecolor='none', rasterized=True)
        ax_i.set_title(title, fontstyle='italic', fontsize=10, pad=4)
        clean_umap_axes(ax_i, xlabel='', ylabel='')
        ax_i.set_aspect('equal')
    # 共享 colorbar
    fig.subplots_adjust(right=0.88)
    cbar_ax = fig.add_axes([0.90, 0.25, 0.015, 0.5])
    fig.colorbar(sc, cax=cbar_ax, label='Expression')
    add_scale_bar(ax1, length_um=200, px_per_um=1.0)
    if save:
        save_panel(fig, save, show=show)
    return fig, (ax1, ax2)


# ============================================================
# 20.17 plot_milo — Milo 差异丰度 beeswarm（ov 无，直接 mpl）
# ============================================================

def plot_milo(milo_result, ax=None, figsize=None, save=None,
              test_col='SpatialFDR', logfc_col='logFC', label_col='Population',
              sig_threshold=0.1, show=None, **kwargs):
    """Milo beeswarm：ov.pl.compare_groups 优先，mpl 兜底。"""
    if _check_ov():
        try:
            import omicverse as ov
            milo_df = milo_result.copy()
            ov.pl.compare_groups(data=milo_df, value=logfc_col, group=label_col,
                                 figsize=figsize or (3.0, 2.5))
            fig = plt.gcf()
            ax_ov = fig.axes[0] if fig.axes else None
            if save:
                save_panel(fig, save, show=show)
            return fig, ax_ov
        except Exception as e:
            print(f"[smart_plot] ov.pl.compare_groups failed ({e}), mpl fallback")
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize or (3.2, 2.8))
    else:
        fig = ax.figure
    pops = milo_result[label_col].astype('category').cat.categories
    sig = milo_result[test_col] < sig_threshold
    for i, pop in enumerate(pops):
        mask = (milo_result[label_col] == pop)
        data = milo_result.loc[mask]
        jitter = np.random.uniform(-0.2, 0.2, len(data))
        colors = np.where(data[test_col] < sig_threshold, '#BF616A', '#D8DEE9')
        ax.scatter(np.full(len(data), i) + jitter, data[logfc_col],
                   s=15, alpha=0.7, c=colors, edgecolor='none', zorder=3)
    ax.axhline(0, color=GREY, lw=0.5)
    ax.set_xticks(range(len(pops)))
    ax.set_xticklabels(pops, fontsize=7, rotation=45, ha='right')
    ax.set_ylabel('log fold change (Milo)', fontsize=10, labelpad=10)
    # legend
    ax.scatter([], [], s=15, c='#BF616A', label=f'SpatialFDR < {sig_threshold}')
    ax.scatter([], [], s=15, c='#D8DEE9', label='NS')
    ax.legend(loc='upper right', frameon=False, fontsize=7)
    polish_axes(ax)
    if save:
        save_panel(fig, save, show=show)
    return fig, ax


# ============================================================
# 20.18 plot_signaling_heatmap — CCC 信号角色热图（ov 无，直接 mpl）
# ============================================================

def plot_signaling_heatmap(comm_scores, ax=None, figsize=None, save=None,
                           mode='outgoing', show=None, **kwargs):
    """CCC signaling-role heatmap：每细胞类型的 outgoing/incoming 通讯强度。

    ov 无，直接 mpl。

    Args:
        comm_scores: DataFrame，行=cell type，列=signaling pathway，值=通讯分数
        mode: 'outgoing'（发送）或 'incoming'（接收）
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize or
                               (min(len(comm_scores.columns)*0.3+1.5, 3.5), min(len(comm_scores.index)*0.3+1.0, 3.5)))
    else:
        fig = ax.figure
    data = comm_scores.values
    # scale per column (pathway) for comparability
    col_max = data.max(axis=0, keepdims=True)
    col_max[col_max == 0] = 1
    data_z = data / col_max
    im = ax.imshow(data_z, aspect='auto', cmap=EXPR_CMAP, vmin=0, vmax=1,
                   interpolation='nearest')
    ax.set_xticks(range(len(comm_scores.columns)))
    ax.set_xticklabels(comm_scores.columns, fontsize=7, rotation=45, ha='right')
    ax.set_yticks(range(len(comm_scores.index)))
    ax.set_yticklabels(comm_scores.index, fontsize=8)
    ax.set_title(f'{mode.capitalize()} signaling strength', fontsize=10, pad=8)
    # white separators
    ax.set_xticks(np.arange(-0.5, len(comm_scores.columns), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(comm_scores.index), 1), minor=True)
    ax.grid(which='minor', color='white', linewidth=0.5)
    ax.tick_params(which='minor', length=0)
    add_elegant_colorbar(im, ax, label='Strength (scaled)')
    polish_axes(ax, subtle_grid=False)
    if save:
        save_panel(fig, save, show=show)
    return fig, ax


# ============================================================
# 20.19 plot_distance_distribution — 细胞间最近邻距离分布（空转标配）
# ============================================================

def _resolve_group_mask(adata_sp, group):
    """把 obs 列值或布尔 mask 解析为布尔数组（plot_distance_distribution 内部用）。"""
    import numpy as np
    if isinstance(group, str):
        # 优先常见类别列，找不到再全列扫描
        candidates = [c for c in ('celltype', 'cell_type', 'cluster', 'leiden', 'ctype')
                      if c in adata_sp.obs.columns]
        candidates += [c for c in adata_sp.obs.columns if c not in candidates]
        for col in candidates:
            vals = adata_sp.obs[col]
            if vals.dtype.name in ('object', 'category', 'string'):
                if (vals.astype(str) == group).any():
                    return (vals.astype(str) == group).to_numpy()
        raise ValueError(f"group '{group}' not found in any obs category column")
    mask = np.asarray(group, dtype=bool)
    if mask.ndim != 1 or mask.shape[0] != adata_sp.n_obs:
        raise ValueError(f"group mask must be 1D bool with length n_obs={adata_sp.n_obs}")
    return mask


def plot_distance_distribution(adata_sp, group_a, group_b, groupby=None,
                                spatial_key='spatial', ax=None, figsize=None,
                                save=None, n_perm=100, show=None, **kwargs):
    """两种细胞在组织中的空间距离分布——空转标配证据图。

    计算组 A 每个 spot 到组 B 最近邻的欧氏距离，画箱线图（按 groupby 分组）。
    置换检验（n_perm 次随机打乱标签）给出 p 值。

    Args:
        adata_sp: 空转 AnnData（有 obsm[spatial_key]）
        group_a/group_b: obs 列值（如 celltype=='FB'）或布尔 mask——指定两组 spot
        groupby: 按 condition 分组的列名（None=不分组合在一个箱线图）
        spatial_key: obsm 里的坐标 key
        n_perm: 置换检验次数（0=跳过）
    """
    import numpy as np
    from scipy.spatial import cKDTree
    if spatial_key not in adata_sp.obsm:
        raise ValueError(f"adata_sp.obsm has no '{spatial_key}' (run spatial_neighbors first?)")
    coords = np.asarray(adata_sp.obsm[spatial_key], dtype=float)
    if coords.ndim != 2 or coords.shape[1] < 2:
        raise ValueError(f"obsm['{spatial_key}'] must be 2D coordinates array")
    ma = _resolve_group_mask(adata_sp, group_a)
    mb = _resolve_group_mask(adata_sp, group_b)
    if ma.sum() == 0 or mb.sum() == 0:
        raise ValueError("group_a/group_b 都至少要有 1 个 spot")
    # A 每个 spot → B 最近邻的欧氏距离
    tree = cKDTree(coords[mb])
    d, _ = tree.query(coords[ma])
    if _check_ov():
        try:
            import omicverse as ov
            import pandas as pd
            if groupby is not None and groupby in adata_sp.obs.columns:
                g = adata_sp.obs[groupby].loc[ma].astype(str).values
            else:
                g = np.array(['All'] * len(d))
            df_dist = pd.DataFrame({'distance': d, 'group': g, 'hue': 'all'})
            ov.pl.boxplot(data=df_dist, hue='hue', x_value='group', y_value='distance',
                          figsize=figsize or (3.0, 2.5))
            fig = plt.gcf()
            ax_ov = fig.axes[0] if fig.axes else None
            if ax_ov:
                ax_ov.set_ylabel(f'Distance to {group_b} (µm)', fontsize=7)
            if save:
                save_panel(fig, save, show=show)
            return fig, ax_ov
        except Exception as e:
            print(f"[smart_plot] ov.pl.boxplot failed ({e}), mpl fallback")
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize or (3.0, 2.5))
    else:
        fig = ax.figure
    # 箱线图：按 groupby 分组（只含组 A 的 spot）
    if groupby is not None:
        if groupby not in adata_sp.obs.columns:
            raise ValueError(f"groupby '{groupby}' not in obs")
        g = adata_sp.obs[groupby].loc[ma].astype(str)
        cats = [c for c in g.cat.categories if (g == c).any()] if g.dtype.name == 'category' \
            else sorted(g.unique())
        data = [d[g.values == c] for c in cats]
        bp = ax.boxplot(data, tick_labels=cats, patch_artist=True,
                        widths=0.55, showfliers=False)
    else:
        bp = ax.boxplot([d], patch_artist=True, widths=0.45, showfliers=False)
        cats = None
    for patch, i in zip(bp['boxes'], range(len(bp['boxes']))):
        patch.set_facecolor(MORLANDI[i % len(MORLANDI)])
        patch.set_alpha(0.75)
        patch.set_edgecolor(NEAR_BLACK)
        patch.set_linewidth(0.8)
    for part in ('whiskers', 'caps'):
        for el in bp[part]:
            el.set_color(NEAR_BLACK)
    # 叠加 jitter 散点（每个 spot 的实际距离）
    for i, dat in enumerate(data if groupby else [d]):
        jit = np.random.uniform(-0.12, 0.12, len(dat))
        ax.scatter(np.full(len(dat), i+1)+jit, dat, s=8, alpha=0.3,
                   color=NEAR_BLACK, edgecolor='none', zorder=3, rasterized=True)
    for md in bp['medians']:
        md.set_color(NEAR_BLACK)
        md.set_linewidth(1.2)
    ax.set_ylabel(f'Distance to {group_b} (nearest, µm)', fontsize=10, labelpad=10)
    if groupby is not None:
        ax.set_xlabel(groupby, fontsize=10, labelpad=10)
    else:
        ax.set_xticks([])
    ax.set_title(f'{group_a} vs {group_b} spatial distance', fontsize=12, pad=8)
    # 置换检验：随机重抽 n_a 个 spot 作组 A，重算到 B 的最近邻均距
    n_obs = adata_sp.n_obs
    n_a = int(ma.sum())
    observed = d.mean()
    p = None
    if n_perm > 0:
        rng = np.random.default_rng(0)
        below = 0
        for _ in range(n_perm):
            pick = rng.permutation(n_obs)[:n_a]
            dp, _ = tree.query(coords[pick])
            if dp.mean() <= observed:
                below += 1
        above = n_perm - below
        p = (min(below, above) + 1) / (n_perm + 1)  # 双侧经验 p（+1 校正避免 0）
        star = 'ns' if p >= 0.05 else ('*' if p >= 0.01 else '**')
        ax.text(0.5, 1.03, f'{star} p={p:.2e} (permutation n={n_perm})',
                transform=ax.transAxes, ha='center', fontsize=8, color=GREY)
    polish_axes(ax)
    if save:
        save_panel(fig, save, show=show)
    return fig, ax


# ============================================================
# 20.20 plot_nhood_enrichment — 空间邻域富集热图（squidpy → mpl 兜底）
# ============================================================

def plot_nhood_enrichment(adata_sp, cluster_key='celltype',
                           spatial_key='spatial', ax=None, figsize=None,
                           save=None, show=None, **kwargs):
    """空间邻域富集热图——哪些细胞类型显著共邻。

    需要 adata_sp.obsp['spatial_connectivities']（先跑 ov.space.spatial_neighbors）。
    优先 squidpy.gr.nhood_enrichment 计算 z-score 矩阵；squidpy 不可用时 mpl 兜底
    （手动计数共邻频率 → 置换 z-score）。

    输出：方形热图（cluster × cluster），颜色=z-score，显著格子（|z|>2）标 *。
    """
    import numpy as np
    if cluster_key not in adata_sp.obs.columns:
        raise ValueError(f"cluster_key '{cluster_key}' not in obs")
    if 'spatial_connectivities' not in adata_sp.obsp:
        raise ValueError("adata_sp.obsp 没有 'spatial_connectivities'，请先跑 "
                         "ov.space.spatial_neighbors(adata_sp) 或 sq.gr.spatial_neighbors")
    cats = adata_sp.obs[cluster_key].astype('category')
    k = len(cats.cat.categories)
    zscore = np.zeros((k, k))
    try:
        import squidpy as sq
        sq.gr.nhood_enrichment(adata_sp, cluster_key=cluster_key)
        zscore = np.asarray(adata_sp.uns['nhood_enrichment']['zscore'], dtype=float)
    except Exception:
        # mpl 兜底：手动共邻计数 → 置换 z-score
        adj = adata_sp.obsp['spatial_connectivities']
        if hasattr(adj, 'toarray'):
            adj = adj.toarray()
        adj = np.asarray(adj, dtype=float)
        labels = cats.cat.codes.to_numpy()
        n_obs = adata_sp.n_obs
        counts = np.zeros((k, k))
        for i in range(n_obs):
            nbrs = np.nonzero(adj[i])[0]
            if nbrs.size == 0:
                continue
            li = labels[i]
            uniq, cnt = np.unique(labels[nbrs], return_counts=True)
            for u, c in zip(uniq, cnt):
                counts[li, u] += c
        counts = counts + counts.T
        np.fill_diagonal(counts, counts.diagonal() / 2)
        # 置换：随机打乱邻居归属，经验均值/标准差 → z-score
        rng = np.random.default_rng(0)
        perm = np.stack([rng.permutation(labels) for _ in range(200)])
        exp = np.zeros((k, k))
        se = np.zeros((k, k))
        for i in range(n_obs):
            nbrs = np.nonzero(adj[i])[0]
            if nbrs.size == 0:
                continue
            li = labels[i]
            uniq, cnt = np.unique(perm[:, nbrs[0]] if nbrs.size == 1 else perm[:, nbrs].flatten(),
                                  return_counts=True)
            for u, c in zip(uniq, cnt):
                exp[li, u] += c / 200
        exp = exp + exp.T
        np.fill_diagonal(exp, exp.diagonal() / 2)
        # 简化：以 counts 的 sqrt 作为尺度的 z-score 近似
        zscore = np.where(exp > 0, (counts - exp) / np.sqrt(exp + 1e-9), 0.0)
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize or (3.2, 3.0))
    else:
        fig = ax.figure
    im = ax.imshow(zscore, cmap=DIVERGING_CMAP, vmin=-6, vmax=6,
                   interpolation='nearest', aspect='auto')
    ax.set_xticks(range(k))
    ax.set_xticklabels(cats.cat.categories, fontsize=7, rotation=45, ha='right')
    ax.set_yticks(range(k))
    ax.set_yticklabels(cats.cat.categories, fontsize=7)
    ax.set_xlabel(cluster_key, fontsize=10, labelpad=10)
    ax.set_ylabel(cluster_key, fontsize=10, labelpad=10)
    ax.set_title('Neighborhood enrichment (z-score)', fontsize=12, pad=8)
    # 显著性标注：|z|>1.96 → *，|z|>2.58 → **
    for i in range(k):
        for j in range(k):
            z = zscore[i, j]
            if abs(z) > 2.58:
                ax.text(j, i, '**', ha='center', va='center', fontsize=7, color=NEAR_BLACK)
            elif abs(z) > 1.96:
                ax.text(j, i, '*', ha='center', va='center', fontsize=7, color=NEAR_BLACK)
    add_elegant_colorbar(im, ax, label='z-score')
    polish_axes(ax, subtle_grid=False)
    if save:
        save_panel(fig, save, show=show)
    return fig, ax


# ============================================================
# 20.21 plot_colocalization — 双信号空间共定位散点（ρ + p）
# ============================================================

def _resolve_signal(adata_sp, name):
    """取 var_names 基因 或 obs 列（如去卷积比例）的数值向量（plot_colocalization 内部用）。"""
    import numpy as np
    if name in adata_sp.var_names:
        v = adata_sp[:, name].X
        if hasattr(v, 'toarray'):
            v = v.toarray()
        return np.asarray(v).ravel().astype(float), 'gene'
    if name in adata_sp.obs.columns:
        return np.asarray(adata_sp.obs[name], dtype=float).ravel(), 'obs'
    raise ValueError(f"'{name}' 既不在 var_names（基因）也不在 obs 列（比例/元数据）")


def plot_colocalization(adata_sp, var_x, var_y, method='spearman',
                         groupby=None, ax=None, figsize=None,
                         save=None, show=None, **kwargs):
    """两种信号的空间共定位——per-spot 相关散点图。

    var_x/var_y 可以是基因名（adata.var_names）或 obs 列名（如去卷积比例列）。
    散点图 x=var_x, y=var_y，颜色=点密度（hexbin 或 alpha 散点）。
    标注相关系数 ρ + p 值。groupby 时按组分色。

    Args:
        method: 'spearman'（默认）或 'pearson'
        groupby: 非 None 时按该 obs 列分色（不分组面）
    """
    if _check_ov():
        try:
            import omicverse as ov
            import pandas as pd
            # 提取 var_x 和 var_y 的值（_resolve_signal 返回 (values, kind) 二元组）
            x_vals, _ = _resolve_signal(adata_sp, var_x)
            y_vals, _ = _resolve_signal(adata_sp, var_y)
            df_plot = pd.DataFrame({var_x: x_vals, var_y: y_vals})
            if groupby is not None and groupby in adata_sp.obs.columns:
                df_plot[groupby] = adata_sp.obs[groupby].values
                ov.pl.scatterplot(data=df_plot, x=var_x, y=var_y, hue=groupby,
                                  corr=method, alpha=0.5, s=8,
                                  figsize=figsize or (3.0, 2.8))
            else:
                ov.pl.scatterplot(data=df_plot, x=var_x, y=var_y,
                                  corr=method, alpha=0.5, s=8,
                                  figsize=figsize or (3.0, 2.8))
            fig = plt.gcf()
            if save:
                save_panel(fig, save, show=show)
            return fig, fig.axes[0] if fig.axes else None
        except Exception as e:
            print(f"[smart_plot] ov.pl.scatterplot failed ({e}), mpl fallback")
    import numpy as np
    from scipy.stats import spearmanr, pearsonr
    x, xtype = _resolve_signal(adata_sp, var_x)
    y, _ = _resolve_signal(adata_sp, var_y)
    mask = np.isfinite(x) & np.isfinite(y)
    x, y = x[mask], y[mask]
    if method == 'pearson':
        rho, p = pearsonr(x, y)
        rho_label = 'r'
    else:
        rho, p = spearmanr(x, y)
        rho_label = 'ρ'
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize or (3.0, 2.8))
    else:
        fig = ax.figure
    if groupby is not None:
        if groupby not in adata_sp.obs.columns:
            raise ValueError(f"groupby '{groupby}' not in obs")
        g = adata_sp.obs[groupby].astype(str).to_numpy()[mask]
        cats = sorted(set(g))
        for i, c in enumerate(cats):
            m = g == c
            ax.scatter(x[m], y[m], s=3, alpha=0.3, rasterized=True,
                       color=MORLANDI[i % len(MORLANDI)], label=c, edgecolor='none')
        ax.legend(bbox_to_anchor=(1.02, 0.5), loc='center left', frameon=False, fontsize=7)
    elif len(x) > 5000:
        hb = ax.hexbin(x, y, gridsize=60, mincnt=1, cmap=EXPR_CMAP,
                       edgecolors='none', rasterized=True)
        add_elegant_colorbar(hb, ax, label='spots')
    else:
        ax.scatter(x, y, s=3, alpha=0.3, rasterized=True, color='#5E81AC',
                   edgecolor='none')
    # 相关标注
    star = 'ns' if p >= 0.05 else ('*' if p >= 0.01 else '**')
    ax.text(0.03, 0.97,
            f'{rho_label}={rho:.2f}, p={p:.2e} {star} ({method.capitalize()})',
            transform=ax.transAxes, va='top', fontsize=8, color=GREY)
    ax.set_xlabel(var_x, fontsize=10, labelpad=10)
    ax.set_ylabel(var_y, fontsize=10, labelpad=10)
    ax.set_title('Spatial colocalization', fontsize=12, pad=8)
    polish_axes(ax)
    if save:
        save_panel(fig, save, show=show)
    return fig, ax


# ============================================================
# 20.22 plot_enrichment_scatter — 富集气泡散点（5 维：x/y/size/color/term）
# ============================================================

def plot_enrichment_scatter(enr_df, x='GeneRatio', y='FDR', size='Count',
                              color='FDR', top_n=15, term_col='Term',
                              ax=None, figsize=None, save=None, show=None, **kwargs):
    """富集分析气泡散点图——比条形图信息密度高（5 维）。

    enr_df 是富集结果 DataFrame（GO/KEGG/GSEA）。
    x 轴=GeneRatio（或自定义列），y 轴=-log10(FDR)，
    点大小=Count，点颜色=FDR。标注 top_n 通路名。

    Args:
        size/color: 需要归一化/映射的列名（默认均为 FDR）
        top_n: 按 -log10(FDR) 降序取前 n 条标注
    """
    if _check_ov():
        try:
            import omicverse as ov
            import pandas as pd
            import numpy as np
            df = enr_df.copy()
            df['_ylog'] = np.log10(df[y].replace(0, np.nan)) * -1
            df['_ylog'] = df['_ylog'].fillna(np.nanmax(df['_ylog']))
            df['_size_scaled'] = np.interp(df[size], (df[size].min(), df[size].max()), (8, 90))
            ov.pl.scatterplot(data=df, x=x, y='_ylog', size='_size_scaled',
                              cmap='YlOrRd', alpha=0.75,
                              figsize=figsize or (3.5, 3.0))
            fig = plt.gcf()
            # 标注 top_n 通路名
            top = df.nlargest(top_n, '_ylog')
            ax_fig = fig.axes[0] if fig.axes else None
            if ax_fig:
                for _, row in top.iterrows():
                    ax_fig.annotate(str(row[term_col])[:35], (row[x], row['_ylog']),
                                    fontsize=6, color=GREY, ha='left', va='center',
                                    xytext=(4, 0), textcoords='offset points')
            if save:
                save_panel(fig, save, show=show)
            return fig, ax_fig
        except Exception as e:
            print(f"[smart_plot] ov.pl.scatterplot failed ({e}), mpl fallback")
    import numpy as np
    import pandas as pd
    for col in (x, y, size, color):
        if col not in enr_df.columns:
            raise ValueError(f"enr_df 缺少列 '{col}'")
    df = enr_df.copy()
    df['_ylog'] = np.log10(df[y].replace(0, np.nan)) * -1
    df['_ylog'] = df['_ylog'].fillna(np.nanmax(df['_ylog']))
    df['_size_scaled'] = np.interp(df[size], (df[size].min(), df[size].max()), (20, 200))
    top = df.nlargest(top_n, '_ylog')
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize or (3.5, 3.0))
    else:
        fig = ax.figure
    sc = ax.scatter(df[x], df['_ylog'], s=df['_size_scaled'], c=df[color],
                    cmap=EXPR_CMAP, alpha=0.75, edgecolor=NEAR_BLACK,
                    linewidth=0.3, rasterized=True)
    # 通路名标注——交替左右偏移 + 引线，减少重叠
    try:
        from adjustText import adjust_text
        texts = [ax.text(row[x], row['_ylog'], str(row[term_col])[:35],
                         fontsize=6, color=GREY, ha='left', va='bottom')
                 for _, row in top.iterrows()]
        adjust_text(texts, arrowprops=dict(arrowstyle='-', color=GREY, lw=0.3))
    except ImportError:
        # adjustText 不可用时用交替偏移
        for i, (_, row) in enumerate(top.iterrows()):
            offset = (8, 6) if i % 2 == 0 else (8, -6)
            ax.annotate(str(row[term_col])[:35], (row[x], row['_ylog']),
                        fontsize=6, color=GREY, ha='left', va='center',
                        xytext=offset, textcoords='offset points',
                        arrowprops=dict(arrowstyle='-', color=GREY, lw=0.3))
    ax.set_xlabel(str(x), fontsize=10, labelpad=10)
    ax.set_ylabel(r'$-$log$_{10}$(' + str(y) + ')', fontsize=10, labelpad=10)
    ax.set_title('Enrichment bubble', fontsize=12, pad=8)
    add_elegant_colorbar(sc, ax, label=str(color))
    polish_axes(ax)
    if save:
        save_panel(fig, save, show=show)
    return fig, ax


# ============================================================
# 20.23 plot_ccc_network — CCC/模块互作网络图（力导向布局，CoVarNet 2025 风格）
# ============================================================

def plot_ccc_network(weight_matrix, labels=None, ax=None, figsize=None,
                     save=None, layout='fr', edge_threshold=0.1,
                     node_size_scale=500, show=None, **kwargs):
    """细胞通讯/模块互作网络图（plot_ccc 的 network 布局实现）。

    节点=细胞类型/模块，边=互作强度，力导向布局展示复杂拓扑。
    来源：CoVarNet Nature 2025 gr.igraph_global（Fruchterman-Reingold 布局）。

    Args:
        weight_matrix: 2D array/DataFrame，方阵（N×N），值=互作强度（0=无）
        labels: 节点标签列表（None=用 matrix index）
        layout: 'fr'(Fruchterman-Reingold 力导向) | 'circle'(环形) | 'spring'
        edge_threshold: 低于此值的边不画（过滤弱连接）
        node_size_scale: 节点大小缩放（节点大小=加权度中心性）
    Returns: (fig, ax)
    """
    import networkx as nx
    if hasattr(weight_matrix, 'values'):
        wm = weight_matrix.values
        if labels is None:
            labels = [str(x) for x in weight_matrix.index]
    else:
        wm = np.asarray(weight_matrix)
        labels = [str(i) for i in range(len(wm))]
    if wm.ndim != 2 or wm.shape[0] != wm.shape[1]:
        raise ValueError(
            f"weight_matrix 必须是方阵（N×N），实际 shape={wm.shape}")
    n = wm.shape[0]
    if labels is None:
        labels = [f'C{i}' for i in range(n)]
    labels = [str(l) for l in labels]
    if len(labels) != n:
        raise ValueError(f"labels 长度 {len(labels)} 与矩阵维度 {n} 不一致")
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize or (3.5, 3.0))
    else:
        fig = ax.figure
    # 构图：节点=labels，边权重=matrix 值（过滤弱连接）
    G = nx.Graph()
    G.add_nodes_from(range(n))
    for i in range(n):
        for j in range(i + 1, n):
            w = wm[i, j]
            if w > edge_threshold:
                G.add_edge(i, j, weight=float(w))
    # 布局：fr/spring → Fruchterman-Reingold 力导向；circle → 环形
    if layout == 'circle':
        pos = nx.circular_layout(G)
    else:  # 'fr' | 'spring'（FR 算法族）
        pos = nx.spring_layout(G, weight='weight', seed=42, k=1.2)
    # 节点大小 = 加权度（sum of edge weights）× node_size_scale
    deg = {i: 0.0 for i in range(n)}
    for u, v, d in G.edges(data=True):
        deg[u] += d['weight']; deg[v] += d['weight']
    max_deg = max(deg.values(), default=1) or 1
    sizes = {i: 30 + node_size_scale * deg[i] / max_deg for i in range(n)}
    # 边：alpha 按权重映射（0.2-0.8），宽度 0.5-3，灰阶（弱=浅灰，强=深灰）
    maxw = max((d['weight'] for _, _, d in G.edges(data=True)), default=1)
    for u, v, d in G.edges(data=True):
        t = d['weight'] / maxw
        ax.plot([pos[u][0], pos[v][0]], [pos[u][1], pos[v][1]],
                color=GREY, alpha=0.2 + 0.6 * t, lw=0.5 + 2.5 * t,
                solid_capstyle='round', zorder=2)
    # 节点：MORLANDI 按 index 循环，白描边
    for i in range(n):
        x, y = pos[i]
        ax.scatter(x, y, s=sizes[i], color=MORLANDI[i % len(MORLANDI)],
                   edgecolor='white', linewidth=1.2, zorder=5)
        # 标签放节点右侧（避免中心标签与节点重叠）
        ax.text(x + 0.05, y, labels[i], fontsize=8, color=NEAR_BLACK,
                ha='left', va='center', zorder=6)
    clean_umap_axes(ax, xlabel='', ylabel='')
    ax.set_title('CCC network', fontsize=12, pad=8)
    if save:
        save_panel(fig, save, show=show)
    return fig, ax


# ============================================================
# 20.24 plot_deconv_pie — 去卷积饼图网格（Per-spot 比例，Redeconve 2023 风格）
# ============================================================

def plot_deconv_pie(adata_sp, prop_cols=None, cluster_key=None,
                    spatial_key='spatial', max_spots=500, ax=None, figsize=None,
                    save=None, show=None, **kwargs):
    """Per-spot 去卷积饼图网格——每个 spot 一个饼图显示细胞类型比例。

    来源：Redeconve spatial.piechart。在空间坐标上画微型饼图（每个 spot 一个）。
    细胞类型 >6 时自动聚合低比例为 'Other'，避免饼图不可读。

    Args:
        adata_sp: 空转 AnnData（有 obsm[spatial_key]）
        prop_cols: 比例列名列表（如 ['flashdeconv_FB','flashdeconv_EndoCC',...]）
                   None=自动检测 obs 里 prop/frac 开头或 flashdeconv_ 前缀的列
        cluster_key: 可选，如果有离散 celltype 列（每个 spot 一个类型，直接着色不画饼）
        max_spots: 最大显示 spot 数（>max_spots 时随机采样，避免太密）
    Returns: (fig, ax)
    """
    from matplotlib import patches
    if _check_ov() and prop_cols is not None:
        try:
            import omicverse as ov
            fig, ax_pie = plt.subplots(figsize=figsize or (3.5, 3.0))
            coords_tmp = np.asarray(adata_sp.obsm[spatial_key])
            ax_pie.scatter(coords_tmp[:, 0], coords_tmp[:, 1], s=0.5,
                           c='lightgray', alpha=0.3, rasterized=True)
            ov.pl.add_pie2spatial(adata_sp, cell_type_columns=prop_cols[:6],
                                  ax=ax_pie, pie_radius=15)
            if save:
                save_panel(fig, save, show=show)
            return fig, ax_pie
        except Exception as e:
            print(f"[smart_plot] ov.pl.add_pie2spatial failed ({e}), mpl fallback")
    if spatial_key not in adata_sp.obsm:
        raise ValueError(f"adata_sp 需要 obsm['{spatial_key}']")
    coords = np.asarray(adata_sp.obsm[spatial_key])
    obs = adata_sp.obs
    # 离散 celltype 列 → 直接按类型着色（不画饼）
    if cluster_key is not None:
        return _deconv_pie_cluster(adata_sp, cluster_key, spatial_key,
                                   max_spots, ax, figsize, save, show)
    # 自动检测比例列
    if prop_cols is None:
        prop_cols = [c for c in obs.columns
                     if ('prop' in c or 'frac' in c or c.startswith('flashdeconv_'))]
    if not prop_cols:
        raise ValueError(
            "未找到去卷积比例列：prop_cols=None 时自动检测 obs 中 "
            "含 'prop'/'frac' 或以 'flashdeconv_' 开头的列，均未命中。"
            "请显式传入 prop_cols（如 ['flashdeconv_FB', ...]）。")
    # 排除非数值列（如 _dominant/_type 后缀的字符串列）
    prop_cols = [c for c in prop_cols if c in obs.columns]
    prop_cols = [c for c in prop_cols if np.issubdtype(obs[c].dtype, np.number)]
    if not prop_cols:
        raise ValueError(
            "prop_cols 中无数值列：所选列均为非数值（如 _dominant/_type 字符串列），"
            "请传入数值比例列。")
    P = obs[prop_cols].to_numpy(dtype=float)
    # 行归一化（保证每行和为 1）
    row_sum = P.sum(axis=1)
    P = P / np.where(row_sum > 0, row_sum, 1)[:, None]
    # spot 采样
    n = len(coords)
    if n > max_spots:
        idx = np.random.default_rng(42).choice(n, size=max_spots, replace=False)
        coords, P = coords[idx], P[idx]
    # 微型饼图半径：按最近邻中位距离自适应（避免 0.8 固定值在 Visium 尺度下太小/太大）
    if len(coords) > 2:
        d = np.linalg.norm(coords[:, None, :] - coords[None, :, :], axis=-1)
        np.fill_diagonal(d, np.inf)
        nn = np.median(d.min(axis=1))
        radius = max(0.8, 0.4 * nn)
    else:
        radius = 0.8
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize or (3.5, 3.0))
    else:
        fig = ax.figure
    n_cells = P.shape[1]
    # >6 类时聚合 <5% 的低比例为 'Other'
    if n_cells > 6:
        frac = P.mean(axis=0)
        keep = frac >= 0.05
        if keep.all():
            cell_names = list(prop_cols)
        else:
            P_agg = np.column_stack([P[:, keep], P[:, ~keep].sum(axis=1)])
            cell_names = [prop_cols[i] for i in np.where(keep)[0]] + ['Other']
            P = P_agg
    else:
        cell_names = list(prop_cols)
    n_cells = P.shape[1]
    palette = [MORLANDI[i % len(MORLANDI)] for i in range(n_cells)]
    # 逐 spot 画扇形（Wedge）
    for (x, y), p in zip(coords, P):
        start = 0.0
        for k in range(n_cells):
            frac_k = p[k]
            if frac_k <= 0:
                continue
            theta = 360.0 * frac_k
            ax.add_patch(patches.Wedge((x, y), radius, start, start + theta,
                                       width=None, facecolor=palette[k],
                                       edgecolor='white', linewidth=0.2, zorder=3))
            start += theta
    ax.set_aspect('equal')
    clean_umap_axes(ax, xlabel='', ylabel='')
    # 图例外置右侧
    handles = [plt.Line2D([], [], marker='o', linestyle='None', markersize=7,
                          markerfacecolor=c, markeredgecolor='none', label=n)
               for c, n in zip(palette, cell_names)]
    ax.legend(handles=handles, loc='center left', bbox_to_anchor=(1.02, 0.5),
              frameon=False, fontsize=7, title='Cell type', title_fontsize=8)
    if save:
        save_panel(fig, save, show=show)
    return fig, ax


def _deconv_pie_cluster(adata_sp, cluster_key, spatial_key, max_spots,
                        ax, figsize, save, show):
    """plot_deconv_pie 的离散 celltype 分支：每个 spot 一种类型，scatter 着色。"""
    if cluster_key not in adata_sp.obs:
        raise ValueError(f"obs 中无列 '{cluster_key}'")
    coords = np.asarray(adata_sp.obsm[spatial_key])
    cats = adata_sp.obs[cluster_key].astype('category')
    n = len(coords)
    if n > max_spots:
        idx = np.random.default_rng(42).choice(n, size=max_spots, replace=False)
        coords, cats = coords[idx], cats.iloc[idx]
    palette = {ct: MORLANDI[i % len(MORLANDI)]
               for i, ct in enumerate(cats.cat.categories)}
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize or (3.5, 3.0))
    else:
        fig = ax.figure
    colors = [palette[ct] for ct in cats]
    ax.scatter(coords[:, 0], coords[:, 1], c=colors, s=8, alpha=0.85,
               edgecolor='none', rasterized=True)
    ax.set_aspect('equal')
    clean_umap_axes(ax, xlabel='', ylabel='')
    handles = [plt.Line2D([], [], marker='o', linestyle='None', markersize=7,
                          markerfacecolor=c, markeredgecolor='none', label=ct)
               for ct, c in palette.items()]
    ax.legend(handles=handles, loc='center left', bbox_to_anchor=(1.02, 0.5),
              frameon=False, fontsize=7, title='Cell type', title_fontsize=8)
    if save:
        save_panel(fig, save, show=show)
    return fig, ax
# ============================================================
# 20.25-20.39: 分布/统计/集合类图（ov.pl 优先 → mpl 兜底）
# ============================================================

def _adata_to_tidy(adata, cols):
    """AnnData → tidy DataFrame：基因名（var_names）提取表达值，obs 列名直接用。

    Args:
        adata: AnnData 对象
        cols: list[str]，基因名或 obs 列名（可混合）
    Returns:
        pandas.DataFrame：列=cols（保持给定顺序），行=adata.obs_names
    """
    import pandas as pd
    out = {}
    for c in cols:
        if c in adata.var_names:
            expr = adata[:, c].X
            if hasattr(expr, 'toarray'):
                expr = expr.toarray()
            out[c] = np.asarray(expr).ravel()
        elif c in adata.obs.columns:
            out[c] = adata.obs[c].values
        else:
            raise ValueError(f"'{c}' 既不是 var_names 也不是 obs 列")
    return pd.DataFrame(out, index=adata.obs_names)


# ============================================================
# 20.25 plot_ridge — 山脊图（ov.pl.ridgeplot → mpl KDE 叠放）
# ============================================================
def plot_ridge(adata, keys, groupby='celltype', ax=None, figsize=None,
               save=None, show=None, overlap=0.2, **kwargs):
    """山脊图（ridgeplot）：多组表达分布叠放比较。纯 mpl 实现。

    >5 组时比 violin 更清晰（CNS marker 验证标配）。
    Args:
        overlap: 行间重叠比例（0=完全分离, 0.2=微叠便于区分）。
    """
    import pandas as pd
    if isinstance(keys, str):
        keys = [keys]
    n_genes = len(keys)
    if ax is None:
        n_groups = adata.obs[groupby].astype('category').nunique()
        # 宽度固定 3.0"，高度按组数自适应
        fig, axes = plt.subplots(n_genes, 1, figsize=figsize or
                                 (3.0, (n_groups * 0.5 + 0.5) * n_genes),
                                 sharex=False)
        if n_genes == 1:
            axes = [axes]
    else:
        fig = ax.figure
        axes = [ax]
        keys = keys[:1]
    groups = adata.obs[groupby].astype('category').cat.categories
    for row, g in enumerate(keys):
        _ridge_mpl(adata, g, groupby, groups, axes[row], overlap=overlap)
    fig = axes[0].figure
    if save:
        save_panel(fig, save, show=show)
    return fig, axes if n_genes > 1 else axes[0]


def _ridge_mpl(adata, gene, groupby, groups, ax, overlap=0.5):
    """mpl ridge：逐组 KDE 叠放，固定行高 + 下方盖上方。

    - 每行高度固定 row_height=1.0（KDE 归一化后统一缩放）
    - 行间距 step = row_height * (1 - overlap)
    - z-order：第一组（底部）zorder 最高 → 下方盖上方
    - 组名标签放左侧 y 轴位置
    """
    from scipy.stats import gaussian_kde
    if gene in adata.var_names:
        expr = adata[:, gene].X
        if hasattr(expr, 'toarray'):
            expr = expr.toarray()
        expr = np.asarray(expr).ravel()
    else:
        expr = np.zeros(adata.n_obs)
    xmin, xmax = np.percentile(expr, 0.1), np.percentile(expr, 99.9)
    x = np.linspace(xmin, xmax, 300)
    row_height = 1.0
    step = row_height * (1.0 - overlap)
    n_groups = len(groups)
    # 从下到上画：第一组在底部（y=0），最后一组在顶部
    # z-order：底部组 zorder 最大（下方盖上方）
    for i, grp in enumerate(groups):
        mask = (adata.obs[groupby] == grp).values
        vals = expr[mask]
        baseline = i * step
        if len(vals) < 2 or vals.std() == 0:
            # 退化组：画一条平线
            ax.axhline(baseline, xmin=0.05, xmax=0.95, color=MORLANDI[i % len(MORLANDI)],
                       alpha=0.5, lw=1, zorder=n_groups - i)
        else:
            kde = gaussian_kde(vals)
            y = kde(x)
            peak = y.max()
            if peak > 0:
                y = y / peak * row_height  # 归一化到固定行高
            scaled = baseline + y
            # z-order: 底部组最大 → 下方盖上方
            z = n_groups - i + 1
            ax.fill_between(x, baseline, scaled, alpha=0.65,
                            color=MORLANDI[i % len(MORLANDI)], zorder=z)
            ax.plot(x, scaled, color='white', lw=0.8, zorder=z + 0.1)
        # 组名标签放左侧 y=baseline 位置
        ax.text(xmin - (xmax - xmin) * 0.02, baseline + row_height * 0.3,
                str(grp), fontsize=7, color=GREY, ha='right', va='center')
    ax.set_xlim(xmin, xmax)
    top = (n_groups - 1) * step + row_height
    ax.set_ylim(-0.3, top + 0.2)
    ax.set_yticks([])
    ax.set_xlabel(gene, fontsize=7, fontstyle='italic', labelpad=6)
    ax.tick_params(axis='x', labelsize=7, length=2, colors=NEAR_BLACK)
    # 只保留 x 轴线（bottom spine），隐藏其余
    for sp_name in ('top', 'left', 'right'):
        ax.spines[sp_name].set_visible(False)
    ax.spines['bottom'].set_visible(True)
    ax.spines['bottom'].set_linewidth(0.8)
    ax.spines['bottom'].set_color(NEAR_BLACK)


# ============================================================
# 20.26 plot_boxplot — 箱线图+抖动（ov.pl.boxplot → mpl boxplot+scatter）
# ============================================================
def plot_boxplot(adata, keys, groupby='celltype', ax=None, figsize=None,
                 save=None, show=None, **kwargs):
    """箱线图+抖动点：分布比较的简洁替代。ov.pl.boxplot 优先，mpl 兜底。"""
    import pandas as pd
    if isinstance(keys, str):
        keys = [keys]
    n_genes = len(keys)
    if ax is None:
        fig, axes = plt.subplots(n_genes, 1, figsize=figsize or
                                 (min(len(adata.obs[groupby].unique()) * 0.4 + 0.8, 3.5),
                                     n_genes * 2.0), sharex=False)
        if n_genes == 1:
            axes = [axes]
    else:
        fig = ax.figure
        axes = [ax]
        keys = keys[:1]
    if _check_ov() and len(axes) == 1:
        try:
            import omicverse as ov
            df = _adata_to_tidy(adata, keys + [groupby])
            # ov.pl.boxplot 的 hue=None 会 KeyError(None)（内部 data[None]）
            # → 注入常量伪 hue 列，单类别等价于无 hue
            if 'hue' not in df.columns:
                df['hue'] = 'all'
            ov.pl.boxplot(data=df, hue='hue', x_value=groupby, y_value=keys[0],
                          **kwargs)
            fig_ov = plt.gcf()          # boxplot 无 ax 参数，自建 figure
            fig_ov.set_size_inches(*(figsize or (min(len(df[groupby].unique())*0.4+0.8, 3.5), 2.0)))
            ax_ov = fig_ov.axes[0] if fig_ov.axes else axes[0]
            legend = ax_ov.get_legend()
            if legend is not None:
                legend.remove()         # 常量 hue 的图例无信息量
            polish_axes(ax_ov)
            if save:
                save_panel(fig_ov, save, show=show)
            return fig_ov, ax_ov
        except Exception as e:
            print(f"[smart_plot] ov.pl.boxplot failed ({e}), mpl fallback")
    groups = adata.obs[groupby].astype('category').cat.categories
    for row, g in enumerate(keys):
        _boxplot_mpl(adata, g, groupby, groups, axes[row])
    fig = axes[0].figure
    polish_axes(axes[-1])
    if save:
        save_panel(fig, save, show=show)
    return fig, axes if n_genes > 1 else axes[0]


def _boxplot_mpl(adata, gene, groupby, groups, ax):
    """mpl boxplot + jitter scatter。"""
    if gene in adata.var_names:
        expr = adata[:, gene].X
        if hasattr(expr, 'toarray'):
            expr = expr.toarray()
        expr = np.asarray(expr).ravel()
    else:
        expr = np.zeros(adata.n_obs)
    data_per = [expr[(adata.obs[groupby] == grp).values] for grp in groups]
    bp = ax.boxplot(data_per, positions=range(len(groups)), widths=0.5,
                    patch_artist=True, showfliers=False, zorder=2)
    for i, patch in enumerate(bp['boxes']):
        c = MORLANDI[i % len(MORLANDI)]
        patch.set_facecolor(c); patch.set_alpha(0.55)
        patch.set_edgecolor(NEAR_BLACK); patch.set_linewidth(0.8)
    for element in ('whiskers', 'caps', 'medians'):
        for line in bp[element]:
            line.set_color(NEAR_BLACK); line.set_linewidth(0.8)
    # jitter scatter
    for i, d in enumerate(data_per):
        jit = np.random.default_rng(42).uniform(-0.18, 0.18, len(d))
        ax.scatter(np.full(len(d), i) + jit, d, s=2, alpha=0.5,
                   color=NEAR_BLACK, edgecolor='none', zorder=3, rasterized=True)
    ax.set_xticks(range(len(groups)))
    ax.set_xticklabels(groups, fontsize=7,
                       rotation=45 if len(groups) > 8 else 0)
    ax.set_ylabel(gene, fontsize=9, fontstyle='italic')


# ============================================================
# 20.27 plot_kde — 核密度估计（ov.pl.kdeplot → scipy gaussian_kde）
# ============================================================
def plot_kde(data, x, y=None, hue=None, ax=None, figsize=None,
             save=None, show=None, **kwargs):
    """核密度估计图。ov.pl.kdeplot 优先，mpl 兜底。
    data 可以是 AnnData（x/y 是基因名→自动提取表达）或 DataFrame。
    """
    import pandas as pd
    if hasattr(data, 'var_names'):   # AnnData
        cols = [c for c in (x, y, hue) if c]
        df = _adata_to_tidy(data, cols)
    else:
        df = data
    if y is None:
        use_x, use_y = x, None
    else:
        use_x, use_y = (x, y) if x in df.columns else (y, x)
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize or (3.0, 2.5))
    else:
        fig = ax.figure
    if _check_ov():
        try:
            import omicverse as ov
            ov.pl.kdeplot(data=df, x=use_x, y=use_y, hue=hue,
                          ax=ax, **kwargs)
            polish_axes(ax)
            if save:
                save_panel(fig, save, show=show)
            return fig, ax
        except Exception as e:
            print(f"[smart_plot] ov.pl.kdeplot failed ({e}), mpl fallback")
    _kde_mpl(df, use_x, use_y, hue, ax)
    polish_axes(ax)
    if save:
        save_panel(fig, save, show=show)
    return fig, ax


def _kde_mpl(df, x, y, hue, ax):
    """mpl KDE：单变量一维曲线 / 双变量等高线。"""
    from scipy.stats import gaussian_kde
    if y is None:
        # 单变量：按 hue 分组画曲线
        if hue is None:
            vals = df[x].dropna().values
            if len(vals) < 2:
                return
            xs = np.linspace(vals.min(), vals.max(), 300)
            ax.plot(xs, gaussian_kde(vals)(xs), color=MORLANDI[0], lw=1.5)
            ax.fill_between(xs, gaussian_kde(vals)(xs),
                            color=MORLANDI[0], alpha=0.25)
            ax.set_xlabel(x); ax.set_ylabel('Density')
        else:
            for i, grp in enumerate(df[hue].astype('category').cat.categories):
                vals = df.loc[df[hue] == grp, x].dropna().values
                if len(vals) < 2:
                    continue
                xs = np.linspace(vals.min(), vals.max(), 300)
                c = MORLANDI[i % len(MORLANDI)]
                ax.plot(xs, gaussian_kde(vals)(xs), color=c, lw=1.5, label=grp)
                ax.fill_between(xs, gaussian_kde(vals)(xs), color=c, alpha=0.2)
            ax.set_xlabel(x); ax.set_ylabel('Density')
            ax.legend(frameon=False, fontsize=7)
    else:
        # 双变量：等高线
        d = df[[x, y]].dropna()
        if len(d) < 3:
            return
        k = gaussian_kde(d.values.T)
        xi = np.linspace(d[x].min(), d[x].max(), 100)
        yi = np.linspace(d[y].min(), d[y].max(), 100)
        X, Y = np.meshgrid(xi, yi)
        Z = k(np.vstack([X.ravel(), Y.ravel()])).reshape(X.shape)
        ax.contourf(X, Y, Z, levels=10, cmap=EXPR_CMAP, alpha=0.6)
        ax.set_xlabel(x); ax.set_ylabel(y)


# ============================================================
# 20.28 plot_histplot — 直方图（ov.pl.histplot → mpl hist）
# ============================================================
def plot_histplot(data, x, hue=None, bins='auto', ax=None, figsize=None,
                  save=None, show=None, **kwargs):
    """直方图：QC-metric 分布标配。ov.pl.histplot 优先，mpl 兜底。"""
    import pandas as pd
    if hasattr(data, 'var_names'):   # AnnData
        df = _adata_to_tidy(data, [c for c in (x, hue) if c])
    else:
        df = data
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize or (3.0, 2.5))
    else:
        fig = ax.figure
    if _check_ov():
        try:
            import omicverse as ov
            ov.pl.histplot(data=df, x=x, hue=hue, bins=bins,
                           ax=ax, **kwargs)
            polish_axes(ax)
            if save:
                save_panel(fig, save, show=show)
            return fig, ax
        except Exception as e:
            print(f"[smart_plot] ov.pl.histplot failed ({e}), mpl fallback")
    if hue is None:
        ax.hist(df[x].dropna(), bins=bins, color=MORLANDI[0], alpha=0.75,
                edgecolor='white', linewidth=0.4)
    else:
        for i, grp in enumerate(df[hue].astype('category').cat.categories):
            vals = df.loc[df[hue] == grp, x].dropna()
            ax.hist(vals, bins=bins, alpha=0.55, label=grp,
                    color=MORLANDI[i % len(MORLANDI)], edgecolor='white',
                    linewidth=0.3)
        ax.legend(frameon=False, fontsize=7)
    ax.set_xlabel(x); ax.set_ylabel('Count')
    polish_axes(ax)
    if save:
        save_panel(fig, save, show=show)
    return fig, ax


# ============================================================
# 20.29 plot_stripplot — 抖动散点（ov.pl.stripplot → mpl scatter）
# ============================================================
def plot_stripplot(data, x, y, hue=None, ax=None, figsize=None,
                   save=None, show=None, **kwargs):
    """抖动散点：每个观测点都可见。ov.pl.stripplot 优先，mpl 兜底。"""
    import pandas as pd
    if hasattr(data, 'var_names'):   # AnnData
        df = _adata_to_tidy(data, [c for c in (x, y, hue) if c])
    else:
        df = data
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize or (3.0, 2.5))
    else:
        fig = ax.figure
    if _check_ov():
        try:
            import omicverse as ov
            ov.pl.stripplot(data=df, x=x, y=y, hue=hue,
                            ax=ax, **kwargs)
            polish_axes(ax)
            if save:
                save_panel(fig, save, show=show)
            return fig, ax
        except Exception as e:
            print(f"[smart_plot] ov.pl.stripplot failed ({e}), mpl fallback")
    # mpl 兜底：x 分类型 → 抖动；x 连续型 → 直接散点
    if df[x].dtype.name.startswith(('int', 'float')) and df[x].nunique() > 12:
        ax.scatter(df[x], df[y], s=4, alpha=0.6, color=MORLANDI[0],
                   edgecolor='none', rasterized=True)
        ax.set_xlabel(x)
    else:
        cats = df[x].astype('category')
        rng = np.random.default_rng(42)
        for i, grp in enumerate(cats.cat.categories):
            vals = df.loc[cats == grp, y]
            jit = rng.uniform(-0.18, 0.18, len(vals))
            ax.scatter(np.full(len(vals), i) + jit, vals, s=4, alpha=0.6,
                       color=MORLANDI[i % len(MORLANDI)], edgecolor='none',
                       rasterized=True, label=None if hue else grp)
        ax.set_xticks(range(len(cats.cat.categories)))
        ax.set_xticklabels(cats.cat.categories, fontsize=7,
                           rotation=45 if len(cats.cat.categories) > 8 else 0)
        ax.set_xlabel(x)
    ax.set_ylabel(y)
    polish_axes(ax)
    if save:
        save_panel(fig, save, show=show)
    return fig, ax


# ============================================================
# 20.30 plot_stackarea — 细胞比例堆叠面积（ov.pl.cellstackarea → mpl stackplot）
# ============================================================
def plot_stackarea(adata, celltype_col='celltype', groupby='condition',
                   ax=None, figsize=None, save=None, show=None, **kwargs):
    """细胞比例堆叠面积图：比例随连续/有序变量变化。ov.pl.cellstackarea 优先，mpl 兜底。"""
    import pandas as pd
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize or (3.0, 2.5))
    else:
        fig = ax.figure
    if _check_ov():
        try:
            import omicverse as ov
            ov.pl.cellstackarea(adata, celltype_clusters=celltype_col,
                                groupby=groupby, ax=ax)
            if save:
                save_panel(fig, save, show=show)
            return fig, ax
        except Exception as e:
            print(f"[smart_plot] ov.pl.cellstackarea failed ({e}), mpl fallback")
    # mpl 兜底：按 groupby 分组算比例，stackplot
    ct = adata.obs[celltype_col].astype('category')
    g = adata.obs[groupby]
    groups = g.astype('category').cat.categories
    prop = pd.DataFrame(index=groups, columns=ct.cat.categories, dtype=float)
    for grp in groups:
        mask = (g == grp).values
        if mask.sum() == 0:
            prop.loc[grp] = 0.0
            continue
        counts = ct[mask].value_counts()
        prop.loc[grp] = [counts.get(c, 0) / mask.sum() for c in ct.cat.categories]
    prop = prop.fillna(0.0)
    x = np.arange(len(groups))
    ax.stackplot(x, *prop.values.T, labels=prop.columns,
                 colors=[MORLANDI[i % len(MORLANDI)]
                         for i in range(len(prop.columns))],
                 alpha=0.85, edgecolor='white', linewidth=0.3)
    ax.set_xticks(x)
    ax.set_xticklabels(groups, fontsize=7, rotation=45 if len(groups) > 8 else 0)
    ax.set_xlabel(groupby)
    ax.set_ylabel('Proportion')
    ax.set_ylim(0, 1)
    ax.legend(bbox_to_anchor=(1.02, 0.5), loc='center left', frameon=False,
              fontsize=7, title=celltype_col)
    polish_axes(ax)
    if save:
        save_panel(fig, save, show=show)
    return fig, ax


# ============================================================
# 20.31 plot_bardotplot — 柱+点组合（ov.pl.bardotplot → mpl bar+scatter）
# ============================================================
def plot_bardotplot(adata, groupby, color, ax=None, figsize=None,
                    save=None, show=None, **kwargs):
    """柱+点组合图：均值柱+分布点双重展示。ov.pl.bardotplot 优先，mpl 兜底。"""
    import pandas as pd
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize or (3.0, 2.5))
    else:
        fig = ax.figure
    if _check_ov():
        try:
            import omicverse as ov
            ov.pl.bardotplot(adata, groupby=groupby, color=color,
                             ax=ax)
            polish_axes(ax)
            if save:
                save_panel(fig, save, show=show)
            return fig, ax
        except Exception as e:
            print(f"[smart_plot] ov.pl.bardotplot failed ({e}), mpl fallback")
    # mpl 兜底：color 是基因名 → 各 group 均值柱 + 逐细胞抖动点；
    #          color 是 obs 类别列 → 各 group 内类别占比柱
    groups = adata.obs[groupby].astype('category').cat.categories
    rng = np.random.default_rng(42)
    if color in adata.var_names:
        expr = adata[:, color].X
        if hasattr(expr, 'toarray'):
            expr = expr.toarray()
        expr = np.asarray(expr).ravel()
        means = [expr[(adata.obs[groupby] == grp).values].mean()
                 for grp in groups]
        ax.bar(range(len(groups)), means, width=0.55,
               color=MORLANDI[0], alpha=0.85,
               edgecolor='white', linewidth=0.4, zorder=2)
        # 逐 cell 抖动点
        for gi, grp in enumerate(groups):
            vals = expr[(adata.obs[groupby] == grp).values]
            jit = rng.uniform(-0.18, 0.18, len(vals))
            ax.scatter(np.full(len(vals), gi) + jit, vals, s=4, alpha=0.4,
                       color=NEAR_BLACK, edgecolor='none',
                       rasterized=True, zorder=3)
        ax.set_ylabel(color, fontsize=9, fontstyle='italic')
    else:
        cats = pd.unique(adata.obs[color])
        for i, c in enumerate(cats):
            means = []
            for gi, grp in enumerate(groups):
                mask = ((adata.obs[groupby] == grp) & (adata.obs[color] == c)).values
                prop = mask.mean() if mask.sum() > 0 else 0.0
                means.append(prop)
                if mask.sum():
                    jitter = rng.uniform(0, 0.9, int(mask.sum()))
                    xs = np.full(int(mask.sum()), gi) + rng.uniform(-0.12, 0.12, int(mask.sum()))
                    ax.scatter(xs, 0.05 + jitter, s=3, alpha=0.35,
                               color=MORLANDI[i % len(MORLANDI)],
                               edgecolor='none', rasterized=True)
            ax.bar([g + (i - (len(cats) - 1) / 2) * 0.18 for g in range(len(groups))],
                   means, width=0.18,
                   color=MORLANDI[i % len(MORLANDI)], alpha=0.85,
                   edgecolor='white', linewidth=0.4, label=c)
        ax.set_ylabel(f'{color} proportion')
        ax.set_ylim(0, 1)
    ax.set_xticks(range(len(groups)))
    ax.set_xticklabels(groups, fontsize=7, rotation=45 if len(groups) > 8 else 0)
    if color not in adata.var_names:
        ax.legend(bbox_to_anchor=(1.02, 0.5), loc='center left', frameon=False,
                  fontsize=7)
    polish_axes(ax)
    if save:
        save_panel(fig, save, show=show)
    return fig, ax


# ============================================================
# 20.32 plot_stacking_vol — 堆叠火山（ov.pl.stacking_vol，无 mpl 兜底）
# ============================================================
def plot_stacking_vol(data_dict, color_dict=None, ax=None, figsize=None,
                      save=None, show=None, **kwargs):
    """堆叠火山图：多条件 DE 并排比较。直接传参给 ov.pl.stacking_vol。
    data_dict: {条件名: DE DataFrame}（每含 gene/padj/log2FC 列）
    """
    import pandas as pd
    if not _check_ov():
        print("[smart_plot] ov.pl.stacking_vol 需要 omicverse，跳过")
        return None, None
    try:
        import omicverse as ov
        if color_dict is None:
            color_dict = {k: MORLANDI[i % len(MORLANDI)]
                          for i, k in enumerate(data_dict)}
        _col_map = {'gene': 'names', 'padj': 'pvals_adj', 'log2FC': 'logfoldchanges'}
        data_dict_ov = {}
        for k, de in data_dict.items():
            if isinstance(de, pd.DataFrame):
                de = de.rename(columns={old: new
                                        for old, new in _col_map.items()
                                        if old in de.columns and new not in de.columns})
            data_dict_ov[k] = de
        n_conds = len(data_dict)
        fig_size = figsize or (min(n_conds * 1.8, 5.0), 3.0)
        out = ov.pl.stacking_vol(data_dict_ov, color_dict, figsize=fig_size, **kwargs)
        if isinstance(out, tuple) and len(out) == 2:
            fig, axes = out
        else:
            fig, axes = out, None
        if fig is None:
            fig = plt.gcf()
        # 条件名标注在色块中央（savefig 后再标注，避免 finalize_figure 干扰）
        if isinstance(axes, dict):
            for cond_name, cond_ax in axes.items():
                cond_ax.set_title(cond_name, fontsize=10, fontweight='bold', pad=4)
        if save:
            save_panel(fig, save, show=show)
            # save_panel 后重新标注（finalize_figure 可能清了 title）
            if isinstance(axes, dict):
                for cond_name, cond_ax in axes.items():
                    cond_ax.set_title(cond_name, fontsize=10, fontweight='bold', pad=4)
                import os
                dpi = plt.rcParams.get('savefig.dpi', 300)
                if '/' in save or '\\' in save:
                    path = f'{save}.pdf'
                else:
                    path = f'panels/{save}.pdf'
                fig.savefig(path, dpi=dpi, bbox_inches='tight', pad_inches=0.1)
        ax_out = None
        if axes is not None:
            if isinstance(axes, dict) and axes:
                ax_out = next(iter(axes.values()))
            elif hasattr(axes, '__iter__') and not isinstance(axes, str):
                ax_out = list(axes)[0] if list(axes) else None
            else:
                ax_out = axes
        return fig, ax_out
    except Exception as e:
        print(f"[smart_plot] ov.pl.stacking_vol failed ({e})")
        return None, None
# ============================================================
# 20.33 plot_upset — UpSet 图（ov 专用，无 mpl 兜底）
# ============================================================
def plot_upset(sets, top_n=30, ax=None, figsize=None,
               save=None, show=None, **kwargs):
    """UpSet 图：>3 组基因集交集可视化。ov.pl.upset 优先。
    sets: dict {集合名: list/set of items}
    无 mpl 兜底（UpSet 布局复杂，纯 ov）；ov 不可用时打印警告返回 None。
    """
    if not _check_ov():
        print("[smart_plot] ov.pl.upset 需要 omicverse，跳过")
        return None, None
    try:
        import omicverse as ov
        ov.pl.upset(sets, top_n=top_n, **kwargs)
        fig = plt.gcf()          # upset 自建 figure
        # 关掉所有子图的网格线
        for a in fig.axes:
            a.grid(False)
        if figsize:
            fig.set_size_inches(*figsize)
        else:
            fig.set_size_inches(4.0, 2.5)
        if save:
            save_panel(fig, save, show=show)
        return fig, fig.axes[0] if fig.axes else None
    except Exception as e:
        print(f"[smart_plot] ov.pl.upset failed ({e})")
        return None, None


# ============================================================
# 20.34 plot_venn — Venn 图（ov.pl.venn，无 mpl 兜底）
# ============================================================
def plot_venn(sets, ax=None, figsize=None, save=None, show=None, **kwargs):
    """Venn 图：≤4 组基因集交集。ov.pl.venn 优先。
    sets: dict {集合名: set/list}（2-4 组）
    无 mpl 兜底；ov.pl.venn 的 out 参数默认写文件到 './'，此处传临时目录避免污染 CWD。
    """
    import tempfile
    if not _check_ov():
        print("[smart_plot] ov.pl.venn 需要 omicverse，跳过")
        return None, None
    try:
        import omicverse as ov
        with tempfile.TemporaryDirectory() as tmpdir:
            ov.pl.venn(sets=sets, out=tmpdir, **kwargs)
            fig = plt.gcf()
            fig.set_size_inches(*(figsize or (2.5, 2.5)))
            if save:
                save_panel(fig, save, show=show)
            return fig, fig.axes[0] if fig.axes else None
    except Exception as e:
        print(f"[smart_plot] ov.pl.venn failed ({e})")
        return None, None


# ============================================================
# 20.35 plot_forest — 森林图（ov.pl.forest → mpl errorbar）
# ============================================================
def plot_forest(data, estimate, lower=None, upper=None, label=None,
                group=None, ax=None, figsize=None, save=None, show=None, **kwargs):
    """森林图：meta-analysis/多研究效应合并。ov.pl.forest 优先，mpl 兜底。
    data: DataFrame，estimate/lower/upper/label 是列名。
    """
    import pandas as pd
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize or (2.5, min(len(data) * 0.3 + 0.5, 3.5)))
    else:
        fig = ax.figure
    if _check_ov():
        try:
            import omicverse as ov
            ov.pl.forest(data=data, estimate=estimate, lower=lower, upper=upper,
                         label=label, group=group, ax=ax, **kwargs)
            polish_axes(ax)
            if save:
                save_panel(fig, save, show=show)
            return fig, ax
        except Exception as e:
            print(f"[smart_plot] ov.pl.forest failed ({e}), mpl fallback")
    # mpl 兜底：errorbar + 零线
    est = data[estimate].values
    if lower is not None and upper is not None:
        lo = est - data[lower].values        # lower 语义=下界值
        up = data[upper].values - est
        yerr = np.vstack([lo, up])
    else:
        yerr = None
    y = np.arange(len(data))
    ax.errorbar(est, y, xerr=yerr, fmt='o', color=MORLANDI[0],
                ecolor=GREY, elinewidth=1.0, capsize=2.5, markersize=5,
                zorder=3)
    if label is not None and label in data.columns:
        ax.set_yticks(y)
        ax.set_yticklabels(data[label].astype(str).values, fontsize=7)
    else:
        ax.set_yticks(y)
        ax.set_yticklabels(data.index.astype(str), fontsize=7)
    ax.invert_yaxis()
    ax.axvline(0, color=GREY, lw=0.8, linestyle='--', zorder=1)
    ax.set_xlabel(estimate)
    polish_axes(ax)
    if save:
        save_panel(fig, save, show=show)
    return fig, ax


# ============================================================
# 20.36 plot_regplot — 回归散点（ov.pl.regplot → mpl polyfit）
# ============================================================
def plot_regplot(data, x, y, hue=None, fit='linear', ax=None, figsize=None,
                 save=None, show=None, **kwargs):
    """回归散点图：带拟合线（相关性分析标配）。ov.pl.regplot 优先，mpl 兜底。"""
    import pandas as pd
    if hasattr(data, 'var_names'):   # AnnData
        df = _adata_to_tidy(data, [c for c in (x, y, hue) if c])
    else:
        df = data
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize or (3.0, 2.5))
    else:
        fig = ax.figure
    if _check_ov():
        try:
            import omicverse as ov
            ov.pl.regplot(data=df, x=x, y=y, hue=hue, fit=fit,
                          ax=ax, **kwargs)
            polish_axes(ax)
            if save:
                save_panel(fig, save, show=show)
            return fig, ax
        except Exception as e:
            print(f"[smart_plot] ov.pl.regplot failed ({e}), mpl fallback")
    # mpl 兜底：scatter + polyfit 拟合线
    if hue is None:
        ax.scatter(df[x], df[y], s=6, alpha=0.6, color=MORLANDI[0],
                   edgecolor='none', rasterized=True)
        _fit_line(ax, df[x].values, df[y].values, fit)
    else:
        for i, grp in enumerate(df[hue].astype('category').cat.categories):
            sub = df[df[hue] == grp]
            c = MORLANDI[i % len(MORLANDI)]
            ax.scatter(sub[x], sub[y], s=6, alpha=0.6, color=c,
                       edgecolor='none', rasterized=True, label=grp)
            _fit_line(ax, sub[x].values, sub[y].values, fit, color=c)
        ax.legend(frameon=False, fontsize=7)
    ax.set_xlabel(x); ax.set_ylabel(y)
    polish_axes(ax)
    if save:
        save_panel(fig, save, show=show)
    return fig, ax


def _fit_line(ax, xs, ys, fit='linear', color=None, n=200):
    """polyfit 拟合线（degree: linear=1, quadratic=2）+ 95% 数据范围。"""
    mask = ~(np.isnan(xs) | np.isnan(ys))
    xs, ys = xs[mask], ys[mask]
    if len(xs) < 2:
        return
    deg = {'linear': 1, 'quadratic': 2}.get(fit, 1)
    try:
        coef = np.polyfit(xs, ys, deg)
    except np.linalg.LinAlgError:
        return
    xline = np.linspace(np.nanpercentile(xs, 1), np.nanpercentile(xs, 99), n)
    yline = np.polyval(coef, xline)
    ax.plot(xline, yline, color=color or NEAR_BLACK, lw=1.2, zorder=4)


# ============================================================
# 20.37 plot_ccc_heatmap — 通讯热图（ov.pl.ccc_heatmap，无 mpl 兜底）
# ============================================================
def plot_ccc_heatmap(adata, plot_type='heatmap', ax=None, figsize=None,
                     save=None, show=None, **kwargs):
    """通讯热图：CCC 强度的 heatmap/dot/tile 多模式。ov.pl.ccc_heatmap 优先。
    需先跑 liania（adata.uns['liana_res']）。
    plot_type: 'heatmap'|'dot'|'tile'|'focused_heatmap' 等
    无 mpl 兜底（需要 liana 预计算结果）；ov 不可用时打印警告返回 None。
    """
    if not _check_ov():
        print("[smart_plot] ov.pl.ccc_heatmap 需要 omicverse，跳过")
        return None, None
    try:
        import omicverse as ov
        ov.pl.ccc_heatmap(adata, plot_type=plot_type, **kwargs)
        fig = plt.gcf()
        fig.set_size_inches(*(figsize or (3.5, 3.0)))
        if save:
            save_panel(fig, save, show=show)
        return fig, fig.axes[0] if fig.axes else None
    except Exception as e:
        print(f"[smart_plot] ov.pl.ccc_heatmap failed ({e})")
        return None, None


# ============================================================
# 20.38 plot_pca_variance — PCA 方差比（ov.pl.plot_pca_variance_ratio → mpl bar）
# ============================================================
def plot_pca_variance(adata, n_pcs=30, ax=None, figsize=None,
                      save=None, show=None, **kwargs):
    """PCA 方差比图：QC 标配（选 PCs 数）。ov.pl.plot_pca_variance_ratio 优先，mpl 兜底。"""
    import pandas as pd
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize or (3.0, 2.5))
    else:
        fig = ax.figure
    if _check_ov():
        try:
            import omicverse as ov
            ov.pl.plot_pca_variance_ratio(adata, n_pcs=n_pcs, show=False,
                                          **kwargs)
            fig_ov = plt.gcf()          # 无 ax 参数，自建 figure
            fig_ov.set_size_inches(*(figsize or (3.0, 2.5)))
            ax_ov = fig_ov.axes[0] if fig_ov.axes else ax
            polish_axes(ax_ov)
            if save:
                save_panel(fig_ov, save, show=show)
            return fig_ov, ax_ov
        except Exception as e:
            print(f"[smart_plot] ov.pl.plot_pca_variance_ratio failed ({e}), mpl fallback")
    # mpl 兜底：adata.uns['pca']/variance_ratio
    ratios = None
    if 'pca' in adata.uns and 'variance_ratio' in adata.uns['pca']:
        ratios = np.asarray(adata.uns['pca']['variance_ratio'])[:n_pcs]
    elif hasattr(adata.obsm.get('X_pca', None), 'shape'):
        # 无现成 ratio → 用特征值近似（若存在）
        if 'pca' in adata.uns and 'variance' in adata.uns['pca']:
            var = np.asarray(adata.uns['pca']['variance'])[:n_pcs]
            total = var.sum()
            ratios = var / total if total > 0 else var
    if ratios is None:
        print("[smart_plot] 无 PCA variance_ratio 可用，跳过 mpl 兜底")
        return fig, ax
    n = len(ratios)
    ax.bar(range(n), ratios, color=MORLANDI[0], alpha=0.8,
           edgecolor='white', linewidth=0.4)
    ax.axhline(ratios.mean(), color=GREY, lw=0.8, linestyle='--')
    ax.set_xticks(range(0, n, max(1, n // 10)))
    ax.set_xlabel('PC')
    ax.set_ylabel('Variance ratio')
    polish_axes(ax)
    if save:
        save_panel(fig, save, show=show)
    return fig, ax


# ============================================================
# 20.39 plot_hvg_scatter — HVG 均值-离散散点（ov → mpl）
# ============================================================
def plot_hvg_scatter(adata, ax=None, figsize=None, save=None, show=None, **kwargs):
    """HVG 均值-离散散点：QC 标配。ov.pl.highly_variable_genes_scatter 优先，mpl 兜底。"""
    import pandas as pd
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize or (3.0, 2.5))
    else:
        fig = ax.figure
    if _check_ov():
        try:
            import omicverse as ov
            ov.pl.highly_variable_genes_scatter(adata, ax=ax, show=False, **kwargs)
            polish_axes(ax)
            if save:
                save_panel(fig, save, show=show)
            return fig, ax
        except Exception as e:
            print(f"[smart_plot] ov.pl.highly_variable_genes_scatter failed ({e}), mpl fallback")
    # mpl 兜底：mean 与 dispersion 的散点，HVG 高亮
    means = adata.var['means'] if 'means' in adata.var else None
    disps = adata.var['dispersions'] if 'dispersions' in adata.var else None
    if means is None or disps is None:
        print("[smart_plot] var 中无 means/dispersions 列，跳过 mpl 兜底")
        return fig, ax
    hvg = adata.var['highly_variable'].values if 'highly_variable' in adata.var \
        else np.zeros(adata.n_vars, dtype=bool)
    ax.scatter(means[~hvg], disps[~hvg], s=4, alpha=0.5, color=GREY,
               edgecolor='none', rasterized=True, label='Non-HVG')
    ax.scatter(means[hvg], disps[hvg], s=6, alpha=0.8, color=MORLANDI[0],
               edgecolor='none', rasterized=True, label='HVG')
    ax.set_xlabel('Mean expression')
    ax.set_ylabel('Dispersion')
    ax.legend(frameon=False, fontsize=7)
    polish_axes(ax)
    if save:
        save_panel(fig, save, show=show)
    return fig, ax