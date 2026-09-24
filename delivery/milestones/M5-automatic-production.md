# M5 策略自动生产与 Worker 资源控制

- Milestone status: `NOT_STARTED`
- Product baseline: `docs/product/prd/详细文档/第五章_素材生产.md`
- Engineering baseline: `docs/engineering/specs/2026-09-24-m4-m5-cloud-content-production.md`
- Decision: `docs/decisions/0017-m4-m5-cloud-owned-content-production.md`
- Dependency: M4 `DONE`
- Confirmed: 2026-09-24，用户确认自动规则直接归 `compose_strategy`

## 1. 里程碑目标

高级运营配置并启用 `compose_strategy.schedule` 后，Cloud Scheduler 在正确时间、正确时区和数量上限内幂等创建 `compose_task`；Worker Pool 在受控并发和资源边界内自动生成 `composite_output`，并能从进程退出、heartbeat 中断、超时和临时依赖失败中恢复。

```text
compose_strategy.schedule
→ Cloud Scheduler
→ 幂等创建 compose_task
→ Worker Pool
→ composite_output
```

M5 不创建 `production_rule`、`compose_pool_item`、成片池、成片领取或 MQ。

## 2. 前置条件

- M4 为 `DONE`；
- 人工 `compose_task → composite_output` 已通过真实 FFmpeg 与对象存储验收；
- `compose_strategy` 已有稳定版本、快照和权限；
- Worker 单任务租约、heartbeat、取消、超时和重试底座已在 M4 验证；
- Scheduler 仍遵守只入队、不执行的边界。

## 3. 闭环拆分与 CHG 顺序

| 阶段 | 独立结果 | 候选 CHG | 状态 |
| --- | --- | --- | --- |
| M5-A | 策略计划、启停、时区、素材范围和数量上限 | M5-C1 | `NOT_STARTED` |
| M5-B | Scheduler 到期扫描、调度幂等与重启恢复 | M5-C2 | `NOT_STARTED` |
| M5-C | Worker Pool 并发、租约、heartbeat、超时和资源保护 | M5-C3 | `NOT_STARTED` |
| M5-D | 批量部分失败、重试、取消、运行统计和人工处置 | M5-C4～M5-C6 | `NOT_STARTED` |
| M5-E | 真实计划时间、并发压力、故障恢复和用户验收 | M5-C7 | `NOT_STARTED` |

## 4. 闭环卡 M5-A：策略调度

### 用户目标

高级运营能够让一条已有合成策略按业务节奏自动生产，同时明确控制素材范围、单次上限和每日上限。

### 前置条件

- 策略模板和参数已在 M4 人工任务中验证；
- 用户拥有策略业务范围的高级运营权限；
- Cloud 时区和调度配置有效。

### 用户操作顺序

1. 打开“合成策略”；
2. 编辑自动执行设置；
3. 选择时区、时间/周期、素材范围、单次上限和每日上限；
4. 启用策略；
5. 查看下一次执行时间；
6. 到期后查看自动创建的任务和运行统计；
7. 可暂停自动执行或手动“立即执行”。

### 系统与外部动作

- Cloud 校验配置并保存到 `compose_strategy`；
- Scheduler 扫描到期策略；
- 按权限范围、素材可用性和上限筛选候选素材；
- 以 `strategy_id + schedule_slot + material_id` 形成调度幂等键；
- 事务创建 `pending compose_task` 并推进下一次执行时间；
- “立即执行”复用同一任务创建入口，不同步合成。

### 成功必须同时满足的事实

- 启用策略在预期时区与时间槽触发；
- 禁用策略不触发；
- 同一时间槽重扫、Scheduler 重启或并发扫描不重复创建；
- 单次与每日上限真实生效；
- 每个候选素材独立创建或记录跳过原因；
- Scheduler 不持有 FFmpeg、对象存储写入或下载执行依赖。

### 失败时禁止出现的假成功

- 只保存 cron 字符串就显示自动生产已完成；
- 调度进程未运行但页面显示“运行中”；
- 同周期重复生成多条任务；
- 超限任务先创建再静默删除；
- Scheduler 直接执行 FFmpeg 或调用 Worker 函数完成任务。

### 对应 CHG

- M5-C1、M5-C2（待建立）。

## 5. 闭环卡 M5-B：Worker 资源控制与恢复

### 用户目标

系统可以无人值守批量生产，但不会超过 Cloud 资源上限；Worker 或依赖短暂失败后，任务能安全恢复且不会双执行。

### 前置条件

- M5-A 已验收并能创建真实 `pending compose_task`；
- Worker 并发、租约、heartbeat、超时和最大重试配置有效；
- 具备受控故障注入和资源监控环境。

### 用户操作顺序

1. 高级运营查看自动任务列表和策略运行统计；
2. 技术查看队列、Worker 和资源指标；
3. 对失败任务查看原因、重试或取消；
4. 在结果不明确时人工处置。

### 系统与外部动作

