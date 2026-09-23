# Evidence: Desktop 真实启动 —— AC-05、T-07 两处遗留、两向 CSP（T-09）

- CHG: `CHG-20260923-056`
- Task: `T-09`
- Date: 2026-09-24
- Type: manual + e2e（真二进制、真 WebView、真 Agent 进程、真配置）
- Status: PASS（四次真实启动全部通过；含 3 处登记发现、1 处 T-07 遗留未闭合）
- Tool: `evidence/tools/ac05_desktop_launch.py` + `evidence/tools/ac05_probe/`
- Run: `evidence/artifacts/ac05-run5.log`（原跑于 `/tmp/ac05-run5.log`；本记录引用的是**与当前工具文本一致**的那一次；run1–run4 为调试过程）

## Purpose

T-07 结束时登记了四处「`cargo test` 看不见」的遗留。其中三处**只有真实启动才能判**：

| # | 遗留 | 为什么单元测试看不见 |
|---|---|---|
| ① | 两条 spawn 路径都注入同一组四个变量 | `tauri_plugin_shell::Command` 需 `AppHandle`，`cargo test` 构造不出 |
| ② | `get_public_config` 真的注册进了 `generate_handler!` | 忘了注册的话编译通过、测试全绿，只有运行期以「命令不存在」暴露 |
| ④ | `.setup()` 晚于窗口创建，故 CSP 只能在 `Builder::run` 之前注入 | 注入点错了没有任何编译或测试信号，只有 WebView 里**策略没生效** |

加上 CHG 自己点名的两项：**AC-05**（页面拿到的 Cloud 地址来自 `get_public_config`，不是字面量）
与**两向 CSP 端到端检查**（故意写错的 `csp_connect_src` 必须产生前端违规，改对后不得再有）。

判据的设计原则：**每一处「没发生」都要有一个同批次、同形状的「发生了」作对照**，否则
「拒绝」与「这条链路本来就坏的」无法区分。

## Method

### 1. 探针页怎么进到真 WebView 里

Tauri 的 CSP **只管 Tauri 自己发出的资源**（`Manager::get_asset` → `protocol/tauri.rs:182`）。
从外部 `devUrl` 加载的页面**完全不受策略约束**——所以 `tauri dev` 测不了 CSP，这不是配置问题
而是机制如此。

办法（不碰任何受版本管理的文件）：`tauri-codegen` 在 `devUrl` 缺席时才嵌 `frontendDist`
（`tauri-codegen/src/context.rs:178`），且 `TAURI_CONFIG` 走 RFC 7386 合并（`null` 即删除键）。
故：

    TAURI_CONFIG={"build": {"devUrl": null, "frontendDist": "<probe dir>"}}  +  cargo build

得到一个**服务于任意页面、且带运行期 CSP** 的 debug 二进制。首次构建曾被误判为「没生效」，
判据是拿一个不存在的 `frontendDist` 去编（报 `proc macro panicked … this path doesn't exist`）
证明 `TAURI_CONFIG` 确实抵达 codegen；再用嵌入资源**键名**（`/index.html`、`/probe.js`）确认。
（先前看「字符串不在二进制里」是 brotli 压缩所致。）

探针页 `ac05_probe/index.html` **刻意没有内联脚本、也没有内联样式**：运行期策略无 nonce、无
预置哈希，内联脚本会被它要测量的那条策略本身挡掉。`probe.js` 通过产品自己的
`log_js_error` 上报，落在 Desktop 进程 stdout 的 `[WEBVIEW]` 行上。

### 2. 四次启动，四个问题（M1 是 M2/M3/M4 的对照）

| leg | `development.python_fallback` (file) | 环境变量门 | exe 旁 sidecar | `csp_connect_src` | 要回答的问题 |
|---|---|---|---|---|---|
| M1 | `true` | 未设 | 无 | `http://127.0.0.1:19998`（**故意写错**） | 错的 CSP 会不会**真的**拦？失败形态是什么？ |
| M2 | `false` | `1` | 无 | `http://127.0.0.1:18080`（对） | Python fallback 路径是否注入四个变量？ |
| M3 | `false` | `1` | **有** | 同上 | sidecar 路径是否注入**同一组**四个变量？ |
| M4 | `false` | `1` | 无 | `ipc: http://ipc.localhost http://127.0.0.1:18080` | `ipc://` 那三条拒绝是不是**只**由缺这个源引起？ |

