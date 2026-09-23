# Evidence: AC-01…AC-11 验收矩阵（T-09）

- CHG: `CHG-20260923-056`
- Task: `T-09`
- Date: 2026-09-24
- Type: e2e + test + mutation + governance
- Status: PASS（11/11 逐条有判据；未覆盖项逐条列在 §覆盖边界）

## Purpose

T-09 是联调回归与证据落盘：把 AC-01…AC-11 逐条钉到**可重跑的工具**上，并明确每条
**覆盖到什么、没覆盖到什么**。工具全部位于 `evidence/tools/`（照 CHG-055 先例），
**不复用** `verify_m1_integration.py`（其 `contract_revision` 期望已过期，且
`run_desktop_verify()` 执行 `npm run verify` 而 desktop 仓没有 `package.json`）。

每条 AC 都附**阳性对照**——「没命中」「没通过」这两种否定结论必须能失败，否则无从区分
「检查通过」与「检查空转」。

## 环境事实（全部实测）

| 项 | 值 |
|---|---|
| Agent HEAD | `da6f593`（工作树 clean） |
| Desktop HEAD | `35a2ee9`（工作树 clean） |
| Workspace HEAD | `901179d` |
| Cloud（隔离） | `http://127.0.0.1:18199`，独立 schema `wt_media_cloud_ac10`，来自本检出构建的 `cmd/server` |
| Cloud（开发者自己） | `:18080` —— **只读探活**（AC-05 的 `/healthz`），不建任务、不轮询 |
| BitBrowser | `:54345` 正常，40 profiles，主身份 `2c9bc06191effa4e0191f9589996619f` |
| 开发者自己的 dev Agent | `:8765`（PID 55443）**全程未触碰**；所有启动用 scratch 端口 |

**为什么不复用开发者的 Cloud 跑任务链**：`claimTask` 是
`ORDER BY created_at ASC LIMIT 1`（`repository/mysql_task_store.go:123-126`，无 type/agent 过滤），
该实例的表里有 7 月的 `profile_open_task` 积压——在那上面起 runner 会打开真实浏览器 profile
并把别人的任务标成失败。故 AC-10 另建实例与 schema，从空表跑。

## Method / Actual（逐条）

### AC-01 — Agent 脱离 Desktop，用 `config/agent.toml` + 环境变量启动，`/healthz` 200

`evidence/tools/ac01_ac09_agent_modes.py`（四棵树证明「文件真的被读」+ MODE 1）：

    1. 真检出                        exit=0  warnings: 0
    2. 副本 + 伪造键 + 凭据键        exit=0  warnings: 2
         ignoring unknown config key agent.bogus_key
         ignoring sensitive key agent.runtime_token from the config file; credentials are environment-only
    3. 副本改一个值                  exit=0  resolved agent_id='ac09-from-file'
    4. 副本写坏 TOML                 exit=1  reported=True

    MODE 1: 监听 54848（默认 8765 是开发者的，未用）
      GET /healthz      -> 200 {"status":"ok","service":"wt-media-agent","mode":"m1"}
      GET /api/v1/status-> 200 bitbrowser_status='normal' profiles=40
      数据目录 -> ['local-agent.sqlite3', '-shm', '-wal', 'logs', 'versions']
      停止后 listening=False

树 2 是 D-07 的正向证据：**凭据键按名忽略**（只报键名不报值）。树 4 的 `exit=1` 与树 1/2/3 的
`exit=0` 互为对照，证明「能启动」不是「解析器忽略了整份文件」。

### AC-02 — `executors/`、`local_api/` 下不得构造客户端；环境变量只在一个模块

