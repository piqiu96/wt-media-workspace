---
id: CHG-20261118-102
parent: delivery/milestones/M6-single-publishing.md#单任务从内容准备到真实作品
status: VERIFYING
depends_on: ["CHG-20261118-101"]
affected_repos: ["wt-media-workspace", "wt-media-agent"]
risk: H
---

# CHG-20261118-102: M6-B 本地提交防重与补报

## Change

先落实首次自动投稿所必需的本地安全单元：复用现有 SQLite checkpoint/outbox，按环境、用户和 attempt 隔离记录；领取输入不可覆盖，提交边界先落盘，任何重启或重复调度均不重放浏览器动作。结果与待补报记录同一事务保存，断网只重发原结果。同 Profile 未核实现场保持占用，不能以失联或补报成功自动释放。

CI 实测首次切换 SQLite WAL 时多连接会立即争锁失败。仅对连接初始化中的 BUSY/LOCKED 作有界重试，非争锁错误关闭连接并直接失败，不重放任务事务或外部动作。

本单元包含 Agent 的存储适配、执行协调器和可复现故障测试，不新增 Cloud API 或 Desktop 页面，不启用真实平台自动投稿。后续同属 M6-B 的领取、平台适配与实际投稿接入此单元；它不是独立业务 Milestone，也不代表首次投稿完成。

执行顺序：先用实际 SQLite 与进程重启测试复现存储缺口，再实现事务及执行防重，最后运行 Agent 回归并提交独立 PR。本次用户允许临时依赖尚未 Review 的 CHG-20261118-101，Workspace 串行堆叠分支；Agent 从最新 main 建分支。一个执行器，不修改长期治理规则，不自动合并。

## Done When

- 同一环境、用户、attempt 重复接收不覆盖输入、不重复执行；跨环境、用户、下载业务的同号任务互不覆盖。
- 同一实际 Profile 的未结束现场拒绝新执行；结果未知及重启不释放；只有明确安全结算才能结束本地占用。
- 提交阶段持久化早于提交前复查与浏览器点击；复查拒绝、响应丢失、点击前后崩溃、结果上报断网均不自动重放点击。
- 结果和 outbox 原子持久化；旧序号、冲突结果、非所属用户补报明确拒绝；重启补报仅发送原结果。
- 定向及 Agent 回归测试通过，证据记录真实 SQLite/进程故障与已验证范围；没有真实平台成功声明。

## References

- [M6](../../milestones/M6-single-publishing.md#单任务从内容准备到真实作品)，M6-B 候选。
- [发布工程设计](../../../docs/engineering/specs/publishing-management.md)：2.2、3.7、4.2、4.5。
- [PRD 第六章](../../../docs/product/prd/详细文档/第六章_发布管理.md)：6.4、6.5。
