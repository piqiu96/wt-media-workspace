# T-08 evidence — FFmpeg 归属：就地改写与全仓复扫

日期：2026-09-25
Task：T-08（独立，无前置）
扫描器：`evidence/artifacts/t08-ffmpeg-ownership-sweep.py`（可复算，见 §1 口径）

## 1. 扫描口径与分母

扫描器做的**只有一件事**：把「执行方词」与「ffmpeg 词」出现在**同一子句**（`。；;` 切分）且相距 ≤80 字符的地方摊开，并标注该子句里有没有否定词。

- 范围：`git ls-files`，排除 `delivery/completed/`、`delivery/reports/`（过去时叙述）、`.claude/`、`.codex/`（`skills/` 的生成副本，改源件即可）。
- **两列都不是结论**：`candidate`（无否定词）与 `negated`（有否定词）都只是候选。判定逐条做，见 §4。
- 为什么否定列不能当干净桶：`不改变 M2 浏览器、文件、FFmpeg、发布和互动自动化的 Agent 边界` 在**否定外壳里仍断言了这个边界含 FFmpeg**——它是真冲突，却落在 `negated` 列。本 Task 的四处真冲突里，恰好有一处（`0015:6`）就藏在该列。

| 读数 | 含 ffmpeg 的行 | 文件 | candidate | negated | 合计 |
|---|---|---|---|---|---|
| 改前（`git show HEAD:`，HEAD＝`42349ee`） | 102 | 26 | 12 | 12 | 24 |
| 改后（工作区） | **100** | **24** | **9** | **11** | **20** |
| 阳性对照（注入后，见 §5） | 100 | 24 | **10** | 10 | 20 |

行数 102→100 与文件数 26→24 的差，就是两个 skill 文件**整个不再含 `ffmpeg` 字样**。

原始输出：`artifacts/t08-sweep-head.out`、`artifacts/t08-sweep-worktree.out`、`artifacts/t08-sweep-positive-control.out`。

## 2. 改前的四处冲突（扫描在 HEAD 上逐一咬住）

| # | 落点 | 列的归属 | 原句要害 |
|---|---|---|---|
| 1 | `docs/decisions/0015-*.md:6`（`Supersedes` 字段） | negated | 把 FFmpeg 列进「**不改变** M2 … 的 Agent 边界」⇒ 在否定外壳里断言该边界含 FFmpeg |
| 2 | `docs/decisions/0015-*.md:27`（`Consequences`） | candidate | 「Agent 仍是 M2 本地浏览器、文件、**FFmpeg**、发布和互动等外部执行能力的**唯一入口**」⇒ 直白的归属断言 |
| 3 | `skills/common/common-architecture-review/SKILL.md:13` | candidate | 「Agent remains the only execution entry for external platforms, files, **FFmpeg**, and browser automation.」⇒ 直白断言，且**分发到 10 处副本** |
| 4 | `skills/desktop/desktop-sidecar-update/SKILL.md:3`（`description`） | candidate | 把 FFmpeg 列为 Desktop／Agent 的打包件；该 `description` 是常驻上下文里的路由行 |

改前 §4.2 的 C2 行写的是「全仓其余落点（MASTER、架构文档、第二章、M2 里程碑）**一致判给 Cloud**」——**该结论过宽**：它只覆盖了当时点到的几类文件，没有把两个 skill 与 `0017` 自身的清单逐条判过。本 Task 按同一口径复扫后才有了上表。C2 行已就地更正（§7）。

对照面的证据（判给 Cloud 的锚点，本 Task 未改）：`0017:28`「Desktop、Local Agent 和 Cloud Agent 均不执行视频合成」、`0017:40`「FFmpeg 属于 Cloud 部署组件」、`0017:10` 的 `Does not supersede` 清单（**只列 BitBrowser、Profile、Cookie、浏览器自动化、发布、互动、本地文件落地，不含 FFmpeg**）、`MASTER:454`／`:757`、`AGENT-INDEX.md:112`、架构文档 §5.11。

