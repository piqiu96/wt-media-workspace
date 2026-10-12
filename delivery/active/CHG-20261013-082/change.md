# CHG-20261013-082：M4-C3 合成任务创建与排队

- Status: IMPLEMENTING
- Level: M
- Milestone: `delivery/milestones/M4-content-production.md`（闭环卡 M4-B；§3.1 M4-C3 行）
- Closure anchor: §3.1 M4-C3「任务创建」；验收矩阵 M4-AC-04 的创建侧
- Product: `docs/product/prd/详细文档/第五章_素材生产.md` §5.4.4、§5.5.5、§5.5.6、§5.6
- Engineering: `docs/engineering/specs/2026-09-24-m4-m5-cloud-content-production.md` §3.4、§5.4
- Decision: `docs/decisions/0021-compose-four-layer-model.md`
- Affected repositories: `wt-media-cloud`
- Current repository: `wt-media-cloud`
- Activation: CHG-20261012-081（M4-C2 策略交付）已归档，用户走查通过；按里程碑顺序进入 M4-C3。

## 1. 独立结果

运营在「我的素材」选择一条或多条素材、选择可用合成策略并按模板 schema 覆盖参数后，Cloud 逐素材原子创建排队任务，保存创建当时的 `strategy_id`、`template_code`、`template_version` 与最终生效的不可变 `config_snapshot`；可在「合成任务」页查看列表/详情并取消尚未开始（pending）的任务。重复提交同一次创建请求不产生重复任务；此后修改策略或新增模板版本均不改变已建任务的快照。

## 2. 范围

- 迁移新建 `compose_task`（工程规格 §3.4 字段集：范围、触发方式 manual、来源 material/usage、策略与快照、状态、幂等键、领取者/租约/heartbeat、尝试次数、阶段/进度/错误、输出键与成片引用）。本 CHG 只落结构与 pending/cancelled 两个状态的实际流转；running/success/failed 由 M4-C5 接管。
- 创建 API（批量命令、逐素材独立任务、部分失败不回滚）：
  - 幂等：请求携带客户端生成的 `request_key`，库上唯一；同键重复提交返回既有任务，不新建。
  - 覆盖参数：请求携带可选 `config_override`，与策略 config 合并后按所绑定模板版本的 schema 校验（同一套执行器 schema 校验器）；最终合并结果整体写入 `config_snapshot`，快照同时含 `strategy_id`、`template_code`、`template_version`。
  - 校验链：素材存在且有本人有效 `material_usage`（移出后不允许新建）、策略 active 且绑定模板版本可用、合并 config 过 schema；任一失败具名拒绝、零写入。
  - 权限：运营只为自己范围内素材创建；管理员全局；审计记录创建与取消。
- 列表/详情/取消 API：按状态、策略、时间筛选；详情含阶段（pending 阶段为「等待源素材」）；取消仅 `pending → cancelled`（running 取消、失败重试属于 M4-C5，接口预留不实现）。
- Cloud Web/Desktop 共用页面：「我的素材」多选创建入口（选策略 + 按模板 schema 渲染可覆盖参数）；「合成任务」页（列表、筛选、详情、排队中取消）。两端路由同源；页面遵循 `docs/standards/前端视觉-AdminUI规范.md`。
- 真实 MySQL/API 验收与全量回归。

## 3. 明确不做

- 不实现任务领取、FFmpeg 执行、`composite_output`（M4-C5）。
- 不实现 running 取消、失败重试、超时与 Worker 恢复（M4-C5）。
- 不实现 Scheduler/定时触发、批量资源上限（M5）。
- 不实现「复制配置重新创建」（§5.6.2 方式 2，随 M4-C6 成片页一并评估）。
- 不修改 Agent 或 Desktop 原生代码；Desktop 复用 Cloud 的 Vue 页面。

## 4. 有序任务与验收

| Task | 实施结果 | 验证 |
| --- | --- | --- |
| T-01 | `compose_task` 迁移与 Cloud API 合同（创建/列表/详情/取消、状态枚举、幂等语义、具名错误） | 合同 YAML 解析通过；迁移与合同字段一致，不含执行期专属字段误用 |
| T-02 | 模型与 MySQL Repository：幂等创建、快照写入、范围过滤列表、pending 取消 | sqlmock 定向测试通过（唯一键冲突读回既有任务、取消仅命中 pending） |
| T-03 | Service：校验链、config 合并校验、快照原子保存、幂等返回、取消与审计 | 定向测试通过：移出关系/停用策略/越权/schema 外覆盖均具名失败零写入；同 request_key 幂等；改策略后旧快照不变 |
| T-04 | Handler、路由注册与合同映射 | 路由⇄合同比对一致；统一信封与具名错误映射 |
| T-05 | 共用页面：「我的素材」创建入口 + 「合成任务」页（列表/筛选/详情/取消） | vitest 红先绿后；两端构建通过、路由 parity 守卫保持 |
| T-06 | 真实 MySQL/API 验收：幂等对照、快照不变对照、故障矩阵、验收数据清零 | 读回一致、重复提交单任务、越权零写入；临时数据清零 |
| T-07 | 全量回归与证据收口 | Go 全量、vitest 全量、两端构建、diff check、治理 PASS |

每项按失败验证 → 最小实现 → 测试 → 证据 → checkpoint → 独立提交推进。

## 5. 验收标准

1. 批量创建为逐素材独立任务，部分失败不回滚；页面即时反映任务数。
2. 同一 `request_key` 重复提交不产生重复任务，返回同一任务。
3. `config_snapshot` 不可变：创建后修改策略、停用模板版本均不改变既有任务快照；同一素材新请求可用不同策略。
4. 移出的 `material_usage`、停用策略、越权素材、schema 外覆盖参数均具名失败且零写入；取消仅对 pending 生效。
5. Cloud Web 与 Desktop 页面真实可用；真实 MySQL/API 验收与回归通过。

## 6. Pending Questions

None.

## 7. 范围裁定（规划期，依据里程碑与 PRD 直接裁定）

- **覆盖参数集合**：模板 schema 定义的全部参数均可通过 `config_override` 覆盖（当前 `basic_cut` v1 即 `start_seconds`/`end_seconds`）；不另建「可覆盖白名单」表。后续模板如需禁止覆盖，经模板新版本语义处理。
- **幂等键粒度**：批量创建请求体逐素材携带 `request_key`（客户端 UUID）；库上 `uq_compose_tasks_request_key` 全局唯一，冲突时读回既有任务判定归属后返回。
- **任务来源字段**：`material_id` 必填、`material_usage_id` 必填（人工创建必有有效使用关系；Scheduler 场景 M5 再放宽 usage 为可空，与工程规格「可选」一致）。
