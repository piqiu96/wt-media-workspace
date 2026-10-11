# Content Discovery State Models（内容发现状态模型）

依据：[M3 有效产品基线 V2](../../product/M3-content-mining-v2.md)、[ADR-0013](../../decisions/0013-m3-content-mining-entry.md)、[ADR-0014](../../decisions/0014-m3-team-content-scope.md)、[ADR-0015](../../decisions/0015-m3-cloud-owned-discovery-execution.md)。[第四章 PRD](../../product/prd/详细文档/第四章_内容发现.md) 标明为历史 V1，其旧状态与“即时直接转素材”流程不作当前依据。本页只定义内容池、挖掘策略和挖掘任务的主状态；首版 `crawl_task` 不新增 `cancelled`，`timeout` 也不作为主状态。

## source_content（内容池；`status`：内容处理阶段）

### 1. 定位

`source_content` 是作品进入内容池后的正式来源记录。`status` 表达该来源在素材转换流程中的**处理阶段**，不表达抓取是否成功、作品在外部平台是否可访问，或源视频文件是否准备好。

### 2. 状态

| 状态 | 展示名称 | 含义 | 是否终态 |
| --- | --- | --- | --- |
| `pending` | 待处理 | 已入池，尚未决定转素材或忽略 | 否 |
| `ignored` | 已忽略 | 本团队当前不把该来源转为素材 | 否 |
| `material_created` | 已转素材 | 已存在对应正式 `material` 关系 | 是，按当前处理流程 |

### 3. 状态流转

```text
入池 → pending → material_created
              → ignored → pending
                        → material_created（人工明确选择时）
```

自动发现不会自行把 `ignored` 恢复为 `pending`。已转素材后的再忽略语义尚无明确产品定义，不能视为常规流转。

### 4. 流转条件

- 入池由人工确认的发现结果或自动策略执行产生；未选择的搜索结果不建 `source_content`。
- 有处理权限的运营可人工忽略、恢复或转素材；自动策略只在已确认的自动转素材规则命中时，将入池来源转为素材。
- `material_created` 以正式 `material` 创建或关联成功为条件；创建失败时保留原处理状态并单独记录失败原因。重复发现不得覆盖人工忽略或首次来源事实。

### 5. 状态能力

| 状态 | 新建或关联素材 | 人工恢复处理 |
| --- | ---: | ---: |
| `pending` | 可，须权限与去重校验 | 不适用 |
| `ignored` | 仅人工明确转素材 | 可 |
| `material_created` | 不再重复创建 | 不适用 |

### 6. 状态影响

转素材成功后，同一 `source_content` 对应唯一正式 `material`；历史入池和处理记录保留。忽略会阻止自动策略暗中恢复或自动转素材，已存在的其他团队记录不受影响。状态变更不意味着删除外部作品、下载源视频或改写已有素材的业务字段。

### 7. 非状态说明

`source_type`、策略来源、`availability`（平台可访问性）、失败原因、审核备注、`crawl_task` 结果、文件状态和“需要处理”提示均不属于该字段。`material_failed` 是一次任务结果项或错误事实，不是 `source_content.status` 的第四态。

## discovery_strategy（挖掘策略；`status`：策略启停）

### 1. 定位

Cloud 代码使用 `DiscoveryStrategy`，数据库表为 `discovery_strategies`，对外 API 使用 `/discovery-strategies`；正式对象名是 `discovery_strategy`。[ADR-0013](../../decisions/0013-m3-content-mining-entry.md) 已取代旧称 `crawl_strategy`，不建立第二个对象。`status` 只表示是否允许后续周期触发。策略配置与每次执行事实分离。

### 2. 状态

| 状态 | 展示名称 | 含义 | 是否终态 |
| --- | --- | --- | --- |
| `enabled` | 启用 | 配有周期计划时，允许在计划窗口创建新的执行任务 | 否 |
| `disabled` | 停用 | 暂停创建新的周期执行任务 | 否 |

### 3. 状态流转

```text
enabled ⇄ disabled
```

### 4. 流转条件

有权维护策略的用户人工启停；启用本身不立即创建任务，周期策略首次执行等待计划窗口。人工“立即执行”是独立触发动作，不成为策略新状态。策略规则编辑只作用于后续任务快照。

### 5. 状态能力

| 状态 | 新的周期任务 | 已创建任务继续执行 |
| --- | ---: | ---: |
| `enabled` | 配有周期计划时可，须符合计划和防重条件 | 是 |
| `disabled` | 不可 | 是 |

### 6. 状态影响

停用后不再按计划创建新 `crawl_task`；在途任务按创建时的配置快照完成，历史任务和来源内容保留。

### 7. 非状态说明

