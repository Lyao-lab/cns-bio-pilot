"""plots_ccc — cns_style sub-module"""

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
