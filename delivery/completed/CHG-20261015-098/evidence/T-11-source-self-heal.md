# T-11 素材文件缺失自愈、准备重试与上传校验（M4-H2 走查整改）

Date: 2026-10-22
Status: MACHINE_VERIFIED; LIVE_SELF_HEAL_VERIFIED（未含用户签收；用户下载端到端与并发未在本机复现）
Cloud: `c2e3261`（28 个文件；提交前重跑 Go 测试、Web 测试与双端 Web 构建）
Workspace: 本文件与 ADR-0017、工程规格、PRD 第五章、M4 里程碑、checkpoint 同轮提交

## 本轮形态

2026-10-21 走查中合成任务 319/320/321 均因「源文件不见了」失败：素材 154/160/159 的
`video_status=ready` 与 `source_object_key` 均在，但对象存储中对应对象已不存在。用户裁定：

1. 清理范围仅限云端本地临时文件/临时对象，正式素材与正式成片保留；
2. `ready` 但对象丢失时，对象在则直接用，不在则重新解析平台地址、下载并补回云端；
3. `video_status=failed` 时自动重试准备一次；
4. 上传完整性用 Content-MD5，取消「上传后回读再比 SHA256」。

代码事实源：`docs/decisions/0017-m4-m5-cloud-owned-content-production.md` 增补记录、
`docs/engineering/specs/2026-09-24-m4-m5-cloud-content-production.md` §3.1/§4.4/§5.6/§5.7/§6.3/§10、
PRD 第五章 §5.3.4/§5.3.5/§5.6.3/§5.6.4/§5.8.4/§5.8.5/§5.9.7/§5.9.14。

## 修改

**云端（`wt-media-cloud`，`c2e3261`）**

- 合成消费前校验与一次自愈：`internal/modules/production/service/execution.go` 新增
  `ComposeInputGate` 与分支表；`internal/jobs/compose_worker.go` 每次 claim 新建 gate、WaitInput 循环复用。
- 素材受控回退：`production/repository/store_mysql.go` 新增 `MarkVideoRepreparing`
  （`ready` + 观察到的 key + `video_prepared_at <=>` 双条件）；放宽 `MarkVideoPreparing`
  （接受 ready 且空 key）与 `MarkVideoFailed`（允许空 key 的 ready）。
- 用户下载/预览：`production/service/service.go` 消费前 `ObjectExists`；对象丢失且有源地址时
  建准备依赖，无源地址返回 `ErrMaterialUnavailable`（409）；`CreateDownload` 插入后立即
  `AttachCompletedDependency`。
- 准备 worker：`internal/jobs/material_prepare.go` 把地址解析 + 下载抽成一次 fetch，
  `codeDetailFailed`/`codeFetchFailed` 同任务内重解析重下一次；失败写入以 `FailTask` 生效为前提；
  上下文取消不写终态。
- 成功挂接竞态：`filetransfer` 完成时写 `source_object_key`；新增 `AttachCompletedDependency`
  与周期 `ReconcileCompletedDependencies`（`internal/jobs/transfer_reconcile.go` 计入日志计数）。
- 上传校验：`internal/infra/storage/minio.go` 的 `Put` 启用 `SendContentMd5`；
  `production/service/execution.go` 与 `production/compose/upload.go` 只保留 `Stat` 大小，删除回读逻辑。
- 前端：`web/src/modules/compose/pages/ComposeTasksPage.vue` 的 `statusText`
  把 `running + waiting_input` 显示为「等待素材准备」。

## 自动验证（最后一次代码改动之后）

- Cloud `go build ./...`：exit 0。
- Cloud `go test ./... -count=1`：**85 个包行 = 73 `ok` + 12 `no test files`，`FAIL` 0，exit 0**。
  （最后一次改动是对 `internal/jobs/material_prepare_test.go` 的 `gofmt -w`，格式化后整套复跑，读数不变。）
- Web `npm test -- --maxWorkers 2`：**77 文件 / 721 测试全部 PASS，exit 0**。
- `npm run build:cloud` 与 `npm run build:desktop`：均 exit 0。
- 新增/改写用例（节选）：
  - `production/service/execution_test.go`：ready + Stat 404 → 一次 Ensure + WaitInput；同 gate 第二轮
    仍 404 → `input_missing`；准备后新 key → 同一 gate 成功且 staged 字节为新文件；failed → 先等待再
    `input_invalid`；downloading → 不重复请求；ready + 空 key → 等待；`Stat` 非 404 → `storage_error`。
  - `jobs/compose_worker_test.go`：同一 claim 的等待循环复用同一 gate 指针，重新 claim 得到不同指针。
  - `production/service/service_test.go`：对象存在直下；对象缺失 → Ensure + `MarkVideoRepreparing` +
    依赖；Mark 被拒后重读三分支；无源地址 409；预览 409 与存储错误区分；挂接成功返回新任务体。
  - `filetransfer/repository/store_mysql_test.go`：完成 SQL 写 `source_object_key`；挂接只复制
    已完成的依赖；对账覆盖 attach 谓词排除的行并计 3 行。
  - `jobs/material_prepare_test.go`：地址失败重试一次、下载中断重试一次、`codeAddressMissing` 不重试；
    上下文取消不写任何终态。
  - `web/src/modules/compose/pages/ComposeTasksPage.test.js`：`waiting_input` 文案与两处徽标绑定。
- 存储侧 Content-MD5 前提（本机 Garage，dev 桶）：
  - 内容 `wt-md5-probe`、故意错 MD5 → HTTP **400**，响应
    `InvalidDigest: MD5 checksum verification failed (from content-md5)`；
  - 同字节、正确 MD5 → HTTP **200**；
  - 探针对象已删除，DELETE **204**。
  结论：本机对象存储确实校验 Content-MD5；错/对两侧都做过，不是「一律拒绝」的空转。