## 3. 四处改动（就地改写，不留取代注记）

用户 2026-09-25 裁定：ADR-0015 的那句**就地改写、整句重写**（不删一个词——原句是面向后续阶段的边界声明，删词会被读成篡改 ADR）。

| # | 落点 | 改后 |
|---|---|---|
| 1 | `0015:6` | `…不改变 M2 浏览器、文件、发布和互动自动化的 Agent 边界；M4-M5 视频合成的 FFmpeg 执行由 Cloud Compose Worker 承担（ADR-0017），不在该边界内。` |
| 2 | `0015:27` | `- Agent 仍是 M2 本地浏览器、文件、发布和互动等外部执行能力的唯一入口；本 ADR 不是全局撤销 Agent 架构。M4-M5 视频合成的 FFmpeg 执行不在该边界内：它由 Cloud Compose Worker 调用 Cloud 运行环境中的 FFmpeg 完成（ADR-0017）。` |
| 3 | `skills/common/common-architecture-review/SKILL.md:13` | `- Agent remains the only execution entry for external platforms, local files, and browser automation; M4-M5 video composition is Cloud-owned (docs/decisions/0017-*.md).` |
| 4 | `skills/desktop/desktop-sidecar-update/SKILL.md:3` | `description: Update Desktop sidecars, local Agent packaging, or platform-specific binaries.` |

改写后这两行**从候选集里整体消失**（不是从「冲突」挪到「已排除」）：补上 Cloud 归属的那句里不再有执行方词，于是同一子句里既没有 Agent 也没有 FFmpeg 的错配。`0017` 的 `Supersedes` 清单按用户政策**不动**（不留取代注记；变更理由在本记录）。

**为什么连 skill 一起改**：只改 ADR 的话，AC-08 的「全仓该归属只有 Cloud 一个结论」当场不成立——两个 skill 仍在断言 Agent 拥有 FFmpeg。它们不在计划点名的 `0015-*.md` 里，是**复扫发现的**。

## 4. 改后 20 条候选的逐条判定

`candidate`（9 条）——无一条断言 Agent 拥有 FFmpeg：

| 落点 | 判定 |
|---|---|
| `MASTER:473` | 验收清单（FFmpeg＝Cloud Worker 的，`Local Agent 下载` 是同列的另一件事）；归属由 `:454`／`:757` 明写 |
| `delivery/active/CHG-20260925-064/change.md:50` | **本 CHG 自述**（逐字引用被判定的原句） |
| `milestones/M4-content-production.md:11` | 判给 Cloud（「Cloud … 执行真实 FFmpeg、上传对象存储」） |
| `milestones/M5-automatic-production.md:175` | 验收链路清单；归属由 `:80`（Scheduler 不持有 FFmpeg）明写 |
| `0016:13` | **历史引述**：引述被本 ADR 取代的架构基线 §5.4 旧定义（`Context` 节，说明「为什么改名」）。活文档 §5.4 已不含 FFmpeg（`:1127` 的 Agent 运行时能力＝配置／日志／生命周期／健康检查／上下文／版本／常量／环境上报） |
| `0017:7` | `Supersedes` 清单里引述**被取代**的旧约束本身 |
| `0017:14` | `Context` 描述旧的两条执行路径（历史描述） |
| `docs/superpowers/plans/2026-07-23-…:132` | 该草案的「不包含」清单（历史过程件） |
| `docs/superpowers/plans/2026-09-24-…:81` | 一条 `rg` 的**搜索模式**（取证命令本身） |

`negated`（11 条）——全部是排除句或与归属无关的清单：

