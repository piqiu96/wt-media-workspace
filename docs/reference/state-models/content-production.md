# 内容生产状态模型

依据：[第五章 PRD V2](../../product/prd/详细文档/第五章_素材生产.md)、[ADR-0017](../../decisions/0017-m4-m5-cloud-owned-content-production.md)、[M4](../../../delivery/milestones/M4-content-production.md)、[M5](../../../delivery/milestones/M5-automatic-production.md)及[工程规范](../../engineering/specs/2026-09-24-m4-m5-cloud-content-production.md)。M4-A 的素材、使用关系和文件任务已有实现；`compose_strategy`、`compose_task`、`composite_output` 属 M4 后续阶段，M5 自动触发尚未实施。后者是已确认的产品模型，不能误报为现有代码状态。

## material（`video_status`；源视频准备事实）

### 1. 定位

`material` 是正式生产输入资产。现阶段**没有独立的 `material` 业务生命周期状态机**；其已落地的 `video_status` 只描述 Cloud 合成所需源视频是否准备好，不表示素材是否被领取、正在生产或已生成成片。

### 2. 状态

| 状态 | 展示名称 | 含义 | 是否终态 |
| --- | --- | --- | --- |
| `not_downloaded` | 未下载 | 有来源链接，Cloud 源视频尚未准备 | 否 |
| `downloading` | 下载中 | Cloud 源视频准备正在进行 | 否 |
| `ready` | 已就绪 | 源文件完成准备与必要校验 | 是，对本次准备 |
| `failed` | 下载失败 | 本次源视频准备失败，资产仍存在 | 否 |

### 3. 状态流转

```text
not_downloaded → downloading → ready
                           → failed → downloading
```

准备中止且没有有效文件时可回到 `not_downloaded`；这是文件准备结果复核，不是素材生命周期倒退。

### 4. 流转条件

转素材只创建资产与来源快照，初始为 `not_downloaded`。主动准备或合成前发现源视频未就绪时，由受控文件任务启动准备；只有文件存在并通过校验才为 `ready`。准备失败记录独立错误原因；重试真实准备后才能再变为 `ready`。

### 5. 状态能力

| 状态 | 保留为正式素材 | 创建合成任务 | 直接开始媒体处理 |
| --- | ---: | ---: | ---: |
| `not_downloaded` | 是 | 可，须先准备文件 | 不可 |
| `downloading` | 是 | 可，等待文件就绪 | 不可 |
| `ready` | 是 | 可 | 可，仍须其他条件通过 |
| `failed` | 是 | 可，须先重试准备 | 不可 |

### 6. 状态影响

源视频未就绪时，关联的合成任务保持排队或等待阶段，不因此给 `material` 增加“生产中”状态。下载失败不删除 `material` 或 `material_usage`，也不意味着本机副本不存在；本机下载由独立文件任务记录。

### 7. 非状态说明

“是否可生产”、使用人数、最近生产结果、风险、源链接是否可访问、本机文件存在性和 `video_error` 都不是 `video_status` 的新取值；它们由业务规则、关联对象或独立错误字段表达。

## material_usage（`status`；个人使用关系）

### 1. 定位

`material_usage` 表示一个用户将一条正式素材加入自己的生产集合。状态只描述这条关系当前是否有效，不描述素材本身或最近合成任务的结果。

### 2. 状态

| 状态 | 展示名称 | 含义 | 是否终态 |
| --- | --- | --- | --- |
| `active` | 已加入 | 关系当前有效 | 否 |
| `removed` | 已移出 | 用户暂时移出自己的集合，关系记录保留 | 否 |

### 3. 状态流转

```text
active ⇄ removed
```

### 4. 流转条件

有权限的用户加入时创建或恢复同一关系；重复加入有效关系不创建第二条。用户移出时将原关系设为 `removed`。恢复前仍须检查当前素材和业务范围是否允许使用。

### 5. 状态能力

| 状态 | 在“我的素材”中作为有效关系 | 基于该关系新建人工合成任务 |
| --- | ---: | ---: |
| `active` | 是 | 可，仍须素材与权限校验 |
| `removed` | 否 | 不可 |

### 6. 状态影响

移出不删除历史 `compose_task`、`composite_output` 或发布记录；恢复沿用原关系，不篡改既有生产事实。自动生产可按策略直接选择有权限的 `material`，不要求个人 `material_usage`。

### 7. 非状态说明

“待合成 / 处理中 / 已生成 / 失败”是最近 `compose_task` 的投影，不是 `material_usage.status`。文件就绪、素材可用性、领取锁和个人收藏标签也不并入此关系状态。

## compose_strategy（当前不定义独立生命周期状态机）

