#!/usr/bin/env python3
"""check_all — 维护者单入口：一次跑全部结构/一致性/新鲜度机检（2026-10-10 聚合）。

用法：python evals/check_all.py [--skip-desc]
顺序执行（任一 FAIL 即整体退出 1）：
  1. lint_skill        结构规范（frontmatter/死链/孤儿 skill）
  2. consistency_check docs↔code 漂移（plot_*/规则编号/计数对账/.py 存在性）
  3. freshness_check   时效敏感文件 review_by 过期
  4. desc_overlap      （--skip-desc 跳过）子 skill description 语义重叠体检
postcheck / data_sanity / qa_deck / edge_sweep 是**产物级**机检（分析/交付时跑），不在本入口。
"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
STEPS = [("lint", ["lint_skill.py"]),
         ("consistency", ["consistency_check.py"]),
         ("freshness", ["freshness_check.py"])]
if "--skip-desc" not in sys.argv:
    STEPS.append(("desc_overlap", [sys.executable, "desc_overlap.py"]))

fail = 0
for name, cmd in STEPS:
    full = [sys.executable, str(HERE / cmd[0])] if cmd[0].endswith(".py") and cmd[0] != sys.executable else [str(HERE / cmd[0])]
    print(f"\n===== {name} =====")
    r = subprocess.run(full)
    if r.returncode != 0:
        fail = 1
        print(f"❌ {name} FAILED")
print(f"\n{'🚨 check_all: 存在 FAIL' if fail else '✅ check_all: 全部通过'}")
sys.exit(fail)
