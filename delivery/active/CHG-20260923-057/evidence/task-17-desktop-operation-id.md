# 证据 — T-17 Desktop 进程内会话 `operation_id`

范围：计划本条——Desktop **进程内**的一次 Agent 会话一个 `operation_id`（start 生成、stop 清除），
落在 `agent.supervisor` 的记录上，使同一次会话的启停与健康检查可被读成一组。
**不加新 target**（`OWNED_TARGETS` 恰 3，两个测试钉着）、**不发任何 Header**、**不进 sidecar 子进程环境**
（裁定九 / D-10：`operation_id` 本 CHG 不跨端）。Agent 侧对应的请求级 id 在 T-21，两侧**不共享** id：
来源不同（Desktop 一个会话一个、Agent 一个请求一个），本 CHG 也不做串联。

提交边界：`wt-media-desktop`（`src-tauri/src/state.rs`、`commands/agent.rs`、`http/local_agent.rs`、
`main.rs`），**1 个 commit** = `9051480`。

---

## 1. 交付形态

| 处 | 内容 |
|---|---|
| `state::OperationId` | `Arc<Mutex<Option<String>>>`，`generate()`（`Uuid::new_v4()`，复用已有 `uuid` 依赖）+ `set` / `clear` / `current`。放在 `AgentProcess` **旁边**：两者回答同一个问题（有没有一个会话在跑），不能互相矛盾 |
| `lifecycle!` 宏 | 两个 `tracing::event!` 分支（`Some` 带 `operation_id = %id` 字段 / `None` 不带）。**不能用 `Option` 字段**：tracing 会把它打印出来，会话外的记录就会写成 `operation_id=None`——那是对「这条记录属于哪个会话」的一个**错误回答**，而且会改掉今天已有的行形状 |
| 六个记录函数 | `started` / `already_running` / `stopped` / `healthy`(DEBUG) / `stop_failed`(WARN) / `failed`(WARN) 各接一个 `Option<&str>`。`not_running()` 硬编码 `None`：没有会话可停 |
| id 的**读取点** | `health` / `start` / `stop` 三个自由函数体内（T-16 已把命令体拆出来，命令只剩实参解包）⇒ 测试直接调它们 |
| `begin` / `ended` | 从 `start` / `stop` 里再拆一层：spawn 成功之后的**登记 + 记录**、kill 成功之后的**记录 + 清除**。理由与 T-16 拆命令体同形——这一段是可以在测试里跑的，不该藏在需要 `AppHandle` / `CommandChild` 才能进入的函数里 |
| 顺序 | `begin`：先 `set` 再记录（不写一条「已启动」而会话还没登记）；`ended`：先读、再记录、最后 `clear`（id 不得活过它标注的会话） |
| `main.rs` | `.manage(OperationId::default())`，紧跟 `AgentProcess` |
| 出站请求 | **逐字不变**：无 Header、无 query、不进环境（本次改动的三处「不该去的地方」都由测试钉住，见 §3） |

## 2. 先红：三个**旧形态**必须打掉自己的用例

新用例与实现同批写入，「先红」由**回退到改动前的形态**来证（`/tmp/t17_mutate.py` 的 R1–R3）：

| # | 回退成 | 结果 |
|---|---|---|
| R1 | 记录不带 `operation_id` 字段（T-16 的形态） | **KILLED**：`a_health_check_reports_the_session_it_was_asked_in`、`a_session_is_held_and_released_around_its_two_records`、`every_record_a_session_can_make_names_that_session` |
| R2 | `begin` 只记录、不登记会话 | **KILLED**：`a_session_is_held_and_released_around_its_two_records`（`held before the record is written` 那一断言） |
| R3 | `ended` 只记录、不清除会话 | **KILLED**：同上（`released once the stop is recorded`） |

R2 / R3 是**成对**的：只回退登记或只回退清除，另一个方向仍会绿——「一个会话一个 id」要求两头都对。

## 3. 变异表（5 个新形态 + 2 个真实幸存者，控制行先绿）

控制行：`cargo test --workspace` 绿（175 passed）后逐个施加，每次只改一处、跑完即还原。

| # | 变异 | 打掉的用例 |
|---|---|---|
| M1 | `health` 把 id 拼进 **query**（`/healthz?op=<id>`） | `the_session_id_never_reaches_the_request` |
| M2 | 客户端 `bearer()` 多加一个 **Header** | `the_session_id_never_reaches_the_request` |
| M3 | `environment()` 多推一个 **环境变量** | `sidecar::tests::the_agent_is_told_where_to_listen_and_what_to_demand`（`vars.len() == 3`，**既有**用例） |
| M4 | `generate()` 恒返回同一个常量 | `state::tests::each_session_gets_its_own_uuid` |
| M5 | 会话外的记录带一个占位 id（`operation_id="-"`） | `a_record_outside_a_session_has_no_id_field` |
| N1 | `start` 里的 `begin(...)` 换成只记录（会话永不登记） | **SURVIVED**——该调用点在 `AppHandle` 之下，单测进不去（见 §5） |
| N2 | `stop` 里的 `Ok(ended(...))` 换成 `Ok(label)`（成功 kill 既不清除也不记录） | **SURVIVED**——同上，该分支要真的 `CommandChild` |