`compose_strategy` 保存模板、参数、版本及可选 `schedule`。已明确的是 M5 自动执行设置中的 `schedule.enabled` 启停：关闭后不创建新的计划任务，已创建任务保留快照并继续按自身状态处理。[第五章 §5.5](../../product/prd/详细文档/第五章_素材生产.md) 与[工程规范 §3.3](../../engineering/specs/2026-09-24-m4-m5-cloud-content-production.md) 提到策略“启停”，但尚未给出独立 `compose_strategy.status` 的正式枚举、进入/退出条件及其与 `schedule.enabled` 的关系。M4-C2 建模时应明确该维度；本轮不把“待审核 / 运行中 / 失败”或 `production_rule` 塞入策略状态。

## compose_task（`status`；一次生产执行，M4 后续阶段）

### 1. 定位

`compose_task` 保存一次生产意图、不可变策略快照和执行事实。人工与 M5 自动触发使用同一种任务；它不是成片资产，也不另建 `compose_pool_item` 或通用 Agent `task`。

### 2. 状态

| 状态 | 展示名称 | 含义 | 是否终态 |
| --- | --- | --- | --- |
| `pending` | 排队中 | 已建立任务，等待输入准备或执行资源 | 否 |
| `running` | 处理中 | 已领取并执行本次生产 | 否 |
| `success` | 成功 | 文件校验和保存完成，已产生正式成片 | 是 |
| `failed` | 失败 | 本次生产未形成正式成片 | 本次执行是；同任务重试边界待确认 |
| `cancelled` | 已取消 | 取消已真正完成 | 是 |

### 3. 状态流转

```text
pending → running → success / failed / cancelled
       → cancelled
```

技术重试及已失败任务再排队的精确路径须在 M4-C5 结合尝试历史确认；这里不预设 `failed → pending`。

### 4. 流转条件

有权用户人工提交，或 M5 Scheduler 按已启用计划创建 `pending` 任务。源视频未就绪时仍为 `pending`；Worker 在输入与资源条件满足后领取。只有真实输出通过媒体校验并写入对象存储后才能 `success`。失败记录原因；运行中取消须确认实际处理进程已停止才进入 `cancelled`。修改策略或参数重新生产时创建新任务。

### 5. 状态能力

| 状态 | 本次继续执行 | 请求取消 | 查看正式成片 |
| --- | ---: | ---: | ---: |
| `pending` | 可 | 可 | 不可 |
| `running` | 可 | 可，须完成真实停止 | 不可 |
| `success` | 不可 | 不可 | 可 |
| `failed` | 不可；重试规则待确认 | 不可 | 不可 |
| `cancelled` | 不可 | 不可 | 不可 |

### 6. 状态影响

只有成功任务可对应新 `composite_output`；失败、取消、超时或结果不明都不能产生假成片。已存在的 `material` 与 `material_usage` 不因一次任务失败转成“失败素材”。策略后续编辑不改历史任务快照。

### 7. 非状态说明

等待源视频、输入校验、FFmpeg 处理、上传阶段、百分比、租约、heartbeat、尝试次数与失败原因都不是主状态。自动或人工触发是来源维度，也不另造主状态。

## composite_output（发布投影；M4 后续阶段）

### 1. 定位

`composite_output` 仅在一次合成真实成功后创建，代表唯一正式成片资产。第五章列出下列**产品状态文案**，但“发布结果”与“是否归档”可能是两个维度；目前不能据此确认一个统一的资产状态字段或完整状态机。正式字段及与 `publication` 的关系待 M4-C6 / M6 契约确认。

### 2. 状态

| 状态 | 展示名称 | 含义 | 是否终态 |
| --- | --- | --- | --- |
| `pending_publish` | 待发布 | 已有成片，尚无成功发布事实 | 未确定统一字段 |
| `published` | 已发布 | 关联的发布事实表明已成功发布 | 未确定统一字段 |
| `archived` | 已归档 | 成片从常用工作集合归档，资产与历史仍保留 | 未确定统一字段 |

### 3. 状态流转

```text
创建真实成片 → 待发布
真实发布成功 → 已发布（发布结果维度）
人工归档 → 已归档（资产整理维度）
```

以上是已知事件与产品文案的关系，**不是** `pending_publish → published → archived` 的单字段流转。归档后能否仍显示已发布、归档恢复及多次发布汇总规则尚未定义。

### 4. 流转条件

`pending_publish` 只能在媒体文件校验与存储完成后随资产创建。`published` 应依据第六章正式发布结果，而不能由“点击去发布”或下载成功触发。`archived` 由有权限的用户人工处理；其与既有发布事实的关系待确认。

### 5. 状态能力

| 状态 | 预览和追溯资产 | 新建发布流程 |
| --- | ---: | ---: |
| `pending_publish` | 可 | 可 |
| `published` | 可 | 依第六章规则 |
| `archived` | 历史可追溯 | 待归档规则确认 |

