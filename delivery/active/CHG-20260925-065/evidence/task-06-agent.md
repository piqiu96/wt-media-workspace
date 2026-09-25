# T-06 — wt-media-agent 四件入口文件收口

Task：把 agent 的 `CLAUDE.md`／`AGENTS.md`／`AGENT-INDEX.md`／`DIRECTORY_MAP.md` 改成 §3 形态；正文迁入 `AGENT-INDEX.md` 的 `## 本仓规则`；落实 E（禁止扫描区换指针）。**只搬家不改义**。
改前锚：**`24da21b`**（T-06 提交的父提交）。凡「改前」读数一律锚此，不用 `HEAD`（理由见 §4）。

## 1. 门禁读数（四仓合计，`scripts/verify_agent_entry.py`）

| 仓 | 改前 | 改后 |
|---|---|---|
| cloud | 51 | **0**（T-05 收口） |
| **agent** | **10** | **0** |
| desktop | 7 | 8 |
| workspace | 3 | 3 |
| **合计** | **71** | **11** |

改后逐仓分判据：desktop 8（`AGENTS.md` 无正文声明 1／复述规则 2／超预算 1／`CLAUDE.md` 无正文声明 1／复述规则 1／H2 长度 1／跨仓序列 1）＋ workspace 3（`AGENTS.md` 无正文声明 1／`CLAUDE.md` 无正文声明 1／复述规则 1）＝ 11。WARN **0**，且 `check_rule_text_duplication` 报出分母：`compared 96 rule sentence(s) across 11 file(s) in 4 repositories`（改前 62）——分母非空，故该 0 不是空转。

**agent 自身缺陷 0。** 剩余 11 条里没有一条指向 agent：desktop 的 8 条是 T-07 的活；workspace 的 3 条是 T-08 的活。`check_layer3_shape` 的跨仓相等判据现在报 **desktop** 的分叉——agent 与 cloud 已在位置 6 同为 `## 本仓规则`，先落地的两仓互为对照。

## 2. 逐条归属表（分母＝**`24da21b` 的非空行数**；各类之和等于分母）

| 源 | 分母 | 去向 | 条数 |
|---|---|---|---|
| `AGENTS.md` | 34 | → `AGENT-INDEX.md` 的 `## 本仓规则` 三个 `###`（配置 3 条／平台适配 1 条／发布构建 1 条／依赖锁文件 1 条）＋ `## 定位`／`## 本仓库拥有`／`## 禁止` | 21 |
| | | 弃：`:1` `# WT Media Agent`、`:3` `## 必须遵守`、`:5` `Follow AGENT-INDEX.md…`（指针指令）、`## Responsibility`／`## Structure`／`## Configuration`／`## Rules` 四个骨架标题 —— 旧骨架被八节形态取代 | 8 |
| | | **迁入 `DIRECTORY_MAP.md`**：`## Structure` 的 13 行模块树——每行的路径与职责**逐条**能在 `DIRECTORY_MAP.md` 指到（见 §3） | 13 |
| | | **回写**：`## Responsibility` 里的「文件与 FFmpeg 运行时」——代码里不存在（§3） | 1 |
| `CLAUDE.md` | 6 | 弃：`:1` 标题、`:3` `## 必须遵守`、`:5` `Follow …`、`:7` `## 禁止事项`（4 行骨架） | 4 |
| | | **改写**：`:9-10` 两行英文锁文件规则 → `### 依赖锁文件` 一行中文（同一规则的措辞统一，非删除） | 2 |
| `AGENT-INDEX.md` | 48 | 保留全部既有节与行（定位／拥有／不拥有／需求路由／禁止 7 条／八节骨架） | 44 |
| | | **改名＋加作用域首行**：`## 上下文加载顺序` → `## 本仓内加载顺序`（F-06／AC-12） | 1 |
| | | **改写**：加载顺序第 1 项「本文件（职责与路由）」→「本文件（职责、路由与本仓规则）」 | 1 |
| | | **删**：加载顺序第 2 项「`AGENTS.md` 与 `CLAUDE.md`（边界与规则）」——指针不再承载规则，正文已在本文件第 1 项 | 1 |
| | | **迁＋换指针**：末行「治理上下文…禁止默认扫描 `__pycache__`、锁文件」→ `## 依赖`，其后半句换成指向 `DIRECTORY_MAP.md` 的指针（E） | 1 |
| `DIRECTORY_MAP.md` | 88 | 全部保留；**＋1 行**（`local_api/health.py`，§3）＋1 句（`pyproject.toml` 可安装包） | 88 |

⇒ 四列各自加总等于分母（34／6／48／88），无一项落入「未登记」。`DIRECTORY_MAP.md` 的 `git diff --stat` 是 **2 insertions, 1 deletion**——那 1 处 deletion 是同一行加句尾的替换，**纯增量**。

## 3. 归属表的两处非机械判定

机械包含测试（`artifacts/t06-ownership.py`，归一化后判同义）报 **35 行需人工归位**，逐条归位结果：

