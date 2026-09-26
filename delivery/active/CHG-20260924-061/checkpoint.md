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

## Current

Task 2 进行中：补齐“我的素材”、独立文件传输 API 与 Local Agent 正式领取/回报接口；HTTP 仅创建或查询事实，不启动 Worker 或等待文件。

## Next

1. **Task 2**：实现素材/我的素材与独立 `file_transfer_task` 的完整读取、取消、重试和 Cloud-Agent API；对重复、越权、取消与非法状态回报增加自动测试。
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
