# Task 23 证据：三页职责重定义——我的素材按钮矩阵 + 下载中心三 Tab + 下载记录生命周期（展示层截断）

- 日期：2026-10-01
- CHG：CHG-20260930-069（用户裁定折入本 CHG 任务 23，不新建 CHG）
- 仓库：`wt-media-cloud`（唯一改动仓）
- 用户裁定四项（执行前确认）：① 折进 CHG-20260930-069；② 生命周期走**展示层截断**（DB 不删不归档，成功 30 天 / 失败 90 天 / 取消 7 天只是显示窗口）；③ 我的素材文件状态列**纯 `download_status`**（去掉 video_status 兜底）；④ 游戏/平台/时间/状态筛选本轮不做。

## 规格核心（用户原话要点）

1. 我的素材按钮由 `usage_status + download_status` 状态矩阵驱动，不直接暴露 `download_task`；
2. 下载中心拆成 进行中 / 失败 / 历史 三 Tab；
3. 完成/失败记录增加生命周期清理策略；
4. 下载中心不承担素材管理；
5. 不展示全部历史下载任务；
6. **任务状态与业务状态严格隔离**。

## 改动（仅 `wt-media-cloud`）

### Part 1 后端：任务列表可筛选 + 暴露 finished_at

1. **`dto.Task` 增可选 `finished_at *time.Time json:"finished_at"`**（无 omitempty——「编码里没有可选键」，缺键与零值不同；nullable 序列化为 `null`）。任务 23 起契约暴露终态完成时间：失败/历史 Tab 需要它来排序与套保留窗口；**不能用 `updated_at`**——它会被租约续租移动。
2. **契约 `contracts/business-schemas/v1/file-transfer.yaml`**：`FileTransferTask` properties 增 `finished_at`（nullable date-time）+ `revision 2026.09.27.1 → 2026.10.01.1`。`contract-map.yaml business_schemas.schema_revision` 未动（`2026.07.14.4`，任务 20 证据确认的独立版本空间）。
3. **`GET /api/v1/file-transfer-tasks` 增三个可选查询参数**（handler + service + repository 三层）：
   - `status`：逗号分隔、空白段丢弃，服务端按 5 档枚举校验，未知值 → `400 10001`「文件传输请求格式错误」；
   - `finished_after`：RFC3339，解析失败 → `400 10001`「finished_after 时间格式无效」；透传为 `TaskFilter.FinishedAfter`，SQL 加 `finished_at >= ?`；
   - `limit`：≤200 封顶、缺省 100（service 默认），解析失败/≤0 → 400。
   - 终态行按构造必有 `finished_at`（cancel/fail/complete/reconcile 都写），NULL 的非终态行自然被窗口排除。
4. 无迁移、无索引改动（`requested_by` 无索引是既有观察，登记不修）。

**先红锚点**：`dto/dto_test.go` `TestTaskMarshalsExactlyTheFrozenPropertySet` 用「Go dto 键集 == yaml 属性集」钉死——只加 `FinishedAt` 后键集失配即红（`want … finished_at`）；补 `finished_at` 进 yaml + 分母 20 属性 / 12 required → 绿。

### Part 2 前端：三 Tab 下载中心

