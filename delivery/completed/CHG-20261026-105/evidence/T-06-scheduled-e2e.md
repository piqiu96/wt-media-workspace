# T-06 真实定时全链（团队素材 → 任务 → 成片 → API/页面）

日期：2026-10-27

本 Task 不新增代码；使用 `f9c3114`（团队素材候选、负责人快照）与 `fbbda88`（批次合同）后的当前源码，跑真实进程与真实依赖。

## 夹具与进程

| 对象 | 实测 |
| --- | --- |
| 策略 66「CHG-105 定时全链」 | 团队 1 / `hy` / 负责人 3 / 创建者 1 / `enabled` / `interval` 1 分钟 / 时区 `Asia/Shanghai` / 单次 1 / 每日 2 / 规则 `like_count eq 258365 → match` |
| 素材 176 | 团队 1 / 来源 906 / `available` / `ready` / `168,126,929` 字节 / sha256 `8aaef058…5e8d74` / `duration_ms=449609` / `material_usages` 计数 0 |
| 来源 906 | 团队 1 / `hy` / `like_count=258365`（`hy` 内唯一）/ `material_created` → `material_id=176` |

进程：`compose-scheduler` pid 82060、`compose-worker` pid 82117 为本 Task 启动；`discovery-worker` pid 68752 为既有进程，负责 `material_source_prepare`。Cloud API 由 pid 77967 重启为 82586（原因见下节）。

## 调度与任务

运行行：

```text
run_key        05aa31370dbeff86e6a3f17c9039d79e296ec83e7cde8f463ecb2ee7112cc32f
trigger_type   scheduled
schedule_slot  2026-10-26 19:30:34.216833（API 序列化为 2026-10-26T19:30:34.216833+08:00）
candidate_count 60
created_count   1
created_at     2026-10-27 03:30:02.462724
```

跳过：45 条 `other_game`（素材 1–34、151–161，逐条与团队素材总数 60 对得上），另有 1 条 `previously_run`（素材 176）。后续 9 次扫描均 `created_count=0`，策略 66 的任务总数始终为 1，说明重复扫描不重复建任务。

任务 350：

```text
status success / trigger_type scheduled / team 1 / game hy
operator_id 3 / operator_name pika / created_by 1
material_id 176 / material_usage_id NULL / compose_strategy_id 66
attempt_count 1 / composite_output_id 77
created_at 03:30:02.462724 / started_at 03:31:04.793355 / finished_at 03:32:08.216031
```

任务 03:30:02 创建，03:31:04 被 worker 领取；素材 176 在 03:31:57.241788 由 Cloud `material_source_prepare` 下载完成（`video_status ready`），worker 随后在 03:31:59 进入 `prepare_input`，证明“先建任务、准备源文件、再合成”的真实顺序。

## 尝试与实际产物

尝试 266（`task_id=350`、`attempt=1`、`source=auto`、`outcome=success`）：

| 步骤 | 耗时 | 实测 |
| --- | --- | --- |
| `prepare_input` | 7,312 ms | `size_bytes=168126929` |
| `cut` | 1,239 ms | `output_duration_ms=3033` |
| `upload` | 352 ms | `sha256=b968e702…dd6a5`、`size_bytes=1368540` |
| `commit` | 43 ms | `output_id=77` |

成片 77：

```text
team 1 / game hy / operator_id 3 / operator_name pika / created_by 1
material_id 176 / material_usage_id NULL / compose_task_id 350 / compose_strategy_id 66
publish_status pending_publish / file_size_bytes 1368540 / sha256 b968e702…dd6a5
media {"duration_ms": 3033}
```

对象存储实测（临时探针，已删除）：

```text
materials/176/8aaef058…5e8d74.mp4   size=168126929 sha256=8aaef058…5e8d74
compose-outputs/350/1/output.mp4    size=1368540   sha256=b968e702…dd6a5
                                    ffprobe duration=3.033008 size=1368540
```

对象大小、SHA-256、FFprobe 时长与成片行、上传步骤逐项一致；素材 176 的 `material_usages` 为 0，创建者 1 与负责人 3 都没有被写入工作集。

## API 读回

