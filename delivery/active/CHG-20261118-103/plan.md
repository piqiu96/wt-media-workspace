# 2026-11-20 PR review 修订实施

设计依据：发布工程设计“基础资料与执行现场的边界”；用户已批准实施、PR review、各仓提交和 Workspace 回写。

1. Cloud103：保留本会话既有 report/attempt/状态常量/乐观更新改动；移除三个基础模块六个 publication_guard 文件及普通资料检查；Profile 删除必要引用检查集中 service/reference.go，通过发布 Service 查询所有任务和历史尝试引用。验证基础服务与相关事务。
2. Cloud103：准备、ready、submitting 检测输入失效，报告明确停止及原因；不得授予提交，保活不重查资源；保留原结果/hash/顺序和 revision 保护。测试条件变化及重复上报。
3. Agent：同步提供方 report 和 singular attempt；统一实际 Profile 操作互斥，保留未决发布持久屏障；仅可证明无提交和现场结束时 failed，其他 uncertain。验证本地 API、协调器、存储和完整离线测试。
4. Cloud104：在 103 提交后同步基础分支，逐项 review 原尝试读取、resolve/retry 的引用、状态和并发边界；修复同类问题并单独验证与提交。
5. 各仓最终 review 与检查，提交至各自分支。Workspace 记录提交、测试、剩余限制，更新 PR review 和说明。不合并 PR，不把离线测试当真实投稿通过。

## 执行记录

- 已确认 Cloud103 当前分支 chg/CHG-20261118-103，Cloud104 为 PR46 / codex/CHG-20261118-104；104 工作树干净。
- 原有 Cloud103 和 Agent 工作区改动均来自当前会话已授权修订；保留并纳入验证提交。
- 仅删除真实存在的破坏性引用保护才添加 checker，避免为无删除入口的 mediaaccount 或无发布直接引用的 proxy 创建空接口。

- Cloud103 两次提交与 Go/MySQL/前端验证已完成；Agent 操作互斥、失败分类和完整787项通过。
- Cloud104 已同步103，移除 recovery task/attempt 悲观锁和基础 scene 锁接口，CAS 与原结果/并发核实测试通过；完整回归进行中。
- 最终独立审查发现4项问题，均加入先失败回归并修复，Agent790项与Cloud完整Go/隔离MySQL通过。
- 引用竞争裁定：使用发布任务真实外键（冻结JSON存储生成列），服务层提供友好引用错误、数据库做原子裁决；不将跨域回调重新放回基础Repository。
- Agent原有PR已合并，当前修订独立分支codex/chg103-104-review，合入远端main后复验；不向已合并PR冒充追加交付。
- 单进程准入假设保留，checkpoint提供重启未决保护；无多进程能力承诺，不做真实平台验收。
- 当前代码提交完成，Workspace与PR最终回写进行中。