## 真实环境自愈读回

环境：`scripts/m2b-local-acceptance.sh up --force-restart` 重启完成，Cloud HTTP pid 2054、
Discovery Worker pid 2078、Compose Worker pid 2098（01:11:32 启动），BitBrowser via Agent PASS。
手动重试用 admin 登录后的 `POST /api/v1/compose-tasks/{id}/retry`，三次均 HTTP 200。

### 任务 319 / 素材 154

- 重试后：任务 `running / waiting_input / attempt 2`；素材 154 `ready → downloading`（CAS 回退，
  `updated_at` 01:11:47.769），同一 `source_object_key`。
- 新准备任务恰好 1 条：`transfer_9654427bb782ac7db7fa709c`，`compose_input_prepare / cloud`；
  01:12:10.573 success，`integrity_bytes = total_bytes = 71,962,320`，`source_object_key` 回写。
- 素材 154 01:12:10.569 回到 `ready`，`video_size_bytes = 71,962,320`。
- 任务 319 01:12:18.736 success，attempt 2；步骤日志 4 步（`prepare_input` 4,161ms →
  `cut` 2,036ms → `upload` 516ms → `commit` 51ms）。
- 成片 63：`compose-outputs/319/2/output.mp4`，2,211,882 B，
  SHA256 `6b7a52483b743c64473101f20a33b75e459d868101318939795cc7107d668e62`。
- 对象下载后本地复算 SHA256 与库内一致，字节数一致（三方闭合）。
- 清理：`compose_task_attempts.staging_cleaned_at = 01:12:33.501`；
  `compose-staging/319/` KeyCount 0、`compose-outputs/319/` 仅 `2/output.mp4`、
  `materials/154/.staging/` KeyCount 0。

### 任务 321 / 素材 159

- 重试后进入 `waiting_input`；素材 159 `ready → downloading`，新准备恰好 1 条：
  `transfer_e40b7ac88c5388c6c2fda10b`，01:13:28.490 success，73,342,566 B。
- 任务 321 01:15:33 前 success（attempt 2），成片 64：
  `compose-outputs/321/2/output.mp4`，126,508,784 B；`staging_cleaned_at = 01:15:33.477`。
- 清理：`compose-staging/321/` KeyCount 0、`compose-outputs/321/` 仅 1 个对象、
  `materials/159/.staging/` KeyCount 0。

### 任务 320 / 素材 160（同时作为 stale-ready 预览样本）

- 为验证 stale ready，先删除素材 160 的正式对象（DELETE 204）。此时预览
  `GET /api/v1/materials/160/video-url` → **409**，`errcode 15005`，
  `error.type = material_unavailable`，未签发 404 签名地址。
- 用户下载 `POST /api/v1/materials/160/downloads` → **409**，`errcode 15105`,
  `local_transfer_node_unavailable`：本机没有新鲜的受信 Local Agent 节点，请求在创建依赖前被拒绝。
  **该分支未在本机端到端复现**（见「未覆盖」）。
- 重试任务 320 后：素材 160 `ready → downloading`，新准备恰好 1 条
  `transfer_dc2ce31928a191c247aef8b3`，01:17:13.048 success，162,200,269 B；
  任务 320 01:21:03 success（attempt 2），成片 65：
  `compose-outputs/320/2/output.mp4`，250,546,703 B；`staging_cleaned_at = 01:21:03.482`。
- 对象恢复后预览同一条 → **200**，返回预签名 URL。
- 清理：`compose-staging/320/` KeyCount 0、`compose-outputs/320/` 仅 1 个对象、
  `materials/160/.staging/` KeyCount 0。

### 次数与边界

- 三次自愈各新增 **1 条云端准备任务**、**1 个素材暂存对象**、**1 个成片临时对象**；
  同一 attempt 下没有出现第二个成片临时对象，也没有重复上传。
- 正式素材对象（`materials/154|159|160/<sha256>.mp4`）与正式成片对象均保留。
- `.compose/task-320-*` 等本轮 run 目录已删除；仅存在历史的 `.compose/task-23-*`，
  早于本轮且不在本轮清理范围（崩溃残留启动清扫未实现，见 §七）。

## 未覆盖 / 未验证

1. **用户下载端到端未在本机复现**：本机是 headless 环境，`local_agent_nodes` 无新鲜受信节点，
   `CreateDownload` 在对象校验之后、建依赖之前返回 409 `local_transfer_node_unavailable`。
   对象缺失的 409、对象恢复后的 200 已验证；「建依赖 → 准备 → `AttachCompletedDependency`
   → Local Agent 直下」只有自动测试覆盖，须在新打包 Desktop 的 M4-H2 走查中复验。
2. **真实并发未复现**：第五轮裁定「一条 (策略,素材) 只跑一次」使同一素材无法由两条不同策略
   同时建任务；开发库中不存在两个可同时领取的合法 (策略,素材) 组合。本次没有为制造并发而
   直插任务行。并发去重与每 claim 一次自愈仅由自动测试覆盖。
3. **准备失败自动重试一次未在真实平台触发**：未人为制造抖音临时地址过期；由
   `material_prepare_test.go` 的地址失败/下载中断两条用例覆盖。
4. 未删除 `wt-media-cloud/.compose/task-23-*` 历史目录；崩溃残留启动清扫不在本轮范围。
5. 不把本证据当作 M5-AC-13 或 M4-H2 的用户签收；页面可视走查与 Desktop 真实下载仍由用户完成。
