# Task 20 证据：下载中心一次点击一条记录 + 素材页「文件状态」补全下载生命周期

- 日期：2026-10-01
- CHG：CHG-20260930-069（并进任务 20，用户裁定）
- 仓库：`wt-media-cloud`（后端 + 前端）
- 提交：见文末

## 背景

两个相关诉求一次交付：

1. **下载中心一次点击显示两条记录**（`compose_input_prepare` 云准备 + `user_download` 本机下载，同一毫秒同建）。用户裁定：**显示层合并**——一次点击只显示一条，用状态区分阶段。DB 保持两行：云准备是 M4-B/M5 合成管线预留的共享输入准备契约，CHECK 约束/去重键/租约模型/执行器都建立在两行协作上；Python Agent 只执行 `user_download`。
2. **素材页「文件状态」补全下载侧生命周期**。现状只反映云侧副本（未准备/准备中/可下载/准备失败），不反映本机下载。用户裁定（逐条）：后端派生下载状态；有成功下载即「已下载」（覆盖式）；排队到传输都算「下载中」；准备失败与本地下载失败统一「下载失败」（用户不关心哪一段失败，知道重试即可）。下载中心保留细分阶段。

## 关键实现顺序（Part A 的唯一坑）

`transferRows` 把完整 `tasks` 传给 `taskState → needsCloudPreparation`（downloadFacts.js）做「等待云端准备」兄弟行扫描；**过滤必须在 `transferRows` 之后**，否则提前滤掉云侧行会把它退化成「排队中」。故：

```js
const rows = computed(() => transferRows(tasks.value, { … }).filter((row) => row.task.purpose === 'user_download'))
const liveDownloads = computed(() => tasks.value.filter((task) => task.purpose === 'user_download'))
```

测试 `DownloadCentreDrawer.test.js` 钉住：`block.indexOf('transferRows(tasks.value') < block.indexOf(".filter((row)")`（顺序）+ 轮询闸门 `hasLiveTask(liveDownloads.value)`。

## 后端侧测试（先红后绿）

- 命令：`gofmt -l internal/modules/`（空）、`go test -count=1 ./...`
- 预期：filetransfer 新增仓存查询 `LatestUserDownloadStatuses`（两条 sqlmock：多条取最新、空 ID 列表不查询）+ service（透传用户、`userID <= 0` 拒绝）；production `downloadStatusOf` 映射（pending/running→downloading、success→downloaded、failed/cancelled→failed、''→空）+ `ListMyMaterials` 派生写入（stub `LatestUserDownloadStatuses`，断言 `DownloadStatus`）；wire_test 分母 9 → 10 且键集 = 契约属性集。
- 实际：66 包 ok / 0 FAIL。中间修平：`stubTransfers` 缺接口方法、wire_test 需把 `removed.DownloadStatus` 设值才覆盖 download_status 键、`slices` 未导入、`model.VideoReady` 常量名（无 `MaterialVideoStatusReady`）、`material30` 未用变量。
- 状态：PASS

## 前端侧测试（先红后绿）

- 命令：`npx vitest run`（cwd = `web/`，Vite root 必须是 web/）
- 预期：labels 三档常量（下载中/已下载/下载失败）且 `VIDEO_STATUSES` 冻结数组不动；MyMaterialsPage 文件状态 cell 按 download_status 优先 + video_status 兜底；MaterialDetailDrawer 从 `transfer.listTasks()` 就地派生；DownloadCentreDrawer 过滤在 transferRows 之后 + 轮询闸门。
- 实际：全量 159/159 用例全绿；三个改到的 SFC 经 compiler-sfc 编译通过。
- 状态：PASS

## 改动（wt-media-cloud `e940ecd`）

### 后端

- `internal/modules/filetransfer/repository/store_mysql.go`：`LatestUserDownloadStatuses`（`requested_by=? AND asset_type='material' AND purpose='user_download' AND asset_id IN (…)`，`ORDER BY created_at DESC, id DESC` 首见去重 = 每条素材最新一条；空 materialIDs 直接返回空表）+ 对应仓存测试两条。
- `internal/modules/filetransfer/{service/store_adapter.go,service/operations.go}`：Store 接口 + service 方法 + wired 函数。
- `internal/modules/production/service/service.go`：`TransferCreator` 接口增 `LatestUserDownloadStatuses`；`ListMyMaterials` 建好 `visible` 后批量查、`visible[i].DownloadStatus = downloadStatusOf(statuses[materialID])`；helper `downloadStatusOf`/`materialIDsOf`。
- `internal/modules/production/model/model.go`：`MaterialUsage` 增 `DownloadStatus string json:"download_status,omitempty"`（与 `status` 平级、按用户派生；`''`=无）。
- `internal/modules/production/{service/store_adapter.go,wire_test.go}`：adapter 接线；wire_test 分母 10、`removed.DownloadStatus="downloaded"`。

### 契约

- `contracts/business-schemas/v1/content-production.yaml`：`MaterialUsage` properties 增**可选** `download_status` enum [downloading, downloaded, failed]（从未下载过时该键不出现），revision `2026.10.01.1`；冻结 `video_status` 不动。

### 前端

- `web/src/modules/materials/labels.js`：`DOWNLOAD_STATUSES=['downloading','downloaded','failed']` + labels 下载中/已下载/下载失败 + tones info/success/danger；`VIDEO_STATUSES` 未动。
- `web/src/modules/materials/pages/MyMaterialsPage.vue`：`toRows` 带 `download_status`；文件状态 cell = download_status 优先 + video_status 兜底（`failed` 也「下载失败」）。
- `web/src/modules/materials/MaterialDetailDrawer.vue`：`deriveDownloadStatus(tasks, assetId)` 从已拉的 `transfer.listTasks()` 就地派生（mine 上下文 watch），`fileStatus` computed 同语义。
- `web/src/modules/transfer/DownloadCentreDrawer.vue`：Part A 过滤 + 轮询闸门。
- 三个 SFC 对应测试 + labels 测试。

## 边界（既定语义，已固化 §2/§3/§4/§5）

- 「下载中/已下载/下载失败」按**最新一条 user_download** 决定；素材云侧状态只在无下载记录时兜底。重新下载 = 新任务，状态随之切换。
- 素材库页 `MaterialLibraryPage` 无用户关系语义，不加这些下载状态。
- 判定只看 `user_download` + 该用户；不看 `compose_input_prepare`（云准备只通过 `video_status` 兜底参与）。
- DB 两行不动、`file_transfer_tasks` 无变化、零迁移；`video_status` 枚举与 使用状态 字段未动。

## 相关提交

- `wt-media-cloud` `e940ecd`（`feat: 下载中心一次点击一条记录 + 素材页文件状态补全下载生命周期`，20 文件 +519/−21）
- 本 Workspace（证据 + checkpoint + change.md §2/§3/§4/§5 任务 20，随本记录提交）
