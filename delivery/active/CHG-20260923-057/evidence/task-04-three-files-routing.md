# Evidence: T-04 Agent 三文件布局与路由

- CHG: `CHG-20260923-057`
- Task: `T-04`
- Date: 2026-09-24
- Type: command（含四次真实启动）
- Status: PASS

## Purpose

把 Agent 的单文件日志改为裁定三的三文件布局（`agent.log` / `task.log` / `error.log`）并建立路由：
`agent.log` 全量且**唯一**含 traceback、`task.log` 只收 `wt_media_agent.runner.*`、
`error.log` 只收 ERROR 级且**不带 traceback**。纯文本，不上 JSON。

## Method

```bash
# 1. 先改测试（src 不动）→ 红
PYTHONPATH=tests .venv/bin/python -m unittest tests.test_runtime_logging

# 2. 实现后 → 绿 + 全套（含 T-02 的 .local 守卫）
bash scripts/test.sh; echo "exit=$?"

# 3. 四次真实启动（单元测试替代不了「接线真的通」），全程 scratch 端口 / 指向死端口
#    臂 A：local_main 常规启动，scratch 18767，BitBrowser→死端口 54399
#    臂 B：cloud_main + runner，DEBUG 级，Cloud→死端口 18099
#    臂 C：cloud_main + runner，Cloud→**自建 scratch HTTP 服务**回 errcode 11001
#    臂 D：local_main，scratch 18768，BitBrowser URL 不可解析（http://[::1）
```

四次启动都在 `/tmp` 的**工作区副本**里跑（`rsync` 含未提交改动、排除 `.local/.venv/.git`），
`repository_root()` 由 `__file__` 推导 ⇒ 跑的是真实 dev 分支；开发者的 `:8765` / `:18080` / `:54345`
与检出目录的 `.local/` 全程未碰。

## Expected

1. 先红（新符号不存在即第一处失败）。
2. 全套只增不减，T-02 的守卫不响。
3. **每条路由方向都要在真实进程里两侧各证一次**：该进的进、不该进的不进。只证「进了」不算数。
4. traceback 的分家要在真实进程里可判：`agent.log` 有 `Traceback`，`error.log` 没有。

## Actual

**1. 先红**：`ImportError: cannot import name 'AGENT_LOG_NAME'`（新符号集先失败，符合预期起点）。

**2. 实现**（`runtime/logging.py`，仍单模块；未拆包）

- `TaskLogFilter`：`record.name == "wt_media_agent.runner"` 或以其加 `.` 开头——**点边界**匹配，
  故未来的 `wt_media_agent.runner_pool` 不会被误收（有专门断言）。
- `ErrorLogFilter`：`record.levelno >= logging.ERROR`。
- `NoTracebackFormatter`：**格式化副本**而不是改记录。理由写在代码里，因为这里有个真陷阱：
  一条记录是**同一个对象**交给所有 handler，而 `Formatter.format` 会把渲染好的 traceback
  **缓存到 `record.exc_text`** ——所以只覆写 `formatException` 返回 `""` 的写法，在
  `agent.log` 的 handler 先跑（正是 `configure_logging` 的安装顺序）时，仍会把 traceback 打进
  `error.log`；而直接清 `record.exc_info` 更糟：会把 `agent.log` 的 traceback 也一起抹掉。
  有一条测试专门按「先标准、后 no-traceback」渲染同一个记录来复现这个陷阱。
- `log_file` 的语义：它命名 `agent.log`，另两个是它的**同目录兄弟**（三份属于同一目录，命名其一即命名全部）。
  这样既保住既有的 `[logging] file` 语义与全部既有测试，也不新增配置键（裁定十二：不做体系改造）。
- 三份 handler 的**滚动策略暂时沿用**今天的 10MB×3，T-07 换成裁定的 20MB / 14 天 / 总量 / 截断。

**3. 全套：259 → 267 tests OK，exit=0**（+8；T-03 那条「恰好两个 handler」的断言按新布局改为
「stderr 仍在且恰有三个文件 handler」——**stderr 未被文件取代**这一点是断言而非假设）。

**4. 单元两向断言**（8 条新增，全部正反成对）：runner 记录进 task.log ✓ / 非 runner 不进 ✓；
形近名 `runner_pool` 不进 ✓；ERROR 进 error.log ✓ / INFO 不进 ✓；
traceback 在 agent.log 且**不在** error.log ✓；同记录二次渲染仍不带 traceback ✓。

**5. 臂 A：常规启动（`local_main`，scratch 18767）**

```
-rw-r--r--  agent.log  357   2026-09-24T13:40:10 [INFO] … listening on 127.0.0.1:18767
-rw-r--r--  error.log    0
-rw-r--r--  task.log     0
```

