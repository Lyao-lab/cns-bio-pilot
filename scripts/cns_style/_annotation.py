"""_annotation — cns_style sub-module"""

import numpy as np
from ._constants import *


# ============================================================
# 9. add_cluster_labels() — on-plot labels with white halo (Nature 2024 style)
# ============================================================

def add_cluster_labels(ax, adata, basis='umap', groupby='celltype', fontsize=7,
                       palette=None):
    """Add cluster labels at median positions with white halo (no adjustText needed).

    This is the 2024-25 Nature/Cell convention: labels directly on the UMAP at
    cluster centroids, with a white stroke halo for readability over dense points.
    """
    import matplotlib.patheffects as pe
    basis_key = f'X_{basis}' if f'X_{basis}' in adata.obsm else basis
    coords = adata.obsm[basis_key]
    categories = adata.obs[groupby].cat.categories

    for i, cat in enumerate(categories):
        mask = (adata.obs[groupby] == cat).values
        if mask.sum() == 0:
            continue
        cx, cy = np.median(coords[mask], axis=0)
        color = NEAR_BLACK
        if palette and cat in palette:
            color = palette[cat]
        ax.text(cx, cy, str(cat), fontsize=fontsize, ha='center', va='center',
                color=color, fontweight='bold', fontfamily='Arial',
                path_effects=[pe.withStroke(linewidth=2.5, foreground='white')])


# ============================================================
# 9b. add_significance_bracket() — p-value annotation
# ============================================================


# ============================================================
# 9b. add_significance_bracket() — p-value annotation
# ============================================================

def add_significance_bracket(ax, x1, x2, pval, y=None, height_frac=0.03):
    """Add bracket + star between two groups. Auto-positions if y not given.

    Args:
        x1, x2: x positions of the two groups
        pval: p-value (determines star count)
        y: y position of bracket (auto = just above data max)
        height_frac: bracket height as fraction of y-range
    """
    if pval < 0.0001: star = '****'
    elif pval < 0.001: star = '***'
    elif pval < 0.01:  star = '**'
    elif pval < 0.05:  star = '*'
    else:              star = 'ns'

    ylim = ax.get_ylim()
    yrange = ylim[1] - ylim[0]
    if y is None:
        y = ylim[1] + yrange * 0.02
    h = yrange * height_frac

    ax.plot([x1, x1, x2, x2], [y, y+h, y+h, y],
            lw=0.8, color=NEAR_BLACK, clip_on=False)
    ax.text((x1+x2)/2, y+h, star, ha='center', va='bottom',
            fontsize=8, color=NEAR_BLACK)
    # Expand ylim to fit bracket
    ax.set_ylim(ylim[0], max(ylim[1], y+h+yrange*0.05))


# ============================================================
# 9c. Manifest functions (paper-level color consistency)
# ============================================================


