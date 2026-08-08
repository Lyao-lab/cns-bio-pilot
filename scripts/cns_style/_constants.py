"""_constants — cns_style sub-module"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.colors import LinearSegmentedColormap


# ============================================================
# Palette definitions (Morlandi Nord — user-selected default)
# ============================================================
# Base 8 (for ≤8 categories; #D8DEE9 removed — too light on white background)
MORLANDI = ['#88C0D0', '#BF616A', '#A3BE8C', '#D08770',
            '#B48EAD', '#EBCB8B', '#5E81AC', '#81A1C1']

# Extended 20 (for atlas figures with 10-20+ cell types; low-saturation, harmonious)

# Extended 20 (for atlas figures with 10-20+ cell types; low-saturation, harmonious)
MORLANDI_EXTENDED = MORLANDI + [
    '#7B9E89', '#C9ADA7', '#9A8C98', '#6D6875',
    '#B5838D', '#E5989B', '#8ECAE6', '#83C5BE',
    '#A2836E', '#C6DABF', '#B8B8FF', '#F4ACB7',
]


OKABE_ITO = ['#E69F00', '#56B4E9', '#009E73', '#F0E442',
             '#0072B2', '#D55E00', '#CC79A7', '#000000']


MUTED = '#C8CDD3'          # non-focus clusters

NEAR_BLACK = '#2E3440'     # axis/text color (Morlandi polar-night)

GREY = '#4C566A'           # annotation/subtle text (Morlandi grey)

# Condition colors (reserved for Normal/Disease narrative — NOT for cell types)

# Condition colors (reserved for Normal/Disease narrative — NOT for cell types)
CONDITION_COLORS = {
    'Normal': '#88C0D0',    # cool = quiet (reserved)
    'Disease': '#BF616A',   # warm = active (reserved)
    'Treated': '#A3BE8C',   # recovery
    'Control': '#88C0D0',
    'Stimulated': '#D08770',
}

# Sequential: blue-yellow-red (low-saturation, bioinformatics consensus)

# Sequential: blue-yellow-red (low-saturation, bioinformatics consensus)
EXPR_CMAP = LinearSegmentedColormap.from_list('byr_morlandi',
    ['#5E81AC', '#8FBCD4', '#ECEFF4', '#D08770', '#9B5A5A'], N=256)

# Diverging: blue-white-red (0=white midpoint)

# Diverging: blue-white-red (0=white midpoint)
DIVERGING_CMAP = LinearSegmentedColormap.from_list('log2fc',
    ['#2C5F8D', '#88C0D0', '#FFFFFF', '#D08770', '#8B2C2C'], N=256)

# ForbiddenCity 命名色板 fallback（供函数 18 ForbiddenCityBridge 降级使用）
# fallback hex 为近似值，精确值需安装 omicverse 后 ov.pl.ForbiddenCity

# ForbiddenCity 命名色板 fallback（供函数 18 ForbiddenCityBridge 降级使用）
# fallback hex 为近似值，精确值需安装 omicverse 后 ov.pl.ForbiddenCity
FORBIDDEN_CITY_FALLBACK = {
    '凝夜紫': '#3D3B5A',
    '霁蓝': '#2E5C8A',
    '石英粉红': '#E8B4B8',
    '胭脂紫': '#9D5C6D',
    '藤黄': '#E8B835',
    '青矾绿': '#5C8D5C',
    '朱砂': '#C73E3A',
    '月白': '#B8CCE0',
    '黛色': '#4A4A4A',
    '牙色': '#F0E6D2',
}


# Global figure scale factor — set by set_cns_style_journal()
# 1.0 = generic (notebook/report), 0.7 = nature/cell (compact print)
