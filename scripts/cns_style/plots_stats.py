"""plots_stats — cns_style sub-module"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from ._constants import *
from ._axes import *
from ._layout import *
from ._save import *
from ._annotation import *
from ._helpers import *
from ._helpers import _check_ov, _adata_to_tidy, _resolve_group_mask, _resolve_signal
from ._layout import _fs, _FIG_SCALE


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
                save_panel(fig, save, show=show, outdir=kwargs.pop("outdir", "panels"),
                    fmt=kwargs.pop("fmt", "pdf"))
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
        save_panel(fig, save, show=show, outdir=kwargs.pop("outdir", "panels"),
                    fmt=kwargs.pop("fmt", "pdf"))
    return fig, ax


# ============================================================
# 20.8 plot_enrichment — GO/KEGG 富集条形（ov 无，直接 mpl）
# ============================================================


# ============================================================
# 20.8 plot_enrichment — GO/KEGG 富集条形（ov 无，直接 mpl）
# ============================================================

def plot_enrichment(enr, ax=None, figsize=None, save=None, top_n=15,
                    term_col='Term', fdr_col='FDR', count_col='Gene_count',
                    group_col=None, group_order=None, per_group=5,
                    cap=None, pretty_terms=True, value_col=None,
                    group_colors=None, show=None, **kwargs):
    """Enrichment barh：-log10(FDR) 降序，条右标 gene count，通路名 pretty 清洗。

    升级（源自 fetal_heart draw_fig2e2_* ORA 系列实战）：
    group_col → 分组模式：每组取 per_group 条（按 FDR），组标题加粗着色 +
    组间分隔线，组色与上游 panel 严格一致；FDR>0.05 的通路 y 标签置灰。
    cap → 极端值轴封顶（如 30）：超限条画到 cap、标签显示真值（核糖体等
    -log10≈98 的通路不再把其他条压扁）。value_col 可换指标（如 combined score）。
    """
    df = enr.copy()
    df['_v'] = (-np.log10(df[fdr_col].clip(lower=1e-300)) if value_col is None
                else df[value_col].astype(float))
    df['_term'] = [_pretty_term(str(t)) if pretty_terms else str(t)[:40]
                   for t in df[term_col]]
    if group_col is not None:
        if group_order is not None:
            gorder = [g for g in group_order if g in set(df[group_col])]
        else:
            gorder = list(df[group_col].dropna().unique())
        parts = []
        for g in gorder:
            sub = df[df[group_col] == g].nsmallest(per_group, fdr_col)
            parts.append(sub.assign(_group=g))
        sel = pd.concat(parts, ignore_index=True)
    else:
        sel = df.nsmallest(top_n, fdr_col).assign(_group=None)
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize or (3.0, 0.24 * len(sel) + 0.6))
    else:
        fig = ax.figure
    if group_colors is None:
        group_colors = {g: MORLANDI[i % len(MORLANDI)]
                        for i, g in enumerate(gorder)} if group_col is not None else {}
    y_pos = np.arange(len(sel))
    vals = sel['_v'].to_numpy(float)
    drawn = np.minimum(vals, cap) if cap is not None else vals
    cols = [group_colors.get(g, '#BF616A') for g in sel['_group']]
    ax.barh(y_pos, drawn, color=cols, height=0.62, alpha=0.88,
            edgecolor='none', zorder=2)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(
        sel['_term'].tolist(), fontsize=7)
    # 非显著通路标签置灰（fetal_heart 约定：FDR>0.05 灰、其余 NEAR_BLACK）
    for t, fdr in zip(ax.get_yticklabels(), sel[fdr_col]):
        if float(fdr) > 0.05:
            t.set_color(GREY)
    ax.set_xlabel(r'$-$log$_{10}$(FDR)' if value_col is None else str(value_col),
                  labelpad=10)
    ax.invert_yaxis()
    for yy, v, d, n in zip(y_pos, vals, drawn, sel[count_col]):
        ax.text(d + 0.1 if cap is None else d + cap * 0.012, yy,
                (f'{v:.1f}' if cap is None or v < cap else f'{v:.0f}') +
                (f'  ({n})' if pd.notna(n) else ''),
                va='center', fontsize=6.3, color=GREY)
    if group_col is not None:
        seen = {}
        for yy, g in zip(y_pos, sel['_group']):
            seen.setdefault(g, yy)
        for g, yy in seen.items():
            ax.text(-0.06, yy - 0.32, str(g), fontweight='bold', fontsize=7.5,
                    transform=ax.get_yaxis_transform(),
                    color=group_colors.get(g, NEAR_BLACK), clip_on=False)
            if yy > 0:
                ax.axhline(yy - 0.62, color=GREY_SCALE['spine'], lw=0.8,
                           zorder=1)
    if cap is not None:
        ax.set_xlim(0, cap * 1.14)
    polish_axes(ax, variant='bar', grid_axis='x')
    ax.spines['left'].set_visible(True)
    ax.spines['left'].set_color(GREY_SCALE['grid'])
    if save:
        save_panel(fig, save, show=show, outdir=kwargs.pop("outdir", "panels"),
                    fmt=kwargs.pop("fmt", "pdf"))
    return fig, ax


_MINOR_WORDS = {'of', 'in', 'to', 'and', 'the', 'via', 'or', 'a', 'an', 'for'}


def _pretty_term(t, maxlen=48):
    """富集术语清洗：去数据库前缀、下划线转空格、介词小写、超长截断。"""
    for pre in ('GOBP_', 'GOCC_', 'GOMF_', 'HALLMARK_', 'REACTOME_', 'KEGG_',
                'WP_', 'CP:'):
        if t.startswith(pre):
            t = t[len(pre):]
            break
    words = t.replace('_', ' ').split()
    out = [w if (w.lower() not in _MINOR_WORDS or i == 0) else w.lower()
           for i, w in enumerate(words)]
    s = ' '.join(out)
    return s if len(s) <= maxlen else s[:maxlen - 1] + '…'


# ============================================================
# 20.9 plot_lr_bubble — L-R Bubble（ov 无，直接 mpl）
# ============================================================


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
                ax_ov.legend(title='-log10(p)', loc='upper left',
                             bbox_to_anchor=(1.22, 1.0), labelspacing=1.5,
                             handletextpad=1.6, frameon=False, fontsize=6,
                             title_fontsize=7, scatterpoints=1)
            if save:
                save_panel(fig, save, show=show, outdir=kwargs.pop("outdir", "panels"),
                    fmt=kwargs.pop("fmt", "pdf"))
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
        save_panel(fig, save, show=show, outdir=kwargs.pop("outdir", "panels"),
                    fmt=kwargs.pop("fmt", "pdf"))
    return fig, ax


# ============================================================
# 20.10 plot_feature_matrix — 多基因 UMAP 矩阵（ov 优先，mpl 兜底）
# ============================================================


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
                save_panel(fig_ov, save, show=show, outdir=kwargs.pop("outdir", "panels"),
                    fmt=kwargs.pop("fmt", "pdf"))
            return fig_ov, ax
        except Exception as e:
            print(f"[smart_plot] ov.pl.cellproportion failed ({e}), mpl fallback")
    _cellproportion_mpl(adata, groupby, celltype_col, ax)
    polish_axes(ax)
    if save:
        save_panel(fig, save, show=show, outdir=kwargs.pop("outdir", "panels"),
                    fmt=kwargs.pop("fmt", "pdf"))
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
            df_de['x_num'] = df_de['group'].map(group_map) + \
                np.random.uniform(-0.16, 0.16, len(df_de))   # 抖动防熔柱
            ov.pl.scatterplot(data=df_de, x='x_num', y='logFC', hue='padj',
                              cmap='coolwarm_r', alpha=0.7, s=15,
                              figsize=figsize or (min(n_groups * 0.8 + 0.5, 4.0), 2.5))
            fig = plt.gcf()
            ax_ov = fig.axes[0] if fig.axes else None
            if ax_ov:
                ax_ov.set_xticks(range(n_groups))
                ax_ov.set_xticklabels(group_names, fontsize=7)
                ax_ov.set_xlabel('')                    # 不泄漏内部列名 x_num
                ax_ov.set_ylabel('log$_2$FC')
            if save:
                save_panel(fig, save, show=show, outdir=kwargs.pop("outdir", "panels"),
                    fmt=kwargs.pop("fmt", "pdf"))
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
        save_panel(fig, save, show=show, outdir=kwargs.pop("outdir", "panels"),
                    fmt=kwargs.pop("fmt", "pdf"))
    return fig, ax


# ============================================================
# 20.16 plot_spatial_ccc — 空间细胞通讯共表达面板（ov 无，直接 mpl）
# ============================================================


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
                save_panel(fig, save, show=show, outdir=kwargs.pop("outdir", "panels"),
                    fmt=kwargs.pop("fmt", "pdf"))
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
        save_panel(fig, save, show=show, outdir=kwargs.pop("outdir", "panels"),
                    fmt=kwargs.pop("fmt", "pdf"))
    return fig, ax


# ============================================================
# 20.18 plot_signaling_heatmap — CCC 信号角色热图（ov 无，直接 mpl）
# ============================================================


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
                ax_fig.set_xlabel(str(x))               # 不泄漏内部列名
                ax_fig.set_ylabel(r'$-$log$_{10}$(FDR)')
                # size 图例（3 档虚拟点，右下角 clip_on=False）
                smin, smax = float(df[size].min()), float(df[size].max())
                for k, f_ in enumerate((1.0, 0.6, 0.25)):
                    ax_fig.scatter([], [], s=np.interp(f_, (0, 1), (8, 90)),
                                   c='lightgray', edgecolor=GREY, lw=0.5,
                                   label=f'{smin + (smax - smin) * f_:.0f}')
                ax_fig.legend(title=str(size), loc='lower right', frameon=False,
                              fontsize=6, labelspacing=1.1, borderpad=0.8,
                              handletextpad=1.2, scatterpoints=1)
            if save:
                save_panel(fig, save, show=show, outdir=kwargs.pop("outdir", "panels"),
                    fmt=kwargs.pop("fmt", "pdf"))
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
        save_panel(fig, save, show=show, outdir=kwargs.pop("outdir", "panels"),
                    fmt=kwargs.pop("fmt", "pdf"))
    return fig, ax


# ============================================================
# 20.23 plot_ccc_network — CCC/模块互作网络图（力导向布局，CoVarNet 2025 风格）
# ============================================================


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
    ov_ok = _check_ov() and not (hue is not None and use_y is not None)
    if ov_ok:
        try:
            import omicverse as ov
            ov.pl.kdeplot(data=df, x=use_x, y=use_y, hue=hue,
                          ax=ax, **kwargs)
            polish_axes(ax)
            if save:
                save_panel(fig, save, show=show, outdir=kwargs.pop("outdir", "panels"),
                    fmt=kwargs.pop("fmt", "pdf"))
            return fig, ax
        except Exception as e:
            print(f"[smart_plot] ov.pl.kdeplot failed ({e}), mpl fallback")
    _kde_mpl(df, use_x, use_y, hue, ax)
    polish_axes(ax)
    if save:
        save_panel(fig, save, show=show, outdir=kwargs.pop("outdir", "panels"),
                    fmt=kwargs.pop("fmt", "pdf"))
    return fig, ax



def _kde_mpl(df, x, y, hue, ax):
    """mpl KDE：单变量一维曲线 / 双变量等高线（hue 分组各自画+图例）。"""
    from scipy.stats import gaussian_kde
    if y is None:
        if hue is None:
            vals = df[x].dropna().values
            if len(vals) < 2:
                return
            xs = np.linspace(vals.min(), vals.max(), 300)
            dens = gaussian_kde(vals)(xs)
            ax.plot(xs, dens, color=MORLANDI[0], lw=1.5)
            ax.fill_between(xs, dens, color=MORLANDI[0], alpha=0.25)
            ax.set_xlabel(x)
            ax.set_ylabel('Density')
        else:
            for i, grp in enumerate(df[hue].astype('category').cat.categories):
                vals = df.loc[df[hue] == grp, x].dropna().values
                if len(vals) < 2:
                    continue
                xs = np.linspace(vals.min(), vals.max(), 300)
                c = MORLANDI[i % len(MORLANDI)]
                dens = gaussian_kde(vals)(xs)
                ax.plot(xs, dens, color=c, lw=1.5, label=grp)
                ax.fill_between(xs, dens, color=c, alpha=0.2)
            ax.set_xlabel(x)
            ax.set_ylabel('Density')
            ax.legend(frameon=False, fontsize=7)
        return
    # 双变量：hue 分组各自 KDE 等高线（3 层）+ 图例
    groups = ([None] if hue is None else
              list(df[hue].astype('category').cat.categories))
    for i, grp in enumerate(groups):
        sub = df if grp is None else df[df[hue] == grp]
        px = sub[x].to_numpy(float)
        py = sub[y].to_numpy(float)
        m_ok = np.isfinite(px) & np.isfinite(py)
        px, py = px[m_ok], py[m_ok]
        if len(px) < 5 or px.std() < 1e-9 or py.std() < 1e-9:
            continue
        c = MORLANDI[i % len(MORLANDI)]
        gx = np.linspace(px.min(), px.max(), 80)
        gy = np.linspace(py.min(), py.max(), 80)
        XX, YY = np.meshgrid(gx, gy)
        try:
            Z = gaussian_kde(np.vstack([px, py]))(
                np.vstack([XX.ravel(), YY.ravel()])).reshape(XX.shape)
        except np.linalg.LinAlgError:
            continue
        Z = Z / Z.max()
        kw = dict(colors=[c], linewidths=1.1, alpha=0.9)
        if grp is not None:
            kw['label'] = grp
        ax.contour(XX, YY, Z, levels=[0.3, 0.6, 0.9], **kw)
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    if hue is not None and len(groups) > 1:
        # contour 的 label 进不了 legend → 用 Line2D 代理
        from matplotlib.lines import Line2D
        handles = [Line2D([], [], color=MORLANDI[i % len(MORLANDI)], lw=1.5,
                          label=g) for i, g in enumerate(groups)]
        ax.legend(handles=handles, frameon=False, fontsize=7)



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
                save_panel(fig, save, show=show, outdir=kwargs.pop("outdir", "panels"),
                    fmt=kwargs.pop("fmt", "pdf"))
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
        save_panel(fig, save, show=show, outdir=kwargs.pop("outdir", "panels"),
                    fmt=kwargs.pop("fmt", "pdf"))
    return fig, ax


# ============================================================
# 20.29 plot_stripplot — 抖动散点（ov.pl.stripplot → mpl scatter）
# ============================================================

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
                save_panel(fig, save, show=show, outdir=kwargs.pop("outdir", "panels"),
                    fmt=kwargs.pop("fmt", "pdf"))
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
        save_panel(fig, save, show=show, outdir=kwargs.pop("outdir", "panels"),
                    fmt=kwargs.pop("fmt", "pdf"))
    return fig, ax


# ============================================================
# 20.30 plot_stackarea — 细胞比例堆叠面积（ov.pl.cellstackarea → mpl stackplot）
# ============================================================

# ============================================================
# 20.30 plot_stackarea — 细胞比例堆叠面积（ov.pl.cellstackarea → mpl stackplot）
# ============================================================
def plot_stackarea(adata, celltype_col='celltype', groupby='condition',
                   ax=None, figsize=None, save=None, show=None,
                   inband_labels=False, number_legend=False, min_band=0.05,
                   band_fs=7.5, groups_of=None, **kwargs):
    """细胞比例堆叠面积图：比例随连续/有序变量变化。ov.pl.cellstackarea 优先，
    mpl 兜底（inband_labels/number_legend 请求时强制走 mpl 以支持带内标注）。

    升级（源自 fetal_heart draw_fig1d_dynamics 实战）：
    inband_labels → 在带宽 ≥ min_band（比例）的带内放标签，字色按底色亮度
    自适应（0.299R+0.587G+0.114B < 120 用白字）；number_legend → 带内只放
    编号、图例给 "编号 全名"（类型多时唯一可读形态）；groups_of={类型: 大类}
    → 大类边界白粗线分隔。
    """
    import pandas as pd
    want_bands = inband_labels or number_legend or groups_of is not None
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize or (3.0, 2.5))
    else:
        fig = ax.figure
    if _check_ov() and not want_bands:
        try:
            import omicverse as ov
            ov.pl.cellstackarea(adata, celltype_clusters=celltype_col,
                                groupby=groupby, ax=ax)
            if save:
                save_panel(fig, save, show=show, outdir=kwargs.pop("outdir", "panels"),
                    fmt=kwargs.pop("fmt", "pdf"))
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
    cts = list(prop.columns)
    # >8 类自动换扩展 20 色板（防相邻撞色），缺省 8 色
    pal = MORLANDI_EXTENDED if len(cts) > len(MORLANDI) else MORLANDI
    colors = [pal[i % len(pal)] for i in range(len(cts))]
    # 堆叠顺序 = 反转（与图例阅读顺序一致；fetal_heart 约定）
    order = cts[::-1]
    colmap = dict(zip(cts, colors))
    ax.stackplot(x, *[prop[c].values for c in order],
                 labels=order, colors=[colmap[c] for c in order],
                 alpha=0.85, edgecolor='white', linewidth=0.3)
    # 底边坐标（绘制顺序 order[0] 在最下）
    bottoms = np.zeros(len(groups))
    band_center = {}
    for c in order:
        band_center[c] = bottoms + prop[c].values / 2
        bottoms = bottoms + prop[c].values
    # 大类边界白粗线（相邻绘制序类型的 groups_of 不同 → 在累计顶边画线）
    if groups_of is not None:
        cum = np.zeros(len(groups))
        prev_g = None
        for c in order:
            cur_g = groups_of.get(c)
            if prev_g is not None and cur_g != prev_g:
                ax.plot(x, cum, color='white', lw=2.6, zorder=3)
            cum = cum + prop[c].values
            prev_g = cur_g
    # 带内标签（编号或名称；宽度达标才放，字色亮度自适应）
    if inband_labels or number_legend:
        nums = {c: i + 1 for i, c in enumerate(cts)}
        for c in order:
            w = prop[c].values
            if w.max() < min_band:
                continue
            xi = int(np.argmax(w))
            lab = str(nums[c]) if number_legend else str(c)[:12]
            lum = _hex_luma(colmap[c])
            ax.text(xi, band_center[c][xi], lab, fontsize=band_fs,
                    color='white' if lum < 120 else NEAR_BLACK,
                    fontweight='bold', ha='center', va='center', zorder=4)
    # 图例：Patch 手柄按 cts 顺序配对（编号/颜色一一对应，杜绝错位）
    from matplotlib.patches import Patch
    leg_labels = ([f'{i + 1} {c}' for i, c in enumerate(cts)]
                  if number_legend else cts)
    ax.legend([Patch(facecolor=colmap[c], edgecolor='none') for c in cts],
              leg_labels, bbox_to_anchor=(1.02, 0.5), loc='center left',
              frameon=False, fontsize=7, title=celltype_col)
    ax.set_xticks(x)
    ax.set_xticklabels(groups, fontsize=7, rotation=45 if len(groups) > 8 else 0)
    ax.set_xlabel(groupby)
    ax.set_ylabel('Proportion')
    ax.set_ylim(0, 1)
    polish_axes(ax)
    if save:
        save_panel(fig, save, show=show, outdir=kwargs.pop("outdir", "panels"),
                    fmt=kwargs.pop("fmt", "pdf"))
    return fig, ax


def _hex_luma(hex_color):
    """相对亮度（YIQ）：<120 视为深底 → 配白字。"""
    h = hex_color.lstrip('#')
    return int(h[0:2], 16) * 0.299 + int(h[2:4], 16) * 0.587 + \
        int(h[4:6], 16) * 0.114


def _fmt_range(v):
    """QC 卡片列顶范围：<1000 用 4 位有效数字，≥1000 用千分位整数。"""
    return f'{v:,.0f}' if abs(v) >= 1000 else f'{v:.4g}'


def _darken_hex(hex_color, factor=0.72):
    """浅色标题加深一档（白底打印对比度兜底）。"""
    h = hex_color.lstrip('#')
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return '#{:02x}{:02x}{:02x}'.format(int(r * factor), int(g * factor),
                                        int(b * factor))


# ============================================================
# 20.31 plot_bardotplot — 柱+点组合（ov.pl.bardotplot → mpl bar+scatter）
# ============================================================

# ============================================================
# 20.31 plot_bardotplot — 柱+点组合（ov.pl.bardotplot → mpl bar+scatter）
# ============================================================
def plot_bardotplot(adata, groupby, color, ax=None, figsize=None,
                    save=None, show=None, **kwargs):
    """柱+点组合图：均值柱+分布点双重展示。mpl 优先（点层带 jitter，可读）；
    ov.pl.bardotplot 点层无抖动会熔成实心柱（2026-09 视觉验收实证），engine='ov' 可回旧路径。"""
    import pandas as pd
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize or (3.0, 2.5))
    else:
        fig = ax.figure
    if kwargs.pop('engine', 'mpl') == 'ov' and _check_ov():
        try:
            import omicverse as ov
            ov.pl.bardotplot(adata, groupby=groupby, color=color,
                             ax=ax)
            polish_axes(ax)
            if save:
                save_panel(fig, save, show=show, outdir=kwargs.pop("outdir", "panels"),
                    fmt=kwargs.pop("fmt", "pdf"))
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
        save_panel(fig, save, show=show, outdir=kwargs.pop("outdir", "panels"),
                    fmt=kwargs.pop("fmt", "pdf"))
    return fig, ax


# ============================================================
# 20.32 plot_stacking_vol — 堆叠火山（ov.pl.stacking_vol，无 mpl 兜底）
# ============================================================

# ============================================================
# 20.32 plot_stacking_vol — 堆叠火山（ov.pl.stacking_vol，无 mpl 兜底）
# ============================================================
def plot_stacking_vol(data_dict, color_dict=None, ax=None, figsize=None,
                      save=None, show=None, **kwargs):
    """堆叠火山图：多条件 DE 并排比较（每条件一列 mini 火山，共享 y 轴）。
    data_dict: {条件名: DE DataFrame}（每含 gene/padj/log2FC 列）。
    ov.pl.stacking_vol 优先（列名自动映射），ov 失败走 mpl 兜底——绝不静默返回。
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
            save_panel(fig, save, show=show, outdir=kwargs.pop("outdir", "panels"),
                    fmt=kwargs.pop("fmt", "pdf"))
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
        print(f"[smart_plot] ov.pl.stacking_vol failed ({e}), mpl fallback")
        fig, ax_out = _stacking_vol_mpl(data_dict, color_dict, figsize,
                                        save, show)
        if fig is None:
            raise RuntimeError(
                f"[smart_plot] plot_stacking_vol 全部路径失败（ov: {e}），"
                "请检查 data_dict 结构（每条件需含 gene/padj/log2FC 列）")
        return fig, ax_out


