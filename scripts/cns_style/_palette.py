"""_palette — cns_style sub-module"""

import numpy as np
from matplotlib.colors import to_rgb
from ._constants import *
from ._helpers import _check_ov, _lighten_color


# ============================================================
# 6. apply_5plus1_palette(categories, focus_list)
# ============================================================
def apply_5plus1_palette(categories, focus_list, base_palette=None, accent=None):
    """≤5 named colors + 1 accent; everything else = grey.

    Args:
        categories: list of all category names (e.g. cell types)
        focus_list: which categories to highlight (≤6)
        base_palette: color list (default MORLANDI)
        accent: accent color for 6th focus item (default '#BF616A')

    Returns:
        dict {category: color} ready for sc.pl.* palette= argument
    """
    if base_palette is None:
        base_palette = MORLANDI
    if accent is None:
        accent = '#BF616A'

    result = {}
    for i, cat in enumerate(focus_list[:5]):
        result[cat] = base_palette[i % len(base_palette)]
    if len(focus_list) > 5:
        result[focus_list[5]] = accent
    for cat in categories:
        if cat not in result:
            result[cat] = MUTED
    return result


# ============================================================
# 7. optical_margin(ax, pad_fraction=0.15)
# ============================================================

# ============================================================
# 18. ForbiddenCityBridge + palette_from_names — 命名色板
# ============================================================
class ForbiddenCityBridge:
    """ov.pl.ForbiddenCity() 命名色板桥：omicverse 可用则用精确色，否则降级 fallback。

    设计目标：脚本在最小环境（无 omicverse）中不因色板缺失而崩溃。
    fallback hex 为近似值，精确值需 ov.pl.ForbiddenCity（omicverse）。

    Usage:
        b = ForbiddenCityBridge()
        color = b.get('霁蓝')          # fallback 为 '#2E5C8A'
        names = b.available_names      # 中文色名列表（优先 ov，否则 fallback）
    """
    def __init__(self):
        self._fb = None
        try:
            import omicverse as ov
            self._fb = ov.pl.ForbiddenCity()
        except Exception:
            self._fb = None  # 无 omicverse → 走 FORBIDDEN_CITY_FALLBACK

    def get(self, name):
        """Return hex (str) for a Chinese color name (ov exact, else fallback).

        ov 2.3.1 的 get_color() 返回 1 行 DataFrame（含 color_html 列），
        这里统一提取为 hex 字符串；ov 版本 API 差异则降级 fallback。
        """
        if self._fb is not None:
            try:
                res = self._fb.get_color(name)
                if hasattr(res, 'iloc'):          # DataFrame → 取 color_html
                    return str(res['color_html'].iloc[0])
                if isinstance(res, str):
                    return res
            except Exception:
                pass  # ov 版本 API 差异 → 降级 fallback
        if name in FORBIDDEN_CITY_FALLBACK:
            return FORBIDDEN_CITY_FALLBACK[name]
        raise KeyError(
            f"Color '{name}' not found. Available: {self.available_names}")

    @property
    def available_names(self):
        """List of Chinese color names (ov first, else fallback keys)."""
        if self._fb is not None:
            for attr in ('color_pd', 'color'):
                try:
                    res = getattr(self._fb, attr)
                    if hasattr(res, 'iloc') and 'name' in res.columns:
                        return list(res['name'])
                    if isinstance(res, dict):
                        return [v['name'] for v in res.values()]
                except Exception:
                    continue
        return list(FORBIDDEN_CITY_FALLBACK.keys())



def palette_from_names(celltypes, color_names):
    """Map cell types to named-palette hex → {celltype: hex}.

    内部实例化 ForbiddenCityBridge（omicverse 可用则精确色，否则近似 fallback）。

    Usage:
        palette_from_names(['T_cell', 'B_cell'], ['霁蓝', '藤黄'])
        # → {'T_cell': '#2E5C8A', 'B_cell': '#E8B835'}   (fallback 近似值)
    """
    bridge = ForbiddenCityBridge()
    if len(color_names) < len(celltypes):
        print(f"⚠️  palette_from_names: {len(color_names)} colors for "
              f"{len(celltypes)} cell types — 不足部分未映射，请补齐 color_names.")
    return {ct: bridge.get(name) for ct, name in zip(celltypes, color_names)}


# ============================================================
# 19b. is_dark / alpha_ramp / focus_ramp — 颜色工具（源自 figures4papers）
# ============================================================

def is_dark(hex_color, threshold=128):
    """True if luminance (0.299R+0.587G+0.114B) < threshold → bar/cell 上用白字，否则黑字。

    Usage:
        label_color = 'white' if is_dark(bar_color) else 'black'
    """
    c = hex_color.lstrip('#')
    r = int(c[0:2], 16)
    g = int(c[2:4], 16)
    b = int(c[4:6], 16)
    return 0.299*r + 0.587*g + 0.114*b < threshold


def alpha_ramp(hex_color, n, lo=0.25, hi=1.0):
    """同一色相的 n 个 RGBA 元组，alpha 从 hi→lo 线性递减：**首项最实，末项最透明**。

    消融/组件对比用：数据按"完整模型在前、消融越多越靠后"排列后直接 zip 使用——
    完整模型=hi(实)，去掉组件越多越透明（信息编码在 alpha 里）。
    """
    base = to_rgb(hex_color)
    alphas = np.linspace(hi, lo, n)
    return [(base[0], base[1], base[2], a) for a in alphas]


def focus_ramp(focus_hex, base_hex, n, lighten_step=0.11):
    """[focus_hex] + (n-1) 个逐步提亮的 base_hex（复用 _helpers._lighten_color）。

    '本方法 vs 基线' 用：焦点饱和、基线可辨识的单色渐褪（比全灰好在基线仍可指认）。
    返回列表第 0 项即 focus_hex 原样，其余为 _lighten_color 的 RGB 元组（0-1 floats）。
    """
    return [focus_hex] + [_lighten_color(base_hex, amount=(i + 1) * lighten_step)
                          for i in range(n - 1)]


# ============================================================
# 19. save_panel(fig, name, ...) — 统一 save 入口
# ============================================================
