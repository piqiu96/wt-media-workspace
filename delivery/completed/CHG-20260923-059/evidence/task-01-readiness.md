# T-01 证据 — 就绪闸门

日期：2026-09-25 ｜ 仓：`wt-media-desktop`（实现）、`wt-media-agent`（契约用例）

## 1. 交付了什么

`sidecar/readiness.rs`（新）+ `sidecar/mod.rs` 注册 + `commands/agent.rs` 接线 + Agent 侧
`tests/test_sidecar_entry.py::ReadinessLineTests`。

两段式闸门（§6 D-01）：

1. **宣告**：解析 Agent 在 `bind`+`listen` 之后、`serve_forever()` 之前打印的那行，
   并**核对它报的端口与将要调用的端口**；
2. **应答**：请求 `/healthz` 并要求 2xx。

`sidecar.start_timeout_ms` 由死配置变成这道闸门的截止时间（§4.1 实测它此前无消费者）。

## 2. 实测推翻了草案的一条，并因此改了设计

**`/healthz` 在鉴权之后**（`local_api/server.py:448` 先 `_check_auth()`，`:451` 才分发 `/healthz`），
所以令牌不一致时它**答 401 而不是 200**。这使第二段闸门可以顺带覆盖
`sidecar/mod.rs:30-37` 那段注释担心的漂移（「被告知 A 令牌、被用 B 令牌质问」），
而该漂移**没有任何构建期检查**。于是闸门把应答分三态：

| 读数 | 判定 | 依据 |
|---|---|---|
| 2xx | 就绪 | 套接字在听**且**它认这份凭据 |
| **401** | **致命，立即失败，不等截止时间** | 等待改不了一份凭据；当作「就绪」会启动一个后续每个调用都 401 的应用 |
| 连不上 | 继续等到截止时间 | 可能只是还没起来 |

**若不做这一步，401 会被当成「就绪」**——这正是「实测推翻预想」而非锦上添花的地方。

## 3. 读数

### 3.1 单测（两侧，计数只增不减）

| 仓 | 起点 | 现在 | 差 |
|---|---|---|---|
| `wt-media-desktop` | 336 passed / 0 failed / 2 ignored | **344 passed / 0 failed / 3 ignored** | +8 passed、+1 ignored（真机臂） |
| `wt-media-agent` | 377 tests OK | **378 tests OK** | +1 |

desktop 编译警告：**基线 7 条 → 现在 7 条**，即**新增 0 条**。基线是**测量**出来的，不是推的：
把三个文件还原成 HEAD 版（其余 10 个既有脏文件保持不动）单独跑一次 `cargo check --tests`，
读到 `generated 7 warnings`；带本次改动再跑，同一条 7。7 条逐条点名且都在本次未触碰的文件里
（`FileSystemBridge`/`SecureStore`/`SystemBridge`/`Updater` 四个空壳与 `rolling.rs` 的两项）。

新增的 `--ignored` 那条与既有两条同类（`commands::reveal::…reveal_opens…`、
`commands::diagnostic::probe::probe_real_machine`），都是「需要真机/兄弟仓」的臂。

### 3.2 变异表：8/8 被各自的用例打掉

每条界至少一次实现变异，并指名它必须打掉的那个用例（脚本 `/tmp/chg059/mutate.py`、
`/tmp/chg059/mutate_agent.py`）：

| # | 变异 | 被打掉的用例 |
|---|---|---|
| M1 | 就绪行前缀改一个词（`on`→`at`） | `the_announcement_is_recognised_and_its_port_read` |
| M2 | 去掉端口一致性判定 | `an_announcement_on_another_port_fails_at_once` |
| M3 | 不看状态码（401 也算就绪） | `a_refused_credential_fails_at_once_and_names_itself` |
| M4 | 只在进闸门前读一次缓冲 | `an_announcement_that_arrives_late_is_still_seen` |
| M5 | 超时用常量而不是配置 | `the_wait_is_the_configured_one` |
| M6 | 到点返回 `Ok` 而不是 `Err` | `an_agent_that_never_announces_times_out` |
| A1 | Agent 侧就绪行改一个词 | `test_the_readiness_line_is_printed_only_after_the_socket_accepts` |
| A2 | 把 Agent 的打印**挪到建服务器之前** | 同上 |

