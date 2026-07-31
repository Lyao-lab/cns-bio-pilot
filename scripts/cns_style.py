#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
cns-bio-pilot cns_style — One-shot CNS-grade matplotlib aesthetics.

Usage:
    import sys; sys.path.insert(0, 'scripts/')
    from cns_style import set_cns_style, polish_axes, add_elegant_colorbar, \
                          safe_scanpy_plot, clean_umap_axes, apply_5plus1_palette

    set_cns_style()          # call ONCE at the top of every plotting script
    polish_axes(ax)          # apply to each panel after plotting
    add_elegant_colorbar(mappable, ax, label='log2 Expression')
    safe_scanpy_plot(sc.pl.umap, adata, color='ct', ax=ax, show=False)

Philosophy:
    figure_aesthetics.md = compliance (avoid errors)
    figure_aesthetics_advanced.md = positive design (create beauty)
    THIS file = the code that implements both.

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
MORLANDI = ['#88C0D0', '#BF616A', '#A3BE8C', '#D08770',
            '#B48EAD', '#EBCB8B', '#5E81AC', '#D8DEE9']

OKABE_ITO = ['#E69F00', '#56B4E9', '#009E73', '#F0E442',
             '#0072B2', '#D55E00', '#CC79A7', '#000000']

MUTED = '#C8CDD3'          # non-focus clusters
NEAR_BLACK = '#2E3440'     # axis/text color (Morlandi polar-night)
GREY = '#4C566A'           # annotation/subtle text (Morlandi grey)

# Sequential: blue-yellow-red (low-saturation, bioinformatics consensus)
EXPR_CMAP = LinearSegmentedColormap.from_list('byr_morlandi',
    ['#5E81AC', '#8FBCD4', '#ECEFF4', '#D08770', '#9B5A5A'], N=256)

# Diverging: blue-white-red (0=white midpoint)
DIVERGING_CMAP = LinearSegmentedColormap.from_list('log2fc',
    ['#2C5F8D', '#88C0D0', '#FFFFFF', '#D08770', '#8B2C2C'], N=256)


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

    plt.rcParams.update({
        # --- Font (modular scale) ---
        'font.family': 'sans-serif',
        'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
        'font.size': F,                              # 8pt (tick labels)
        'axes.titlesize': int(F * S**2),             # 10pt → 12pt
        'axes.labelsize': int(F * S**2),             # 10pt
        'xtick.labelsize': F,                        # 8pt
        'ytick.labelsize': F,                        # 8pt
        'legend.fontsize': int(F * S),               # 9.6 → 10pt
        'figure.titlesize': int(F * S**3),           # 14pt

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

        # --- Legend ---
        'legend.frameon': False,
        'legend.borderaxespad': 0.3,

        # --- Title ---
        'axes.titlepad': 8,
    })


# ============================================================
# 2. polish_axes(ax) — per-panel finishing touch
# ============================================================
def polish_axes(ax, keep_spines=('left', 'bottom'), subtle_grid=True):
    """CNS-grade axis styling: L-frame, outward ticks, subtle gridlines.

    Apply to EVERY panel after plotting. For UMAP/tSNE use clean_umap_axes() instead.
    """
    # Spine hierarchy
    for spine in ax.spines.values():
        spine.set_visible(False)
    for spine_name in keep_spines:
        ax.spines[spine_name].set_visible(True)
        ax.spines[spine_name].set_linewidth(0.8)
        ax.spines[spine_name].set_color(NEAR_BLACK)

    # Outward ticks, no tick marks
    ax.tick_params(direction='out', length=0, labelsize=8, colors=NEAR_BLACK)

    # Subtle horizontal reference lines
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
                      fraction=0.046,    # width relative to axes (slim)
                      pad=0.04,         # gap from axes
                      aspect=20,        # height/width ratio (tall & slim)
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
    This saves and restores them around the call.
    """
    saved = plt.rcParams.copy()
    result = plot_func(*args, **kwargs)
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
# 9. condition_colors() — temperature narrative
# ============================================================
CONDITION_COLORS = {
    'Normal': '#88C0D0',    # frost-blue = quiet
    'Disease': '#BF616A',   # dark-red = active
    'Treated': '#A3BE8C',   # moss-green = recovery
    'Control': '#88C0D0',   # cool
    'Stimulated': '#D08770', # warm
}


# ============================================================
# 9b. Recipe helpers (figure_recipes.md — high-frequency decisions)
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
    """Return color dict for volcano plot (temperature narrative).

    Usage:
        colors = volcano_colors()
        ax.scatter(..., color=colors['up'])    # significant upregulated
        ax.scatter(..., color=colors['down'])  # significant downregulated
        ax.scatter(..., color=colors['ns'])    # not significant
    """
    return {
        'up': '#BF616A',     # warm red = active/upregulated
        'down': '#5E81AC',   # cool blue = suppressed/downregulated
        'ns': '#D8DEE9',     # grey = not significant
        'ns_alpha': 0.4,     # non-sig points are faint
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
        'umap': (4.5, 4.0),
        'volcano': (4.0, 3.5),
        'feature': (3.0, 3.0),      # per-gene panel in a grid
        'spatial': (5.0, 4.5),
        'chord': (5.0, 5.0),
        'paga': (3.5, 3.0),
    }

    if chart_type in recipes:
        w, h = recipes[chart_type]
        return (w * scale, h * scale)
    elif chart_type == 'heatmap' and n_x and n_y:
        w = n_x * 0.18 + 2.0   # +2 for dendrogram + colorbar
        h = n_y * 0.35
        return (w * scale, h * scale)
    elif chart_type == 'dotplot' and n_x and n_y:
        w = n_x * 0.3 + 2.0
        h = n_y * 0.3 + 1.0
        return (w * scale, h * scale)
    elif chart_type in ('violin', 'bar') and n_x:
        w = n_x * 0.7 + 1.0
        h = 3.5
        return (w * scale, h * scale)
    else:
        return (5.0 * scale, 4.0 * scale)  # safe default


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
