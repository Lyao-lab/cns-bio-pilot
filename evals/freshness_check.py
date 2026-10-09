#!/usr/bin/env python3
"""freshness_check — 时效敏感文件的新鲜度机检（2026-10-09，Reviewer C P0-1）。

扫描 references/（含 analysis/）所有带 `> as_of: ... | review_by: ...` 标记的文件：
  - review_by 已过 → ERROR（内容过期，需跑调研 runbook 更新后刷新标记）
  - review_by 30 天内到期 → WARN（排期更新）
无标记的文件视为长青（guards/meta_methodology/stats_convention 等），不检查。
运行：python evals/freshness_check.py（与 lint_skill / consistency_check 同入口习惯）
"""
import re
import sys
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TAG = re.compile(r'^>\s*as_of:\s*([\d-]+)\s*\|\s*review_by:\s*([\d-]+)', re.M)
errors, warns = [], []

for f in sorted((ROOT / 'references').rglob('*.md')):
    m = TAG.search(f.read_text())
    if not m:
        continue
    as_of, review_by = m.group(1), m.group(2)
    today = date.today()
    rb = datetime.strptime(review_by, '%Y-%m-%d').date()
    days = (rb - today).days
    if days < 0:
        errors.append(f'{f.relative_to(ROOT)}  review_by={review_by} 已过期 {-days} 天（as_of={as_of}）→ 跑调研 runbook 更新并刷新标记')
    elif days <= 30:
        warns.append(f'{f.relative_to(ROOT)}  review_by={review_by} 将在 {days} 天内到期（as_of={as_of}）')

for w in warns:
    print('WARN  ', w)
for e in errors:
    print('ERROR ', e)
print(f'\n{len(errors)} ERROR / {len(warns)} WARN')
sys.exit(1 if errors else 0)
