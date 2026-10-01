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

- `wt-media-cloud`（本任务提交，见文末 commit）
- 本 Workspace（证据 + checkpoint + change.md §5 任务 23，随本记录提交）

## 验证 / 剩余（m2b 重建走查）

前端有变 → 整跑，但**不碰 8765 Agent 的 runner 入口**（沿用节点绑定约束）：

- 下载中心三 Tab：进行中（点下载 → 下载中/进度/取消）；失败（造一次失败 → 原因/时间/重新下载）；历史（成功行表格式、打开文件/重新下载；>30 天成功与 >7 天取消不出现——可用旧数据验证窗口）；
- 我的素材矩阵 5 行逐一核对按钮；文件状态列纯四态；详情抽屉 downloading 显示进度/速度/ETA + 取消下载；
- 取消后行落「已取消」进历史（7 天窗口内）。

## 边界 / 不做

- 游戏/平台/时间/状态筛选本轮不做（用户裁定④）；
- 不做 DB 删除/归档 job、不加 `requested_by` 索引（展示层截断即可；登记观察）；
- 不从详情抽屉移除云端文件态（文件信息区保留 video_status）；素材库页不加下载状态；
- 不改两阶段取消机制、不动节点注册/绑定。
