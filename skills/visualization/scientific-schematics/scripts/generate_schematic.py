#!/usr/bin/env python
"""纯代码科学示意图模板库（matplotlib + networkx）。

5 类模板，JSON 参数驱动，无需任何 AI API：
  flow                - 分析流程图（水平箭头流，>6 步自动换行）
  pathway             - 信号通路级联（节点 + 带标签箭头）
  feedback            - 反馈环路（正/负反馈，环形布局）
  comparison          - 左右对比图（Control vs Treatment / Normal vs Disease）
  graphical_abstract  - 三栏图形摘要（Input → Process → Output）

用法：
  python generate_schematic.py --template feedback_loop --params params.json -o output.png
  python generate_schematic.py --template flow --params '{"steps":[...]}' -o out.pdf
  python generate_schematic.py --template comparison            # 用默认示例参数

配色：Morlandi 色板 + Navy 标题色（与 cns_style 的 cns-bio-light preset 一致）。
"""
import argparse
import json
import os
import sys

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# ---------------------------------------------------------------------------
# 全局样式常量（与 cns-bio-pilot 库统一配色）
# ---------------------------------------------------------------------------
MORLANDI = ['#3C5488', '#E64B35', '#00A087', '#4DBBD5', '#F39B7F', '#8491B4']
TITLE_COLOR = '#1F3A5F'   # Navy，cns-bio-light preset 标题色
ARROW_COLOR = '#666666'
FONT_FAMILY = 'DejaVu Sans'

ARROW_STYLE = '->,head_width=0.3,head_length=0.6'


# ---------------------------------------------------------------------------
# 通用工具
# ---------------------------------------------------------------------------
def clean_axes(ax):
    """背景白色、隐藏 spines、无刻度。"""
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_facecolor('white')


def add_title(ax, text, y=0.94):
    """统一标题样式：Navy、16pt、bold。"""
    if text:
        ax.text(0.5, y, text, transform=ax.transAxes, ha='center', va='center',
                fontsize=16, fontweight='bold', color=TITLE_COLOR,
                family=FONT_FAMILY)


def draw_arrow(ax, x1, y1, x2, y2, color=ARROW_COLOR, lw=1.8, rad=0.0):
    """统一箭头：FancyArrowPatch，arrowstyle 全局一致。"""
    ax.add_patch(mpatches.FancyArrowPatch(
        (x1, y1), (x2, y2), arrowstyle=ARROW_STYLE,
        mutation_scale=16, color=color, lw=lw,
        connectionstyle=f"arc3,rad={rad}"))


def node_color(params, idx):
    """取节点颜色（color 索引 → MORLANDI），越界回退到索引取模。"""
    c = params.get('color', idx)
    if isinstance(c, str):
        return c
    return MORLANDI[int(c) % len(MORLANDI)]


def box(ax, cx, cy, w, h, text, fc, ec='none', fs=10, fw='normal', lw=1.0,
        tc='white', rounded=True, alpha=1.0):
    """圆角矩形节点（FancyBboxPatch）+ 居中文本。"""
    if rounded:
        boxstyle = f"round,pad=0.02,rounding_size=0.08"
    else:
        boxstyle = "square,pad=0.02"
    ax.add_patch(mpatches.FancyBboxPatch(
        (cx - w / 2, cy - h / 2), w, h,
        boxstyle=boxstyle, fc=fc, ec=ec, lw=lw, alpha=alpha,
        mutation_aspect=1.0))
    ax.text(cx, cy, text, ha='center', va='center', fontsize=fs,
            fontweight=fw, color=tc, family=FONT_FAMILY)


def resolve_params(raw, default):
    """raw 为 None → 默认示例；否则浅合并（用户字段覆盖默认）。"""
    if raw is None:
        return dict(default)
    merged = dict(default)
    merged.update(raw)
    return merged