### 6. 状态影响

发布投影不能改变 `compose_task` 的成功事实或删除对象存储资产。下载成片、本地副本及后续发布记录分别属于文件任务和发布领域；归档不抹掉这些历史。

### 7. 非状态说明

`pending`、`running`、`failed` 属于 `compose_task`；下载进度与失败属于 `file_transfer_task`；平台发布的逐次结果属于 `publication`。它们不加入成片发布投影。

## file_transfer_task（`status`；一次文件执行）

### 1. 定位

同一文件任务对象记录 Cloud 源视频准备或运营电脑上的素材/成片下载；用途和执行位置由独立字段区分。它的状态只表示**这次传输执行**，不充当素材、成片或本机文件的业务生命周期。

### 2. 状态

| 状态 | 展示名称 | 含义 | 是否终态 |
| --- | --- | --- | --- |
| `pending` | 待执行 | 已创建，尚未完成领取 | 否 |
| `running` | 进行中 | 传输执行中 | 否 |
| `success` | 成功 | 目标文件完成并通过所需完整性校验 | 是 |
| `failed` | 失败 | 本次传输失败 | 对本次尝试是；当前实现可重排同一任务 |
| `cancelled` | 已取消 | 取消完成，临时文件不作正式文件 | 是 |

### 3. 状态流转

```text
pending → running → success / failed / cancelled
       → cancelled
```

当前实现另有 `failed → pending` 重试同一条记录；它涉及历史执行事实保留问题，见下方偏差，不作为通用推荐规则。

### 4. 流转条件

用户下载或合成前准备创建任务；受控执行者领取后开始传输。完成且字节数、Hash 等必要校验通过才成功。失败记录原因，取消须停止实际传输并确保残留临时文件不被当作成品。重试前须确认旧执行已停止并有剩余次数。

### 5. 状态能力

| 状态 | 本次继续传输 | 请求取消 | 作为完整文件使用 |
| --- | ---: | ---: | ---: |
| `pending` | 可领取 | 可 | 不可 |
| `running` | 可 | 可 | 不可 |
| `success` | 不可 | 不可 | 可，仍需文件事实有效 |
| `failed` | 不可；可发起受控重试 | 不可 | 不可 |
| `cancelled` | 不可 | 不可 | 不可 |

### 6. 状态影响

Cloud 源视频准备成功并读回文件事实后，可将 `material.video_status` 更新为 `ready`；失败保持素材资产并记录文件错误。用户本机下载成功不创建成片或发布记录，本机文件删除也不删除 Cloud 资产。

### 7. 非状态说明

`asset_type`、`purpose`、`execution_scope`、传输进度、速度、失败原因、文件所在位置及“可打开”判断都不属于 `status` 的取值。

## 不建立独立状态机的旧对象

`production_rule` 的自动规则归 `compose_strategy.schedule`；`compose_pool_item` 和通用生产 `task` 的执行语义归 `compose_task`；`composite_output_pool` 与 `composite_output_claim` 不属于 M4/M5 正式对象。[ADR-0017](../../decisions/0017-m4-m5-cloud-owned-content-production.md)和 [M5](../../../delivery/milestones/M5-automatic-production.md)已明确这些边界，不为旧名称编造状态或以它们表达页面集合。

## 待确认与实现偏差

- **P1 合成任务重试：**[第五章 §5.6、§5.8](../../product/prd/详细文档/第五章_素材生产.md)允许失败后“重试当前任务”，并要求同任务保留尝试次数；一次执行失败事实也必须可追溯。M4-C5 需明确技术尝试在何时属于同一个未终结的业务任务、如何留存每次结果，以及何时应创建新任务；确认前不把 `failed → pending` 写成正式流转。
- **P2 成片发布与归档维度：**[第五章 §5.9.5](../../product/prd/详细文档/第五章_素材生产.md)给出三值产品状态，[工程规范 §3.5](../../engineering/specs/2026-09-24-m4-m5-cloud-content-production.md)称其为发布投影。“已归档”描述资产整理，“已发布”描述发布事实，可能不能互斥。M4-C6 / M6 应先确定字段维度、它如何由 `publication` 派生或受控同步，以及多次发布和归档恢复语义；确认前不创建三值数据库 enum。
- **P3 文件任务历史：**Cloud `internal/modules/filetransfer/repository/store_mysql.go:RetryTask` 现把同一条 `failed` 记录改为 `pending`，清空 `error_code`、`error_message`、`finished_at` 等字段，仅保留累计 `attempt_count`。这不足以还原旧尝试的失败事实。应在文件传输契约中明确“新任务重试”或独立尝试记录方案，再评估迁移与兼容性；本轮不改代码或数据。