1. `downloadFacts.js` 增 `isFailed(task)`（只有 `failed`）、`isHistory(task)`（success|cancelled）、`withinDays(task, days)`（取 `finished_at`，缺了才退 `updated_at` 兜底）。
2. `transferRows.js` `splitTransferRows` 改三分（active 非终态 / failed / history success+cancelled，一行恰好属于一栏）；`transferRow` 增 `finishedAt`/`finishedText`（终态行写完成时间）。
3. `DownloadCentreDrawer.vue` 三 Tab（进行中/失败/历史），各自空态文案，**每栏各拉各的查询**（`QUERIES` 表 + `daysAgoISO`）：
   - 进行中 `status=pending,running`（仍含云 prepare 兄弟行，客户端 `purpose==='user_download'` 过滤保留在 `transferRows` 之后，`needsCloudPreparation` 不退化）；
   - 失败 `status=failed&finished_after=now-90d`；
   - 历史 `status=success,cancelled&finished_after=now-30d&limit=50`，客户端把 cancelled 再收到 7 天内（`visibleRows` + `withinDays`）。
   - 计数只挂当前栏（三栏各自查询、按需加载，别的栏的数据不在手里）；历史用 `t-table`（素材/大小/完成时间/状态/操作：打开文件·重新下载）。
   - 失败行「详情」打开 `MaterialDetailDrawer mode="transfer"`（只读、无页脚动作——下载中心不承担素材管理，下载动作就在本栏内）。
   - 轮询门加 `activeTab==='active'`：只在停在进行中且有非终态任务时 2s 拉一次；切失败/历史各拉一次、无轮询。
4. `fileTransfer.js` `listTasks(params)` 透传查询参数（http.js 对 undefined/null/'' 跳过）。

### Part 3 前端：我的素材按钮矩阵 + 纯 download_status 列

1. `MyMaterialsPage.vue` `#op` 改状态矩阵（全部平铺 ≤3，无「更多」，§5.6）：

   | usage_status | download_status | 按钮 |
   | --- | --- | --- |
   | removed | 任意 | 详情 / 恢复使用 |
   | active | ''（未下载） | 详情 / 下载 / 放弃使用 |
   | active | downloading | 详情 / 放弃使用（不给主操作：文件已经在准备了） |
   | active | downloaded | 详情 / 加入合成 / 放弃使用 |
   | active | failed | 详情 / 重新下载 / 放弃使用 |

2. `labels.js` `DOWNLOAD_STATUSES` 增 `''` → `未下载`(neutral)；`downloadActionLabel` failed → `重新下载`（原「重试」）。
3. 文件状态列 `fileStatus(row)` 改**纯 `download_status`**（未下载/下载中/已下载/下载失败），去掉 video_status 兜底；云端源文件态（可下载/准备失败）只留在详情抽屉「文件信息」区。

### Part 4 前端：共用详情抽屉 mine 上下文按矩阵

1. `MaterialDetailDrawer.vue` mine 页脚动作同 Part 3 矩阵（removed→恢复使用；downloading→**取消下载**+放弃使用；downloaded→加入合成+放弃使用；failed→重新下载+放弃使用；''→下载+放弃使用）。
2. downloading 时正文「文件信息」卡渲染**下载进度 / 下载速度 / 预计时间**（复用 `transferRow`：progressOf/rateText/etaText，从已拉的 `transfer.listTasks()` 找该素材 pending/running 的 `user_download` 行）+ **取消下载**（`canCancel` → `transfer.cancelTask` → 本地 `cancelRequested`，与下载中心同一条「本机记忆」约定：取消 running 任务后它仍报 running，终态由执行器写）。
3. 详情抽屉的云端文件态（`fileStatus` 的 video_status 兜底）+ 本机下载目录区保留不动（任务 17/20 裁定）。

## 测试

- **Cloud 定向**：dto 键集测试（20 属性 / 12 required 分母，含 finished_at 进 null-keys 清单）；service 四条（`FinishedAfter` 透传 repository、status 枚举映射与拒绝、limit 用调用方或模块默认、终态行带 finished_at）；handler 八条 probe-engine（无参 200、status 拆分/trim/空白段丢弃、finished_after RFC3339、畸形 400、limit 50/abc 400/0 400）；repository sqlmock `TestListTasksAppliesAFinishedAfterBound`（断言 `WHERE requested_by = ? AND status IN (?) AND finished_at >= ? ORDER BY created_at DESC, id DESC LIMIT 50`）。
- **web 定向**：downloadFacts（isFailed/isHistory 不相交、withinDays 含边界 30 天与 0 天、finished_at 优先于 updated_at）；transferRows（三分保序 + finishedAt/finishedText 用 finished_at 而非 updated_at）；labels（'' 未下载 neutral、重新下载）；fileTransfer（带参 URL）；DownloadCentreDrawer（三 Tab、每栏查询参数、历史 t-table、取消 7 天窗口、轮询门 activeTab、三句空态、mode="transfer"）；MyMaterialsPage（矩阵 5 行判据、纯 download_status 列）；MaterialDetailDrawer（mine 页脚矩阵 + downloading 进度/取消/「正在取消」）。

