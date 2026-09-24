# M4-M5 Cloud 内容生产工程设计

> 日期：2026-09-24
> 状态：Accepted
> 决策依据：ADR-0017  
> 产品依据：`docs/product/prd/详细文档/第五章_素材生产.md`

## 1. 设计目标

本设计为 M4 人工内容生产与 M5 自动内容生产提供同一套 Cloud 执行底座：

```text
Web / Desktop WebView
→ Cloud API
→ material / material_usage / compose_strategy / compose_task
→ Compose Worker Pool
→ FFmpeg
→ Object Storage
→ composite_output
```

首版继续使用 Go + Hertz 模块化单体、MySQL、对象存储和独立 Cloud CMD。不引入微服务、MQ、工作流引擎或动态插件。

## 2. 职责边界

| 能力 | Cloud | Desktop / Local Agent |
| --- | --- | --- |
| 业务对象与权限 | 唯一事实源 | 只消费合同 |
| 合成任务创建 | 负责 | 不创建正式任务 |
| 策略调度 | Scheduler | 不参与 |
| 视频合成 | Compose Worker + FFmpeg | 禁止 |
| 原素材合成前准备 | Cloud File Transfer Worker | 不参与 |
| 对象存储 | 上传、校验、引用、生命周期 | 不直接管理 |
| 下载到运营电脑 | 签发受控下载信息并保存任务事实 | Local Agent 写本地文件并回报进度 |
| 发布与互动 | 保存业务事实 | 浏览器自动化与本机执行 |

Cloud Web 与 Desktop WebView 复用同一业务页面。只有“选择保存目录、打开文件、写本地文件”等本机能力通过 Tauri / Local Agent。

## 3. 领域模型

### 3.1 `material`

保留正式素材语义，增加视频准备投影：

```text
video_status = not_downloaded | downloading | ready | failed
```

`material` 保存源链接、必要元数据、业务范围与当前可生产性；不保存某个用户的领取关系，也不保存传输进度明细。

### 3.2 `material_usage`

唯一“我的素材”关系：

```text
material 1 ── n material_usage n ── 1 user
```

同一用户与同一素材同一时间最多一个有效关系。移出“我的素材”不删除历史任务和成片。

### 3.3 `compose_strategy`

保存：

- 模板引用与模板版本；
- 视频比例、字幕、BGM、片尾等参数；
- 策略版本和变更审计；
- 可选 `schedule`：`enabled`、调度表达式/周期、时区、单次上限、每日上限；
- 启停状态与下次执行时间。

自动规则不拆出 `production_rule`。每次创建 `compose_task` 时保存不可变策略快照；后续修改策略不改写历史任务。

### 3.4 `compose_task`

`compose_task` 是一次生产行为及其执行事实，至少包含：

- 业务范围、触发方式 `manual | scheduled`；
- 来源 `material_id`、可选 `material_usage_id`；
- `compose_strategy_id` 与策略快照；
- 状态 `pending | running | success | failed | cancelled`；
- 调度幂等键；
- 领取者、租约到期时间、heartbeat 时间；
- 尝试次数、最大尝试次数、开始/结束时间；
- 当前阶段、进度、错误码和脱敏错误信息；
- 输出对象存储临时键/正式键和可选 `composite_output_id`。

同一次生产不得再创建 `compose_pool_item` 或通用 Agent `task`。

### 3.5 `composite_output`

只表示已通过完整性校验的成片资产。保存：

- 来源素材、素材使用关系、任务与策略快照引用；
- 对象存储键、文件大小、媒体信息和 Hash；
- 生成时间；
- 发布投影状态 `pending_publish | published | archived`。

下载记录不属于 `composite_output`，发布事实仍由第六章 `publication` 管理。

### 3.6 `file_transfer_task`

统一承载原素材与成片传输：

| 维度 | 取值 |
| --- | --- |
| `asset_type` | `material`、`composite_output` |
| `purpose` | `compose_input_prepare`、`user_download` |
| `execution_scope` | `cloud`、`local_agent` |
| `status` | `pending`、`running`、`success`、`failed`、`cancelled` |

