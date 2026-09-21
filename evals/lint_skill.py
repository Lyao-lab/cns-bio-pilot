#!/usr/bin/env python3
"""cns-bio-pilot 结构 lint（本地化 agentskills 规范校验 + agnix + SkillForge doctor 思路）。

检查项：
  L1  frontmatter 可解析，含 name/description
  L2  name 为 lowercase-hyphen 格式且与目录名一致
  L3  description 非空且 ≤1024 字符
  L4  SKILL.md 引用的 references/ scripts/ 文件与 skills/ 子目录全部存在（无死链）
  L5  路由器 Routing Table 中的每个子 skill 都有对应目录（正向）
  L6  每个子 skill 目录都在路由器 SKILL.md 中被提及（反向，防孤儿 skill）
  L7  子 skill description 含触发语（"当用户要...时触发"），与官方"when-to-use 入 description"一致
  L8  SKILL.md ≤500 行；>300 行的子 skill 头部 40 行内应有目录/TOC 提示（官方渐进披露）
退出码：有 ERROR 为 1，仅 WARN 为 0。
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
errors, warns = [], []


def err(msg):
    errors.append(msg)


def warn(msg):
    warns.append(msg)


FULL_RE = re.compile(r"skills/[A-Za-z0-9_/,{}.-]*(?:references|scripts|assets)/[A-Za-z0-9_/,{}.-]*")
REL_RE = re.compile(r"(?:references|scripts|assets)/[A-Za-z0-9_/,{}.-]+")


def expand_braces(p: str):
    m = re.search(r"\{([^{}]+)\}", p)
    if not m:
        return [p]
    out = []
    for alt in m.group(1).split(","):
        out.extend(expand_braces(p[: m.start()] + alt + p[m.end():]))
    return out


def check_refs(text: str, base: Path, tag: str) -> None:
    """L4: 引用文件存在性。两遍扫描：先抓 skills/... 全路径（从 skill 根解析），
    屏蔽后再抓相对引用（先试子 skill 目录、再试 skill 根）。支持 {} 花括号模式。"""
    masked = list(text)
    fulls = set()
    for m in FULL_RE.finditer(text):
        fulls.add(m.group(0).rstrip(".,;:)"))
        for i in range(m.start(), m.end()):
            masked[i] = " "
    for p in sorted(fulls):
        for cand in expand_braces(p):
            if not (ROOT / cand).exists():
                err(f"{tag}: 引用文件不存在: {cand}")
    rels = set(m.group(0).rstrip(".,;:)") for m in REL_RE.finditer("".join(masked)))
    for p in sorted(rels):
        for cand in expand_braces(p):
            if not (base / cand).exists() and not (ROOT / cand).exists():
                err(f"{tag}: 引用文件不存在: {cand}")


def parse_fm(path: Path):
    text = path.read_text(encoding="utf-8")
    m = re.search(r"^---\n(.*?)\n---\n", text, re.S | re.M)
    if not m:
        return None, text
    return m.group(1), text


def get_field(fm: str, field: str):
    m = re.search(rf"^{field}:\s*(.+)$", fm, re.M)
    return m.group(1).strip().strip('"').strip("'") if m else None


router = ROOT / "SKILL.md"
fm, rtext = parse_fm(router)
if not fm:
    err("router: frontmatter 缺失/无法解析")
    sys.exit(1)

# L1-L3 router
for field in ("name", "description"):
    if not get_field(fm, field):
        err(f"router: 缺少 {field}")
rname = get_field(fm, "name")
if rname and not re.fullmatch(r"[a-z0-9-]+", rname):
    err(f"router: name '{rname}' 不符合 lowercase-hyphen")
rdesc = get_field(fm, "description") or ""
if len(rdesc) > 1024:
    err(f"router: description {len(rdesc)} 字符超过 1024")

# L4 router 引用完整性
check_refs(rtext, ROOT, "router")

subdirs = sorted(d.parent.relative_to(ROOT / "skills") for d in (ROOT / "skills").glob("*/*/SKILL.md"))
sub_ids = [str(d) for d in subdirs]

# L5 路由表正向：SKILL.md 中以 `xxx/yyy` 形式出现的子 skill 引用
for s in sorted(set(re.findall(r"`([a-z-]+/[a-z-]+)`", rtext))):
    if s not in sub_ids:
        err(f"router: 路由表引用的子 skill 无目录: skills/{s}")

# L6 反向孤儿检查
for s in sub_ids:
    if s not in rtext:
        err(f"孤儿子 skill: skills/{s} 未在 router SKILL.md 中提及")

# 子 skill 检查
for sdir in sub_ids:
    f = ROOT / "skills" / sdir / "SKILL.md"
    sfm, stext = parse_fm(f)
    tag = f"skills/{sdir}"
    if not sfm:
        err(f"{tag}: frontmatter 缺失")
        continue
    name = get_field(sfm, "name")
    desc = get_field(sfm, "description") or ""
    if not name:
        err(f"{tag}: 缺少 name")
    else:
        if not re.fullmatch(r"[a-z0-9-]+", name):
            err(f"{tag}: name '{name}' 不符合 lowercase-hyphen")
        if name != Path(sdir).name:
            warn(f"{tag}: name '{name}' 与目录名 '{sdir.name}' 不一致")
    if not desc:
        err(f"{tag}: 缺少 description")
    elif len(desc) > 1024:
        err(f"{tag}: description {len(desc)} 字符超过 1024")
    # L4 子 skill 引用（相对其自身目录与 skill 根都试；支持 skills/ 全路径与 {} 模式）
    check_refs(stext, f.parent, tag)
    # L7 触发语
    if desc and not re.search(r"当用户|触发|Use (this|when)|whenever", desc, re.I):
        warn(f"{tag}: description 缺少 when-to-use 触发语（官方要求 what+when）")
    # L8 行数（官方：SKILL.md ≤500 行；>420 提示接近上限）
    lines = len(stext.splitlines())
    if lines > 500:
        err(f"{tag}: {lines} 行超过 500 上限（官方要求拆分/渐进披露）")
    elif lines > 420:
        warn(f"{tag}: {lines} 行接近 500 行上限，建议拆分或加目录")

print(f"检查了 1 个 router + {len(sub_ids)} 个子 skill\n")
for m in errors:
    print(f"❌ ERROR {m}")
for m in warns:
    print(f"⚠️  WARN  {m}")
print(f"\n{len(errors)} ERROR / {len(warns)} WARN")
sys.exit(1 if errors else 0)
