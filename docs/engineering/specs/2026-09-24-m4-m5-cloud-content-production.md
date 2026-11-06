# M4-M5 Cloud 内容生产工程设计

> 产品基线：[PRD 第五章](../../product/prd/详细文档/第五章_素材生产.md)，2026-11-05 按已确认原型回写。
> 状态：当前 Cloud 内容生产实现，覆盖人工、立即、定时创建、多组展开、任务恢复及成片管理。代码实施不代表生产环境已上线；次日人工与原生 Desktop 签收以 Delivery 记录为准。
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

`compose_task_batches` 仅组织同次创建任务，不替代任务执行和恢复。最小事实：ID、名称、团队／类目／负责人、策略、触发来源、创建人、整次请求幂等键及请求摘要、必要创建配置快照、创建时间。批次有实际任务才存在；受理／拒绝结果与后续任务执行结果分开。

任务扩展 `batch_id`、成片设置稳定 key／名称／平台快照、份序号，实际执行读最终参数，不读当前策略。唯一性为 `(batch_id, material_id, setting_key, copy_index)`；整次重放同键同内容返回既有结果，同键异内容拒绝。人工再次制作创建新批次及新任务；重试保留原任务、批次和配置，历史尝试不删。

触发来源区分人工创建、立即执行、定时执行，与策略执行方式、attempt 的自动／人工恢复来源分开。提供方契约与共享页面统一使用 `manual | immediate | scheduled`，分别表示人工创建、立即执行和定时执行；与策略 `manual | scheduled` 两种执行方式分开。

`compose_schedule_runs` 保存一次策略选材／创建结果及可空 `batch_id`；零任务记录不建批次，人工创建不伪造成策略运行。统一分页查询，按 ID 关联批次，不按 `schedule_slot` 猜身份。

`compose_task_attempts` 保留逐次步骤与错误；每次 attempt 至多一次的人工核实人、依据、时间已并入此记录，独立核实表已迁移删除。核实是受保护的处置事件，不建审批产品；记录随执行历史返回，普通运营不取得核实依据，写入权限、两项确认、审计与恢复事务不因合表放宽。

批次进度从授权范围内全部任务聚合，结束率与成功率分开；局部任务筛选不改全批统计。阶段常量百分比不是逐帧合成进度，不能假装 0／1 已完成。

### 3.5 `composite_output`

仅保存校验通过的成功产出，继承任务负责人；关联素材、可空个人关系、任务与策略创建时快照。补齐可供显示的视频文件名、时长、宽高、大小、Hash 与对象键；未知信息不推算，名称、参数和平台不能从当前策略反推。

`composite_outputs.name` 与 `file_name` 为资产字段，在成功提交事务内写入；名称在首次成功提交时由素材标题与已冻结任务组名生成，此后不随素材改名变化，视频文件名经过路径／控制字符清理并保留实际扩展名。旧记录未知时保持空值，不推造历史。`media_json` 只存真实输出探测的时长、宽高等媒体参数，大小与 Hash 沿用上传校验事实。任务、批次、组、平台及模板参数通过已冻结任务关联读取，不重复建立资产配置表。

再次制作复用 `POST /compose-tasks`，可选 `source_output_id` 与普通 `material_ids/items/config_override` 互斥。服务器从受权源成片与原任务读取原素材、原组稳定 key／名称／平台、原模板版本及最终参数，固定只生成该组一份；客户端不能提交替代的固定参数。仅原版本 Schema 的开放参数可覆盖。原策略须仍启用、原负责人仍有效并匹配策略与原团队／类目，且原模板版本已部署可用；任一缺失明确拒绝，不切换到当前默认组或新负责人。历史无完整快照或无负责人时引导普通新建，不猜补。源成片文件丢失不妨碍利用可获取原素材再制作。

`source_output_id` 纳入整次请求摘要；重放优先返回已保存受理结果，新命令才重新核验当前授权、原负责人关系与输入可获取性。批次保留源成片／原任务关联供追溯，不建立第二套创建接口或新表。

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

进度字段包括总字节、完成字节、瞬时/平滑速度、预计剩余秒数、尝试次数和错误。正式业务表不保存本机绝对路径；Local Agent 按租约 `category_name` 命名文件，字段缺失时兼容旧 `game_name`；本地路径由 Local Agent / Desktop 在本机可信存储中管理，Cloud 只保存请求用户、领取审计、文件名和完成事实。

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

下载按用户、资产与传输代次去重，仅复用仍为 `pending/running` 的请求。终态后的显式下载创建下一代，旧成功事实不改写，也不能证明当前设备仍有文件；不增加设备归属、强制下载接口或本机路径列。创建下载的事务使用 READ COMMITTED，唯一去重键仲裁同代并发，冲突请求可读到已提交的同一任务；其他业务事务隔离级别不变。

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