**A2 是这条用例真正的价值**：它测的不是格式而是**顺序**——在那一行出现的**当刻**去
`connect` 那个地址。格式钉死一条打印在 `listen()` 之前的行同样会通过，而 Desktop 的第一段
信号就整个建在一句没有含义的话上。

**两次「验证工具本身出错」已记录，两者都会把红读成绿：**

1. 第一版脚本把「写变异」放在读「变异前」之前，6 条全部报「变异前已红」；
2. 修好顺序后 A1 仍报「没打掉」。根因是 **`python3` 的字节码缓存**：`on`→`at` 长度不变，
   而 `.pyc` 里的源文件 mtime 精度是**整秒**，同一秒内写入的变异被**上一轮的缓存**服务了。
   改用 `-B` + 空的私有 `pycache_prefix` 后转红。
   这条对「就地改一个字符再跑一遍」的验证方式是通用的，值得记住。

### 3.3 真机臂：**真的 Rust 闸门**对**真的 Agent 进程**

`sidecar::readiness::tests::the_gate_waits_for_a_real_agent_process`（`#[ignore]`）：

```
cargo test --manifest-path src-tauri/Cargo.toml -- --ignored real_agent
→ test result: ok. 1 passed; 0 failed
```

它跑的是 `../wt-media-agent` 的真实检出、真实的 `python3 -m wt_media_agent.local_api.server`、
真实套接字，stdout 按 `drain::follow` 的同一方式灌进 `SidecarLog`，再交给**本 crate 出货的那个
`gate`**。没有替身。

**这条通过得太快（0.17s），所以做了阳性对照**：把期望值故意写错成 `…:1`，它红了并报出真实读到的那行——
`left: "wt-media-agent local API listening on 127.0.0.1:54606"`。**这才算证明它真的起了进程并读到了真机那一行**，
而不是「没选中任何用例也算成功」。

另外两条独立读数（原始转录在 `agent-probe.out` / `agent-probe-phases.out`）：

- **同一句话出现两次，只有一句能认**：logger 那句带时间戳前缀
  （`2026-09-25T08:59:53 [INFO] …`）**不匹配** `ANNOUNCEMENT`，raw `print` 那句匹配。
  这正是要的：Desktop 认的是「原始 stdout 宣告」，不是日志格式。
- **401 那一臂是真的**：带对令牌 `HTTP 200 {"status":"ok",…}`；带错令牌 `HTTP 401 {"error":"unauthorized"}`。
- 看到那一行之后立刻 `connect`：连续两次成功。

端口 18771 与本臂随机端口均为**临时端口**；开发机自己的 8765 / 18080 / 54345 全程未占用
（`54345` 是用户的 BitBrowser，不碰）。

## 4. 未覆盖项（登记，不静默吸收）

1. **接线那一行没有自动化用例**：`commands/agent.rs::start` 里调用 `gate` 的那一段需要 `AppHandle`，
   而**本 CHG 环境下前端不启动**（窗口空白，CHG-056/058 已登记的既有事实），所以 `local_agent_start`
   这条命令**没有可达路径**——既不是测试遗漏，也不是本轮新增的限制。
   可得的最近证据是 3.3：闸门自身对真进程跑通；**未覆盖的是「命令确实会调它、以及调用后的
   失败分支（报错→停子进程→关会话）」**。
2. **宣告行报的是「请求的端口」而非「实际绑定的端口」**（`server.py:627` 打印 `port` 形参）。
   生产路径两者恒等（Desktop 传 `agent.port`，已校验 ≥1024），故 `port=0` 才会分叉，而无人这样用。
   已写进 Agent 侧用例的类文档，**故意不改**：Desktop 要比的就是请求端口。
3. **超过 `drain::CAPACITY`(200) 行才就绪的 Agent 会被读成「从未宣告」**——已写进模块头。
4. **Windows / x86_64** 未测（§5 明示不做）。
5. **前端等待语义的变化**：`local_agent_start` 从「spawn 完就返回」变成「就绪才返回」，
   最长等 `start_timeout_ms`。这对调用方是 await 一个 Promise，前端无需改；但**本轮没有真机走查过前端**，
   与第 1 条同源。
