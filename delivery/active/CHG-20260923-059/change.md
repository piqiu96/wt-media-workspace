# CHG-20260923-059：联合工程优化 D——Sidecar、打包、升级与回归

## 1. Basic Information

- Level: M
- Status: IMPLEMENTING（2026-09-25 由 `delivery/planned/` 激活并改写为十三节执行记录）
- Created: 2026-09-23
- 前置：CHG-20260923-058（C）——**已于 2026-09-25 归档 `DONE`**，前置满足
- Current repository: wt-media-workspace（治理与发布矩阵）；运行时改动分布于 wt-media-desktop、wt-media-agent
- Affected repositories:
  - `wt-media-desktop`
  - `wt-media-agent`
  - `wt-media-workspace`
- 不受影响并已声明：`wt-media-cloud` 的 Go 后端与 `web/`——本 CHG 不改这两个面。
  （发布校验要**读** Cloud 契约版本，但读不改；见 T-06。C 的 `web/` 授权**不结转**到本 CHG。）

## 2. Change Goal

完成上线前工程优化第四阶段（D），也是最后一段：把 Desktop 与随包 sidecar 之间**今天靠约定、不靠确认**
的那几件补齐——就绪、身份、退出、完整性、配置随包、版本可追溯——再对全程序之后的树跑一遍 M2 业务回归。

用户可见的独立可验证结果：

1. **就绪是确认过的，不是猜的**：Desktop 起 sidecar 后，等到 Agent **自己说可以了**（它 bind+listen
   之后打印的那一行）**并且**健康检查真的应答，才算启动成功；超时是**真的会超时**，不是一个没人读的配置键。
2. **不会连上旧进程**：sidecar 已经死掉时，界面不再说「已在运行」；如实说「未在运行」并允许重新启动。
3. **退出是收尾过的**：Desktop 退出时**先请** sidecar 停（宽限窗口内自己收尾在飞任务），**再**强制结束；
   今天是一路 `kill()`，退出报告里能看到「被信号终止」。
4. **随包 sidecar 是被验过的**：启动前核对它和构建时记录的那个 sha256 一致；不一致**拒绝启动并说清原因**，
   不静默放行。
5. **产物里带着 Agent 的配置**：`config_online/` 整目录替换进产物，`diff -r` 无差异；
   装机后跑的是产物的配置，不是内置默认值。
6. **五类版本可追溯**：Desktop、Agent、前端构建、Contract、组件与资源各有一个可得来源；
   发布脚本对 Desktop ↔ sidecar 做**版本兼容校验**（今天读了两个版本却从不比较）。
7. **升级不覆盖用户数据**：`settings.toml`、SQLite、检查点、待回传结果不在升级的写入范围。
8. **M2 业务回归**对 A/B/C/D 之后的树通过。

**明确不做**：不重写现有稳定脚本；不为目录整齐整体重构；不改日志轮转与保留（C 已定型，见 D-10）。

## 3. Baseline References

- Milestone: `delivery/milestones/M-launch-engineering.md#成功事实全部成立`
  （本 CHG 的验收锚点是**成功事实 #7**「正式安装包脱离开发源码/venv/开发机路径可运行；发布可追溯五类版本」、
  **#8**「升级不覆盖用户配置、SQLite、检查点与待回传结果」、**#4**「既有 M2 链路 dev 模式回归通过」；
  失败行为锚点：「升级或清理删除业务数据」与「因普通用户设置环境变量将正式包重定向到未知服务」）
- Engineering baseline: `docs/engineering/specs/2026-09-23-launch-engineering-optimization-program.md`
  §3 CHG-D（`:70`）、§4 横切要求（`:74-81`）
- Engineering baseline（架构）: `docs/engineering/architecture/社媒运营平台工程架构与分层设计_V1.md`
  §5.2（进程模型）、§6.8（安装目录和用户数据）、§7.11（日志和诊断）
- 发布矩阵: `config/release-matrix.yaml` 的 `0.2.5-m2-c-e-private-distribution`
  （`status: verifying`、`target_status.macos_arm64: verified_pending_user_install_acceptance`、
  `manual_acceptance` 三条、两条 `residual_risks`）
- 上游 CHG: [CHG-20260923-058](../completed/CHG-20260923-058/change.md)（C，已将 `active/` 清空并归档）、
  [CHG-20260923-057](../completed/CHG-20260923-057/change.md)（B，**已登记的 `already_running` 实缺陷**，
  本 CHG 的 T-02 关闭它）、[CHG-20260923-056](../completed/CHG-20260923-056/change.md)（A，
  **D-07 的硬约束**：凭证只走环境变量）
- 吸收来源: CHG-20260923-053 Task 7（`config_online → 产物/config`、Agent 侧入口文档同步、
  workspace skill 改指 `clients/<platform>`）

## 4. Current Facts