总并发是跨进程的系统上限。当前使用 `compose_worker_capacity` 的单行锁，在同一事务内校验容量、统计占用、领取任务及建立 attempt。占用包括 `running`，以及当前尝试尚未核实的 `execution_uncertain`；尝试记录缺失时保守占用，旧尝试的核实不能释放新尝试。当前初始容量为 2，正式值以部署资源与配置校验为准；配置缺失、非法或与数据库不一致时拒绝启动，不以无限并发降级。磁盘低于阈值暂停领取。

现有 Repository 生命周期接口覆盖领取、续租、结束与恢复，是未来并发实现的内部替换边界，不另建只包装 `max_running` 读取的接口；不新增 HTTP 配置接口、通用锁平台或 Redis 空实现。未来 Redis 适配须原子申请唯一名额令牌、续期、按持有者释放；数据库领取失败补偿释放，任务代次守卫与提交仍在 MySQL。TTL 过期不证明旧 FFmpeg 已停止，Redis 不可用时停止新领取，不自动切回另一套同时生效的控制。

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
- 启动时检查可执行文件、配置版本及必需编码器；配置 SHA256 pin 时同时核对 Hash，开发配置可不设 pin；
- 当前启动器不单独探测 CPU 架构或 Filter，部署制品须为对应架构并通过实际模板执行验证；
- 版本不兼容时 Worker 健康检查失败，不领取任务；
- 版本、编译信息与许可证进入发布清单。

### 6.2 临时目录

每个任务使用独立目录，目录名只使用内部任务 ID。输入、输出和日志文件名不得直接拼接用户标题。清理规则只删除本任务可再生临时文件，不触碰对象存储正式键或其他任务目录。

### 6.3 对象存储提交

采用“临时键 → 校验 → 正式键/标记”的提交方式。键按任务与领取代次隔离；已结束且结果明确的尝试若临时键删除失败，由恢复扫描重试并记录清理时间。只在明确得知数据库提交回滚时删除该代次正式键；提交结果不明确时保留正式键，避免误删已成功的成片。`execution_uncertain` 在有权角色的核对记录写入前不进入自动清理；核对后仅该旧尝试的隔离暂存键可进入恢复清理。数据库已成功但正式对象缺失时，成片状态必须暴露异常，不能继续进入发布。

上传完整性由 Content-MD5 证明：`Put` 发送本地算出的 MD5（`SendContentMd5`），对象存储对收到的字节自行校验，不一致即拒收（MinIO 返回 `BadDigest`；本机 Garage 实测返回 `InvalidDigest`）；随后 `Stat` 校验对象大小作为第二事实。不再把对象回读下载后比对 SHA256。该证明要求存储实现校验 Content-MD5（MinIO、阿里云 OSS 支持；Garage 需实测，若不校验只能记为大小校验）。

清理边界：合成 attempt 结束（成功、失败或取消）后删除 Cloud 本地 run 目录、素材暂存对象与成片临时对象；正式素材对象与正式成片对象保留。崩溃残留的启动清扫不在本期范围。

## 7. API 与 Contract

Cloud 为正式提供方，完整前缀 **`/api/v1` 保留**。最终 Schema、路径参数和错误由 Cloud 的 `contracts/` 定义，Workspace 只维护映射与职责。业务列表使用服务端分页、总数、稳定排序及受权过滤；模板／负责人候选按自身目录合同返回，不冒充全量业务列表。策略分页默认20、最大100；策略页、任务筛选和新建选择器共享远程分页搜索，已选 ID 单独读取完整详情。

### 7.1 当前接口清单