## 读数

- `gofmt -l internal/modules/filetransfer/` → 空
- `go build ./...` → 干净
- `go test -count=1 ./...` → **66 包 ok / 0 FAIL**
- `npx vitest run`（cwd = `web/`）→ **46 文件 / 425 用例全绿**
- 契约核对：`file-transfer.yaml` revision `2026.10.01.1`、dto 键集测试分母 20/12（与 yaml 属性集一致）、`contract-map.yaml business_schemas.schema_revision` 未动（`2026.07.14.4`，任务 20 证据确认的独立版本空间）。

## 相关提交

- `wt-media-cloud`（本任务提交 `5091ce3`，走查修正 `560b875`）
- 本 Workspace（证据 + checkpoint + change.md §5 任务 23，随本记录提交）

## 走查修正（2026-10-01，抽屉尺寸）

用户反馈「下载中心的弹窗可以参考详情的弹窗，需要更大一些的组件」：下载中心 `t-drawer` 尺寸 `min(46vw, 640px)` → `min(62vw, 880px)`（与 `MaterialDetailDrawer` 同宽）。旧宽度下历史表格五列（素材/大小/完成时间/状态/操作 ≈720px）必然横向滚动，新宽度整表一屏放得下。新增测试钉住尺寸防回退。读数：全量 vitest（web/ 下）**46 文件 / 426 用例全绿**、`build:cloud` 与 `build:desktop` 均 exit 0（均在最后一次改动之后重跑）。提交 cloud `560b875`。

## 走查修正（2026-10-01，第二轮：标题溢出 + 去「重试」+ 每素材一行）

用户本轮走查提三条，全部折进任务 23（同 CHG，不新建）。用户两项裁定：**A.「重试」与「重新下载」合并为单一「重新下载」**（前后端一起清）；**B. 每个素材一行 + 已成功的不能再次下载**。

### Part 1 历史 Tab 标题冲出边界（前端 CSS，根因在行内元素）

`DownloadCentreDrawer.vue` 的 `.transfer-table__title` **三件套齐全但不生效**：它是个行内 `<span>`，`overflow/white-space/text-overflow` 在行内元素上不产生裁切盒子，长标题直接压出单元格。补 `display: block; max-width: 100%;`（对齐同仓可用写法 `.material-title`，`MyMaterialsPage.vue:308`），三件套原样保留。断言用模板读 `.transfer-table__title` 规则块，钉住 `display: block` 与 `max-width: 100%`。

### Part 2 去掉「重试」，失败行只留「重新下载」（前端 + 后端 + 契约）

根因是两个动作对同一行同时成立：`canRetry`（failed 且 attempts 有余、非等待类错误码）走 `retryTask` **复用原行**；`canRedownload`（failed/cancelled 恒真）走 `createDownload` **新建一行**。后端既有注释（`service.go`）已写明等待云端准备而失败的行「出路是 new download 而不是 retry」——即「重新下载」才是一律成立的那个动作。