- **13 行模块树**：全部落到 `DIRECTORY_MAP.md`。逐路径核对 `local_main.py`／`cloud_main.py`／`sidecar_main.py`／`local_api/server.py:main`／`bootstrap`／`environment.py`／`constants`／`bitbrowser/`／`platform_urls.py`／`profile_guard.py`／`health.py`／`reporting.py`／`migration.py`／`registry.py`／`protocol.py`／`noop`／`adapters`／`utils/time.py` 均命中。**两行是换词不是丢失**：`paths.py` 的「落盘位置唯一事实源」在 `DIRECTORY_MAP.md` 写作「数据/日志/版本目录解析的唯一事实源」（同义，「改落盘位置」在「何时进入」列）；`utils` 的「跨层共用的小工具」写作「供落库与比较共用」（同义）。
- **1 行是回写，不是丢失**：`## Responsibility` 说 Agent 拥有「**文件与 FFmpeg 运行时**」。实测无此能力——`git grep -in ffmpeg -- src/` 只命中 `runtime/environment.py` 的**探测**（`:105` 跑 `ffmpeg -version`，`:107` 记 `status=not_installed`），`src/wt_media_agent/` 下无文件运行时模块。新形态按代码写为 `需求路由` 的「改本地 FFmpeg 合成执行 → **尚无实现**：`runtime/environment.py` 只探测 ffmpeg 是否存在」，与云端侧「Cloud Agent：运行在云端执行环境（如云端视频生产、FFmpeg 合成）」并置。**这与 cloud 的 infra 列表同属「按代码回写文档」，是 §5 允许的例外，不是内容丢失。**

## 4. AC-09（analogue）／AC-10／AC-11／AC-14 的判据与阳性对照

| AC | 判据 | 分母 | 读数 | 阳性对照 |
|---|---|---|---|---|
| AC-09′ | `AGENT-INDEX.md` 点名的路径须存在（或明标「尚无实现／占位」） | **25** 条反引号路径 | 22 条直接 resolve；3 条是同句内已点名目录的简写（`account_check.py` ← `executors/`、`config.py` ← `runtime/`、`.ai/CURRENT_CONTEXT.md` ← `../wt-media-workspace`），按上下文补齐后 **25/25 存在**，**0 条指向不存在的路径** | 注入 `src/wt_media_agent/nosuchmod/file.py` → 报出（missing 3 → 4）⇒ 扫描有判别力 |
| AC-10 | 归属表以改前非空行数为分母 | 34／6／48／88 | 见 §2，四列加总等于分母 | `artifacts/t06-ownership.py agent 24da21b` |
| AC-11 | `AGENT-INDEX.md` 内不得再有排除清单 | 92 行（非空 62） | 命中 **0** → **PASS** | `24da21b:AGENT-INDEX.md` → 命中 **1**（`:65`）。**第三方对照**：desktop 未改动，`worktree` 命中 **1**（`:75`）⇒ 同一扫描在未处理仓上仍能命中 |
| AC-14 | 只碰四类入口文件 | — | `git status --porcelain` ＝ 4 个 `M`，无 `??` 新增 | — |
| — | 指针 8 个链接全部 resolve | 8 | 0 unresolved | 注入 `[dead](NO-SUCH-FILE.md)` → 报出 |

**AC-11 的判据本轮收窄过一次，且收窄是必需的**：初版写作「同现规则词与构建路径」，误命中 agent 的锁文件**规则**（`依赖锁文件（uv.lock、dependency.lock）由依赖工具生成，禁止手改。`——它禁的是**手改**，不是**扫描**）。收紧为「出现 **扫描** ∧ 枚举具体构建/产物路径」后，在本轮**已修好的文件**上仍有判别力：松判据（只查 `扫描`）在 agent 报 **2** 行、cloud 报 **3** 行，**全部是假阳性**——两条是指向 `DIRECTORY_MAP.md` 的指针行（含「禁止扫描区」四字），一条是 cloud 的 `go vet` 行（「格式和架构边界扫描」）。故路径词表是**承重构件**，不是装饰。读数：`artifacts/t06-ac11.out`，脚本 `artifacts/t06-ac11.py`。

## 5. 未覆盖 / 已知边界

- **desktop 的 8 条 ERROR 未消**（§1），属 T-07；workspace 的 3 条属 T-08。T-09 必须重测。
- **AC-09′ 与 AC-11 的判据是证据期临时构造的扫描，不是门禁**：仓库内无任何门禁读 infra 列表或排除清单（§14 第 11 项）。它们是可重放命令 ＋ 带阳性对照的比对，不宣称更多。
- 本 Task **只改四件入口文件**，未碰任何运行时代码／配置／测试。
- **AC-11 的对照曾在提交瞬间失效**：取证时写的是 `HEAD`，读数正确；`24da21b` 一旦被 T-06 提交取代，`HEAD` 就是修复后的文件，同命令读数也为 0——**与「扫描无判别力」形状相同**。已在脚本里钉为常量锚。**可重放命令一律指向具体提交，不指向 `HEAD`。** 同一处已在 `task-05-cloud.md` 的 cloud 臂上发生过一次（`0346edf`）。