本节每条都是**激活时实测**的（file:line 与命中数），不是从草案推想的。**与草案不一致的两条已改正**
（4.4 的依赖前提、4.6 的「无任何表示」范围），依据是 C 之后树已变。

### 4.1 就绪：Agent 会宣告，但**没有任何人听**；超时键是死配置

- Agent 在 `local_api/server.py:627` 打印
  `wt-media-agent local API listening on {host}:{port}`（`flush=True`），同一句也进 logger（`:626`）。
- **这一行是可靠的**：`ThreadingHTTPServer((host, port), …)` 在 `:625` 构造（构造即 `bind`+`listen`），
  `:627` 才打印，`:629` 才 `serve_forever()`。所以看到这行时套接字**已经在听**，内核 backlog 会接住
  紧接着到来的请求，只是要等 `serve_forever` 转起来才应答——**这正是一个「两段式闸门」该有的第一信号**。
  （T-01 实施时更正：激活当天此条写的是 `:624`，实为 `:625`；T-01 的 Agent 侧用例把这行钉死了。）
- **`/healthz` 在鉴权之后**（T-01 实施时实测）：`do_GET` 先调 `_check_auth()`（`:448`）再分发，
  `:451` 才轮到 `/healthz`。所以**令牌不对时它答 401**——这正是 `sidecar/mod.rs:30-37` 那段注释
  担心的漂移（「一个被告知 A 令牌、却被用 B 令牌质问的 sidecar 会对所有请求答 401」），
  而它在第二段闸门上**当场可见**。这是把 401 定为「致命、不等待」的实测依据，不是推想。
- **消费者为零**：`git grep -n listening -- src-tauri/src src-tauri/*.json` 在 desktop 侧的 4 处命中
  全是测试里的套接字注释（`commands/agent.rs:368`、`:545`、`http/mod.rs:266`、`:321`），**没有一处读 Agent 的输出**。
- `[sidecar] start_timeout_ms = 15000`（`src-tauri/resources/desktop.production.toml:46`）被读进
  `config.rs:105`、被校验 `> 0`（`config.rs:237`）、在 dto 测试里往返（`dto/config.rs:85`、`:151`），
  但 **`git grep -n timeout -- src-tauri/src/sidecar/` 命中 0**——`sidecar/` 里没有任何地方用它。
  **它是死配置**：写得出来、验得过、没人用。

### 4.2 实例身份：`already_running` 看的是**手里的句柄**，不是**对方还在不在**

（本节在 T-01 收尾时回改过一处措辞：激活时我把它写成「读的是托管状态里记着的会话 id」，
与代码不符。判定读的一直是 `AgentProcess` 槽里的 `CommandChild` 句柄；**缺陷结论不变**，
但机制说错了就会把后来人引到错的修法上，故按 `f1d1fba^:src-tauri/src/commands/agent.rs:163-168`
的原文改回如下。）

- 判定在 `commands/agent.rs:275`（T-01 之前是 `:163-168`）：读 `AgentProcess.0` 锁住后
  `.is_some()`——**槽里有没有一个 `CommandChild` 句柄**。有就 `return Ok("already_running")`。
- 关键在**这个句柄不会因为进程退出而消失**：`CommandChild` 是 spawn 的返回值，
  子进程自己死掉时没有任何人把它从 `state.rs` 的 `AgentProcess(Mutex<Option<CommandChild>>)` 里取走。
  ⇒ 判定问的是「**我还记着一个句柄吗**」，而不是「**那个 Agent 还活着吗**」。
- `already_running()`（`commands/agent.rs:63`）本身只是**一条日志函数**，不参与判定。
- ⇒ CHG-057 登记的实缺陷**今天仍然成立**（`CHG-20260923-057/checkpoint.md:55`、`:358-359` 原文）：
  「**`already_running` 在 sidecar 自己死掉之后仍会说「已在运行」**（托管状态里的 `CommandChild`
  不会因进程退出被清掉）——**既有行为**」。

### 4.3 退出：Desktop 不停 Agent；`stop` 是硬杀；Agent 不处理信号

- Desktop 侧 **无退出钩子**：`git grep -n "RunEvent\|on_window_event\|ExitRequested"` 在 `src-tauri/src`
  命中 **0**。应用退出时 sidecar 不被要求停止。
- `sidecar::stop`（`src-tauri/src/sidecar/mod.rs:121-127`）= `child.kill()`——**硬杀**，没有请求、没有宽限。
- Agent 侧**只有** `KeyboardInterrupt`（`server.py:630`）：`git grep -n "signal\.\|atexit\|SIGTERM\|shutdown" -- src`
  在 agent 只命中这一处。⇒ SIGTERM 到不了任何清理路径，`finally: httpd.server_close()`（`:632-633`）不执行。
- 退出报告的形状已经存在（`sidecar/drain.rs:193-196`，`(None, Some(signal)) => "被信号 {signal} 终止"`）
  ——**它今天正是在报硬杀**。

