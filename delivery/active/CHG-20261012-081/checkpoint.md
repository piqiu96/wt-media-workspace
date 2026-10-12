# CHG-20261012-081 Checkpoint

## Completed

- 已确认 CHG079 结构和 CHG080 执行器验收完成，`basic_cut` v1 当前仅支持切段。
- 已修正 PRD §5.5 首版参数示例，与已验证执行代码一致。
- T-01 策略 API、请求/响应 schema、错误及枚举合同已定义并通过 YAML 解析；证据见 `evidence/T-01.md`。Cloud commit `b334437`。
- T-02 已从执行器代码发布 `basic_cut` v1 到真实 MySQL；两次发布读回同一模板 ID 3、版本 1、状态 active，schema/执行器与代码一致。证据见 `evidence/T-02.md`。Cloud commit `6ff0331`。
- T-03 已实现策略当前态模型与 MySQL 创建、按 ID 读回、团队/游戏/可用状态过滤；定向数据层测试通过。证据见 `evidence/T-03.md`。Cloud commit `e62ff58`。
- T-04 已实现按角色及团队/游戏授权、按已部署模板版本校验配置、创建/修改/复制/启停和事务内审计；定向测试通过。证据见 `evidence/T-04.md`。Cloud commit `056c0d6`。
- T-05 已注册六条策略路由并接 Service 层；错误映射为合同具名错误，成功走统一信封；旧版本端点保持 404。定向测试、合同⇄路由比对（6=6）和全仓构建通过。证据见 `evidence/T-05.md`。Cloud commit `bc9fa91`。
- T-06 已交付 Cloud Web/Desktop 共用合成策略页面（列表、创建、编辑、复制、启停；普通运营只读）与 compose API 客户端；两端路由指向同一页面，CHG079 占位守卫改写为 parity 守卫。补齐客户端缺失的 `listGames`。vitest 510 例全绿，两端构建通过。证据见 `evidence/T-06.md`。Cloud commit `58bb32a`。
- T-07 真实 MySQL/API 验收完成：模板幂等重发布（id=3 不变）；admin 创建/修改/复制/停用读回一致且绑定版本不漂移；schema 外参数、非法区间、非法状态均 400 且零写入；临时账号实测普通运营只读+越权 403/404、高级运营范围内可写+越团队 403；页面路由 200。验收数据与临时账号/团队已精确清零，模板未动。证据见 `evidence/T-07.md`。基于 Cloud `58bb32a`，无代码改动。
- T-08 全量回归通过：Go 71 包 0 FAIL、vitest 510 例全绿、两端 Web 构建通过、diff check 与 delivery 治理 PASS。验收矩阵 §5 五项全部 PASS。证据见 `evidence/T-08.md`。
- T-09 走查修订已实施（范围见 `change.md` §7）：移除 `content_type`（合同/迁移 052/模型/服务/页面全链，旧字段请求被 400 拒绝）；表单分「基础信息」+「模板参数」两节，参数区由所选模板 schema 动态渲染（schema 增补 `title`，模板行已重发布 id=6）；启停外置为列表行内开关。T-08 同口径回归全绿，PRD §5.5.4 已回写。证据见 `evidence/T-09.md`。Cloud commit `916e070`。
- T-10 个人信息卡新增「所属分组」「游戏范围」（`change.md` §7 第 4 条）：运营可从自己页面看出策略归属分组；管理员显示不受限，游戏 ID 映射为名称。两端共用页自动同源，vitest 510 例与两端构建全绿。证据见 `evidence/T-10.md`。Cloud commit `da42edf`。
- T-11 策略编辑弹窗与详情抽屉补「所属团队」「所属游戏」（`change.md` §7 第 5 条）：编辑态只读展示（服务端不改归属），团队名全角色经团队列表映射。vitest 510 例与两端构建全绿。证据见 `evidence/T-11.md`。Cloud commit `374e03f`。
- T-12 AdminUI 视觉规范贯彻（`change.md` §7 第 6 条）：规范文档与设计图入库 `docs/standards/`，约束 M4-M5 后续任务；合成策略页完成一轮优化——筛选区改共享 `filter-bar`/`wt-filter-field`/`wt-filter-actions` 约定、编辑容器 Dialog→Drawer 分组（基础信息/模板参数）、未保存关闭二次提示、校验错误就近提示、详情抽屉分区只读。vitest 510 例与两端构建全绿。证据见 `evidence/T-12.md`。Cloud commit `0cb2dd9`，Workspace 规范入库 commit `500584f`。
- T-13 视觉优化第二轮（`change.md` §7 第 7 条，用户截图裁定）：筛选区与表格合并同卡（同内容池）、补分页与「合成模板」筛选、编辑弹窗改回与挖掘策略同构的 880px Dialog（分组卡片+配置说明面板）、移除统计区域；另修弹窗底部「取消/保存」高度不一（裸 outline 按钮缺 `wt-secondary-button` 约定类，36px vs 32px），合成策略与挖掘策略弹窗同修。vitest 510 例与两端构建全绿。证据见 `evidence/T-13.md`。Cloud commits `ff6c60a`、`41390a1`。

## Current

待用户对修订后页面的复查（GUI 级统一走查）；通过后 CHG 转 DONE 并归档。

## Next

统一走查 → 处理走查发现（如有）→ 归档 CHG-20261012-081（移出 `delivery/active` 与 LEDGER）。

## Blockers

None.

## Recent verification

- CHG080 真实 FFmpeg/Garage 验收已归档；Cloud 工作树开始本 CHG 前干净。
- 四份 Cloud 合同 YAML 使用 `gopkg.in/yaml.v3` 解析通过。
- `go test ./cmd/compose-template-publish ./internal/modules/production/executor ./internal/modules/production/repository -count=1` 通过；真实 MySQL 两次发布同一模板 ID。
- `go test ./internal/modules/production/model ./internal/modules/production/repository -count=1` 与 `git diff --check` 通过。
- `go test ./internal/modules/production/repository ./internal/modules/production/service -count=1` 通过。
- `go test ./internal/modules/production/... -count=1` 与 `go build ./...` 通过；合同 YAML 与注册路由 6 条精确相等。
- T-07：真实 MySQL/API 全对照（读回一致、故障零写入）后残留清零。
- T-08：`go test ./... -count=1`（71 包 0 FAIL）、`go build ./...`、vitest 510 例、`build:cloud`/`build:desktop`、diff check、delivery 治理全部通过。
- T-09：修订后同口径重测全绿；迁移 052 实跑（1 applied, 54 total）；模板行重发布 id=6 basic_cut v1（schema 带 title）；真实 API 复验「无 content_type 创建 201、旧字段 400、schema 标题下发」，验收数据清零。
- T-12：vitest 56 文件 510 用例全绿、`build:cloud`/`build:desktop` PASS；筛选区标签与 ContentPoolPage 逐一同构。
- T-13：vitest 56 文件 510 用例全绿、`build:cloud`/`build:desktop` PASS；列表卡与编辑弹窗分别比对 ContentPoolPage / DiscoveryStrategiesPage 同构。
