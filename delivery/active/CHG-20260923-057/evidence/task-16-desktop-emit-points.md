# 证据 — T-16 三个既有 emit 点改道 + 生命周期补点

范围：计划本条——①`drain::report_exit` 由 `eprintln!` 改走 `agent.supervisor` 记录（**恰一条**，
按裁定五**保留末 20 行尾**）；②`drain` 的 `CommandEvent::Error` 分支补一条记录（否则进程未退出时的
读失败永不为人所见）；③`commands/logging.rs` → `commands/webview.rs` 纯重命名（**已单独一个 commit
`5eb7d0c`**）后两处 `println!` 改走 `webview` 记录；④Agent 启停与健康检查的**生命周期补点**
（`agent.supervisor`，今天一处都不记），health 响应体只在 DEBUG 记（裁定四）、**失败记录不带尾行**。

提交边界：`wt-media-desktop`（`src-tauri/src/sidecar/drain.rs`、`commands/{agent,webview}.rs`、
`logging/{backend,mod,test_support}.rs`），**2 个 commit**（①纯重命名 = `5eb7d0c`；②本文件描述的改道）。

---

## 1. 交付形态

| 处 | 内容 |
|---|---|
| `drain::Heard` / `classify` / `heard` | `CommandEvent` 是 `#[non_exhaustive]`，测试**构造不出**它 ⇒ 把「一行是什么」压成三臂（`Line`/`Failure`/`Exited`）的纯函数，`follow` 里只剩收流与三臂 match |
| `heard(Line)` | `push` + `false`：**缓冲且不记**（D-07 / AC-09 收窄后的口径） |
| `heard(Failure)` | 缓冲 + `warn!` 一条：读失败是**Desktop 的问题**，进程可能还活着，只缓冲则永不为人所见 |
| `heard(Exited)` | `report_exit` ⇒ `info!` 一条，**含末 20 行尾**（裁定五）；`single_line` 把整份报告转义成一行 |
| `commands/webview.rs` | `println!("[WEBVIEW] …")` → `tracing::error!(target: "webview", …)`；stack 那条加 `[stack] ` 前缀（原来靠 `[WEBVIEW-STACK]` 区分）；空 stack 不产生记录 |
| `commands/agent.rs` 的记录函数 | `started` / `already_running` / `stopped` / `not_running` / `healthy`（DEBUG）/ `failed`，各一条记录 |
| `commands/agent.rs` 的体拆分 | `health` / `start` / `stop` 三个自由函数；命令只剩实参解包。**理由与 T-15 的 `plan`/`install` 同一形态**：命令体吃 `State`，测试造不出来，内联的 `tracing!` 只有真机够得着（本节 §3 实测：本环境的真机**也够不着**，见 §4.1） |
| `failed` 的两个文本 | 记录 = 原因；返回给前端的 = 原因 + `drain::summary`（尾行）。前端看到的字符串**与改动前逐字相同**（`test` 里钉着），新增的只有记录 |
| `logging/test_support.rs`（新） | 三个模块（`backend`、`drain`、`commands`）都要「写文件 → 读回」的同一套四件套（scratch 目录 / options / 固定时钟 / `written`）；四份副本就是四种「记录到了没有」的答案。新增 `capture_at`，把「按生产级别跑一遍」变成可写的臂（裁定四的 DEBUG 边界靠它才验得了） |

## 2. 先红：三个**旧形态**必须打掉自己的用例

新用例与实现同批写入，所以「先红」由**回退到改动前的形态**来证（`/tmp/t16_mutate.py` 的 R1–R3）：

| # | 回退成 | 结果 |
|---|---|---|
| R1 | `report_exit` 用 `eprintln!`（T-16 之前的写法） | **KILLED**：`sidecar::drain::tests::the_exit_is_one_record_carrying_the_tail` |
| R2 | `heard(Line)` 里补一条 `info!`（把 Agent 输出记成 Desktop 记录） | **KILLED**：`ordinary_output_reaches_the_buffer_and_no_record`、`the_exit_is_one_record_carrying_the_tail` |
| R3 | `heard(Failure)` 去掉 `warn!` | **KILLED**：`a_read_failure_is_buffered_and_logged` |

R1 的对照在用例内部：同一用例断言「缓冲 50 行、报告含 `l30..l49`、不含 `l29`」，所以「零条记录」
不可能来自一个什么都没收到的 drain。

## 3. 变异表（10 个，控制行先绿）

