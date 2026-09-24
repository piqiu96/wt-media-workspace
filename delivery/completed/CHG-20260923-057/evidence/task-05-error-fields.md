# Evidence: T-05 `error.log` 的结构化字段通道

- CHG: `CHG-20260923-057`
- Task: `T-05`
- Date: 2026-09-24
- Type: command（含两次真实启动）
- Status: PASS

## Purpose

按裁定三，`error.log` 每行必含 `timestamp`、`error_code`、`task_id`(可选)、`context`(可选)、`message`。
本 Task 只建**通道**（`extra={...}` 约定 + formatter 缺省），**不发明错误码**；取值来源限于仓里已有的字面量。

## Method

```bash
# 1. 先红（src 不动）
PYTHONPATH=tests .venv/bin/python -m unittest \
  tests.test_runtime_logging.ErrorRecordFieldsTest tests.test_runner_error_fields

# 2. 实现后 → 绿 + 全套
bash scripts/test.sh; echo "exit=$?"

# 3. 设计前提先实测（裁定/计划写的机制能不能成立）
#    setLogRecordFactory 预置字段 + extra= 会不会撞车

# 4. 两次真实启动（臂 A 真实任务失败 / 臂 B 未注册类型），全程 scratch 端口 17901 + /tmp 工作树副本
```

## Expected

1. 先红，且红在「字段没渲染」这一因上。
2. 全套只增不减，T-02 的 `.local` 守卫不响。
3. 两向：有 `extra` 出字段；**没有 `extra` 不抛**且把「无码」说清楚。
4. 真实进程里可判：失败任务在 `error.log` 里能按 `task_id` / `error_code` 定位，且**另两个文件不渲染字段**。

## Actual

**1. 先红**：8 处（5 条字段缺失、1 条 `AttributeError: 'LogRecord' object has no attribute 'error_code'`、
1 条 `error_code=none` 缺失、1 条转义断言），**全部红在「通道不存在」这一因**上，无一条因别的错而红。

**2. 实现**

- `runtime/logging.py`：新增 `ERROR_CODE_FIELD`/`TASK_ID_FIELD`/`CONTEXT_FIELD`/`NO_VALUE`/`ERROR_FMT`、
  `_field()` 与 `ErrorRecordFormatter`（`NoTracebackFormatter` 的子类，`isolate()` 提为可复用方法）；
  `error.log` 的 handler 由 `no_traceback` formatter 换成 `error_record`。**只有 `error.log` 渲染这三个字段**。
- `runner/runner.py`：**9 个** task-scoped emit 点加 `extra={"task_id": …}`（计划写「8 个」，
  实测分母是 9：`:73/:75/:90/:92/:108/:113/:120/:123/:126`），其中 3 个按仓里**已存在**的字面量加
  `error_code`：`no_executor`(`:109`)、`session_invalidated_result_uncertain`(`:124`)、
  `executor_error`(`:182` 的 checkpoint 码)。**`task_id` 仍留在消息里**（字段是补充，不是替代）。
  另外 5 个 emit 点（`:57/:70/:82/:134/:137`）本就没有 task 在作用域内，**不加 extra**——它们是真实代码里的
  「无 extra」臂。

**3. 设计前提实测（推翻计划里写死的机制）**

计划写的是 `setLogRecordFactory` 默认 `None` + `extra={...}` 约定。**这两半不能共存**：

```
factory 预置 record.error_code = ""
  logger.error("plain", extra={})                      → OK
  logger.error("code", extra={"error_code": "x"})      → KeyError "Attempt to overwrite 'error_code' in LogRecord"
```

`Logger.makeRecord` 拒绝任何已经是记录属性的 `extra` 键，故预置默认值会让**它本要服务的那个约定**必然抛错。
缺省因此放在 **formatter** 里（渲染副本，不与任何 `extra` 相撞），并把这条碰撞写成测试
（`test_pre_populating_the_fields_in_a_record_factory_would_break_extra`），使该取舍成为可执行的决定而非注释。

