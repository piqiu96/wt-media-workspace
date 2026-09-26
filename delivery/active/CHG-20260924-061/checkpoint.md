# Checkpoint: CHG-20260924-061

- CHG: `CHG-20260924-061`（M4-A 素材库、我的素材与原素材懒加载下载）
- Level: M
- Updated: 2026-09-27

## 状态

`IMPLEMENTING`（2026-09-26 激活）

## Completed

- **T-00 激活与基线盘点**：确认 M3 为 `DONE`、`delivery/active` 为空、M4/M5 的 Product、Engineering、ADR-0017 与 CHG-061 一致；061 从 `planned/` 移至 `active/`，M4 更新为 `IN_PROGRESS`，M5 保持 `NOT_STARTED`。未修改任何运行时代码。基线记录见 `evidence/20260926-activation-baseline.md`。
- **T-00 合同与运行前提冻结**：Cloud 提供方合同已在 `wt-media-cloud@fcb07a1` 冻结；随后依照横向任务边界把 `file_transfer_task` 从生产领域拆为独立 `filetransfer` 模块及独立 schema/enum/error/API 合同。Douyin 可按 `platform_content_id` 从 Cloud 详情接口即时解析源文件地址；Local Agent 使用既有绑定会话与新鲜心跳的信任校验。当前配置树没有对象存储端点或测试桶配置，故不阻止数据库/API 开发，但阻止 Task 3/Task 6 的真实对象存储验收。
- **T-01 迁移、模型与 Repository**：在 `wt-media-cloud@a3825b4` 增加 `20260926_039_content_production_m4_a.sql`、`production` 的素材投影与唯一 `material_usage` 仓储，以及不依赖生产模块的 `filetransfer` 仓储。测试覆盖素材关系原子创建/恢复、软移出、范围查询、传输去重、条件领取、续租、进度、成功、失败与取消终态；迁移不保存本机路径、签名 URL 或长期存储凭据。
- **T-02 合同冻结与迁移运行器缺陷**：`contracts/cloud-agent-api/v1/file-transfer.openapi.yaml` 补齐领取/完成响应 schema（`LocalLease`、`ClaimResult`、`TransferTerminal`）并给缺失 `responses` 的 `progress` 补上该键；`contracts/business-schemas/v1/file-transfer.yaml` 增加 `file_name`。另修迁移运行器：`strings.Split(sql, ";")` 会把 039 头注释里的分号当语句边界，导致该迁移从未被应用过（`Error 1064`），现改为五状态扫描器。
- **T-02 迁移 041 与传输仓储**：新增 `20260926_041_file_transfer_task_executor_facts.sql`（`asset_title`／`source_object_key`／`file_name`），因运行器按版本字符串判定，改已提交的 040 会被静默跳过。仓储补齐 `GetTask`／`ListTasks`／`RetryTask`／`ClaimCloudTask` 与两个 reconciler；修三处真实缺陷：领取缺 `cancel_requested_at IS NULL` 会让取消中的任务永远卡在 `running`、`attempt_count` 无上限、`createTask` 在去重键冲突时按 `input.ID` 回读导致成功请求报 `ErrNotFound`。
- **T-02 API helper 与“我的素材”**：`api` 增加 `Accepted`／`NoContentEmpty`／`UnprocessableEntity`／`ConflictNamed`／`FailureNamed`（冻结的错误码合同只发布名字，`error.type` 是唯一判别位）；`production` 增加 `GET /api/v1/my-materials` 与 `DELETE /api/v1/material-usages/{id}`，后者由 200 信封改为真 204，并把“我的素材记录不存在”从 15003（素材不存在）拆出为 15006。
- **T-02 传输模块与下载入口（收口）**：`filetransfer` 补齐 `dto`／`service`／`handler`／`router` 七条路由（会话侧 3 条 ＋ Cloud-Agent 侧 4 条），Cloud-Agent 四条的凭据读取一律排在 body 解析之前，使无凭据答案统一为 401；`runtimebinding` 增加仅凭凭据识别节点（`claim` 的冻结合同既无路径参数也无请求体，身份只能来自凭据）与按用户解析新鲜本机节点（确定性择一）；`production` 增加 `POST /api/v1/materials/{id}/downloads`（权限 → `video_status=ready` → 新鲜节点 → 建 `user_download`／`local_agent` 任务 → 202）；`bootstrap/routes.go` 把模块清单拆成 `registerModuleRoutes` 并注册 `filetransfer`，使“模块漏注册＝全路由 404 而无其他症状”可被断言。`production` 的 200/201 由 SQL 的 `RowsAffected` 判定（`updated_at` 改为条件赋值，否则重复点击恒为 201），并修同一语句里 `status` 读写顺序导致恢复行留下陈旧 `removed_at` 的缺陷。读数：`go test ./...` `64 ok / 0 FAIL`（`0607087`）；提交 `74b6568`、`1355baf`、`b542403`、`a159315`、`c106283`、`e78a031`、`dbd35f5`、`4243e21`。
- **T-02 错误映射守门**：`filetransfer/writeTransferError` 的七支映射此前无可证伪测试（两个 409 仅靠 `error.type` 区分，422 是合同专属的完整性状态，把 422 折进 409 会让全仓测试保持全绿）。新增两张测试表读同一份表的两端：一张经探针路由断言真实响应，一张读 `contracts/cloud-error-codes/v1/file-transfer.yaml` 断言名字与状态均已声明，链条为「代码 → 表 → 合同」；另断言未映射错误必须完全省略 `error`（而非 `"type": ""`）与受检名字数。五个变异控制各自单独施加且各自变红，文件按 sha256 逐字节还原；提交 `0607087`。

