---
id: CHG-20261118-103
parent: delivery/milestones/M6-single-publishing.md#单任务从内容准备到真实作品
status: VERIFYING
depends_on: ["CHG-20261118-102"]
affected_repos: ["wt-media-workspace", "wt-media-cloud", "wt-media-agent", "wt-media-desktop"]
risk: H
---

# CHG-20261118-103: M6-B 所属用户领取与执行前检查

## Change

把已确认任务接入执行授权、按账号所属用户领取、固定 attempt 输入、UID/Profile 互斥和提交前复查；Cloud 保存过程和原结果，Agent 核实本机 UID 及实际文件并使用前置 CHG 的持久化边界。共享页面提供独立执行确认及实际尝试进展，Desktop 更新提供方契约锁，不复制业务逻辑。必要 CI 整改仅修复干净 macOS 测试环境中的调试资源定位，正式安装包校验不放宽。

先更新 Cloud 提供方契约，再实现事务与隔离数据库测试、Agent 消费及真实文件/身份检查，最后用实际页面授权并检查服务器与本机记录。受控验证只允许安全未提交结果，不模拟平台成功。百度上传填写与最终点击在下一单元接入；本单元不启用无实现的投稿循环，不将检查通过当作投稿成功。

本轮继续按用户明确授权串行堆叠：Workspace 基于 CHG-102，Cloud 基于 CHG-101，Agent 基于 CHG-102，Desktop 基于 main；分别保留可审查差异与 PR，不自动合并。既有 start 的前置合并限制不改写；本次临时例外在这里记录。

2026-11-19 按已确认 ORM 方案适配：领取键改用共享 Database/Session，身份按显式 `cloud_env/user_id` 隔离；准备阶段使用原始 task/attempt ID。Desktop 将 Cloud 地址和环境成对传给 Sidecar，开发包可连接 prod；不改 Cloud 状态、报文摘要算法或平台准备范围。

后续存储清理已落在同一 PR：`PublicationClaimStore` 归入 `storage/publication.py`，保留独立类，旧文件删除；插入差异委派 Database 适配，准备补报调用既有 Runner。领取键生命周期、原请求值、状态和报告摘要不改变，当前验证见原 evidence。

用户进一步确认 Agent/Desktop 的 `environment` 也统一为 dev/test/pre/prod。Desktop 配置、页面/诊断输出和 Sidecar 的 `WT_MEDIA_ENV` 同步；`cloud_env` 独立，开发应用可连接 prod。原 release 强制 prod 校验、安装目录和 fallback 限制保持，非 release 的 test/pre 使用非 prod 策略；旧环境拼写须按配置说明更新。

## Done When

- 实际共用页面单独确认执行，保存授权与审计；未来时间不提前领取，已授权输入不可被编辑覆盖。
- 仅所属用户有效 Desktop 会话的 Agent 能领取；原请求键重放同一 attempt，跨用户代执行、同 UID/实际 Profile 并发及未完成现场复用均拒绝。
- 冻结输入不含临时 URL；传输地址只在响应签发；本机实读 UID、文件大小和摘要，错误输入不得进入提交。
- progress 的提交前复查读取当前授权、资源及停止状态，响应丢失不重放点击；旧会话不能领取或开始新动作，原 attempt 的合法结果仍可 report-safe 补报。
- 单调序号和原结果摘要防止旧报告或冲突结果覆盖；失联保留结果待确认，不派新尝试、不释放现场。审核回执不冒充公开成功。
- 实际隔离 MySQL、协议、Agent 与页面测试通过；现有安装包组合可构建，记录未验证内容。M6 不标记 DONE。

## References

- [M6](../../milestones/M6-single-publishing.md#单任务从内容准备到真实作品)，M6-B。
- [发布工程设计](../../../docs/engineering/specs/publishing-management.md)：2.2、3.4/3.5/3.7、4、5.3、6。
- [PRD 第六章](../../../docs/product/prd/详细文档/第六章_发布管理.md)：6.4、6.5、6.8。
- Cloud 原型 `web/example/proto/publishing-design/TaskDetail.vue`、`PublishingTaskPage.vue`，业务路由 `/example/operations/publishing/tasks`；访问地址以本次原型服务启动输出为准。
- [AdminUI](../../../docs/standards/frontend/AdminUI页面规范.md)、[交互](../../../docs/standards/frontend/前端交互规范.md)、[视觉与组件](../../../docs/standards/frontend/前端架构与视觉规范.md)。