# ---------------------------------------------------------------------------
# 模板 1：分析流程图（水平箭头流，>6 步自动换行成 2 行蛇形）
# ---------------------------------------------------------------------------
DEFAULT_FLOW = {
    "steps": ["QC", "Cluster", "Annotate", "DE", "CCC", "Spatial"],
    "title": "Analysis pipeline",
}


def template_flow(params, ax):
    p = resolve_params(params, DEFAULT_FLOW)
    steps = p.get('steps') or DEFAULT_FLOW['steps']
    add_title(ax, p.get('title'))

    n = len(steps)
    box_h = 0.16
    gap = 0.045
    if n <= 6:
        # 单行水平流
        box_w = min(0.13, (0.92 - (n - 1) * gap) / n)
        total_w = n * box_w + (n - 1) * gap
        x0 = (1 - total_w) / 2
        y = 0.5
        for i, s in enumerate(steps):
            cx = x0 + i * (box_w + gap) + box_w / 2
            box(ax, cx, y, box_w, box_h, s, MORLANDI[i % 6], fs=10, fw='bold')
            if i < n - 1:
                draw_arrow(ax, cx + box_w / 2 + 0.004, y,
                           cx + box_w / 2 + gap - 0.004, y)
    else:
        # 2 行蛇形：第 1 行左→右，第 2 行右→左
        k = (n + 1) // 2
        row1, row2 = steps[:k], steps[k:]
        box_w = min(0.13, (0.92 - (max(len(row1), len(row2)) - 1) * gap) / max(len(row1), len(row2)))
        y1, y2 = 0.68, 0.28

        def row_xs(row, y):
            total_w = len(row) * box_w + (len(row) - 1) * gap
            x0 = (1 - total_w) / 2
            return [x0 + i * (box_w + gap) + box_w / 2 for i in range(len(row))]

        xs1 = row_xs(row1, y1)
        xs2 = row_xs(row2, y2)
        for i, s in enumerate(row1):
            box(ax, xs1[i], y1, box_w, box_h, s, MORLANDI[i % 6], fs=10, fw='bold')
            if i < len(row1) - 1:
                draw_arrow(ax, xs1[i] + box_w / 2 + 0.004, y1,
                           xs1[i + 1] - box_w / 2 - 0.004, y1)
        # 蛇形：第 2 行从右到左
        for j, s in enumerate(row2):
            idx = len(row2) - 1 - j
            box(ax, xs2[idx], y2, box_w, box_h, s, MORLANDI[(k + j) % 6], fs=10, fw='bold')
            if j < len(row2) - 1:
                draw_arrow(ax, xs2[idx] - box_w / 2 - 0.004, y2,
                           xs2[idx - 1] + box_w / 2 + 0.004, y2)
        # 行间连接箭头：第 1 行末 → 下方第 2 行首（蛇形对接）
        draw_arrow(ax, xs1[-1], y1 - box_h / 2 - 0.01,
                   xs1[-1], y2 + box_h / 2 + 0.01, rad=0.0)


# ---------------------------------------------------------------------------
# 模板 2：信号通路级联（自动布局 + 带标签箭头）
# ---------------------------------------------------------------------------
DEFAULT_PATHWAY = {
    "nodes": [
        {"id": "A", "label": "CXCL12+ Fibro", "color": 0},
        {"id": "B", "label": "CXCR4+ Mac", "color": 2},
        {"id": "C", "label": "M2 activation", "color": 1},
    ],
    "edges": [
        {"from": "A", "to": "B", "label": "CXCL12-CXCR4"},
        {"from": "B", "to": "C", "label": "activates"},
    ],
    "title": "Signaling pathway",
}


