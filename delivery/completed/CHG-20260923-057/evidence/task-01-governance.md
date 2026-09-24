# Evidence: T-01 建 active 记录并激活

- CHG: `CHG-20260923-057`
- Task: `T-01`
- Date: 2026-09-24
- Type: command
- Status: PASS

> **归档后追加（2026-09-24，T-18）**：本文是 T-01 当时的**原始记录**，其中的
> `delivery/active/CHG-20260923-057/...` 是 T-01 那一刻的真实路径，**原文一字未改**。本 CHG 已于
> 2026-09-24 归档，记录现位于 `delivery/completed/CHG-20260923-057/`；本文件里 9 处 `active/` 引用
> （`:21`/`:22` 的两条命令、`:46-51` 的 `find` 输出、`:111` 的 README 改写说明）**保留为叙述**，
> 不改成 `completed/`——改了就不是 T-01 的证据了。外部指向 active 的**活链接**已由 T-18 全部改掉
> （见 `change.md` §13 的关闭记录：分母 10 / 2 文件，全部在本记录内部，外部 0）。

## Purpose

把 `delivery/planned/CHG-20260923-057/` 的 PLANNED 草案转为 `delivery/active/` 下的可执行记录，
并令「快照 / LEDGER / active 目录」三者指向同一个 CHG。这是本 CHG 的治理前置，不产生运行时代码。

## Method

```bash
# 0. Start Gate：四仓工作区干净、active 为空、LEDGER 无表行
for r in wt-media-agent wt-media-desktop wt-media-cloud; do git -C ../$r status --porcelain; done

# 1. 移入 active（不留副本）；建子目录
git mv delivery/planned/CHG-20260923-057 delivery/active/CHG-20260923-057
mkdir -p delivery/active/CHG-20260923-057/{evidence,status}

# 2. 改写为十三节执行记录，并写 checkpoint.md / status/*.md
# 3. LEDGER 加裸 id 表行；planned/README.md 的 B 行改 ACTIVE（含链接与「当前无 active CHG」两处已假文案）

# 4. 再生成快照并跑两个验证器
python3 scripts/prepare_ai_workspace.py --change CHG-20260923-057
python3 scripts/verify_agent_entry.py
python3 scripts/verify_delivery_governance.py
```

## Expected

1. `planned/` 下不再有 057 目录（**不留副本**）。
2. 快照 `Active CHG: CHG-20260923-057`，字符数在 8000 预算内。
3. `verify_delivery_governance.py` → `ok. Active CHG: CHG-20260923-057`——因 `Level: M` 会强制校验
   Milestone 引用**及其锚点**。
4. `verify_agent_entry.py` → `ok`，0 warning。

## Actual

**1. 移动后 `planned/` 无残留**

```
$ find delivery/active/CHG-20260923-057 | sort
delivery/active/CHG-20260923-057
delivery/active/CHG-20260923-057/change.md
delivery/active/CHG-20260923-057/evidence
delivery/active/CHG-20260923-057/checkpoint.md
delivery/active/CHG-20260923-057/status
$ ls delivery/planned/ | grep 057 || echo "(已移走，未留副本)"
(已移走，未留副本)
```

`git status --short` 记为 `R  delivery/planned/CHG-20260923-057/change.md -> delivery/active/...`（Rename），
即 Git 认作移动而非「删一份、加一份」。

**2. `prepare_ai_workspace.py` 回显（节选）**

```json
{
  "mode": "workspace-governance-active",
  "active_change": "CHG-20260923-057",
  "active_change_status": "IMPLEMENTING（2026-09-24 激活；此前为 `delivery/planned/` 下的 PLANNED 草案）",
  "active_milestone": "delivery/milestones/M-launch-engineering.md#成功事实全部成立",
  "affected_repositories": ["wt-media-agent", "wt-media-desktop", "wt-media-workspace"]
}
```

**3. 两个验证器**

```
$ python3 scripts/verify_agent_entry.py
execution snapshot: 2145 characters (~858 tokens, budget 8000 characters)
Agent entry verification ok. 0 warning(s) need review.

$ python3 scripts/verify_delivery_governance.py
Delivery governance verification ok. Active CHG: CHG-20260923-057
```

**锚点是**校验过**的，不是摆设**：`verify_delivery_governance.py:80-83` 只在
`separator and anchor.lower() not in heading_anchors(...)` 时报错，而本次 `#成功事实全部成立` 与
里程碑的 `### 成功事实（全部成立）` 经 `heading_anchors()`（去非 `[a-z0-9一-鿿 -]`、空白与连字转 `-`）
归一后相等。用**裸文件路径**（无 `#`）也能过，但那等于放弃了锚点校验——本记录因此取**带锚点**的形式，
比 CHG-056 的写法更严。

**4. 一处与计划的偏差（如实登记）**

计划 T-01 写「`planned/CHG-20260923-057/` 记录移入 active」并同时写「§3 锚点写**里程碑**」。
实测 `planned/CHG-20260923-057/` 里**只有一份 26 行的草案 `change.md`**（无 `checkpoint.md`、无 `evidence/`、
无 `status/`），且草案的锚点段是「程序总纲 §3 CHG-B；ADR-0016；架构基线 §5.8」——**没有** `- Milestone:` 行。
故本 Task 按 `templates/delivery/change.md` **重写**为十三节，并**新增** `checkpoint.md` 与 `status/` 三份，
而不是「移动到新路径后小改」。草案的实质内容（吸收自 CHG-053 Task 6 的范围、明确不做清单）已并入
新记录的 §2/§5，未丢弃。

**5. 被本轮裁定推翻、故**未**延续的草案条款（防止再次出现）**

草案 `:14` 写「Agent 三个 **JSON** 日志文件」、`:17-18` 写 Desktop「单文件 20MB / 保留 14 天 / 总占用 100MB」
并自称「来自程序总纲」。两条实测：
（a）程序总纲 §3 CHG-B（`:46-48`）**只有一行范围、无任何数字**，「来自程序总纲」的归属**不成立**；
（b）用户裁定三明写「不调整 JSONL」，且架构基线 §5.8`:1177` 只给三个**文件名**、从未提 JSON。
⇒ JSON 一条**不采纳**（已写入 §6 D-02），数字按裁定与草案取 20MB/14d/100MB/400MB 并在 T-18 回写
程序总纲 §3 CHG-B，把那个空缺补上（§7 Q-02）。

## Follow-Up

- T-18 需把 20MB / 14 天 / 总量 / 截断标记 / 三文件纯文本写进程序总纲 §3 CHG-B 与架构基线 §5.8/§6.8
  （见上 §5 的 (a)：这些数字今天**没有任何基线**承载）。
- `planned/README.md` 第 3 行原有的「**当前无 active CHG**」在本轮**已变假**，已同批改写为指回 active 路径；
  同理其 B 行的链接由 `CHG-20260923-057/change.md` 改为 `../active/CHG-20260923-057/change.md`
  （链接是读者会**照着点**的东西，属「修」类，照 CHG-060 归档扫描立下的分类规则）。
