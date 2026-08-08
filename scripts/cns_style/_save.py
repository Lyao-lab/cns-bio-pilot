"""_save — cns_style sub-module"""

import os
import matplotlib.pyplot as plt
import numpy as np
from ._constants import *
from ._helpers import _check_ov


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