### 4.4 完整性：**记录齐全，运行期一个字节都不验**（依赖前提与草案不同）

- `git grep -n "manifest\|sha256\|digest\|hash" -- src-tauri/src/sidecar/` 命中 **0**——`sidecar/` 既不读
  manifest 也不验哈希。全仓其余命中都在 `app_paths`/`diagnostic`/`logging` 里，**没有一个属于 sidecar 启动路径**。
- 打包侧**已经产出**完整链条（`package-release-macos.sh`，119 行）：构建期 sha256 由
  `wt-media-agent/scripts/build_desktop_sidecar.py:93,130` 写入 `target/sidecar-manifest.json`；
  打包期重算并写成同名文件的 `sha256`（`:97-98`），**与构建期的 `build_sha256` 并排放在同一个 JSON 里**。
- **但两者从不比较**：脚本读了 `SIDECAR_BUILD_SHA`（`:81`）与重算的 `PACKAGED_SIDECAR_SHA`（`:97`），
  把它们各写成两个字段（`:98`），**没有任何一行断言二者相等**。⇒ 一个与构建产物不一致的 sidecar
  会被**如实记录成不一致**，然后照样发布。
  脚本确实检查了**存在性**（app / dmg / manifest 三个必需产物 `:75-77`、包内 sidecar `:87`）与
  `codesign --verify --deep --strict`（`:94`）——它缺的是**相等性判定**这一条。
- **与草案不同的一条**：草案说「Cargo 里没有哈希依赖」。**实测已有**——`src-tauri/Cargo.toml:85`
  `sha2 = "0.10"`（C 为诊断包摘要引入的**直接**依赖）。⇒ T-04 **不需要新增依赖**。

### 4.5 `config_online → 产物/config`：**产物里根本没有 Agent 的配置**

- `src-tauri/tauri.conf.json:26`：`"resources": ["resources/*.toml"]`——只带 Desktop 自己的 toml。
- `build_desktop_sidecar.py` 里 **`config_online` 零命中**（`grep -n` 只命中 shutil/sha256/manifest 相关行）：
  它构建、拷贝、写 manifest，**不做配置替换**。
- ⇒ 冻结的 sidecar 跑的是**内置默认值**，不是 `config_online/agent.toml`。而后者已经是 `environment = "production"`
  （`wt-media-agent/config_online/agent.toml:16`）——**一份声明为生产、却进不了产物的配置**。
- 吸收来源给出的验收判据是 `diff -r` 无差异。

### 4.6 版本：打包脚本读了两个版本却**从不比较**；五类里只有两类有表示

- `package-release-macos.sh:53` 从 `tauri.conf.json` 取 `VERSION`（现为 `0.1.0`）；
  `:82` 从 sidecar manifest 取 `SIDECAR_VERSION`（现为 Agent 的 `pyproject.toml:3` = `0.2.2`）。
  **两个都读了，没有一处比较它们**——版本不兼容的包今天可以正常打出来。
- 诊断包报 `app_version` 与 `build_version`（`commands/diagnostic.rs:185,205`，后者是
  `CARGO_PKG_VERSION`）——**两者都是 Desktop 侧**。
- ⇒ 五类里 **Desktop / Agent 各有来源**；**前端构建版本**与**组件与资源版本**在本仓、agent 仓、workspace
  的 `release-matrix.yaml` / `contract-map.yaml` 里**没有任何表示**（`git grep` 无 `frontend`/`build_version`/
  `resource_version` 类字段，`release-matrix` 只有 `components:` 下的 cloud/agent/desktop/local_agent）。
  **这是「新建」而不是「校验已有」**。

### 4.7 升级不覆盖：今天**没有升级动作**，所以这条要证的是「不发生」

- 本 CHG 不改升级器（`filesystem/`、`updater/` 在 desktop 侧仍是空壳）。要证的因此是一条**否定命题**：
  升级路径不写 `settings.toml`、SQLite、检查点、待回传结果。
- 判据必须是**路径**，不是名字清单——沿用 C 的做法（「保护是一条路径，不是一个名字清单」，
  `CHG-20260923-058` 的 T-06）。

### 4.8 起点测试基线（本 CHG 的「只增不减」分母）

| 仓 | 命令 | 起点 |
|---|---|---|
| `wt-media-desktop` | `cargo test --workspace` | **336 passed / 0 failed / 2 ignored** |
| `wt-media-agent` | `bash scripts/test.sh` | **377 tests OK** |
| `wt-media-workspace` | `python3 -m unittest discover -s tests -q` | **69 tests / 4 failures（4 条为既知红项）** |