M1/M2 是**两条不同的出逃路径**，同一条用例的两组断言分别打掉：请求行逐字（query 会出现在第一行）、
头名列表逐字（多出来的头名字会出现在列表里），外加「整份请求里不含该 id」一票否决。
M3 特意去动用**既有**用例而不是新写一条：环境变量契约本来就有一条 `vars.len() == 3` 在守。

**出站头集合的基准是测量出来的，不是推断的**：
`authorization` / `accept` / `host`——`host` 由 hyper 在 send 时添加（`Accept: */*` 由 reqwest 加），
`RequestBuilder::build()` **看不到 host**。所以断言打在**桩套接字实际收到的字节**上（`recording()`），
而不是打在 `build()` 的头上；名单按收到的顺序逐字写死，谁改动它谁就得重测一次。

## 4. 真机臂：探针页跑出两个会话，登记与清除都在真实进程里成立

脚手架与 T-16 同一套（**debug 二进制带 `cfg(dev)`、加载 `devUrl` = `127.0.0.1:5174`**，本环境没有
Vite 开发服务器 ⇒ 窗口整页空白 ⇒ 真前端跑不到命令层；见 T-16 证据 §4.1）。探针页依次调
`local_agent_start` → `health` → `stop` → `health` → `start` → `stop`，另用一个只答
`{"status":"ok"}` 的 stub 占住 scratch 端口 `127.0.0.1:18767`（**不是 8765**）。

同一轮的 `desktop.log`（**逐字**；id 未缩写）：

```
10:34:52Z [INFO] desktop.startup: …级别 DEBUG（配置 auto）…
10:34:52Z [INFO] agent.supervisor: Local Agent 已启动（sidecar_started） operation_id=1190a95e-3a40-42a4-b6e0-fbb55df92a41
10:34:52Z [DEBUG] agent.supervisor: 健康检查成功：{"status":"ok","agent_id":"stub"} operation_id=1190a95e-3a40-42a4-b6e0-fbb55df92a41
10:34:52Z [INFO] agent.supervisor: Local Agent 已停止 operation_id=1190a95e-3a40-42a4-b6e0-fbb55df92a41
10:34:52Z [INFO] agent.supervisor: [wt-media-desktop] Local Agent（sidecar_started）被信号 9 终止；缓冲共 0 行，末 0 行输出：
10:34:52Z [DEBUG] agent.supervisor: 健康检查成功：{"status":"ok","agent_id":"stub"}
10:34:52Z [INFO] agent.supervisor: Local Agent 已启动（sidecar_started） operation_id=f386572a-8469-4553-85bb-137f08cdfca0
10:34:52Z [INFO] agent.supervisor: Local Agent 已停止 operation_id=f386572a-8469-4553-85bb-137f08cdfca0
10:34:52Z [INFO] agent.supervisor: [wt-media-desktop] Local Agent（sidecar_started）被信号 9 终止；缓冲共 0 行，末 0 行输出：
```

一屏之内成立四件事：

1. **一个会话一个 id**：会话 A 的三条（启动 / 健康 / 停止）同为 `1190a95e…`，会话 B 的两条同为
   `f386572a…`，两值不同 ⇒ **N1（登记）与 N2（清除 + 记录）在真实进程里都跑到了**：
   第四条（stop 之后的 health）**没有** `operation_id` 字段，只有 `ended` 的 `clear` 跑过才会如此。
2. **id 不出进程**：探针页打印的六条返回值是 `sidecar_started` / `{"status":"ok","agent_id":"stub"}` /
   `stopped` …（截图 `/tmp/t17/armB.png`），**没有一条含 id**；stub 收到的请求里也没有（单测 M1/M2 守着）。
3. **`stop` 之后立即再 `start` 得到新 id** ⇒ id 不跨会话复用。
4. **退出报告不带 id**（两条都没有）：它由 `drain` 在进程退出时写，那时会话可能已被 `stop` 清除——
   有意不加，见 §5。

### 4.1 脚手架与还原（逐项核对）

| 干预 | 还原 | 核对 |
|---|---|---|
| `.generated/frontend/index.html` 换成探针页 | `cp` 回原文件 | `shasum -a 256` 与备份**逐字相同**：`e568216d644dd34ee5f9df583de3dd4f0ba1e144dc12338e22fea460416e8f94` |
| `127.0.0.1:5174` 上挂探针（`python3 -m http.server`） | 进程已结束 | `lsof -nP -iTCP:5174 -sTCP:LISTEN` 空 |
| `127.0.0.1:18767` 上挂 stub | 进程已结束 | 同上，空 |
| 2 次真实启动 | 均 `kill -TERM` | `pgrep -fl 'wt-media-desktop-shell|wt-media-agent'` 空 |

