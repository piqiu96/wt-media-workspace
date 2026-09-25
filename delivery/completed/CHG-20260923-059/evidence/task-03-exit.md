# T-03 证据 — 退出收尾（请停 → 宽限 → 强杀）

日期：2026-09-25 ｜ 仓：`wt-media-agent` + `wt-media-desktop`（两仓各一个 commit）

## 1. 交付了什么

**Agent 侧**（`70a1647`，`feat(chg-059): T-03 Agent 侧 SIGTERM 收尾与在飞请求等待`）
——让那个「请」不是慢一点的杀：

- `local_api/server.py::serve()` 安置 SIGTERM 处理器，把 `httpd.shutdown()` **派到自己的
  线程**上（信号只投递到主线程，而主线程正在 `serve_forever` 里，就地调用会死锁）。
- `httpd.daemon_threads = False`。这一行是承重的：`ThreadingHTTPServer` 默认 `True`，
  而 `socketserver._Threads.append` 是 `self.reap(); if thread.daemon: return`——守护线程
  **根本不登记**，于是 `server_close()` 的 `_threads.join()` 拼的是一张空表。
- `print("…stopped")` 挪到 `server_close()` 之后。它的位置就是它的价值。
- `serve()` 结束时还原被顶掉的那个处理器（处置是全进程的，`ReadinessLineTests` 正是就地
  调用 `serve` 的调用方）。

**Desktop 侧**（`242f61e`，`fix(chg-059): T-03 退出收尾——Desktop 侧先请停、再宽限、最后强杀`）：

- `main.rs` 挂 `RunEvent::Exit` → `commands::agent::stop_at_exit`（`tauri::async_runtime::block_on`）。
- `sidecar::ask(pid)` = `kill_process(pid, SIGTERM)`；`sidecar::alive(pid)` = `test_kill_process`，
  `Errno::PERM` 算「在」（有东西在，只是不归我）；`sidecar::force(child)` = `CommandChild::kill()`。
- `commands::agent::stop()`：请停 → 以 50ms 轮询 `alive` → 到 `stop_timeout_ms` 仍在就强杀。
- 新增 `[sidecar] stop_timeout_ms`（出货 5000；`validate()` 拒绝 0，只报键名）。
- 新增三条记录，`stopped` / `ended` 与返回值 `"stopped"` / `"not_running"` **原样不动**
  （那是前端匹配的标签）。

## 2. 缺陷的复现（「先红」读数）

缺陷不是「少了一个函数」，而是一个**行为**：修复前 `stop` 上来就 `kill()`，于是
「Agent 把在飞的任务做完、自己退的」与「被我们杀在半路上的」在 `desktop.log` 里是**同一行**
（都只有 `Local Agent 已停止`），事后读不出差别。

复现方式与 T-02 同法：**保留本次全部新用例**，把 `stop` 的函数体还原成它在 HEAD
（`f1d1fba`）的形状——也就是 `kill(process, session)`——再重跑。**这不是历史转录，是重跑。**

原始转录：`task-03-desktop-red.out`（该过滤器 `0 passed; 2 failed`）

```
2026-09-24T10:11:12 [INFO] agent.supervisor: Local Agent 已停止 operation_id=session-ignored
2026-09-24T10:11:12 [INFO] agent.supervisor: Local Agent 已停止 operation_id=session-answered

assertion `left == right` failed: a signal here would mean it was killed, whatever the records say
  left: (None, Some(9))      ← 「答」的那条：SIGKILL，trap 从未跑到
 right: (Some(0), None)

the window is not decoration: the kill came at 900.875µs   ← 「不答」的那条：窗口等于不存在
```

两个读数各自钉住一半：**日志**（两条 arm 不可区分）与**退出状态**（SIGKILL 也照样把槽位清空、
把会话关掉，所以「进程没了」并不能证明有人被请过）。修复后同两条转绿：
`task-03-desktop-green.out`（353 passed / 0 failed）。

## 3. 真机两条读数（本任务的判据）

`cargo test -- --ignored real_agent`：**Desktop 自己的停路对着 `../wt-media-agent` 的真进程跑**。
起法用的是生产那条路（`app.shell().command("python3")`，同一 crate、同一条 spawn 路径），
所以 pid、信号、`CommandChild` 全是真的。

原始转录：`task-03-desktop-real-agent.out`

```
已请 Local Agent（pid 71848）停止            operation_id=real-agent-answered
Local Agent 在宽限内自行退出（518 ms）        operation_id=real-agent-answered
Local Agent 已停止                          operation_id=real-agent-answered
已请 Local Agent（pid 71856）停止            operation_id=real-agent-killed
宽限已到，强杀 Local Agent（1 ms）            operation_id=real-agent-killed
Local Agent 已停止                          operation_id=real-agent-killed

test result: ok. 2 passed; 0 failed
```