def template_pathway(params, ax):
    p = resolve_params(params, DEFAULT_PATHWAY)
    nodes = p.get('nodes') or DEFAULT_PATHWAY['nodes']
    edges = p.get('edges') or DEFAULT_PATHWAY['edges']
    add_title(ax, p.get('title'))

    # 简单自动布局：拓扑排序分层。若图无环且边延"每一层向右"推进则水平排列；
    # 兜底：按节点原顺序水平均布（保持因果方向 A→B→C）。
    pos = {}
    try:
        import networkx as nx
        G = nx.DiGraph()
        for nd in nodes:
            G.add_node(nd['id'])
        for e in edges:
            G.add_edge(e['from'], e['to'])
        try:
            layers = list(nx.topological_generations(G))
        except nx.NetworkXUnfeasible:
            layers = [[nd['id'] for nd in nodes]]
        max_layer = max(len(ly) for ly in layers)
        for li, layer in enumerate(layers):
            y = 0.5 + (li - (len(layers) - 1) / 2) * 0.22
            xs = np.linspace(0.18, 0.82, len(layer))
            for xi, nid in zip(xs, layer):
                pos[nid] = (xi, y)
    except ImportError:
        # 无 networkx 时的兜底：水平均布
        xs = np.linspace(0.18, 0.82, len(nodes))
        for i, nd in enumerate(nodes):
            pos[nd['id']] = (xs[i], 0.5)

    # 画节点（椭圆）
    for nd in nodes:
        cx, cy = pos[nd['id']]
        w = max(0.16, 0.012 * len(nd.get('label', nd['id'])) + 0.10)
        h = 0.13
        ax.add_patch(mpatches.FancyBboxPatch(
            (cx - w / 2, cy - h / 2), w, h,
            boxstyle="round,pad=0.02,rounding_size=0.1",
            fc=node_color(nd, 0), ec='none'))
        ax.text(cx, cy, nd.get('label', nd['id']), ha='center', va='center',
                fontsize=10, color='white', family=FONT_FAMILY)

    # 画带标签箭头
    for e in edges:
        x1, y1 = pos[e['from']]
        x2, y2 = pos[e['to']]
        draw_arrow(ax, x1, y1, x2, y2)
        if e.get('label'):
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2 + 0.05
            ax.text(mx, my, e['label'], ha='center', va='center',
                    fontsize=8, fontstyle='italic', color=ARROW_COLOR,
                    family=FONT_FAMILY)


# ---------------------------------------------------------------------------
# 模板 3：反馈环路（环形布局 + 弧形箭头 + 正/负反馈标记）
# ---------------------------------------------------------------------------
DEFAULT_LOOP = {
    "loop_type": "positive",
    "nodes": [
        {"id": "F", "label": "Fibroblast", "color": 0},
        {"id": "M", "label": "Macrophage", "color": 2},
    ],
    "edges": [
        {"from": "F", "to": "M", "label": "CXCL12"},
        {"from": "M", "to": "F", "label": "TGFβ"},
    ],
    "title": "Feedback loop",
}


def template_feedback(params, ax):
    p = resolve_params(params, DEFAULT_LOOP)
    nodes = p.get('nodes') or DEFAULT_LOOP['nodes']
    edges = p.get('edges') or DEFAULT_LOOP['edges']
    loop_type = p.get('loop_type', 'positive')
    add_title(ax, p.get('title'))

    # 环形布局：极坐标算位置
    n = len(nodes)
    ang = np.linspace(np.pi / 2, np.pi / 2 + 2 * np.pi, n, endpoint=False)
    pos = {}
    for i, nd in enumerate(nodes):
        a = ang[i]
        pos[nd['id']] = (0.5 + 0.30 * np.cos(a), 0.5 + 0.26 * np.sin(a))

    # 节点（圆形）
    for nd in nodes:
        cx, cy = pos[nd['id']]
        ax.add_patch(plt.Circle((cx, cy), 0.085, fc=node_color(nd, 0), ec='none'))
        ax.text(cx, cy, nd.get('label', nd['id']), ha='center', va='center',
                fontsize=10, color='white', family=FONT_FAMILY)

    # 弧形箭头（沿环形弯曲）+ edge label
    for e in edges:
        x1, y1 = pos[e['from']]
        x2, y2 = pos[e['to']]
        draw_arrow(ax, x1, y1, x2, y2, rad=0.3)
        if e.get('label'):
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            ax.text(mx, my, e['label'], ha='center', va='center',
                    fontsize=8, fontstyle='italic', color=ARROW_COLOR,
                    family=FONT_FAMILY)

    # 中心：正/负反馈标记
    if loop_type == 'negative':
        sign, sc = '⊖', '#4DBBD5'
    else:
        sign, sc = '+', '#E64B35'
    ax.add_patch(plt.Circle((0.5, 0.5), 0.055, fc='white', ec=sc, lw=2.0))
    ax.text(0.5, 0.5, sign, ha='center', va='center', fontsize=18,
            fontweight='bold', color=sc, family=FONT_FAMILY)


