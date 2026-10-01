# CHG-20260930-071：素材状态写路径与使用情况统计

- Status: PLANNED
- Level: `M`
- 激活条件：`CHG-20260930-069` 关闭归档后，按 `delivery/planned/README.md` 的队列顺序激活（`delivery/active` 同一时间只允许一个活跃 CHG）。
- 来源：2026-09-30 素材库走查四轮，用户带设计图并裁定「先落纯交互层，后端另立 CHG」（交互层那半由 CHG-20260930-069 任务 9 承载）。
- **范围收窄（2026-09-30 走查六轮）**：原「素材状态维度」的后端读取那半已由 CHG-20260930-069 任务 12 交付——`materials.status`（`available / paused / delisted`，`NOT NULL DEFAULT 'available'`）、Business Schema `Material.status`、投影与 `wire_test` 分母、两处页面读真值，提交 `71deb48`。本记录只剩两件事：素材状态的**写路径**（谁来暂停 / 下架、在哪一页操作、对已有 `material_usage` 与 `compose_task` 生效到哪一步）与**使用情况统计**。§0 盘点表里标注「已交付」的行不再属于本记录。

## 0. 这份草案还没有可执行的范围

下面是 2026-09-30 后端能力盘点的实测结论与需要用户裁定的事项。**§4 的 Q-01、Q-03～Q-06 关闭之前，本记录不具备可执行范围**，不得据此开始迁移、契约或实现——按 `AGENT-INDEX.md` §4，产品语义未定的部分不靠实现倒推。（Q-02 已于走查六轮关闭，见 §4。）

盘点结论（`wt-media-cloud`，2026-09-30 只读核对）：

| 设计图要求的 | 实测 | 证据 |
| --- | --- | --- |
| 素材状态（可用 / 已暂停 / 已下架）**列与读取** | **已交付**（CHG-20260930-069 任务 12，`71deb48`）：`migrations/20260930_042_material_status.sql` 加列 + `CHECK`，契约 `Material.status`，投影带出，实测 API 149 行全部返回 `status` | `evidence/task12-material-status.md` |
| 素材状态的**写入口**（谁暂停 / 下架） | 仍无：4 条素材路由里没有任何改状态的路径；`POST /materials/{id}/usages` 是无状态校验的 upsert，不校验 `status` | `internal/modules/production/handler.go`、`repository/store_mysql.go` |
| 素材状态的顶部 tab、统计卡、筛选项 | 仍无数据源：列表接口不返回计数聚合，服务端只读 `search`；且写路径不存在时每档计数恒为「全部 / 0 / 0」 | `handler.go:38-49`、`repository/store_mysql.go:76-111` |
| 使用情况（成片数、发布数、最近生产、最近发布） | 全库**没有**任何素材维度的用量或时间聚合；`file_transfer_tasks.asset_type` 里的 `composite_output` 只是传输任务类型枚举，没有成片实体表 | `migrations/` 建表清单、`internal/modules/production/model/model.go:71-81` |
| 重复风险 | 全库没有这个概念；`duplicate_of_account_id` 属 `media_accounts`，与本项无关 | `internal/modules/mediaaccount/model/model.go:33,75` |
| tab 计数（128 / 103 / 17 / 8）与分页总数 | 列表接口返回**裸数组**、`LIMIT 200`、无 `total`、无计数聚合 | `internal/modules/production/handler.go:38-49`、`repository/store_mysql.go:102-110` |
| 按素材状态 / 文件状态筛选 | 服务端只读 `search`，无任何筛选条件 | `handler.go:38-49`、`repository/store_mysql.go:76-111` |

盘点里**已经不需要**的一项：「该素材是否已加入我的素材」。CHG-20260930-069 任务 9 已用 `/api/v1/my-materials` 做客户端 join 得出，不新增后端字段；本记录不再重复这一项。

## 1. 独立结果

（待 §4 裁定后填写。）方向：素材库能按素材状态筛选与分组，并在行与详情里看到该素材在内容生产里的使用情况。

## 2. 范围与边界

（待裁定。）已可确定要触达的面：
- `wt-media-cloud` 数据库迁移、领域模型、Repository/Service/Handler、OpenAPI 与 Business Schema；
- `wt-media-cloud` Web 素材库与我的素材页；
- `docs/product/prd/详细文档/第五章_素材生产.md` 的素材状态与生命周期定义（该章现在只定义了 `video_status` 四态与「素材已禁止生产：不允许新加入」这句话，没有状态取值表）。

## 3. 明确不做

- 不改 `video_status` 四态取值与文案（已由 CHG-20260930-069 定稿为未准备/准备中/可下载/准备失败）；
- 不改素材状态的**读取**侧（列、契约、投影、两处页面渲染已由 CHG-20260930-069 任务 12 交付，本轮只加写路径与由它解锁的计数 / 筛选）；
- 不做内容池（CHG-20260930-070 的范围）；
- 不引入 `user_material` 之类的替代关系表（M4-A 闭环卡已禁止）。

## 4. 待裁定（激活前必须逐条关闭）

- `Q-01`：素材状态的取值集合已由 2026-09-30 走查六轮裁定为「可用 / 已暂停 / 已下架」三档并落库（CHG-20260930-069 任务 12）。**仍待裁定的是写入口**：谁来暂停与下架、在哪一页操作？（是否就是 PRD 第五章「素材已禁止生产」那句话的落地？）
- `Q-02`：**已关闭**（2026-09-30 走查六轮）——「可用」是独立取值，不是派生读法：库里存一个三值 enum（`materials.status VARCHAR(16) NOT NULL DEFAULT 'available'`），不是两个时间戳或布尔。理由与代价见 `evidence/task12-material-status.md` §6：写路径出现之前，这一列只能证明链路通了。
- `Q-03`：暂停或下架对**已存在的** `material_usage` 与已创建的 `compose_task` 生效到哪一步？PRD §5.4.3 只说「不允许新加入，并说明原因」，历史关系与结果的处置需要明确。
- `Q-04`：使用情况的四项（成片数、发布数、最近生产、最近发布）各自口径是什么、数据源是哪张表？M4-B 的 `compose_task` 与 M4-C 的成片/发布记录若尚未落地，本项依赖谁先建成？
- `Q-05`：「重复风险」的判据是什么？全库没有这个概念，需要先有定义才能谈实现；若暂不定义，设计图里这一项应从本轮移除。
- `Q-06`：列表是否改为服务端分页与筛选（响应从裸数组变为带 `total` 的信封）？这是 listing 契约的形状变化，需要按 `docs/contracts/compatibility-policy.md` 判断兼容性。

## 5. 有序任务

（待 §4 关闭后按 `planning-wt-media-delivery` 重写。）

## 6. 验证与提交边界

- 契约与迁移可分提交；素材状态与使用情况各自独立验证；
- 用户走查签收前不关闭本 CHG。