- **T-03 对象存储配置键（第一段）**：`config/storage/object_storage.toml` 与 `config_online/` 同构新增（`endpoint`／`bucket`／`region`／`prefix`／`use_ssl`／`presign_ttl`），`internal/config` 增加 `Storage.ObjectStorage` 与凭据键并在 `Validate` 里校验端点、桶名、正数 TTL 与「凭据成对」。凭据文件 `config/credentials/object_storage.toml` **不入库**：仓内只提交无值 `.example`，`.gitignore` 加两条规则并在 `config/README.md` 说明该偏离（既有 `agent.toml`／`douyin.toml` 是被跟踪的，A-03 记录在案）。这一偏离由 `git check-ignore -v` 双向验证：真实路径被忽略、`.example` 不被忽略、真实文件不出现在 `git status`。提交 `af13a22`。
- **T-03 对象存储边界（第一段）**：新增 `internal/infra/storage`，`Store` 接口 `PresignGet`／`Stat`／`Put`／`Copy`／`Remove`；键位内容寻址 `materials/{id}/{sha256}.{ext}` 与暂存键 `materials/{id}/.staging/{taskID}.{ext}`；`registry.go` 照抄 `pkg/clients/http/registry.go` 形状，**凭据双空是正常状态**（发布 `notConfiguredStore{}`，五个方法全部 `ErrNotConfigured`），使发布树与本仓测试在没有用户密钥时也能启动。依赖 `minio-go/v7 v7.0.98`（`go 1.24.0` 可接受的最新高版本；`v7.0.99+` 要求 `go 1.25.0`，实测会连带升级 x/crypto 等）。另修一处会在生产里才暴露的缺陷：region 为空时 minio-go 会在**本地签名**过程里插入一次 `GetBucketLocation` 网络往返，故显式传入 region 并用请求计数型 `httptest` 把该行为钉住。提交 `20c8847`。`validateExtension` 里一条空白字符守卫被**删除**：移除它不改变任何可观测行为（`[a-z0-9]` 字符检查已拒绝空格），按 §12「无法被证伪的规则不是防御」不保留死防御。
- **T-03 接线：租约授权改由对象存储签发（第一段）**：此前 claim 路径落到默认的 `unavailableGrants`——没有 bucket 时正确，有 bucket 时**每次领取都失败**，且故障在执行器侧显形、看起来像 Cloud 的错。新增 `objectStorageGrants` 适配器（接口不收寿命、`storage.Store.PresignGet` 要求寿命，故不做成 Store 本身：模块内调用方因此无从指定地址有效期），`storageResource()` 加入 **server 与 worker 两个 plan** 的 database 与 clients 之间（server 要签发是因为冻结合同的 `LocalLease` 携带地址），migration 与 scheduler plan 明确不带。新增三个守门测试覆盖无其他测试可达的接缝：server plan 丢步、接线服务退回拒绝态、适配器丢 `ExpiresAt`、注册表未捕获配置寿命。提交 `a620e4f`。
- **T-03 一次点击：云端排队 ＋ 本地等待任务（第一段）**：此前 `POST /materials/{id}/downloads` 对任何 `video_status != ready` 的素材一律回 409 `material_unavailable`，于是 M4-AC-03 的「触发后有任务」没有任何触发点——M4-A 里**没有任何代码**会创建准备任务，T-03 的 worker 将无任务可领。这与 PRD 5.3.4 的状态表相反（`not_downloaded` 一栏写的是「是，系统先准备文件」）。按用户裁定改为一次点击、两条状态行、一个 `dependency_task_id` 相连：`filetransfer` 新增 `compose_input_prepare`（Cloud 任务，去重键 `material_source_prepare|asset|generation`，故同素材并发点击只取一次源）；`leaseable` 增加 `AND (execution_scope = 'cloud' OR dependency_task_id IS NULL)`，等待中的本地任务不可领取——它租约要承诺的对象、大小与哈希正是它等待的那个任务尚未写出的事实；`HandOverDependencies` 一条语句写入事实并清空指针，`FailDependents` 与 `failDependentsOfTerminalTasks` 终结失败／取消的准备的下游（安全网用多表 `UPDATE ... JOIN` 而非子查询，MySQL 1093 禁止更新表出现在自身子查询里）；`validateCreateInput` 仅在带依赖时跳过本地事实检查，并拒绝「Cloud 准备任务依赖另一个任务」；`production.CreateDownload` 先解析节点（失败不留痕）再动投影，且在被守卫的投影写入被拒时**重读**素材——「别人已在准备」与「此刻已 ready」需要不同的任务，猜错第二个会把可下载的文件挡在无人需要的准备之后。`MarkVideoPreparing` 以 `video_status IN ('not_downloaded','failed')` 守卫，使带着陈旧读数的点击无法把 `ready` 拖回 `downloading`。提交 `7c83969`。