def _stacking_vol_mpl(data_dict, color_dict, figsize, save, show):
    """mpl 兜底：每条件一列 up/down 双色 mini 火山，共享 -log10(p) y 轴。"""
    conds = list(data_dict)
    n = len(conds)
    if n == 0:
        return None, None
    if color_dict is None:
        color_dict = {k: MORLANDI[i % len(MORLANDI)] for i, k in enumerate(conds)}
    fig, axes = plt.subplots(1, n, figsize=figsize or (1.7 * n + 0.6, 3.0),
                             sharey=True, squeeze=False)
    vmax = 0.0
    frames = {}
    for c in conds:
        de = data_dict[c]
        y = -np.log10(de['padj'].clip(lower=1e-300))
        frames[c] = (de, y)
        vmax = max(vmax, np.nanquantile(y, 0.995))
    for k, c in enumerate(conds):
        a = axes[0][k]
        de, y = frames[c]
        fc = de['log2FC'].values
        sig = (de['padj'].values < 0.05) & (np.abs(fc) > 1)
        col = color_dict[c]
        a.scatter(fc[~sig], y[~sig], s=3, color=MUTED, alpha=0.5, lw=0,
                  rasterized=True)
        a.scatter(fc[sig], y[sig], s=5, color=col, alpha=0.85, lw=0,
                  rasterized=True)
        a.set_title(c, fontsize=8, loc='left', color=col)
        a.set_xlabel('log2FC', fontsize=7)
        if k == 0:
            a.set_ylabel(r'$-$log$_{10}$(padj)', fontsize=7)
        a.set_ylim(0, vmax * 1.05)
        polish_axes(a, variant='bar', grid_axis='y')
        a.tick_params(labelsize=6.5)
    fig.tight_layout(w_pad=0.6)
    if save:
        save_panel(fig, save, show=show)
    return fig, axes[0]
