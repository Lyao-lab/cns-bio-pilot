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