- **T-03 源文件流式客户端（第一段）**：新增 `internal/infra/client/sourcefile`（`Open(ctx, url, offset)`）。平台 CDN 地址是任意 origin，无法注册成绑定单一 origin 的 `pkg/clients/http`，而 `boundary_test.go` 又把 `http.Client` 挡在 `internal/modules` 之外——所以这一处自持客户端，并由边界测试保证「这个决定只做一次」。`Open` 报 `RangeStart` 而非布尔：服务端忽略 `Range` 时回 200 与整份文件，把「已续传」当真的调用方会把整份文件追加到半份之后，得到长度正确、内容错误的文件，只有很久以后的哈希才看得出来；`Content-Range` 优先于状态码、未知总长是 `-1` 而非 `0`。这些地址是短时效签名 URL，故地址与传输层包装（其文本就是请求 URL）都不得进入错误：只解出 cause、缺失地址在 `url.Parse` 之前就拒绝、错误体截断为前缀，而取消仍可被识别。提交 `5b8ee56`。
- **T-03 媒体探针（第一段）**：新增 `internal/infra/media`（`box.go` ＋ `probe.go`）。worker 在写 `video_status='ready'` 之前只需回答「到的是视频还是一张 HTML 错误页」——完整性与可读性因此严格分开，探针只管后者。直接解析 MP4 box 而不引 FFmpeg：FFmpeg 是每台 worker 上多一个二进制，其输出格式又自成一个解析契约，而这里想要的每个事实都是定长偏移上的整数或四字符码。两条刻意决定并由测试钉住：**取不到的时长是 `DurationMS == 0` 且不报错**（完整性归 size＋hash 管，这里失败会把一个已定的问题报成未定的，也会让截断文件因错误的理由被拒）；**谎报自身长度的 box 被拒而不是读进去**。`ErrNotVideo` 与 I/O 失败分开，因为调用方对二者的处理不同。提交 `27cef54`。
- **T-03 播放地址解析（第一段）**：新增 `internal/infra/client/platforms/douyin/media.go` 的 `MediaAddress(payload)`。worker **不读** `materials.source_snapshot` 取地址——快照存的是 provider 原始 payload，其中的签名 URL 早已过期（该既存问题另见 Blocked）；改为执行时用稳定的 `platform_content_id` 重新解析详情。只读 `video.play_addr.url_list`：真实 payload 另有 `play_addr_h264`、`download_addr` 与按码率给出的地址，但哪一个才是源而非转码／带水印版本尚未对该 provider 实测，选一个就是「把猜测当兜底」，留给第一次实网抓取定案。列表其余项不遍历（它们是等价地址，一次尝试内换一个 URL 只会掩盖失败）。地址是凭据：不记录、任何拒绝都不带它，`url.Parse` 的错误文本就是地址本身故只传出 cause。提交 `9760794`。
- **T-03 投影写入（第一段）**：`production` 增加 `MarkVideoReady`／`MarkVideoFailed` 与 `VideoFacts`，并暴露为 `production/service` 的 `MarkVideoReady`／`MarkVideoFailed`——worker 与两个既有 job 一样走模块的 `service` 公共面，仓储是模块内部的持久化细节，越过它会让 `internal/jobs` 成为第二个知道 SQL 面的地方。四个事实作为一个值同行进检（`ready` 但没有键／大小／哈希的行比 `failed` 更坏：下游无法把它与已备好的视频区分开）且大小按字符而非字节截到 500（严格模式下 1406 会让语句失败，恰好在最想知道失败原因时丢掉原因）。**就绪写入刻意不带状态谓词**（准备可以从任意状态完成，谓词必须枚举全部状态并会拒绝它漏掉的那些；内容寻址保证重跑得到同一个键），**失败写入刻意拒绝已 `ready` 的素材**（更慢的先前尝试已成功时，重跑失败不得把有可取视频的素材拖回 failed）。service 对两个行数读法不同且这一不对称就是要点：就绪写入零行是 `ErrNotFound`（无谓词＋每条语句都写新的 `updated_at`，匹配不到只可能是该团队没有这条素材），失败写入被拒不是错误。连接**没有**设 `CLIENT_FOUND_ROWS`，所以这是「改动的行」而非「匹配的行」，`updated_at` 赋值正是让两种读法相等的那个东西，测试为此单独钉它。提交 `8be62d4`。

