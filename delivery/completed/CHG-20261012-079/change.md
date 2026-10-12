# CHG-20261012-079：M4-B 模板与策略结构

- Status: DONE
- Level: M
- Milestone: `delivery/milestones/M4-content-production.md`
- Closure anchor: §3.1 M4-C2 基础；§5 闭环卡 M4-B
- Product: `docs/product/prd/详细文档/第五章_素材生产.md` §5.5
- Engineering: `docs/engineering/specs/2026-09-24-m4-m5-cloud-content-production.md` §3.3、§7
- Decision: `docs/decisions/0017-m4-m5-cloud-owned-content-production.md`、`docs/decisions/0021-compose-four-layer-model.md`
- Affected repositories: `wt-media-cloud`
- Current repository: `wt-media-cloud`
- Activation: CHG070 已按用户走查结论关闭；M4-A 用户于 2026-10-12 确认走查通过。
- Rework: 2026-10-12 用户裁定四层模型（Q-01 已按 ADR-0021 关闭），并确认执行代码先部署、模板记录与 schema 后发布（Q-02）。T-01～T-04 按旧模型交付且**尚未签收**；旧验收数据已清理。本 CHG 仅完成结构和合同调整，首版模板发布与策略创建移到 M4-C4 执行器验证之后。

## 1. 独立结果

Cloud 数据库具备四层模型前两层的正确结构，合同不再宣称旧策略版本能力。执行器未就绪期间，模板目录为空，Cloud Web 与 Desktop 不提供无法完成的策略创建操作。

## 2. 范围

- 建立 `compose_templates` 表：`code`、`name`、整数 `version`、`schema_json`、`executor`、`status`，`UNIQUE(code, version)`；本 CHG 不插入 `basic_cut` 记录。
- 将 `compose_strategies` 调整为无策略版本的结构：模板引用（模板 id + 版本）、当前配置、业务范围与状态；移除旧版本表和列。
- 修订 Cloud 合同与业务 Schema，移除旧模型的 `expected_version`、版本端点和 15204 冲突语义；模板目录只返回已发布记录，此阶段为空。
- 撤下旧模型的策略写入端点和两端页面操作，避免在执行器缺失时呈现可创建的假入口。

## 3. 明确不做

- 不发布模板记录或 schema，不启用 `basic_cut`，不创建或验收业务策略；这些能力待 M4-C4 执行器就绪后交付。
- 不创建 `compose_task`、`composite_output`、自动调度规则或定时触发；`schedule` 到 M5 再引入。
- 不运行 FFmpeg，不触碰 Agent/Desktop 原生代码；本 CHG 只预留 `executor` 结构。
- 不提供片头/片尾/BGM 等资产参数键；不做动态工作流、上传脚本、任意执行参数或泛化 `template` 表。

## 4. 有序任务与验收

| Task | 实施结果 | 验证 |
| --- | --- | --- |
| T-01 | （旧模型）确定首个受控模板版本、参数与可覆盖字段；新增策略和版本 Migration | 已交付；被 T-05 部分取代 |
| T-02 | （旧模型）发布 Cloud 策略合同并实现 Repository、Service、Handler 与路由 | 已交付；版本语义被 T-06/T-07 取代 |
| T-03 | （旧模型）两端共用策略页面及客户端 | 已交付；版本 UI 被 T-07 取代 |
| T-04 | （旧模型）真实 MySQL/API 验收（自动化部分） | 已交付并全 PASS；走查中止，按新模型重验 |
| T-05 | 核对并清理旧验收数据；完成 `compose_templates` 建表和 `compose_strategies` 无版本迁移，不插入模板记录 | 新库升级与已升级开发库一致；模板目录为空；唯一约束生效 |
| T-06 | 修订 Cloud 合同/Schema；移除旧模型策略版本语义和过早开放的写入路由 | 合同不宣称未实现的策略创建；旧版本端点不存在；模板查询读回空目录 |
| T-07 | 撤下旧策略页面操作与旧 API Client，Cloud Web/Desktop 统一显示尚未开放的页面状态 | 两端没有策略创建入口；两端构建通过 |
| T-08 | 真实 MySQL、API、页面及回归验证，记录证据 | 无旧验收数据、无模板记录、无旧策略写入；合同与数据库结构一致 |

每个 Task 按“先验证失败→最小实现→测试→证据→checkpoint→独立提交”推进。数据与合同、业务规则、页面、验收记录分别提交。

## 5. 验收标准

1. 模板与策略结构符合 ADR-0021：模板 `(code, version)` 唯一；策略没有版本列和版本表。
2. Cloud 合同和当前路由不再提供旧策略版本语义；模板目录从数据库读取，尚无模板记录时返回空列表。
3. Cloud Web 与 Desktop 不提供不能完成的策略创建操作；没有合成任务或自动触发的假成功。
4. 本机旧验收数据清理完成。M4-C4 验证执行代码后，另行发布模板和 schema、验收策略创建；M4-C3 再验任务快照。

## 6. Pending Questions

None. Q-02 已由用户裁定：本 CHG 先建表和改合同，模板发布与策略创建留到 M4-C4/C5 执行器就绪后验收。050 草稿迁移已修正并提交，旧验收数据清理见 `evidence/T-05-data-cleanup.md`。

## 7. 关闭记录（2026-10-12）

- T-05～T-08 全部完成并留证据；补做 051 结构对齐（`parameters_json → config_json`、删 `allowed_overrides_json`，Cloud 提交 `3535f86`），开发库结构与 ADR-0021 完全一致：模板 0 行、策略 0 行、无版本列/表、`config_json` 单一来源。
- 最终回归（051 之后重跑）：`go test ./... -count=1` 67 包 ok / 0 FAIL；web 全量 507 测试 PASS；`build:cloud`、`build:desktop` PASS。
- 验收标准 1–4 逐项对应 `evidence/T-08.md` 与 `evidence/T-05-data-cleanup.md` 读数，全部 PASS。
- Cloud 仓提交：`aeb173b`（050 建表）、`79b3a3e`（合同与目录）、`2b71fd6`（页面撤下）、`3535f86`（051 对齐）；工作树干净。
- 后继：M4-C4 验证执行代码后发布 `basic_cut` v1 与 schema 并交付「M4-C2 策略交付」，M4-C3 再验任务快照。
