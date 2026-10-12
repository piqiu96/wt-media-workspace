# CHG-20261012-081：M4-C2 合成策略交付

- Status: IMPLEMENTING
- Level: M
- Milestone: `delivery/milestones/M4-content-production.md`
- Closure anchor: §3.1 M4-C2 策略交付；§5 闭环卡 M4-B
- Product: `docs/product/prd/详细文档/第五章_素材生产.md` §5.5、§5.10
- Engineering: `docs/engineering/specs/2026-09-24-m4-m5-cloud-content-production.md` §3.3、§7
- Decision: `docs/decisions/0021-compose-four-layer-model.md`
- Affected repositories: `wt-media-cloud`
- Current repository: `wt-media-cloud`
- Activation: CHG079 建立结构并撤下旧策略入口；CHG080 已用真实 FFmpeg 与 Garage 验证 `basic_cut` v1。用户要求继续 M4 剩余任务，并在本 CHG 全部完成后统一走查。

## 1. 独立结果

技术侧发布与已部署执行代码一致的 `basic_cut` v1 模板和 schema。高级运营能在负责范围内创建、修改、复制和停用合成策略；普通运营能查看可用策略。保存后数据库、API 和 Cloud Web/Desktop 共用页面读回一致。

## 2. 范围

- 模板发布从 `executor.BasicCutV1()` 取得代码和 schema，重复发布不覆盖已发布版本；模板目录只返回入库且启用的版本。
- 策略绑定固定模板 id 和版本，`config_json` 只允许 `start_seconds`、`end_seconds`，并按所绑定版本校验。模板停用后不能建立新的绑定。
- 高级运营在所属团队和游戏范围内创建、修改、复制和停用策略；普通运营只读所在范围的可用策略。管理员按现有全局管理权限操作。
- Cloud 提供策略 API、错误合同和审计；共用 Vue 页面完成列表、编辑、复制、状态操作。
- 使用真实 MySQL 验证模板发布与策略写入/读回；Cloud Web 和 Desktop 构建与回归。

## 3. 明确不做

- 不创建 `compose_task`、`composite_output`，不从页面触发 FFmpeg；属于 M4-C3/C5。
- 不增加 `schedule`、定时触发、批量资源上限；属于 M5。
- 不实现画幅、片头、片尾、BGM、脚本、动态节点或模板编辑页面。
- 不新增策略版本表；历史任务快照由 M4-C3 实施。
- 不修改 Agent 或 Desktop 原生代码；Desktop 复用 Cloud 的 Vue 页面。

## 4. 有序任务与验收

| Task | 实施结果 | 验证 |
| --- | --- | --- |
| T-01 | 对齐 `basic_cut` v1 产品示例，定义策略 API 与错误合同 | 合同只声明当前可执行参数与操作；schema 外参数无入口 |
| T-02 | 技术侧受控发布模板，schema 取自执行器代码 | 重复发布幂等且不覆盖既有版本；真实 MySQL 读回与代码 schema 一致 |
| T-03 | 策略 Repository 与数据模型 | 团队/游戏范围、模板版本和当前配置保存及读回一致；无策略版本表 |
| T-04 | 策略 Service：参数校验、权限、创建/修改/复制/停用与审计 | 越权、停用模板和 schema 外参数具名失败；普通运营只读 |
| T-05 | Handler、路由及 Cloud 合同 | API 成功与失败均符合统一响应；旧版本端点不恢复 |
| T-06 | Cloud Web/Desktop 共用策略页面与客户端 | 高级运营操作可用，普通运营只读；两端路由同源 |
| T-07 | 真实 MySQL、API、页面读回和故障对照 | 发布模板及创建策略后读回一致；越权/非法参数不写入 |
| T-08 | 全量回归、证据和交付收口 | Go、Web 测试及 Cloud/Desktop 构建通过；本 CHG 完成后统一走查 |

每项按失败验证 → 最小实现 → 测试 → 证据 → checkpoint → 独立提交推进。

## 5. 验收标准

1. `basic_cut` v1 数据库模板与代码 schema/执行器一致，重复发布不修改旧版本。
2. 高级运营策略创建、修改、复制、启停和读回真实可用；普通运营只读；团队/游戏越权不可写入或读取。
3. 模板停用阻止新绑定，既有策略不因模板升级自动变更版本。
4. schema 外参数、非法时间范围和旧策略版本语义均被拒绝；无任务/成片假成功。
5. Cloud Web 与 Desktop 共用页面可用；真实 MySQL/API 验收和回归通过。

## 6. Pending Questions

None.
