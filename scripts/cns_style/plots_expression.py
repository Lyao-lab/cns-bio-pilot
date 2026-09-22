"""plots_expression — cns_style sub-module"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from ._constants import *
from ._axes import *
from ._layout import *
from ._save import *
from ._annotation import *
from ._helpers import *
from ._helpers import _check_ov, _adata_to_tidy, _resolve_group_mask, _resolve_signal, _lighten_color
from ._layout import _fs, _FIG_SCALE


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
                         plot_genes_num=0)   # ov 标注无防撞 → 关掉，统一走下方
            fig_ov = plt.gcf()
            fig_ov.set_size_inches(*recipe_figsize('volcano'))
            ax = fig_ov.axes[0] if fig_ov.axes else ax
            fig = fig_ov
            up = (de[pval_name] < sig_pval) & (de[fc_name] > sig_fc)
            dn = (de[pval_name] < sig_pval) & (de[fc_name] < -sig_fc)
            _annotate_volcano_top(ax, de, up, dn, fc_name, pval_name,
                                  annotate_top)
            if save:                          # 修复：ov 路径也要走 save_panel
                save_panel(fig, save, show=show, outdir=kwargs.pop("outdir", "panels"),
                    fmt=kwargs.pop("fmt", "pdf"))
            return fig, ax  # ov 自建 figure，直接返回
        except Exception as e:
            print(f"[smart_plot] ov.pl.volcano failed ({e}), mpl fallback")
    _volcano_mpl(de, pval_name, fc_name, ax, annotate_top, sig_pval, sig_fc)
    polish_axes(ax)
    if save:
        save_panel(fig, save, show=show, outdir=kwargs.pop("outdir", "panels"),
                    fmt=kwargs.pop("fmt", "pdf"))
    return fig, ax



def _annotate_volcano_top(ax, de, up, dn, fc_name, pval_name, annotate_top,
                          fontsize=7):
    """火山图 top 基因防撞标注：up/down 各取 |FC| 最大 N 个，ax.text 落点后
    layout_labels 斥力求解开（白晕字，无箭头——保持 tightbbox 干净）。"""
    from ._annotation import layout_labels
    import matplotlib.patheffects as pe
    texts = []
    y_max = (-np.log10(de[pval_name].clip(lower=1e-300))).max()
    for mask in (up, dn):
        sub = de.loc[mask]
        if len(sub) == 0:
            continue
        n = min(annotate_top, len(sub))
        top = sub.reindex(sub[fc_name].abs().sort_values(ascending=False)
                          .index).head(n)
        for idx, r in top.iterrows():
            gene = r['gene'] if 'gene' in r.index else idx
            x = float(r[fc_name])
            y = -np.log10(max(float(r[pval_name]), 1e-300))
            t = ax.text(x, y + 0.055 * y_max, str(gene), fontsize=fontsize,
                        ha='center', va='bottom', color=NEAR_BLACK,
                        path_effects=[pe.withStroke(linewidth=2.5,
                                                    foreground='white')],
                        zorder=6)
            texts.append(t)
    if texts:
        # 首选 adjustText（点+标签联合斥力，本职工具；compat 可选依赖）
        try:
            from adjustText import adjust_text
            sig = up | dn
            xs = de.loc[sig, fc_name].to_numpy(float)
            ys = (-np.log10(de.loc[sig, pval_name]
                            .clip(lower=1e-300))).to_numpy(float)
            if len(xs) > 1500:
                _idx = np.random.default_rng(0).choice(len(xs), 1500,
                                                       replace=False)
                xs, ys = xs[_idx], ys[_idx]
            adjust_text(texts, x=xs, y=ys, ax=ax,
                        arrowprops=dict(arrowstyle='-', lw=0.4, color=GREY),
                        expand=(1.35, 1.6), force_text=(0.4, 0.7),
                        force_static=(0.5, 0.9),
                        ensure_inside_axes=True)
            return texts
        except ImportError:
            pass
        layout_labels(ax.figure, ax, texts)
        # 点感知避让：实测 bbox 压到显著点 → 上移一格；越左脊 → 右移（≤3 轮）
        fig = ax.figure
        sig_mask = up | dn
        px_ = de.loc[sig_mask, fc_name].to_numpy(float)
        py_ = (-np.log10(de.loc[sig_mask, pval_name]
                         .clip(lower=1e-300))).to_numpy(float)
        for t in texts:
            for _ in range(3):
                fig.canvas.draw()
                r_ = fig.canvas.get_renderer()
                inv = ax.transData.inverted()
                b = t.get_window_extent(renderer=r_)
                (dx0, dy0), (dx1, dy1) = inv.transform(
                    [(b.x0, b.y0), (b.x1, b.y1)])
                xl, xh = ax.get_xlim()
                hit_pt = bool(((px_ > dx0) & (px_ < dx1) &
                               (py_ > dy0) & (py_ < dy1)).any())
                out_left = dx0 < xl + 0.015 * (xh - xl)
                if not (hit_pt or out_left):
                    break
                cx, cy = t.get_position()
                if hit_pt:
                    cy += (dy1 - dy0) * 1.15
                if out_left:
                    cx += (xl + 0.02 * (xh - xl)) - dx0
                t.set_position((cx, cy))

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
    _annotate_volcano_top(ax, de, up, dn, fc_name, pval_name, annotate_top)
    ax.set_xlabel(r'log$_2$(Fold Change)')
    ax.set_ylabel(r'$-$log$_{10}$(adjusted P)')


# ============================================================
# 20.3 plot_dotplot — 点图（ov.pl.dotplot → mpl scatter 矩阵）
# ============================================================


# ============================================================
# 20.3 plot_dotplot — 点图（ov.pl.dotplot → mpl scatter 矩阵）
# ============================================================

def plot_dotplot(adata, var_names, groupby='celltype', ax=None, figsize=None,
                 save=None, standard_scale='var', show=None, **kwargs):
    """Dotplot：sc.pl.dotplot 优先（标准色条/尺寸图例），ov.pl.dotplot 次之
    （ov 色条在部分环境渲染错位，2026-09 视觉验收实证），mpl scatter 矩阵兜底。"""
    try:
        import scanpy as sc
        sc.pl.dotplot(adata, var_names, groupby=groupby,
                      standard_scale=standard_scale, dendrogram=False,
                      show=False, ax=ax)
        fig_sc = plt.gcf()
        # 保持 scanpy 原生尺寸（强制 resize 会在顶部留大片空白，2026-09 实证）
        for a_ in fig_sc.axes:
            a_.tick_params(labelsize=6)   # 尺寸图例刻度小一号防粘连
        # DotPlot 默认给 dendrogram/分类条预留头部（无 dendrogram 时主轴只占
        # 下半幅 → 顶部大片空白）：把主点阵轴拉伸到与图例轴同高
        main_ax = max(fig_sc.axes,
                      key=lambda a_: a_.get_position().width *
                      a_.get_position().height)
        top_target = max(a_.get_position().y1 for a_ in fig_sc.axes)
        p_main = main_ax.get_position()
        if p_main.y1 < top_target - 0.02:
            main_ax.set_position([p_main.x0, p_main.y0, p_main.width,
                                  top_target - p_main.y0])
        if save:
            save_panel(fig_sc, save, show=show,
                       outdir=kwargs.pop('outdir', 'panels'),
                       fmt=kwargs.pop('fmt', 'pdf'))
        return fig_sc, fig_sc.axes[0] if fig_sc.axes else None
    except Exception as e:
        print(f"[smart_plot] sc.pl.dotplot failed ({e}), try ov/mpl")
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
                save_panel(fig_ov, save, show=show, outdir=kwargs.pop("outdir", "panels"),
                    fmt=kwargs.pop("fmt", "pdf"))
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
        save_panel(fig, save, show=show, outdir=kwargs.pop("outdir", "panels"),
                    fmt=kwargs.pop("fmt", "pdf"))
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
                save_panel(fig_ov, save, show=show, outdir=kwargs.pop("outdir", "panels"),
                    fmt=kwargs.pop("fmt", "pdf"))
            return fig_ov, axes[0]
        except Exception as e:
            print(f"[smart_plot] ov.pl.violin failed ({e}), mpl fallback")
    for row, g in enumerate(keys):
        _violin_mpl(adata, g, groupby, axes[row])
    fig = axes[0].figure
    polish_axes(axes[-1])
    if save:
        save_panel(fig, save, show=show, outdir=kwargs.pop("outdir", "panels"),
                    fmt=kwargs.pop("fmt", "pdf"))
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
        save_panel(fig, save, show=show, outdir=kwargs.pop("outdir", "panels"),
                    fmt=kwargs.pop("fmt", "pdf"))
    return fig, ax


# ============================================================
# 20.6 plot_spatial — 空间图（ov → squidpy → mpl scatter）
# ============================================================


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
        save_panel(fig, save, show=show, outdir=kwargs.pop("outdir", "panels"),
                    fmt=kwargs.pop("fmt", "pdf"))
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
                save_panel(fig_ov, save, show=show, outdir=kwargs.pop("outdir", "panels"),
                    fmt=kwargs.pop("fmt", "pdf"))
            return fig_ov, ax_ov
        except Exception as e:
            print(f"[smart_plot] ov.pl.boxplot failed ({e}), mpl fallback")
    groups = adata.obs[groupby].astype('category').cat.categories
    for row, g in enumerate(keys):
        _boxplot_mpl(adata, g, groupby, groups, axes[row])
    fig = axes[0].figure
    polish_axes(axes[-1])
    if save:
        save_panel(fig, save, show=show, outdir=kwargs.pop("outdir", "panels"),
                    fmt=kwargs.pop("fmt", "pdf"))
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