# ---------------------------------------------------------------------------
# 模板 4：左右对比图（Control vs Treatment / Normal vs Disease）
# ---------------------------------------------------------------------------
DEFAULT_COMPARISON = {
    "left": {"title": "Normal", "items": ["Low fibrosis", "Quiescent FB", "Few immune"]},
    "right": {"title": "Disease", "items": ["High fibrosis", "Activated FB", "Mac infiltrate"]},
    "title": "Normal vs Disease",
}


def _draw_panel(ax, cx, cy, w, h, title, items, fc, emphasize=False):
    if emphasize:
        ax.add_patch(mpatches.FancyBboxPatch(
            (cx - w / 2, cy - h / 2), w, h,
            boxstyle="round,pad=0.02,rounding_size=0.06",
            fc='#FDE8E8', ec='none'))
    box(ax, cx, cy + h / 2 - 0.05, w - 0.02, 0.09, title,
        fc, fs=12, fw='bold', rounded=False)
    for i, it in enumerate(items):
        ax.text(cx - w / 2 + 0.03, cy - h / 2 + 0.10 + i * 0.07, f'• {it}',
                ha='left', va='center', fontsize=10, color='#333333',
                family=FONT_FAMILY)


def template_comparison(params, ax):
    p = resolve_params(params, DEFAULT_COMPARISON)
    left = p.get('left') or DEFAULT_COMPARISON['left']
    right = p.get('right') or DEFAULT_COMPARISON['right']
    add_title(ax, p.get('title'))

    # 左右两栏 + 中间分隔线
    ax.plot([0.5, 0.5], [0.12, 0.82], color='#CCCCCC', lw=1.2, ls='--', zorder=1)
    _draw_panel(ax, 0.25, 0.5, 0.42, 0.55, left.get('title', 'Left'),
                left.get('items', []), MORLANDI[0])
    _draw_panel(ax, 0.75, 0.5, 0.42, 0.55, right.get('title', 'Right'),
                right.get('items', []), MORLANDI[1], emphasize=True)


# ---------------------------------------------------------------------------
# 模板 5：三栏图形摘要（Input → Process → Output）
# ---------------------------------------------------------------------------
# 默认 icon 用 DejaVu Sans 可渲染的符号（⚙/★/▷ 等）；
# 若环境字体支持 emoji（如系统装有 emoji 字体），也可在 params 中传 emoji 字符。
DEFAULT_ABSTRACT = {
    "columns": [
        {"title": "Input", "icon": "▷", "items": ["Patient samples"]},
        {"title": "Method", "icon": "⚙", "items": ["scRNA-seq", "Spatial"]},
        {"title": "Finding", "icon": "★", "items": ["FB subtypes", "CXCL12 axis"]},
    ],
    "title": "Graphical Abstract",
}


