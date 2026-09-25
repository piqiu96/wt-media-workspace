# T-02 — 边界成文与可删量实测

- CHG: `CHG-20260925-066`
- Task: T-02 边界成文 ＋ 实测可删量
- 日期: 2026-09-25
- 前置: T-01 已提交（`7e3c8c4`）

## 1. 先写后实现的判据串

按计划「判据串先写后实现」，T-04 的 `check_completed_has_boundary` 要匹配的标记串在**本 Task 写定**，
T-04 只实现、不另定：

```text
delivery/completed/README.md 中必须出现一行（沿用 verify_agent_entry.py 的机读键形状：
行首 `-`、CJK 全角冒号、目标反引号包裹、行末锚定）：

    - 归档边界：`READ-ONLY`
```

正则：`^-\s*归档边界：\s*`READ-ONLY`\s*$`（与 `verify_agent_entry.py:45` 的
`MACHINE_KEY_RE = ^-\s*正文：\s*`(?P<target>[^`]+)`\s*$` 同形）。
`check_archive_readonly` 的判据面同时写定：扫**已跟踪的 `scripts/*.py`**，AST 找对字符串字面量
以 `delivery/completed/` 或 `completed/` 前缀开头的**写**操作（`write_text`／`open(...,'w')`／
`mkdir`／`shutil.*`），白名单外即报。

## 2. 边界落点（唯一落点 ＋ 三处不矛盾）

| 落点 | 动作 | 读数 |
|---|---|---|
| `delivery/completed/README.md` | **新建**——边界唯一落点 | 含标记串 `- 归档边界：\`READ-ONLY\``（1 处）；「已知例外」段点名 `verify_m3_acceptance.py` |
| `AGENT-INDEX.md` §8 | 补一句边界 ＋ 指落点，**声明不复述其正文** | 3 行 |
| `MASTER_IMPLEMENTATION_PLAN.md` §3 历史词汇段后 | 补「『保持原样』与『移除』不矛盾」的消歧 ＋ 指落点 | 1 段 |
| `README.md:51` | 消歧：把 `Remove …records` 改写为「移出 `active/` 与 `LEDGER.md`，记录本身不删不改」 | 1 行 |

## 3. 可删量实测（分母 ＝ §4 F-01 的 698 文件 / 10,736,581 B）

原始输出 `artifacts/t02-deletable-measure.out`。判据：候选 ＝ 原始捕获/可重放类
（`.out`／`.log`／`.txt`／`.json`／`.patch`）＋ `.pyc`，**扣除**硬排除包
`CHG-20260916-052/evidence/m3-e3-acceptance-20260923`；再逐文件判「是否被归档 `.md` 引用」。

| 分类 | 判定 | files | bytes | 占归档 |
|---|---|---|---|---|
| (A) 有真引用 → 保留 | 同 CHG 内 basename／部分路径命中，或跨 CHG 的 **CHG 限定路径**命中 | 158 | 630,808 | 5.9% |
| (B) 仅同名碰撞 → 可删 | 只在**别的** CHG 里出现同名裸 basename | 1 | 1,801 | 0.0% |
| (C) 无任何引用 → 可删 | 341 篇 `.md` 全无命中 | 41 | 138,755 | 1.3% |
| **可删合计 (B)+(C)** | | **42** | **140,556** | **1.3%** |

**结论：删除这一步的结构性上限是 1.3%。** 归档体量落在政策明确保护的三类里：
`.png` 4,566,847（42.5%，视觉缺陷的唯一判据）、CHG-052 的包 5,922,113（55.2%，M3 签收的唯一证据
且脚本读取面仍是活依赖）、手写记录 981,058（9.1%，`change.md`／`checkpoint.md`）。
用户 2026-09-25 就该读数裁定 D-05：**删 1.3%，不碰 CHG-052 包**。

### 3.1 粗读 vs 细读（方法学更正，如实登记）

第一版按**全局 basename** 匹配，报「158 个候选被引用」；第二版加**同 CHG 限定**后（同 CHG 内命中，
或跨 CHG 必须写出 CHG 限定的路径），保留侧仍是 158，可删从 41 变 42——**只差 1 个文件**。

⇒ 第一版中 `[base-only]` 的含义是「按 basename 而非完整路径命中」，而其中**绝大多数是本 CHG 内**的
真引用。我一度据此推断「同名碰撞普遍」（`t04-gate-readings.out` 在 063／064／065 都存在），
**实测碰撞只有 1 例**。判据采用细读版，但该结论的量级被我高估——如实记下，不留「已发现重大问题」的印象。

## 4. F-01 的一处自纠

`change.md` §4 F-01 初稿写「原始机器捕获合计 7,958,694 B ＝ 74.1%」，是**拼装的、不是量的**。
逐类求和实测为 **7,989,554 B ＝ 74.4%**（差 30,860 B / 0.3pp），已就地更正。

## 5. 门禁读数

见 `artifacts/t02-gate-readings.out`。

## 6. 本 Task 变更文件

新建：`delivery/completed/README.md`、本记录、`artifacts/t02-deletable-measure.out`、
`artifacts/t02-gate-readings.out`。
修改：`AGENT-INDEX.md`、`delivery/MASTER_IMPLEMENTATION_PLAN.md`、`README.md`、`change.md`。
**未删任何文件**（删除在 T-05）；未改任何归档记录的正文；未改三仓任何文件。