周期表达式、下次执行时间、`strategy_type`、自动转素材开关、上次运行结果及调度器是否在线均不是该启停字段的状态。`author` 策略在 M3 本期暂停交付，不是 `status` 的取值。

## crawl_task（挖掘任务；`status`：一次执行状态）

### 1. 定位

`crawl_task` 记录一次内容发现执行，保存当次规则快照、结果和错误。它是内容发现领域的执行事实，不是通用 Agent `task`，也不是 `source_content` 的处理状态。

### 2. 状态

| 状态 | 展示名称 | 含义 | 是否终态 |
| --- | --- | --- | --- |
| `pending` | 待执行 | 已创建，尚未开始执行 | 否 |
| `running` | 执行中 | 已被执行者领取并正在处理 | 否 |
| `success` | 成功 | 本次执行完成，没有失败项 | 是 |
| `partial_success` | 部分成功 | 同次执行有失败项，也有已处理成功项 | 是 |
| `failed` | 失败 | 有失败项，且本次执行没有可计入的已处理成功项 | 是 |

### 3. 状态流转

```text
pending → running → success / partial_success / failed
```

终态任务不改回 `pending`；重试失败项创建新 `crawl_task`，关联原任务。

### 4. 流转条件

策略到期调度或有权用户对策略执行“立即执行”时创建待执行记录；内容池的即时关键词搜索和链接查询不创建代表自动挖掘的业务 `crawl_task`。Cloud Discovery Worker 原子领取后进入 `running`。完成时按当次统计和错误事实确定终态：[M3 V2 §5](../../product/M3-content-mining-v2.md) 定义 `processed = added + duplicate + pending + auto_materialized`；有失败项且 `processed > 0` 为 `partial_success`，有失败项且 `processed = 0` 为 `failed`，否则为 `success`。仅失败或部分成功且有失败项的任务允许按失败项创建新重试任务，原记录的终态与统计保持不变。

### 5. 状态能力

| 状态 | 继续本次执行 | 基于失败项创建重试任务 |
| --- | ---: | ---: |
| `pending` | 可由执行者领取 | 不可 |
| `running` | 可继续 | 不可 |
| `success` | 不可 | 不可 |
| `partial_success` | 不可 | 有失败项时可 |
| `failed` | 不可 | 有失败项时可 |

### 6. 状态影响

成功入池或转素材的对象各自保留正式事实；部分失败不回滚成功项。重试只处理原任务的失败项，不能覆盖原任务的执行历史或通过任务状态直接篡改来源处理状态。

### 7. 非状态说明

任务项处理结果、失败原因、统计、阶段进度、是否由计划触发、策略是否启用、来源内容状态都不是 `crawl_task.status` 的附加取值。任务项的独立结果集合由 [M3 V2 §5](../../product/M3-content-mining-v2.md) 定义，不混入五态任务机。首版不提供执行中人工取消，因此不新增 `cancelled`；超时属于一次执行的错误事实，任务结束时仍按已确认的统计规则结算既有终态，不新增 `timeout` 主状态。

## 不建立独立状态机的对象

| 对象 | 处理方式与原因 |
| --- | --- |
| 即时关键词搜索结果 | 是选择入池前的临时查询结果；未选中不建正式 `source_content`，不赋予内容池处理状态，也不另建搜索结果生命周期。 |
| 链接查询结果 | 是 ID/链接发现的临时解析结果；用户提交入池后才由有效条目建立或更新 `source_content`。逐目标解析失败记录为查询错误，不建立结果状态机。 |
| 关键词执行摘要 | 从当次查询的结果、计数和错误事实汇总，用于展示查询情况；它不是独立业务执行对象，不复制 `crawl_task` 五态。 |
| `source_content` availability | 表达外部来源当前是否可访问的独立事实或派生判断，可能随平台情况变化；不改变 `source_content.status`，首版不为它建立独立生命周期状态机或预设枚举。 |

## 待确认与实现偏差

- **D1 已转素材后忽略：**M3 V2 未给出 `material_created → ignored` 的业务语义；Cloud `internal/modules/contentpool/service/service.go:setStatus` 只拒绝 `material_created → pending`，仓储更新也不限制原状态，实际允许改为 `ignored`，导致状态显示与已存在 `material` 关系可能不一致。需产品明确是否允许及其对素材的影响，再收紧或补齐服务校验。
- **D2 调度防重与可用性：**[M3 V2 §5](../../product/M3-content-mining-v2.md) 记录手工连续触发重复排队；独立 Scheduler 启动故障的修复与复验见 [ADR-0015 增补记录](../../decisions/0015-m3-cloud-owned-discovery-execution.md#增补记录)。这些执行与防重问题不新增“重复中”“调度失败”等策略或任务主状态；剩余缺陷按原 Milestone 整改与验收。