两条 arm 各有一半佐证：

- 「答」的 arm 退出码 `Some(0)`——**Agent 自己走完了 `serve()` 的收尾路径**（这正是 §1 那半
  的读数），518 ms 与它自己 `serve_forever` 的 0.5s 轮询吻合。
- 「杀」的 arm `signal: Some(9)`——**只有 SIGKILL 能结束它**。这个窗口（1 ms）是**故意**短于
  Agent 那半秒轮询的：这样这一条读数由「截止时间到」决定，而不是两个时钟赛跑。

**稳定性**：连跑 5 次，5/5（见 §6 的说明：这条读数里唯一个真实存在的窗口是「信号早于
Agent 的 handler 装好」，它若发生会把读数变成 `(None, Some(15))`，不会假绿）。

## 4. 变异表

两条都带控制行（先用未变异的树确认那条用例是绿的）与守卫（空过滤器会报成功，读成「打掉了」）。

### 4.1 Agent 侧 5/5（`/tmp/chg059/mutate_t03_agent.py`）

转录：`task-03-agent-mutations.out`

| # | 变异 | 必须被打掉的用例 | 读数 |
|---|---|---|---|
| A1 | 不安置处理器（`_answer_sigterm` 不接线） | `test_a_sigterm_is_answered_with_the_ordinary_exit_path` | 打掉 ✓ |
| A2 | 去掉 `daemon_threads = False` | `test_a_request_in_flight_when_the_signal_arrives_is_waited_for` | 打掉 ✓ |
| A3 | 「stopped」那行挪到 join 之前 | 同上 | 打掉 ✓ |
| A4 | 不还原被顶掉的那个处理器 | `test_an_in_process_serve_restores_the_disposition_it_displaced` | 打掉 ✓ |
| A5 | 处理器里直接调 `shutdown()`（不起线程） | `test_a_sigterm_is_answered_with_the_ordinary_exit_path` | 打掉 ✓ |

A2 是这张表里最该有的一条：它是**唯一**能证明 `daemon_threads = False` 不是装饰的读数——
把这一行去掉，「close 会等在飞请求」看上去仍然成立（`block_on_close` 为 True、join 也真的调了）。

### 4.2 Desktop 侧 9/9（`/tmp/chg059/mutate_t03_desktop.py`）

转录：`task-03-desktop-mutations.out`

| # | 变异 | 必须被打掉的用例 | 读数 |
|---|---|---|---|
| D1 | 不写「已请…停止」那条记录 | `a_stop_the_agent_answers_reads_as_it_leaving_on_its_own` | 打掉 ✓ |
| D2 | 不写「宽限内自行退出」那条记录 | 同上 | 打掉 ✓ |
| D3 | 不写「宽限已到，强杀」那条记录 | `a_stop_the_agent_ignores_reads_as_killed_at_the_deadline` | 打掉 ✓ |
| D4 | 窗口当零（截止时间不加上宽限） | 同上 | 打掉 ✓ |
| D5 | 一次信号都不发（`ask` 变空操作） | `a_stop_the_agent_answers_…` | 打掉 ✓ |
| D6 | `Signal::TERM` 换成 `Signal::KILL` | `an_ask_reaches_a_real_process_and_it_leaves` | 打掉 ✓ |
| D7 | `alive` 永远说「有东西在」 | 同上 | 打掉 ✓ |
| D8 | `alive` 永远说「没东西」 | `a_process_that_ignores_the_ask_is_still_alive` | 打掉 ✓ |
| D9 | 进程号解析失败时当成「有东西在」 | `a_pid_of_zero_is_refused_rather_than_signalled` | 打掉 ✓ |

D5 是承重的那条：`ask` 变成空操作时另外两个信号仍在跑、槽位照样清空、会话照样关闭——
只有「退出状态」与「那条记录」两件一起断言才看得见它。

## 5. 设计裁定与两处订正

1. **为什么是「先请后杀」而不是「直接杀」**：直接杀会**丢掉在飞的任务**。Agent 侧的
   in-flight 请求是要落库的（检查点、待回传结果），杀在半路上留下的是一份没人知道自己
   没写完的状态。宽限窗口就是给这些请求收尾用的。
2. **`alive` 用 `test_kill_process` 而不是「试发一次信号」**：`kill(pid, 0)` 不发信号、
   只看进程在不在，`Errno::PERM` 是「在，但不归我」——也算在。**`Pid::from_raw(0)` 返回
   `None` 不是形式**，`kill(0, sig)` 的语义是「我整个进程组」，所以 0 必须被拒
   （逐条用例：`a_pid_of_zero_is_refused_rather_than_signalled`）。
