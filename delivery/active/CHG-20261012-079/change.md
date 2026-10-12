# CHG-20261012-079：M4-B 合成策略与版本

- Status: IMPLEMENTING
- Level: M
- Milestone: `delivery/milestones/M4-content-production.md`
- Closure anchor: §3.1 M4-C2；§5 闭环卡 M4-B
- Product: `docs/product/prd/详细文档/第五章_素材生产.md` §5.5
- Engineering: `docs/engineering/specs/2026-09-24-m4-m5-cloud-content-production.md` §3.3、§7
- Decision: `docs/decisions/0017-m4-m5-cloud-owned-content-production.md`
- Affected repositories: `wt-media-cloud`
- Current repository: `wt-media-cloud`
- Activation: CHG070 已按用户走查结论关闭；M4-A 用户于 2026-10-12 确认走查通过。

## 1. 独立结果

高级运营在“内容生产 → 合成策略”保存、修改、复制本业务范围内的策略，能读回当前配置和历史版本；普通运营只能查看有权使用的策略及允许覆盖的参数。Cloud 对无权限和非法参数的请求具名拒绝。Cloud Web 与 Desktop 共用同一页面。

## 2. 范围

- Cloud 维护受控模板目录和版本、`compose_strategy` 当前记录及不可变版本记录；策略修改不覆盖历史版本。
- Cloud 提供策略创建、列表、详情、修改、复制、版本查询与模板目录 API；合同、Schema、枚举和错误码由 Cloud 维护。
- 服务端按角色、团队和游戏范围校验；普通运营只读有权使用的启用策略。
- 共享 Vue 页面提供策略列表、创建、编辑、复制与版本查看；按现有反馈规范显示校验与操作结果。

## 3. 明确不做

- 不创建 `compose_task`、`composite_output`、自动调度规则或定时触发；不运行 FFmpeg，也不触碰 Agent/Desktop 原生代码。
- 不在“我的素材”放置尚不能提交的策略选择流程。人工选择和不可变任务快照属于 M4-C3。
- 不提供用户上传模板脚本、动态插件或任意执行参数。

## 4. 有序任务与验收

| Task | 实施结果 | 验证 |
| --- | --- | --- |
| T-01 | 确定首个受控模板版本、参数与可覆盖字段；新增策略和版本 Migration | 迁移可重复执行；非法模板或参数被拒绝；旧版本不被覆盖 |
| T-02 | 发布 Cloud 策略合同并实现 Repository、Service、Handler 与路由 | 创建→读回一致；修改递增版本；复制产生独立策略；越权读写拒绝 |
| T-03 | 两端共用策略页面及客户端 | 高级运营可维护；普通运营只读；错误参数靠近字段反馈；Cloud/Desktop 构建通过 |
| T-04 | 真实 MySQL/API 与页面走查、回归测试和证据 | 查库与 API 读回一致；角色/业务范围矩阵通过；用户验收后关闭 |

每个 Task 按“先验证失败→最小实现→测试→证据→checkpoint→独立提交”推进。数据与合同、业务规则、页面、验收记录分别提交。

## 5. 验收标准

1. 策略保存后再次查询与页面展示一致；修改后旧版本仍可读，复制不会修改原策略。
2. 普通运营和范围外用户不能修改策略；范围外策略不能被读出，非法模板和参数被具名拒绝。
3. Cloud Web 与 Desktop 共用页面，列表、详情、创建、编辑、复制和版本查看均可用。
4. 本项没有合成任务或自动触发的假成功。后续 M4-C3 才验证任务快照，M4-C4/C5 才验证模板真实执行。

## 6. Pending Questions

- Q-01（blocking，2026-10-12）：用户提出「compose_template → compose_strategy → compose_task → composite_output」四层模型修正。逐项冲突：
  1. 「compose_strategy 不需要独立版本」与里程碑 M4-C2「查看版本记录」及本 CHG §2 / 验收 1 直接冲突——已交付并验证的 `compose_strategy_versions`、`expected_version`、版本历史页面将拆除；
  2. 模板入库存表（整数自增版本、`schema_json`、`executor`）与 T-01 代码内目录设计不同，且 `executor` 在 M4-C4/C5 前无可绑定执行代码；
  3. 策略 `schedule` 字段与本 CHG §3「不做自动调度」冲突；
  4. `config` 资产键（intro/outro/bgm）与 T-01「无资源合同不启用」裁定冲突，资源接入属 M4-C4/C5；
  5. `compose_task` 快照与执行语义属 M4-C3/C4/C5，不在本 CHG 范围。
  待用户裁定处置路径（改范围重开本 CHG 或另开新 CHG）与逐项取舍后方可继续实施；版本记录若移除需同步回写里程碑 M4-C2 文本。
