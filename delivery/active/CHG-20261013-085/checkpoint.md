# CHG-20261013-085 Checkpoint

## Completed

- 前置核对：CHG-20261013-084（M4-C6 我的成片）已归档；`file_transfer_tasks` 表 CHECK 约束已允许 `asset_type='composite_output'` + `purpose='user_download'` + `execution_scope='local_agent'`（迁移 039），DB 无需迁移；下载链（production 创建→Agent 领取→落盘回报→Drawer 投影）现状已通读并在 change.md §7 登记扩展点。
- CHG 记录已建立（本文件与 `change.md`），范围裁定见 `change.md` §7。

## Current

T-01 合同放宽与成片下载端点定义，尚未开始编码。

## Next

T-01：`business-schemas/v1/file-transfer.yaml` 与 `cloud-agent-api/v1/file-transfer.openapi.yaml` 的 asset_type 枚举化 + version bump；`content-production.openapi.yaml` 新增 `POST /compose-outputs/{output_id}/downloads`；红先合同测试。

## Blockers

None.

## Recent verification

- governance verify exit 0（归档 CHG084 后重新登记本 CHG 前读数：Active CHG: none）。