四条既知红项的判定沿用 C 的**同集合阳性对照**（必须在真实 `wt-media/` 之内的树上做，
否则路径敏感的用例会静默 `skipTest`，把 4 红读成 2 红）。见 `CHG-20260923-058/evidence/task-09-writeback-and-archive.md` §3.1。
**T-01 时实测确认了这两种读数**：把 `git archive HEAD` 解到 `/tmp` 再跑 ⇒ 2 红；
在真实树内把两个记录文件 stash 回 HEAD 再跑 ⇒ 4 红、逐条同名。

### 4.9 本机环境事实（影响验证方式）

- 本机是 **arm64 macOS 开发机**，装着 Python/Node/Rust 与 `.local/` 开发树 ⇒ **它不能充当「干净机」**（见 §6 D-09）。
- BitBrowser 在本机 `:54345` 上**正在运行**（用户自己的工具）。Cloud `:18080` 与 dev Agent `:8765`
  **当前空闲**。本 CHG **不得占用** `:54345`；需要起 Cloud/Agent 时用**临时端口**，不改这两个默认值。
- 会话可被锁定（C 期间实测锁定过），**屏幕锁定不影响无头测试与真实进程取证**，只影响「有人点过」这一类验收。

## 5. Scope

### Add

- Desktop：sidecar **就绪闸门**（消费 Agent 的 readiness 行 + 真实健康应答 + 真的超时）；
- Desktop：**活性探针**取代「记录里有会话」的判定；
- Desktop：退出钩子（`RunEvent::Exit`）→ 请停 → 宽限 → 强杀；
- Agent：SIGTERM 处理与在飞任务收尾；
- Desktop：启动前**运行期完整性校验**（读 `sidecar-manifest.json`、验 sha256、失败拒绝启动）；
- Desktop + Agent：`config_online/ → 产物/config` 的打包步骤与 `diff -r` 校验；`tauri.conf.json`
  的 `bundle.resources` 补上 Agent 配置；
- Desktop + workspace：**五类版本**的来源与发布脚本的 **Desktop ↔ sidecar 版本兼容校验**；
- workspace：M2 回归的**重跑记录**（工具已有）。

### Modify

- `src-tauri/resources/desktop.production.toml`：`start_timeout_ms` 从死配置变成真消费者
  （超时语义由 T-01 定义；键名不变）；
- `src-tauri/src/sidecar/`（就绪、退出、完整性）、`commands/agent.rs`（活性判定）；
- `wt-media-agent/src/wt_media_agent/local_api/server.py`（信号处理）；
- `wt-media-agent/tests/test_sidecar_entry.py`：**T-01 已用**——就绪行的格式与顺序钉死。
  Desktop 从 T-01 起解析这行，于是它成了跨仓契约，而两侧都没有构建期检查（§6 D-01）；
- `wt-media-agent` 的入口文档：`AGENTS.md`、`README.md`、`contracts/*/README.md`（吸收项）；
- `wt-media-workspace/skills/agent/agent-platform-adapter-change`：改指 `clients/<platform>`，
  并跑 `scripts/sync_skills.py` 同步生成副本；
- `config/release-matrix.yaml`：仅在本 CHG 有可登记的结论时加行/加注，**不改 `0.2.5` 的 status**（D-09）。

### Delete

- 无。本 CHG 不删既有文件。（`start_timeout_ms` **保留**，它由死变活。）

### Explicitly Not Doing

- 不重写现有稳定脚本（`package-release-macos.sh` 只**加**判定，不重排结构）；
- 不为目录整齐整体重构；
- **不改日志命名、轮转、保留**（C 已定型；本 CHG 只在退出路径上碰日志的**写入者生命周期**）；
- **不做 Windows / x86_64 构建**（本机是 arm64，无原生工具链；`release-matrix` 已登记为 residual risk）；
- **不改 Cloud Go 后端与 `web/`**；
- **不实现升级器**（无升级动作可改）；T-07 只证「升级不覆盖」这条否定命题的路径判据；
- **不做「干净机」安装验收**（D-09：登记为未做）。

## 6. Confirmed Decisions

