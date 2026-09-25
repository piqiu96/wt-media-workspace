# T-05 cloud 四件入口文件收口

原始输出：`artifacts/t05-gate-before.out`（改前）、`artifacts/t05-gate-after.out`（改后）、`artifacts/t05-cloud-checks.out`（AC-09／AC-10／AC-11）、`artifacts/t05-ownership.out`（逐条比对）。

## 1. 门禁读数（改前 → 改后）

| 面 | 改前 | 改后 |
|---|---|---|
| `cloud` 报出条数 | **51** | **1** |
| 四仓合计 | 71 | **22**（agent 10、desktop 8、workspace 3、cloud 1） |
| 其余五门禁 | `exit=0` | `exit=0` |
| `unittest discover -s tests -q` | `Ran 94` / OK | `Ran 94` / OK |

**cloud 那 1 条必须按归属读，不能读成「还差一条」**：它是 `check_layer3_shape` 的**跨仓相等**判据（`cloud: AGENT-INDEX.md H2 sequence diverges from agent at position 6: '本仓规则' != '禁止'`）。cloud 一侧的文件本身**零缺陷**——agent 与 desktop 还没有 `## 本仓规则` 节，位置 6 自然不同。**该条在 T-06／T-07 落地前不可满足**，故 T-05 的收口按「**cloud 自身缺陷 0**」认定，跨仓那条留到 T-07 之后重测。改后逐仓分判据：`restates a rule without naming` 10 ／ `declares no rule body` 6 ／ `exceeds the pointer budget` 2 ／ `H2 sections, expected 8` 2 ／ `H2 sequence diverges` 2。

WARN 为 **0**，且 `check_rule_text_duplication` **报出分母**：`compared 95 rule sentence(s) across 11 file(s) in 4 repositories`（改前 62）——分母非空，故这个 0 不是空转。

## 2. 逐条归属表（分母＝**改前 `HEAD` 版本的非空行数**；各类之和等于分母）

| 源 | 分母 | 去向 | 条数 |
|---|---|---|---|
| `AGENTS.md` | 86 | → `AGENT-INDEX.md` 的 `## 本仓规则` 各 `###`（项目定位／进程与目录／受控全局基础资源／配置规则／Database 与 Repository／Client 与执行边界／日志规则／Scheduler、Job 与 Worker／Module 规则／Shared 与 API／测试与提交） | 79 |
| | | 弃：`:1` 标题、`:3` `## 必须遵守`、`:4` `Follow AGENT-INDEX.md…`（指针指令——该文件的角色已由「本文件即正文」承担） | 3 |
| | | **改写**：`:10`「完整设计基线：`docs/superpowers/…`」→ 按工作区 §3 写成「分析材料，不作为新开发依据」（冲突 A／F-05） | 1 |
| | | **回写**：`:18` infra 列表含 `cache`／`storage`，磁盘无此二目录 → 改为实测值，并把 `media`／`storage` 登记为「尚未创建」 | 1 |
| | | **迁入 `DIRECTORY_MAP.md`**：`:112` `# 禁止扫描`（第二个 H1）与 `:113` 的 `.gitignore` 扫描范围 | 2 |
| `CLAUDE.md` | 99 | 弃：与 `AGENTS.md` 同义／被其覆盖／纯结构（含 15 个 H1-H2 与 `:11`／`:13`／`:21`／`:25`／`:29`／`:31`／`:57`／`:63`／`:69`／`:72`／`:89`／`:99`／`:101`／`:115`／`:117`／`:121`／`:127`／`:141` 等；`:23`／`:27` 重复的 `## internal/bootstrap` 一并去重） | 79 |
| | | **保全新内容**：`:80`／`:82`／`:84-87` 外部服务接入 → `### 外部服务接入`（第 3 步「接入 Runtime」按 A 的裁定改写为「由 Bootstrap 统一初始化，业务侧经各包公有只读 Getter 使用」） | 6 |
| | | **保全新内容**：`:150`／`:152`／`:154-157` 修改原则 → `### 修改原则` | 6 |
| | | **保全新内容**：`:161`／`:163`／`:165-168` 提交要求 → `### 提交要求` | 6 |
| | | **回写**：`:38` 的 `redis` 按实测消失（正确列表已在 `### 进程与目录`） | 1 |
| | | **不迁移（冲突 A 的对立句）**：`:76`「必须通过 Runtime 获取」 | 1 |
| `AGENT-INDEX.md` | 45 | 保留全部既有节与行（含 `## 禁止` 9 条、需求路由 11 行、拥有／不拥有） | 43 |
| | | **删**：旧第 2 项「`AGENTS.md` 与 `CLAUDE.md`（架构与编码规则）」——两个指针不再承载规则，规则正文已在本文件第 1 项 | 1 |
| | | **迁**：`## 上下文加载顺序` 改名 `## 本仓内加载顺序` ＋ 作用域首行；末行「治理上下文…」迁 `## 依赖`，其「禁止默认扫描 …」半句换成指向 `DIRECTORY_MAP.md` 的指针 | 1 |
| `DIRECTORY_MAP.md` | 75 | 全部保留（含禁止扫描区、模块表、Vue 分区 8 节） | 75 |
| | | **新增** 1 行，接收 `AGENTS.md:113` | −1 |

