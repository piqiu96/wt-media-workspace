# Evidence: 架构基线核对与三仓入口文档回写（T-10）

- CHG: `CHG-20260923-056`
- Task: `T-10`
- Date: 2026-09-24
- Type: governance + docs
- Status: PASS（回写完成 3/3 仓；基线核对逐节给出判据，2 处偏离逐条登记在 §偏离）

## Purpose

T-10 有两件事，证据要分开留：

1. **三仓 AI 入口文档按实际新布局回写。** T-02…T-08 搬了目录、拆了模块、改了
   地址来源，文档必须跟上——否则下一个 agent 会照着旧树找代码。
2. **核对 workspace 架构基线。** 基线在程序启动时已按 ADR-0016 改写完毕，本次的
   任务是**逐节核对**「文档写的」与「代码实际是的」，并**登记** `core/` 的撤销。

核对不是「看一眼觉得一致」，所以下面每节都给出可重跑的命令与原始输出。

## 一、三仓入口文档回写

判断一个文档是否过时，用**退役名扫描**：拿已删除的模块名/路径去打，命中即过时。
`executors/` 与 `local_api/` 的 URL 字面量清零这类事实，再补一次源码扫描做交叉验证。

### Agent 仓（`ba179ed`）

    退役名扫描  log_setup|proxy_check|runtimes/|core/profile_guard|未迁出|尚余|8765|18080|目标布局
      分母 5 个 md → 3 命中，逐条都是合法的（README 的临时端口 18765；AGENTS.md 新增的 runtime/constants.py）
      ⇒ 无退役名残留
    交叉验证    grep -rn 'https\?://' src/wt_media_agent/{executors,local_api}/          → 0 命中
                阳性对照 grep -rln 'https\?://' src/wt_media_agent/clients/             → 4 个文件（平台表与各 identity）
    分母写明    4344 行 src、395 行 executors、714 行 local_api

改了什么：`AGENTS.md` 的 Structure（旧树 `app.py`/`runner.py`/`core/`/`runtimes/`
+ 两个顶层模块）、`AGENT-INDEX.md` 的分层与需求路由、`DIRECTORY_MAP.md:49` 的
「尚余 4 处未迁出」（已由 `a4a43cc` 清零，且补上缺失的 `clients/platform_urls.py` 行）、
`README.md` 的 Key Directories。

**一次自查纠正**：第一版扫描用 `for f in $files` 遍历 `ls` 的输出。zsh 不对未加引号的
变量做词分割，`$f` 成了整个多行字符串，grep 拿到多行文件名报错、又被 `2>/dev/null` 吞掉，
于是「0 命中」。用 `runtime/constants.py` 做阳性对照才暴露出来——同一模式手工跑是有命中的。
换成 glob 重跑后得到上面那 3 条命中。**这条记录的存在本身就是「否定结论必须先证明检查会失败」
的一个实例**：那次 0 命中是检查坏了，不是仓库干净。

### Desktop 仓（`5c74ca1` 文档 + `2599819` 注释）

    退役名扫描  local_agent/mod|Client::new|1570|8765|18080|npm test|npm run verify|future sidecar|placeholder
      分母 5 个 md → 2 命中，两条都是我这次新写的「本仓库没有 src/ 顶层目录」
      ⇒ 无退役名残留

改了什么：`DIRECTORY_MAP.md` 的入口/命令/生命周期三节（`bootstrap.rs`/`config.rs`/
`paths.rs`/`token.rs`/`state.rs`/`http/`/`dto/`/`preflight.rs`/`resources/` 全部缺失；
sidecar 启停其实在 `sidecar/` 而非 `local_agent/`）、`AGENT-INDEX.md`、
`AGENTS.md` 的 Structure、`README.md`（原先声称本仓有 `src/` Vue 页面、用
`npm test` 验证、`binaries` 是 future placeholders——三条全不成立）。

**顺带查到一处被夸大的能力描述**，两处都改了：

    Agent 侧确有 text/event-stream 端点   local_api/server.py:445
    Desktop 侧消费流的地方                 0 处（commands/agent.rs 的 local_agent_task_status 打的是状态端点，返回快照）

文档写的是「Rust 代理 Local Agent HTTP 与 SSE」。这条 overstated 不改变行为，
但会让下一个 agent 去找一条不存在的流，所以文档按实际改写、并在 `main.rs` 与
`commands/agent.rs` 的两条注释里点明「不要写成已实现」（注释改动单独一个 commit）。