- **前端**：`DownloadCentreDrawer.vue` 删 `retry()` 与两处「重试」按钮（进行中栏本就恒不成立，一并清掉死按钮）；`transferRows.js` 行对象去掉 `canRetry`；`downloadFacts.js` 删 `canRetry` 与 `WAITER_RELEASE_CODES`；`shared/api/fileTransfer.js` 删 `retryTask`（删后全仓无调用方）。
- **后端**：`router.go` 删路由、`handler.go`/`service/operations.go`/`service/service.go`（含 Store 接口那行）/`service/store_adapter.go`/`repository/store_mysql.go` 逐层删除。**`cloudagent` 模块的同名 `RetryTask` 是另一功能，未触碰**。
- **契约**：`contracts/cloud-api/v1/file-transfer.openapi.yaml` 删 `/api/v1/file-transfer-tasks/{task_id}/retry` path，`info.version` `2026.09.26.2 → 2026.10.01.1`；`contracts/cloud-api/README.md` 去掉 retry 字面。该 openapi 是文档性契约（`dto_test` 的键集锚点指向另一个文件 `cloud-agent-api`，不校验此文件），版本号的判别力在于「与 path 集合同步」而非机器校验——如实登记。

### Part 3 每个素材一行（前端展示层收敛 + 后端幂等去重）

**先说清这不是 DB 错**：`reference/state-models/README.md` 规则 4/5——`file_transfer_task` 记录**过程**、`material` 记录**资产**，执行记录默认保留。重复的来源有两处，都不该靠删数据解决：
1. `createUserDownloadTask` 的去重键带**代次** `userDownloadDedupeKey(assetID, userID, assignedNodeID, finished+1)`，`finished` = 终态行数（`store_mysql.go`）——每次进入终态后再点就是新代次 = 新行；
2. 每栏各查各的 `status`，同一素材的失败行与成功行会**跨栏各出现一次**。

收敛口径与「我的素材」的派生（`production/service.go` `downloadStatusOf` ← `LatestUserDownloadStatuses` **取该素材最新一条 user_download**）对齐。

- **前端**：`DownloadCentreDrawer.vue` 改**一次查询 + 客户端按素材收敛**——`listTasks({ limit: 200 })`（不带 `status`/`finished_after`：`finished_after` 会把 `finished_at` 为 null 的非终态行滤掉，不能用），`transferRows(...)` → `purpose === 'user_download'` 过滤（仍保留在 `transferRows` **之后**，`needsCloudPreparation` 不退化）→ 按 `asset_id` **首见去重**（服务端顺序 `created_at DESC, id DESC`，首见即最新）。分栏按最新任务的 `status` 归栏，窗口在客户端套（失败 90 天；历史 success 30 天、cancelled 7 天）。删掉 `QUERIES`/`daysAgoISO` 那套按栏查询。轮询门不变（`visible && activeTab==='active' && hasLiveTask(liveDownloads)`）。任务 23 已加的三个后端参数**保留不回退**（`limit` 仍在用，`status`/`finished_after` 成为可选能力）。
- **后端**（防客户端绕过）：`createUserDownloadTask` 事务闭包开头先查该（素材, 用户, `user_download`）**最新一条**任务的 `status`，若为 `success` 则**直接返回那条既有行**（不新建代次）。做成**最新一条**而非「任意一条成功」是为了与 `LatestUserDownloadStatuses` 同口径——那正是界面上「已下载」标签的来源，两者不一致会让「显示已下载」与「还能再下」同时成立。

### Part 4 「已成功的不能再次下载」

`downloadFacts.canRedownload` 去掉 `success && presence === absent` 那支（连带 `presence` 参数），只对 `failed`/`cancelled` 为真；下载中心那句「文件已不在本机已知的保存位置，可以重新下载」去掉后半句承诺，只陈述事实（`rows` 里成功行的 `canRedownload` 因此恒假，`transferRows.test.js` 三条读数为证）。

### 测试（先红后绿）

