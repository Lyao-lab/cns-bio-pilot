#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
cns-bio-pilot api_check — API 实存性自检

用途：每次安装或更新 omicverse（或 scop/pertpy 等）后，跑一遍确认 skill 文档里
提到的 API 在当前环境真实存在。防止"文档写了 ov.xxx.yyy 但新版改名/删除了"
导致的运行时 AttributeError。

用法：
    python scripts/api_check.py                    # 扫描 skill 文档 + 验证 omicverse
    python scripts/api_check.py --skill-dir /path/to/cns-bio-pilot
    python scripts/api_check.py --package omicverse
    python scripts/api_check.py --help

工作流：
  1. 扫描 skill 全部 .md/.json/.py 文件，提取所有 ov.* API 调用
  2. 在当前 Python 环境逐个 hasattr() 检查
  3. 对"已知故意不存在的负结果 API"（白名单）跳过
  4. 报告：哪些存在 / 哪些缺失 / 缺失的修复建议

设计原则：
  - 不硬编码 API 列表——从 skill 文档动态提取，skill 加新 API 自动纳入
  - 白名单管理"故意不存在的负结果"（如 ov.pl.add_labels 文档里标注为不存在）
  - 每条 FAIL 给修复建议（用 dir() 找最接近的真实 API）

退出码：0 = 全部通过；1 = 有 FAIL（缺失 API）
"""
import argparse, os, re, sys, importlib, inspect

# ============================================================
# 已知"故意不存在的负结果 API"白名单
# 这些 API 在 skill 文档里是作为"does NOT exist"的负结果说明出现的，
# 不是错误调用，验证时跳过。
# 每项格式：(api_pattern, reason)
# ============================================================
NEGATIVE_RESULT_WHITELIST = {
    "ov.pl.add_labels": "documented as non-existent (figure_layout.md: use ax.text instead)",
    "ov.pl.get_cmap_seg": "documented as non-existent (use 'Reds' or ov.pl.Forbidden_Cmap)",
    "ov.pl.stacking_vol": "documented as non-existent (use manual gridspec + ov.pl.volcano)",
    "ov.pl.space": "documented as non-existent (use ov.pl.plot_spatial)",
    "ov.io.read_visium": "documented as non-existent (use ov.space.read_visium_10x)",
    "ov.io.read_": "extraction artifact (read_visium_hd truncated by regex)",
    "ov.pp.spatial_neighbors": "documented as moved to ov.space.spatial_neighbors",
    "ov.space.BANKSY": "documented as standalone (not wrapped in ov.space)",
    "ov.space.BINARY": "documented as standalone (not wrapped in ov.space)",
    "ov.space.GraphST": "documented as standalone (not wrapped in ov.space)",
    "ov.space.COMMOT": "documented as no public method (use COMMOT standalone)",
    "ov.single.MetabolityCCC": "documented as misspelling (real: MetaboliteCCC)",
}

# 包名 → import 名 + API 前缀 映射
PACKAGE_MAP = {
    "omicverse": {"import": "omicverse", "prefix": "ov", "attr": "ov"},
}


def extract_apis_from_skill(skill_dir, prefix="ov"):
    """扫描 skill 目录全部 .md/.json/.py，提取所有 {prefix}.* API 调用"""
    apis = set()
    pattern = re.compile(rf"\b{re.escape(prefix)}\.(pp|pl|single|space|bulk|io|plot|read|utils|fm|style)\.[a-zA-Z_][a-zA-Z_0-9]*")
    for root, _, files in os.walk(skill_dir):
        if ".git" in root:
            continue
        for fn in files:
            if not fn.endswith((".md", ".json", ".py")):
                continue
            fp = os.path.join(root, fn)
            try:
                with open(fp, encoding="utf-8") as f:
                    text = f.read()
                for m in pattern.findall(text):
                    pass  # group 只取了中间模块名，重新完整匹配
                for m in re.finditer(rf"\b{re.escape(prefix)}\.(?:pp|pl|single|space|bulk|io|plot|read|utils|fm|style)\.[a-zA-Z_][a-zA-Z_0-9]*", text):
                    apis.add(m.group(0))
            except Exception:
                pass
    return sorted(apis)


def resolve_api(obj, api_str, prefix):
    """把 'ov.pp.qc' 解析成实际属性——逐级 getattr"""
    # 去掉 prefix（如 'ov.'）
    parts = api_str.split(".")
    # parts[0] == prefix（如 'ov'）
    cur = obj
    for part in parts[1:]:
        if not hasattr(cur, part):
            return None, f"{'.'.join(parts[:parts.index(part)+1])} not found"
        cur = getattr(cur, part)
    return cur, None


def find_similar(obj, missing_attr, mod_path):
    """在模块里找最接近 missing_attr 的真实属性名（给修复建议）"""
    try:
        members = [x for x in dir(obj) if not x.startswith("_")]
        # 简单模糊匹配：包含关系
        lower = missing_attr.lower()
        candidates = [x for x in members if lower in x.lower() or x.lower() in lower]
        if not candidates:
            # 首字母/前缀匹配
            candidates = [x for x in members if x[0].lower() == lower[0]]
            candidates = candidates[:5]
        return candidates[:5]
    except Exception:
        return []


def check_apis(skill_dir, package="omicverse"):
    """主检查函数"""
    pkg_info = PACKAGE_MAP.get(package)
    if not pkg_info:
        print(f"❌ 未知包: {package}（支持: {list(PACKAGE_MAP)}）")
        return 1

    # import 包
    try:
        obj = importlib.import_module(pkg_info["import"])
        ver = getattr(obj, "__version__", "?")
        print(f"=== {package} {ver} API 实存性自检 ===")
        print(f"skill 目录: {skill_dir}")
        print()
    except ImportError as e:
        print(f"❌ 无法 import {package}: {e}")
        print(f"   先装包: pip install {package}")
        return 1

    prefix = pkg_info["prefix"]
    apis = extract_apis_from_skill(skill_dir, prefix)
    print(f"从 skill 文档提取 {len(apis)} 个唯一 {prefix}.* API\n")

    ok, missing, whitelisted = [], [], []
    for api in apis:
        if api in NEGATIVE_RESULT_WHITELIST:
            whitelisted.append(api)
            continue
        resolved, err = resolve_api(obj, api, prefix)
        if resolved is not None:
            ok.append(api)
        else:
            missing.append((api, err))

    # 报告
    print(f"{'='*60}")
    print(f"✅ 存在: {len(ok)}")
    print(f"⬜ 白名单（故意不存在的负结果）: {len(whitelisted)}")
    print(f"❌ 缺失（skill 提到但环境不存在）: {len(missing)}")
    print(f"{'='*60}")

    if whitelisted:
        print(f"\n⬜ 白名单 API（跳过——文档里已标注为'不存在/已修正'）:")
        for api in whitelisted:
            print(f"   {api}  — {NEGATIVE_RESULT_WHITELIST[api]}")

    if missing:
        print(f"\n❌ 缺失的 API（需修正 skill 文档或更新白名单）:")
        for api, err in sorted(missing):
            # 找修复建议
            parts = api.split(".")
            mod_path = ".".join(parts[:-1])
            missing_attr = parts[-1]
            try:
                parent = obj
                for part in parts[1:-1]:
                    parent = getattr(parent, part, None)
                    if parent is None:
                        break
                suggestions = find_similar(parent, missing_attr, mod_path) if parent else []
            except Exception:
                suggestions = []
            sug_str = f" → 可能的正确名: {suggestions}" if suggestions else ""
            print(f"   {api}  ({err}){sug_str}")
        print(f"\n修复方式:")
        print(f"  1. 若 API 真实存在但改名 → 更新 skill 文档里的调用")
        print(f"  2. 若 API 确实不存在（文档写错）→ 更正为真实 API 或标注'不存在'")
        print(f"  3. 若是'故意不存在的负结果说明' → 加入本脚本的 NEGATIVE_RESULT_WHITELIST")
        return 1
    else:
        print(f"\n✅ 全部通过——skill 文档里的 {prefix}.* API 在当前环境均真实存在。")
        return 0


def main():
    ap = argparse.ArgumentParser(
        description="cns-bio-pilot API 实存性自检（装/更包后跑一遍）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python scripts/api_check.py                                 # 默认检查 omicverse
  python scripts/api_check.py --package omicverse
  python scripts/api_check.py --skill-dir ~/.agents/skills/cns-bio-pilot

退出码: 0 = 全部通过; 1 = 有缺失 API
        """,
    )
    # 默认 skill 目录：脚本上两级（scripts/ -> skill 根）
    default_skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ap.add_argument("--skill-dir", default=default_skill_dir, help="cns-bio-pilot skill 根目录（默认: 脚本上两级）")
    ap.add_argument("--package", default="omicverse", choices=list(PACKAGE_MAP), help="要检查的包（默认: omicverse）")
    a = ap.parse_args()

    if not os.path.isdir(a.skill_dir):
        print(f"❌ skill 目录不存在: {a.skill_dir}")
        return 1

    return check_apis(a.skill_dir, a.package)


if __name__ == "__main__":
    sys.exit(main())
