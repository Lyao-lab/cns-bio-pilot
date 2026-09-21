# cns-bio-pilot 评测体系（evals/）

路由/触发回归测试，用于每次修改 SKILL.md 后验证"路由表清晰、触发不误伤"。

## 组成

| 文件 | 作用 |
|---|---|
| `route_cases.yaml` | 路由测试集（30 条：clean / near_miss / negative），判定"用户话术 → 正确子 skill" |
| `trigger_cases.yaml` | 触发测试集（14 条），判定"description → 该/不该触发 cns-bio-pilot"（有 docx/pdf/pptx 等干扰技能在场） |
| `sync_prompts.py` | 从 SKILL.md 重新生成 `prompts/*.md`——**改了 SKILL.md 必跑**，保证评测输入零漂移 |
| `run_eval.py` | 评测器：调用模型 → 打分 → 写 `results/`；有失败退出码为 1，可挂 CI / pre-commit |
| `lint_skill.py` | 结构 lint（本地版 agentskills 规范 + SkillForge doctor）：frontmatter/name 格式/description 长度、引用死链（支持 `skills/` 全路径与 `{}` 花括号模式）、路由表↔目录双向一致、触发语完整性、500 行上限 |
| `desc_overlap.py` | 子 skill description 语义重叠检测（本地版 SkillEvaluator Tier2，char 2~4-gram TF-IDF 余弦），防"描述互相抢触发" |
| `results/` | 每轮结果 JSON（含逐条输出），按时间戳留档 |

## 日常使用（改完 SKILL.md 后）

```bash
cd ~/.agents/skills/cns-bio-pilot/evals
~/miniforge3/envs/sc/bin/python lint_skill.py           # 0. 结构体检（秒级，先跑）
~/miniforge3/envs/sc/bin/python desc_overlap.py         # 0b. description 重叠体检（秒级）
~/miniforge3/envs/sc/bin/python sync_prompts.py        # 1. 同步 prompt
# 2. 跑评测（二选一）：
# a) 有 OpenAI 兼容 API 时，脚本直跑：
EVAL_BASE_URL=https://api.moonshot.cn/v1 EVAL_API_KEY=sk-... EVAL_MODEL=kimi-k2 \
  ~/miniforge3/envs/sc/bin/python run_eval.py --suite route
EVAL_BASE_URL=... EVAL_API_KEY=... EVAL_MODEL=... \
  ~/miniforge3/envs/sc/bin/python run_eval.py --suite trigger
# b) 无 API key 时，agent 驱动：让 ZCode 逐条派子代理执行
#    （每个子代理 Read prompts/<suite>_prompt.md + 替换 {utterance} 回答一行），
#    回收答案存成 answers.json 后打分：
~/miniforge3/envs/sc/bin/python run_eval.py --suite route --from-json answers.json
```

## 判定规则

- route 套件：输出包含期望子 skill ID 即通过；`not_contains` 字段可禁指定兄弟 ID（near-miss 对）；负例需字面输出 `NONE`
- trigger 套件：正例需选中 `cns-bio-pilot`；负例只要**没选** cns-bio-pilot 即通过（选中正确的干扰技能如 docx 也算对）

## 加新用例的时机

- 真实使用中每抓到一次路由错误/误触发 → 补一条 near_miss
- 新增子 skill → 至少 1 条 clean + 与最相近兄弟的 1 条 near_miss
- 用例里的话术尽量用用户的原话，不要书面改写

## 首轮基线（2026-09-21，执行器 = ZCode 子代理，模型 moonshot-kimi/k3）

- route：29/30 → 修复后 30/30。唯一失败 R18 暴露 SKILL.md 真实缺陷：Quick Route 中
  "Stereo-seq→multiomics" 与 "domain→omicverse-spatial" 两条关键词规则打架，
  已在 Quick Route 表下补平台优先级条款（高分平台一律走 multiomics）。
- trigger：14/14（正例全触发、负例全部正确避让，含 T04 与 presentations:pptx 的竞争场景）。

## 后续可接入（需装包，未做）

- NVIDIA SkillEvaluator Tier2：子 skill description 语义重叠的 embedding 检测
- skill-creator run_loop：description 触发率的自动迭代优化
- promptfoo：若有 node 环境可迁到其 YAML/CI 体系
