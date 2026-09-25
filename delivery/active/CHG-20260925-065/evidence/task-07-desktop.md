# T-07 — wt-media-desktop 四件入口文件收口

Task：把 desktop 的四件入口文件改成 §3 形态；正文迁入 `AGENT-INDEX.md` 的 `## 本仓规则`；落实 E（禁止扫描区换指针）与 **D-04 的范围限定句**。
改前锚：**`623583d`**（T-07 提交的父提交）。凡「改前」读数一律锚此，不用 `HEAD`（理由见 `task-05-cloud.md` §2 与 §14 第 14 项）。

## 1. 门禁读数

| 仓 | 改前 | 现在 |
|---|---|---|
| cloud | 51 | **0** |
| agent | 10 | **0** |
| **desktop** | **8** | **0** |
| workspace | 3 | 3 |
| **合计** | **71** | **3** |

**desktop 自身缺陷 0。** 剩余 3 条**全部**指向 workspace（T-08）。WARN **0**；`check_rule_text_duplication` 报出分母 `compared 97 rule sentence(s) across 11 file(s) in 4 repositories`。

**跨仓八节相等判据本 Task 转绿**：三仓 `AGENT-INDEX.md` 的八个 H2 现在逐字同序（`## 本仓规则` 落在位置 6）。该判据自 T-04 落地起一直是红的，且它的红**只能**由三仓齐备消——这是它设计如此，不是缺陷。

## 2. 逐条归属表（分母＝**`623583d` 的非空行数**；各类之和等于分母）

| 源 | 分母 | 去向 | 条数 |
|---|---|---|---|
| `AGENTS.md` | 28 | **弃**：`:1` `# WT Media Desktop`、`:4` `## 必须遵守`、`:6` `Follow AGENT-INDEX.md…`（指针指令）、`## Responsibility`／`## Structure`／`## Rules` 骨架标题 | 6 |
| | | **改写**：`## Responsibility` 一句总述 → `## 定位` ＋ `## 本仓库拥有` 的七项（Tauri 壳／Rust 系统桥／Local Agent 生命周期／安全存储／文件选择／更新器／跨平台打包——**逐项都在**） | 1 |
| | | **迁入 `DIRECTORY_MAP.md`**：`## Structure` 的 12 行模块树（`DIRECTORY_MAP.md` 本就有**更精确**的版本，见 §3） | 12 |
| | | **迁入 `## 本仓规则`**：`## Rules` 六条中**独有**的 4 条（Rust 代理 HTTP 不消费流／`src-tauri/gen` 禁止手改／敏感 Token 走 OS 安全存储／平台特定行为放 Rust 桥） | 4 |
| | | **已覆盖（与 `## 禁止` 同义）**：`Desktop 不复制 Cloud 业务 Web`、`Vue 不直接访问…动态端口或 Token` —— 不在 `本仓规则` 里重复写第二遍 | 2 |
| | | **已覆盖（内容原样在两个目标中）**：`Desktop 是客户端控制壳…`（`## 定位`）、`contracts.lock.json`（`DIRECTORY_MAP.md`，**改前就是重复项**） | 2 |
| | | **已覆盖**：`:30` Vue 产物来源行与 `AGENT-INDEX.md` 的 `## 本仓库不拥有` 同义 | 1 |
| `CLAUDE.md` | 7 | **弃**：`:1` 标题、`:3` `## 必须遵守`、`:4` `Follow …`、`:7` `## 其他内容`（4 行骨架） | 4 |
| | | **改写**：`:9-10` 两行英文「Vue 源码在 cloud，本仓不维护第二份」→ 已有同义中文（`## 本仓库不拥有` ＋ `### 前端产物与 Workspace 依赖`） | 2 |
| | | **改写**：`:12` 英文「`src-tauri/gen` 不得手改」→ `### 生成内容` 一行中文 | 1 |
| `AGENT-INDEX.md` | 59 | 保留全部既有节与行（定位／拥有／不拥有／需求路由 22 行／禁止 10 条） | 55 |
| | | **改名＋加作用域首行**：`## 上下文加载顺序` → `## 本仓内加载顺序`（F-06／AC-12） | 1 |
| | | **改写**：加载顺序第 1 项「本文件（职责与路由）」→「本文件（职责、路由与本仓规则）」 | 1 |
| | | **删**：加载顺序第 2 项「`AGENTS.md` 与 `CLAUDE.md`（边界与规则）」——指针不再承载规则 | 1 |
| | | **迁＋换指针**：末行「治理上下文…禁止默认扫描 …」→ `## 依赖`，其后半句换成指向 `DIRECTORY_MAP.md` 的指针（E） | 1 |
| `DIRECTORY_MAP.md` | 68 | 全部保留；**＋2 行**（禁止扫描区补「唯一落点」说明 ＋ `../generated` 的处置，见 §3） | 68 |

