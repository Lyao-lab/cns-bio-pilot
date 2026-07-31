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
    # pertpy 0.7 → 1.0 breaking changes (documented as removed in perturb-seq/SKILL.md)
    "pt.tl.PseudobulkDE": "documented as removed in pertpy 1.0 (use PseudobulkSpace + PyDESeq2)",
    "pt.tl.PerturbationSignature": "documented as removed in pertpy 1.0 (use Mixscape.perturbation_signature)",
    "pt.tl.perturbation_embedding": "documented as removed in pertpy 1.0 (use CentroidSpace.compute + sc.tl.leiden)",
    "pt.tl.cluster_perturbations": "documented as removed in pertpy 1.0 (use CentroidSpace + scanpy clustering)",
}

# 包名 → import 名 + API 前缀 映射
PACKAGE_MAP = {
    "omicverse": {"import": "omicverse", "prefix": "ov", "attr": "ov"},
    "pertpy":    {"import": "pertpy",    "prefix": "pt", "attr": "pt"},
}


def extract_apis_from_skill(skill_dir, prefix="ov"):
    """扫描 skill 目录全部 .md/.json/.py，提取所有 {prefix}.* API 调用

    支持二级（ov.pp.qc）和三级（ov.pp.ambient.remove_ambient）API。
    模块名覆盖 omicverse (pp/pl/single/space/bulk/io/plot/read/utils/fm/style)
    和 pertpy (tl/pl/tools) 等不同包的命名约定。
    """
    # 包内子模块名集合——按 prefix 区分（omicverse vs pertpy 命名不同）
    if prefix == "pt":
        modules = r"tl|pl|tools|data|datasets|io|utils"
    else:
        modules = r"pp|pl|single|space|bulk|io|plot|read|utils|fm|style|synbio|Agent"
    apis = set()
    # 二级 API: <prefix>.<module>.<name>
    two_level = rf"\b{re.escape(prefix)}\.(?:{modules})\.[a-zA-Z_][a-zA-Z_0-9]*"
    # 三级 API: <prefix>.<module>.<sub>.<name>  （用于 ov.pp.ambient.remove_ambient 这种子包）
    three_level = rf"\b{re.escape(prefix)}\.(?:{modules})\.[a-zA-Z_][a-zA-Z_0-9]*\.[a-zA-Z_][a-zA-Z_0-9]*"
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
                # 先吃三级（更具体），再吃二级；set 自动去重
                for m in re.finditer(three_level, text):
                    apis.add(m.group(0))
                for m in re.finditer(two_level, text):
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


