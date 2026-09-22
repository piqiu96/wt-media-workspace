# CHG-20260915-044：M3-A 内容池基础能力

- Status: HANDOFF
- Level: M
- Milestone: `delivery/milestones/M3-content-discovery-v2.md#m3-a-内容池基础能力`
- 日期：2026-09-15
- 基线：`docs/product/M3-content-mining-v2.md`；ADR-0013；团队隔离决策见 ADR-0014。
- 当前仓库：wt-media-cloud、wt-media-workspace；开始 M3-A 实施。

## 独立目标与前置

独立用户目标和成功事实以对应闭环卡为准，不扩展至其他阶段。

前置：用户已确认仅按业务团队隔离：同团队运营可见全部团队素材，管理员可见全部团队；不使用游戏维度。

范围：来源列表/详情、pending/material_created/ignored、批量处理、统一入池与转素材服务、最小只读素材库。

## 明确不做

外部接口接入（M3-B）、手工新增作品产品入口、自动转素材、完整素材管理、文件操作；本阶段只提供后续入口复用的受控 source ingest 服务。

## 顺序任务

### Task 1：定义模型与权限

- 工作：落实团队级范围：source_content.team_id 必填；普通/高级运营按所属团队查看，管理员跨团队查看；唯一键为 team_id + platform + platform_content_id；定义来源审计、状态转换与 Cloud-owned 合同。
- 验收：设计与用户确认一致；同团队全量可见、跨团队拒绝、管理员跨团队可见；不同团队相同作品可各自建档。

### Task 2：交付内容池页面与读回

- 工作：以显式标注 fixture 的测试来源验证列表/详情、筛选、批处理与状态；统一入池服务供后续复用。
- 验收：页面/数据库一致；外部可访问性不覆盖处理状态，不能称 fixture 为真实采集。

### Task 3：交付人工转素材

- 工作：单条事务锁定来源、幂等创建或关联 material、更新状态与审计，批量独立提交。
- 验收：并发只有一个素材，失败不写 material_created；素材库可查来源快照，未转换零 material。

### Task 4：基础验收

- 工作：覆盖权限、忽略恢复、重复/并发及部分失败；记录基础能力证据。
- 验收：A 只作能力验收，B 的真实来源必须再次复验转素材；禁止据此宣告外部入口完整通过。

## Evidence 与提交边界

每项记录输入/角色、预期、实际、PASS/FAIL、环境版本、相关 ID 与脱敏截图。fixture/mock 与真实接口证据分开；HTTP 成功、任务创建、代码存在都不能替代业务读回。

Cloud 负责业务 API/数据库/Web 及正式合同；Agent 负责渠道执行适配；Desktop 复用 Web 不复制业务；Workspace 负责决策、治理索引和 Evidence。按提供方先行与消费者验证顺序，分别在各仓提交。

后续阶段的待决产品规则或缺真实依赖时不激活；本 CHG 的团队级规则已确认。不得为通过验收私自降级范围。若实施设计仍超出该独立闭环，暂停并回到规划，不横跨 A～E 全部实施。

## Checkpoint

- Completed：V2 文档级范围、依赖、任务与验收拆分；用户已确认团队级隔离规则。
- Current：HANDOFF；Cloud migration、内容池服务/API、团队范围校验、幂等转素材和 Web 内容池/素材库入口已实现；本记录的后续 M3-B～E 由 CHG-20260916-052 统一承载。
- Next：由 CHG-20260916-052 复用并复验内容池基础能力；本记录不再单独推进。
- Blockers：M3-A 不依赖外部接口；需要避免与其他未提交 Cloud 变更冲突。
- Verification：启动门已完成；`go test ./...`、Web `npm test`（19 files/74 tests）、`npm run build:cloud`、`npm run build:desktop` 均通过。自动化结果见 `evidence/20260916-implementation.md`。