| # | 决定 | 依据 |
|---|---|---|
| D-01 | **就绪用两段式闸门**：第一信号是 Agent 在 `bind`+`listen` 之后打印的 readiness 行（`server.py:624→627→629` 的顺序使它可靠），第二信号是健康检查**真的应答**。`start_timeout_ms` 从死配置变成这道闸门的超时。**不发明新协议**——复用 Agent 已经打印的东西。 | 用户裁定「尽量使用开源，尽可能不改轮子」；4.1 实测「宣告存在但无人听」+「超时键无人读」 |
| D-02 | **实例身份改成活性探针**：判定不再只看受管槽位里那个 `CommandChild` 句柄，而是**非空时才真的问一次** `/healthz`；句柄在而 Agent 不应答 ⇒ 如实报「未在运行」、丢弃句柄并允许重启。**槽位为空时一次请求都不发**——那个端口上可能是开发机上别人的 Agent。 | CHG-057 已登记的实缺陷（4.2） |
| D-03 | **退出请停而非硬杀**：SIGTERM → 宽限窗口（在飞任务收尾）→ 必要时强杀；Desktop 经 `RunEvent::Exit` 触发。**退出报告要能区分「请停后自己退出」与「被强杀」**。 | 成功事实 #8 与失败行为「升级或清理删除业务数据」；4.3 实测一路硬杀 |
| D-04 | **完整性校验放在启动前**，读 `sidecar-manifest.json` 验 sha256；**失败拒绝启动并说清原因**。**复用已有的 `sha2` 直接依赖，不新增依赖**。 | 成功事实 #7；4.4 实测「记录齐全、运行期零校验」+「`sha2` 已在」 |
| D-05 | **`config_online/` 整目录替换进产物**，验收 `diff -r` 无差异。**不携带凭证**（CHG-056 D-07：凭证只走环境变量）⇒ **发布校验不得依赖该通路**。 | 吸收项验收判据；4.5 实测产物无 Agent 配置 |
| D-06 | **五类版本各建一个可得来源**，并在发布脚本加 Desktop ↔ sidecar 的**版本兼容校验**。前端构建版本与组件/资源版本是**新建**。 | 成功事实 #7；4.6 实测两个版本读了不比较、两类无表示 |
| D-07 | **升级不覆盖用路径判据**：保护的是一组路径（用户设置、SQLite、检查点、待回传结果），不是名字清单。 | 成功事实 #8；沿用 C 的 T-06 先例 |
| D-08 | **Q-01 按用户 2026-09-25 裁定关闭**：生产 Cloud 地址**就是本机 `http://127.0.0.1:18080`**。两份出货配置的**值与 CSP 一个字都不改**（`wt-media-agent/config_online/agent.toml:22`、`src-tauri/resources/desktop.production.toml:24`、`csp_connect_src` `:35`）。**要改的是注释**：`agent.toml:17-21` 那段仍写着 Q-01「still open … Resolve before release」，它已成**过期陈述**，由 T-10 回写为「已裁定：保持回环」。**改注释不算改配置**——留一句「还没定」才是真错。 | 用户 2026-09-25 裁定「就按本机 18080 定稿」 |
| D-09 | **「干净机」安装验收按用户 2026-09-25 裁定登记为未做**：本机是开发机，装了 Python/Node/Rust 与 `.local/` 开发树，装一次证不了「没有 Python 的机器」。`release-matrix` 的 `0.2.5` **status 不改**，D 的 DONE Gate **带一条登记过的例外**，不以文字充当证据。 | 用户 2026-09-25 裁定「登记为未做，不宣布发布验证通过」；skill 的 Stop Condition「实机验收需要未提供的权限/资源」 |
| D-10 | **Agent 侧不改轮转与保留**：C 已定型的「有意不对称」（Desktop 由 `file-rotate` 按天删、Agent 由 `LogBudget` 按天删）在本 CHG **原样保留**。D 只动退出路径上写入者的生命周期。 | C 的 §6；避免在 D 内重开已关闭的口径 |
| D-11 | **同一个 401，两道判定给出相反的处置**：T-01 的就绪闸门里 401 **致命**（凭据对不上 = 用不了，等待改不了一份凭据）；T-02 的活性探针里 401 **算活着**（谁在不在与人认不认我们是两个问题，把 401 当「没人应答」会去 `kill` 一个活着的进程）。两条都由同一次实测（`/healthz` 在 `_check_auth` 之后）推出，**不能合并成一条规则**。 | §4.1 实测；两处判定的问题不同，见 `evidence/task-02-identity.md` §3 |

## 7. Pending Questions

| # | 问题 | 状态 | Blocking |
|---|---|---|---|
| Q-01 | `config_online/agent.toml` 与 `resources/desktop.production.toml` 的生产真实 Cloud 地址 | **已关闭（2026-09-25 用户裁定：本机 `http://127.0.0.1:18080`，配置与 CSP 均不改）** | **NO** |
| Q-02 | 「干净机」安装验收（`release-matrix` 的 `0.2.5` manual_acceptance 第 1 条） | **已裁定（2026-09-25）：登记为未做**，`0.2.5` 的 status 不改 | **NO**（但 D 的 DONE Gate 因此带一条登记过的例外） |
| Q-03 | Windows x64 与 macOS x86_64 构建 | 不在本 CHG 范围；`release-matrix` 已登记为 `residual_risks` | NO |
| Q-04 | 「组件与资源版本」的**口径**（版本从哪算、资源清单算不算它的输入） | 待 T-06 实施时定；若定不下则退回用户 | **YES（T-06 内）** |

## 8. Implementation Tasks

顺序即依赖顺序。每条都要有**先失败的验证/测试**、变异、阴性对照与独立提交。

