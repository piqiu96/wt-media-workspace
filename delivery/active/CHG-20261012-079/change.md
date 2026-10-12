# CHG-20261012-079：M4-B 合成策略与版本

- Status: IMPLEMENTING
- Level: M
- Milestone: `delivery/milestones/M4-content-production.md`
- Closure anchor: §3.1 M4-C2；§5 闭环卡 M4-B
- Product: `docs/product/prd/详细文档/第五章_素材生产.md` §5.5
- Engineering: `docs/engineering/specs/2026-09-24-m4-m5-cloud-content-production.md` §3.3、§7
- Decision: `docs/decisions/0017-m4-m5-cloud-owned-content-production.md`、`docs/decisions/0021-compose-four-layer-model.md`
- Affected repositories: `wt-media-cloud`
- Current repository: `wt-media-cloud`
- Activation: CHG070 已按用户走查结论关闭；M4-A 用户于 2026-10-12 确认走查通过。
- Rework: 2026-10-12 用户裁定四层模型（Q-01 已按 ADR-0021 关闭：重开本 CHG 改范围；移除策略版本记录，里程碑 M4-C2 已回写；`schedule` 推迟到 M5；资产参数键随模板新版本放开）；T-01～T-04 按旧模型交付且**尚未签收**，其策略版本机制随 T-05～T-08 重做移除，本 CHG 范围随之更新。

## 1. 独立结果

高级运营在“内容生产 → 合成策略”保存、修改、复制本业务范围内的策略，每条策略正确绑定一个 `(compose_template, version)`；再次查询读回当前配置。普通运营只能查看有权使用的策略及允许覆盖的参数。Cloud 对无权限、越权和 schema 外参数的请求具名拒绝。Cloud Web 与 Desktop 共用同一页面。

## 2. 范围

- Cloud 维护入库的受控模板目录 `compose_template`：`code`、`name`、整数自增 `version`（`UNIQUE(code, version)`，旧版本不覆盖）、`schema_json`、`executor`、`status`；首个模板 `basic_cut` v1，schema 只含当前可执行参数（画面比例等）。
- `compose_strategy` 为无版本业务配置：模板引用（模板 id + 模板版本）、`config`（由所绑定模板版本 `schema_json` 校验）、业务范围与启停状态；修改直接覆盖，变更走审计日志。
- Cloud 提供模板目录、策略创建、列表、详情、修改与复制 API；合同、Schema、枚举和错误码由 Cloud 维护，随重做同步修订（移除版本与 15204 冲突语义）。
- 服务端按角色、团队和游戏范围校验；普通运营只读有权使用的启用策略。
- 共享 Vue 页面提供策略列表、创建、编辑、复制与模板选择；按现有反馈规范显示校验与操作结果。

## 3. 明确不做

- 不保存策略版本记录、`expected_version` 防覆盖与版本历史页面（Q-01 裁定移除；历史追溯由 M4-C3 任务快照承担）。
- 不创建 `compose_task`、`composite_output`、自动调度规则或定时触发；`schedule` 字段推迟到 M5 定时生产落地时引入，本 CHG 不建空转列。
- 不运行 FFmpeg，不触碰 Agent/Desktop 原生代码；`executor` 字段随表结构一次到位，但其绑定执行代码属 M4-C4/C5。
- 不提供片头/片尾/BGM 等资产参数键（当前无资源合同，随模板新版本放开）；不做动态工作流、用户上传模板脚本、任意执行参数或泛化 `template` 表。
- 不在“我的素材”放置尚不能提交的策略选择流程。人工选择和不可变任务快照属于 M4-C3。

## 4. 有序任务与验收

| Task | 实施结果 | 验证 |
| --- | --- | --- |
| T-01 | （旧模型）确定首个受控模板版本、参数与可覆盖字段；新增策略和版本 Migration | 已交付；被 T-05 部分取代 |
| T-02 | （旧模型）发布 Cloud 策略合同并实现 Repository、Service、Handler 与路由 | 已交付；版本语义被 T-06/T-07 取代 |
| T-03 | （旧模型）两端共用策略页面及客户端 | 已交付；版本 UI 被 T-08 取代 |
| T-04 | （旧模型）真实 MySQL/API 验收（自动化部分） | 已交付并全 PASS；走查中止，按新模型重验 |
| T-05 | 新增 `compose_template` Migration 与种子（basic_cut v1，schema_json、executor、UNIQUE(code,version)）；调整 `compose_strategies` 列（模板 id 引用），移除 `compose_strategy_versions` 表与 `current_version` | 迁移可重复执行；UNIQUE 约束生效；旧版本不被覆盖 |
| T-06 | 修订 Cloud 合同（模板目录、策略 CRUD、错误码；移除 versions 端点与 15204）并按新模型实现 Repository、Service、Handler | 创建→读回一致且模板绑定正确；复制产生独立策略；schema 外参数具名拒绝；越权拒绝 |
| T-07 | 调整共用页面与 API Client：移除版本历史与 expected_version，模板选择改为目录实体 | 高级运营可维护；普通运营只读；错误参数靠近字段反馈；两端构建通过 |
| T-08 | 真实 MySQL/API 与页面走查、回归测试和证据（重做 T-04 矩阵） | 查库与 API 读回一致；角色/业务范围矩阵通过；用户验收后关闭 |

每个 Task 按“先验证失败→最小实现→测试→证据→checkpoint→独立提交”推进。数据与合同、业务规则、页面、验收记录分别提交。

## 5. 验收标准

1. 策略保存后再次查询与页面展示一致，且正确绑定 `(模板, 模板版本)`；复制产生独立策略，不修改原策略。
2. 修改策略直接生效；历史任务保证由 M4-C3 任务快照承担，本项不存在策略版本记录。
3. 普通运营和范围外用户不能修改策略；范围外策略不能被读出，schema 外参数和非法请求被具名拒绝。
4. 模板目录为入库实体：`(code, version)` 唯一，旧版本保留可查。
5. Cloud Web 与 Desktop 共用页面，列表、详情、创建、编辑、复制均可用。
6. 本项没有合成任务或自动触发的假成功。后续 M4-C3 才验证任务快照，M4-C4/C5 才验证模板真实执行。

## 6. Pending Questions

None.
