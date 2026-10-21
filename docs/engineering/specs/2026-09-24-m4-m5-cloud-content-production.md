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

`video_status=ready` 是投影，不是对象存在的证明。合成、用户下载与预览在消费前必须对 `source_object_key` 执行 `Stat`；不得仅凭状态直接开始合成或签发下载地址。

素材准备采用两跳落盘：平台临时地址 → 准备进程本地文件 → 暂存对象 `materials/<id>/.staging/<taskID>.<ext>` → 云端内部复制为正式对象 `materials/<id>/<sha256>.<ext>` → 删除暂存对象。正式 key 只在内容确认后出现；平台临时播放地址每次准备重新解析，不持久化。

`ready` 且对象确认丢失时，消费方用 `MarkVideoRepreparing` 把状态回退为 `downloading`。该 CAS 只匹配调用方观察到的 `source_object_key` 与 `video_prepared_at`（NULL-safe），并发准备刚成功时不会误回退新结果。`MarkVideoPreparing` 同时接受 `ready` 但 `source_object_key` 为空的残缺记录。

### 3.2 `material_usage`

唯一“我的素材”关系：

```text
material 1 ── n material_usage n ── 1 user
```

同一用户与同一素材同一时间最多一个有效关系。移出“我的素材”不删除历史任务和成片。

### 3.3 `compose_template` 与 `compose_strategy`

`compose_template` 是技术资产（ADR-0021）：固定执行动作、定义参数 `schema_json`、绑定 `executor`、管理版本。`version` 整数自增，唯一约束 `(code, version)`；升级只新增版本，旧版本永久保留。

新增模板版本时先部署并验证对应执行代码，再发布该版本与 schema；数据库记录本身不代表执行能力已经就绪。CHG079 先建表，首版 `basic_cut` v1 在 M4-C4/C5 执行代码就绪后入库。

引导视频模板使用策略填写的可下载 HTTPS 地址。策略和任务快照保存该地址，不保存本地路径或自定义 FFmpeg 命令。Worker 按快照下载，限制公共网络目标、跳转与文件大小，探测实际视频后执行固定的 `guide_insert` 或 `guide_pip` FFmpeg 图。外部链接失效或内容变化会影响尚未执行或重试的任务；执行失败须明确报告，不静默换源。转链接功能由独立运营工具承担，不在本合成流程实现。`basic_cut` v1 保持原执行语义。

停用模板版本会阻止新的策略绑定和新的任务创建；已创建任务仍按快照执行。因此停用不删除模板记录，也不能移除历史任务仍需使用的执行代码。

`compose_strategy` 是业务配置，保存：

- 模板引用与模板版本（策略按 `(模板, 版本)` 绑定，模板升级不迁移旧策略）；
- 由所绑定模板版本 `schema_json` 校验的业务参数；
- `execution_mode = manual | scheduled`；仅定时模式的 `schedule` 保存当前支持的间隔或每日时间及时区；
- 持久化的优先级规则组（`match | filter`、`all | any`、白名单条件），以及单次与每日上限；
- `enabled | disabled` 策略状态，控制整条策略能否产生新任务。

策略不保存版本记录（ADR-0021）：修改策略是配置变化，直接覆盖；策略变更走审计日志。历史追溯由 `compose_task` 的不可变策略快照承担——每次创建任务时保存 `template_code`、`template_version`、`config_snapshot`，后续修改策略不改写历史任务，执行只读快照。

自动规则不拆出 `production_rule`，也不以 `schedule.enabled` 保存第二个业务开关。手动触发与 Scheduler 共用同一候选选择及任务创建实现；`filter` 对整组谓词取反，不消耗额度；`match` 消耗额度。历史任务仍按不可变快照执行。

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

1. 读取状态为 `enabled`、执行方式为 `scheduled` 且到期的 `compose_strategy`；
2. 基于业务范围选择可生产 `material`；
3. 应用系统固定资格、策略优先级规则、数量上限和已存在任务防重；
4. 用 `strategy_id + schedule_slot + material_id` 形成唯一调度键；
5. 为选中素材逐项创建 `pending compose_task`，单项失败不回滚此前成功项，并记录真实运行结果；
6. 更新策略下一次执行时间。

Scheduler 不下载文件、不调用 FFmpeg、不推进任务为 `running`。

### 4.3 Compose Worker

独立 `cmd/compose-worker`，核心循环：

```text
原子领取 pending / 可恢复任务
→ 创建租约
→ 确认输入对象可用（ready + Stat）；否则按 §5.6 自愈或等待 Cloud 文件准备任务
→ 准备隔离工作目录
→ 执行 FFprobe 输入校验
→ 执行 FFmpeg
→ FFprobe 输出校验
→ 上传对象存储临时键（Content-MD5）
→ 校验对象大小
→ 原子提交正式对象键与 composite_output
→ compose_task = success
→ 清理临时文件
```

