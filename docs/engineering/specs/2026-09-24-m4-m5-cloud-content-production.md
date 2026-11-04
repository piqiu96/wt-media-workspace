# M4-M5 Cloud 内容生产工程设计

> 产品基线：[PRD 第五章](../../product/prd/详细文档/第五章_素材生产.md)，2026-11-05 按已确认原型回写。
> 状态：现有 Cloud 执行架构继续有效；本次批次、多组展开、接口与表结构收敛为**待实施目标设计**，不代表已经上线或完成验收。
> 决策依据：[ADR-0017](../../decisions/0017-m4-m5-cloud-owned-content-production.md)、[ADR-0023](../../decisions/0023-m3-m5-team-resources-and-production-operator.md)、[ADR-0031](../../decisions/0031-content-production-batches-and-manual-reproduction.md)。
> 本文维护模型、接口职责和工程约束；原型入口见[内容生产设计导航](../../../example/proto/content-operations/design/content-production.md)。实际迁移、提供方 OpenAPI 和代码位于 Cloud，实施步骤与验收证据进入对应 CHG，不在原型目录另存技术方案。

## 1. 设计目标

本设计为 M4 人工内容生产与 M5 自动内容生产提供同一套 Cloud 执行底座：

```text
Web / Desktop WebView
→ Cloud API
→ material / material_usage / compose_strategy / compose_task_batches / compose_task
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

唯一“我的素材”关系，同一用户与同一素材最多一个有效关系，移出不删除历史任务或成片。

独立页面归当前登录人；人工任务中的选材归任务负责人。管理角色代办须核验团队、类目、负责人及策略，不能继续用请求人代替关系所属人。从库“使用所选”才加入／恢复该负责人的关系并准备输入；公共素材库“加入我的素材”只写关系。

“我的使用”按登录人的成功成片计算，“团队使用”包含本人；负责人工作集上下文不改变此口径。普通运营只取得团队计数，使用人姓名仍限管理角色。个人关系、策略任务历史、成功产出计数分别返回，不用一个 `used` 代替。原素材本机下载继续要求当前下载人的关系，不因代办权限放开。

### 3.3 `compose_template` 与 `compose_strategy`

模板为固定执行能力，按 `(code, version)` 唯一发布，旧版本保留；先部署并验证执行器，再发布模板。模板升级不迁移已绑定策略。停用阻止新绑定和新建任务，旧任务仍执行其快照，不移除旧执行器。

模板参数定义扩展可调整声明：字段的类型、默认值、必填、范围、说明、任务内是否可调整。沿用版本化模板 Schema，不新增逐字段 CRUD 或参数表。缺失可调整声明按固定处理；服务端对覆盖键、类型、范围及最终配置校验，禁用输入框不能替代授权。引导地址仍固定且按现有读取规则脱敏。

策略保存团队、类目、有效负责人、模板版本、成片设置数组、选材规则、执行方式和额度。成片设置内有稳定 key、名称、适用平台、份数、顺序和完整参数默认值，以 JSON 随策略整体维护；不建设置表、策略版本或实时继承层。新增组取模板初始值，复制组显式复制；外层结构与组内模板参数分层校验，不能把整个数组交给执行器。

模板参数随执行器变化。引导 HTTPS 地址与插入／截取等参数同属组内模板配置；限制目标、跳转、大小并探测媒体，拒绝任意脚本或 FFmpeg 命令。快照固定参数，但不承诺外链内容永不变化。

策略状态 `enabled | disabled`，执行方式 `manual | scheduled`；仅定时计划保存间隔或每日时间及时区，不设第二个 `schedule.enabled` 开关。手动只校验每次素材上限，定时校验每次与每日上限；定时的立即执行共用每日额度但不移动下一计划时间。人工选材创建不计策略额度。

选材先应用全部排除，再按优先级选入；`all | any` 的缺失指标不补零，只有已知谓词足以定论时可短路，否则记录缺失原因。团队／类目匹配的候选按发布时间和稳定 ID 排序。策略执行跳过本策略任何任务历史；人工明确新制作不使用该永久拦截。不可保留一条覆盖所有创建来源的永久 `(strategy, material)` 唯一限制。

### 3.4 任务、批次、尝试与执行记录

`compose_task` 是 Worker 最小执行单位：一条素材、一组成片设置的一份产出。任务保存创建人、负责人、团队／类目、执行来源、素材、可空个人关系、策略及最终不可变快照，状态仍为 `pending | running | success | failed | cancelled`，保留租约、领取代次、阶段、错误与输出关联。

新增 `compose_task_batches`，仅组织同次创建任务，不替代任务执行和恢复。最小事实：ID、名称、团队／类目／负责人、策略、触发来源、创建人、整次请求幂等键及请求摘要、必要创建配置快照、创建时间。批次有实际任务才存在；受理／拒绝结果与后续任务执行结果分开。

任务扩展 `batch_id`、成片设置稳定 key／名称／平台快照、份序号，实际执行读最终参数，不读当前策略。唯一性为 `(batch_id, material_id, setting_key, copy_index)`；整次重放同键同内容返回既有结果，同键异内容拒绝。人工再次制作创建新批次及新任务；重试保留原任务、批次和配置，历史尝试不删。

触发来源区分人工创建、立即执行、定时执行，与策略执行方式、attempt 的自动／人工恢复来源分开。现有 `manual | scheduled` 编码不足以表达三种业务入口，提供方契约需扩展且同步消费者，不能仅改中文标签。

`compose_schedule_runs` 保留一次策略选材／创建结果，加可空 `batch_id`；零任务记录不建批次，人工创建不伪造成策略运行。统一分页查询，按 ID 关联批次，不按 `schedule_slot` 猜身份。

`compose_task_attempts` 保留逐次步骤与错误；将每次 attempt 至多一次的人工核实人、依据、时间并入此记录，迁移后删除独立核实表。核实是受保护的处置事件，不建审批产品；记录随执行历史返回，普通运营不取得核实依据，写入权限、两项确认、审计与恢复事务不因合表放宽。

批次进度从授权范围内全部任务聚合，结束率与成功率分开；局部任务筛选不改全批统计。阶段常量百分比不是逐帧合成进度，不能假装 0／1 已完成。

### 3.5 `composite_output`

仅保存校验通过的成功产出，继承任务负责人；关联素材、可空个人关系、任务与策略创建时快照。补齐可供显示的视频文件名、时长、宽高、大小、Hash 与对象键；未知信息不推算，名称、参数和平台不能从当前策略反推。

“成片批次”按 `material_id` 聚合实际成片，**不建表**；先授权，再聚合、计数、排序和分页。查询通过精确 `material_id`／`batch_id` 关联，不能用混合搜索替代。

视频可用性、当前用户与设备的传输状态、逐平台发布安排分开投影。不存在成片全局 `downloaded` 布尔值，历史下载不证明当前文件仍在。对象访问签名前执行 `Stat`，错误不回写原合成任务为失败。发布已安排／已发布必须来自发布领域真实任务与结果，现有单个全局发布字段不能充当逐平台依据；本轮无归档产品入口。

### 3.6 `file_transfer_task`

统一承载原素材与成片传输：

| 维度 | 取值 |
| --- | --- |
| `asset_type` | `material`、`composite_output` |
| `purpose` | `compose_input_prepare`、`user_download` |
| `execution_scope` | `cloud`、`local_agent` |
| `status` | `pending`、`running`、`success`、`failed`、`cancelled` |

进度字段包括总字节、完成字节、瞬时/平滑速度、预计剩余秒数、尝试次数和错误。正式业务表不保存本机绝对路径；本地路径由 Local Agent / Desktop 在本机可信存储中管理，Cloud 只保存请求用户、领取审计、文件名和完成事实。

## 4. 进程模型

### 4.1 HTTP Server

`cmd/server` 负责：

- 权限与参数校验；
- `material_usage`、`compose_strategy`、`compose_task`、`file_transfer_task` 查询和命令；
- 返回任务事实和签发受控下载信息。

HTTP 请求创建任务后立即返回，不等待下载或 FFmpeg 完成。

### 4.2 Compose Scheduler 与统一创建服务

独立 Scheduler 只读取到期启用策略并调用生产创建服务，不下载、不调用 FFmpeg。到期调度、立即执行与人工创建共享配置展开和快照校验，但分别执行其选材、防重和额度规则，不能复用同一永久素材锁。

创建服务：核验权限与负责人 → 校验输入／规则 → 按素材确定受理集合 → 按组和份数展开 → 幂等建立批次／任务／结果。策略与每日额度在事务内同步校验并扣计实际受理素材，不能按展开后的任务数计。单项创建失败要说明实际产出与计额结果，不把部分创建标为全成功。定时执行使用稳定周期键；展开唯一键另含组与份序号。

立即执行预览是只读服务，与真实命令共用候选判定：先检查同策略未完成任务，再返回选材依据、实际读数、数量及额度。不创建个人关系、准备任务、预览表或长时间额度锁。确认时重新核验未完成状态、配置、素材与额度；实质变化返回新预览供确认，不静默换素材／配置。创建中的同策略并发由事务和幂等保护；不将此入口规则擅自扩展为定时重叠政策。

历史数据没有批次时保持无批次关联，可追原任务，不按名称、时间或虚构“历史批次 ID”补造。尚未上线可重建开发数据库；保留的开发数据须有明确迁移，删除建表代码不等于已迁移。

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

总并发是跨进程的系统上限。短期继续用 `compose_worker_capacity` 的单行锁，在同一事务内校验容量、统计运行数、领取任务及建立 attempt。当前初始容量为 2，正式值以部署资源与配置校验为准；配置缺失、非法或与数据库不一致时拒绝启动，不以无限并发降级。磁盘低于阈值暂停领取。

预留内部并发准入边界，覆盖领取及其生命周期，不只包装 `max_running` 的读取；不新增 HTTP 配置接口、通用锁平台或 Redis 空实现。未来 Redis 适配须原子申请唯一名额令牌、续期、按持有者释放；数据库领取失败补偿释放，任务代次守卫与提交仍在 MySQL。TTL 过期不证明旧 FFmpeg 已停止，Redis 不可用时停止新领取，不自动切回另一套同时生效的控制。

Redis 服务部署后仍需实现适配、验证崩溃／过期／数据丢失和切换全部 Worker，不能只配地址即替换。短期停 Worker 切换，避免双实现并行；完成替换后再删除容量表。

### 5.3 Heartbeat 与租约

Worker 在运行期间周期续租。恢复扫描只处理 `running` 且租约已过期的任务：租约失效不证明旧执行已停止，因此不自动重排，也不做部分输出的完成或清理判断，而是按错误码 `execution_uncertain` 记为失败事实，留给人工处置，不启动第二个 FFmpeg。

`execution_uncertain` 保留原尝试与错误事实。同团队高级运营或管理员核实旧 FFmpeg 已停止且未提交成片、填写核对依据后，可从任务详情发起受保护的同任务人工重试；原 attempt 的核实字段、审计及重新排队在单事务中写入，同时建立下一次待执行记录；其 `started_at` 仅在后续真实领取时填写，未领取不计为已执行。存储已存在成片、状态变化、重复处置或无法核实时，仍维持失败待处置。普通运营在可见范围内仍不能提交核对，跨团队高级运营按不可见处理。界面展示核对人声明及脱敏的阶段、时间、错误类别，不将声明表述为系统自动核实。

### 5.4 超时和取消

取消 `pending` 任务可直接改为 `cancelled`。取消 `running` 任务先写取消请求，Worker 向 FFmpeg 发送受控终止并等待退出；只有进程已退出、临时文件已处置后才确认 `cancelled`。

任务超时使用同一终止流程，不能只改数据库状态而遗留 FFmpeg 进程。

### 5.5 重试

- 网络抖动、临时对象存储错误及已经确认旧执行结束的 Worker 失败：允许在上限内退避重试；单凭租约到期无法确认旧执行结束，仍按 §5.3 隔离；
- 输入不存在、模板参数非法、不支持的编码器：业务失败，不自动重试；
- 修改策略或参数后重做：创建新的 `compose_task`，不覆盖旧任务；
- 所有重试保留尝试次数、上次错误和时间。普通人工重试沿用当前完整 3 次自动容错配额，即 `max_attempts = attempt_count + 3`，编号不回退；原错误保留在旧 attempt 中，当前任务摘要按重排规则更新。

可重试任务将下一次领取时间持久化在 `compose_task.next_attempt_at`，所有 Worker 只领取到期任务；退避按尝试次数从 30 秒倍增，封顶 15 分钟。达到最大尝试次数后明确失败，不留下永远不可领取的 `pending`。

普通人工重试继续拒绝 `execution_uncertain`；高级运营／管理员的人工核对使用单独的受保护入口，不改变自动重试分类。任务和尝试记录的 API 错误文本仅返回固定类别摘要，不返回原始 FFmpeg 命令、路径、凭据或签名地址。任务 API 的参数快照对读者隐藏引导视频下载地址，数据库内的执行快照保持原值供 Worker 使用。

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

采用“临时键 → 校验 → 正式键/标记”的提交方式。键按任务与领取代次隔离；已结束且结果明确的尝试若临时键删除失败，由恢复扫描重试并记录清理时间。只在明确得知数据库提交回滚时删除该代次正式键；提交结果不明确时保留正式键，避免误删已成功的成片。`execution_uncertain` 在有权角色的核对记录写入前不进入自动清理；核对后仅该旧尝试的隔离暂存键可进入恢复清理。数据库已成功但正式对象缺失时，成片状态必须暴露异常，不能继续进入发布。

上传完整性由 Content-MD5 证明：`Put` 发送本地算出的 MD5（`SendContentMd5`），对象存储对收到的字节自行校验，不一致即拒收（MinIO 返回 `BadDigest`；本机 Garage 实测返回 `InvalidDigest`）；随后 `Stat` 校验对象大小作为第二事实。不再把对象回读下载后比对 SHA256。该证明要求存储实现校验 Content-MD5（MinIO、阿里云 OSS 支持；Garage 需实测，若不校验只能记为大小校验）。

清理边界：合成 attempt 结束（成功、失败或取消）后删除 Cloud 本地 run 目录、素材暂存对象与成片临时对象；正式素材对象与正式成片对象保留。崩溃残留的启动清扫不在本期范围。

## 7. API 与 Contract

Cloud 为正式提供方，完整前缀 **`/api/v1` 保留**；本文定义目标职责，最终 Schema、路径参数和错误在 Cloud OpenAPI 及对应 CHG 落实，不在 Workspace 生成第二份提供方合同。列表统一服务端分页、总数、稳定排序、范围／日期／权限过滤，取消最多 200 条取全后前端拼接的方案。

### 7.1 目标接口清单

以下为本轮收敛建议：保留／扩展现有 30 个、新增 6 个，共 **36 个 production 接口**，尚未实施。关联的 7 个文件传输接口另计，发布领域不计入。

| 方法与完整路径 | 用途 |
| --- | --- |
| `GET /api/v1/materials` | 团队素材分页及使用投影；可带策略上下文返回该策略任务历史 |
| `GET /api/v1/materials/:material_id` | 素材详情 |
| `GET /api/v1/materials/:material_id/video-url` | 核验后的视频访问 |
| `POST /api/v1/materials/:material_id/usages` | 加入或恢复个人素材；任务选材的受权代办需显式校验目标负责人 |
| `GET /api/v1/my-materials` | 个人工作集分页；代办上下文不扩成通用跨人读取 |
| `DELETE /api/v1/material-usages/:usage_id` | 移出关系 |
| `POST /api/v1/material-usages/:usage_id/restore` | 恢复关系 |
| `POST /api/v1/materials/:material_id/downloads` | 当前用户原素材下载 |
| `GET /api/v1/compose-templates` | 模板目录、指定绑定版本说明与参数定义，包括只读历史版本 |
| `GET /api/v1/compose-operators` | 按团队与类目返回有效负责人候选 |
| `GET /api/v1/compose-strategies` | 策略分页查询 |
| `POST /api/v1/compose-strategies` | 新建策略及多组成片设置 |
| `GET /api/v1/compose-strategies/:strategy_id` | 当前策略详情 |
| `PUT /api/v1/compose-strategies/:strategy_id` | 校验不可变归属后更新配置 |
| `POST /api/v1/compose-strategies/:strategy_id/copy` | 复制为新策略 |
| `PATCH /api/v1/compose-strategies/:strategy_id/status` | 启停策略 |
| `POST /api/v1/compose-strategies/next-run-preview` | 计算下一计划时间，不能充当选材预览 |
| `POST /api/v1/compose-strategies/:strategy_id/execution-preview` | 新增：只读选材、未完成任务检查、预计产量及依据 |
| `POST /api/v1/compose-strategies/:strategy_id/run-now` | 确认后真实创建，重新校验预览与并发 |
| `GET /api/v1/compose-strategies/:strategy_id/runs` | 统一分页／时间／触发筛选的执行记录，返回可空真实批次 ID |
| `GET /api/v1/compose-task-batches` | 新增：人工及策略任务的统一批次分页 |
| `GET /api/v1/compose-task-batches/:batch_id` | 新增：批次主体与全批统计 |
| `GET /api/v1/compose-tasks` | 任务分页，支持精确 batch_id |
| `POST /api/v1/compose-tasks` | 人工创建／再次制作；返回批次及逐项受理结果，重放幂等 |
| `GET /api/v1/compose-tasks/:task_id` | 任务主体、快照与允许动作 |
| `GET /api/v1/compose-tasks/:task_id/attempts` | 分次执行记录；核实事件对受权角色附带依据 |
| `POST /api/v1/compose-tasks/:task_id/retry` | 重试原任务 |
| `POST /api/v1/compose-tasks/:task_id/cancel` | 取消排队任务或请求停止执行 |
| `POST /api/v1/compose-tasks/:task_id/uncertain-review` | 保留：受保护的核实并恢复，不混入普通重试 |
| `POST /api/v1/compose-tasks/batch-retry` | 新增：受权整批或明确所选任务重试 |
| `POST /api/v1/compose-tasks/batch-cancel` | 新增：受权整批或明确所选任务取消 |
| `GET /api/v1/compose-output-materials` | 新增：先授权、按素材 ID 聚合成片并分页 |
| `GET /api/v1/compose-outputs` | 成片分页及素材／批次精确过滤 |
| `GET /api/v1/compose-outputs/:output_id` | 成片与创建时来源、视频及真实发布关联 |
| `GET /api/v1/compose-outputs/:output_id/video-url` | 先核验对象，再签发访问地址 |
| `POST /api/v1/compose-outputs/:output_id/downloads` | 当前用户下载到本机 |

模板读取应精确匹配绑定版本，不因目录只列启用版本而无法查看历史。我的素材、公共素材可复用查询实现，但保留不同业务语义。访问视频与创建本机下载分别承担打开／传输，不能机械合并。按钮能力和原因随现有读取返回，不为每个按钮新增状态查询接口。

### 7.2 收敛的旧接口

当前源码核对为 35 个 production 接口；建议移除以下 5 个独立入口，并同步调用方及合同。不能先删路由再等消费者适配。

| 当前完整路径 | 目标承接 |
| --- | --- |
| `GET /api/v1/compose-strategies/:strategy_id/runs/history` | 合并进分页 runs；最近记录用较小 page_size |
| `GET /api/v1/compose-strategies/:strategy_id/runs/tasks` | runs 返回 batch_id，复用批次详情与任务查询 |
| `GET /api/v1/compose-strategies/:strategy_id/material-states` | 素材查询的可选策略上下文；不可冒充我的使用／团队使用 |
| `GET /api/v1/compose-tasks/:task_id/uncertain-review` | 并入 attempts 的受权处置事件，无需独立核实查询页 |
| `POST /api/v1/compose-outputs/:output_id/archive` | 已确认产品无归档入口，本轮不保留 |

保留独立的核实**写**入口是必要的安全职责：管理员或同团队高级运营，且仍为结果不明确的旧尝试、无已提交成片、两项确认成立、依据有效时才能恢复；合表和合并读取不放宽任一条件。读取依据继续按原有权限裁剪。

### 7.3 批量与跨端合同

批量重试／取消的批次范围与所选 ID 必须二选一；服务端固定并重新核验实际操作集合，逐项返回受理、跳过及失败。运行中取消返回请求已受理，不提前返回已取消；不因前端只加载一页漏掉整批剩余任务。再制作复用创建接口，无独立 regenerate API 或另一套批次写 API。

Cloud Web 与 Desktop 共用业务源码、同一能力投影；Local Agent 只领取本机传输任务并上报进度／Hash，不取得合成参数和 FFmpeg 控制权。关联接口维持：

- `GET /api/v1/file-transfer-tasks`
- `POST /api/v1/file-transfer-tasks/:task_id/cancel`
- `POST /api/v1/file-transfer-tasks/:task_id/hide`
- `POST /api/v1/cloud-agent/file-transfer-tasks/claim`
- `POST /api/v1/cloud-agent/file-transfer-tasks/:task_id/heartbeat`
- `POST /api/v1/cloud-agent/file-transfer-tasks/:task_id/progress`
- `POST /api/v1/cloud-agent/file-transfer-tasks/:task_id/complete`

## 8. 安全与可观测性

- 对象存储凭据只在 Cloud 受控配置中；Local Agent 使用短时、最小范围下载授权；
- 日志包含 `trace_id`、`request_id`、`module`、任务 ID 和 Worker ID，不记录凭据或完整签名 URL；
- 生产指标至少包括队列长度、领取延迟、执行时长、成功率、重试率、超时数、FFmpeg 退出码分布、临时磁盘与对象存储失败；
- 审计记录策略启停、人工创建/取消/重试和下载任务创建；
- M3–M5 正式授权按 ADR-0023：团队公共 `material` 不按个人或负责类目硬限制；普通运营任务、成片固定本人，高级运营仅本团队全部类目，管理员跨团队；个人工作集按 §3.2 区分独立页面与受权代选材，本机下载仍按当前用户。审计保留策略、任务和下载操作。

## 9. 配置

运行时仍只读 `./config`，发布时由 `config_online` 替换产物中的 `config`。沿用 Cloud 当前 Loader 的 scheduler、存储和媒体配置，不在此虚定新 YAML 文件名；实际配置格式与键名在实施 CHG 核对。不把配置放进 `internal`，不创建第二份 Worker 容量来源，不用环境变量绕过只读 Config。

来源平台当前仅抖音，成片／发布目标为 B站、百度、小红书，分开枚举。当前账号提供方枚举与目标不完全一致，须在账号／发布领域核对真实支持后扩展合同；不能把原型候选视为已经具备发布能力。

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

### 本次产品基线的增量验证

- 多组／多份／多平台正确展开，固定参数越权拒绝；最终快照不随策略修改漂移。
- 重复提交、同键异内容、并发立即执行、预览过期、零任务无批次；定时周期幂等与按素材计额。
- 人工再次制作与原任务重试语义独立；代办、批量权限和部分成功，取消请求不假终态。
- 全批进度不受局部筛选影响；成片聚合跨批次但不跨授权；大于 200 条的数据正确分页、筛选及统计。
- 人工核实合并后仍校验旧执行／成片事实、保留历史，旧 Worker 失去租约后不能提交。
- 来源仅抖音与目标平台分离；共享页面与正式合同一致，无虚假下载、合成或发布成功。

## 11. 明确不做

- Local Agent / Cloud Agent 视频合成；
- 同步 HTTP 等待视频生成；
- MQ、微服务、动态 Worker 注册中心；
- 可视化流程编排、任意脚本或策略插件；
- 为原素材与成片分别新建下载任务表；
- 重新命名 `material_usage` 或复制“我的素材”关系；
- 在 M4 自动创建定时生产任务；自动调度属于 M5。

## 12. 数据库现状与目标收敛

### 12.1 表清单

2026-11-05 源码核对有 **12 张关联业务表**，不含 users／团队／类目／账号／审计等共享表。本次新增统一任务批次、将核实字段合入执行记录后删除独立核实表，MySQL 阶段目标仍为 **12 张**；没有执行迁移或删表。

| 当前表 | 作用 | 本轮目标 |
| --- | --- | --- |
| `source_contents` | 挖掘来源内容 | 沿用，上游事实 |
| `materials` | 团队正式素材与输入准备 | 补足指标缺失／有效性语义，不能缺失补零 |
| `material_usages` | 个人素材关系 | 沿用，代办明确关系所属人 |
| `compose_templates` | 固定模板版本、Schema 与执行器 | 扩展任务内可调整声明 |
| `compose_strategies` | 业务策略、计划、条件及参数 | 成片设置 JSON 数组、正确选材及额度语义 |
| `compose_tasks` | 单份产出的任务与租约 | 增加批次、组及份序号、最终快照 |
| `composite_outputs` | 成功成片与存储事实 | 补视频元数据、稳定名称与追溯投影 |
| `compose_schedule_runs` | 每次策略选材与创建结果 | 保留，新增可空 batch_id |
| `compose_task_attempts` | 每次真实尝试、步骤与错误 | 保留，接纳核实字段 |
| `compose_uncertain_reviews` | 结果不确定时的人工核实 | 并入原 attempt 后删除 |
| `compose_worker_capacity` | MySQL 全局并发准入 | 当前保留，未来适配替换后再删 |
| `file_transfer_tasks` | Cloud 输入准备及本机下载 | 复用，不建另一套文件任务 |
| `compose_task_batches`（新增） | 人工、立即、定时创建的统一集合 | 真实批次身份与提交幂等，不保存冗余实时状态 |

成片设置、按素材聚合的成片批次、使用统计、预览和批次进度均不建表。发布表归发布领域，不借本轮内容生产界面扩出一整套发布数据库。

### 12.2 四张辅助表的当前字段与必要性

以下是当前模型字段，不是新增 migration DDL；主外键、类型、索引、删除顺序须在实施时按 Cloud migration 定向核实。

| 表 | 当前字段 | 事实与取舍 |
| --- | --- | --- |
| `compose_schedule_runs` | `run_key`、`strategy_id`、`trigger_type`、`schedule_slot`、`candidate_count`、`created_count`、`skipped_json`、`created_at` | run_key 标识执行，周期／触发说明来源，候选／创建／跳过解释为何有或无任务；不是最终任务执行结果，不能替代统一任务批次 |
| `compose_task_attempts` | `id`、`task_id`、`attempt`、`source`、`started_at`、`finished_at`、`outcome`、`stage`、`error_code`、`error_message`、`steps_json`、`staging_cleaned_at`、`created_at`、`updated_at` | 保存执行次数、时间、过程、结果与暂存清理，任务重试不能覆盖旧事实；保留 |
| `compose_uncertain_reviews` | `id`、`task_id`、`attempt`、`actor_user_id`、`evidence`、`created_at` | 每个任务尝试最多一条核实；没有独立生命周期，合到原 attempt 更简单；保留人、依据、时间及审计，不保留独立表 |
| `compose_worker_capacity` | `id`（固定 1）、`max_running`、`updated_at` | 容量行锁协调多个 Worker；现阶段有实际原子领取作用，不能直接删掉后只靠进程内计数 |

核实写入仍校验“旧执行已停止”“无已提交成片”两项确认，依据 20–2000 字且禁止 URL；两项确认当前是服务端提交门禁，不是两列已存布尔值。合表后清理任务必须读取原尝试核实事实，不能丢掉安全前提。

### 12.3 实施前必须闭合的差距

- 补齐统一批次、按组展开及批次／组／份唯一键，去除人工新制作的永久对锁；同次重放与再次制作分别验证。
- 修正规则先排除再选入、缺失指标、手动隐藏每日额度及按素材计额；预览与提交共用判定并处理确认期间变化。
- 所有列表服务端分页／统计，按授权先过滤再聚合；修复最多 200 条截断和成片无分页，不能以浏览器全量拼接落地。
- 受权代选材须在创建与关系写入中一致；任务读取、成片追溯从最终快照取值，不读取当前策略配置冒充历史。
- 统一实际策略枚举与提供方 Schema 的 `enabled/disabled` 等差异，增加三种触发来源；平台来源／去向与账号合同分别校验。
- 文件访问先核验实际对象，补实际文件名与宽高；设备下载状态由本机核验，不以历史成功补造。
- 核实合表与删除旧 GET 同步仓储、恢复事务、清理器、审计及调用方；保留原 POST 权限和不可重复处置守卫。

落地时由 CHG 明确迁移／重建、契约生成、消费者更新、验证证据及交付状态。现有架构与既有验收不证明上述新能力已实现，原型内的演示步骤与样例数据也不属于真实运行证据。