进度字段包括总字节、完成字节、瞬时/平滑速度、预计剩余秒数、尝试次数和错误。正式业务表不保存本机绝对路径；本地路径由 Local Agent / Desktop 在本机可信存储中管理，Cloud 只保存目标节点、文件名和完成事实。

## 4. 进程模型

### 4.1 HTTP Server

`cmd/server` 负责：

- 权限与参数校验；
- `material_usage`、`compose_strategy`、`compose_task`、`file_transfer_task` 查询和命令；
- 返回任务事实和签发受控下载信息。

HTTP 请求创建任务后立即返回，不等待下载或 FFmpeg 完成。

### 4.2 Compose Scheduler

独立 `cmd/compose-scheduler`，通过 `internal/scheduler` 运行周期扫描：

1. 读取启用且到期的 `compose_strategy`；
2. 基于业务范围选择可生产 `material`；
3. 应用素材状态、策略上限和已存在任务防重；
4. 用 `strategy_id + schedule_slot + material_id` 形成唯一调度键；
5. 事务创建 `pending compose_task`；
6. 更新策略下一次执行时间。

Scheduler 不下载文件、不调用 FFmpeg、不推进任务为 `running`。

### 4.3 Compose Worker

独立 `cmd/compose-worker`，核心循环：

```text
原子领取 pending / 可恢复任务
→ 创建租约
→ 确认输入 ready；否则创建/等待 Cloud 文件准备任务
→ 准备隔离工作目录
→ 执行 FFprobe 输入校验
→ 执行 FFmpeg
→ FFprobe 输出校验
→ 上传对象存储临时键
→ 校验对象大小/Hash
→ 原子提交正式对象键与 composite_output
→ compose_task = success
→ 清理临时文件
```

Worker 不直接处理 HTTP，不跨模块写其他业务表；通过生产模块 Service 和 Repository 完成事务。

### 4.4 File Transfer Worker

Cloud 侧处理 `execution_scope=cloud` 的输入准备；Local Agent 处理 `execution_scope=local_agent` 的用户下载。

若 Cloud 输入准备与 Compose Worker 共进程，仍必须通过 `file_transfer_task` 状态边界协作，不允许在 Scheduler 调用栈内下载。只有观测到传输成功并把 `material.video_status` 投影为 `ready` 后，合成任务才能进入 FFmpeg 阶段。

## 5. 领取、并发与恢复

### 5.1 原子领取

Repository 用单条条件更新或数据库锁保证：

```text
pending
→ running + worker_id + lease_expires_at + heartbeat_at
```

更新影响行数为 1 才算领取成功。进程内锁不能代替数据库领取。

### 5.2 并发限制

配置位于 `config/scheduler`，不绑定 App 名称。至少支持：

- Worker 总并发；
- 单任务超时；
- heartbeat 间隔；
- 租约时长；
- 最大重试次数；
- 临时目录容量阈值。

默认 Worker 并发可从 5 起步，但正式值以压测和部署资源为准。配置缺失或非法时进程拒绝启动，不以无限并发降级。

### 5.3 Heartbeat 与租约

Worker 在运行期间周期续租。恢复扫描只处理 `running` 且租约已过期的任务：

- 能确认 FFmpeg 子进程已不存在：按错误分类重排或失败；
- 输出已上传但事务未提交：校验临时对象后完成或清理；
- 外部状态不明确：停止自动重试并记录人工处置原因。

### 5.4 超时和取消

取消 `pending` 任务可直接改为 `cancelled`。取消 `running` 任务先写取消请求，Worker 向 FFmpeg 发送受控终止并等待退出；只有进程已退出、临时文件已处置后才确认 `cancelled`。

任务超时使用同一终止流程，不能只改数据库状态而遗留 FFmpeg 进程。

### 5.5 重试

- 网络抖动、临时对象存储错误、Worker 崩溃：允许在上限内退避重试；
- 输入不存在、模板参数非法、不支持的编码器：业务失败，不自动重试；
- 修改策略或参数后重做：创建新的 `compose_task`，不覆盖旧任务；
- 所有重试保留尝试次数、上次错误和时间。