- Worker 原子领取任务并创建租约；
- Worker Pool 限制同时运行数量；
- 执行中周期续租和 heartbeat；
- 超时触发受控终止，不遗留 FFmpeg；
- 可重试技术失败退避重排；
- 租约过期任务在确认旧执行停止后恢复；
- 业务失败和结果不明确停止自动重试。

### 成功必须同时满足的事实

- 实测最大并发不超过配置；
- 同一任务任何时刻最多一个执行者；
- Worker 崩溃后任务不会永久卡在 `running`；
- 达到重试上限后稳定进入 `failed`；
- 取消与超时后真实 FFmpeg 进程已经退出；
- 对象存储临时键和临时目录可恢复清理；
- 运行统计与任务、尝试和错误事实一致。

### 失败时禁止出现的假成功

- 只靠进程内锁宣称分布式唯一领取；
- heartbeat 停止后立即启动第二个执行者而不确认旧进程；
- 数据库状态取消但 FFmpeg 继续运行；
- 重试覆盖历史错误或无限循环；
- 资源不足时绕过并发上限。

### 对应 CHG

- M5-C3～M5-C6（待建立）。

## 6. 闭环卡 M5-C：自动生产综合验收

### 用户目标

高级运营能从策略页面确认一条自动计划真正按时生成了可播放成片，并在常见故障后继续稳定运行。

### 前置条件

- M5-A、M5-B 已完成；
- 有真实素材、真实对象存储和可验证的 Cloud 资源指标；
- M4 人工链路仍保持通过。

### 用户操作顺序

1. 创建或复制一条策略并设定近期计划时间；
2. 启用并等待真实 Scheduler 触发；
3. 查看批量任务、部分失败与成功成片；
4. 暂停策略并确认不再生成任务；
5. 查看 Worker 重启与失败重试后的最终结果；
6. 在“我的成片”预览并下载一条自动生成成片。

### 系统与外部动作

- Scheduler、Worker 作为独立进程实际运行；
- 任务按计划创建并按并发限制执行；
- 成片写入对象存储并进入普通“我的成片”查询；
- 下载继续复用 M4 `file_transfer_task`，不增加领取或成片池对象。

### 成功必须同时满足的事实

- 从策略启用到成片下载的整条链路使用真实时间、数据库、FFmpeg、对象存储和 Local Agent；
- 自动与人工成片使用同一 `composite_output`；
- M4 人工生产和下载回归通过；
- Cloud Web 与 Desktop WebView 显示同一正式状态；
- 用户人工签收完成。

### 失败时禁止出现的假成功

- 用手动接口代替定时触发却宣称 Scheduler 通过；
- 只创建任务、不生成文件就宣称自动生产完成；
- 通过 Mock FFmpeg 或内存对象存储代替真实依赖；
- 自动成片进入另一套列表或另一张成片表；
- 测试结束后残留无限重试或失控 Worker。

### 对应 CHG

- M5-C7（待建立）。

## 7. M5 验收矩阵

| AC | 验收要求 | 最低证据 | 状态 |
| --- | --- | --- | --- |
| M5-AC-01 | `compose_strategy.schedule` 配置、启停和时区正确 | API/数据库/UI 对照 | `TODO` |
| M5-AC-02 | 真实到期扫描创建任务 | 独立 Scheduler 进程证据 | `TODO` |
| M5-AC-03 | 同时间槽并发/重启扫描防重 | 并发测试 + 唯一键证据 | `TODO` |
| M5-AC-04 | 单次和每日上限生效 | 边界值测试 | `TODO` |
| M5-AC-05 | Worker 有界并发和资源保护 | 压测 + 指标 | `TODO` |
| M5-AC-06 | heartbeat、租约过期和 Worker 重启恢复 | 故障注入 | `TODO` |
| M5-AC-07 | 超时/取消真实终止 FFmpeg | 进程与任务对照 | `TODO` |
| M5-AC-08 | 技术失败退避重试、业务失败不盲目重试 | 错误分类测试 | `TODO` |
| M5-AC-09 | 批量部分失败统计准确 | 数据库/API/UI 对账 | `TODO` |
| M5-AC-10 | 自动任务生成真实可播放成片 | FFprobe + 对象存储 | `TODO` |
| M5-AC-11 | M4 人工生产和下载完整回归 | M4 验收矩阵复跑 | `TODO` |
| M5-AC-12 | 不存在旧对象或 Agent 合成路径 | Migration/代码/Contract 扫描 | `TODO` |
| M5-AC-13 | 用户按真实计划流程签收 | 人工验收记录 | `TODO` |

## 8. M5 DONE Gate

M5 只有在 M5-AC-01～13 全部 PASS、M4 回归通过、真实 Scheduler/Worker/FFmpeg/Object Storage 证据齐全并经用户签收后才能进入 `DONE`。保存策略、调用“立即执行”、创建任务记录或 Mock Worker 都不能替代真实定时自动生产验收。