每个 leg 一个独立 scratch 端口（`8765` 是开发者自己的 dev Agent，四次都没碰），
一个独立 scratch 数据目录，一份现写的 `desktop.toml`，独立进程组，退出后核对**零残留监听**。

### 3. 子进程的环境**从不读取**

T-07 的四个变量名就是 Agent 认的那四个，这是①的全部论点。最直接的读法是看子进程的环境，
但那次 `ps -wwE` 被自动模式分类器**正确地拒绝了**：它会把开发者的 Agent runtime token
物化进转写文本。拒绝被接受，**没有绕路**，改为行为取证——四项全部由**外部可见的行为**反推：

| 变量 | 行为判据 | 为什么这是充分证据 |
|---|---|---|
| `HOST`/`PORT` | 监听地址是 `127.0.0.1:<该 leg 配置的端口>` | 默认是 8765；端口来自每 leg 不同的配置文件，只有真读到了才会是这个值 |
| `DATA_DIR` | 该 scratch 目录下出现 `local-agent.sqlite3`/`logs`/`versions` | 目录由配置给，且仓库 `.local/` 未被触碰 |
| 运行时 token | 无 token **401**、**错** token **401**、Desktop 自己的 client **200** | 空 token 时 `_check_auth` 对一切放行；因此 401 是「非空 token 已抵达」的正向证明，而 200 证明 client 持有的是**那一个** |

D-04 的否定面（token 不得经 argv）另有取证：读子进程 argv，断言其中**没有** token 形状的
参数，并用一次**植入阳性对照**（`secret_checker_control()` 种下 `--token 9f2ac41d…`）证明这个
检查会失败——否则「没找到」可能只是匹配模式空转。

## Expected

- **M1**：`local_agent_start` 返回错误（文案含「未找到或无法启动」）；`127.0.0.1:19998` 的
  fetch 被拒且产生违规，违规的 `originalPolicy` 里出现**那个错地址**。
- **M2/M3**：`local_agent_start` 成功且标签分别为 `started` / `sidecar_started`；Agent 起来并
  被 Desktop 的 client 以 200 问到；四个变量全部生效（上表）。
- **全部四 leg**：`get_public_config` 返回**当次配置文件**的值，键集恰好三个；
  `localhost:18080` 的 fetch **处处被拒**（对照：任何配置都没同时允许两个名字）。
- **M4**：`ipc://` 拒绝数归零，其余不变。

## Actual

四次全部 PASS（`evidence/artifacts/ac05-run5.log`）。逐 leg 关键行：

```
M1 csp_connect_src = http://127.0.0.1:19998   (故意写错)
  get_public_config -> {'cloud_base_url': 'http://127.0.0.1:18080',
                        'local_agent_port': 63166, 'environment': 'development'}
  fetch http://127.0.0.1:18080/healthz -> rejected refusals=1
    policy: script-src 'self' 'sha256-6ggz…'; img-src 'self' https:;
            connect-src 'self' http://127.0.0.1:19998; default-src 'self';
            style-src 'self' 'unsafe-inline'
  local_agent_start -> ok=False error='未找到或无法启动随应用提供的 Local Agent。请重新安装完整的 WT Media 安装包。'
  after stop: nothing listening on 63166

M2 python fallback 路径
  fetch http://127.0.0.1:18080/healthz -> resolved refusals=0   (no violation)
  fetch http://localhost:18080/healthz  -> rejected refusals=1   (对照，四 leg 一致)
  local_agent_start  -> ok=True value='started'
  local_agent_health -> ok=True body='{"status":"ok","service":"wt-media-agent","mode":"m1"}'
  listener pid=23963 bound=127.0.0.1:63223
  child    ppid=23957 argv=python3 -m wt_media_agent.local_api.server   (无 token 形状参数)
  /healthz no token -> 401, wrong token -> 401, Desktop 自己的 client -> 200
  data dir ['local-agent.sqlite3', 'logs', 'versions']

M3 sidecar 路径（exe 旁 sidecar 就位）
  local_agent_start -> ok=True value='sidecar_started'
  listener pid=23972 bound=127.0.0.1:63244
  child    ppid=23967 argv=<venv python> -m wt_media_agent.sidecar_main
  /healthz no token -> 401, wrong token -> 401, Desktop 自己的 client -> 200

M4 csp_connect_src 加上 ipc:
  ipc:// refusals  0        (M1/M2/M3 均为 3)
  其余各项与 M2 相同
```