- **T-03 素材准备 Worker（第一段收口）**：新增 `internal/jobs/material_prepare.go`（约 825 行）与 21 个测试／39 个子用例的失败注入矩阵。worker 经 `filetransfer` **仓储**而非其 service 领取 `material_download_task`（service 的对应函数一律先鉴一个 Cloud worker 没有、也不得假装的节点凭据），解析平台地址、边下边算 sha256、探针读过、再按自身字节派生的键提交：暂存 → 回读 → 拷贝 → 回读 → 删暂存。**只有到这里**才写 `ready` 投影并把事实交给等待中的下载：此前任一步失败都要把三行都写上（素材、等待者、任务），此后素材已是 ready、失败只是账面记录，不得记成准备的失败。四点刻意决定：探针跑在上传**之前**（计划写的是之后；它保护的要求——不为未在正式键校验通过的字节写事实——未变，而一个解析不了的容器不值得两次上传和一个无人引用的键）；**不调 `MarkVideoPreparing`**（一次点击裁定后点击本身已置 `downloading`，真正的双执行排除是 `ClaimCloudTask` 的租约，计划里那条旧守卫到此作废）；完成写入失败**刻意不记终态**（行留在 `running`、租约过期、下次领取重跑一遍每步都幂等的准备，因为键是内容寻址的）；worker 在**每条**终态路径上自己释放等待者，因为**本 build 没有注册任何 reconciler job**，而 `leaseable` 会永久拒绝带 `dependency_task_id` 的本地任务。沿用既有 worker 进程与 `WorkerInterval`，不新增 `cmd/`、也不新增配置键（两个 worker 都是轮询排空队列，第二个键只会让进程在运维编辑两棵配置树之前拒绝启动）。**先红**：36 个变异臂逐条单独施加（每臂一个守卫、逐臂从字节备份还原、断言锚点恰好命中一次、要求能编译且能变红），读数 **36 红 / 0 绿 / 0 跳过**，文件逐字节还原（sha256 `56bf8508…`）。两个臂查出了东西，都做了处置而非容忍：`commit` 之后的 lost-lease 分支**不可达**（`commit` 只与对象存储说话，不与任何持有租约的东西说话），按 §12「无法被证伪的规则不是防御」**删除**；失败消息的上限此前只被长度钉住，测试补钉「本来就装得下的消息原样返回」（截断装得下的消息会丢掉末字并像一条还没说完的话）。提交 `88532e7`。