- **web 定向**：`DownloadCentreDrawer.test.js` 重写 tabs 块（单一查询、按素材收敛成一行、按最新任务归栏、三栏窗口、失败行只有 `重新下载`+`详情`）；新增「无 retry 按钮与 retry 调用残留」与「历史标题在单元格内被裁切」（断言 `display: block` / `max-width: 100%`）；`downloadFacts.test.js` 去 `canRetry`、`canRedownload` 只认 failed/cancelled；`transferRows.test.js` 钉 `'canRetry' in row === false`、成功行 `canRedownload === false`；`fileTransfer.test.js` 去 retry；`labels.js` failed 主操作词「重试」→「重新下载」。
- **Cloud 定向**：`handler_test.go` 路由表去掉 retry 行（路由表被整表钉住，少一行即红）；`service_test.go`/`store_mysql_test.go` 去掉 RetryTask 用例；新增 `TestCreateUserDownloadTaskRepeatsAnAlreadySuccessfulDownload`（sqlmock：最新为 success → 返回既有行、不新建；最新为 failed → 照常新代次）。

### 读数

- `gofmt -l internal/modules/filetransfer/` → 空（新增 sqlmock 常量块对齐用单文件 `go fmt` 修平；**未**整仓 `cargo fmt`/全仓格式化）
- `go build ./...` → 干净；`go test -count=1 ./...` → **66 包 ok / 0 FAIL**
- `npx vitest run`（cwd = `web/`）→ **46 文件 / 428 用例全绿**（上一轮走查修正时实测 426；本轮净 +2——删掉 retry 相关用例的同时新增了裁切与去 retry 断言）
- `build:cloud` 与 `build:desktop` 均 exit 0（均在最后一次改动之后重跑）；两个 `npm run` 都必须在 `web/` 下落跑——在仓根跑是 `ENOENT: …/wt-media-cloud/package.json`（与 vitest 同一条规矩），第一次就这么误跑了一次，改目录后 `rc=0` 才是真读数
- 契约：`file-transfer.openapi.yaml` `2026.10.01.1`、无 retry path；`contract-map.yaml` 未动

### 与计划不符 / 边界

- **一处与计划文字不符（如实登记）**：计划 Part 2 写「删两处『重试』按钮（进行中 309、失败 334）」，实际只有失败栏那一处是真按钮，进行中栏的 `canRetry/canRedownload/canOpen` 在该栏恒为假——按计划把这几个死条件一并清掉，只留「取消」。
- **待确认项按批准执行**：Part 4 后，「文件已下载成功但本机文件被删」的素材没有重新下载入口（我的素材对该态本就给「加入合成」），按用户原话「已成功的不能再次下载」一律不重下。
- 不删 DB 任何执行记录；不做素材状态机重构；`cloudagent` 的同名 `RetryTask` 不动；不动节点注册/绑定。

## 验证 / 剩余（m2b 重建走查）

前端有变 → 整跑，但**不碰 8765 Agent 的 runner 入口**（沿用节点绑定约束）：

- 下载中心三 Tab：进行中（点下载 → 下载中/进度/取消）；失败（造一次失败 → 原因/时间/重新下载）；历史（成功行表格式、打开文件；>30 天成功与 >7 天取消不出现——可用旧数据验证窗口）；
- 本轮四条新增核对：① 历史 Tab 里超长标题被省略号裁在单元格内、不压出边界；② 失败栏每素材一行、只有「重新下载」+「详情」，全站无「重试」入口；③ 同一素材多次下载只显示最新一条（不是每代次一行）；④ 已成功的素材无法再下载（行上只有「打开文件」，点下载入口不会新建任务）；
- 我的素材矩阵 5 行逐一核对按钮；文件状态列纯四态；详情抽屉 downloading 显示进度/速度/ETA + 取消下载；
- 取消后行落「已取消」进历史（7 天窗口内）。

## 边界 / 不做

- 游戏/平台/时间/状态筛选本轮不做（用户裁定④）；
- 不做 DB 删除/归档 job、不加 `requested_by` 索引（展示层截断即可；登记观察）；
- 不从详情抽屉移除云端文件态（文件信息区保留 video_status）；素材库页不加下载状态；
- 不改两阶段取消机制、不动节点注册/绑定。