要点：

- **CSP 两向成立**：同一个 fetch，错地址→`rejected` + 违规且 `originalPolicy` 逐字含
  `http://127.0.0.1:19998`；对地址→`resolved` 且**零违规**。M4 证明 `ipc://` 的拒绝只由这一个
  缺失源引起。`localhost:18080` 在四 leg 全被拒 —— 策略是**按源**精确的，
  不是「大概放行了回环」。
- **生效策略是 Tauri 渲染后的**：`connect-src` 逐字来自配置文件，而 header 里多出的
  `script-src 'self' 'sha256-…'` 是 Tauri 为自己注入的引导脚本加的（`csp_policy()` 里没有这条）。
- **①两条路径闭合同一组四个变量**：M2 与 M3 的四处判据全部成立，且两 leg 的子进程
  `ppid` 都等于 Desktop 的 pid。
- **②`get_public_config` 确实注册**：四次启动它都被调用并返回，若漏注册只会以
  「命令不存在」出现。
- **④注入点正确**：策略之所以**在页面里生效**，正是因为它在 `Builder::run` 之前施加；
  探针页能被策略拦到，就是注入点唯一的运行期信号。
- **报告本身是回退路径的证据**：`log_js_error` 走的是被 CSP 拒掉的 `ipc://` 传输，而
  `[WEBVIEW]` 行仍然出现在 stdout —— 说明 Tauri 的 `postMessage` 回退真的在工作。

## Findings（实测，非推断）

### 1. `development.python_fallback` 是装饰键

M1（文件 `true`、环境变量未设）**失败**并给出「未找到或无法启动随应用提供的 Local Agent」；
M2（文件 `false`、环境变量 `1`）走了 Python 路径。真正的门是
`development_python_fallback_enabled()` = `cfg!(debug_assertions) && WT_MEDIA_DESKTOP_ALLOW_PYTHON_FALLBACK == "1"`
（`commands/agent.rs:64`、`main.rs:24-34`），grep 全仓无任何代码读 TOML 里那个键。
**登记，不在本 CHG 内改**：这是 T-07 自己写进 `resources/desktop.production.toml` 的键。

### 2. `connect-src` 不含 `ipc:`，Tauri 的**首选** IPC 传输每次启动都被拒

M1/M2/M3 各有 3 条 `ipc://localhost/<cmd>` 违规，M4 加上 `ipc: http://ipc.localhost` 后归零。
Tauri 的首选传输是 `fetch(ipc://localhost/<cmd>)`（`scripts/ipc-protocol.js:30-88`），失败一次后
本会话内改走 `window.ipc.postMessage`（macOS 上是 `webkit.messageHandlers`，CSP 不管）。

**这是既有事实，不是 T-07 引入的**：退役的 `tauri.conf.json` 字面量是
`default-src 'self'; connect-src 'self' http://127.0.0.1:18080; style-src 'self' 'unsafe-inline'; img-src 'self' https:`
（`git show 14ff67c^:src-tauri/tauri.conf.json`），T-07 逐字保留了这条策略。修法很小
（`csp_connect_src` 本就允许空格分隔多值，故**可只改配置**），但「生产策略要不要加 `ipc:`」
是产品决定，故**只登记**，不静默改。

### 3. `reqwest` 默认读 macOS 系统代理，本机 Agent 的 token 会经代理

这是 T-07 遗留③（`connect_timeout` 未单独验证）**查不下去的原因**，实测链条：

    TcpListener listen(1) 且永不受理，用连接塞满队列后 → 裸 connect 挂起（SYN 被丢，守卫断言）
    同一个地址，走 build_client() 造出的 client → 拿到 HTTP 502 + connection: close
    curl -x http://127.0.0.1:7897 <同地址>  → HTTP 502
    curl --noproxy '*' <同地址>            → exit 7 (连不上)
    scutil --proxy                         → HTTPEnable=1 / 127.0.0.1:7897，ExceptionsList 含 127.0.0.1
    hyper-util-0.1.20 matcher.rs mac 模块  → 只读 HTTPEnable/HTTPProxy/HTTPPort(+HTTPS)，不读 ExceptionsList