当前有 **36 个 production 接口**；关联的 7 个文件传输接口另计，发布领域不计入。

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
| `POST /api/v1/compose-strategies/:strategy_id/execution-preview` | 只读选材、未完成任务检查、预计产量及依据 |
| `POST /api/v1/compose-strategies/:strategy_id/run-now` | 确认后真实创建，重新校验预览与并发 |
| `GET /api/v1/compose-strategies/:strategy_id/runs` | 统一分页／时间／触发筛选的执行记录，返回可空真实批次 ID |
| `GET /api/v1/compose-task-batches` | 人工及策略任务的统一批次分页 |
| `GET /api/v1/compose-task-batches/:batch_id` | 批次主体与全批统计 |
| `GET /api/v1/compose-tasks` | 任务分页，支持精确 batch_id |
| `POST /api/v1/compose-tasks` | 人工创建／再次制作；返回批次及逐项受理结果，重放幂等 |
| `GET /api/v1/compose-tasks/:task_id` | 任务主体、快照与允许动作 |
| `GET /api/v1/compose-tasks/:task_id/attempts` | 分次执行记录；核实事件对受权角色附带依据 |
| `POST /api/v1/compose-tasks/:task_id/retry` | 重试原任务 |
| `POST /api/v1/compose-tasks/:task_id/cancel` | 取消排队任务或请求停止执行 |
| `POST /api/v1/compose-tasks/:task_id/uncertain-review` | 受保护的核实并恢复，不混入普通重试 |
| `POST /api/v1/compose-tasks/batch-retry` | 受权整批或明确所选任务重试 |
| `POST /api/v1/compose-tasks/batch-cancel` | 受权整批或明确所选任务取消 |
| `GET /api/v1/compose-output-materials` | 先授权、按素材 ID 聚合成片并分页 |
| `GET /api/v1/compose-outputs` | 成片分页及素材／批次精确过滤 |
| `GET /api/v1/compose-outputs/:output_id` | 成片与创建时来源、视频及真实发布关联 |
| `GET /api/v1/compose-outputs/:output_id/video-url` | 先核验对象，再签发访问地址 |
| `POST /api/v1/compose-outputs/:output_id/downloads` | 当前用户下载到本机 |

模板读取应精确匹配绑定版本，不因目录只列启用版本而无法查看历史。我的素材、公共素材可复用查询实现，但保留不同业务语义。访问视频与创建本机下载分别承担打开／传输，不能机械合并。按钮能力和原因随现有读取返回，不为每个按钮新增状态查询接口。

### 7.2 读取与受保护处置

策略执行记录统一由分页 `runs` 返回，带可空真实批次 ID；任务步骤与核实事件统一由 `attempts` 返回。没有独立的 runs/history、runs/tasks、material-states 或 uncertain-review GET，也没有成片归档命令。素材的策略历史通过素材查询上下文读取，与“我的使用／团队使用”分别表达。

核实**写**入口独立保留：管理员或同团队高级运营，且仍为结果不明确的旧尝试、无已提交成片、两项确认成立、依据有效时才能恢复。合并读取及合表不放宽条件，普通运营不取得核实依据。

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

- 对象存储凭据只在 Cloud 受控配置中；Local Agent 使用受会话有效期约束的最小范围下载授权；
- 日志包含 `trace_id`、`request_id`、`module`、任务 ID 和 Worker ID，不记录凭据或完整签名 URL；
- 生产指标至少包括队列长度、领取延迟、执行时长、成功率、重试率、超时数、FFmpeg 退出码分布、临时磁盘与对象存储失败；
- 审计记录策略启停、人工创建/取消/重试和下载任务创建；
- M3–M5 正式授权按 ADR-0023：团队公共 `material` 不按个人或负责类目硬限制；普通运营任务、成片固定本人，高级运营仅本团队全部类目，管理员跨团队；个人工作集按 §3.2 区分独立页面与受权代选材，本机下载仍按当前用户。审计保留策略、任务和下载操作。

## 9. 配置与本地运行

Cloud 从 runtime home 下的 `config/` 加载配置；发布配置由既有打包流程提供。`config/scheduler/compose.toml` 管理 Compose Worker 节点、并发、磁盘阈值、租约、心跳、超时与轮询；`config/scheduler/scheduler.toml` 管理调度周期。媒体二进制和对象存储使用现有媒体／存储配置，不创建第二套容量来源。

Workspace `bin/control.sh` / `scripts/dev/local_env.py` 是统一环境入口：管理 Cloud、文件准备 Worker、Compose Worker、Compose Scheduler、Web、Desktop 开发页面及 Agent，使用固定开发数据库；Scheduler 纳入 PID、停止与新鲜度检查，发现挖掘的 Discovery Scheduler 仍不自动启动。Agent 使用正式 `wt_media_agent.local_main`，并通过受支持配置启用文件传输循环；仅启动 Local API 健康服务不能代替执行器。正式 Desktop 使用其自身 Sidecar 与凭证交接。

来源平台仅抖音；成片目标为 B站、百度、小红书。目标枚举不等于已具备发布执行能力，发布任务、账号与结果继续由发布领域承接。

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

## 12. 当前数据库模型

### 12.1 表清单

内容生产关联 **12 张业务表**，不含用户、团队、类目、账号及审计等共享表。

