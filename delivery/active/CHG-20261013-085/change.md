# CHG-20261013-085：M4-C7 下载中心（成片下载接入统一 file_transfer_task）

- Status: IMPLEMENTING
- Level: L
- Milestone: `delivery/milestones/M4-content-production.md`
- Closure anchor: §3.1 M4-C7「下载中心」；§6 闭环卡 M4-C（下载与发布衔接）；验收矩阵 M4-AC-08 的下载侧
- Product: `docs/product/prd/详细文档/第五章_素材生产.md` §5.9.6–5.9.11、§5.10.5
- Engineering: `docs/engineering/specs/2026-09-24-m4-m5-cloud-content-production.md` §3.6、§8（权限行）、§9（排除项）
- Decision: `docs/decisions/0017-m4-m5-cloud-owned-content-production.md`（对象集：唯一横向文件对象 `file_transfer_task`）
- Affected repositories: `wt-media-cloud`（含 Cloud Web/Desktop 共用页面源码）、`wt-media-agent`
- Current repositories: `wt-media-cloud`、`wt-media-agent`
- Activation: CHG-20261013-084（M4-C6 我的成片）已归档；用户指示 M4 剩余 CHG 连续执行、不等待单项验收，2026-10-14 晨统一验收。按里程碑顺序进入 M4-C7。

## 1. 独立结果

原素材与成片共用同一个下载中心（顶部导航「下载」右侧 Drawer）与同一张 `file_transfer_task` 表：成片可从「我的成片」发起下载到运营电脑，Local Agent 领取、短时授权下载、原子落盘、校验字节数与 SHA256 后回报；Drawer 展示真实进度/速度/剩余时间，支持取消与失败重下；成功后可打开文件/目录；清理显示记录不删除素材、成片或本地文件。Cloud 不保存运营电脑绝对路径。

## 2. 范围

- 合同：`asset_type` 由 `const material` 放宽为枚举 `material | composite_output`（`contracts/business-schemas/v1/file-transfer.yaml`、`contracts/cloud-agent-api/v1/file-transfer.openapi.yaml`，version bump）；`content-production.openapi.yaml` 新增 `POST /compose-outputs/{output_id}/downloads`（202 + 409 语义），version bump。
- Cloud：`AssetCompositeOutput` 常量与 `CreateTask` 参数化；`CreateUserDownloadTask` 去重键的 asset_type 参数化；`POST /compose-outputs/:output_id/downloads` 路由 + handler + service（复用 `ComposeOutputService.readable` 范围门；成片行必持已验证对象，无 prepare/依赖链）。
- Agent：transfer 领取门放宽接受 `composite_output` 租约；任务类型按 asset_type 分派；成片下载的落盘命名规则（game_name 缺省回退、无 published_at）。
- Web（Cloud/Desktop 共用）：Drawer 与 `downloadFacts` 的 asset_type 分支——成片行的重下走成片下载端点、标题回退「成片 #id」、文件名投影不排除 output；`compose.js` 新增 `createOutputDownload`。
- 审计：成片下载创建/取消入审计（沿用既有 transfer 审计路径）。
- 真实环境验收与全量回归。

## 3. 明确不做

- 不新增成片下载任务表或第二套下载记录（spec §9 排除）。
- 不把运营电脑绝对路径存入 Cloud（`file_transfer_task` 无本地路径列，Local Agent 本机可信存储管理）。
- 不实现断点续传的暂停/继续 UI（执行器未支持分片断点续传时不展示，PRD §5.9.9）。
- 不实现下载成功→发布事实（`publication` 属 M6）。
- 不修改 Desktop 原生代码（open/reveal/presence 均按文件名工作，成片文件落盘后即用）。
- 不做 compose_output 的 cloud prepare（成片行必持已验证对象，`dependency_task_id` 机制本 CHG 不触碰）。
- 不改素材下载徽章投影 `LatestUserDownloadStatuses`（成片列表徽章非本 CHG 范围，PRD 未要求）。

## 4. 有序任务与验收

| Task | 实施结果 | 验证 |
| --- | --- | --- |
| T-01 | 合同：asset_type 枚举放宽（两份契约 version bump）+ `POST /compose-outputs/{output_id}/downloads` 端点定义 | YAML 解析 + 冻结名/键集比对测试 |
| T-02 | Cloud：model/常量、`CreateTask`/去重参数化、成片下载路由 + service（readable 门、无 prepare） | 单测 + sqlmock（越权 404、重复创建去重、202 语义） |
| T-03 | Agent：租约接受 composite_output、按 asset_type 分派、成片命名规则 | pytest（租约解析门、命名、错误码路径） |
| T-04 | Web：Drawer/downloadFacts 的成片分支 + `createOutputDownload` 客户端 | vitest（钉住成片行重下与文案、不回退素材分支） |
| T-05 | 真实环境：建任务→成片→发起下载→Agent 真实领取→本地文件 + sha 校验→读回 success；越权/去重/取消探针；验收数据清零（本地文件与显示记录处置披露） | 真实环境探针 + 前后对照 |
| T-06 | 全量回归与证据收口（Go 全量、agent pytest 全量、web 全量、governance） | 三仓套件 + governance exit code |

## 5. 验收标准

1. 成片与原素材出现在同一 Drawer、同一任务表；Drawer 行展示资产类型与真实进度。
2. 成片下载从创建到本地文件：短时授权、字节数与 SHA256 校验、原子落盘、`success` 读回；本地路径不入 Cloud。
3. 越权发起（范围外成片）404 同形；重复发起按去重语义不产生并行任务；取消 pending 立即终态、running 走 cancel_requested。
4. 失败可重下（新任务、generation 递增）；清理显示记录不删素材/成片/本地文件。
5. 下载成功不产生发布事实、不翻转 `publish_status`。

## 6. Pending Questions

None.

## 7. 范围裁定（规划期，依据 PRD/工程规格与代码现状裁定）

- **合同放宽非破坏**：`const material → enum [material, composite_output]` 是向后兼容加宽（旧实例仍合法）；两个消费方（Agent 租约门、web downloadFacts）在同 CHG 内更新并补契约测试，满足 breaking-change-policy 的实质要求，无需新决策记录。
- **无 prepare 链**：成片行只在对象落盘+校验后创建（CHG083/084 已证），下载直接对 `composite_outputs.object_key` 签发短时 GET；不触碰 `dependency_task_id`/`HandOverDependencies`。
- **去重语义**：沿用素材的用户级去重形状——(asset_type, asset_id, requested_by, assigned_device_id) + generation 递增；asset_type 进去重键参数化。
- **成片落盘命名**：沿用 `game_name/日期/文件名` 目录形状；成片无 title/published_at，文件名用「成片-<output_id>-<日期>.mp4」形（game_name 来自成片 game_id 的游戏名，缺省回退「未分类」）。Agent 常量 `TASK_TYPE_MATERIAL_DOWNLOAD` 泛化为按 asset_type 分派，不新建执行器文件。
- **Drawer 详情**：成片行不打开 MaterialDetailDrawer；详情入口指向「我的成片」页（`/finished-media`）。
- **Agent 任务类型**：不新增云端 task_type 字段值——领取返回的租约本身含 asset_type，Agent 侧按它分派到同一 MaterialDownloadExecutor（参数化命名与校验路径）。
