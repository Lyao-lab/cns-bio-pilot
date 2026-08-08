"""_palette — cns_style sub-module"""

from ._constants import *
from ._helpers import _check_ov


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
# 19. save_panel(fig, name, ...) — 统一 save 入口
# ============================================================