| Task | 内容 | 仓 | 状态 | 判据 |
|---|---|---|---|---|
| T-01 | **就绪闸门**：解析 Agent 的 readiness 行作为第一信号，健康检查应答作为第二信号；`start_timeout_ms` 变成真超时且**真的会超时** | desktop + agent | **DONE** | 「打印了但不应答」与「不应答且不打印」两种形态各有用例；超时按配置值生效；变异打掉自己。**加一臂**：401（令牌漂移）致命且不等待——依据是 `/healthz` 在 `_check_auth` 之后（§4.1 实测补记） |
| T-02 | **活性探针**：`already_running` 的判定改为问一次；sidecar 死后如实报「未在运行」并允许重启 | desktop | **DONE** | 先有一条**能红的**用例复现 CHG-057 登记的缺陷（杀掉 sidecar 后仍说已在运行）；修复后同一条转绿。变异 **8/8**；第一轮曾 6/8，两个存活变异各查出一处真洞（详见 `evidence/task-02-identity.md` §4.1） |
| T-03 | **退出收尾**：Desktop `RunEvent::Exit` → SIGTERM → 宽限 → 强杀；Agent 侧 SIGTERM 处理与在飞任务收尾 | desktop + agent | **DONE** | 真机上两条读数**都拿到**（`--ignored real_agent`：Desktop 自己那条停路对上真 Agent 进程，`Some(0)`/518ms 与 `Some(9)`/1ms，5 次连跑 5/5）；先红是把 `stop` 还原成 HEAD 的硬杀形状，两条用例都红（日志不可区分、`(None, Some(9))`、窗口 900µs）；变异 agent 5/5 + desktop 9/9。**随包 onefile sidecar 那一臂做不到**（本机 `dlopen` 被签名拒），引导器是否转发 SIGTERM 未测——登记在证据 §7 |
| T-04 | **运行期完整性校验**：启动前读 `sidecar-manifest.json` 验 sha256，失败拒绝启动 | desktop | TODO | 篡改一个字节的 sidecar 必须被拒且报出原因；完好时必须通过（阳性对照）；**不新增依赖** |
| T-05 | **`config_online → 产物/config`**：打包步骤 + `bundle.resources` 补 Agent 配置 + `diff -r` 校验 | desktop + agent | TODO | 产物内配置与 `config_online/` `diff -r` 无差异；**产物里不含凭证**（D-05） |
| T-06 | **五类版本**：Desktop / Agent / 前端构建 / Contract / 组件与资源各一个来源；发布脚本加 Desktop ↔ sidecar 版本兼容校验 | desktop + workspace | TODO | 五类逐个有可得来源（每条附命令）；版本不匹配的包**必须被拒**（先造一个不匹配的，看它红）；Q-04 一并关闭 |
| T-07 | **升级不覆盖**：用路径判据证明升级路径不写用户设置 / SQLite / 检查点 / 待回传结果 | desktop + agent | TODO | 先写一条会红的用例（把某条用户数据路径喂进升级写入集合）；按路径而非名字 |
| T-08 | **M2 业务回归**：对 A/B/C/D 之后的树重跑 M2 链路 | workspace + cloud | TODO | `m2b_local_acceptance.py` 读数；实网/实凭据部分按 §7 如实标注覆盖与否 |
| T-09 | **吸收项**：Agent 侧 `AGENTS.md`/`README.md`/`contracts/*/README.md` 同步；workspace skill 改指 `clients/<platform>` 并跑 `sync_skills.py` | agent + workspace | TODO | `sync_skills.py` 后生成副本与源一致；skill 里的路径真的存在（resolve 判据，不只是字符串） |
| T-10 | **回写基线 + 关闭收尾**：架构基线、里程碑、`release-matrix`、`LEDGER.md`、快照与归档；并把 `config_online/agent.toml:17-21` 那段过期的 Q-01 注释改成「已裁定：保持回环」（D-08） | workspace + agent | TODO | 先失败的检查钉着回写；关闭门禁同集合阳性对照；档案两遍扫描 |

## 9. Repository Checklist

### wt-media-workspace

- [ ] `config/release-matrix.yaml`：五类版本相关字段与判定（**不改 `0.2.5` 的 status**）
- [ ] `skills/agent/agent-platform-adapter-change` 改指 `clients/<platform>` + `python3 scripts/sync_skills.py`
- [ ] 本 CHG 的记录与证据、`LEDGER.md`、里程碑回写、快照重生成、归档

### wt-media-agent

- [x] `local_api/server.py`：SIGTERM 处理与在飞任务收尾（T-03）——`70a1647`；
      `daemon_threads = False` 与「stopped」的位置各有一条会红的用例钉着
- [ ] `scripts/build_desktop_sidecar.py`：`config_online/ → 产物/config` 整目录替换（T-05）
- [ ] 入口文档同步（`AGENTS.md`、`README.md`、`contracts/*/README.md`）（T-09）

### wt-media-desktop

