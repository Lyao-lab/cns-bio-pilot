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
# 8c. assert_no_text_overlap() — 画布级重叠硬断言（finalize 的 strict 版）
#     （fetal_heart 15+ 脚本手写 harness 的统一封装，2026-09 实战回灌）
# ============================================================

def assert_no_text_overlap(fig, include_ticks=True, include_legend=True,
                           check_bounds=False, tol_px=0.5,
                           raise_on_fail=True, verbose=True):
    """渲染后逐对检查 fig/ax 文字 bbox：重叠即 raise（把"审图"变成 CI）。

    覆盖 finalize_figure 不查的对象：fig.texts（面板字母/标题/脚注）、ax.title、
    tick labels、legend。tol_px 容忍贴边接触；check_bounds=True 时另查越出画布
    （save_panel 用 bbox_inches='tight' 会自动扩边，故默认关）。

    Args:
        fig: matplotlib Figure
        include_ticks: 检查 tick label 两两重叠（长旋转标签挤压时能抓到）
        include_legend: legend 作为整体 bbox 参与检查
        raise_on_fail: True → AssertionError 列出全部重叠对；False → 只返回 issues 列表

    Usage:
        stamp_panel(fig, 'a', 'Title', 'methods note ...')
        assert_no_text_overlap(fig)          # 保存前的机械验收门
    """
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    items = []

    def _add(lbl, artist):
        try:
            if artist.get_text().strip():
                items.append((lbl, artist))
        except Exception:
            pass

    for t in fig.texts:
        _add(f"fig.text '{t.get_text()[:24]}'", t)
    for k, ax in enumerate(fig.axes):
        if ax.title.get_text():
            items.append((f"ax{k} title '{ax.title.get_text()[:24]}'", ax.title))
        for nm, lab in (('xlabel', ax.xaxis.label), ('ylabel', ax.yaxis.label)):
            if lab.get_text():
                items.append((f'ax{k} {nm}', lab))
        for t in ax.texts:
            _add(f"ax{k} text '{t.get_text()[:24]}'", t)
        if include_ticks:
            for t in list(ax.get_xticklabels()) + list(ax.get_yticklabels()):
                _add(f"ax{k} tick '{t.get_text()[:24]}'", t)
        if include_legend and ax.get_legend() is not None:
            items.append((f'ax{k} legend', ax.get_legend()))

    def _isect(a, b):
        w = min(a.x1, b.x1) - max(a.x0, b.x0)
        h = min(a.y1, b.y1) - max(a.y0, b.y0)
        return (w > tol_px and h > tol_px)

    issues = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            try:
                bi = items[i][1].get_window_extent(renderer=r)
                bj = items[j][1].get_window_extent(renderer=r)
            except Exception:
                continue
            if _isect(bi, bj):
                issues.append(f"文字重叠: {items[i][0]} ↔ {items[j][0]}")

    if check_bounds:
        fb = fig.bbox
        for lbl, artist in items:
            try:
                b = artist.get_window_extent(renderer=r)
            except Exception:
                continue
            if b.x0 < fb.x0 - tol_px or b.x1 > fb.x1 + tol_px or \
               b.y0 < fb.y0 - tol_px or b.y1 > fb.y1 + tol_px:
                issues.append(f"越出画布: {lbl}")

    if issues:
        msg = "[assert_no_text_overlap] " + "; ".join(issues)
        if raise_on_fail:
            raise AssertionError(msg)
        if verbose:
            print("⚠️  " + msg)
    return issues


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
        fmt: 'pdf' | 'png' | 'svg'（默认 'pdf'）；支持 '+' 连接的多格式一次性输出，
             如 'png+pdf'（先 png 供自检、后 pdf 矢量交付，close 前完成全部写出）
        show: None（默认）→ 自动检测：Jupyter notebook 中为 True（savefig 后不 close，
              figure 在 cell 输出显示）；纯脚本中为 False（savefig 后 close）。
              True → 强制保留显示（notebook 场景）；
              False → 强制 close（脚本批处理场景）

    Returns:
        str 单格式时的保存路径；多格式时为路径列表

    Usage:
        save_panel(fig, 'A_umap')              # → panels/A_umap.pdf
        save_panel(fig, 'A_umap', fmt='png+pdf')  # → panels/A_umap.png + .pdf
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
    fmts = [f.strip() for f in str(fmt).split('+') if f.strip()] or [fmt]
    paths = []
    for f in fmts:
        # name 含路径分隔符 → 视为完整路径（不再拼 outdir）；否则拼 outdir/name
        if '/' in name or '\\' in name:
            path = f'{name}.{f}'
            out_dir = os.path.dirname(path)
            if out_dir:
                os.makedirs(out_dir, exist_ok=True)
        else:
            os.makedirs(outdir, exist_ok=True)
            path = f'{outdir}/{name}.{f}'

        dpi = plt.rcParams['savefig.dpi'] if journal else 300
        fig.savefig(path, dpi=dpi, bbox_inches='tight', pad_inches=0.1)
        # 空文件检查（源自 figures4papers 的 run-验证契约）：输出写穿 → 立即报错
        if os.path.getsize(path) == 0:
            raise RuntimeError(f"[save_panel] 输出文件为空: {path}")
        paths.append(path)
    if not show:
        plt.close(fig)
    print(f"Saved: {' + '.join(paths)} (dpi={dpi})" + (" [figure displayed in notebook]" if show else ""))
    return paths[0] if len(paths) == 1 else paths


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