## 6. FFmpeg 与存储

### 6.1 运行组件

FFmpeg / FFprobe 固定在 Cloud Worker 镜像或受控部署产物：

- 使用绝对路径；
- 启动时校验 SHA256、CPU 架构、编码器和 Filter；
- 版本不兼容时 Worker 健康检查失败，不领取任务；
- 版本、编译信息与许可证进入发布清单。

### 6.2 临时目录

每个任务使用独立目录，目录名只使用内部任务 ID。输入、输出和日志文件名不得直接拼接用户标题。清理规则只删除本任务可再生临时文件，不触碰对象存储正式键或其他任务目录。

### 6.3 对象存储提交

采用“临时键 → 校验 → 正式键/标记”的提交方式。数据库提交失败时，临时对象由恢复任务清理；数据库已成功但正式对象缺失时，成片状态必须暴露异常，不能继续进入发布。

## 7. API 与 Contract

Cloud 是以下正式合同提供方：

- 素材库与 `material_usage` API；
- `compose_strategy` API；
- `compose_task` API、枚举和错误；
- `composite_output` API；
- `file_transfer_task` API 与进度投影；
- Cloud Web 使用的业务 Schema。

Local Agent 只消费受控下载合同：领取被分配的本地传输任务、获得短时下载信息、上报进度和最终 Hash。Agent 合同不得出现 FFmpeg、策略快照或合成步骤。

## 8. 安全与可观测性

- 对象存储凭据只在 Cloud 受控配置中；Local Agent 使用短时、最小范围下载授权；
- 日志包含 `trace_id`、`request_id`、`module`、任务 ID 和 Worker ID，不记录凭据或完整签名 URL；
- 生产指标至少包括队列长度、领取延迟、执行时长、成功率、重试率、超时数、FFmpeg 退出码分布、临时磁盘与对象存储失败；
- 审计记录策略启停、人工创建/取消/重试和下载任务创建；
- 普通运营只能查看本人或授权业务范围内的素材、任务、成片和下载；高级运营按负责范围管理策略；技术查看全局执行事实并留下审计。

## 9. 配置

运行时仍只读 `./config`，发布时由 `config_online` 替换产物中的 `config`。建议新增：

```text
config/scheduler/compose.yaml
config/storage/object_storage.yaml
config/media/ffmpeg.yaml
```

具体文件名在实现 CHG 中以 Cloud 现有 Loader Schema 为准；不得把配置放进 `internal`，不得创建 `server.yaml`，不得使用环境变量绕过只读 Config。

## 10. 验证矩阵

### M4

- 人工把 `material` 加入“我的素材”，同一用户重复操作不产生第二个有效 `material_usage`；
- 源视频未就绪时创建文件准备任务，完成后才执行合成；
- 真实 FFmpeg 生成可播放视频并上传真实对象存储；
- 只有校验通过后才出现 `composite_output`；
- 取消、输入损坏、FFmpeg 失败、上传失败和 Worker 崩溃均无假成片；
- 原素材和成片可经下载中心落到运营电脑并通过 Hash 校验。

### M5

- 启用策略在计划时间由 Scheduler 创建任务；同策略、同周期、同素材不重复；
- 禁用策略不创建任务；单次和每日上限生效；
- Worker 并发不超过配置；
- heartbeat、租约过期、超时终止、重试上限和重启恢复可验证；
- HTTP Server 单独运行不会启动 Scheduler 或 Worker；
- 不存在 `production_rule`、`compose_pool_item` 或 Agent 合成链路。

## 11. 明确不做

- Local Agent / Cloud Agent 视频合成；
- 同步 HTTP 等待视频生成；
- MQ、微服务、动态 Worker 注册中心；
- 可视化流程编排、任意脚本或策略插件；
- 为原素材与成片分别新建下载任务表；
- 重新命名 `material_usage` 或复制“我的素材”关系；
- 在 M4 自动创建定时生产任务；自动调度属于 M5。
