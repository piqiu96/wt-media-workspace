# CHG-20261013-085 Checkpoint

## Completed

- 前置核对：CHG-20261013-084（M4-C6 我的成片）已归档；`file_transfer_tasks` 表 CHECK 约束已允许 `asset_type='composite_output'` + `purpose='user_download'` + `execution_scope='local_agent'`（迁移 039），DB 无需迁移；下载链（production 创建→Agent 领取→落盘回报→Drawer 投影）现状已通读并在 change.md §7 登记扩展点。
- CHG 记录已建立（本文件与 `change.md`），范围裁定见 `change.md` §7。
- T-01 完成：三份契约放宽/新增（asset_type 枚举化两处 + `POST /compose-outputs/{output_id}/downloads`），两条合同测试红先绿后，相关包全绿。Cloud commit `88aa46a`。证据 `evidence/T-01.md`。

## Current

无进行中任务。

## Next

T-02 Cloud 实施：`AssetCompositeOutput` 常量、`CreateTask`/去重 asset_type 参数化、`POST /compose-outputs/:output_id/downloads` 路由 + service（readable 门）；单测 + sqlmock 红先。

## Blockers

None.

## Recent verification

- governance verify exit 0（Active CHG: CHG-20261013-085）；filetransfer/production/bootstrap 包测试全绿。