控制行：`cargo test --workspace` 绿（166 passed）后逐个施加，每次只改一处、跑完即还原。

| # | 变异 | 打掉的用例 |
|---|---|---|
| M1 | 退出记录不带尾行（改成 `Local Agent（{path}）已退出`） | `the_exit_is_one_record_carrying_the_tail` |
| M2 | `failed` 把尾行也写进记录 | `a_failure_keeps_the_tail_out_of_the_record`、`an_unreachable_agent_keeps_the_tail_out_of_the_record` |
| M3 | 「已在运行」的记录用「未在运行」的文案 | `the_lifecycle_records_are_desktops_own_and_survive_production` |
| M4 | 「已启动」降到 DEBUG（生产看不见） | 同上 |
| M5 | JS 报错的 target 拼成 `webviews` | `the_stack_and_the_message_are_two_records_under_this_target`、`an_empty_stack_is_not_a_record` |
| M6 | 空 stack 也发一条 | `an_empty_stack_is_not_a_record` |
| M7 | `capture_at` 无视传入的级别（恒用开发态） | `the_health_body_is_development_only` |
| M8 | `health` 成功路径不发 `healthy` | `a_health_answer_is_returned_and_recorded` |
| M9 | `stop` 的 `None` 分支不发 `not_running` | `a_stop_with_nothing_running_is_recorded` |
| M10 | `health` 的连接失败路径不经 `failed`（只返回不记录） | `an_unreachable_agent_keeps_the_tail_out_of_the_record` |

全部 KILLED，且**打掉的是自己的用例**（M2/M5 各打掉两处同一族的用例，符合预期）。
M4 与 M7 是**成对**的：M4 只让「生产看不见」这一臂红，M7 只让「开发看得见」这一臂红——
任一条单独存在都不足以证明 DEBUG 边界，这也是 `capture_at` 存在的理由。

## 4. 真机臂：**探针页**逼出的完整一轮

### 4.1 先说结论：本环境的 debug 二进制**不加载 dist**，窗口是白的

计划原本假设「真实启动 → 前端会调 `local_agent_start`」。实测**不成立**：debug 构建的窗口
**整页空白**，连静态 HTML 都不渲染，日志里一条命令记录都没有。根因**不是**产品缺陷：

```
target/debug/build/wt-media-desktop-shell-*/output:  cargo:rustc-cfg=dev
src-tauri/tauri.conf.json:  "devUrl": "http://127.0.0.1:5174"
```

`cargo build`（debug profile）带 `cfg(dev)` ⇒ 窗口加载 **`devUrl`**（Vite 开发服务器），
**不是** `frontendDist`。开发机没跑 `npm run dev:desktop`，于是白屏。T-15 的三臂只断言 Rust 侧
的记录，未受影响；但「真机跑到命令层」这一条按原样**做不到**——除非把探针页喂给 devUrl。

做法（**全部是临时脚手架，事后逐项还原，见 §4.4**）：把一页只调 `__TAURI_INTERNALS__.invoke`
的 HTML 用 `python3 -m http.server` 挂在 `127.0.0.1:5174`（该端口当场核查为空闲），
再真实启动 desktop 二进制。页面上逐条打印返回值，截图存档；同一时刻 `desktop.log` 里是本 Task 的记录。

### 4.2 臂 B（无 stub）：真实 sidecar + 真实退出

探针依次 `local_agent_start` / `local_agent_health` / `local_agent_status` / `local_agent_stop`：

```
local_agent_start => "sidecar_started"
local_agent_health !! agent unreachable: error sending request for url (http://127.0.0.1:18766/healthz)

Local Agent 最近输出:
[PYI-6683:ERROR] Failed to load Python shared library '/var/folders/…/libpython3.14.dylib': dlopen(…)
local_agent_status  !! agent unreachable: error sending request for url (http://127.0.0.1:18766/api/v1/status)
local_agent_stop => "stopped"
```

同一轮的 `desktop.log`（**逐字，长行按记录原样**）：

```
10:22:17Z [INFO] desktop.startup: 配置来自环境变量指定的文件；日志目录 …/.local/logs；级别 DEBUG（配置 auto）；环境 production（构建 development）
10:22:18Z [INFO] agent.supervisor: Local Agent 已启动（sidecar_started）
10:22:19Z [INFO] agent.supervisor: [wt-media-desktop] Local Agent（sidecar_started）退出码 255；缓冲共 1 行，末 1 行输出：\n[wt-media-desktop] | [PYI-6683:ERROR] Failed to load Python shared library …
10:22:20Z [WARN] agent.supervisor: agent unreachable: error sending request for url (http://127.0.0.1:18766/healthz)
10:22:20Z [INFO] agent.supervisor: Local Agent 已停止
```