⇒ 四列各自加总等于分母（28／7／59／68），无一项落入「未登记」。机械包含测试报 34 行需人工归位（`artifacts/t07-ownership.out`），逐条归位结果即上表。

## 3. 两处非机械判定

- **12 行模块树是「迁入」而非「改写」**：`DIRECTORY_MAP.md` 本就逐条记着这些模块，**且更精确**——`webview.rs` 那行带 CHG 编号与「命令名一个字都没动」（`DIRECTORY_MAP.md:31`），sidecar 那行带「内存环形 200 行／退出时恰一条 `agent.supervisor` 带末 20 行」（`:49`），占位模块那行带「目前是 3 行空壳——不要把它们当成可读的实现来源」（`:42`）。逐项核对 `main.rs`／`config.rs`／`commands`／`http`／`sidecar`／`logging`／`local_agent`／`BoundNodeFacts`／`filesystem`／`resources/desktop.production.toml`／`binaries`／`capabilities`／`scripts`／`contracts.lock.json` 均命中。**`3 行` 一句另按磁盘复核：四个 `mod.rs` 各 3 行，共 12 行，与地图一致。** ⇒ AGENTS.md 的 Structure 段是**精确度更低**的第二份，迁入即消重复。
- **排除清单里 `../generated`（无点）实测不存在**，按代码回写删除：`frontendDist` 是 `../.generated/frontend`（`tauri.conf.json` 实测），`../.generated/` 与 `../generated` 当前都不在磁盘（前者是构建产物、后者**全仓仅该行提到过**，工作区根下也没有 `generated/`）。故 `DIRECTORY_MAP.md` 的禁止扫描区保留三条真实条目，并把这条处置写在该节里。**与 cloud 的 infra 列表、agent 的「文件与 FFmpeg 运行时」同属「按代码回写文档」**，是 §5 允许的例外。

## 4. D-04 的范围限定句（用户裁定：只改措辞）

`AGENTS.md:30` 那句事实本身正确，已随迁入写成 `### 前端产物与 Workspace 依赖` 的两条：

1. 业务 Vue 源码在 `../wt-media-cloud/web`；开发时 `beforeDevCommand` 指向该工程，发布时由 `../wt-media-workspace/scripts/build-desktop.sh` 产出到 `../.generated/frontend`（`frontendDist`）；本仓库不维护第二套 Vue 源码，也没有 `src/` 顶层目录。
2. **上述是开发／发布期的工具依赖；产物与运行期不依赖 Workspace**——见 `src-tauri/tauri.conf.json` 的 `beforeBuildCommand`。

**`tauri.conf.json`、`arch:478`／`:1801`、`build-desktop.sh` 的归属本 CHG 一律未动**，按用户裁定登记为待独立 CHG（`change.md` §14 第 1 项）。实测取值：`frontendDist`=`../.generated/frontend`、`beforeDevCommand`=`cd ../../wt-media-cloud/web && npm run dev:desktop`、`beforeBuildCommand`=`bash scripts/prepare-release-sidecar.sh && bash ../wt-media-workspace/scripts/build-desktop.sh`。

## 5. AC 判据与阳性对照

| AC | 判据 | 分母 | 读数 | 阳性对照 |
|---|---|---|---|---|
| AC-10 | 归属表以改前非空行数为分母 | 28／7／59／68 | 见 §2，四列加总等于分母 | `artifacts/t07-ownership.py`（`t06-ownership.py desktop 623583d`） |
| AC-11 | `AGENT-INDEX.md` 内不得再有排除清单 | 99 行（非空 72） | 命中 **0** → **PASS** | 对 **`623583d`** 命中 **1**（`:75`）⇒ 有判别力 |
| AC-12 | 小节改名 ＋ 作用域首行 | — | `## 本仓内加载顺序` ＋ 作用域句已落；加载顺序无 `CURRENT_CONTEXT`／`LEDGER.md`／`delivery/` | `check_local_order_scope` WARN 0 |
| AC-14 | 只碰四类入口文件 | — | `git status --porcelain` ＝ 4 个 `M`，无 `??` 新增 | — |
| — | 指针 8 个链接全部 resolve | 8 | 0 unresolved | 同一解析器在 agent 臂上对注入链接报出（`task-06-agent.md` §4） |

## 6. 未覆盖 / 已知边界

- **workspace 的 3 条 ERROR 未消**，属 T-08；T-09 必须重测。
- **AC-11 的判据是证据期临时构造的扫描，不是门禁**（同上，`change.md` §14 第 11 项）。
- 本 Task **只改四件入口文件**，未碰 `tauri.conf.json`、发布链路或任何运行时代码。
- **未做**：`README.md`（不在本 CHG 范围）；`.claude/skills`／`.codex/skills` 分发副本（本 CHG 不动分发，§14 第 2 项）。
