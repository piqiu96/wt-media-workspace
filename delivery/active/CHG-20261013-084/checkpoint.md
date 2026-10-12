# CHG-20261013-084 Checkpoint

## Completed

- 前置核对：CHG-20261013-083（M4-C5）已归档；`composite_outputs` 表与 `publish_status` 投影（pending_publish）已在（迁移 053/054），成片由 M4-C5 真实闭环产出；`materials/{id}/video-url` 预签名边界与合成任务 canRead 范围形状均在代码中。
- CHG 记录已建立（本文件与 `change.md`），范围裁定见 `change.md` §7。
- T-01 完成：openapi `ComposeOutput`/`ComposeOutputTrace`/`ComposeOutputDetail` schema + list/detail/archive/video-url 四端点 + version 2026.10.13.3；模型 `ObjectKey` 改 `json:"-"`（对象地址永不进响应）；wire 键集全等比对红先绿后。Cloud commit `b106c06`。
- T-02 完成：Repository（范围内 List/Find、条件归档 `pending_publish→archived` + 同事务审计、无归档列只翻 updated_at）+ Service（canRead 与任务页同形、trace 只读投影、预签名走 ObjectKey、越权 404 同形）；service 用例 8 组 + sqlmock 条件归档用例；repository 新增无归属 `FindUsage`（trace 的历史事实读法）。Cloud commit `37becc0`。
- T-03 完成：四路由 + 错误写手（15214/15215/15216/新 15218 `compose_output_not_archivable`，输出具名）+ detail/trace 键集比对 + 路由 401 探针。Cloud commit `068aed7`。
- T-04 完成：「我的成片」页（列表/详情抽屉/预览/归档/去发布入口）+ 两端 `finished-media` 路由由占位页换成真实页面 + 客户端四方法；红先绿后（新增 5 条页面钉住、parity 钉住、约定量具、客户端路径比对），web 全量 59 files 532/532 绿。证据 `evidence/T-04.md`。Cloud commit `27215ed`。
- T-05 完成：真实环境探针 0/A–G 全 PASS（建任务→成片→读回一致且无对象地址、越权 404 同形、预签名 URL 全量下载 sha 一致、归档翻转+审计+409 零写入、无发布写入者、清零带正假对照）。遗留 CHG083 worker 进程导致的任务 14 失败残留已披露并清零。证据 `evidence/T-05.md`。

## Current

无进行中任务。

## Next

T-06 全量回归与证据收口（Go 全量、web vitest 全量、governance exit code）→ 归档 CHG084。

## Blockers

None.

## Recent verification

- governance verify exit 0（归档 CHG083 后，Active CHG: none）。