def template_graphical_abstract(params, ax):
    p = resolve_params(params, DEFAULT_ABSTRACT)
    cols = p.get('columns') or DEFAULT_ABSTRACT['columns']
    add_title(ax, p.get('title'))

    n = len(cols)
    col_w = 0.26
    gap = 0.05
    total_w = n * col_w + (n - 1) * gap
    x0 = (1 - total_w) / 2
    y_top, y_bottom = 0.72, 0.22
    for i, c in enumerate(cols):
        cx = x0 + i * (col_w + gap) + col_w / 2
        # 标题框（带 icon）
        label = f"{c.get('icon', '')} {c.get('title', '')}".strip()
        box(ax, cx, y_top, col_w, 0.10, label, MORLANDI[i % 6], fs=12, fw='bold')
        # 条目列表
        for j, it in enumerate(c.get('items', [])):
            ax.text(cx, y_bottom + (len(c.get('items', [])) - 1) / 2 * 0.055 - j * 0.055,
                    f'• {it}', ha='center', va='center', fontsize=10,
                    color='#333333', family=FONT_FAMILY)
        # 栏间箭头
        if i < n - 1:
            draw_arrow(ax, cx + col_w / 2 + 0.005, y_top,
                       cx + col_w / 2 + gap - 0.005, y_top)


# ---------------------------------------------------------------------------
# 模板注册表
# ---------------------------------------------------------------------------
TEMPLATES = {
    'flow': template_flow,
    'pathway': template_pathway,
    'feedback': template_feedback,
    'comparison': template_comparison,
    'graphical_abstract': template_graphical_abstract,
}
TEMPLATE_ALIASES = {
    'feedback_loop': 'feedback',
    'loop': 'feedback',
    'flow_diagram': 'flow',
    'pathway_diagram': 'pathway',
    'comparison_diagram': 'comparison',
    'graphical': 'graphical_abstract',
    'abstract': 'graphical_abstract',
}
DEFAULT_FIGSIZE = {
    'flow': (10, 6),
    'pathway': (10, 6),
    'feedback': (10, 6),
    'comparison': (10, 6),
    'graphical_abstract': (12, 5),
}


def resolve_template(name):
    key = name.lower().replace('-', '_')
    if key in TEMPLATES:
        return key
    if key in TEMPLATE_ALIASES:
        return TEMPLATE_ALIASES[key]
    sys.exit(f"Error: unknown template '{name}'. "
             f"Available: {', '.join(sorted(TEMPLATES))} "
             f"(aliases: feedback_loop, flow_diagram, pathway_diagram, comparison_diagram)")


def load_params(raw):
    if raw is None:
        return None
    s = raw.strip()
    if s.startswith('{') or s.startswith('['):
        return json.loads(s)
    if os.path.exists(s):
        with open(s, 'r', encoding='utf-8') as f:
            return json.load(f)
    sys.exit(f"Error: params '{raw}' 既不是 JSON 字符串也不是存在的文件路径。")


def main():
    parser = argparse.ArgumentParser(
        description='纯代码科学示意图模板库（matplotlib + networkx，无 AI API 依赖）。')
    parser.add_argument('--template', required=True,
                        help='模板名：flow | pathway | feedback | comparison | graphical_abstract')
    parser.add_argument('--params', default=None,
                        help='参数：JSON 文件路径或内联 JSON 字符串；省略则用默认示例参数')
    parser.add_argument('-o', '--output', default='schematic.png',
                        help='输出文件路径（按后缀决定 .png/.pdf/.svg），默认 schematic.png')
    parser.add_argument('--dpi', type=int, default=300, help='输出 DPI，默认 300')
    args = parser.parse_args()

    key = resolve_template(args.template)
    params = load_params(args.params)
    if params is None:
        print(f"[generate_schematic] 未提供 --params，使用模板 '{key}' 的默认示例参数。")

    fig = plt.figure(figsize=DEFAULT_FIGSIZE[key])
    ax = fig.add_axes([0, 0, 1, 1])
    clean_axes(ax)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    TEMPLATES[key](params, ax)

    out = args.output
    if not out.lower().endswith(('.png', '.pdf', '.svg')):
        out += '.png'
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    fig.savefig(out, dpi=args.dpi, facecolor='white')
    print(f"[generate_schematic] 已保存：{out} (dpi={args.dpi})")


if __name__ == '__main__':
    main()