# CHG-20261013-085 Checkpoint

## Completed

- 前置核对：CHG-20261013-084（M4-C6 我的成片）已归档；`file_transfer_tasks` 表 CHECK 约束已允许 `asset_type='composite_output'` + `purpose='user_download'` + `execution_scope='local_agent'`（迁移 039），DB 无需迁移；下载链（production 创建→Agent 领取→落盘回报→Drawer 投影）现状已通读并在 change.md §7 登记扩展点。
- CHG 记录已建立（本文件与 `change.md`），范围裁定见 `change.md` §7。
- T-01 完成：三份契约放宽/新增（asset_type 枚举化两处 + `POST /compose-outputs/{output_id}/downloads`），两条合同测试红先绿后，相关包全绿。Cloud commit `88aa46a`。证据 `evidence/T-01.md`。
- T-02 完成：Cloud 创建链——`AssetCompositeOutput` 常量、repository/service 的 AssetType 透传与默认（空→material，未知拒绝）、去重摘要加入 asset_type（四个冻结字面量按新格式重算，旧格式经独立复算做阳性对照）、`POST /compose-outputs/:output_id/downloads`（202/404/409 15105）+ `CreateOutputDownload`（readable 门、节点哨兵、标题 `成片-<id>`、无 prepare）。repo/service 两条红先绿后；production 侧 5 组变异补判别力。相关包全绿。证据 `evidence/T-02.md`。Cloud commit `ec79845`。
- T-03 完成：Agent——`LEASABLE_ASSET_TYPES` 门外放、`TransferLease.asset_type` 字段、`EXECUTORS_BY_ASSET_TYPE` 把 material/composite_output 都路由到同一下载执行器、未知类型 no-executor 分支；执行器与命名零改动（租约驱动）。unroutable 分派红先绿后；门与路由以 2 组变异补判别力。全仓 unittest 705 全绿。证据 `evidence/T-03.md`。
- T-04 完成：Web——`downloadFacts` 三门按 `DOWNLOADABLE_ASSET_TYPES` 放行 + `assetFallbackTitle`；`compose.js` 新增 `createOutputDownload`（202 语义 + Desktop 可信 Agent 前置）；`DownloadCentreDrawer` 增 `createDownloadFor` 唯一入口（asset_type 分派）、成片行详情 `router.push FinishedMedia`、三处标题兜底。source-pin 红先；类型门以 2 组变异补判别力（测试构造错误已当场修正）。三文件 63 全绿，web 全量 536 全绿。证据 `evidence/T-04.md`。Cloud commit `4a3bee6`。
- T-05 完成：真实环境——server 从最新源（4a3bee6）重启、compose-worker 真实合成产出成片 6、无 GUI 等价链路注册节点（binding-ticket → ed25519 设备证明 → register → 本地 bind → runtime-report）。主链 202→Agent 领取→落盘 21875 B→sha 与声明一致→success；success 幂等去重（并发双击零新增）、pending 折叠、取消（cancelled_by_user）、取消后再下（generation 前进 + 磁盘名避让 (2)）；越权/不存在 404 同形、无可信节点 409 15105、未登录 401。清零完成（DB 三表 0、对象 204/404、本地目录删除、绑定解绑），审计行保留见披露。证据 `evidence/T-05.md`。
- T-06 完成：四门全绿——Cloud `go test ./...` exit 0；Agent unittest 705 OK；web vitest 536/536（59 文件）；governance exit 0。验收矩阵 §5 五条对照完成（running→cancel_requested 臂按未复测如实登记；UI 视觉走查并入 2026-10-14 M4 统一验收）。证据 `evidence/T-06.md`，change.md §8 已写。

## Current

无进行中任务。

## Next

归档：CHG085 移入 `delivery/completed/`、LEDGER 更新、工作区独立提交；随后按常设指示开启 CHG086（M4-C8 验收，可自动化项执行、需用户签收项留待晨间统一验收）。

## Blockers

None.

## Recent verification

- 四门收口读数（T-06 表）：Go exit 0 / Agent 705 OK / web 536 全绿 / governance exit 0。