`evidence/tools/ac02_agent_boundary.sh`（grep + T-05 的 AST 测试双证据）：

    os.getenv / os.environ in src/        2 hit(s) (of 4344 lines)
        src/wt_media_agent/runtime/config.py:291, :330   <- 两处都在允许的那一个模块
    BitBrowserClient( in src/             1 hit(s) (of 4344 lines)
        src/wt_media_agent/clients/bitbrowser/factory.py:27
      ... under executors/                0 hit(s) (of 395 lines)
      ... under local_api/                0 hit(s) (of 714 lines)
    CloudAgentClient( in src/             1 hit(s) (of 4344 lines)
        src/wt_media_agent/bootstrap/app.py:85
      ... under executors/                0 hit(s) (of 395 lines)
    AST 边界测试（tests/test_dependency_boundaries.py）: Ran 29 tests  OK

**分母写明**（4344 / 395 / 714 行）并附**活的阳性对照**——脚本自己先验证「这些模式能命中
它们该命中的东西」，否则 0 命中与「模式写错」同形。

### AC-03 — sidecar 用受控参数启动；带 token 200 / 无 token 401

同一工具的 MODE 3（直接给四个变量启动），另有 AC-05 的 M3（**Desktop 真的把它拉起来**）：

    HOST=127.0.0.1 PORT=54862 TOKEN=<set> DATA_DIR=<scratch>
    监听 127.0.0.1:54862（不是默认 8765）⇒ PORT 被采纳
    /healthz 带对 token -> 200 ；不带 -> 401 ；带错 -> 401
    /api/v1/status (带 token) -> 200 profiles=40
    argv: <venv python> -m wt_media_agent.sidecar_main

### AC-04 — Desktop 测试全绿且 `main.rs` 收敛

`evidence/tools/ac04_desktop.sh`：

    cargo test --workspace -> 63 passed; 0 failed
    main.rs: 115 lines (ceiling 300)

（T-06 时为 89 行；T-07 的配置引导与 CSP 注入落在 `main.rs` 后为 **115 行**，仍远低于 300。）

### AC-05 — 页面地址来自 `get_public_config`，且 app 树无 18080

运行期：`evidence/tools/ac05_desktop_launch.py` 四次真实启动，见
**`evidence/task-09-desktop-launch.md`**（含 T-07 遗留①②④与两向 CSP 的完整取证）。
静态面：

    grep -rn 18080 src/apps/desktop/   -> 0 命中（分母 9 个 js/vue 文件）
    阳性对照 get_public_config         -> 命中 init.js
    同目录 127.0.0.1 字面量            -> 0 命中
    shared/api/http.js:89              -> 1 命中（已按用户裁定登记为 CHG 外残留）

### AC-06 — 四条本机链路 + 真实 Desktop 观察

`evidence/tools/ac06_local_chains.py`（直打 Agent 本地 API —— 即 Desktop 命令所代理的同一目标）：

    bind          200，返回 node id 与新的 64-hex session token；缺 token 400 binding_token_required
    profile       scan 200（40 profiles / 1 group）；open/close 使 BitBrowser 自己的 status 0 -> 1 -> 0
                  缺 id 400 profile_id_required
    account-check 真实 bilibili 账号识别为 login_status='normal' platform_account_id='3706971620379308'，4 个 check_items
                  平台越界 400 account_check_input_invalid
                  期望值=真实 id 200 不误报；期望值=错 id 200 account_mismatch（**两个方向都测了**）
    cookie-read   36 个真实 cookie；31 个可检索值一个都没出现在 Agent 日志里
                  阳性对照：profile id 在日志中可见 -> True（扫描有效）
                  缺 id 400 cookie_read_input_invalid
    结束态        被打开的 profile 已复原为 status=0；agent 已停（exit=-15）

    COVERAGE: 16 exercised, 3 not（未做的三条原文列在工具输出末尾，含理由）

真实 Desktop 侧的对应观察由 AC-05 的 M2/M3 给出（Desktop 自己的 client 打到 Agent 得 200）。

### AC-07 — 三仓测试

`evidence/tools/ac07_three_repos.sh`：

    wt-media-agent      bash scripts/test.sh            Ran 253 tests  OK       (基线 85，单调不降)
    wt-media-desktop    cargo test --workspace           63 passed
    wt-media-cloud/web  npm test                         21 files / 101 tests passed

### AC-08 — 治理校验

`evidence/tools/ac08_governance.sh`：

    verify_agent_entry.py          execution snapshot 2104 chars (~842 tokens, budget 8000)  0 warning  exit=0
    verify_delivery_governance.py  ok, Active CHG: CHG-20260923-056                           exit=0
    阳性对照（把同一对校验器指向一份故意弄坏的副本）:
      verify_agent_entry.py            exit=1  ERROR missing execution snapshot
      verify_delivery_governance.py    exit=1  ERROR current context and ledger disagree

对照那一半是本条的关键：0 ERROR 只有在「校验器会红」被证明之后才有意义。

### AC-09 — 三模式各一次真实启动

`ac01_ac09_agent_modes.py`：

    local   : /healthz 200、/api/v1/status 200（BitBrowser normal、40 profiles）、停止后无监听
    cloud   : 0.09s 退出 0，打印环境事实 JSON（agent_id/cloud_base_url/data_dir/environment/
              mode=cloud/run_runner=false/version=0.2.2）——cloud_base_url 故意指向死地址
              http://127.0.0.1:1，0.09s 内返回即证明**没有发任何请求**（默认不轮询）
    sidecar : 见 AC-03

外加 AC-05 的四次 Desktop 启动（Desktop 拉起的 Agent 是第 4 类真实启动）。

### AC-10 — 任务链路 e2e + 崩溃恢复

`evidence/tools/ac10_task_chain.py`（隔离 Cloud，空表起步；开工前先断言表是空的）：

    LEG A  创建 noop 任务 -> runner 领取 -> 执行 -> 上报
           Cloud 行 status=succeeded progress=100 message='noop succeeded' agent_id='ac10-agent'
           日志 'executing task'=True 'task succeeded'=True
           本任务 checkpoint 行数 = 0（成功后已清），且文件确实存在（在同一次运行的另一 leg 里看到过 running 行，
           故 0 行是「清掉了」而非「从没写过」）
    LEG B  上报被代理挂住 -> checkpoint 落盘 running -> SIGKILL
           Cloud 此时仍 status='leased'（没被误报成功）
           SIGKILL 后 checkpoint 仍在且仍为 running
           重启后日志 'recovering 1 incomplete task(s)'=True 且 'resuming task <id> at progress 0'
           重启后 checkpoint 仍是 running —— 恢复**不重跑**，工具按实际行为断言，不假定更强的行为

### AC-11 — demo executor / client 落成常驻测试

常驻测试 `tests/test_new_task_type.py`（**产品代码零改动**：新任务类型与它的 client 全在测试文件里定义，
经公开缝 `TaskRunner.register_executor` 装入）。失败验证 `/tmp/ac11-mutants.py`：

    DETECTOR SELF-CHECK  故意制造一次失败 -> FAILED（探测器会红）
    M-01 不注册工厂                                    CAUGHT
    M-02 executor 不用新 client                        CAUGHT
    M-03 runner 完成后不清 checkpoint                  CAUGHT
    M-04 runner 不写 running checkpoint                CAUGHT
    M-05 工厂拿到的不是 runner 自己的 client           CAUGHT
    M-06 未注册的类型被报成 succeeded                  CAUGHT
    mutants run: 6   CAUGHT 6   SURVIVED 0   INVALID 0

跑前跑后 `git status --porcelain` 均为 0 行（变异体自行还原）。

## 覆盖边界（未覆盖的逐条写明）

1. **真实前端 bundle 未被端到端驱动**（`.generated/frontend` 快照早于 T-08 的 `init.js` 改动）。
   Vue 层（`bindTrustedLocalAgent`/`cloudBaseUrl`）只有 `npm test` 的单元与变异证据。
2. **只有 macOS**。Windows/Linux 的 IPC 与 CSP 渲染不同，本矩阵不可外推。
3. **BitBrowser 相关链路依赖当时的真实账号状态**：本次四条链路全部可用（AC-06 的 16 项），
   但 `account-check`/`cookie-read` 依赖的 bilibili 登录态会随时间变化；
   重跑时若某条不可用，应按实际覆盖缩小结论，不以「测试通过」替代真实副作用证据。
4. **`profile-create/update/delete` 未驱动**（会改动用户真实 profile 清单，本 CHG 无此授权）；
   **`bind` 不发 Cloud 往返**（handler 只铸本地 session token），故「绑定到 Cloud」这一步
   不在本矩阵内。
5. **T-07 遗留③`connect_timeout` 不闭合**：`reqwest` 默认读 macOS 系统代理，
   回环请求被代理接管，connect 阶段无法隔离量测。机制与实测见
   `evidence/task-09-desktop-launch.md` §Findings 3。
6. **两处待用户裁定的产品决定**（只登记未改）：生产 CSP 是否加 `ipc:`；回环 client 是否加 `.no_proxy()`。
7. Cloud 侧：AC-10 的隔离实例只跑 `noop_task`；Cloud 仓的 Go 测试不在本 CHG 的验收面内。

## Follow-Up

- 工具与驱动的落点：`evidence/tools/`（不扩 CHG 声明范围，不动任何受版本管理的产品文件）。
- 隔离 Cloud（:18199）与 scratch schema 的收尾见 `change.md` §12 的清理清单。