# ============================================================
# 20.33 plot_upset — UpSet 图（ov 专用，无 mpl 兜底）
# ============================================================

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
            save_panel(fig, save, show=show, outdir=kwargs.pop("outdir", "panels"),
                    fmt=kwargs.pop("fmt", "pdf"))
        return fig, fig.axes[0] if fig.axes else None
    except Exception as e:
        print(f"[smart_plot] ov.pl.upset failed ({e})")
        return None, None


# ============================================================
# 20.34 plot_venn — Venn 图（ov.pl.venn，无 mpl 兜底）
# ============================================================

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
                save_panel(fig, save, show=show, outdir=kwargs.pop("outdir", "panels"),
                    fmt=kwargs.pop("fmt", "pdf"))
            return fig, fig.axes[0] if fig.axes else None
    except Exception as e:
        print(f"[smart_plot] ov.pl.venn failed ({e})")
        return None, None


# ============================================================
# 20.35 plot_forest — 森林图（ov.pl.forest → mpl errorbar）
# ============================================================

# ============================================================
# 20.35 plot_forest — 森林图（ov.pl.forest → mpl errorbar）
# ============================================================
def plot_forest(data, estimate, lower=None, upper=None, label=None,
                group=None, ax=None, figsize=None, save=None, show=None, **kwargs):
    """森林图：meta-analysis/多研究效应合并。mpl 优先（无效线语义正确：
    null_value 默认 auto——估计全为正（OR/HR 类）时无效线=1.0，否则=0；
    ov 版无效线固定画 0 会误读 OR 结果，2026-09 视觉验收实证）。
    data: DataFrame，estimate/lower/upper/label 是列名。
    """
    import pandas as pd
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize or (2.5, min(len(data) * 0.3 + 0.5, 3.5)))
    else:
        fig = ax.figure
    null_value = kwargs.pop('null_value', 'auto')
    if null_value == 'auto':
        _est = pd.to_numeric(data[estimate], errors='coerce').dropna()
        null_value = 1.0 if (_est.min() > 0) else 0.0
    if kwargs.pop('engine', 'mpl') == 'ov' and _check_ov():
        try:
            import omicverse as ov
            ov.pl.forest(data=data, estimate=estimate, lower=lower, upper=upper,
                         label=label, group=group, ax=ax, **kwargs)
            polish_axes(ax)
            if save:
                save_panel(fig, save, show=show, outdir=kwargs.pop("outdir", "panels"),
                    fmt=kwargs.pop("fmt", "pdf"))
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
    ax.axvline(null_value, color=GREY, lw=0.8, ls='--', linestyle='--', zorder=1)
    ax.set_xlabel(estimate)
    polish_axes(ax)
    if save:
        save_panel(fig, save, show=show, outdir=kwargs.pop("outdir", "panels"),
                    fmt=kwargs.pop("fmt", "pdf"))
    return fig, ax


