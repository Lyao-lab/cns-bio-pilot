"""_style — cns_style sub-module"""

import matplotlib.pyplot as plt
import matplotlib as mpl
from ._constants import *


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