`MASTER:454`（Desktop／Local Agent 不执行）、`MASTER:471`（失败清单里的「FFmpeg 失败」，其 `无` 属「无假成功」）、`MASTER:757`（Cloud Worker 不依赖 PATH）、`M2-account-runtime.md:120`（M2-A 不检测 FFmpeg）、`planned/CHG-061:69`／`:135`（Agent 合同／边界不得出现 FFmpeg）、`0015:10`（M3 不涉及 FFmpeg）、`0017:24`（Cloud 语境下的 FFmpeg 运行隔离）、`0017:55`（Local Agent 的 FFmpeg 打包工作不再复用）、`specs/2026-09-24-m4-m5-…:242`（Agent 合同不得出现 FFmpeg）、`superpowers/plans/2026-09-24-…:28`（Agent 移除 FFmpeg 后…）。

⇒ **判定结果：20 条候选里 0 条把 FFmpeg 判给 Agent／Desktop。** 这是逐条判定的结论，不是某一列为空。

## 5. 阳性对照（证明扫描能咬住）

临时把 `MASTER:454`（`- 视频合成只在 Cloud Compose Worker 执行；Desktop / Local Agent 不执行 FFmpeg；`）改成 `- 视频合成由 Local Agent 执行 FFmpeg；`：

- `candidate` **9 → 10**，新条目正是 `delivery/MASTER_IMPLEMENTATION_PLAN.md:454 | 距离 9 | - 视频合成由 Local Agent 执行 FFmpeg`（`negated` 11 → 10：该行换列）。
- 还原：`git restore` 后 `sha256sum` 与改前同为 `29e6499…e58c0`，`git status --porcelain` 对该文件为空 ⇒ **逐字节还原**。
- 读数：`artifacts/t08-sweep-positive-control.out`。

另一个方向的反证：改前的 HEAD 读数里，四处真冲突分别落在**两列**（3 条 candidate、1 条 negated）——说明两列都得逐条判，任一列为空都不构成通过。

## 6. 分发：源件一改，副本必随

`skills/` 是唯一源（`AGENT-INDEX.md:41`），两个源件改动经 `scripts/sync_skills.py sync` 分发：

| 目标 | 收到 | 说明 |
|---|---|---|
| 执行根 `..` | common／workspace／cloud／agent／desktop | `kind: distribution`，非 git 仓，副本无法提交 |
| `wt-media-cloud` | common | `commit_generated: true` ⇒ 随该仓提交 |
| `wt-media-agent` | common | 同上 |
| `wt-media-desktop` | common／desktop | 同上 |
| `wt-media-workspace` | common／workspace | 本仓 `commit_generated: true` |

- `sync_skills.py check` → `skill outputs are up to date`，`exit=0`（`sync` 之后复测）。
- 三仓的 `git status --porcelain` 在 `sync` 前为空（cloud 另有开工基线里的 `?? dump.rdb`），`sync` 后**只有**各自的 `.claude/skills`、`.codex/skills` 生成副本被改——明细见 §8 的收尾读数。
- 依据：`conventions` §7「这 5 处副本都随各自仓库提交」＋ `AGENT-INDEX.md` §9「一仓一 commit：跨仓改动在各仓分别提交」。**本 CHG 仍不改任何运行时代码**，写进三仓的只有生成副本。先例：`wt-media-agent` 的 `2b26808 docs(chg-059): T-09 …`。
- 因此 AC-15「对三个运行仓零写」按事实改写为「只写分发副本」（§7 ④）。
- 三仓各自一条提交（内容只有上表的生成副本）：

| 仓 | 提交 | 提交后 `git status --porcelain` |
|---|---|---|
| `wt-media-cloud` | `0346edf` | `?? dump.rdb`（＝开工基线） |
| `wt-media-agent` | `24da21b` | （空，＝开工基线） |
| `wt-media-desktop` | `623583d` | （空，＝开工基线） |

提交顺序是先三仓、后 workspace：本记录要能引用**实测到的**哈希，而不是「稍后补」。各仓的提交信息已写明源件改动所在（workspace 的 CHG-064 T-08）。

