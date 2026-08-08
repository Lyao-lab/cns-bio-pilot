"""plots_spatial — cns_style sub-module"""

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