一屏之内同时成立四件事：

1. **裁定五的尾行只出现一次**：`[PYI-6683:ERROR] …` 在整份日志里**只**出现在那条退出记录里
   （`desktop.log` 的每一行都以时间戳开头 ⇒ 数记录就是数行，退出记录是**一行**，尾行被
   `single_line` 转义成 `\n`）。
2. **同一次失败的两种文本**：前端拿到的那条**带** `Local Agent 最近输出:` 与 PYI 行，
   日志里那条 `agent unreachable: …` **不带**——这就是裁定五/裁定六要求的分工，在真实进程里对照成立。
3. **AC-09 收窄后的口径成立**：sidecar 打印的 1 行**没有**变成一条记录（该 target 下没有以它开头的记录），
   **对照**是它确实到了 drain（就在退出报告的尾行里）。分母是 1 行，不是 50 —— 见 §5。
4. 退出记录了真实退出：这条臂是**退出码 255**（sidecar 自己死的），臂 C 是**被信号 9 终止**
   （Desktop 的 `kill` 先到），两种状态拼写都出自真实进程。

### 4.3 臂 C（stub 占住 scratch 端口）：一次跑齐五个生命周期分支

探针改为 start → **start（第二次）** → health → stop → **stop（第二次）**；另外用一个只答
`{"status":"ok","agent_id":"stub"}` 的 stub 占住 `127.0.0.1:18766`（scratch 端口，非 8765）：

```
local_agent_start => "sidecar_started"
local_agent_start => "already_running"
local_agent_health => "{\"status\":\"ok\",\"agent_id\":\"stub\"}"
local_agent_stop => "stopped"
local_agent_stop => "not_running"
```

```
10:22:59Z [INFO] desktop.startup: …
10:22:59Z [INFO] agent.supervisor: Local Agent 已启动（sidecar_started）
10:23:00Z [INFO] agent.supervisor: Local Agent 已在运行，忽略本次启动请求
10:23:00Z [DEBUG] agent.supervisor: 健康检查成功：{"status":"ok","agent_id":"stub"}
10:23:00Z [INFO] agent.supervisor: Local Agent 已停止
10:23:00Z [INFO] agent.supervisor: Local Agent 未在运行，忽略本次停止请求
10:23:00Z [INFO] agent.supervisor: [wt-media-desktop] Local Agent（sidecar_started）被信号 9 终止；缓冲共 1 行，末 1 行输出：…
```

⇒ 五个生命周期记录**各自的调用点**都在真实进程里跑到过，且与前端收到的返回值逐条对应。
`健康检查成功` 是 **DEBUG**（`级别 DEBUG（配置 auto）` 那一行说明本次是开发态），
生产态的对应臂在单测里（M4/M7 成对）。

### 4.4 脚手架与还原（逐项核对）

| 干预 | 还原 | 核对 |
|---|---|---|
| `.generated/frontend/index.html` 换成探针页 | `cp` 回原文件 | `shasum -a 256` 与备份**逐字相同**：`e568216d644dd34ee5f9df583de3dd4f0ba1e144dc12338e22fea460416e8f94` |
| `127.0.0.1:5174` 上挂探针（`python3 -m http.server`） | 进程已结束 | `lsof -nP -iTCP:5174 -sTCP:LISTEN` 空 |
| `127.0.0.1:18766` 上挂 stub | 进程已结束 | 同上，空 |
| 5 次真实启动（每次 8–9 秒） | 全部 `kill -TERM` | `ps` 无 `wt-media-desktop-shell` / `wt-media-agent` 残留 |

**全程未碰** `:8765` / `:18080` / `:54345`（三个开发者端口），也未向仓库配置写入任何代理设置。
`.generated/` 是构建产物目录（工作区约定里明确跳过扫描），未进任何 commit。

## 5. 读数与未覆盖项（如实登记，不静默吸收）

**测试**：`cargo test --workspace` **153 → 166 passed**（+13 = drain 4 + webview 2 + agent 7；
agent 那 7 条 = 生命周期全表 1 + 记录文案与返回串 3 + 真实套接字上的命令体 3）。**只增不减**。

