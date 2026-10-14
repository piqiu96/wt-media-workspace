# CHG-20261014-091：M5-C1 合成策略计划配置与读回

- Status: DONE
- Level: M
- Milestone: `delivery/milestones/M5-automatic-production.md`
- Closure anchor: §4 M5-A（计划配置与页面读回这一段）
- Product: `docs/product/prd/详细文档/第五章_素材生产.md` §5.5.7～5.5.8
- Engineering: `docs/engineering/specs/2026-09-24-m4-m5-cloud-content-production.md` §3.3、§4
- Decision: `docs/decisions/0017-m4-m5-cloud-owned-content-production.md`
- Current repository: `wt-media-cloud`
- Affected repositories: `wt-media-cloud`（MySQL、Cloud API、Cloud Web/Desktop 共用 Vue）

## 目标

高级运营可以给已有合成策略设置手动、每 N 分钟或每天 HH:MM 的计划，明确时区、单次和每日上限，独立启停自动执行，并从服务端读回下次执行时间。启用或修改计划不立即创建任务。

## 当前事实与边界

- 策略只保存模板配置和可用状态，尚无 `schedule`、下次执行时间或自动执行入口。
- 素材范围首版固定为策略创建人的“我的素材”中仍有效、属于策略团队和游戏的素材；已由该策略成功生产的素材将被 C2 跳过。C1 页面只展示这条规则，不做素材实际筛选。
- Cloud 是计划唯一事实源。Scheduler 到点扫描、候选素材筛选、任务创建和“立即执行”属于 M5-C2；Worker Pool 属于后续 CHG。
- M4-H2 人工页面走查暂缓，最终与 M5 统一由用户走查；本 CHG 的机器验收只覆盖 C1 自身。

## 有序任务

| Task | 结果 | 验证 |
| --- | --- | --- |
| T-01 | 计划结构、下次时间计算、严格校验与独立启停规则 | Service 定向测试，跨日和时区测试 |
| T-02 | MySQL 列/索引、审计、API 和合同读写 | 数据库迁移/读回、Repository/Handler 测试、合同解析 |
| T-03 | 合成策略页面显示与编辑计划、就近校验、区分策略状态和自动执行状态 | Web 定向测试、Cloud/Desktop 双构建 |
| T-04 | 实际读回与回归，记录证据，独立提交 | API/数据库/UI 对照；Go/Web 定向回归、diff 范围检查 |

## 验收

1. 有权限的高级运营/管理员能保存计划，普通运营不能更改；非法时区、周期和数量上限被拒绝，错误可定位。
2. 手动计划不产生下次执行时间；启用间隔或每日计划时，下次执行时间严格晚于保存时刻，按选定时区计算；启用和编辑不创建任务。
3. 策略可用状态与自动执行状态独立显示；策略停用时不产生可执行下次时间，重新启用后重新计算。复制策略不意外开启自动执行。
4. 数据库、API 和页面读回一致；范围文案明确“创建人的我的素材”，不展示尚不存在的运行统计或“运行中”状态。

## 不做

- 不运行定时扫描、不创建 `scheduled compose_task`、不开放“立即执行”。
- 不增加自定义素材筛选表达式、独立生产规则表、MQ 或新执行器。
- 不把本 CHG 的机器验证写成 M4/M5 最终用户走查通过。

## Pending Questions

None. 用户确认首版素材范围为创建人的“我的素材”，跳过该策略已生产过的素材。

## 验收结论

T-01～T-04 机器验收均 PASS，证据在 `evidence/`。真实 MySQL 迁移已应用到本地稳定库；旧策略可读，计划事务内写入、读回与回滚通过。Cloud commit `6124dab`。M4/M5 最终人工 UI 走查仍由用户统一签收。