def diff_mode(skill_dir, package="omicverse"):
    """--diff mode: compare installed version vs compat.yaml verified version.

    Reports exactly what changed so you only update what's needed.
    """
    import yaml as _yaml

    compat_path = os.path.join(skill_dir, "compat.yaml")
    if not os.path.isfile(compat_path):
        print("❌ compat.yaml not found — create it first (version declaration)")
        return 1

    with open(compat_path, encoding="utf-8") as f:
        compat = _yaml.safe_load(f)

    if package not in compat:
        print(f"❌ '{package}' not in compat.yaml")
        return 1

    verified = compat[package]["verified_against"]
    compat_range = compat[package].get("compatible_range", "?")
    last_date = compat[package].get("last_verified", "?")

    # Get installed version
    info = PACKAGE_MAP.get(package)
    if not info:
        print(f"❌ '{package}' not in PACKAGE_MAP")
        return 1
    try:
        mod = importlib.import_module(info["import"])
    except ImportError:
        print(f"❌ {package} not installed")
        return 1
    installed = getattr(mod, "__version__", "?")

    print(f"{'='*60}")
    print(f"  {package} version diff check")
    print(f"{'='*60}")
    print(f"  Installed:        {installed}")
    print(f"  Skill verified:   {verified}  (last: {last_date})")
    print(f"  Compatible range: {compat_range}")
    print()

    if installed == verified:
        print("✅ Versions match — no diff needed. Skill docs are current.")
        return 0

    print(f"⚠️  VERSION MISMATCH: installed {installed} ≠ verified {verified}")
    print(f"    Scanning for API surface differences...\n")

    # 1. Get all documented APIs from skill
    prefix = info["prefix"]
    doc_apis = set(extract_apis_from_skill(skill_dir, prefix))

    # 2. Get all actual APIs from installed package (3-level deep scan)
    actual_apis = set()
    for attr in dir(mod):
        if attr.startswith("_"):
            continue
        actual_apis.add(f"{prefix}.{attr}")
        submod = getattr(mod, attr, None)
        if submod is None:
            continue
        # 2nd level
        try:
            for sub_attr in dir(submod):
                if sub_attr.startswith("_"):
                    continue
                full2 = f"{prefix}.{attr}.{sub_attr}"
                actual_apis.add(full2)
                # 3rd level (for sub-packages like ov.pp.ambient.* and classes like ov.space.Deconvolution.*)
                try:
                    sub2 = getattr(submod, sub_attr, None)
                    if sub2 is not None and not callable(sub2):
                        for sub2_attr in dir(sub2):
                            if sub2_attr.startswith("_"):
                                continue
                            actual_apis.add(f"{full2}.{sub2_attr}")
                except Exception:
                    pass
        except Exception:
            pass

    # 3. Compare — use hasattr resolution for "removed" (robust against lazy-load/classes)
    # APIs in skill docs but NOT resolvable in installed (removed/renamed)
    removed = []
    for api in sorted(doc_apis):
        # Skip whitelist entries
        if api in NEGATIVE_RESULT_WHITELIST:
            continue
        if any(api.startswith(w) for w in NEGATIVE_RESULT_WHITELIST):
            continue
        # Resolve via hasattr chain (same as check_apis does)
        resolved, err = resolve_api(mod, api, prefix)
        if resolved is None:
            removed.append(api)

    # APIs in installed but NOT in skill docs (new — potential additions)
    # Only report 2-level APIs (prefix.module.name) that look like public functions
    new_candidates = sorted([a for a in actual_apis - doc_apis
                            if a.count(".") >= 2 and not a.split(".")[-1].startswith("_")])

    # 4. Find files still referencing old version string
    old_version_refs = []
    for root, _, files in os.walk(skill_dir):
        if ".git" in root:
            continue
        for fn in files:
            if not fn.endswith((".md", ".py", ".R", ".json")):
                continue
            fp = os.path.join(root, fn)
            try:
                with open(fp, encoding="utf-8") as f:
                    if verified in f.read():
                        rel = os.path.relpath(fp, skill_dir)
                        old_version_refs.append(rel)
            except Exception:
                pass

    # 5. Report
    print(f"{'─'*60}")
    if removed:
        print(f"\n❌ REMOVED/RENAMED (in skill docs but NOT in {package} {installed}): {len(removed)}")
        for api in removed[:20]:
            print(f"   {api}")
        if len(removed) > 20:
            print(f"   ... and {len(removed)-20} more")
    else:
        print(f"\n✅ No removed APIs — all documented APIs still exist in {installed}")

    if new_candidates:
        print(f"\n🆕 NEW in {installed} (not yet in skill docs): {len(new_candidates)} candidates")
        for api in new_candidates[:30]:
            print(f"   {api}")
        if len(new_candidates) > 30:
            print(f"   ... and {len(new_candidates)-30} more")
    else:
        print(f"\n✅ No significant new APIs detected")

    if old_version_refs:
        print(f"\n📁 Files still referencing '{verified}' ({len(old_version_refs)} files):")
        for ref in old_version_refs:
            print(f"   {ref}")
    else:
        print(f"\n✅ No files reference old version '{verified}'")

    # 6. Verdict
    print(f"\n{'='*60}")
    needs_update = bool(removed) or bool(old_version_refs)
    if needs_update:
        n_files = len(set(
            [os.path.relpath(os.path.join(skill_dir, r), skill_dir) for r in old_version_refs]
        ))
        print(f"  VERDICT: {len(removed)} APIs removed + {n_files} files need version update")
        print(f"  ACTION:  update compat.yaml verified_against to {installed},")
        print(f"           fix removed APIs in docs, optionally document new APIs.")
    else:
        print(f"  VERDICT: Only new APIs (no breaking changes). Update compat.yaml")
        print(f"           verified_against to {installed} and optionally document new APIs.")
    print(f"{'='*60}")

    return 0


def main():
    ap = argparse.ArgumentParser(
        description="cns-bio-pilot API 实存性自检 + 版本差异检测",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python scripts/api_check.py                       # 默认检查全部已配置包（omicverse + pertpy）
  python scripts/api_check.py --package omicverse   # 只检查 omicverse
  python scripts/api_check.py --package pertpy      # 只检查 pertpy
  python scripts/api_check.py --diff                # 版本差异检测（installed vs compat.yaml）
  python scripts/api_check.py --diff --package pertpy
  python scripts/api_check.py --skill-dir ~/.agents/skills/cns-bio-pilot

退出码: 0 = 全部通过; 1 = 有缺失 API / 版本不匹配需更新
        """,
    )
    default_skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ap.add_argument("--skill-dir", default=default_skill_dir, help="cns-bio-pilot skill 根目录")
    ap.add_argument("--package", default=None, choices=list(PACKAGE_MAP) + [None],
                    help=f"要检查的包（默认: 全部 = {list(PACKAGE_MAP)}）")
    ap.add_argument("--diff", action="store_true",
                    help="版本差异检测模式：对比 installed vs compat.yaml，报告精确变化")
    a = ap.parse_args()

    if not os.path.isdir(a.skill_dir):
        print(f"❌ skill 目录不存在: {a.skill_dir}")
        return 1

    if a.diff:
        targets = [a.package] if a.package else ["omicverse"]
        final_rc = 0
        for pkg in targets:
            rc = diff_mode(a.skill_dir, pkg)
            if rc != 0:
                final_rc = 1
        return final_rc

    # Default: full API existence check
    targets = [a.package] if a.package else list(PACKAGE_MAP)
    final_rc = 0
    for pkg in targets:
        print()
        rc = check_apis(a.skill_dir, pkg)
        if rc != 0:
            final_rc = 1
    return final_rc


if __name__ == "__main__":
    sys.exit(main())
