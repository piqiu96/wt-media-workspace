# CHG-20261013-084 Checkpoint

## Completed

- 前置核对：CHG-20261013-083（M4-C5）已归档；`composite_outputs` 表与 `publish_status` 投影（pending_publish）已在（迁移 053/054），成片由 M4-C5 真实闭环产出；`materials/{id}/video-url` 预签名边界与合成任务 canRead 范围形状均在代码中。
- CHG 记录已建立（本文件与 `change.md`），范围裁定见 `change.md` §7。
- T-01 完成：openapi `ComposeOutput`/`ComposeOutputTrace`/`ComposeOutputDetail` schema + list/detail/archive/video-url 四端点 + version 2026.10.13.3；模型 `ObjectKey` 改 `json:"-"`（对象地址永不进响应）；wire 键集全等比对红先绿后。Cloud commit `b106c06`。
- T-02 完成：Repository（范围内 List/Find、条件归档 `pending_publish→archived` + 同事务审计、无归档列只翻 updated_at）+ Service（canRead 与任务页同形、trace 只读投影、预签名走 ObjectKey、越权 404 同形）；service 用例 8 组 + sqlmock 条件归档用例；repository 新增无归属 `FindUsage`（trace 的历史事实读法）。Cloud commit `37becc0`。
- T-03 完成：四路由 + 错误写手（15214/15215/15216/新 15218 `compose_output_not_archivable`，输出具名）+ detail/trace 键集比对 + 路由 401 探针。Cloud commit `068aed7`。

## Current

无进行中任务。

## Next

T-04 「我的成片」页面（列表/详情/预览/归档/去发布入口）+ 路由导航接入，vitest 用例。

## Blockers

None.

## Recent verification

- governance verify exit 0（归档 CHG083 后，Active CHG: none）。