以本机临时管理员会话（`X-Session-Token`，只存 `/tmp/chg105-session-token`，未打印）请求：

| 请求 | 结果 |
| --- | --- |
| `GET /api/v1/compose-tasks/350` | 200；`operator_id=3`、`operator_name=pika`、`created_by=1`、`material_usage_id=null`、`trigger_type=scheduled`、`composite_output_id=77` |
| `GET /api/v1/compose-outputs/77` | 200；`output.material_usage_id=null`、`trace.material_usage=null`、`operator_id=3`、`created_by=1`、`publish_status=pending_publish`、SHA-256 与对象一致 |
| `GET /api/v1/compose-strategies/66/runs/tasks?schedule_slot=<run 返回值>` | 200；`counts={pending:0,running:0,success:1,failed:0,cancelled:0}`，`tasks=[350]` |
| 同一端点缺 `schedule_slot` | 400（`15210 compose_strategy_invalid`） |
| 同一端点传合法但无 run 的 slot | 404（`15212 compose_strategy_not_found`） |

`schedule_slot` 必须复用 `GET /runs` 返回的序列化值（带 `+08:00`）。把同一墙钟写成 `Z` 会表示相隔 8 小时的另一个时刻并得到 404；页面正是把 run 行的 `schedule_slot` 原样传回（`ComposeStrategyPage.vue:118`），不做时区重写。

## 页面读回

用 headless Chrome + CDP（Vite dev `127.0.0.1:5173`，管理员会话 cookie）读取三个共用页面的渲染文本；临时脚本 `/tmp/chg105-page-probe.mjs` 不提交。

```text
策略运行记录 → 查看本次任务
  排队中 0 · 处理中 0 · 成功 1 · 失败 0 · 已取消 0
  任务 350 · 素材 176
  成功 · 成片 77

任务详情（/compose?task_id=350）
  任务 ID 350 / 触发方式 策略自动 / 创建人 ID 1 / 负责人 pika
  当前状态 成功 / 关联素材 素材 176 / 合成策略 CHG-105 定时全链
  执行次数 1 / 生成成片 成片 77

成片详情（/finished-media?output_id=77）
  成片 ID 77 / 生成方式 定时 / 负责人 pika / 视频时长 3.0 秒
  文件大小 1.3 MB / SHA-256 · b968e702…dd6a5

任务关联的成片详情 → 来源追踪
  素材 ID 176 / 素材使用 — / 合成策略 66 CHG-105 定时全链
  合成模板 basic_cut v1 / 合成任务 350 / 任务状态 成功
```

探针监听 console error、`Runtime.exceptionThrown` 与所有 HTTP ≥500：三项均为 `none`。

## 旧进程导致的 500（环境事实，非产品缺陷）

首次请求任务/成片详情时两者返回 500「服务内部错误」。核查：运行中的 `.cache/wt-media-cloud-server` 构建于 03:10，早于可空 `material_usage_id` 提交 `3fe596b`（03:17），旧二进制把 NULL 扫进 `int64`。用当前源码在进程内直接调用 `GetComposeTask(admin, 350)`、`GetComposeOutput(admin, 77)` 均成功；`bin/control.sh restart` 后（pid 82586）三条 API 全部 200。结论为开发缓存二进制过期，不修改产品代码。

## 清理

- `cmd/chg105-probe/`、仓根 `chg105-probe` 与两个临时 live 调试用例已删除；Cloud `git status --short` 为空。
- `compose-scheduler`/`compose-worker` 已停止，`pgrep -fl` 无残留。
- 夹具策略 66、任务 350、成片 77、素材 176、来源 906 保留到 T-07 继续使用，CHG 归档后按 T-01 登记清理；对象存储对象不删除。

## 覆盖边界

- 本 Task 只用单 scheduler、单 worker；双 scheduler（含重启）、双 worker 抢同一素材、`run-now` 重放与额度/部分失败/人工入口是 T-07。
- 页面读回是 Cloud Web（Chromium）DOM 文本；Desktop（WebKit）共用页面走查留给 CHG-098。
- 任务/成片详情页的读回使用管理员会话；高级运营与普通运营的可见性口径已由 CHG-102/103/104 覆盖，不在本 Task 重测。