- **T-04 保存目录合同（第一段）**：Agent 仓 `9584d9c`。`contracts/local-agent-api` 新增 `GET`／`POST /api/v1/save-directory`（`info.version` → `2026.09.27.1`）；`POST` 收 `{save_dir}` 回 `{save_dir, writable, free_bytes}`，相对路径与非目录 → 400。**未存过目录时 `save_dir: null`／`writable: false`／`free_bytes: 0`，执行器据此拒绝下载，而不是替运营猜一个目录**（本 CHG 裁定，不设默认目录）。新增 `contracts/local-error-codes/v1/transfer.yaml`（`revision 2026.09.27.1`），承载保存目录 API 的 400 与下载执行器的八个终态理由，并写明不可回显的字段；区域 README 改为逐文件列版本的形式，与区内其它区一致。`tests/test_contract_docs.py` 补三处此前无人守的判据，各自都有变异臂证明现在会红：①端点清单改为**双向比对 `(METHOD, path)`**（此前只比路径，README 把方法写错或漏掉新方法都能通过）；②README 必须**写明版本号**（此前一个都不写也是绿的，现以 `unstated` 单列）；③README 必须**逐个点名区域内的定义文件**（否则新增定义可以完全不进文档）。变异控制 11 臂：10 红 1 绿，四个文件每臂后按字节还原、sha256 与备份一致。workspace 侧 `551527c` 把 `config/contract-map.yaml` 的两条 revision 推进到 `2026.09.27.1` 并同步 `scripts/verify_m0_config.py` 的期望值（该推进暴露了一处此前无人察觉的守卫缺口，见 Blocked）。按兼容策略，「新增端点」与「新增区文件」都属兼容变更，无需决策记录。

## Current

Task 3 第一段**已完成**（Cloud 仓 `codex/m4-a-cloud`，HEAD `88532e7`）：配置键、存储边界、租约授权接线、「一次点击＝云端排队＋本地等待任务」的 Cloud 侧全链路、worker 的全部依赖（源文件流式客户端、媒体探针、播放地址解析、投影写入）与 worker 本身均已落地、均有读数、均已有先红证据。Cloud 侧可离线的部分到此为止，余下的是需要真实凭据与可达端点的第二段。

Task 4 的**合同闸门已过**（Agent 仓 `9584d9c`、workspace `551527c`）：`/api/v1/save-directory` 与 `v1/transfer.yaml` 已定义、已被守、map 已推进，余下的实现不再有合同前置。

**用户裁定（2026-09-26，不再重开）**：一次点击即可——「发起下载先判断云端任务是否有，有就本地直接下载，否则云端先加等待，本地定期获取作为本地下载的一部分」。落地为 `7c83969`：本地任务立即创建并带 `dependency_task_id`，在准备任务交出事实前不可领取（`/claim` 回 `{"task": null}`，即合同里既有的「无事可做」），因此「本地定期获取」不需要第二条机制，也不需要改任何冻结合同。

**用户裁定（2026-09-27，不再重开）**：①合同遗漏的 7 条已实现路径**只登记、不在本 CHG 补**（登记在 `contracts/local-agent-api/README.md` 末尾；该段刻意不含 HTTP 动词，因此不会冒充端点清单）；②未选保存目录时**回 `null` 并让执行器拒绝下载**，不设默认目录。

## Next

1. **Task 3 第二段（需要凭据与可达端点）**：真实键、真实 size／sha256 对账、真实字节上的媒体探针、`play_addr` 实网确认与 AC-01 反证。凭据只存在于用户手工填写的未跟踪文件 `config/credentials/object_storage.toml`；`minio.New` 是否接受该 endpoint／bucket／region、presign 出的 url 在 Agent 机器上真能下，都只有这一段能回答。
2. **Task 4 余下部分（合同已就位）**：Agent 侧下载执行分层（`clients/transfer/source.py` 流式下载 → `storage/download_sink.py` 原子落盘 → `executors/material_download.py` 编排；三者都是 `test_dependency_boundaries.py` R4 允许的边，动手前先核 R10 的 `FROZEN_LAYER_EDGES`）→ `runtime/constants.py` 的 `TASK_TYPE_MATERIAL_DOWNLOAD` → `runner/registry.py` 的 `default_executor_factories(bitbrowser, *, transfer=None)` → `storage/checkpoint_store.py` 的 `TaskCheckpoint.transfer_state_json`（**先写往返用例**：`get_checkpoint` 按 `SELECT *` 构造，缺字段是运行时 `TypeError` 而非测试失败）＋ `storage/migration.py` 末尾追加 `0003_transfer_resume` → `local_api/server.py` 的 `do_GET`／`do_POST` 分支 → Desktop 的 `tauri-plugin-dialog` 与三个命令。顺带修 `AGENT-INDEX.md` 的命令数漂移（实测 29 个）与「`save_dir` 目前没有消费方」这句在 Task 4 后即为假的陈述。
3. **Task 5 待办（因本次裁定新增）**：准备任务按**素材**去重而非按用户，所以第二个操作员的抽屉里只会有他自己那条等待中的本地任务，看不到共享的云端准备。UI 必须把等待中的本地任务标注为「等待云端准备」，否则它会看起来像一条停滞的任务。