**全程未碰** `:8765` / `:18080` / `:54345`（三个开发者端口），未向仓库配置写入任何代理设置；
`.generated/` 是构建产物目录，未进任何 commit。二进制在两次启动前核对过 mtime
（`18:34:15`，晚于最后一次源码改动 `18:33:39`）。

## 5. 读数与未覆盖项（如实登记，不静默吸收）

**测试**：`cargo test --workspace` **166 → 175 passed**（+9 = state 3 + commands/agent 5 +
http/local_agent 1）。**只增不减**。

**警告**：`touch src-tauri/src/main.rs && cargo build` 条目级警告 **9**（T-16 后也是 9，**未增**）；
`cargo clippy --workspace --all-targets` **13**（T-16 后也是 13，**未增**）。

**`rustfmt` 口径**：本仓**不是 rustfmt-clean 的**（T-13 已量化）。本 Task 新增/改动的行**无一处**
在 `rustfmt --check` 的差异清单里（`state.rs` 整文件 0 处差异）；途中把因我改动而变长的三行按 `rustfmt`
的写法顺手改掉，`commands/agent.rs` 的既有脏行因此 **9 → 8**。**未**对整文件跑格式化
（`rustfmt --check` 会连带报出别的 Task 的行，全文件重排不在本 Task）。

未覆盖 / 需要下一个人知道的：

- **N1 / N2 各是**一行调用点**（`start` 里的 `begin(...)`、`stop` 里的 `ended(...)`），单测进不去**
  （前者要 `AppHandle`、后者要真的 `CommandChild`）。二者**只由 §4 的真实启动臂覆盖**——会话 A
  的三条记录同 id、stop 之后的那条无字段，就是这两行跑过的证据。**没有**为它们写「等价于真机」的假替身。
- **退出报告（`drain::report_exit`）不带 id**，有意为之：它由 `drain` 在进程退出时发出，而那时
  `stop` 可能早已清除会话（被 kill 的情形更是如此）⇒ 同一个记录类型会「有时带、有时不带」，
  比一律不带更误导。要让它带上，得把会话传进 `drain` 并在退出时读——超出 D-10 之外的决定，本 CHG 不做。
- **`already_running` 带 id 的形态只在单测表里**（`every_record_a_session_can_make_names_that_session`）：
  真机臂的时序是「每次都先 stop 再 start」，槽位总是空的，所以真实进程里没走到这一支。
- **两侧的 id 不相关**：Desktop 这个 id 只标识「一次 Desktop 监督的会话」；Agent 侧的 T-21 id 标识一个
  请求。本 CHG **不**做跨端串联（D-10 不变）——两边的 id 在日志里各自成组，但**不能**互相对照。
- **Windows 日志布局仍未取证**（T-11…T-16 同一登记）。
- **探针页是替身**：它只证明「真实 IPC → 真实命令 → 真实记录」，不证明真前端的调用时序；
  真前端跑不起来的原因是 `cfg(dev)`/`devUrl`（环境事实，非产品缺陷），**未修**。

## 6. 复现命令

```bash
cd wt-media-desktop
cargo test --workspace                                   # 175 passed（起点 166）
python3 /tmp/t17_mutate.py                               # R1-R3 + M1-M5 全部 KILLED；N1/N2 如实 SURVIVED
touch src-tauri/src/main.rs && cargo build 2>&1 | grep -cE '^warning: [a-z]'          # 9（未增）
cargo clippy --workspace --all-targets 2>&1 | grep -cE '^warning: [a-z]'              # 13（未增）
rustfmt --edition 2021 --check --config skip_children=true src-tauri/src/state.rs     # 0 处差异
rustfmt --edition 2021 --check --config skip_children=true src-tauri/src/commands/agent.rs  # 8 处既有脏行

# 真机（探针页只是脚手架，跑完必须还原 index.html）：
cp .generated/frontend/index.html /tmp/t17/index.html.bak
cp /tmp/t17/probe/index.html .generated/frontend/index.html
python3 -m http.server 5174 --bind 127.0.0.1 --directory /tmp/t17/probe &   # 该端口必须先确认空闲
python3 /tmp/t17/stub_agent.py &                                           # 占住 127.0.0.1:18767（scratch）
rm -rf src-tauri/.local/logs
WT_MEDIA_DESKTOP_CONFIG=/tmp/t17/agent-scratch.toml target/debug/wt-media-desktop-shell
grep -o 'operation_id=[0-9a-f-]*' src-tauri/.local/logs/desktop-*.log | sort -u   # 两个 id
# 还原：cp /tmp/t17/index.html.bak .generated/frontend/index.html && shasum -a 256 校验
```