**执行中发现的新遗留**：`wt-media-desktop/.gitignore:10-11` 忽略 `.claude`／`.codex`，而已有的 10 份副本是 **tracked**（tracked 文件不受 ignore 影响，故本次能提交）。但 `config/skills-distribution.yaml` 对 desktop 声明 `commit_generated: true`、`conventions` §7 也写着「这 5 处副本都随各自仓库提交」——**新增**一份分发到 desktop 的 skill 会被 ignore 静默吞掉。这是「声明的治理事实」与「仓库配置」相冲，属独立裁定（改 `.gitignore` 要动运行仓），已登记为 §14 第 16 项。

## 7. 本 Task 造成的记录更正（就地覆盖）

| # | 位置 | 改前 | 改后 |
|---|---|---|---|
| ① | §4.2 C2 | 「全仓其余落点…**一致判给 Cloud**」 | 补上「T-08 复扫发现**另有 2 处**（两个 skill）与 `0015` 同判 Agent」——原句过宽，见 §2 |
| ② | §4.4 | 「本 CHG 对三仓**零写**，收尾按同一命令复测」 | 改为「不改运行时**代码**；三仓只收 `skills/` 的生成副本（§8.6）」，收尾按同一命令复测并逐条对账 |
| ③ | §9 三仓清单 | 三行都是 `Not affected` | 改为「只收 skill 生成副本（T-08）」，不动代码 |
| ④ | §10 AC-15 | 「对三个运行仓零写」 | 「不改三个运行仓的任何运行时代码；只写 `skills/` 的分发副本，且副本内容与 `skills-distribution.yaml` 一致（`sync_skills.py check` 绿）」 |
| ⑤ | §14 第 4 项 | 架构文档「其余陈旧点未扫」 | 补记「FFmpeg 切片已扫（该文 24 行 FFmpeg 落点：全部判给 Cloud 或为排除句）」——把已覆盖的部分从遗留里划掉 |

## 8. 判据

| 判据 | 读数 |
|---|---|
| 活文件中把 FFmpeg 判给 Agent／Desktop 的落点 | 改前 4（`0015:6`、`0015:27`、两个 skill）→ 改后 **0**（20 条候选逐条判定，见 §4） |
| 扫描器可失败 | 注入 Agent-owned 句子 → candidate 9→10 且新条目就是被注入的那行；还原经 `sha256` 与 `git status` 双向证明 |
| 六门禁 + `unittest` | 见 `artifacts/t08-gate-readings.out`（三遍：初遍 20:06:16 ／ 关闭遍 20:07:05 ／ 复核遍 20:07:17，除 `unittest` 耗时外逐行相同） |
| `sync_skills.py check` | `skill outputs are up to date`，`exit=0` |
| 三仓改动面 | 只有 `.claude/skills`、`.codex/skills` 下被分发到的生成副本；无代码、无配置、无 `dump.rdb` |

## 9. 未覆盖与明确不改

- **`0017` 的 `Supersedes` 清单不动**（用户政策：不留取代注记）。
- **`0016:13` 引述的旧 §5.4 定义不改**：ADR 的 `Context` 记录的是**决策前的状态**，且该句正是「为什么 §5.4 要改名」的理由。但它暴露一类失效：**ADR 里逐字引用的旧基线文本，在基线被就地覆盖后失去所指**——登记为 §14 第 15 项（无机制可检）。
- **`scripts/verify_m3_acceptance.py:1640` 的 `ffmpeg=normal` 与 `M2-account-runtime.md:120` 的「不检测 FFmpeg」不是冲突**：前者是 2026-09-16 M2-B 验收时 Agent 环境探针上报的字段值（取证字符串，记的是当次运行），后者说的是 M2-A 的账号检查项。两者轴不同；且本 CHG 不改运行时代码。
- **`docs/superpowers/` 与 M4／M5 里程碑里的 FFmpeg 行**：只读判定，未改（前者是历史过程件，后者本就判给 Cloud）。
- **本 CHG 自己的 evidence 产物**（`t08-*.out`、本文件）含被判定原句的逐字引用，一旦入库会自报为候选；T-12 归档后它们落在 `delivery/completed/` 排除项内，收尾读数按归档后的口径重跑。
