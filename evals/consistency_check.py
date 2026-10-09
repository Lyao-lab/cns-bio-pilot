#!/usr/bin/env python3
"""cns-bio-pilot 内部一致性机检（2026-10-09 新增，补 lint_skill.py 未覆盖的语义漂移）。

检查项（docs ↔ code 漂移，过往实战坑）：
  C1  cns_style 真实 plot_* 函数 vs tool_registry/plotting_reference/figure_guide 声明
      —— 代码有而文档从未提及 = 未接线的新函数；文档有而代码不存在 = 死链/改名。
  C2  SKILL.md frontmatter version 与路由/Key Files 提到的关键 reference 文件存在性。
  C3  dispatch_cheatsheet 规则计数（A/B/C/D/E 系编号连续性，防新增规则编号撞车）。
  C4  路由 Quick Route 提到的 ref:references/xxx.md 文件必须存在。
退出码：有 ERROR 为 1，仅 WARN 为 0。运行：python evals/consistency_check.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
errors, warns = [], []


def err(m): errors.append(m)
def warn(m): warns.append(m)


# ---------- C1: cns_style plot_* drift ----------
cns = ROOT / 'scripts' / 'cns_style'
real = set()
for py in cns.glob('*.py'):
    real |= set(re.findall(r'^def (plot_[a-z_]+)\(', py.read_text(), re.M))

doc_files = [ROOT / 'references' / n for n in
             ('tool_registry.md', 'plotting_reference.md', 'figure_guide.md')]
doc = set()
for f in doc_files:
    doc |= set(re.findall(r'(?<![\w.])plot_[a-z_]+\b', f.read_text()))

# filter obvious non-functions (placeholders)
doc -= {'plot_', 'plot_type', 'plot_xxx'}

missing_doc = real - doc          # code exists, doc silent
missing_code = doc - real         # doc claims, code absent
if missing_doc:
    warn(f'C1 代码有 {len(missing_doc)} 个 plot_* 文档未提及（考虑登记 tool_registry）: '
         + ', '.join(sorted(missing_doc)))
if missing_code:
    err(f'C1 文档声明但代码不存在的 plot_*（死链/改名）: '
        + ', '.join(sorted(missing_code)))

# ---------- C2: version + Key Files existence ----------
sk = (ROOT / 'SKILL.md').read_text()
mv = re.search(r'^\s*version:\s*"([^"]+)"', sk, re.M)
if not mv:
    warn('C2 SKILL.md 无 frontmatter version')
else:
    ver = mv.group(1)
# every `references/...` path mentioned in Key Files must exist
for m in re.findall(r'`(references/[^`\s]+?\.md)`', sk):
    if not (ROOT / m).exists():
        err(f'C2 Key Files 引用不存在的文件: {m}')

# ---------- C3: cheatsheet rule-id continuity (only definition lines "- **[Xn]") ----------
cs = (ROOT / 'references' / 'dispatch_cheatsheet.md').read_text()
for series in 'ABCDE':
    ids = sorted(int(n) for n in
                 re.findall(rf'^- \*\*\[{series}(\d+)\]', cs, re.M))
    if ids and ids != list(range(1, len(ids) + 1)):
        err(f'C3 规则编号 {series} 系不连续/撞车: {ids}')

# ---------- C4: Quick Route ref: targets exist ----------
for m in re.findall(r'`ref:(references/[^`]+?\.md)`', sk):
    if not (ROOT / m).exists():
        err(f'C4 Quick Route 引用不存在的文件: {m}')

# ---------- C5: prose rule counts vs actual（手维护计数必然漂移，机检对账） ----------
actual = {s: len(set(re.findall(rf'^- \*\*\[{s}(\d+)\]', cs, re.M)))
          for s in 'ABCDE'}
for m in re.finditer(r'([A-E])[0-9]+-([A-E])[0-9]+', cs.split('\n', 8)[7] if len(cs.split('\n')) > 7 else ''):
    pass  # (range prose handled by C5b below)
# 5) cheatsheet 头部计数行若写死条数，与实际核对
head = '\n'.join(cs.split('\n')[:10])
for mm in re.finditer(r'(\d+)\s*系\s*(\d+)\s*条', head):
    n_series, n_total = int(mm.group(1)), int(mm.group(2))
    real_total = sum(actual.values())
    if n_total != real_total:
        err(f'C5 计数漂移：头部写 {n_total} 条，实际 {real_total} 条 {actual}')

# ---------- C6: 全文 references/ 死链（SKILL.md + cheatsheet + guards 正文链接） ----------
for fname in ('SKILL.md', 'references/dispatch_cheatsheet.md',
              'references/guards_vs_guides.md'):
    txt = (ROOT / fname).read_text()
    for m in re.findall(r'`(references/[A-Za-z0-9_/.-]+?\.md)`', txt):
        if not (ROOT / m).exists():
            err(f'C6 {fname} 正文引用不存在: {m}')

# ---------- C7: 注入模板规则范围一致（仅限注入模板/规则区块，避免误伤领域卡 C1-C15 等异义编号） ----------
def _inject_sections(txt):
    """取注入模板与规则计数相关区块（Dispatch Injection 节 + 注入模板节）。"""
    parts = []
    for pat in (r'(## ⚠️ Dispatch Injection.*?)(?=\n## )',
                r'(## 注入模板.*?)(?=\n## |\Z)'):
        m = re.search(pat, txt, re.S)
        if m:
            parts.append(m.group(1))
    return '\n'.join(parts) or txt

for fname in ('SKILL.md', 'references/dispatch_cheatsheet.md'):
    txt = _inject_sections((ROOT / fname).read_text())
    for m in re.finditer(r'\b([A-E])(\d+)-\1(\d+)\b', txt):
        s, lo, hi = m.group(1), int(m.group(2)), int(m.group(3))
        if hi > actual[s]:
            err(f'C7 {fname} 注入区块写 {s}{lo}-{s}{hi} 但实际 {s} 系最大编号 {actual[s]}')

# ---------- C8: 文档提到的 .py 必须存在 ----------
scan = [(ROOT / 'SKILL.md', sk), (ROOT / 'references/dispatch_cheatsheet.md', cs)]
for f in (ROOT / 'references').rglob('*.md'):
    scan.append((f, f.read_text()))
for f, txt in scan:
    for m in re.findall(r'`((?:scripts|skills)/[A-Za-z0-9_/.-]+?\.py)`', txt):
        if not (ROOT / m).exists():
            err(f'C8 {f.name} 引用不存在脚本: {m}')

# ---------- report ----------
for w in warns:
    print('WARN  ', w)
for e in errors:
    print('ERROR ', e)
print(f'\n{len(errors)} ERROR / {len(warns)} WARN  |  real plot_*={len(real)} doc={len(doc)}')
sys.exit(1 if errors else 0)
