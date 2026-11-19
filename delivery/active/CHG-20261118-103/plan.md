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
- Cloud PR45/46已推送并追加最终review，Agent草稿PR13已建立，Workspace PR54/55已回写；代码和文档工作树保持可继续review，不合并PR。

## 第二轮基础边界与并发清理（已授权实施）

1. 先更新发布工程设计；删除基础九个 publication.go，将有用查询并回 identity/mediaaccount/profilebinding/production 的现有 Service/Repository 及 files/service.go，基础 Repository 不判断发布资格。
2. migration109 为 attempt 增加执行槽和活动 Profile/用户槽唯一约束，回填旧数据；覆盖并发、释放、未决占位及迁移拒绝错误历史。移除普通读取七处 FOR SHARE 和 Profile/owner FOR UPDATE；执行复查事务使用 READ COMMITTED，正式文件引用锁保留。
3. 发布 Service 统一比较资格/冻结输入，Repository 只读取所属事实；report.go 改通用 JSON 序列化并保持现有 Python 摘要样例一致。
4. 先跑失败回归，再实施并运行相关 Go、隔离 MySQL；完成103提交后同步104、检查恢复路径并复验；最终独立 review、修复、推送原PR45/46，回写 Workspace PR54/55。不合并PR。

- 第二轮103已提交42d9771；两项数据库/阻塞回归RED→GREEN，完整Go与全部发布隔离MySQL通过，原摘要及扩展边界样例一致。104已顺序同步，恢复路径当前事实读取与原现场释放验证进行中。

- 第二轮104完整Go与全部发布隔离MySQL通过，恢复使用当前已提交输入；最终独立review无可行动发现，模型摘要测试独立通过。Cloud103提交42d9771，Cloud104提交e6f4847，推送原PR45/46；Workspace按原PR54/55提交。无额外裁定或延后minor。
