# -*- coding: utf-8 -*-
"""领域特色图型（plots_domain）—— 源自 2024-2026 年 15 领域 506 篇 CNS 文献调研
（D:\\workspace\\lit_survey\\，详见 references/figure_templates.md §5 图型频率表）。

本模块收跨领域**中高频**但此前 cns_style 缺失的图型：
  plot_sankey          状态转换/命运流 alluvial（肾 PT 转换、心血管治疗 alluvial、
                       衰老最优传输矩阵、发育命运流；频率 ~15-25% 论文）
  plot_cnv_heatmap     inferCNV 式基因组 CNV 热图（实体瘤高频：区分恶性/非恶性、
                       克隆-微环境耦合；肿瘤领域 ~40% 论文）
  plot_axis_gradient   信号沿连续组织轴/距离的梯度曲线（肝 zonation、皮质-髓质肾轴、
                       病理-分子距离梯度、肿瘤边界带、母胎界面距离分箱；跨领域通用）
  plot_clone_expansion 克隆扩增追踪（免疫/血液/感染：TCR 克隆-表型-空间三连图、
                       AML 克隆演化组合拳）

更低频的领域特色图（fishplot/克隆树/oncoprint/Voronoi/3D 重建/空间时钟等）
不建代码模板，选型与外部工具指引见 plotting_reference.md §3.45（低频-降优先度）。
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgba
from matplotlib.path import Path
from matplotlib.patches import PathPatch

from ._constants import *
from ._axes import *
from ._layout import *
from ._save import *
from ._annotation import *

__all__ = ['plot_sankey', 'plot_cnv_heatmap', 'plot_axis_gradient',
           'plot_clone_expansion']


# ============================================================
# plot_sankey — 两阶段状态转换 alluvial（命运流/转变矩阵可视化）
# ============================================================
def plot_sankey(flows, order_top=None, order_bottom=None, min_flow=0.0,
                node_w=0.045, gap=0.012, alpha=0.45, label_nodes=True,
                ax=None, figsize=None, save=None, show=None, **kwargs):
    """两阶段 Sankey/alluvial：转移矩阵 → 左右节点 + 贝塞尔 ribbon。

    flows: 转移矩阵 DataFrame（index=source 状态, columns=target 状态,
           值=流量——PAGA transition / CellRank fate probability / 最优传输
           转变矩阵 / 治疗 before→after 计数均为此形态）。
    min_flow: 流量低于该值（占总流量比例）的 ribbon 不画，去毛刺。
    节点按流量降序排布（order_top/order_bottom 可覆盖）；ribbon 按 source 着色。
    深度 ≥3 阶段的命运流请拆成多个两阶段面板（CNS 惯例）。
    """
    mat = flows.astype(float)
    out_sum = mat.sum(axis=1)
    in_sum = mat.sum(axis=0)
    srcs = order_top or out_sum.sort_values(ascending=False).index.tolist()
    tgts = order_bottom or in_sum.sort_values(ascending=False).index.tolist()
    mat = mat.loc[[s for s in srcs if out_sum.get(s, 0) > 0],
                  [t for t in tgts if in_sum.get(t, 0) > 0]]
    total = mat.values.sum()
    if total <= 0:
        raise ValueError("plot_sankey: 流量全为 0")
    srcs, tgts = list(mat.index), list(mat.columns)
    n_s, n_t = len(srcs), len(tgts)
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize or (4.6, 3.4))
    else:
        fig = ax.figure
    span = 1.0 - gap * (n_s - 1)
    sh = span * out_sum[srcs].values / total
    sy = np.cumsum(np.concatenate([[0], sh])) + gap * np.arange(n_s + 1)
    span = 1.0 - gap * (n_t - 1)
    th = span * in_sum[tgts].values / total
    ty = np.cumsum(np.concatenate([[0], th])) + gap * np.arange(n_t + 1)
    palette = MORLANDI_EXTENDED
    src_color = {s: palette[i % len(palette)] for i, s in enumerate(srcs)}
    x0, x1 = 0.0, 1.0
    off_l = off_r = 0.0
    for i, s in enumerate(srcs):
        for j, t in enumerate(tgts):
            f = mat.loc[s, t] / total
            if f < min_flow or f <= 0:
                continue
            y0t, y0b = sy[i] - off_l, sy[i] - off_l - f
            y1t, y1b = ty[j] + off_r, ty[j] + off_r + f
            cx = 0.5
            verts = [(x0 + node_w, y0t), (cx, y0t), (cx, y1t), (x1 - node_w, y1t),
                     (x1 - node_w, y1b), (cx, y1b), (cx, y0b), (x0 + node_w, y0b),
                     (x0 + node_w, y0t)]
            codes = [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4,
                     Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4,
                     Path.CLOSEPOLY]
            ax.add_patch(PathPatch(Path(verts, codes), facecolor=src_color[s],
                                   edgecolor='none', alpha=alpha, zorder=2))
            off_l += f
        off_l = 0.0
    # 节点矩形（source 收流量自上而下、target 展开自上而下，语义一致）
    off = np.zeros(n_t)
    for i, s in enumerate(srcs):
        ax.add_patch(plt.Rectangle((x0, sy[i + 1] - sh[i]), node_w, sh[i],
                                   facecolor=src_color[s], edgecolor='white',
                                   lw=0.4, zorder=3))
    for j, t in enumerate(tgts):
        ax.add_patch(plt.Rectangle((x1 - node_w, ty[j]), node_w, th[j],
                                   facecolor='#b8bcc2', edgecolor='white',
                                   lw=0.4, zorder=3))
    if label_nodes:
        for i, s in enumerate(srcs):
            ax.text(x0 - 0.02, (sy[i] + sy[i + 1]) / 2, f'{s}',
                    ha='right', va='center', fontsize=7.5, color=NEAR_BLACK)
        for j, t in enumerate(tgts):
            ax.text(x1 + 0.02, (ty[j] + ty[j + 1]) / 2, f'{t}',
                    ha='left', va='center', fontsize=7.5, color=NEAR_BLACK)
    ax.set_xlim(-0.42, 1.42)
    ax.set_ylim(1.0 + 2 * gap, -2 * gap)
    ax.axis('off')
    if save:
        save_panel(fig, save, show=show,
                   outdir=kwargs.pop("outdir", "panels"),
                   fmt=kwargs.pop("fmt", "pdf"))
    return fig, ax


# ============================================================
# plot_cnv_heatmap — inferCNV 式基因组 CNV 热图（细胞 × 基因组序基因）
# ============================================================
def plot_cnv_heatmap(cnv, chrom=None, groups=None, cmap=None,
                     vmin=-1.5, vmax=1.5, group_palette=None,
                     ax=None, figsize=None, save=None, show=None, **kwargs):
    """inferCNV 式 CNV 热图：行=细胞（按分组排布），列=按基因组位置排序的基因，
    染色体边界白线分隔 + 顶部染色体号注释；左侧可选分组色条。

    cnv:    DataFrame（index=细胞, columns=基因, 值=推断 CNV——inferCNV/copyKAT
            的 expr 值或 log-ratio；行顺序=展示顺序，先按分组排序再传入）。
    chrom:  与 columns 对齐的染色体标签 Series（如 var['chrom']）——提供时画
            染色体分隔线与顶注；缺省假设已按位置排序、无分隔线。
    groups: 与 index 对齐的分组标签 Series（恶性/非恶性、样本、克隆）——提供时
            左侧画分组色条。
    cmap 默认 DIVERGING_CMAP（0=白，红=扩增，蓝=缺失，与 inferCNV 惯例一致）。
    """
    df = cnv
    if cmap is None:
        cmap = DIVERGING_CMAP
    n_c, n_g = df.shape
    h = figsize[1] if figsize else min(0.0042 * n_c + 1.0, 9.0)
    w = figsize[0] if figsize else max(5.0, 0.012 * n_g)
    if ax is None:
        fig, ax = plt.subplots(figsize=(w, h))
    else:
        fig = ax.figure
    if groups is not None:
        ax_grp = ax.inset_axes([-0.055, 0.0, 0.018, 1.0], transform=ax.transAxes)
        uniq = list(pd.unique(groups))
        pal = group_palette or {u: MORLANDI_EXTENDED[i % len(MORLANDI_EXTENDED)]
                                for i, u in enumerate(uniq)}
        gcol = groups.map(pal).to_numpy()
        rgba = np.array([[to_rgba(c) for c in gcol]], dtype=float).reshape(-1, 1, 4)
        ax_grp.imshow(rgba, aspect='auto', interpolation='nearest')
        ax_grp.set_xticks([])
        ax_grp.set_yticks([])
        for sp in ax_grp.spines.values():
            sp.set_visible(False)
    im = ax.imshow(df.values, aspect='auto', interpolation='nearest',
                   cmap=cmap, vmin=vmin, vmax=vmax, rasterized=True)
    if chrom is not None:
        ch = chrom.reindex(df.columns).to_numpy()
        bounds = np.flatnonzero(np.r_[True, ch[1:] != ch[:-1]])
        for b in bounds[1:]:
            ax.axvline(b - 0.5, color='white', lw=0.8)
        labels = [ch[b] for b in bounds]
        mids = [(bounds[k] + (bounds[k + 1] if k + 1 < len(bounds) else n_g)) / 2
                for k in range(len(bounds))]
        ax.set_xticks(mids)
        ax.set_xticklabels(labels, fontsize=6.5)
    else:
        ax.set_xticks([])
    ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_visible(False)
    cb = fig.colorbar(im, ax=ax, orientation='horizontal',
                      fraction=0.046, pad=0.08, shrink=0.7)
    cb.set_label('Inferred CNV (log-ratio)', fontsize=7)
    cb.ax.tick_params(labelsize=6)
    cb.outline.set_visible(False)
    if save:
        save_panel(fig, save, show=show,
                   outdir=kwargs.pop("outdir", "panels"),
                   fmt=kwargs.pop("fmt", "pdf"))
    return fig, ax


# ============================================================
# plot_axis_gradient — 信号沿连续组织轴/距离的梯度曲线
# ============================================================
def plot_axis_gradient(data, x, y, hue, norm='each', window=0.1,
                       landmark=True, point_threshold=4000, point_s=2,
                       colors=None, ax=None, figsize=None, save=None,
                       show=None, **kwargs):
    """信号沿连续轴（解剖轴/距离/pseudotime）的梯度曲线 + 分位带。

    data: tidy DataFrame；x=轴坐标（µm 距离、zone 位置 0-1、皮层深度、
          距肿瘤边界/血管/母胎界面距离）；y=信号（表达/score/比例）；hue=信号名。
    norm: 'each'=每信号 min-max 归一（肝 zonation/多基因比较的标准形态，可同图
          比形状）；'global'=全局归一；None=原始值（同量纲信号）。
    每信号画：散点（超点自动降密度）+ 局部平滑曲线（LOWESS 优先，滑窗中位兜底）
    + p25-p75 带。landmark=True 时 x=0 画虚线（解剖标志原点：中央静脉/血管/
    肿瘤边界/母胎界面——CNS 距离梯度论文标准动作）。
    """
    df = data.copy()
    xname, yname, hname = x, y, hue
    if norm == 'each':
        for h, idx in df.groupby(hname).groups.items():
            lo, hi = df.loc[idx, yname].min(), df.loc[idx, yname].max()
            df.loc[idx, yname] = (df.loc[idx, yname] - lo) / (hi - lo + 1e-9)
    elif norm == 'global':
        lo, hi = df[yname].min(), df[yname].max()
        df[yname] = (df[yname] - lo) / (hi - lo + 1e-9)
    hues = list(pd.unique(df[hname]))
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize or (4.2, 3.0))
    else:
        fig = ax.figure
    palette = colors or {h: MORLANDI_EXTENDED[i % len(MORLANDI_EXTENDED)]
                         for i, h in enumerate(hues)}
    try:
        from statsmodels.nonparametric.smoothers_lowess import lowess
        have_sm = True
    except ImportError:
        have_sm = False
    for h in hues:
        d = df[df[hname] == h].sort_values(xname)
        xs, ys = d[xname].to_numpy(float), d[yname].to_numpy(float)
        c = palette.get(h, MUTED)
        if len(xs) > point_threshold:
            idx = np.random.default_rng(0).choice(
                len(xs), point_threshold, replace=False)
            ax.scatter(xs[idx], ys[idx], s=point_s, alpha=0.10, color=c,
                       edgecolors='none', zorder=2)
        else:
            ax.scatter(xs, ys, s=point_s + 1, alpha=0.15, color=c,
                       edgecolors='none', zorder=2)
        if have_sm:
            sm_y = lowess(ys, xs, frac=max(window, 5 / max(len(xs), 5)))[:, 1]
        else:
            s = pd.Series(ys).rolling(max(5, int(window * len(xs))),
                                      center=True, min_periods=1).median()
            sm_y = s.to_numpy()
        ax.plot(xs, sm_y, color=c, lw=1.4, zorder=4, label=h,
                solid_capstyle='round')
        q25 = pd.Series(ys).rolling(max(5, int(window * len(xs))), center=True,
                                    min_periods=1).quantile(0.25).to_numpy()
        q75 = pd.Series(ys).rolling(max(5, int(window * len(xs))), center=True,
                                    min_periods=1).quantile(0.75).to_numpy()
        ax.fill_between(xs, q25, q75, color=c, alpha=0.12, lw=0, zorder=3)
    if landmark:
        ax.axvline(0, color=GREY, lw=0.8, ls='--', alpha=0.7, zorder=1)
        ax.text(0.01, 1.02, kwargs.pop('landmark_label', 'landmark'),
                transform=ax.get_yaxis_transform(), fontsize=6.5, color=GREY,
                ha='left', va='bottom')
    ax.set_xlabel(kwargs.pop('xlabel', xname), fontsize=8)
    ax.set_ylabel(kwargs.pop('ylabel', yname if norm is None else
                             'Normalized ' + yname), fontsize=8)
    polish_axes(ax)
    if len(hues) <= 6:
        ax.legend(frameon=False, fontsize=7, loc='upper right')
    if save:
        save_panel(fig, save, show=show,
                   outdir=kwargs.pop("outdir", "panels"),
                   fmt=kwargs.pop("fmt", "pdf"))
    return fig, ax


# ============================================================
# plot_clone_expansion — 克隆扩增追踪（TCR/BCR/肿瘤克隆）
# ============================================================
def plot_clone_expansion(clone_df, clone_col, group_col, mode='composition',
                         bins=((1, 1, 'singleton'), (2, 9, 'small'),
                               (10, 99, 'medium'), (100, np.inf, 'large')),
                         order=None, top_n=10, by='cells', colors=None,
                         ax=None, figsize=None, save=None, show=None,
                         **kwargs):
    """克隆扩增追踪（免疫/血液/感染领域的"克隆-表型-空间"三连图之一）。

    clone_df: 每行=一个克隆在一个分组中的记录，列含 clone_col（克隆 ID）/
              group_col（细胞类型/时间点/组织）/ size（该克隆在该组的细胞数）。
              若传每细胞一行（无 size 列），内部自动 groupby 计数。
    mode='composition'（默认）：分组堆叠柱——每组细胞按克隆大小分类
              （singleton/small/medium/large，bins 可调）着色堆叠，
              展示"哪群在克隆性扩增"（CNS 免疫论文标准形态）。
    mode='track'：top_n 大克隆跨组折线追踪（端点直标克隆名；时间点/组织演化）。
    by='cells'|'clones'：堆叠分子用细胞占比（默认）或克隆数占比。
    """
    df = clone_df.copy()
    if 'size' not in df.columns:
        size = df.groupby([clone_col, group_col]).size().rename('size').reset_index()
    else:
        size = df[[clone_col, group_col, 'size']].copy()
    groups = list(order) if order else list(pd.unique(size[group_col]))
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize or (0.9 * len(groups) + 1.6, 3.0))
    else:
        fig = ax.figure
    if mode == 'composition':
        rows = []
        for g in groups:
            sub = size[size[group_col] == g]
            total_units = sub['size'].sum() if by == 'cells' else len(sub)
            for lo, hi, name in bins:
                m = sub[(sub['size'] >= lo) & (sub['size'] <= hi)]
                frac = (m['size'].sum() if by == 'cells' else len(m)) / \
                    max(total_units, 1)
                rows.append({'group': g, 'class': name, 'frac': frac})
        comp = pd.DataFrame(rows)
        classNames = [b[2] for b in bins]
        default = ['#c7cdd6', '#9aa5b1', '#7f97a8', MORLANDI[1]]
        pal = colors or {c: default[i % len(default)]
                         for i, c in enumerate(classNames)}
        bottom = np.zeros(len(groups))
        for cname in classNames:
            vals = comp[comp['class'] == cname]['frac'].to_numpy()
            ax.bar(range(len(groups)), vals, bottom=bottom, width=0.62,
                   color=pal.get(cname, MUTED), label=cname,
                   edgecolor='white', lw=0.4)
            bottom += vals
        ax.set_xticks(range(len(groups)))
        ax.set_xticklabels(groups, fontsize=8)
        ax.set_ylabel(f'Fraction of {by}', fontsize=8)
        ax.set_ylim(0, 1)
        polish_axes(ax, variant='bar', grid_axis='y')
        ax.legend(frameon=False, fontsize=7, ncol=1, loc='upper left',
                  bbox_to_anchor=(1.02, 1.0))
    elif mode == 'track':
        wide = size.pivot_table(index=clone_col, columns=group_col,
                                values='size', aggfunc='sum', fill_value=0)
        wide = wide.reindex(columns=[g for g in groups if g in wide.columns])
        top = wide.sum(axis=1).sort_values(ascending=False).head(top_n).index
        wide = wide.loc[top]
        palette = colors or {c: MORLANDI_EXTENDED[i % len(MORLANDI_EXTENDED)]
                             for i, c in enumerate(wide.index)}
        for i, c in enumerate(wide.index):
            row = wide.loc[c].values.astype(float)
            ax.plot(range(wide.shape[1]), row, color=palette[c], lw=1.6,
                    marker='o', ms=3, zorder=3)
        labels = [f'{c} (n={int(wide.loc[c].iloc[-1])})' for c in wide.index]
        direct_label(ax, wide.iloc[:, -1].values, labels,
                     x=wide.shape[1] - 1, side='right', gap_pt=11, fontsize=6.5)
        ax.set_xticks(range(wide.shape[1]))
        ax.set_xticklabels(list(wide.columns), fontsize=8)
        ax.set_ylabel('Clone size (cells)', fontsize=8)
        ax.set_xlim(-0.3, wide.shape[1] - 0.55)
        polish_axes(ax, variant='bar', grid_axis='y')
    else:
        raise ValueError(f"未知 mode: {mode}（'composition' | 'track'）")
    if save:
        save_panel(fig, save, show=show,
                   outdir=kwargs.pop("outdir", "panels"),
                   fmt=kwargs.pop("fmt", "pdf"))
    return fig, ax
