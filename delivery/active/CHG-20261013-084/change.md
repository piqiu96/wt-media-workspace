# CHG-20261013-084：M4-C6 我的成片（查询、预览、来源追踪、归档与去发布入口）

- Status: IMPLEMENTING
- Level: M
- Milestone: `delivery/milestones/M4-content-production.md`
- Closure anchor: §3.1 M4-C6「我的成片」；验收矩阵 M4-AC-05/06 的查询侧
- Product: `docs/product/prd/详细文档/第五章_素材生产.md` §5.9.1–5.9.5、§5.9.12、§5.10.2/5.10.3
- Engineering: `docs/engineering/specs/2026-09-24-m4-m5-cloud-content-production.md` §3.5、§8（权限行）
- Decision: `docs/decisions/0021-compose-four-layer-model.md`
- Affected repositories: `wt-media-cloud`（含 Cloud Web/Desktop 共用页面源码）
- Current repository: `wt-media-cloud`
- Activation: CHG-20261013-083（M4-C5 成片执行）已归档；用户指示 M4 剩余 CHG 连续执行、不等待单项验收，2026-10-14 晨统一验收。按里程碑顺序进入 M4-C6。

## 1. 独立结果

运营在「我的成片」页查看自己（高级运营/管理员按范围）有权查看的 `composite_output`：列表可按状态筛选；详情可预览视频（短时预签名 GET，与素材 video-url 同边界）、可追溯来源（素材、素材使用关系、策略与快照、任务、文件信息与生成时间）；`pending_publish` 成片可归档；「去发布」入口点击只传递成片信息进入发布衔接（M4 不创建 `publication`，不把成片记为已发布）。无权限者看不到成片。

## 2. 范围

- 查询与权限：`GET /api/v1/compose-outputs`（状态筛选、范围内可见）、`GET /api/v1/compose-outputs/{id}`（详情 + 来源追踪投影）。可见范围与合成任务一致：管理员全局、高级运营 team+game 范围、普通运营仅本人创建（`created_by`）。
- 安全预览：`GET /api/v1/compose-outputs/{id}/video-url`，短时预签名 GET，边界与 `materials/{id}/video-url` 相同（只在范围与可读性校验后签发、不随列表/详情返回、调用方须重取）。
- 归档：`POST /api/v1/compose-outputs/{id}/archive`，条件翻转 `pending_publish → archived`（单条条件 UPDATE）；`published`（M6 才可达）与已归档行按合同拒绝；不删除历史成片。
- 去发布入口：详情/列表内点击后携带成片信息进入发布衔接界面；M4 不建 `publication`，不写发布事实，文案不出现「已发布」状态翻转（PRD §5.9.12「下载、预览和归档均不等于发布」）。
- 合同：openapi 新增 ComposeOutput 投影与上述端点；错误码沿用 production 冻结区间并登记；contract version bump。
- 页面（Cloud Web/Desktop 共用 Vue）：「我的成片」页——列表（状态筛选）、详情抽屉（视频预览、来源追踪、归档、去发布）；路由与导航接入两端；遵循 AdminUI 规范与既有列表页约定（页脚/分页、搜索区合并）。
- 审计：归档动作入审计。
- 真实 MySQL/API 验收与全量回归。

## 3. 明确不做

- 不实现成片下载（M4-C7 下载中心）；预览 URL 不是下载授权。
- 不实现 `publication`、发布事实、重复风险校验（M6/第六章）。
- 不实现 `published` 状态的真实流转；M4 可达状态只有 `pending_publish | archived`。
- 不提供归档恢复入口（如需，随 M6 发布管理评估）。
- 不删除成片、不建成片池或领取关系。
- 不修改 Agent / Desktop 原生代码（Desktop 复用 Cloud 页面源码）。

## 4. 有序任务与验收

| Task | 实施结果 | 验证 |
| --- | --- | --- |
| T-01 | openapi：ComposeOutput schema、list/detail/archive/video-url 端点与错误语义；contract version bump | YAML 解析测试 + 冻结名比对 |
| T-02 | Repository（范围内查询、条件归档）+ Service（权限门、详情来源追踪装配、预签名、审计） | sqlmock / 单测：权限拒绝、条件归档、published 拒绝 |
| T-03 | API handlers + wire 投影与 openapi schema 全等比对 | handler 探针测试 + wire 比对 |
| T-04 | 「我的成片」页面（列表/详情/预览/归档/去发布入口）+ 路由导航接入 | vitest（页面行为与约定用例） |
| T-05 | 真实 MySQL/API 验收：建任务→成片→读回、权限拒绝、归档翻转、预览 URL 可拉流；验收数据清零 | 真实环境探针 + 前后对照 |
| T-06 | 全量回归与证据收口 | Go 全量、web vitest 全量、governance PASS |

## 5. 验收标准

1. 范围外成片对列表、详情、预览 URL、归档均不可见/拒绝（404 同形）。
2. 详情可追溯素材、usage、策略与快照、任务、文件信息与生成时间，字段值与数据库行一致。
3. 预览地址为短时签名且可实际播放对象存储中的成片；列表/详情响应不携带任何对象地址。
4. 归档只翻转 `pending_publish → archived`；`archived` 重复归档与越权归档具名拒绝、零写入。
5. 去发布入口只传递成片信息，不创建任何发布记录、不翻转状态。

## 6. Pending Questions

None.

## 7. 范围裁定（规划期，依据 PRD 与工程规格裁定）

- **可见范围**：沿用 M4-C3 合成任务的 canRead 形状（admin 全局；senior team+game；operator 仅 `created_by` 本人）。PRD §5.10.2「查看自己的任务与成片」、§5.10.3「查看范围内任务和成片」的直接读法。
- **归档语义**：M4 单向 `pending_publish → archived`；`published` 行归档拒绝（PRD「不影响已进入发布流程的成片」）；无恢复入口，需要时随 M6 评估。
- **去发布入口**：M4 交付信息传递界面（点击后展示将被发布的成片信息并进入发布衔接），不建发布表、不写发布事实；真实发布与重复风险属 M6。
- **界面参考图** `05-my-outputs.png` 仅作视觉参考；与 PRD 文本、AdminUI 规范或既有列表页约定冲突处按文本与规范裁定并登记，不照搬图。
- **错误码**：沿用 152xx production 冻结区间，新增冻结名随本 CHG 合同 revision 登记。