# ============================================================
# 20.36 plot_regplot — 回归散点（ov.pl.regplot → mpl polyfit）
# ============================================================

# ============================================================
# 20.36 plot_regplot — 回归散点（ov.pl.regplot → mpl polyfit）
# ============================================================
def plot_regplot(data, x, y, hue=None, fit='linear', ax=None, figsize=None,
                 save=None, show=None, **kwargs):
    """回归散点图：散点+拟合线+95% CI 带。mpl 优先（CI 带完整）；
    ov.pl.regplot 无 CI 层（2026-09 视觉验收实证），engine='ov' 可回旧路径。"""
    import pandas as pd
    if hasattr(data, 'var_names'):   # AnnData
        df = _adata_to_tidy(data, [c for c in (x, y, hue) if c])
    else:
        df = data
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize or (3.0, 2.5))
    else:
        fig = ax.figure
    if kwargs.pop('engine', 'mpl') == 'ov' and _check_ov():
        try:
            import omicverse as ov
            ov.pl.regplot(data=df, x=x, y=y, hue=hue, fit=fit,
                          ax=ax, **kwargs)
            polish_axes(ax)
            if save:
                save_panel(fig, save, show=show, outdir=kwargs.pop("outdir", "panels"),
                    fmt=kwargs.pop("fmt", "pdf"))
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
        save_panel(fig, save, show=show, outdir=kwargs.pop("outdir", "panels"),
                    fmt=kwargs.pop("fmt", "pdf"))
    return fig, ax



def _fit_line(ax, xs, ys, fit='linear', color=None, n=200, ci=True):
    """拟合线 + 95% CI 带：linear/quadratic → 多项式±1.96·残差SD；
    lowess → LOWESS 曲线 + 残差幅度的 LOWESS 包络带。"""
    mask = ~(np.isnan(xs) | np.isnan(ys))
    xs, ys = np.asarray(xs, float)[mask], np.asarray(ys, float)[mask]
    if len(xs) < 3:
        return
    c = color or NEAR_BLACK
    if fit == 'lowess':
        try:
            from statsmodels.nonparametric.smoothers_lowess import lowess
        except ImportError:
            fit = 'linear'
        else:
            order = np.argsort(xs)
            sm = lowess(ys[order], xs[order], frac=0.7, return_sorted=True)
            xl, yl = sm[:, 0], sm[:, 1]
            resid = np.interp(xs, xl, yl) - ys
            rabs = lowess(np.abs(resid)[order], xs[order], frac=0.7,
                          return_sorted=True)
            band = 1.96 * np.interp(xl, rabs[:, 0], rabs[:, 1])
            ax.plot(xl, yl, color=c, lw=1.4, zorder=4)
            if ci:
                ax.fill_between(xl, yl - band, yl + band, color=c,
                                alpha=0.13, lw=0, zorder=3)
            return
    deg = {'linear': 1, 'quadratic': 2}.get(fit, 1)
    try:
        coef = np.polyfit(xs, ys, deg)
    except np.linalg.LinAlgError:
        return
    xline = np.linspace(np.nanpercentile(xs, 1), np.nanpercentile(xs, 99), n)
    yline = np.polyval(coef, xline)
    ax.plot(xline, yline, color=c, lw=1.2, zorder=4)
    if ci:
        se = 1.96 * float(np.std(ys - np.polyval(coef, xs)))
        ax.fill_between(xline, yline - se, yline + se, color=c, alpha=0.13,
                        lw=0, zorder=3)


def plot_pca_variance(adata, n_pcs=30, ax=None, figsize=None,
                      save=None, show=None, **kwargs):
    """PCA 方差比图：QC 标配（选 PCs 数）。mpl 优先（方差比柱+累计方差线双轴）；
    ov 版无累计线且刻度粘连（2026-09 视觉验收实证），engine='ov' 可回旧路径。"""
    import pandas as pd
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize or (3.0, 2.5))
    else:
        fig = ax.figure
    if kwargs.pop('engine', 'mpl') == 'ov' and _check_ov():
        try:
            import omicverse as ov
            ov.pl.plot_pca_variance_ratio(adata, n_pcs=n_pcs, show=False,
                                          **kwargs)
            fig_ov = plt.gcf()          # 无 ax 参数，自建 figure
            fig_ov.set_size_inches(*(figsize or (3.0, 2.5)))
            ax_ov = fig_ov.axes[0] if fig_ov.axes else ax
            polish_axes(ax_ov)
            if save:
                save_panel(fig_ov, save, show=show, outdir=kwargs.pop("outdir", "panels"),
                    fmt=kwargs.pop("fmt", "pdf"))
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
    ax.set_xticks(range(0, n, max(1, int(np.ceil(n / 6)))))
    ax.set_xlabel('PC')
    ax.set_ylabel('Variance ratio')
    # 累计方差贡献线（右轴）——scree 图标配
    ax2 = ax.twinx()
    cum = np.cumsum(ratios) / ratios.sum()
    ax2.plot(range(1, n + 1), cum, color=CONTRAST_RED, lw=1.2, marker='',
             zorder=4)
    ax2.set_ylim(0, 1.05)
    ax2.set_ylabel('Cumulative', fontsize=7, color=CONTRAST_RED)
    ax2.tick_params(labelsize=6.5, colors=CONTRAST_RED, length=2)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_color(GREY_SCALE['spine'])
    polish_axes(ax)
    if save:
        save_panel(fig, save, show=show, outdir=kwargs.pop("outdir", "panels"),
                    fmt=kwargs.pop("fmt", "pdf"))
    return fig, ax