## Blocked

- **Task 3 第二段与 T-03 真实验收**需要两个尚未提供的值：(1) 凭据文件 `config/credentials/object_storage.toml` 由用户手工填写且不入库，尚未创建；(2) **桶名与 region**——用户只给了端点 `data.bucket.oss.longyanyue.cn`，桶名与 region 未知。两棵树里的 `bucket` 现写作自述式哨兵 `REPLACE_WITH_BUCKET`（而非看起来可信的虚构名），使缺失值在第一次调用即显式失败，而不是伪装成 access denied。二者都不阻止第一段、Task 4 与 Task 5。
- **三处既有问题待登记，不在本 CHG 范围内**（计划已裁定只登记、不扩大范围）：(1) `migrations/README.md` 的 Active Migrations 清单停在 025，且其 `WT_MYSQL_DSN`／`WT_MEDIA_MYSQL_DSN` 说明与 Go 源码不符；(2) `materials.source_snapshot` 存 provider 原始 payload，Douyin 响应含短时效签名 URL，与 CHG §4「不把完整签名 URL 写入 Cloud 业务表」相悖（`contentpool/service/discovery_crawler.go`，M3 既存路径）；(3) **没有任何 job 注册传输模块的两个 reconciler**。取证：`git grep -n "ReconcileCancelledTasks\|ReconcileExhaustedTasks\|failDependentsOfTerminalTasks" -- '*.go'` 的全部命中都在 `filetransfer/repository/store_mysql.go`（定义、彼此调用、注释）与 `store_mysql_test.go`（测试），**没有生产调用方**；`git grep -n "runner.Register(" -- '*.go'` 只命中 `bootstrap/jobs.go` 的四行（`discovery-schedule`、`proxy-expiry`、`discovery-worker`、`material-prepare-worker`），没有一条是清扫。同一分母下的阳性对照：把函数换成 `ClaimCloudTask` 重跑同一模式，命中 `material_prepare.go:749` 的真实调用方——即该检索能看见调用方，`0` 是真 `0`。因此本 CHG 的 worker 在每条终态路径上自己释放等待者，不依赖那趟清扫；但**别的**路径留下的悬空 `dependency_task_id`（节点中途死亡、任务被别处终结）仍然只能靠人工。这是本 CHG 之前就有的缺口，登记在案，修它要动 scheduler 的 job 清单与两个仓的配置。

- **`config/contract-map.yaml` 的 revision 只被一个手写常量守着**（本 CHG 因推进合同而实测确认；不在其范围内，只登记）。唯一的守卫是 `scripts/verify_m0_config.py` 里的期望值，它比的是「map vs 脚本常量」，**从不比「map vs 定义文件」**——尽管全工作区模式下 `provider_path` 已经把那份文件解析出来了。于是钉子与 map 可以一起停在一个过期值上而双双通过。实测时间线（三处都在 git 上）：`988a010`（M2-C）把 map 定在 `2026.09.06.1`；`87b1264`（CHG-057 T-08）把定义文件推进到 `2026.09.24.1`，没碰 map；CHG-20260923-059 T-09 量到该漂移并登记为 Q-06、判不阻塞；CHG-20260925-063 T-01 以「对齐现状」为由把钉子挪到 `2026.09.06.1`，即把守卫对到了一个已经过期的值上。本 CHG 改 map 时红是必然的（改前四个校验器全绿、改后 `verify_m0_config.py` 与 `tests/test_verify_m0_config.py` 两条用例点名这两处期望值），**这条红同时就是该钉子能失败的阳性对照**。map 只有三个读者（`verify_m0_config.py:50` 等值钉值、`verify_m2_acceptance.py:62` 与 `verify_product_master_alignment.py:389` 子串包含），故改这两条 revision 只影响第一处。要让「map 与定义文件相等」真被守住，需要新增一条读定义文件的检查；本 CHG 不做（会把「合约版本前进须人工复核」的既有设计换成自动跟随）。
- **两处本 CHG 登记但未处理的合同缺口**：①`contracts/local-agent-api` 有 **7 条已实现但无定义**的 `/api/v1/*` 路径（`/api/v1/bind`、`/api/v1/bit-browser/profile-{create,open,close,update,delete}`、`/api/v1/cookie-read`），按 2026-09-27 裁定只登记在 API README 末尾；定义事后编出来只会是实现的描述而非商定的接口。其中 `profile-delete` 在 Desktop 与 Agent 两仓都没有消费方（CHG-20260923-059 T-09 实测）。②`contracts/local-error-codes/v1/transfer.yaml` 的**错误码清单本身**目前无人守：11 臂里唯一为绿的那条（删掉 `save_directory_invalid` 无任何断言变红），因为真正的消费方——下载执行器与本机 API 的 400 分支——在 Task 4 余下部分才落地。**届时必须把该臂转为红**，否则这份文件是「写了但没人用」。