三文件**均被创建**；`agent.log` 有真实内容。
**同一次启动里的一个实测（对 T-08 有用）**：BitBrowser 指向死端口时 `/api/v1/status` 返回
**HTTP 200** 且 `bitbrowser_status: "unreachable"` ⇒ 该端点对 BitBrowser 不可用**已经**是降级而不是抛异常。
T-08 的题设（「制造每个依赖不可用 → 断言 200 + abnormal」）必须**逐依赖重测**，不能假设今天会抛。

**6. 臂 B：DEBUG 级 + 死 Cloud（18099）——真实进程里的反向证据**

```
task.log   268  [DEBUG] wt_media_agent.runner.runner: claim failed (may be normal): <urlopen error [Errno 61] Connection refused>  ×2
agent.log  268  同上两条
error.log    0  ← DEBUG 不进 error.log，真实进程实测
```

**同一个启动里查出一条既有行为（只登记，本 CHG 不改）**：默认 INFO 级时，**Cloud 不可达在任何文件里
都看不见**——`runner.py:137` 的 `_claim_task` 把所有异常吞成 `logger.debug`。
这是业务级日志级别策略，改动超出本 CHG 范围（裁定十二禁止大范围业务重构），故**只记录**：
「Cloud 一直连不上」这条现场，今天在 INFO 下不可定位。臂 B 顺便坐实了这一点（必须显式设 DEBUG 才看得见）。

**7. 臂 C：真实 ERROR（Cloud 由 scratch HTTP 服务应答 `errcode 11001`）**

```
agent.log  127  2026-09-24T13:41:23 [ERROR] wt_media_agent.runner.runner: agent session invalidated; draining runner: scratch: session invalid
task.log   127  同一条（ERROR 也是任务叙事的一部分）
error.log  127  同一条
```

三文件**同时非空**且内容一致（该记录无 `exc_info`，故无 traceback 可分离）。
scratch 服务是**自建**的（`/tmp/t04-fake-cloud.py`，仅本 Task 期间存在，已删），不碰开发者的 `:18080`。

**8. 臂 D：真实 traceback 的分家（BitBrowser URL 不可解析）**

`status()` 的 `except` 里 `logger.exception` 抛出前被触发（`http://[::1` → `ValueError: Invalid IPv6 URL`）：

```
agent.log  2406  … [ERROR] local_api.status.failure duration_ms=55
                 Traceback (most recent call last):
                   File "…/local_api/server.py", line 89, in status
                 ValueError: Invalid IPv6 URL          ← 完整 traceback

error.log   101  2026-09-24T13:41:42 [ERROR] wt_media_agent.local_api.server: local_api.status.failure duration_ms=55
                                                       ← 同一记录，**无 traceback**（grep Traceback = 0）

task.log      0  ← local_api.server 的 ERROR **不进** task.log
```

**一次启动同时给出三条真实进程的两向证据**：traceback 只在 `agent.log`；`error.log` 收到该 ERROR 但
不带栈；非 runner 的 ERROR 不进 `task.log`。这是本 Task 最有力的一条，因为它不依赖任何单元断言。

**9. 边界与未做（不夸大）**

- `task.log` 的真实内容**需要 runner 在跑**：实测 runner 只由 `bootstrap/cloud.py:48`（`WT_MEDIA_AGENT_RUN_RUNNER`）
  与 `bootstrap/sidecar.py:20` 启动，**`local_main` 从不启动它**。故臂 A 的 `task.log` 为空是结构事实，
  不是路由失效（臂 B/C 已证明同一个文件在有 runner 时会写）。**没有为了好看而造一条任务记录。**
- 三文件的滚动预算是 3 × 10MB × 3 ≈ 最多 120MB（原先 40MB）。T-07 按裁定改为 20MB / 14 天 / 总量上限。
- 真实取证只在 macOS 上做；Windows 未取证（沿用 CHG-056 的登记方式）。

## Follow-Up

- T-05：`error.log` 的行要含 `timestamp` / `error_code` / `task_id` / `context` / `message`
  ——`NoTracebackFormatter` 与 `FMT` 会随之扩展。
- T-07：把三份 handler 的 10MB×3 换成 20MB / 14 天 / 总量 / 单条截断（本 Task 刻意没动它）。
- T-08：**不要假设**外部依赖不可用会抛——BitBrowser 一条实测已降级为 200/`unreachable`，其余依赖逐条重测。
- 观察项（不改）：「Cloud 不可达」在默认 INFO 下全文件不可见（`runner.py:137` 吞成 DEBUG）。