# ============================================================
# 20.39 plot_hvg_scatter — HVG 均值-离散散点（ov → mpl）
# ============================================================

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
            from matplotlib.ticker import MaxNLocator
            ax.xaxis.set_major_locator(MaxNLocator(3))    # 稀疏化
            ax.xaxis.set_major_formatter('{x:.2f}')       # 定点两位（指数串太长）
            polish_axes(ax)
            if save:
                save_panel(fig, save, show=show, outdir=kwargs.pop("outdir", "panels"),
                    fmt=kwargs.pop("fmt", "pdf"))
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
    from matplotlib.ticker import MaxNLocator
    ax.xaxis.set_major_locator(MaxNLocator(3))
    ax.xaxis.set_major_formatter('{x:.2f}')
    ax.set_xlabel('Mean expression')
    ax.set_ylabel('Dispersion')
    ax.legend(frameon=False, fontsize=7)
    polish_axes(ax)
    if save:
        save_panel(fig, save, show=show, outdir=kwargs.pop("outdir", "panels"),
                    fmt=kwargs.pop("fmt", "pdf"))
    return fig, ax


# ============================================================
# 20.40 plot_radar — 多尺度雷达（mpl polar，源自 figures4papers）
# ============================================================

def plot_radar(values, axis_labels, series_names=None, axis_ranges=None, colors=None,
               ax=None, figsize=(3.2, 3.2), r_lo=0.15, r_hi=0.9,
               fill_alpha=0.06, lw=1.0, show_spoke_max=True, label_fontsize=6,
               tick_fontsize=5.5, legend_fontsize=6, save=None, show=None,
               outdir='panels', fmt='pdf'):
    """多尺度雷达图（每根辐条按自己的量程归一化）。

    values: (n_series × n_axes) array/DataFrame；axis_ranges: None(按各轴数据 min/max) 或
    {axis_label: (lo, hi)} / list[(lo,hi)]（异量纲指标各按其合理范围归一——iLISI/cLISI/ASW 同图的关键）。
    归一后统一映射到 [r_lo, r_hi]；顶点 scatter 标出真实数据点；手绘辐条+外环(grid off)；
    每辐条外侧只标该轴 max 数值(show_spoke_max)；spoke 标签按 |sin(angle)| 加 offset 防挤；
    适用于：方法/整合基准的多指标对比（batch mixing × bio conservation 一图比）。返回 (fig, ax)。

    Usage:
        plot_radar(vals, ['iLISI', 'cLISI', 'ASW_batch', 'ASW_celltype', 'GraphConn'],
                   series_names=['Harmony', 'scVI', '未校正'],
                   axis_ranges={'iLISI': (0, 1), 'GraphConn': (0, 100)})
    """
    was_df = isinstance(values, pd.DataFrame)
    df_columns = list(values.columns) if was_df else None
    values = np.asarray(values, dtype=float)
    if values.ndim != 2:
        raise ValueError("plot_radar: values 需为 (n_series x n_axes) 二维数组/DataFrame")
    n_series, n_axes = values.shape
    if len(axis_labels) != n_axes:
        raise ValueError(f"plot_radar: axis_labels 长度 {len(axis_labels)} != 轴数 {n_axes}")
    if series_names is None and df_columns is not None:
        series_names = df_columns
    if series_names is not None and len(series_names) != n_series:
        raise ValueError(f"plot_radar: series_names 长度 {len(series_names)} != 系列数 {n_series}")

    # NaN 按轴 nanmean 填充（整轴全 NaN → 0）
    if np.isnan(values).any():
        fill = np.where(np.isnan(values).all(axis=0), 0.0, np.nanmean(values, axis=0))
        values = np.where(np.isnan(values), fill, values)

    # 每轴 (lo, hi)：axis_ranges 显式给定（dict 按标签查、缺失回退数据 min/max）或数据 min/max
    def _data_range(j):
        lo, hi = float(np.min(values[:, j])), float(np.max(values[:, j]))
        if hi - lo <= 1e-12:
            lo, hi = 0.0, 1.0
        return (lo, hi)

    if axis_ranges is None:
        ranges = [_data_range(j) for j in range(n_axes)]
    elif isinstance(axis_ranges, dict):
        # dict 键缺失 → 该轴回退数据 min/max
        ranges = [tuple(axis_ranges[lbl]) if lbl in axis_ranges else _data_range(j)
                  for j, lbl in enumerate(axis_labels)]
    else:
        ranges = [tuple(r) for r in axis_ranges]
        if len(ranges) != n_axes:
            raise ValueError(f"plot_radar: axis_ranges 长度 {len(ranges)} != 轴数 {n_axes}")

    # 各轴按自身量程归一 → 统一映射到 [r_lo, r_hi]
    norms = np.zeros_like(values)
    for j in range(n_axes):
        lo, hi = ranges[j]
        span = hi - lo
        if span <= 0:
            norms[:, j] = (r_lo + r_hi) / 2
        else:
            norms[:, j] = r_lo + (r_hi - r_lo) * np.clip((values[:, j] - lo) / span, 0.0, 1.0)

    angles = np.linspace(0, 2 * np.pi, n_axes, endpoint=False)
    angles_closed = np.append(angles, angles[0])
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize, subplot_kw={'projection': 'polar'})
    else:
        fig = ax.figure
    if colors is None:
        colors = MORLANDI

    for m in range(n_series):
        r_closed = np.append(norms[m], norms[m][0])
        col = colors[m % len(colors)]
        ax.plot(angles_closed, r_closed, color=col, linewidth=lw,
                label=series_names[m] if series_names is not None else None)
        ax.fill(angles_closed, r_closed, color=col, alpha=fill_alpha)
        ax.scatter(angles, norms[m], color=col, s=6, zorder=5, edgecolors='none')

    ax.set_theta_zero_location('N')
    ax.set_ylim(r_lo, r_hi)
    ax.grid(False)
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    # 手绘辐条 + 外环（grid off 后手动补回）
    for a in angles:
        ax.plot([a, a], [r_lo, r_hi], color=GREY, linewidth=0.4, zorder=4)
    ax.plot(angles_closed, np.full_like(angles_closed, r_hi),
            color=NEAR_BLACK, linewidth=0.6, zorder=4)
    ax.set_xticks(angles)
    ax.set_xticklabels([])

    # spoke 标签：小数据半径偏移（勿用大数——r 为数据单位，曾致 tightbbox 爆炸）
    for a, lbl in zip(angles, axis_labels):
        offset = 0.07 + 0.10 * abs(np.sin(a))
        ax.text(a, r_hi + offset, str(lbl), fontsize=label_fontsize,
                ha='center', va='center', transform=ax.transData, clip_on=False)
    # 每辐条外侧标该轴 max 数值（原始单位，沿辐条旋转）
    if show_spoke_max:
        for a, j in zip(angles, range(n_axes)):
            v = float(np.max(values[:, j]))
            txt = f'{v:.0f}' if v == int(v) else f'{v:.2f}'
            import matplotlib.patheffects as _pe
            ax.text(a, r_hi - 0.09, txt, fontsize=tick_fontsize,
                    ha='center', va='center', rotation=0,
                    transform=ax.transData, clip_on=False,
                    path_effects=[_pe.withStroke(linewidth=2.0,
                                                 foreground='white')])

    if series_names is not None:
        # 图例置底横排：右侧外置会把 tight 画布撑宽超单栏（2026-09 刊出验收实证）
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.06),
                  ncols=len(series_names), frameon=False,
                  fontsize=legend_fontsize, columnspacing=1.4,
                  handletextpad=0.4)
    if save:
        save_panel(fig, save, show=show, outdir=outdir, fmt=fmt)
    return fig, ax