**警告**：`touch src-tauri/src/main.rs && cargo build` 条目级警告 **9**（T-15 后也是 9，**未增**）；
`cargo clippy --workspace --all-targets` **13**（T-15 后也是 13，**未增**）。13 条**逐条**列过，无一条落在
本 Task 新增的代码上：`rolling.rs` 5 条（T-14 之后成为 test-only，T-15 §4.1 已登记）、四个占位 struct 4 条、
`main.rs:45` 「items after a test module」、`account.rs` 2 条、`drain.rs:284` 一条既有 `assert_eq!(…, true)`。
**说明**：T-15 登记过的「93→4 / 97→10」期望**已作废**，以实测 9/13 为准（本轮再次确认：两个数字在
T-16 前后**相同**，即本 Task 没有引入新的条目级警告）。

未覆盖 / 需要下一个人知道的：

- **AC-09 的真机分母是 1 行，不是 50 行**。`50` 那个数字来自单测（`ordinary_output_reaches_the_buffer_and_no_record`
  造 50 行，且对照断言它们**确实在缓冲里**）。真机这边 sidecar 只来得及打印 1 行就死了，
  所以真机只证明「那 1 行没变成记录、且确实到了 drain」，**不**证明规模。结论按分母收窄。
- **`start` 的 spawn 失败分支（`failed` 那一次调用）在本地这棵树里够不着**：随应用提供的 sidecar
  **存在且能 spawn 成功**，只是运行期因 macOS Team ID 起不来（退出码 255 / 被 kill），
  因此「找不到 sidecar」与「python 回退也起不来」两条 `Err` 都到不了。
  要够着就得临时搬走一个构建产物——没做。**登记为未覆盖**（`failed` 本身的记录/返回分工由 M2、M10 与
  §4.2 的连接失败臂守着）。
- **探针页是替身，不是真前端**。它只证明「真实 IPC → 真实命令 → 真实记录」，不证明真前端的调用时序；
  真前端在本环境跑不起来的原因是 §4.1 的 `cfg(dev)`（开发机没起 Vite），与产品无关，**未修**（不属于本 CHG）。
- **`already_running` 在 sidecar 自己死掉之后仍会说「已在运行」**：托管状态里的 `CommandChild` 句柄
  不会因为进程退出而被清掉（臂 B 的 sidecar 自己退出了；若此时再点一次启动，记录会是「已在运行」而进程已不在）。
  **这是既有行为**，不是本 Task 引入的；本 Task 只是让它**第一次变得可听见**。留作 T-18 的 §7 候选条目，
  本轮不改（改它要动 `drain` 与 `AgentProcess` 之间的耦合，超出本 Task）。
- **`local_agent_status` 未加记录**：计划没要求，本轮也没加（探针里的两条 `status` 失败只出现在前端文本里）。
- **Windows 日志布局仍未取证**（T-11/T-12/T-13/T-14/T-15 同一登记）。
- **`cargo fmt` 口径**：新增的 `logging/test_support.rs` 整文件跑过 `rustfmt`；改动的四个既有文件
  **只手改**，没跑全文件格式化（本仓不是 rustfmt-clean 的，T-13 已量化）。

## 6. 复现命令

```bash
cd wt-media-desktop
cargo test --workspace                                   # 166 passed（起点 153）
python3 /tmp/t16_mutate.py                               # 13 个变异：3 个旧形态 + 10 个新形态，全部 KILLED
touch src-tauri/src/main.rs && cargo build 2>&1 | grep -cE '^warning: [a-z]'          # 9（未增）
cargo clippy --workspace --all-targets 2>&1 | grep -cE '^warning: [a-z]'              # 13（未增）

# 真机（探针页只是脚手架，跑完必须还原 index.html）：
cp src-tauri/../.generated/frontend/index.html /tmp/t16/index.html.bak
# 把探针页写进 .generated/frontend/index.html（内容见 §4.1 说明；页面调 __TAURI_INTERNALS__.invoke）
python3 -m http.server 5174 --bind 127.0.0.1 --directory /tmp/t16/probe &   # 该端口必须先确认空闲
rm -rf src-tauri/.local/logs
WT_MEDIA_DESKTOP_CONFIG=/tmp/t16/agent-scratch.toml target/debug/wt-media-desktop-shell
#   臂 C 另需：python3 /tmp/t16/stub_agent.py &   # 占住 127.0.0.1:18766（scratch，非 8765）
cat src-tauri/.local/logs/desktop-*.log
# 还原：cp /tmp/t16/index.html.bak .generated/frontend/index.html && shasum -a 256 校验
```