- [ ] `src-tauri/src/sidecar/`：完整性校验（T-04）
- [x] `src-tauri/src/sidecar/`：就绪闸门（T-01）
- [x] `src-tauri/src/sidecar/` + `commands/agent.rs` + `main.rs`：退出收尾（T-03）——`242f61e`；
      `ask`/`alive`/`force` 三个函数、`stop()` 的请停→宽限→强杀、`RunEvent::Exit` 钩子
- [x] `src-tauri/src/commands/agent.rs`：活性探针（T-02）——`c54025a` 生产修复 + 4 条用例；
      `15951a4` 的 `tauri` `test` feature dev-dependency 与 `R: Runtime` 泛化是它的前置
- [ ] `src-tauri/tauri.conf.json`：`bundle.resources` 补 Agent 配置（T-05）
- [ ] `scripts/package-release-macos.sh`：相等性判定（T-04 的打包侧一半）与版本兼容校验（T-06）
- [ ] 五类版本中的 Desktop 与前端构建版本来源（T-06）

## 10. Acceptance Matrix

| AC | 内容 | 判据 | 状态 |
|---|---|---|---|
| AC-01 | 就绪是确认过的：readiness 行 + 健康应答；超时真的会超时 | 两种失败形态各一条用例 + 真机读数 | TODO（T-01） |
| AC-02 | 不会连上旧进程：sidecar 死后如实报「未在运行」 | 先红后绿的复现用例 + 真机读数 | **一半**（T-02）：先红后绿已成立（`evidence/task-02-red.out` / `task-02-green.out`，真 `CommandChild` + 真无人听的端口）；**真机读数未做**，按 T-02 证据 §7 第 1 条登记，不以文字充当证据 |
| AC-03 | 退出是收尾过的：请停 → 宽限 → 强杀；报告能区分 | 真机两条读数 | **满足**（T-03）：两条读数都是真 Agent 进程给的（`task-03-desktop-real-agent.out`），请停/自行退出/宽限强杀三条记录互不重名。**一处例外**：随包 onefile sidecar 的引导器是否转发 SIGTERM **未测**（本机跑不起来，D-09 式登记，见 `evidence/task-03-exit.md` §7 第 1 条） |
| AC-04 | 随包 sidecar 被验过：篡改必拒、完好必过 | 阳性对照 + 阴性对照各一条 | TODO（T-04） |
| AC-05 | 产物带着 Agent 配置且 `diff -r` 无差异；**不含凭证** | `diff -r` 输出 + 凭据扫描阳性对照 | TODO（T-05） |
| AC-06 | 五类版本可追溯；Desktop ↔ sidecar 版本不匹配必拒 | 五条来源命令 + 一条不匹配必红的用例 | TODO（T-06） |
| AC-07 | 升级不覆盖用户设置 / SQLite / 检查点 / 待回传结果 | 路径判据的用例（先红） | TODO（T-07） |
| AC-08 | M2 业务回归对 A/B/C/D 之后的树通过 | `m2b_local_acceptance.py` 读数；实网部分按覆盖情况如实标注 | TODO（T-08） |
| AC-09 | 正式安装包脱离开发源码 / venv / 开发机路径可运行 | **含一条登记过的例外**：干净机这一臂**未做**（D-09）——能证的是「产物不含 `config_online` 之外的开发态路径引用」与「sidecar 是随包原生二进制」；**不证**「在没有 Python 的机器上装过」 | TODO（T-05/T-06；例外见 D-09） |
| AC-10 | 发布可追溯五类版本 | 同 AC-06 | TODO（T-06） |
| AC-11 | 计数只增不减 | desktop 336 / agent 377 为分母，逐任务报增量；agent 若有例外**先登记再吸收** | 进行中 |

## 11. Evidence

- `evidence/task-01-readiness.md`——就绪闸门：两种失败形态、超时读数、变异表。**已产出**，
  另附原始转录 `evidence/agent-probe.out`（真机起 Agent）与 `evidence/agent-probe-phases.out`（两段式探针）
- `evidence/task-02-identity.md`——**先红**的复现（CHG-057 登记的缺陷）与修复后的绿。**已产出**，
  另附原始转录 `evidence/task-02-red.out`（守卫还原成修复前形状后同一条用例转红）、
  `evidence/task-02-green.out`（修复后该过滤器下 16 passed）、
  `evidence/task-02-mutations.out`（8/8 变异表）
- `evidence/task-03-exit.md`——请停/宽限/强杀两侧的形态、先红读数、真机两条读数与退出报告形状。**已产出**，
  另附原始转录 `evidence/task-03-desktop-red.out`（`stop` 还原成硬杀后两条用例转红）、
  `evidence/task-03-desktop-green.out`（353 passed / 0 failed / 4 ignored）、
  `evidence/task-03-desktop-real-agent.out`（`--ignored real_agent`，两条真机读数）、
  `evidence/task-03-agent-green.out`（agent 382 OK）、
  `evidence/task-03-agent-mutations.out`（5/5）、`evidence/task-03-desktop-mutations.out`（9/9）、
  `evidence/task-03-sidecar-bootloader-untested.out`（随包 onefile 在本机 `dlopen` 被拒，故该臂未测）