# ============================================================
# 20.41 plot_raincloud — 云雨图（左半小提琴+白底箱线+右侧雨点三合一；
#        源自 mHeart 外部验证 149f/149g 实战模板）
# ============================================================

def plot_raincloud(data, x, y, order=None, colors=None, ax=None, figsize=None,
                   save=None, show=None, half_width=0.28, box_width=0.11,
                   rain_offset=0.10, rain_jitter=0.08, rain_size=11,
                   kde_bw=0.3, kde_min_n=5, violin_alpha=0.55,
                   box_edge=None, median_color=None, show_n=True,
                   test=None, ref=None, seed=1, **kwargs):
    """云雨图：每组 = 左半小提琴(n≥kde_min_n) + 白底箱线 + 右侧雨点（每点=一观测/一样本）。

    data: tidy DataFrame（x=分组列名, y=数值列名）；AnnData 自动转 tidy。
    order: 组顺序；colors: {组: hex} 或列表，缺省 MORLANDI 循环。
    test='mwu': 各组 vs ref 组（默认第一组）Mann-Whitney U 错位显著性括号。
    show_n: x 刻度附 (n=..)。样本级数据（每点=一供体/一样本）先聚合到样本级再画。
    """
    from scipy.stats import gaussian_kde, mannwhitneyu
    if hasattr(data, 'var_names'):
        df = _adata_to_tidy(data, [x, y])
    else:
        df = data
    sub = df[[x, y]].dropna()
    groups = list(order) if order is not None else list(pd.unique(sub[x]))
    if colors is None:
        colors = {g: MORLANDI[i % len(MORLANDI)] for i, g in enumerate(groups)}
    elif not isinstance(colors, dict):
        colors = {g: c for g, c in zip(groups, colors)}
    box_edge = NEAR_BLACK if box_edge is None else box_edge
    median_color = box_edge if median_color is None else median_color
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize or (3.8, 3.0))
    else:
        fig = ax.figure
    rng = np.random.default_rng(seed)
    arrays = {g: sub.loc[sub[x] == g, y].to_numpy(float) for g in groups}
    lo = min(v.min() for v in arrays.values() if len(v))
    hi = max(v.max() for v in arrays.values() if len(v))
    pad = (hi - lo) * 0.12 if hi > lo else abs(hi) * 0.1 + 1
    # test 括号预留头顶空间（错位 j 层：hi + pad*(0.5 + 1.05*j) + 文字）
    ref_g = groups[0] if ref is None else ref
    non_ref = [g for g in groups if g != ref_g]
    n_brk = len(non_ref) if test == 'mwu' else 0
    grid = np.linspace(lo - pad, hi + pad * (0.5 + 1.05 * max(n_brk - 1, 0) + 0.9),
                       200)
    for i, g in enumerate(groups):
        vals = arrays[g]
        color = colors[g]
        x0 = float(i)
        # 左半小提琴（n 太小时 KDE 不稳，退化为箱线+雨点）
        if len(vals) >= kde_min_n:
            try:
                dens = gaussian_kde(vals, bw_method=kde_bw)(grid)
                dens = dens / dens.max() * half_width
                dens[grid < vals.min()] = 0
                dens[grid > vals.max()] = 0
                ax.fill_betweenx(grid, x0 - dens, x0, color=color,
                                 alpha=violin_alpha, lw=0, zorder=1)
            except np.linalg.LinAlgError:
                pass
        # 中间白底箱线
        bp = ax.boxplot([vals], positions=[x0], widths=box_width,
                        patch_artist=True, showfliers=False, showcaps=True,
                        manage_ticks=False, zorder=3)
        for b in bp['boxes']:
            b.set(facecolor='white', edgecolor=box_edge, lw=1.0)
        for w in bp['whiskers']:
            w.set(color=box_edge, lw=1.0)
        for m in bp['medians']:
            m.set(color=median_color, lw=1.6)
        # 右侧雨点
        rain_x = x0 + rain_offset + rng.normal(0, rain_jitter, size=len(vals))
        ax.scatter(rain_x, vals, s=rain_size, color=color, alpha=0.8,
                   lw=0, rasterized=True, zorder=2)
    # 错位显著性括号：各组 vs ref
    if test == 'mwu':
        for j, g in enumerate(non_ref):
            _, p = mannwhitneyu(arrays[g], arrays[ref_g], alternative='two-sided')
            y0 = hi + pad * (0.5 + 1.05 * j)
            xi, xj = groups.index(ref_g), groups.index(g)
            ax.plot([xi, xi, xj, xj], [y0, y0 + pad * 0.25, y0 + pad * 0.25, y0],
                    color='#9aa0a6', lw=0.8)
            stars = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else 'n.s.'
            ax.text((xi + xj) / 2, y0 + pad * 0.38,
                    (f'{stars} (p<0.001)' if p < 0.001 else
                     f'{stars} (p={p:.2f})') if stars != 'n.s.'
                    else f'n.s. (p={p:.2f})',
                    ha='center', fontsize=7.5, color=NEAR_BLACK)
    ax.set_xticks(range(len(groups)))
    ax.set_xticklabels([f'{g}\n(n={len(arrays[g])})' if show_n else str(g)
                        for g in groups], fontsize=8)
    ax.set_xlim(-half_width - 0.34, len(groups) - 0.55)
    ax.set_xlabel('')
    ax.set_ylabel(str(y), fontsize=9)
    polish_axes(ax)
    if save:
        save_panel(fig, save, show=show)
    return fig, ax


# ============================================================
# 20.42 plot_slope — 斜率图（组成/指标跨条件变化，端点直接标签防撞）
#   源自 fetal_heart draw_fig1d2_movers / draw_fig2k1_trajectories 实战
#   （2026-09 人工多轮验证形态：无图例 + 端点带 Δ 标签 + 强调线加粗）
# ============================================================

def plot_slope(data, value_col=None, entity_col=None, group_col=None,
               top_n=8, order=None, colors=None, emphasize=None,
               base_color=None, emph_lw=2.6, base_lw=1.6, label_deltas=True,
               point=True, gap_pt=12, ax=None, figsize=None, save=None,
               show=None, **kwargs):
    """斜率图：每实体一条跨组（≥2 个时间点/条件）的折线，端点直接标注。

    data 两种形态：
      ① tidy DataFrame + entity_col/group_col/value_col（实体×组×值长表）
      ② wide DataFrame（index=实体, columns=组）——entity 系参数留空自动识别
    top_n: 按距行均值的最大偏差选前 N 实体（同时抓净变化与中途峰）。
    emphasize: 需加粗强调的实体列表（其余走 base_color 灰，视觉层级）。
    端点标签用 direct_label 像素级防撞（gap_pt），label_deltas 时右端附 +Δ。
    """
    if entity_col is not None and group_col is not None and value_col is not None:
        wide = data.pivot_table(index=entity_col, columns=group_col,
                                values=value_col, aggfunc='mean')
    else:
        wide = data
    groups = list(order) if order is not None else list(wide.columns)
    wide = wide[groups]
    if len(groups) < 2:
        raise ValueError("plot_slope 需要至少 2 个组（时间点/条件）")
    dev = (wide - wide.mean(axis=1)).abs().max(axis=1)
    sel = dev.sort_values(ascending=False).head(top_n).index.tolist()
    wide = wide.loc[sel]
    n_g = len(groups)
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize or (3.4, 0.46 * len(wide) + 0.9))
    else:
        fig = ax.figure
    emphasize = list(emphasize or [])
    base_color = base_color or GREY_SCALE['guide']
    if colors is None:
        colors = {e: base_color for e in wide.index}
    elif not isinstance(colors, dict):
        colors = {e: c for e, c in zip(wide.index, colors)}
    for e in [x for x in wide.index if x not in emphasize] + \
             [x for x in wide.index if x in emphasize]:
        row = wide.loc[e].values.astype(float)
        c = colors.get(e, base_color)
        ax.plot(range(n_g), row, color=c, lw=emph_lw if e in emphasize else base_lw,
                zorder=3 if e in emphasize else 2, alpha=0.95,
                solid_capstyle='round')
        if point:
            # 白晕垫底再画白芯环点：端点聚集时不同线的 marker 不互相吞没
            ax.scatter(range(n_g), row, s=22 * 2.6, color='white', lw=0,
                       zorder=(4 if e in emphasize else 3) - 0.1)
            ax.scatter(range(n_g), row, s=22, color=c, marker='o',
                       facecolor='white', linewidths=1.2,
                       zorder=4 if e in emphasize else 3)
    # 端点直接标签（像素防撞 stagger；Δ 两位小数，<0.005 只留名）
    lefts = [f'{e}' for e in wide.index]
    rights = []
    for e in wide.index:
        d = wide.loc[e, groups[-1]] - wide.loc[e, groups[0]]
        with_d = f'{e} {d:+.2f}' if abs(d) >= 0.005 else f'{e}'
        rights.append(with_d if label_deltas else f'{e}')
    direct_label(ax, wide[groups[0]].values, lefts, x=0, side='left',
                 gap_pt=gap_pt, fontsize=7.5)
    direct_label(ax, wide[groups[-1]].values, rights, x=n_g - 1, side='right',
                 gap_pt=gap_pt, fontsize=7.5)
    ax.set_xticks(range(n_g))
    ax.set_xticklabels(groups, fontsize=8)
    ax.set_xlim(-0.78, n_g - 0.22)
    # 底部预留 0.3×range：最低系列的端点标签与 x 刻度彻底分层
    rng_ = wide.values.max() - wide.values.min() + 1e-9
    ax.set_ylim(wide.values.min() - 0.30 * rng_, wide.values.max() + 0.14 * rng_)
    polish_axes(ax, variant='bar', grid_axis='y')
    ax.spines['bottom'].set_visible(False)
    ax.tick_params(axis='x', length=0, pad=6)
    if save:
        save_panel(fig, save, show=show,
                    outdir=kwargs.pop("outdir", "panels"),
                    fmt=kwargs.pop("fmt", "pdf"))
    return fig, ax