⇒ 四列各自加总等于分母（86／99／45／75），无一项落入「未登记」。**CLAUDE.md 里三块独有内容（外部服务接入／修改原则／提交要求）全部保全**——它们与 `AGENTS.md` **无任何同义行**，只有逐条比对（`artifacts/t05-ownership.out`：99 行中 43 行无逐字同义行，逐行归位）才会现形，这正是「只搬家不改义」要防的丢失点。

## 3. 形态读数（改前 `HEAD` → 改后；此处是 `wc -l` 的总行数，与 §2 的非空行数不是同一个分母）

| 文件 | 总行数 | 角色 |
|---|---|---|
| `AGENT-INDEX.md` | 60 → **205** | 正文（吸收 79 行规则 ＋ 新增 `## 本仓规则`） |
| `AGENTS.md` | 113 → **11** | 指针 |
| `CLAUDE.md` | 168 → **11** | 指针 |
| `DIRECTORY_MAP.md` | 105 → **106** | 目录地图（＋1 行） |
| 合计 | 446 → **333** | |

两个指针各 3 个链接，**全部 resolve**：`../wt-media-workspace/AGENT-INDEX.md`、`AGENT-INDEX.md`、`DIRECTORY_MAP.md`。

## 4. AC-09／AC-10／AC-11 的判据与阳性对照

| AC | 判据 | 分母 | 读数 | 阳性对照 |
|---|---|---|---|---|
| AC-09 | infra 规则行枚举的目录须在磁盘存在 | 1 行规则／5 个目录名 | `client database logger metrics tracing`，missing **none** → **PASS** | 注入 `cache` → 报 `missing -> ['cache']` ⇒ **检查能失败** |
| AC-11 | `AGENT-INDEX.md` 内不得再有排除清单 | 205 行 | 命中 **0** → **PASS** | 同一扫描跑 `HEAD:AGENT-INDEX.md`（**未改动的基线**）→ 命中 **1** ⇒ 扫描有判别力 |
| AC-10 | 归属表以改前非空行数为分母 | 45／86／99／75 | 见 §2，各类加总等于分母 | 逐条比对脚本对 `HEAD` 版本运行；CLAUDE.md 43 行无逐字同义行，逐行人工归位 |
| AC-14 | 只碰四类入口文件 | — | `git -C ../wt-media-cloud status --porcelain` 仅 4 个 `M` ＋ 既存 `?? dump.rdb` | — |

## 5. 未覆盖 / 已知边界

- **cloud 自身的 1 条跨仓 ERROR 未消**（§1），只能由 T-06／T-07 消；T-09 必须重测。
- **AC-09 的判据是证据期临时构造的扫描**：仓库内无任何门禁读 infra 列表（`grep -rn 'internal/infra' scripts/ tests/ config/` 零命中）。它是可重放命令 ＋ 带阳性对照的一次比对，**不是门禁**，不宣称更多。
- 本 Task **只改四件入口文件**，未碰任何运行时代码／配置／测试。
- **未做**：`docs/arch/wt-media-cloud-arch.md:5` 的同类主张（§14 第 3 项）；`README.md` 未动（它在 `check_rule_text_duplication` 的比较集内，本次报 0 WARN）。
- 归属表是**按非空行**统计的，`## 禁止` 等节的空行与分隔线未逐条列；它们不含内容，不构成丢失面。