Worker 不直接处理 HTTP，不跨模块写其他业务表；通过生产模块 Service 和 Repository 完成事务。

### 4.4 File Transfer Worker

Cloud 侧处理 `execution_scope=cloud` 的输入准备；Local Agent 处理 `execution_scope=local_agent` 的用户下载。

若 Cloud 输入准备与 Compose Worker 共进程，仍必须通过 `file_transfer_task` 状态边界协作，不允许在 Scheduler 调用栈内下载。只有观测到传输成功并把 `material.video_status` 投影为 `ready` 后，合成任务才能进入 FFmpeg 阶段。

输入准备的重试边界：平台地址解析或下载失败（`codeDetailFailed`、`codeFetchFailed`）时，同一任务内重新解析地址并再下载一次，只重试一次；`codeAddressMissing`、租约丢失、探测/暂存/提交/写 `ready` 失败不重试。上下文取消不写终态，任务留给租约到期后的重新领取。

失败写入顺序为 `FailTask`（带 worker/attempt 守卫）→ `MarkVideoFailed` → `FailDependents`；`FailTask` 未生效时不得写素材状态或等待者，避免旧进程覆盖新进程结果。`FailDependents` 失败由周期对账兜底。

用户下载在对象确认丢失且素材有 `source_url` 时，创建 `purpose=user_download` 的本地传输任务，并以 `dependency_task_id` 指向一次 Cloud 准备；下载任务保持 `pending` 直到准备成功。Cloud 不中转文件字节，只在准备完成后签发对象下载信息。

## 5. 领取、并发与恢复

### 5.1 原子领取

Repository 用单条条件更新或数据库锁保证：

```text
pending
→ running + worker_id + lease_expires_at + heartbeat_at
```

更新影响行数为 1 才算领取成功。进程内锁不能代替数据库领取。

每次领取递增任务的领取代次（`attempt_count`）；续租、进度、取消确认、失败、成片提交与重排等全部生命周期写入都条件更新到当前代次，旧执行即使复用同一 node_id 也不能覆盖新结果。

### 5.2 并发限制

配置位于 `config/scheduler`，不绑定 App 名称。至少支持：

- Worker 总并发；
- 单任务超时；
- heartbeat 间隔；
- 租约时长；
- 最大重试次数；
- 临时目录容量阈值。

总并发是跨进程的系统上限：数据库单行容量记录在领取事务内行锁校验，多个 Worker 的运行数之和不超过它；Worker 启动时校验自身配置与数据库容量一致，不一致拒绝启动。本机磁盘剩余空间低于阈值时暂停领取，恢复后自动继续。默认 Worker 并发可从 5 起步，但正式值以压测和部署资源为准。配置缺失或非法时进程拒绝启动，不以无限并发降级。

### 5.3 Heartbeat 与租约

Worker 在运行期间周期续租。恢复扫描只处理 `running` 且租约已过期的任务：租约失效不证明旧执行已停止，因此不自动重排，也不做部分输出的完成或清理判断，而是按错误码 `execution_uncertain` 记为失败事实，留给人工处置，不启动第二个 FFmpeg。

`execution_uncertain` 保留原尝试与错误事实。仅管理员核实旧 FFmpeg 已停止且未提交成片、填写核对依据后，可从任务详情发起受保护的同任务人工重试；处置事实、审计、新人工尝试及重新排队在单事务中写入。存储已存在成片、状态变化、重复处置或无法核实时，仍维持失败待处置。界面展示管理员声明及脱敏的阶段、时间、错误类别，不将声明表述为系统自动核实。

### 5.4 超时和取消

取消 `pending` 任务可直接改为 `cancelled`。取消 `running` 任务先写取消请求，Worker 向 FFmpeg 发送受控终止并等待退出；只有进程已退出、临时文件已处置后才确认 `cancelled`。

任务超时使用同一终止流程，不能只改数据库状态而遗留 FFmpeg 进程。

### 5.5 重试

- 网络抖动、临时对象存储错误及已经确认旧执行结束的 Worker 失败：允许在上限内退避重试；单凭租约到期无法确认旧执行结束，仍按 §5.3 隔离；
- 输入不存在、模板参数非法、不支持的编码器：业务失败，不自动重试；
- 修改策略或参数后重做：创建新的 `compose_task`，不覆盖旧任务；
- 所有重试保留尝试次数、上次错误和时间。

可重试任务将下一次领取时间持久化在 `compose_task.next_attempt_at`，所有 Worker 只领取到期任务；退避按尝试次数从 30 秒倍增，封顶 15 分钟。达到最大尝试次数后明确失败，不留下永远不可领取的 `pending`。