# ============================================================
# 20.43 plot_lollipop — 发散棒棒糖（每实体一个效应量，可选第二统计量空心点）
#   源自 fetal_heart draw_fig2e1_hdwgcna（module-trait 双统计量）/
#   draw_fig1g_v4_bars（置换 null 带 + 参考线）实战回灌
# ============================================================

def plot_lollipop(data, label_col, value_col, value2_col=None, pval_col=None,
                  tag_col=None, order=None, pos_color=None, neg_color=None,
                  stars=True, ref_line=None, null_band=None,
                  null_label='random matching', tag_title=None,
                  value_fmt='{:+.2f}', pair_dy=0.16, ax=None, figsize=None,
                  save=None, show=None, **kwargs):
    """发散棒棒糖：stem 从 0 到 value（正/负双色），实心大点=主统计量，
    可选空心小点=第二统计量（如 Pearson 实心 + Spearman 空心）。

    data: DataFrame；label_col=实体名；value_col=主统计量（r/ρ/log2FC…）；
    value2_col=第二统计量；pval_col → 值旁星号；tag_col → 右缘身份标签
    （get_yaxis_transform 坐标）；ref_line=参考值虚线（如 0.8）；
    null_band=(lo, hi) → 灰底置换零带 + 顶部斜体注释（先算好 2.5–97.5% 分位）。
    """
    df = data.copy()
    if order is not None:
        df = df.set_index(label_col).loc[order].reset_index()
    else:
        df = df.sort_values(value_col, ascending=True).reset_index(drop=True)
    pos_color = pos_color or CONTRAST_RED
    neg_color = neg_color or CONTRAST_BLUE
    n = len(df)
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize or (3.4, 0.34 * n + 0.7))
    else:
        fig = ax.figure
    if null_band is not None:
        ax.axvspan(null_band[0], null_band[1], color=GREY_SCALE['grid'],
                   alpha=0.85, zorder=0)
        ax.text((null_band[0] + null_band[1]) / 2, n - 0.25, null_label,
                ha='center', va='bottom', fontsize=6.5, color=GREY,
                style='italic')
    ax.axvline(0, color=GREY_SCALE['zero'], lw=1.0, zorder=1)
    if ref_line is not None:
        ax.axvline(ref_line, color=GREY_SCALE['guide'], lw=0.9,
                   ls=(0, (4, 3)), zorder=1)
    for yi, (_, row) in enumerate(df.iterrows()):
        v = float(row[value_col])
        c = pos_color if v >= 0 else neg_color
        ax.plot([0, v], [yi, yi], color=c, lw=2.2, alpha=0.85, zorder=2)
        ax.scatter([v], [yi], s=58, color=c, edgecolor='white', lw=0.7,
                   zorder=3)
        v2 = row.get(value2_col) if value2_col is not None else None
        if v2 is not None and pd.notna(v2):
            v2f = float(v2)
            # 第二统计量空心点纵向错位 pair_dy 行 + 细连接线：
            # 两值接近时双点仍可辨（位置横坐标始终真实，不错位造假）
            ax.plot([v, v2f], [yi, yi - pair_dy], color=GREY_SCALE['zero'],
                    lw=0.7, zorder=2)
            ax.scatter([v2f], [yi - pair_dy], s=24, facecolor='none',
                       edgecolor=c, lw=1.2, zorder=3)
        star = ''
        if stars and pval_col is not None and pd.notna(row.get(pval_col)):
            p = float(row[pval_col])
            star = '***' if p < 0.001 else '**' if p < 0.01 else \
                '*' if p < 0.05 else ''
        x_end = v
        if v2 is not None and pd.notna(v2):
            far = max(abs(v), abs(float(v2)))
            x_end = far if v >= 0 else -far
        ax.text(x_end, yi + 0.34, value_fmt.format(v) + star,
                ha='center', fontsize=6.8, color=c if star else GREY,
                fontweight='bold' if star else 'normal',
                bbox=dict(boxstyle='round,pad=0.15', fc='white',
                          ec='none', alpha=0.9), zorder=4)
        # 行标签避让：正行放 0 左侧、负行放 0 右侧（stem 不穿字）
        ax.annotate(str(row[label_col]), xy=(0, yi),
                    xytext=(-8, 0) if v >= 0 else (8, 0),
                    textcoords='offset points', va='center',
                    ha='right' if v >= 0 else 'left',
                    fontsize=7.5, color=NEAR_BLACK, annotation_clip=False)
        if tag_col is not None and pd.notna(row.get(tag_col)):
            ax.text(1.03, yi, str(row[tag_col]),
                    transform=ax.get_yaxis_transform(),
                    fontsize=6.8, color=GREY, va='center', ha='left')
    if tag_col is not None and tag_title:
        ax.text(1.03, n - 0.1, tag_title, transform=ax.get_yaxis_transform(),
                fontsize=6.8, color=GREY, va='bottom', ha='left',
                fontweight='bold')
    ax.set_ylim(-0.6, n - 0.4 + (0.7 if null_band is not None else 0.3))
    ax.set_yticks([])
    for side in ('top', 'right', 'left'):
        ax.spines[side].set_visible(False)
    ax.spines['bottom'].set_color(GREY_SCALE['spine'])
    ax.tick_params(length=2, labelsize=7.5, colors='#444444')
    ax.grid(axis='x', color=GREY_SCALE['grid'], lw=0.6, zorder=0)
    ax.set_axisbelow(True)
    if save:
        save_panel(fig, save, show=show,
                    outdir=kwargs.pop("outdir", "panels"),
                    fmt=kwargs.pop("fmt", "pdf"))
    return fig, ax


# ============================================================
# 20.44 plot_qc_cards — 样本×指标 QC 条形卡片（行=样本，列=指标）
#   源自 fetal_heart draw_fig1i1_qc 实战（GA 色块 + 行对齐多列条形 + 直标数值）
# ============================================================