### Cloud 仓（`f89467f`）

    退役名扫描  18080|127\.0\.0\.1:8765   分母 5 个 md → 0 命中
    阳性对照    同一模式打 web/src/**（*.vue/*.js，排除 test）→ 7 命中，正是登记为残留的三处：
                AccountsPage.vue:493-497、ProfilesPage.vue:208-212、shared/api/http.js:89
    ⇒ 0 命中是真的 0，且残留清单与 T-09 登记的一致

改了什么：只补 T-08 的缺口——`DIRECTORY_MAP.md` 补
`web/src/apps/desktop/features/local-agent/init.js`（唯一知道地址从哪来的点）与
仓库根的 `web/src/localAgentBoundary.test.js`（常驻边界断言），`AGENT-INDEX.md`
的需求路由补一行。

    三仓验证   agent   bash scripts/test.sh        → Ran 253 tests  OK
               desktop cargo test --workspace      → 63 passed; 0 failed
               cloud   cd web && npm test          → 21 files / 101 tests passed

## 二、基线逐节核对

基线文件：`docs/engineering/architecture/社媒运营平台工程架构与分层设计_V1.md`。

### §5.2 推荐目录 — **有偏离，见 §偏离 1/2**

实际 `src/wt_media_agent/` 一级条目（`ls -1`，剔除 `__pycache__`）：

    __init__.py  bootstrap  clients  executors  generated  local_api  modes
    runner  runtime  services  storage  utils  adapters
    cloud_agent_client.py  cloud_agent_contract.py
    cloud_main.py  local_main.py  sidecar_main.py

§5.2 的树声明了其中 11 项（`__init__`、`sidecar_main`、bootstrap、runtime、runner、
executors、clients、services、storage、local_api、utils）。**多出来的 7 项**分三类，
逐条落在下面。根级同理：§5.2 未列 `AGENT-INDEX.md`、`DIRECTORY_MAP.md`、`uv.lock`，
三者实际存在（前两个是本轮 AI 入口治理的产物，`uv.lock` 是 uv 的锁文件）。

### §5.4 分层关系 — **一致，且是机器校验的**

    bootstrap → runner → executors → {clients, services, storage}
    runtime 横切；local_api 与 runner 平行

对照 `tests/test_dependency_boundaries.py`：R2 白名单给出允许的层间方向，R10 把观测到的
层对边集合**冻结成棘轮**（`FROZEN_LAYER_EDGES`，`:167`「as observed at T-05」，新增跨界边即失败）。
`bash scripts/test.sh` 全绿 ⇒ 实际依赖方向满足 §5.4，不是靠约定。

### §5.5 平台目录 — **一致**

    clients/            实际：bitbrowser/ bilibili/ baijiahao/ cloud/
    §5.5 点名           bitbrowser/、bilibili/identity.py、baijiahao/identity.py —— 全部存在
    §5.5 禁止           不提前创建未实现的平台目录
    douyin/             实际 absent（内容发现按 ADR-0015 归 Cloud，Agent 侧不建）—— 符合

`clients/cloud/` 不在 §5.5 的例子里，但 ADR-0016 第 2 条把 Cloud 协议明确列在
`clients/`（「外部系统协议（Cloud、BitBrowser、平台身份、代理）」），故一致而非偏离。

### §5.8 本地目录和日志 — **macOS/dev/override 一致；Windows 分支未实现**

`runtime/paths.py` 三态对照：

    override   config 的 data_dir 非空 → <data_dir> 及 <data_dir>/logs          与 §5.8 的 override 语义一致
    dev        非 frozen 且非 production → <repo>/.local/{data,logs}           与 §5.8 的 dev 路径一致
    installed  frozen 或 production → ~/Library/Application Support/WTMedia/Agent
                                     + ~/Library/Logs/WTMedia/Agent            与 §5.8 的 macOS 一致
    data/logs/versions 懒创建，失败降级为空操作                                与 §5.8「均懒创建」一致
    配置不在数据目录内                                                        与 §5.8 末段一致

**但 `paths.py` 里没有任何 `sys.platform` 分支**（`grep -c 'sys.platform|os.name|windows|Windows'`
在 124 行里 0 命中）。installed 分支无条件走 `Path.home()` + `("Library","Application Support",...)`。
§5.8 另外指定了 Windows 的 `%LOCALAPPDATA%\WTMedia\Agent\`，而基线 §1.4 把 Windows x64
列为桌面首版支持范围之一。登记为 §偏离 2。

### ADR-0016 层表 — **一致**

ADR-0016 第 2 条的目录职责表（bootstrap/runtime/runner/executors/clients/services/
storage/local_api/utils）与 §5.4、与实际三层一致；第 3 条的依赖规则由 R3（明禁边单独报错）
与 R4/R5（executors 不得直接 `sqlite3`/`subprocess`/`socket`/…、不得构造 client）落地。
`core/` 在 ADR-0016 的层表里**不存在**，见下。

## 三、登记：`core/` 撤销

`core/` 是本次唯一被物理撤销的包，撤销方式是迁移而非删除：

    core/profile_guard.py   →   services/profile_guard.py
    实际态                  ls src/wt_media_agent/ → 无 core/（见 §5.2 的一级条目清单）

基线侧无需改动：§5.2 的 `:1040` 早已明写「不保留 `modes/`、`core/`、`communication/`、
`runtimes/`、`platforms/`、`generated/`」，ADR-0016 第 2 条的层表也没有 `core/` 一层。
**这条登记的意义是「代码追上了文档」**：撤销之后基线不再是被违反的，而是被满足的。

同批消失的还有 `runtimes/`（拆入 `clients/` 与 `services/`，§5.2 同样明写不保留）
与根级 `config.py`/`log_setup.py`（T-03 删除，其内容迁入 `runtime/`）。

## 偏离（逐条登记，本次不改）

### 偏离 1 — §5.2 的树与实际的 7 项差集

| 实际多出来的 | 性质 | 处置 |
|---|---|---|
| `local_main.py`、`cloud_main.py` | 进程入口。§5.2 只列了 `sidecar_main.py` | 登记；ADR-0016 四条入口的现实一致，基线树是不完整的示意 |
| `cloud_agent_client.py`、`cloud_agent_contract.py` | T-02 留的**废弃导入 shim**，仅为冻结的 `tests/test_runner_session.py` 保留 | 登记；计划已写明在 CHG-B/C 退役 |
| `adapters/` | 占位包（一行 docstring），基线**全文未提及** | 登记；计划明写「三个已登记占位包不动」 |
| `modes/` | 占位包（一行 docstring），基线 `:1040` 明写**不保留** | **待用户裁定**：基线与计划相反 |
| `generated/` | 占位包（一行 docstring），基线 `:1040` 明写**不保留** | **待用户裁定**：同上 |

`modes/` 与 `generated/` 是**基线与实现正面冲突**的两处，且这次的处置是计划预先定的
（「不动」）。按纪律，文档明写「不保留」的例外不擅自回写，故留作待裁定项。两者都是一行
docstring、零实现、零引用，裁定成本很低：要么删掉三个占位包，要么把 `:1040` 的清单改成
「保留为占位」。

### 偏离 2 — §5.8 的 Windows 路径未实现

`runtime/paths.py`（124 行）无平台分支，installed 态在 Windows 上会落到
`%USERPROFILE%\Library\Application Support\WTMedia\Agent`，而 §5.8 指定
`%LOCALAPPDATA%\WTMedia\Agent\`。基线 §1.4 把 Windows x64 列为桌面首版支持范围。

本次只登记不改：T-03 的计划文本本身就只写了 macOS 的形状，修它属于新增平台分支 + 测试，
超出「结构审计、Config 与 Client 解耦」的范围。**这一条不是「测试通过所以没事」**——
是本次全部取证都只在 macOS 上做过（T-09 的覆盖边界第 2 条已写明不可外推到
Windows/Linux），所以它在 Windows 上是否真的错，本 CHG 没有判据，只报机制。

## 覆盖边界（未覆盖的逐条写明）

1. **§5.2 的差集是「按一级条目比对」**，不是逐文件比对；包内部的文件级漂移不在本核对内。
2. **§5.8 的 Windows 行为完全没有在 Windows 上跑过**（本机 macOS）。偏离 2 报的是代码里
   没有平台分支这一静态事实，不是实测的 Windows 失败。
3. **`modes/` / `generated/` / `adapters/` 是否有外部引用** 只查了本仓 `src/`、`tests/`、
   `scripts/`；workspace 的 skill 与 verify 脚本未逐个复查。
4. **基线其余章节（第一～四章、第六章、第七章及以后）未逐节核对**，只核了计划点名的
   §5.2/§5.4/§5.5/§5.8 与 ADR-0016 的层表。核对范围**就是这五处**，别把它读成「整份基线已核对」。
5. **文档回写的判据是退役名扫描**，它只能抓「名字还在」这类过时；措辞层面的失真
   （例如把某能力写强了）抓不到——§一里 SSE 那条就是靠人工读出来的，不是扫描出来的。