- `evidence/task-04-integrity.md`——篡改必拒 / 完好必过 / 打包侧相等性判定
- `evidence/task-05-shipped-config.md`——`diff -r` 输出、产物树、凭据扫描（带阳性对照与分母）
- `evidence/task-06-versions.md`——五类版本的来源命令与不匹配必红
- `evidence/task-07-upgrade.md`——路径判据的先红用例与结论
- `evidence/task-08-m2-regression.md`——M2 重跑读数与**覆盖情况**（实网/实凭据部分逐条标注）
- `evidence/task-09-absorbed.md`——文档同步与 skill 路径 resolve
- `evidence/task-10-writeback-and-close.md`、`evidence/test-summary.md`

## 12. Current Checkpoint

- **Completed**：
  - **激活**（`git mv` 自 `planned/`，草案改写为十三节执行记录，§4 的每条事实都是 2026-09-25 实测）；
    Q-01 与 Q-02 由用户 2026-09-25 裁定关闭。
  - **T-01 就绪闸门**（双侧）。desktop 336→**344** passed / 0 failed（2→3 ignored）；
    agent 377→**378** OK；编译警告 7→**7**（新增 0，基线是还原三个文件后**测**出来的）；
    变异 **8/8** 打掉自己的用例；真机臂是**本 crate 的 `gate` 对上真实的 Agent 进程**
    （`--ignored real_agent` 通过，并用阳性对照证明它真的读到了真机那一行）。
    详见 `evidence/task-01-readiness.md`。
  - **T-02 活性探针**（desktop）。344→**348** passed / 0 failed（ignored 仍 3）；警告 7→**7**；
    变异 **8/8**（第一轮 6/8，两个存活变异各查出一处真洞：一条断言在说自己证明不了的事、
    一条变异被错派给看不见它的用例——两处都已改，不是调断言了事）；
    先红读数见 `evidence/task-02-red.out`。**AC-02 只算一半**：真机读数未做，按 D-09 的登记方式
    如实标注。详见 `evidence/task-02-identity.md`。
  - **T-03 退出收尾**（双侧）。desktop 348→**353** passed / 0 failed（ignored 3→**4**，新增的那条
    就是真机臂）；agent 378→**382** OK；编译警告 7→**7**；变异 agent **5/5** + desktop **9/9**；
    先红是把 `stop` 还原成 HEAD 的硬杀形状后两条用例都红（两条 arm 的日志**不可区分**、
    `(None, Some(9))`、窗口 900µs）；真机两条读数由 Desktop 自己的停路对着真 Agent 进程取得
    （`Some(0)`/518ms、`Some(9)`/1ms，连跑 5 次 5/5）。详见 `evidence/task-03-exit.md`。
    **一处例外照 D-09 登记**：随包 onefile sidecar 在本机 `dlopen` 被签名拒，故「引导器是否
    转发 SIGTERM」未测；`RunEvent::Exit` 钩子本身只有阅读级覆盖。
- **Current**：T-04 运行期完整性校验——尚未开工。
- **Next**：T-04 → T-05 → T-06 → T-07 → T-08 → T-09 → T-10。
- **Blocked**：无。Q-04（「组件与资源版本」的口径）在 **T-06 内部**待定，若定不下则退回用户。
- **不动的东西**（免得后来者以为是漏项）：两份出货配置与 CSP（D-08）、日志轮转与保留（D-10）、
  Cloud 的 Go 后端与 `web/`、`0.2.5` 的 status（D-09）、Windows/x86_64 构建（Q-03）。

## 13. DONE Gate

- [ ] 每个 Task 有先失败的验证/测试、最小实现、测试、diff 检查、evidence、checkpoint、独立提交
- [ ] AC-01…AC-11 逐条有判据；**AC-09 的例外按 D-09 登记，不以文字充当证据**
- [ ] Manual verification evidence recorded where required.——**不完全满足，如实标注**：干净机那一臂**未做**；
      其余真机臂（就绪、活性、退出、完整性、产物配置、版本）**都做**
- [ ] 计数只增不减（desktop 336 / agent 377 为分母；例外先登记）
- [ ] 一仓一 commit；「移动文件」与「改逻辑」不同 commit；desktop 只对单个文件跑 `rustfmt`
- [ ] 关闭门禁：三个校验器 + `unittest discover`（**4 条既知红项**，判据是同集合阳性对照，不是「看着无关」）
- [ ] `release-matrix.yaml` 的更新**只加不改**（`0.2.5` 的 status 保持 `verifying`）
- [ ] 归档：`git mv` 到 `delivery/completed/`，`LEDGER.md` 与 `planned/README.md` 同步，快照用 `--no-active` 重生成
