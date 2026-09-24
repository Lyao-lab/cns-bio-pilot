# -*- coding: utf-8 -*-
"""plots_domain 四新图型合成数据渲染回归（plots_domain.py 20.47）。

运行：PYTHONPATH=<skill>/scripts python scripts/tests/render_domain_20260924.py
输出：scripts/tests/renders_20260924/T1-T4*.png（视觉回归基线，.gitignore 定向豁免）
来源：15 领域 506 篇 CNS 文献调研回灌（references/figure_templates.md §5）。
"""
import sys
import pathlib
import numpy as np
import pandas as pd
import matplotlib

matplotlib.use('Agg')
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from cns_style import (set_cns_style_journal, plot_sankey, plot_cnv_heatmap,
                       plot_axis_gradient, plot_clone_expansion)

set_cns_style_journal('nature')
rng = np.random.default_rng(42)
outdir = str(pathlib.Path(__file__).resolve().parent / 'renders_20260924')


def main():
    # T1 Sankey：3x3 转移矩阵（命运流/OT 转变矩阵形态）
    flows = pd.DataFrame({
        'Quiescent': {'Quiescent': 5, 'Activated': 30, 'Matrix': 3},
        'Activated': {'Quiescent': 2, 'Activated': 8, 'Matrix': 22},
        'Cycling': {'Quiescent': 1, 'Activated': 12, 'Matrix': 6},
    }).T
    plot_sankey(flows, min_flow=0.01, save='T1_sankey', outdir=outdir, fmt='png')

    # T2 CNV 热图：200 细胞 x 800 基因（10 染色体），恶性组带 amp/del block
    n_cells, n_genes = 200, 800
    chrom = pd.Series([f'{(i // 80) + 1}' for i in range(n_genes)])
    groups = pd.Series(['Malignant'] * 120 + ['Non-malignant'] * 80)
    cnv = pd.DataFrame(rng.normal(0, 0.25, (n_cells, n_genes)),
                       index=[f'c{i}' for i in range(n_cells)],
                       columns=[f'G{i}' for i in range(n_genes)])
    cnv.iloc[:120, 100:220] += 1.1
    cnv.iloc[:120, 500:580] -= 1.0
    plot_cnv_heatmap(cnv, chrom=chrom, groups=groups, save='T2_cnv',
                     outdir=outdir, fmt='png')

    # T3 轴梯度：3 信号沿距离 0-300µm 衰减（zonation/边界带形态）
    rows = []
    for name, base in [('GeneA', 0.8), ('GeneB', 0.3), ('GeneC', 0.1)]:
        d = rng.uniform(0, 300, 1200)
        v = base * np.exp(-d / 80) + rng.normal(0, 0.12, len(d))
        rows += [{'dist_um': dd, 'expr': vv, 'signal': name}
                 for dd, vv in zip(d, v)]
    plot_axis_gradient(pd.DataFrame(rows), x='dist_um', y='expr',
                       hue='signal', norm='each',
                       xlabel='Distance from vessel (µm)',
                       landmark_label='vessel', save='T3_axis_gradient',
                       outdir=outdir, fmt='png')

    # T4a/T4b 克隆扩增：composition + track
    recs = []
    for ctype, rate in [('CD8_Tex', 0.8), ('CD8_Tn', 0.1), ('Treg', 0.5)]:
        for cid in range(60):
            size = int(rng.geometric(1 - rate * 0.5)) * \
                (int(rate * 50) if rng.random() < rate else 1)
            recs.append({'clone_id': f'{ctype}_cl{cid}', 'celltype': ctype,
                         'size': max(1, min(size, 500))})
    plot_clone_expansion(pd.DataFrame(recs), clone_col='clone_id',
                         group_col='celltype', mode='composition',
                         save='T4a_clone_comp', outdir=outdir, fmt='png')
    tr = []
    for cid in range(40):
        growth = rng.uniform(0.5, 3.0)
        for t, tp in enumerate(['D0', 'D7', 'D28']):
            tr.append({'clone_id': f'cl{cid}', 'timepoint': tp,
                       'size': max(1, int(5 * growth ** t *
                                          rng.uniform(0.7, 1.3)))})
    plot_clone_expansion(pd.DataFrame(tr), clone_col='clone_id',
                         group_col='timepoint', mode='track', top_n=6,
                         save='T4b_clone_track', outdir=outdir, fmt='png')
    print('render_domain_20260924: ALL PASS')


if __name__ == '__main__':
    main()