def plot_qc_cards(metrics, covariate=None, covariate_label=None,
                  covariate_cmap='Blues', row_order=None, formats=None,
                  ranges=True, highlight=None, bar_colors=None,
                  cell_w=1.35, label_w=1.15, figsize=None, save=None,
                  show=None, **kwargs):
    """样本 QC 条形卡片：每行一样本（首列样本名+协变量色块），每指标一列横条
    + 右端数值直标 + 列顶范围注释。全轴隐藏，3 秒可读的"表格化条形图"。

    metrics: DataFrame(index=样本, columns=指标, 数值)。
    covariate: 同 index 的数值 Series（如供体 GA）→ 首列渐变色块 swatch。
    row_order: 行序（默认按 covariate 升序，最小在上；无 covariate 按原序）。
    formats: {指标: 格式串}，如 {'detected_genes': '{:,.0f}'}；缺省 '{:,.0f}'。
    highlight: 需底纹高亮的样本列表。bar_colors: {指标: hex}，缺省 MORLANDI。
    """
    from matplotlib import cm as _cm
    from matplotlib.colors import Normalize as _Normalize
    from matplotlib.gridspec import GridSpec as _GridSpec
    df = metrics.copy()
    if row_order is not None:
        df = df.loc[[s for s in row_order if s in df.index]]
    elif covariate is not None:
        df = df.loc[covariate.loc[df.index].sort_values().index]
    n, m = df.shape
    y = np.arange(n)[::-1]                       # 首行在上
    fmts = formats or {}
    highlight = set(highlight or [])
    bar_colors = bar_colors or {c: MORLANDI[i % len(MORLANDI)]
                                for i, c in enumerate(df.columns)}
    fig = plt.figure(figsize=figsize or (label_w + m * cell_w, 0.28 * n + 0.8))
    gs = _GridSpec(1, m + 1, width_ratios=[label_w] + [cell_w] * m,
                   wspace=0.55, figure=fig)
    # 首列：样本名 + 协变量色块
    axl = fig.add_subplot(gs[0])
    for yy, s in zip(y, df.index):
        axl.text(0.0, yy, str(s), fontsize=7.5, va='center', ha='left',
                 color=NEAR_BLACK)
    if covariate is not None:
        cmap = plt.get_cmap(covariate_cmap)
        norm = _Normalize(float(covariate.loc[df.index].min()),
                          float(covariate.loc[df.index].max()))
        for yy, s in zip(y, df.index):
            axl.barh([yy], [0.26], left=0.58, height=0.52,
                     color=cmap(norm(float(covariate[s]))), lw=0)
        axl.text(0.71, n - 0.55, covariate_label or
                 (covariate.name if hasattr(covariate, 'name') else ''),
                 fontsize=6.5, color=GREY, ha='center', va='bottom')
    axl.set_xlim(0, 1)
    axl.axis('off')
    axl.set_ylim(-0.7, n - 0.3)
    # 指标列
    axes_out = [axl]
    for k, col in enumerate(df.columns):
        ax = fig.add_subplot(gs[k + 1], sharey=axl)
        v = df[col].astype(float)
        for yy, s in zip(y, v.index):
            if s in highlight:
                ax.axhspan(yy - 0.5, yy + 0.5, color='#FCEDEB', zorder=0)
        ax.barh(y, v.values, height=0.60, color=bar_colors[col],
                alpha=0.9, zorder=2)
        for yy, vv in zip(y, v.values):
            ax.text(vv + v.max() * 0.03, yy,
                    fmts.get(col, '{:,.0f}').format(vv),
                    fontsize=6.3, color=GREY, va='center')
        ax.set_title(str(col), pad=15, fontsize=8, loc='left')
        if ranges:
            ax.text(0, 1.008,
                    f'{_fmt_range(v.min())} – {_fmt_range(v.max())}',
                    transform=ax.transAxes, fontsize=6.3, color=GREY)
        ax.set_xlim(0, v.max() * 1.24)
        ax.axis('off')
        axes_out.append(ax)
    if save:
        save_panel(fig, save, show=show,
                    outdir=kwargs.pop("outdir", "panels"),
                    fmt=kwargs.pop("fmt", "pdf"))
    return fig, axes_out


# ============================================================
# 20.45 plot_trend_grid — 样本级小倍数趋势（点径∝n + 标题内嵌统计量）
#   源自 fetal_heart draw_fig2e_hdwgcna_merged / draw_fig2i_temporal 实战
# ============================================================

def plot_trend_grid(data, x, y, by, size_col=None, stat_col=None,
                    pval_col=None, fit='ols', colors=None, highlight=None,
                    shared_xlim=None, shared_ylim=None, ncols=4, cell_fs=7.5,
                    figsize=None, save=None, show=None, **kwargs):
    """小倍数趋势网格：每实体（模块/基因/通路）一面板，样本级散点 + 拟合线；
    点径∝size_col（如每供体细胞数，权重可视化）；标题内嵌 Spearman ρ 与星号。

    data: tidy DataFrame（x=GA 等连续变量, y=得分, by=实体,
    可选 size_col=每点权重 / stat_col,pval_col=预计算统计量，缺省现场算 ρ）。
    fit: 'ols' | 'lowess' | None。highlight 实体红描边+红标题。
    小倍数替代面条图——原始数据与统计量一体呈现（供体级验证标准形态）。
    """
    from scipy.stats import spearmanr
    entities = list(data[by].dropna().unique())
    nrows = int(np.ceil(len(entities) / ncols))
    fig, axes = plt.subplots(nrows, ncols,
                             figsize=figsize or (2.15 * ncols, 1.75 * nrows),
                             squeeze=False)
    highlight = set(highlight or [])
    if colors is None:
        colors = {e: MORLANDI[i % len(MORLANDI)] for i, e in enumerate(entities)}
    elif not isinstance(colors, dict):
        colors = {e: c for e, c in zip(entities, colors)}
    for k, e in enumerate(entities):
        ax = axes[k // ncols][k % ncols]
        sub = data[data[by] == e]
        c = colors.get(e, MORLANDI[0])
        if size_col is not None and len(sub) and sub[size_col].max() > 0:
            s = 10 + 2.4 * np.sqrt(sub[size_col] / sub[size_col].max()) * 5
            s = np.asarray(s, float)
        else:
            s = np.full(len(sub), 12.0)
        emph = e in highlight
        ax.scatter(sub[x], sub[y], s=s, color=c,
                   edgecolor=CONTRAST_RED if emph else 'white',
                   linewidths=1.1 if emph else 0.5, zorder=3)
        if fit and len(sub) >= 3 and sub[x].nunique() >= 2:
            mode = fit
            if mode == 'lowess':
                try:
                    from statsmodels.nonparametric.smoothers_lowess import lowess
                    sm = lowess(sub[y], sub[x], frac=0.8)
                    ax.plot(sm[:, 0], sm[:, 1], color=c, lw=1.6, alpha=0.9,
                            zorder=2)
                    mode = None
                except ImportError:
                    mode = 'ols'
            if mode == 'ols':
                b1, b0 = np.polyfit(sub[x].astype(float),
                                    sub[y].astype(float), 1)
                xs = np.array([sub[x].min(), sub[x].max()], float)
                ax.plot(xs, b0 + b1 * xs, color=c, lw=1.6, alpha=0.9, zorder=2)
        title = str(e)
        if len(sub) >= 3:
            if stat_col is not None:
                rho = float(sub[stat_col].iloc[0])
                _, p_val = spearmanr(sub[x].astype(float), sub[y].astype(float))
            else:
                rho, p_val = spearmanr(sub[x].astype(float), sub[y].astype(float))
            if pval_col is not None:
                p_val = float(sub[pval_col].iloc[0])
            star = '*' if p_val < 0.05 else ''
            title += f'  ρ={rho:+.2f}{star}'
        ax.set_title(title, fontsize=cell_fs, loc='left', pad=3,
                     color=CONTRAST_RED if emph else
                     (_darken_hex(c) if _hex_luma(c) > 170 else c),
                     fontweight='bold' if emph else 'normal')
        if shared_xlim is not None:
            ax.set_xlim(shared_xlim)
        if shared_ylim is not None:
            ax.set_ylim(shared_ylim)
        polish_axes(ax)
        ax.tick_params(labelsize=6.5)
    for k in range(len(entities), nrows * ncols):
        axes[k // ncols][k % ncols].axis('off')
    for row in axes:
        row[0].set_ylabel(str(y), fontsize=7.5)
    for a in axes[-1]:
        if a.axison:
            a.set_xlabel(str(x), fontsize=7.5)
    fig.tight_layout(h_pad=0.7, w_pad=0.5)
    if save:
        save_panel(fig, save, show=show,
                    outdir=kwargs.pop("outdir", "panels"),
                    fmt=kwargs.pop("fmt", "pdf"))
    return fig, axes