| 表 | 作用 |
| --- | --- |
| `source_contents` | 上游来源内容与原始指标 |
| `materials` | 团队正式素材、准备状态和输入对象事实 |
| `material_usages` | 个人素材工作集；移出保留制作历史 |
| `compose_templates` | 按 code/version 发布的固定能力和参数 Schema |
| `compose_strategies` | 负责人、模板、成片设置 JSON、规则、计划和额度 |
| `compose_task_batches` | 一次真实创建命令的身份、幂等摘要和必要快照 |
| `compose_tasks` | 单素材、单组、单份的任务与最终参数、领取租约 |
| `composite_outputs` | 校验通过的成片、名称、媒体与对象事实 |
| `compose_schedule_runs` | 一次策略选材及创建结果，零任务也保留原因 |
| `compose_task_attempts` | 逐次执行步骤、错误、核实和暂存清理记录 |
| `compose_worker_capacity` | MySQL 跨进程并发准入的单行锁 |
| `file_transfer_tasks` | 统一 Cloud 输入准备与 Local Agent 本机下载 |

成片设置、按素材聚合的成片批次、使用统计、预览和批次进度均不建表。`compose_uncertain_reviews` 已合并删除；不新建 Redis 占位表或发布领域数据表。

### 12.2 辅助事实字段与必要性

| 表 | 实际字段 | 保留原因 |
| --- | --- | --- |
| `compose_schedule_runs` | `run_key`（主键）、`compose_strategy_id`、`trigger_type`、`schedule_slot`、`candidate_count`、`created_count`、`skipped_json`、`created_at`、可空 `batch_id`、`request_hash` | 解释策略为什么创建或没有创建任务；不是任务最终结果，也不覆盖人工批次 |
| `compose_task_attempts` | `id`、`task_id`、`attempt`、`source`、`started_at`、`finished_at`、`outcome`、`stage`、`error_code`、`error_message`、`steps_json`、`staging_cleaned_at`、`created_at`、`updated_at`；可空 `uncertain_review_actor_id`、`uncertain_review_evidence`、`uncertain_reviewed_at` | 重试不覆盖旧事实；核实归原尝试，没有额外审批生命周期 |
| `compose_worker_capacity` | `id`（固定1）、`max_running`、`updated_at` | 多 Worker 原子领取必须有实际协调；未来 Redis 完整适配后可删除，当前不能用进程内计数代替 |

核实的两项确认是写入门禁，不存冗余布尔列；依据20–2000字且禁止 URL，读取和写入保持原有管理权限。Redis 替换涉及全生命周期与失效处理，见 §5.2，部署 Redis 服务本身不会切换实现。

### 12.3 迁移与交付核对

Cloud migrations 是唯一 DDL 来源，部署前通过标准迁移器顺序执行，重复执行不重复变更。087建立批次及组／份唯一键；088–090完善可调整字段、人工制作与请求摘要；091保留核实证据后合并删除旧表；092增加真实资产名／视频文件名；093将文件传输类目列统一为 `category_name`；094仅撤销可精确证明由087生成的人造历史批次，原任务、尝试和成片保留，无法证明的关联不改。

历史未知数据保持未知，不按当前策略、相近时间或显示名称补造。JSON默认、最终参数、来源平台与目标平台分别验证；旧记录无完整快照时拒绝直接再次制作并引导普通新建。升级与回归证据归对应 CHG，正式文档不保存中间方案流水。


## 2026-11-06 资源与合成执行收敛

以 ADR-0032 和产品第五章5.10为目标。内部对象引用在已有字段编码存储标识与完整对象键；存储层统一解析，新增引用不再受全局prefix变化影响，旧逻辑键只在legacy配置下读取。迁移工具在Cloud仓：盘点、复制、摘要验证、引用CAS和报告，先核验后切换，旧缺失/冲突逐项报告，不能把更换bucket配置当作迁移。素材ID固定内容，成片ID先在独立分配事实中保留再上传，只有成功事务才产生正式成片。storage_content_claims在数据库原子保留bucket/fullkey的摘要和字节数，跨进程只允许同内容重试，不将S3条件PUT作为唯一保证；SQL归storage/repository，运行时未注入共享claim时拒绝正式写入。

模板定义以code/version查找执行器；任务管理与资源下载/渲染职责分开。执行器接收来源、参数、种子和任务目录，返回实际资源/时间线/输出事实。新增模板不要求修改公共任务入口分支。五段重叠计算实际段数；完整参数、种子、资源摘要与选段固定，重试可复现。服务端约束任务上限不超过策略上限及仅开放参数。

运营文件复用Cloud存储和统一传输基础；独立模块保存文件名、归属、对象位置及稳定访问令牌，不复制素材业务或建立另一套下载中心。切片CLI和Skill以已验证对象及index.json为可用池，串行更新索引、同源去重，模型判定结果作为Skill输入而不是固定脚本假判断。

运营文件管理使用独立files模块；稳定resource_path在客户端按实际Cloud origin构成URL，线上由HTTPS部署提供。图片/视频预览和附件下载交由系统浏览器，复用Desktop已有新窗口交接；原素材与成片的本机落盘继续统一file_transfer，不引入第二个本机执行器。
