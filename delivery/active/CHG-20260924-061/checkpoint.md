# Checkpoint: CHG-20260924-061

- CHG: `CHG-20260924-061`（M4-A 素材库、我的素材与原素材懒加载下载）
- Level: M
- Updated: 2026-09-26

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

## Current

Task 3 第一段进行中（Cloud 仓 `codex/m4-a-cloud`，HEAD `a620e4f`）。配置键、存储边界与接线已落地并有读数；第一段余下 `infra/client/sourcefile`、`MediaAddress` 合成夹具、媒体探针、`material_prepare` worker 与失败注入矩阵。

## Next

1. **Task 3 第一段余项（无外部副作用，可离线完成）**：`infra/client/sourcefile`（`Open(ctx, url, offset)` 带 `Range` 并如实报告服务端是否忽略）、`infra/client/platforms/douyin/media.go` 的 `MediaAddress(payload)`（`example.invalid` 合成夹具）、`infra/media/probe.go`（MP4 box 解析，不引入 FFmpeg；`moov` 在尾时 `DurationMS=0` 不算失败）、`internal/jobs/material_prepare.go`（临时键→校验→正式键，任一失败绝不写正式键与 `video_status='ready'`）与失败注入矩阵逐行留证。
2. **Task 3 第二段（需要凭据与可达端点）**：真实键、真实 size／sha256 对账、真实字节上的媒体探针、`play_addr` 实网确认与 AC-01 反证。凭据只存在于用户手工填写的未跟踪文件 `config/credentials/object_storage.toml`。
3. **Task 4**：合同先行（`save-directory` 端点与 `contracts/local-error-codes/v1/transfer.yaml`）→ Agent 侧下载执行分层 → checkpoint 字段与 `0003` 迁移 → local API → Desktop 选择器与推送。Task 4 的唯一硬前置（Cloud-Agent 领取／完成响应 schema）已在 `a5b5e43` 冻结。

## Blocked

- **Task 3 第二段与 T-03 真实验收**需要两个尚未提供的值：(1) 凭据文件 `config/credentials/object_storage.toml` 由用户手工填写且不入库，尚未创建；(2) **桶名与 region**——用户只给了端点 `data.bucket.oss.longyanyue.cn`，桶名与 region 未知。两棵树里的 `bucket` 现写作自述式哨兵 `REPLACE_WITH_BUCKET`（而非看起来可信的虚构名），使缺失值在第一次调用即显式失败，而不是伪装成 access denied。二者都不阻止第一段、Task 4 与 Task 5。
- **两处既有问题待登记，不在本 CHG 范围内**（计划已裁定只登记、不扩大范围）：(1) `migrations/README.md` 的 Active Migrations 清单停在 025，且其 `WT_MYSQL_DSN`／`WT_MEDIA_MYSQL_DSN` 说明与 Go 源码不符；(2) `materials.source_snapshot` 存 provider 原始 payload，Douyin 响应含短时效签名 URL，与 CHG §4「不把完整签名 URL 写入 Cloud 业务表」相悖（`contentpool/service/discovery_crawler.go`，M3 既存路径）。

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
