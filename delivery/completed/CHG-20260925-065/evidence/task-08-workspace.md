# T-08 — wt-media-workspace 入口文件补机读键

Task：workspace 的 `CLAUDE.md`／`AGENTS.md` 补机读键 `- 正文：\`AGENT-INDEX.md\``，使 workspace 臂由红转绿。
改前锚：**`23eeaa6`**（T-07 记录的提交，即 T-08 改前的 workspace 状态）。凡「改前」读数一律锚此，不用 `HEAD`——本 Task 一提交，`HEAD` 就是改好的文件（理由见 `task-05-cloud.md` §2 与 `change.md` §14 第 14 项）。

## 1. 门禁读数

| 仓 | 改前 | 现在 |
|---|---|---|
| cloud | 0 | 0 |
| agent | 0 | 0 |
| desktop | 0 | 0 |
| **workspace** | **3** | **0** |
| **合计** | **3** | **0** |

**四仓 0 ERROR / 0 WARN** —— 本 CHG 的中心验收条件达成。改前三条逐字（`artifacts/t08-gate-before.out`）：

```
ERROR workspace: AGENTS.md declares no rule body: expected `- 正文：`<file>``
ERROR workspace: CLAUDE.md declares no rule body: expected `- 正文：`<file>``
ERROR workspace: CLAUDE.md:9 restates a rule without naming AGENT-INDEX.md: 本仓库**不是**运行时代码仓：…
```

`check_rule_text_duplication` 分母 `97 rule sentence(s) across 11 file(s) in 4 repositories` —— 与 T-07 同分母，本 Task 未增删可比较的规则句。

## 2. 三处改动（`git diff` 全文即本节，5 增 1 删）

1. **两个文件各加一行机读键**，位置与三仓一致（H1 之下、第一个 H2 之前）：`- 正文：\`AGENT-INDEX.md\``。
2. **`CLAUDE.md:9` 由规则句改为指针句**。原句同时是一条规则（`不存放`／`不得`）和一条事实，而**该事实的唯一落点早就在 `AGENT-INDEX.md` §1**——实测 `AGENT-INDEX.md:23` `## 1. 本仓库定位` 的第 6 行即 `- **不拥有**：运行时代码、服务运行代码、构建产物、临时文件。`，第 9 行即三仓路径。故这是**改写为指针，不是搬家**：内容没有移动到新地方，它本来就在那里，被删的是第二份。

改后（引 `CLAUDE.md:9` 全文，用代码块括起——它的链接是相对 `CLAUDE.md` 的位置，在本文件里**不是**指针）：

```
本仓库**不拥有**运行时代码、服务运行代码、构建产物或临时文件；运行时代码位于 `../wt-media-cloud`、`../wt-media-agent`、`../wt-media-desktop`。仓库职责边界的唯一落点是 [`AGENT-INDEX.md`](AGENT-INDEX.md) §1。
```

**`AGENTS.md` 只增不减**——它的对应内容（`## 红线` 段）本来就是指针写法，未复述任何规则。

## 3. 阳性对照（活体真树，非 fixture）

T-04 的变异对照做在 `tests/` 的 fixture 上。本 Task 另在**真树**上做一次，因为 workspace 是四仓里最后一个由红转绿的臂：删掉 `AGENTS.md` 的机读键 → 门禁报 `ERROR workspace: AGENTS.md declares no rule body`、`exit=1`；还原后 `cmp` 逐字节相同、门禁回 0（`artifacts/t08-live-control.out`）。

第二条对照锚在**改前提交 `23eeaa6`**：把两文件还原成改前版本 → 恰报出上面那三条、`exit=1`；还原 → `exit=0` 且逐字节相同（`artifacts/t08-gate-before.out`）。

⇒ workspace 的红→绿是**判据真的闭上了**，不是门禁变瞎了。两条对照各有一个可失败的分支，且都在同一次运行里报了出。

## 4. 指针预算与规则词判据（T-03 改正后的 §3 口径）

| 文件 | 行数 | 字节 | H2 | 机读键 | 规则词行 |
|---|---|---|---|---|---|
| `CLAUDE.md` | 30 | 1796 | 3（`项目概览`／`权威源`／`红线`） | `:3` | 1（`:30` 红线句，**同现** `AGENT-INDEX.md` ✔） |
| `AGENTS.md` | 24 | 1296 | 2（`权威源`／`红线`） | `:3` | 1（`:22` 红线句，**同现** `AGENT-INDEX.md` ✔） |

三仓参照件各 11 行 / 656 B / 1 H2。workspace 更大**不是措辞松**：多出的 H2 与篇幅在解释一件运行仓不存在的事实——**同一个 `AGENT-INDEX.md` 在 workspace 是治理正文、在运行仓是三层索引**，同名两角色。这条边界本身写在 `AGENT-INDEX.md` 并已在 §14 登记。

**唯一的规则词行是两个文件末尾的红线段**，内容相同，且都是「红线正文的唯一落点是 `AGENT-INDEX.md` §2，本文件不复述」——它**是**指针，不是被复述的规则；规则词判据要求同现正文名，此行满足。

## 5. AC 判据

| AC | 判据 | 分母 | 读数 | 阳性对照 |
|---|---|---|---|---|
| AC-01 | 四仓指针皆含机读键且目标存在 | 4 仓 × 2 文件 = **8** | **8/8** → **PASS** | 删 workspace `AGENTS.md` 的键 → 报出 |
| AC-02 | 规则词行须同现正文名 | workspace 2 个指针的规则词行＝**2** | 2/2 同现 → **PASS** | 改前 `CLAUDE.md:9` 报出（锚 `23eeaa6`） |
| AC-03 | H2 ≤ 4 ／ 行数 ≤ 30 ／ 字节 ≤ 2000 | 2 文件 | 见 §4，均在预算内 → **PASS** | T-03 已做 7 类变异（灌水到 37 行／超 H2 → 报出） |
| AC-14 | 只碰入口文件 | — | `git status --porcelain` ＝ 2 个 `M`（`AGENTS.md`／`CLAUDE.md`），**无新增** | — |

## 6. 未覆盖 / 已知边界

- **workspace 的 `README.md` 不在本 CHG 范围**：其 `:42-51` 的 4 条独有规则之一与 `MASTER:132` 相抵，归 CHG-20260925-066 一并裁。
- 本 Task **只改两件入口文件**：未碰任何脚本、生成器、`AGENT-INDEX.md` 或运行时代码。
- **`AGENT-INDEX.md` 在 workspace 豁免八节检查**（它在运行仓是三层索引、在 workspace 是治理正文），这不是本 Task 引入的豁免，设计如此。
