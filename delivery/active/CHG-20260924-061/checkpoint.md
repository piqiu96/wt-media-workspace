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

## Current

Task 2 进行中（Cloud 仓 `codex/m4-a-cloud`）。已完成：迁移运行器的注释切分缺陷修复、迁移 041、`filetransfer` 仓储全量补全与两处领取谓词修复、`api` 的状态 helper、`production` 的“我的素材”读取与移出（含 204 与 15006 对齐）。尚未开始：`filetransfer` 的 dto／service／handler／router、`runtimebinding` 的凭据鉴权与新鲜节点解析、`production` 的 `POST /materials/{id}/downloads`、路由注册。

## Next

1. **Task 2 余下部分**：`filetransfer/dto` → `service`／`handler`／`router`（会话侧 3 条 ＋ Cloud-Agent 侧 4 条）→ `runtimebinding.AuthenticateNodeCredential` 与 `FindFreshLocalNode` → `production` 的下载入口（202）→ `bootstrap/routes.go` 注册。
2. **Task 3**：在获得对象存储端点、桶与最小权限凭据后实现真实 Cloud 原素材准备；此前只完成无外部副作用的类型化客户端与配置加载。

## Blocked

- 真实对象存储测试环境未配置：`config/` 与 `config_online/` 当前没有对象存储端点、桶或凭据文件。它只阻止 Task 3/Task 6 的真实文件传输验收，不阻止当前 API、Agent 或 UI 开发。

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