3. **`stop` 先 `take()` 再判**：句柄取走之后槽位就是空的，所以「停的时候正好有人来 start」
   不会拿到一个正在被杀的句柄。
4. **订正一**：`rustix` 的 `process` **不在**它的默认 feature 里（`default = ["std"]`）。
   上一轮的记录里写反了，已在 `Cargo.toml` 显式请求并写明理由。
5. **订正二**：`sidecar.stop_timeout_ms` 补进 `validate()`（0 拒绝，只报键名，不回显值），
   与既有的 `start_timeout_ms` 同一条规则、同一个循环。
6. **提交范围内不含 rustfmt 变动**（同 T-01/T-02 的做法）：`commands/agent.rs`、
   `sidecar/mod.rs`、`dto/config.rs` 带着未提交的 rustfmt 重排，本次用**三路合并**
   （HEAD / `rustfmt(HEAD)` / 工作区）把重排反推掉后再提交。判据两条，都要报：
   - `rustfmt(候选) == rustfmt(工作区)`——候选与工作区是同一个程序的两种排版；
   - 候选内容跑出 `353 passed; 0 failed`（与工作区同数）。

   重排随后原样放回工作区，13 个带重排的文件逐个复核为 `工作区 == rustfmt(HEAD)`（13/13）。

## 6. 读数

| 项 | T-02 结束时 | 现在 | 差 |
|---|---|---|---|
| desktop `cargo test` | 348 passed / 0 failed / 3 ignored | **353 passed / 0 failed / 4 ignored** | +5 passed，+1 ignored |
| agent `bash scripts/test.sh` | 378 OK | **382 OK** | +4 |
| desktop 编译警告 | 7 | **7** | +0 |

新增的 6 条：desktop 2 条（shell trap 两条 arm）、agent 4 条，再加 1 条 `#[ignore]` 的真机臂。
超出 5 的 1 条就是那条真机臂，默认不跑。

## 7. 未覆盖项与已知极限（登记，不静默吸收）

1. **随包 sidecar（PyInstaller onefile）这一臂未做，且在本机做不到。**
   转录：`task-03-sidecar-bootloader-untested.out`。那个二进制在本机**根本起不来**：
   onefile 引导器解出 `libpython3.14.dylib` 后 macOS 拒绝 `dlopen`——
   `code signature … not valid for use in process: mapping process and mapped file (non-platform)
   have different Team IDs`（产物是 `flags=0x10002(adhoc,runtime)`）。
   后果有两条，都不许用文字糊过去：
   - 「**引导器是否把 SIGTERM 转发给真正在服务的那进程**」**仍未测**。Desktop 请的是
     `CommandChild::pid()` 报的那个 pid，而在随包形态下那是**引导器**的 pid。
   - 那个产物在本机跑不起来这件事本身，是打包/签名口径的实缺陷（`ad-hoc` 签名 +
     hardened runtime 的组合），登记给 **T-05/T-06 与 AC-09** 处理，本任务不越界去改。
2. **「信号早于 handler 装好」这个窗口真实存在**，在真机臂里也在：Agent 的宣告行打在
   `_answer_sigterm()` **之前**（相隔几条语句）。若某次调度真的抢在前面，读数会是
   `(None, Some(15))`，用例会红——**这是有意的**：它把「handler 没赶上」与「代码错了」
   分开报，而不是让一条含糊的断言吞掉。连跑 5 次未复现（5/5）。
3. **`RunEvent::Exit` 这个钩子本身只有阅读级覆盖，没有用例。** `stop_at_exit` 需要
   真 `AppHandle` 走一次真正的退出，套件里够不着；本任务能证的是它里面调的 `stop()`
   （已被 §3/§4 覆盖），证不了「Tauri 一定会在退出时调它」。
4. **宽限内 pid 被复用**：`alive` 判的是「这个 pid 上有没有东西」，`force` 用的是句柄。
   若 Agent 在窗口内退出而 pid 被系统立刻分给别的进程，`alive` 会一直为真，于是走强杀——
   而 `force` 用的是**句柄**，`CommandChild::kill()` 对已结束的子进程会失败，被记成
   `stop_failed`。**这是一条真实但极窄的极限**：需要「Agent 恰好死在窗口内」+
   「pid 恰好在窗口内被复用」同时发生。登记而不修。
5. **僵尸进程与「在不在」**：`kill(pid, 0)` 对僵尸仍返回成功，所以 `alive` 在子进程被
   回收之前一直说「在」。生产里回收由 `tauri-plugin-shell` 自己的读线程做（`CommandEvent::Terminated`
   就是它发的），所以轮询能等到它变假；§3 的读数（518 ms）就是这条路径。
6. **Windows / x86_64** 仍未测（Q-03）。