## Recent verification

| 判据 | 读数 |
|---|---|
| `python3 scripts/verify_delivery_governance.py`（激活后） | `exit=0`；active CHG 为 `CHG-20260924-061` |
| `python3 scripts/verify_product_master_alignment.py`（激活后） | `exit=0` |
| `python3 -m unittest tests.test_prepare_ai_workspace tests.test_verify_delivery_governance tests.test_verify_product_master_alignment -q` | `Ran 28 tests / OK` |
| Cloud `go test ./...`（`a3825b4` 前） | `exit=0` |
| Cloud `go vet ./...`（`a3825b4` 前） | `exit=0` |
| Cloud contracts YAML parse（31 files） | `exit=0`；无凭据写入合同 |
| Cloud `go test ./...`（`1355baf`） | `62 ok / 0 FAIL` |
| Cloud `go vet ./...`（`1355baf`） | `exit=0` |
| 迁移应用到稳定 dev 库（`1355baf`） | `1 applied, 42 total`；重跑 `0 applied, 42 total` |
| 空库从零跑全部迁移（`1355baf`） | `42 applied`，28 张表；`file_transfer_tasks` 33 列且顺序与 `taskColumnList` 一致 |
| Cloud `go test ./...`（`0607087`，最后一次内容改动之后重跑） | `64 ok / 0 FAIL` |
| Cloud `go vet ./...`（`0607087`） | `exit=0` |
| Cloud `gofmt -l internal/`（`0607087`） | 无输出 |
| 错误映射守门变异控制（`0607087`） | 5 个，各自单独施加、各自变红；还原后两文件 sha256 与备份一致 |
| Cloud `go test ./...`（`a620e4f`，最后一次内容改动之后重跑） | `65 ok / 0 FAIL` |
| Cloud `go build ./...` / `go vet ./...`（`a620e4f`） | `exit=0` |
| Cloud `gofmt -l internal/`（`a620e4f`） | 无输出 |
| 接线变异控制（`a620e4f`） | 4 个，各自单独施加、各自变红，且各自只被预期的那条断言抓住；每条臂开始时还原全部四个被触碰文件，结束读数 4 份 sha256 与备份逐一相同 |
| 存储边界变异控制（`20c8847`） | 6 个，各自单独施加、各自变红；其中 1 个（空白守卫）保持不变红，该守卫随即被删除而不是保留 |
| Cloud `go test ./...`（`7c83969`，最后一次内容改动之后重跑） | `65 ok / 0 FAIL` |
| Cloud `go build ./...` / `go vet ./...`（`7c83969`） | `exit=0` |
| Cloud `gofmt -l internal/`（`7c83969`） | 无输出 |
| 一次点击变异控制（`7c83969`） | 12 个，各自单独施加、各自变红，且各自只被预期的那条断言抓住；每条臂开始时还原全部七个被触碰文件，结束读数 7 份 sha256 与备份逐一相同。其中两条首轮为绿（`validateCreateInput` 的准备依赖守卫、`MarkVideoPreparing` 的投影接线）——前者是测试用的 mock 未按「守卫被删后会插入的那一行」布防，等于让 mock 而非守卫去拒绝；后者是选错了判据，两条都已改成能失败的形式并复跑 |
| `sourcefile` 变异控制（`5b8ee56`） | 9 个，各自单独施加、各自变红；其中 1 个（`Content-Range` 单位检查）首轮为绿——测试输入没有一个让该单位成为承重项，补上 `0-9/10` 这一例而不是保留未验证的检查 |
| Cloud `go test ./...`（`27cef54`） | `67 ok / 0 FAIL` |
| 媒体探针变异控制（`27cef54`） | 23 个，各自单独施加、各自变红；两文件 sha256 还原后与备份一致。其中一条臂因删除代码块导致变量未使用（编译错误，按 §12 什么都不证明）而重射；另一条锚点匹配 0 次（锚点写在注释之前）而改用当前原文 |
| `MediaAddress` 变异控制（`9760794`） | 8 个，各自单独施加、各自变红；文件 sha256 还原后与备份一致 |
| Cloud `go test ./...`（`8be62d4`，最后一次内容改动之后重跑） | `67 ok / 0 FAIL` |
| Cloud `go vet ./...` / `gofmt -l internal/`（`8be62d4`） | `exit=0` / 无输出 |
| 投影写入变异控制（`8be62d4`） | 27 个（仓储 19 ＋ service 8），各自单独施加、各自变红；两文件 sha256 还原后与备份一致。仓储批首轮 5 个为绿且都是同一处自身测试缺陷：把「被拒绝」断言成「返回了错误」——语句落到未布防的 mock 上也会返回错误，故删掉守卫同样通过；此前提交里写的范围拒绝测试有同一个洞，三处一并改成断言拒绝原因。另有两个**完全没有测试**的守卫（对象键与哈希的空白裁剪，因 `video_sha256` 是 `CHAR(64)` 而校验接受的是裁剪后的值，属承重项）补测试而非删除 |
| Cloud `go test -count=1 ./...`（`88532e7`，最后一次内容改动之后重跑） | `67 ok / 0 FAIL` |
| Cloud `go vet ./...` / `gofmt -l internal/`（`88532e7`） | `exit=0` / 无输出 |
| `internal/jobs` 用例量（`88532e7`） | 21 个顶层测试 ／ 39 个子用例 ／ 0 FAIL（分母为 `-v` 下 `^--- PASS` 与 `^    --- PASS` 的计数） |
| 素材准备 worker 变异控制（`88532e7`） | 36 个，各自单独施加、各断言锚点恰好命中一次、各要求能编译、各自变红；文件 sha256 还原后与备份一致（`56bf8508…`）。首轮 30 臂：24 红、2 绿、4 因编译或锚点被跳过。两条绿都是真发现而非噪声，都做了处置：`commit` 之后的 lost-lease 分支**不可达**（臂删掉它没有任何测试变红，因为 `commit` 只与对象存储说话、`errLeaseLost` 是包内私有哨兵，没有任何实现能返回它）→ 删除该分支；失败消息上限只被长度钉住（臂删掉「装得下就原样返回」后仍全绿）→ 补断言而非删除守卫。4 条跳过的臂逐条修复后重射（3 条因删代码块留下未使用变量而改成「把条件置假」的形式，1 条锚点在两个函数里各命中一次而按上一行文本拆成两条独立臂） |
| Agent `scripts/test.sh`（`9584d9c`，最后一次内容改动之后重跑） | `Ran 418 tests / OK`，`exit=0`。worktree 内无 `.venv`，按脚本自带的覆盖位 `PYTHON_BIN` 指向主检出解释器运行 |
| `tests/test_contract_docs.py` 用例量（`9584d9c`） | 8 个顶层测试，其中 3 个是阳性对照；本次新增的 3 处判据均先红后绿 |
| 合同变更变异控制（`9584d9c`） | 11 个，各自单独施加、各断言锚点恰好命中一次、各自只跑 `tests/test_contract_docs.py`；10 红 / 1 绿（绿的那条是 `transfer.yaml` 的错误码清单，成因见 Blocked）。每条臂开始时还原全部四个被触碰文件，结束读数 4 份 sha256 与备份逐一相同 |
| workspace `verify_m0_config` / `verify_delivery_governance` / `verify_product_master_alignment` / `verify_agent_entry`（`551527c`） | 四个全部 `exit=0`；另跑 `verify_m2_acceptance.py` 亦 `exit=0`（它也读 map，但用子串包含） |
| workspace `python3 -m unittest discover -s tests -q`（`551527c`） | `Ran 106 tests / OK`。改 map 之前该套件为 `FAILED (failures=2)`，两条用例都点名 `local_agent_api` 与 `local_error_codes` 的期望值——即本次改动的阳性对照 |