普通人工重试继续拒绝 `execution_uncertain`；管理员核对使用单独的受保护入口，不改变自动重试分类。任务和尝试记录的 API 错误文本仅返回固定类别摘要，不返回原始 FFmpeg 命令、路径、凭据或签名地址。任务 API 的参数快照对读者隐藏引导视频下载地址，数据库内的执行快照保持原值供 Worker 使用。

### 5.6 合成输入自愈

每次任务领取创建一份只属于该次领取的 `ComposeInputGate{PrepareRequested, PrepareObserved, RequestedKey}`，在本次领取的所有 `waiting_input` 轮询间复用；人工重试产生新领取，得到新的一份，因此每次领取最多自愈一次。

| 素材状态 | 闸门 | 动作 | 结果 |
| --- | --- | --- | --- |
| ready + key，Stat OK | 任意 | 预签名并下载 | 继续合成 |
| ready + key，Stat 404 | 未请求 | 请求准备 + `MarkVideoRepreparing` | `waiting_input` |
| ready + key，Stat 404 | 已请求未观测 | 不重复请求 | `waiting_input` |
| ready + key，Stat 404 | 已请求且已观测 | 一次自愈后仍缺失 | 终态 `input_missing` |
| failed / not_downloaded | 未请求 | 请求准备 + `MarkVideoPreparing` | `waiting_input` |
| failed / not_downloaded | 已请求且已观测 | 准备结束仍未产出 | 终态 `input_invalid` |
| failed / not_downloaded | 已请求未观测 | 排队或未落地 | `waiting_input`（任务超时兜底） |
| downloading | 任意 | 去重确保准备；记已观测 | `waiting_input` |
| ready + 空 key | 未请求 | 请求准备 + `MarkVideoPreparing` | `waiting_input` |
| ready + 空 key | 已请求且已观测 | 仍未补全 | 终态 `input_invalid` |
| 其他状态 / 素材不存在 | 任意 | — | 终态 `input_invalid` / `input_missing` |

需要重新准备但 `source_url` 为空时，不创建必然失败的准备任务：ready 但对象缺失立即终态 `input_missing`，其他未就绪状态立即终态 `input_invalid`。`Stat` 报非 404 存储错误按 `storage_error` 失败，不触发准备。

等待中的任务保持 `running` + 阶段 `waiting_input`，页面文案为“等待素材准备”；不改回 `pending`。

### 5.7 准备完成与下载任务插入的竞态

准备任务成功与用户下载任务插入之间存在一个时间窗：下载行插入时可能错过“把文件事实交给等待者”的一步，导致行永远停在 `pending`。两条兜底：

- 下载行插入后立即尝试 `AttachCompletedDependency`：仅当依赖已完成且 key、大小、完整性 hash 齐全时，复制事实并清空 `dependency_task_id`；
- 周期对账对同一 join 做批量版本 `ReconcileCompletedDependencies`，计为独立计数。

`file_transfer_task` 完成时写入 `source_object_key`，供上述挂接与后续消费使用。

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

采用“临时键 → 校验 → 正式键/标记”的提交方式。键按任务与领取代次隔离；已结束且结果明确的尝试若临时键删除失败，由恢复扫描重试并记录清理时间。只在明确得知数据库提交回滚时删除该代次正式键；提交结果不明确时保留正式键，避免误删已成功的成片。`execution_uncertain` 在管理员核对记录写入前不进入自动清理；核对后仅该旧尝试的隔离暂存键可进入恢复清理。数据库已成功但正式对象缺失时，成片状态必须暴露异常，不能继续进入发布。

上传完整性由 Content-MD5 证明：`Put` 发送本地算出的 MD5（`SendContentMd5`），对象存储对收到的字节自行校验，不一致即拒收（MinIO 返回 `BadDigest`；本机 Garage 实测返回 `InvalidDigest`）；随后 `Stat` 校验对象大小作为第二事实。不再把对象回读下载后比对 SHA256。该证明要求存储实现校验 Content-MD5（MinIO、阿里云 OSS 支持；Garage 需实测，若不校验只能记为大小校验）。

清理边界：合成 attempt 结束（成功、失败或取消）后删除 Cloud 本地 run 目录、素材暂存对象与成片临时对象；正式素材对象与正式成片对象保留。崩溃残留的启动清扫不在本期范围。

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
- 原素材和成片可经下载中心落到运营电脑并通过 Hash 校验；
- `ready` 但对象丢失时，合成任务触发一次重新准备并继续；准备仍失败时以明确终态结束，不循环重试，同一领取内不重复请求；
- 用户下载/预览先确认对象存在：对象丢失且有源地址时先补准备再下载，无源地址或预览时明确拒绝，不签发 404 链接；
- 等待素材的合成任务在页面显示“等待素材准备”，不显示“处理中”；
- 上传使用 Content-MD5 校验；试改一字节后上传应被存储拒绝（存储不校验时按降级记录）。

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