def volcano_colors():
    """Return color dict for volcano plot (aligned with ov.pl.volcano defaults).

    Usage:
        colors = volcano_colors()
        ax.scatter(..., color=colors['up'])    # significant upregulated
        ax.scatter(..., color=colors['down'])  # significant downregulated
        ax.scatter(..., color=colors['ns'])    # not significant
    """
    return {
        'up': '#e25d5d',     # omicverse up_color (soft coral red)
        'down': '#7388c1',   # omicverse down_color (soft periwinkle blue)
        'ns': '#d7d7d7',     # omicverse normal_color (light grey)
        'ns_alpha': 0.6,     # slightly more visible than before
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


# ============================================================
# 9d. mark_events() — 曲线上标事件（'*' 手工防撞梯，源自 figures4papers）
# ============================================================

def mark_events(ax, x, y, events, dy=0.06, fontsize=7, arrow_lw=0.6, color='#2E3440'):
    """在曲线 y(x) 上标注事件。events: dict {x_value: label}。

    label 里的每个 '*' 把文字再抬高一个 dy*(ylim span)——手工防撞梯（源自 figures4papers）。
    箭头 '-|>'，shrinkA=shrinkB=0；文字白色描边光晕（与 add_cluster_labels 一致）。

    Usage:
        mark_events(ax, months, cumsum, {'2023-03': 'GPT-4*', '2023-12': 'Gemini 1.0**'})
    """
    import matplotlib.patheffects as pe
    x_idx = {t: i for i, t in enumerate(x)}
    y0, y1 = ax.get_ylim()
    for xv, label in events.items():
        if xv not in x_idx:
            continue
        i = x_idx[xv]
        y_pt = float(y[i])
        n_stars = label.count('*')
        ax.annotate(
            label.replace('*', ''),
            xy=(i, y_pt),
            xytext=(i, y_pt + (1 + n_stars) * dy * (y1 - y0)),
            ha='center', va='bottom', fontsize=fontsize, color=color,
            path_effects=[pe.withStroke(linewidth=2.0, foreground='white')],
            arrowprops=dict(arrowstyle='-|>', lw=arrow_lw, color=color,
                            shrinkA=0, shrinkB=0, mutation_scale=6),
        )


# ============================================================
# 9e. stamp_panel() — 面板字母 + 版内标题 + 灰副标题三件套
#     （fetal_heart 62/79 脚本的统一开头，2026-09 实战回灌）
# ============================================================

def stamp_panel(fig, letter, title=None, subtitle=None,
                letter_xy=(0.005, 0.965), title_xy=(0.03, 0.958),
                letter_fs=13, title_fs=13.5, sub_fs=7.6, sub_color=None,
                push_axes=True):
    """面板字母（bold）+ 版内标题 + 灰色方法学副标题，一次性盖上。

    letter: 面板字母（'a' / 't1' / 大 fig 分区子编号均可）。
    title: 版内标题（bold，放字母右侧）。
    subtitle: 方法学副标题（灰字块，挂到标题实测 bbox 下缘之下）。
    push_axes: 把顶边侵入头部区的子图下压（add_axes 精排的画布不受影响——
    只有 axes 顶边真的进入头部区才动）。默认坐标按 ≥8in 宽画布调校。
    返回创建的 Text 对象列表。

    Usage:
        stamp_panel(fig, 't1', 'Gene-set programs',
                    'top-12 genes per set; GO BP ORA, universe n=14,532; BH-FDR')
    """
    made = []
    t = fig.text(*letter_xy, str(letter), fontsize=letter_fs,
                 fontweight='bold', va='top', ha='left', color=NEAR_BLACK)
    made.append(t)
    t_title = None
    if title:
        t_title = fig.text(*title_xy, title, fontsize=title_fs,
                           fontweight='bold', va='top', ha='left',
                           color=NEAR_BLACK)
        made.append(t_title)
    sub_bottom = None
    if subtitle:
        # 副标题挂到标题实测 bbox 下缘之下（短画布上固定 0.928 会与标题相撞）
        sub_y = title_xy[1] - 0.030
        if t_title is not None:
            try:
                fig.canvas.draw()
                r = fig.canvas.get_renderer()
                tb = t_title.get_window_extent(renderer=r)
                sub_y = (tb.y0 - 0.012 * fig.bbox.height) / fig.bbox.height
            except Exception:
                pass
        t_sub = fig.text(title_xy[0], sub_y, subtitle,
                         fontsize=sub_fs, va='top', ha='left',
                         color=sub_color or GREY_SCALE['note'])
        made.append(t_sub)
        try:
            fig.canvas.draw()
            r = fig.canvas.get_renderer()
            sb = t_sub.get_window_extent(renderer=r)
            sub_bottom = sb.y0 / fig.bbox.height
        except Exception:
            sub_bottom = sub_y - 0.03
    # 子图顶边入侵头部区 → 下压（预留 1.2% 呼吸隙；inset 轴用父坐标系，跳过）
    if push_axes and sub_bottom is not None:
        head_bottom = 1.0 - sub_bottom + 0.012
        for ax in fig.axes:
            if ax.get_axes_locator() is not None:
                continue
            pos = ax.get_position()
            if pos.y1 > 1.0 - head_bottom + 1e-6:
                h = pos.height - (pos.y1 - (1.0 - head_bottom))
                if h > 0.05:
                    ax.set_position([pos.x0, pos.y0, pos.width, h])
    return made


# ============================================================
# 9f. layout_labels() — on-plot 标签斥力求解器（两遍 bbox 实测推开）
#     （源自 fetal_heart figstyle.layout_labels，2026-09 实战回灌）
# ============================================================

def layout_labels(fig, ax, texts, max_passes=25):
    """迭代实测 window_extent，把互相重叠的 on-plot 标签沿重叠较小的轴推开。

    texts: 已放在锚点位置的 matplotlib Text 对象列表（如手动放的 cluster 标签）。
    每轮 draw 后取真实 bbox 换算数据坐标半宽（pad 1.16/1.22），pairwise 推开
    （额外 2% 轴距间隙），≤max_passes 轮收敛。不改字号、不加引线。

    Usage:
        layout_labels(fig, ax, ax.texts)   # 或自建 Text 列表
    """
    inv = ax.transData.inverted()
    for _pass in range(max_passes):
        fig.canvas.draw()
        r = fig.canvas.get_renderer()
        boxes = [t.get_window_extent(renderer=r) for t in texts]
        hw, hh = [], []
        for b in boxes:
            (dx0, dy0), (dx1, dy1) = inv.transform([(b.x0, b.y0), (b.x1, b.y1)])
            hw.append(abs(dx1 - dx0) / 2 * 1.16)
            hh.append(abs(dy1 - dy0) / 2 * 1.22)
        hw, hh = np.array(hw), np.array(hh)
        xr = abs(ax.get_xlim()[1] - ax.get_xlim()[0])
        yr = abs(ax.get_ylim()[1] - ax.get_ylim()[0])
        P = np.array([t.get_position() for t in texts])
        moved = False
        for i in range(len(texts)):
            for j in range(i + 1, len(texts)):
                d = P[j] - P[i]
                ox = (hw[i] + hw[j]) - abs(d[0])
                oy = (hh[i] + hh[j]) - abs(d[1])
                if ox > 0 and oy > 0:
                    if abs(d[0]) < 1e-9:
                        d = d + np.array([1e-4, 0.0])
                    if abs(d[1]) < 1e-9:
                        d = d + np.array([0.0, 1e-4])
                    if ox < oy:
                        s = np.sign(d[0]) or 1.0
                        P[i, 0] -= s * (ox / 2 + 0.02 * xr)
                        P[j, 0] += s * (ox / 2 + 0.02 * xr)
                    else:
                        s = np.sign(d[1]) or 1.0
                        P[i, 1] -= s * (oy / 2 + 0.02 * yr)
                        P[j, 1] += s * (oy / 2 + 0.02 * yr)
                    moved = True
        for t, p in zip(texts, P):
            t.set_position((p[0], p[1]))
        if not moved:
            break


# ============================================================
# 9g. direct_label() — 轴端直接标签（显示坐标防撞 stagger）
#     （fetal_heart draw_fig1d2/draw_fig2k2 的右缘标签技巧，2026-09 回灌）
# ============================================================

def direct_label(ax, ys, texts, x=None, side='right', gap_pt=11,
                 offset_pt=5, fontsize=7.5, color=None, leader=True,
                 **text_kw):
    """在轴右（或左）缘给每条线/实体直接标注，像素级强制最小行距防撞。

    ys: 各标签的数据 y 位置；texts: 标签字符串；x: 锚点 x 位置
    （默认轴缘内缩 2%）。把 y 转显示坐标后迭代下推强制相邻间距 ≥ gap_pt
    （且 ≥1.7×行高），差值换算 offset points 交给 annotate。
    leader: 标签被推离锚点超过 ~1.2 行时自动画细引线（端点聚集时保归属）。
    """
    fig = ax.figure
    xlim = ax.get_xlim()
    span = xlim[1] - xlim[0]
    if x is None:
        x = xlim[1] - 0.02 * span if side == 'right' else xlim[0] + 0.02 * span
    pts = ax.transData.transform(np.column_stack([np.full(len(ys), x), ys]))
    order = np.argsort(pts[:, 1])[::-1]          # 自上而下
    # 间距随字号自适应：至少 1.7 倍行高（7.5pt → 12.75pt）
    gap_pt = max(gap_pt, fontsize * 1.7)
    gap_px = gap_pt * fig.dpi / 72
    base = pts[:, 1].copy()
    # 迭代下推直到稳定（单遍链在密集锚点+链式推挤下可能漏对）
    for _ in range(8):
        moved = False
        for k in range(1, len(order)):
            i_prev, i_cur = order[k - 1], order[k]
            if pts[i_prev, 1] - pts[i_cur, 1] < gap_px:
                pts[i_cur, 1] = pts[i_prev, 1] - gap_px
                moved = True
        if not moved:
            break
    inv = ax.transData.inverted()
    out = []
    for i, (yv, lab) in enumerate(zip(ys, texts)):
        dy = (pts[i, 1] - base[i]) * 72 / fig.dpi
        dx = offset_pt if side == 'right' else -offset_pt
        # 引线：标签被推离锚点较远时，细灰线锚定归属（不进 tightbbox 逻辑，
        # 用 plot 而非 annotate 箭头，保持文字 bbox 干净）
        if leader and abs(dy) > fontsize * 1.2:
            sgn = 1 if side == 'right' else -1
            x_px = ax.transData.transform((x, yv))[0]
            start = inv.transform((x_px + sgn * 2 * fig.dpi / 72, base[i]))
            end = inv.transform((x_px + sgn * (offset_pt - 2) * fig.dpi / 72,
                                 pts[i, 1]))
            ax.plot([start[0], end[0]], [start[1], end[1]],
                    color=GREY_SCALE['guide'], lw=0.5, zorder=1,
                    clip_on=False)
        out.append(ax.annotate(lab, xy=(x, yv), xytext=(dx, dy),
                               textcoords='offset points',
                               va='center', fontsize=fontsize,
                               ha='left' if side == 'right' else 'right',
                               color=color if color is not None else NEAR_BLACK,
                               **text_kw))
    return out