**4. 全套：267 → 278 tests OK，exit=0**（+11：`ErrorRecordFieldsTest` 7 条 + `test_runner_error_fields` 4 条）。

**5. 两向断言（单元）**

- 有 `extra`：`error_code=executor_error` 与 `task_id=t-1` 同时出现在 `error.log`，**消息仍在** ✓
- 无 `extra`：渲染 `error_code=none`（而非空串——读者要能区分「本事件无码」与「字段没进这一行」）✓
- 可选字段不设时**整段不出现**（`task_id=`/`context=` 零命中），且**同一文件里同一子串在设值时确实命中**（阳性对照）
- 字段值的换行被转义：注入 `task_id="t-1\n2026-01-01 [ERROR] forged"` 后该文件仍**只有一行** ✓
- 边界：同一条记录在 `error.log` 有 `error_code=`，在 `agent.log`/`task.log` **零命中**（该 Task 只给 `error.log` 上结构）✓

**6. 真实进程（臂 A：真实任务、真实 executor 失败）**

scratch Cloud（`/tmp` 自建，仅本 Task 期间存在，已删）派一个 `cookie_read_task`、payload 为空；
真实 `CookieReadExecutor` 自己抛错：

```
error.log  186  2026-09-24T13:47:57 [ERROR] wt_media_agent.runner.runner: error_code=executor_error task_id=t05-real-1 task t05-real-1 failed: cookie_read_task requires profile_id or browser_profile_id
task.log   248  … 同一条但**无字段**
agent.log  248  … 同一条但**无字段**
```

字段命中分母（`grep -c 'error_code='`）：**`error.log` 1 / `agent.log` 0 / `task.log` 0**；
`task.log` 的 `task_id=` 命中 0。一次启动同时给出「该渲染的渲染了、另两个文件没被顺带改格式」。

**7. 真实进程（臂 B：未注册类型 → `no_executor` 是 WARNING）**

```
agent.log  [WARNING] … no executor for task type a_type_nobody_registered
error.log  0 字节   ← WARNING 不进 error.log（真实进程实测）
```

**8. 边界与未做（不夸大）**

- **`context` 今天没有生产点**。通道建好、渲染有测试覆盖，但没有任何 `src/` 调用传它——
  因为记录的 `%(name)s` 已经承载了组件，再塞一个 context 会与之重复。登记为「通道就绪、无生产点」，
  **没有为了让字段好看而造调用点**。
- **非 ERROR 的 `error_code` 在文件里看不见**：`no_executor` 是 WARNING，`error.log` 按级别不收，
  而 `agent.log`/`task.log` 不渲染字段 ⇒ 该码只存在于记录对象与 checkpoint / Cloud 上报里（臂 B 即此形状）。
  要让它可见只需给 `task.log` 换 formatter（一行），本 Task 按裁定三的范围**不做**。
- **既有不一致（只登记，本 CHG 不改）**：`_save_failed` 无论何种失败都把 checkpoint 的
  `error_code` 列写成 `executor_error`，更具体的码落在 `message` 列。日志行比 DB 列更具体。改动超出本 CHG 范围。
- 消息里的 `task_id` 仍是**文本插值**（既有的形状，本 Task 未改）：值里若含换行，仍可伪造一行。
  本 Task 只保证**自己渲染的字段**单行；报文级的行完整性属 T-06 的议题，已登记。
- 真实取证只在 macOS 上做；Windows 未取证（沿用 CHG-056 的登记方式）。

## Follow-Up

- T-06：脱敏 Filter（表驱动）。本 Task 的 `_field()` 只管单行，**不管敏感值**。
- T-07：三份 handler 仍是 10MB×3，换成 20MB / 14 天 / 总量 / 单条截断。
- T-08：契约文件同步；`contracts/local-error-codes/v1/bitbrowser.yaml` 的三个码本轮**未接进日志**
  （它们在 `local_api/server.py` 只作为 HTTP 响应体出现），要接需先定它们在哪个 emit 点上出现。
