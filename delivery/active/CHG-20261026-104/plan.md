# CHG-20261026-104 实施计划

## 1. 当前事实与约束

- 素材库列表/详情当前按“团队 + 本人负责游戏”硬授权：`canAccessMaterial` 与 `ListMaterialsFiltered` 把负责游戏当可见边界，普通运营看不到同团队其他游戏素材。
- `/material-library` 已指向正式 `material` 页面，但“使用情况”列仍读前端占位协议（`clip_count/published_count/...`），后端从未返回；页面还从 `/my-materials` 全量拉关系做加入状态，并在加入成功提示里保留“立即下载”。
- `material_usage` 是当前用户个人工作集；下载端点只校验素材可见，不校验当前用户是否有有效关系。Cloud Worker 的 `PreparationSource` 不经过用户身份，不能被个人门槛误伤。
- `composite_outputs` 只在成功提交后创建；历史 16 条成片 `operator_id` 全为 NULL，不能从 `created_by` 回填。因此团队成片数统计全部成功行，使用人数只统计已知负责人；姓名明细只给高级运营/管理员，普通运营不收姓名。
- 合同缺口：`cloud-error-codes/v1/content-production.yaml` 尚未登记 `compose_task_not_retryable`。

## 2. 明确不修改

- 不新增平行素材表、个人状态表或“已发布”事实；发布口径与 `publication` 保持 M6 前不展示。
- 不改 `material` 入库、视频准备状态机、`file_transfer_task` 字段/枚举。
- 不改创建抽屉按 `(策略, 素材)` 任何任务记录判“已使用过”的防重口径；本 CHG 的“我的使用/使用情况”只看成功成片。
- 不改 Desktop/Agent 运行时合同；两端只复用 Cloud Web 页面。

## 3. API 读模型

`GET /api/v1/materials` 与 `GET /api/v1/materials/{id}` 在素材 body 上增加可选读字段：

```text
usage_status            active | removed；无关系时不出现（加入状态：active=已加入）
added_at                当前用户关系的建立时间
my_usage                used | unused；used = 当前用户是成功成片的 operator
usage.output_count      该素材本团队全部成功成片数
usage.operator_count    已知 operator 的去重人数
usage.operators         仅高级运营/管理员返回 [{id, name, output_count}]
```

列表新增服务端筛选：`team_id`（管理员目标团队）、`game_ids`（逗号分隔，保留旧 `game_id`）、`joined=joined|not_joined`、`my_usage=used|unused`、`team_usage=used|unused`。普通运营/高级运营团队固定本团队，游戏只做筛选；管理员可选团队，未选时跨团队列出但统计按素材所属团队隔离。

`POST /materials/{id}/downloads` 在素材可见性之后新增当前用户有效 `material_usage` 校验；不满足返回既有 `material_usage_forbidden`（403）。Worker 的源准备不经此路径。

## 4. 任务

| Task | 内容 | 验证 | 提交边界 |
| --- | --- | --- | --- |
| T-01 | Cloud 团队可见性：列表/详情/加入/移出/恢复/视频地址改为团队隔离；游戏筛选多选；新增请求参数解析与校验 | Go service/repository/handler 单测：跨游戏可见、跨团队拒绝、管理员目标团队、非法参数 400 | Cloud：production 读权限与参数 |
| T-02 | Cloud 使用事实投影：当前用户加入状态、我的使用、团队成功成片数/负责人数/姓名明细；列表筛选下推 SQL | sqlmock + live DB 查询；历史 NULL 负责人不计姓名、不回填 `created_by` | Cloud：repository/service 读模型 |
| T-03 | 个人下载门槛：下载 API 校验有效 `material_usage`；确认 Worker 源准备不受影响 | service 单测（无关系/已移出/有效关系三臂）+ 既有 preparation 测试 | Cloud：service 下载守卫 |
| T-04 | 合同同步：OpenAPI 素材读模型/参数/403、错误码补 `compose_task_not_retryable`、Business Schema 可选字段、Workspace contract-map revision | OpenAPI/Schema 解析、M0 合同校验、双向 revision 对比 | Cloud 合同 + Workspace 合同映射 |
| T-05 | 共用页面：管理员团队筛选、游戏多选默认本人负责项、加入状态/我的使用/使用情况三列与服务端筛选、移除素材库下载入口、详情使用卡 | Vitest 全量；Cloud Web 与 Desktop 共用源码构建 | Cloud web |
| T-06 | 真实 API/DB 验收：三角色、跨游戏/跨团队、加入/移出/恢复、失败/成功成片、筛选与统计、直连下载拒绝、Worker 准备回归 | 真实 MySQL/API 读数 + 数据前后对照 | 无代码；evidence |
| T-07 | 真实页面读回：Cloud Web + Desktop 共用页面筛选项、三列状态、详情、从“我的素材”发起真实下载 | CDP/页面读回 + 传输任务/本地文件证据 | 无代码；evidence |
| T-08 | 负责人筛选修订：任务/成片页只列团队成员（含本人）、未选即团队全部；高级运营列表/详情改为团队范围，普通运营与管理员不变；同步 PRD/产品主文档/里程碑 | Go service 用例 + Vitest + 真实页面走查 | Cloud 前后端 + Workspace 文档 |
| T-09 | 门禁、PR、归档：Cloud PR + Workspace 记录 PR，更新 LEDGER/里程碑/MASTER | `go test`、Vitest、Workspace 全量、PR CI | Workspace 交付记录 |

## 5. 验收映射

- Done When 第 1 条：T-01 + T-06 三角色/跨团队读数。
- 第 2 条：T-02 + T-06 加入/移出/恢复、失败/取消/成功对照；T-06 同时回归 `(策略,素材)` 防重与重试入口。
- 第 3 条：T-02 + T-06 普通运营无姓名、高级运营/管理员有姓名、跨团队素材不合并。
- 第 4 条：T-03 + T-05 + T-07 页面无入口、直连下载 403、我的素材下载成功、Worker 准备回归。
- 第 5 条：T-05 + T-07 共用页面；发布相关不展示；回归 M4-A 与 M5 生产链路。
- 2026-10-27 修订：T-08 覆盖负责人筛选与高级运营团队范围；原 T-01/T-02 的团队与游戏授权口径不变。

## 6. 风险

- 历史成片无负责人：团队成片数含全部成功行，人数只含已知负责人；页面明示“历史负责人未记录”，不把 NULL 或 `created_by` 当负责人。
- 普通运营默认游戏筛选可能隐藏其他游戏素材：筛选可清空，服务端仍按团队返回；真实验收覆盖清空后读回。
- 下载新增 403 会改变既有直连行为：只影响无有效关系的请求；M4-A 从“我的素材”下载与 Worker 源准备两条路径必须同时实测。
- 管理员跨团队列表：统计与姓名按素材所属团队；真实验收覆盖同外部作品在两团队分别计数。
