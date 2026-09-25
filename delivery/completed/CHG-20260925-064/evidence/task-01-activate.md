# Evidence: T-01 激活

- CHG: `CHG-20260925-064`
- Task: `T-01`
- Date: 2026-09-25
- Type: command
- Status: PASS
- 提交：见本文件末「提交边界」

## Purpose

把本 CHG 落到 `delivery/active/`，并让「活动记录 ↔ `LEDGER.md` ↔ 执行快照」三者一致。
激活是**有判据**的动作：三个文件各自被人读、被脚本读，写错一个字就会打红门禁。

## 1. 动作与产物

| 动作 | 结果 |
|---|---|
| 建 `delivery/active/CHG-20260925-064/{change.md,checkpoint.md,evidence/}` | 三个条目存在（`ls -1` 输出见 §3） |
| `LEDGER.md` 表行由占位行改为本 CHG 行 | 见 §2 |
| `python3 -B -X pycache_prefix=/tmp/pyc-none scripts/prepare_ai_workspace.py --change CHG-20260925-064` | `exit=0`，`mode=workspace-governance-active`、`active_change=CHG-20260925-064`、`active_milestone=null`、`affected_repositories=["wt-media-workspace"]` |

`active_milestone: null` 与 §1 的散文锚点一致——Level S 不挂 Milestone（`verify_delivery_governance.py:119` 只对 `Level: M/L` 强制 `- Milestone:`）。

## 2. `LEDGER` 表行逐字比对（判据：`verify_product_master_alignment.py:306-311`）

该脚本要求 `LEDGER.md` 里出现**逐字等于** `| <CHG> | <title> | <status> | <repo> |` 的行，其中三段都从 `change.md` 现场解析（`：`/`:` 两种标题分隔、dash 与 blockquote 两种字段形式都接受）。

独立复算（不调脚本、直接按同一正则解析两侧）：

```
expected row: | CHG-20260925-064 | 权威冲突与重复落点处置——按单一落点收口 | IMPLEMENTING | wt-media-workspace |
present in LEDGER: True
```

`LEDGER.md:9` 的实际内容与该期望行**逐字相同**。

另：`verify_delivery_governance.py:37` 的 `LEDGER_ROW_RE` 要求表行**以** `| CHG-… |` **开头**，故历史叙述段里提到 CHG id 不会（也不应）被读成第二个 active CHG。

## 3. §7 Pending Questions 的形状（判据：`verify_product_master_alignment.py:300`）

该脚本只接受**标题后紧跟字面 `None.`** 这一种形态（表格不算）：

```
pending-questions shape ok: True
```

## 4. 门禁与套件读数

时间 2026-09-25 19:36:11 CST；原始输出 `artifacts/t01-gate-readings.out`（本次为**一次运行内顺序取数**，六门禁 + 套件在同一份输出里）。

| 判据 | 读数 |
|---|---|
| `verify_delivery_governance.py` | `exit=0` — `Active CHG: CHG-20260925-064` |
| `verify_agent_entry.py` | `exit=0` — `0 warning(s)`，快照 **1916 字符** |
| `verify_skills.py` | `exit=0` — `verified 10 skill source files` |
| `verify_m0_config.py` | `exit=0` |
| `verify_product_master_alignment.py` | `exit=0` |
| `verify_m2_acceptance.py` | `exit=0`（附注：真实 MySQL 与 BitBrowser 证据须另行记录，与本 CHG 无关） |
| `python3 -m unittest discover -s tests -q` | `Ran 75 tests` / `OK`（`exit=0`） |

**一处必须分清的口径**（否则会读成「两个数矛盾」）：快照体积有两个**不同的单位**在同一份输出里——

```
verify_agent_entry.py  → 1916 characters   （脚本按 len(str) 计，字符）
wc -c .ai/CURRENT_CONTEXT.md → 1958        （按字节计，UTF-8 多字节）
```

两者都对，差 42 是中文标点的多字节所致。**记的是字符数**（预算 8000 也是字符），与 CHG-063 记法一致。**CHG-063 的关闭读数是 1919 字符**（同一有活动 CHG 态），本 CHG 为 1916——差额来自标题长度不同，不是文件异常。

## 5. 三仓工作区基线（本次记录，收尾按同一命令复测）

```
$ git -C ../wt-media-cloud status --porcelain
?? dump.rdb
$ git -C ../wt-media-agent status --porcelain
（空）
$ git -C ../wt-media-desktop status --porcelain
（空）
```

`dump.rdb` 是 cloud 下**未跟踪**的 88 字节 Redis 空转储，CHG-062 与 CHG-063 都已登记过（mtime `2026-09-24 17:19:16`，早于本 CHG）。**这次留下的是基线本身**——CHG-063 的 AC-12 之所以只能事后推证，就是因为开工时没记这一行。

## 6. 提交边界

| 文件 | 是否本 Task 产物 |
|---|---|
| `delivery/active/CHG-20260925-064/**`（新增） | 是 |
| `delivery/LEDGER.md`（表行） | 是 |
| `.ai/CURRENT_CONTEXT.md`（生成物） | 是 |
| `CLAUDE.md`、`docs/engineering/specs/agent-workspace-conventions.md` | **否**——2026-09-24 入口重构遗留的工作区编辑，归 T-02 单独提交（`change.md` §6 D-06） |

## 7. 未覆盖 / 未判定

- 本 Task **不验证** `verify_agent_entry.py` 诸判据的判别力（本 Task 未改任何判据；判别力由各 Task 自己的变异对照承载）。
- 本 Task **不覆盖** `verify_m2_acceptance.py` 的真实 MySQL / BitBrowser 证据——该脚本自己声明那部分须另行记录，与激活无关。