即：`reqwest` 的 `system-proxy` 是**默认特性**（`reqwest-0.12.28/Cargo.toml:105,180` →
`hyper-util/client-proxy-system`），macOS 上经 `system-configuration` 生效，**从不豁免回环**。
后果：任何在系统设置里开了代理的 macOS（本机就是），Desktop→本机 Agent 的请求会交给该代理，
而 `LocalAgentClient` 的每个请求都带 per-launch runtime token。本机因代理在回环上才「能用」；
若代理是**远端**的，Desktop 将完全够不到自己的 sidecar。

修法一行（回环 client 加 `.no_proxy()`），但「Cloud client 要不要保留系统代理」是产品决定
（开发者在公司代理后访问 Cloud 是合理诉求），故**只登记**。它同时挡住③的闭合路径：
`connect_timeout` 要隔离量测必须让 reqwest 不走代理，故本 CHG 内**不闭合③**，只把
「CI 不稳定」这个笼统说法换成**已定位的机制**。

## Coverage（枚举，未覆盖的写明未覆盖）

已覆盖：

| 项 | 判据 |
|---|---|
| AC-05 运行期 | `get_public_config` 返回**当次配置**的 `cloud_base_url` / `local_agent_port`；`environment=development`；键集恰好三个 |
| AC-05 静态面 | `grep -rn 18080 src/apps/desktop/` **0 命中**（分母 9 个 js/vue 文件；阳性对照 `get_public_config` 命中 `init.js`）；`127.0.0.1` 字面量同目录 0 命中 |
| T-07 ① | M2/M3 四变量行为判据；两 leg 的 `ppid` = Desktop pid |
| T-07 ② | 四次启动命令均可调用 |
| T-07 ④ | 策略在真 WebView 中生效（注入点在 `run` 之前） |
| 两向 CSP | 错地址 rejected+违规（`originalPolicy` 含该地址）/ 对地址 resolved+零违规 / `ipc:` 反事实 M4 / 按源精确（`localhost` 处处被拒） |
| 进程卫生 | 每 leg 退出后「零残留监听」；四次均未触碰 :8765 的开发者 Agent |
| 探针自证 | 违规事件先于 `PublicConfig` 上报；`postMessage` 回退使报告抵达 stdout |

**未覆盖（明确列出）**：

1. **真实前端 bundle 未被驱动**。探针页替换了真页面。且仓内快照 `.generated/frontend`
   （Sep 23 18:26）**早于** T-08 的 `init.js` 改动（`305d002`，Sep 24 00:34），跑它等于测旧代码，
   故不做。`bindTrustedLocalAgent()`/`cloudBaseUrl()`（`init.js:87`/`:41`，由
   `AgentStatusPage.vue:36` 消费）在**真 WebView 里**的行为因此**未有端到端证据**，
   只有 `npm test`（含 `localAgentBoundary.test.js` 与 T-07 的 5/5 变异矩阵）的单元证据。
2. **只测了 macOS**。Windows/Linux 的 IPC 传输与 CSP 渲染不同（Windows 走 `window.ipc.postMessage`，
   不存在 `ipc://` 这一条），本记录**不可外推**。
3. **`mode: "no-cors"`**：探针量的是「策略放行与否」（resolved/rejected + 违规事件），
   不量 HTTP 状态。Cloud 侧只做了 `GET /healthz` 只读。
4. **③`connect_timeout` 不闭合**（原因见 Findings 3）。
5. WebView 的控制台输出（devtools）未采集；页面侧的可见证据仅限 `[WEBVIEW]` 上报行。

## Follow-Up

1. 待用户裁定的两处产品决定（均只登记未改）：生产策略是否加 `ipc:`（可只改配置）；
   回环 client 是否加 `.no_proxy()`（涉及 Cloud client 是否保留系统代理）。
2. 本工具与被测仓均无耦合：探针页与驱动位于 `evidence/tools/`，构建用 `TAURI_CONFIG` 环境变量，
   **未改动任何受版本管理的文件**（`wt-media-desktop` 工作树在本记录落盘时为 clean）。
3. ④的 `bindTrustedLocalAgent()` 端到端空缺：若 T-10 后要补，最小路径是把 `.generated/frontend`
   按 T-08 后的源码重建一次，再以本工具同法启动真页面。
