# Evidence: T-01 激活与记录

- CHG: `CHG-20260923-058`
- Task: `T-01`
- Date: 2026-09-24
- Type: command | manual
- Status: PASS
- Commit: `12ae5e9`

## Purpose

把 C 阶段草案由 `delivery/planned/` 激活为执行记录：十三节正文、`checkpoint.md`、`status/<repo>.md`、
`evidence/`，同步 LEDGER 与 planned 索引，再生成执行快照，跑三验证器。

## Method

```bash
git mv delivery/planned/CHG-20260923-058 delivery/active/CHG-20260923-058
mkdir -p delivery/active/CHG-20260923-058/{evidence,status}
python3 scripts/prepare_ai_workspace.py --change CHG-20260923-058
python3 scripts/verify_delivery_governance.py
python3 scripts/verify_agent_entry.py
python3 scripts/verify_skills.py
```

## Actual

### 快照再生成（`prepare_ai_workspace.py --change CHG-20260923-058`）

```
"active_change": "CHG-20260923-058",
"active_change_status": "IMPLEMENTING（2026-09-24 由 `delivery/planned/` 激活并改写为十三节执行记录）",
"active_milestone": "delivery/milestones/M-launch-engineering.md#成功事实全部成立",
"affected_repositories": ["wt-media-desktop", "wt-media-cloud", "wt-media-agent", "wt-media-workspace"],
```

### 三验证器

| 命令 | 读数 |
|---|---|
| `verify_delivery_governance.py` | `ok. Active CHG: CHG-20260923-058` |
| `verify_agent_entry.py` | `ok. 0 warning(s) need review.`；快照 **2159 字符**（约 864 tokens，预算 8000） |
| `verify_skills.py` | `verified 10 skill source files` |

治理器新要求逐条满足：`- Level: M` 独占一行；`- Milestone:` 指向的锚点 `成功事实全部成立`
是按该脚本自己的 `heading_anchors()` 归一化算出来的（`### 成功事实（全部成立）` 去掉标点 ⇒ `成功事实全部成立`）；
LEDGER 表行**只有一条**且与快照的 `Active CHG:` 一致；`delivery/active/` 下**只有一个** CHG 目录；
`active/058/` 下 `change.md` 与 `checkpoint.md` 齐备；因本 CHG 跨多仓，`status/` 三份齐备。

### 定向检查（带分母与阳性对照）

```bash
ls -a delivery/active/                     # 只剩 .gitkeep 与 CHG-20260923-058
git grep -n "planned/CHG-20260923-058\|planned/CHG-20260923-059"   # 0 命中
git grep -o "completed/CHG-20260923-057" | wc -l                   # 阳性对照：12 ⇒ 该 grep 机制非空转
for r in ../wt-media-{agent,desktop,cloud}; do git -C $r grep -n "CHG-20260923-058"; done   # 三仓各 0
```

「0 命中」不是一个空转的 0：同一机制在 `completed/CHG-20260923-057` 上命中 **12** 处。

顺带修掉两处**因激活而变假**的活基线语句（不是笔误，是状态发生了真实变化）：

- 程序总纲 `:4` 状态行与 `:6` 承载 CHG 行，原写「C/D 仍待激活」「CHG-20260923-058（C）、
  CHG-20260923-059（D，均 planned）」——激活后为假，改指 `active/`。
- `delivery/LEDGER.md:14` 的「后续阶段 CHG-058/059 仍在 planned 登记，待激活」同因。

### 提交边界

只暂存本次改动的 11 个路径（`git diff --cached --name-status` 逐条核对）；
工作区里 **6 个与本次无关的既有脏文件**（`AGENT-INDEX.md`、`AGENTS.md`、`CLAUDE.md`、`README.md`、
`delivery/MASTER_IMPLEMENTATION_PLAN.md`、`docs/engineering/specs/agent-workspace-conventions.md`）
提交后**仍是未暂存状态**（`git status --porcelain` 复核），全程未被读写或提交。

## Expected

`active/` 下恰一条记录、快照指向它、三验证器绿、档指无残留、无关脏文件不动。

## Actual（结论）

全部达成。**未做**的一处如实登记：`git grep` 只覆盖**已入库**文件，
忽略区（`.local/`、`target/`、`node_modules/`）不在分母内——它们不是文档，本轮也不需要进分母。

## Follow-Up

- T-02 承接：四处活基线的**日志数字口径**回写（程序总纲 §3 CHG-B、架构基线 §5.8、
  里程碑成功事实 #5、`Cargo.toml` 拒绝注释）与 CHG-057 归档记录顶部的取代注记。
  本条只改了**状态行**，没动任何一个日志数字。
