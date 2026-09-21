#!/usr/bin/env python3
"""从 SKILL.md 重新生成评测用 prompt，保证评测输入与线上路由规则零漂移。

用法:  python sync_prompts.py
产出:  prompts/route_prompt.md   (含 {utterance} 占位符)
       prompts/trigger_prompt.md
"""
import re
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent / "SKILL.md"
PROMPTS = Path(__file__).resolve().parent / "prompts"

SUB_SKILLS = [
    "single-cell/omicverse-pipeline",
    "single-cell/scop",
    "single-cell/rna-velocity",
    "single-cell/perturbation",
    "single-cell/research-planner",
    "spatial/omicverse-spatial",
    "spatial/deconvolution",
    "spatial/multiomics",
    "spatial/proteomics",
    "general-bio/omicverse-bulk",
    "visualization/figure-production",
    "visualization/scientific-schematics",
    "presentation/manuscript-writing",
    "presentation/scientific-slides",
    "presentation/web-report",
]

# 触发测试中的干扰技能（与真实客户端同时在场的技能保持一致）
DISTRACTORS = [
    ("browser-use:control-browser", "浏览器自动化：打开网页、点击、填表、截图、抓取渲染后的页面内容"),
    ("documents:docx", "Word 文档的创建、编辑、格式保留与文本提取"),
    ("pdf:pdf", "PDF 报告生成，以及现有 PDF 的提取、合并、拆分"),
    ("presentations:pptx", "PPT 演示文稿的创建、编辑、读取与文本提取"),
    ("spreadsheets:xlsx", "Excel/CSV 表格的读取、编辑、修复与创建"),
    ("computer-use:computer-use", "操作原生桌面应用与操作系统 GUI"),
]

ROUTE_TEMPLATE = """你是 cns-bio-pilot 的路由器。阅读下面的路由规则，针对用户请求选择唯一一个最合适的子 skill。

# 输出要求（严格遵守）
- 只输出一行：选中的子 skill ID，必须从下方列表中原样选择
- 若请求与所有子 skill 都无关，输出 NONE
- 不要输出任何解释、标点或多余字符

# 可选子 skill ID
{skill_list}

# 路由规则（摘自 SKILL.md 的 Quick Route 与 Routing Table 原文）
{sections}

用户请求：{{utterance}}
"""

TRIGGER_TEMPLATE = """你是一个 agent 客户端，当前加载了以下技能。针对用户的这句话，决定调用哪个技能。

# 输出要求（严格遵守）
- 只输出一行：要调用的技能 name
- 若没有任何技能适用，输出 NONE
- 不要输出任何解释

# 可用技能（name: description）
{skill_list}

用户请求：{{utterance}}
"""


def main() -> int:
    text = SKILL.read_text(encoding="utf-8")

    m = re.search(r"^---\n(.*?)\n---\n", text, re.S | re.M)
    if not m:
        sys.exit("SKILL.md 缺少 frontmatter")
    fm = m.group(1)
    desc = re.search(r"^description:\s*(.+)$", fm, re.M)
    if not desc:
        sys.exit("frontmatter 缺少 description")

    sec = re.search(
        r"^(## Quick Route.*?)(?=^## Environments)", text, re.S | re.M
    )
    if not sec:
        sys.exit("未找到 Quick Route 段落，SKILL.md 结构可能已变化")
    sections = sec.group(1).strip()

    missing = [s for s in SUB_SKILLS if s not in text]
    if missing:
        print(f"[warn] 以下子 skill ID 未在 SKILL.md 中出现，请同步 SUB_SKILLS: {missing}")

    skill_lines = "\n".join(f"- {s}" for s in SUB_SKILLS)
    route = ROUTE_TEMPLATE.format(skill_list=skill_lines, sections=sections)
    (PROMPTS / "route_prompt.md").write_text(route, encoding="utf-8")

    trig_lines = [f"- cns-bio-pilot: {desc.group(1).strip()}"]
    trig_lines += [f"- {n}: {d}" for n, d in DISTRACTORS]
    trigger = TRIGGER_TEMPLATE.format(skill_list="\n".join(trig_lines))
    (PROMPTS / "trigger_prompt.md").write_text(trigger, encoding="utf-8")

    print(f"OK  route_prompt.md   {len(route)} chars")
    print(f"OK  trigger_prompt.md {len(trigger)} chars")
    return 0


if __name__ == "__main__":
    sys.exit(main())
