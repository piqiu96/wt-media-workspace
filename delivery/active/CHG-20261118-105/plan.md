# CHG-105 发布职责重整实施清单

依据：[发布工程设计](../../../docs/engineering/specs/publishing-management.md)、[ADR-0034](../../../docs/decisions/0034-agent-platform-capabilities-and-publish-boundary.md) 和用户最终 Review。

- [x] 新增平台发布公共入口测试，复现入口缺失；覆盖 browser 默认/显式参数、非法方式零动作、两次身份检查、阶段回调、许可失败、停止、一次提交、断开连接及旧实例不可重入。
- [x] runtime/constants.py 集中 PublishMethod；platforms/publish.py 定义不可变载荷、回执和必填控制回调；协议不接受 Page/Token/Cloud 任务。
- [x] clients/browser.py → services/browser/session.py；clients/baidu/publisher.py 的现有页面实现迁为 BrowserPublisher，同文件新增 BaiduPublisher。初次 UID 成功后回调准备完成；上传后 UID 成功才请求提交前许可；不修改封面原字节、格式识别及现有页面回执保护。
- [x] clients/publication.py 的下载完整性校验迁为 services/files/verified_download.py，复用 clients/transfer/source.py；身份组合移到百度实现，Profile 启动保留在任务资源准备。
- [x] preparation 提供 prepared/ready 回调，Job 只调用发布入口并显式传 browser；维持现有阶段、报告序号与关闭/存储/恢复语义，bootstrap 显式装配，不建立全局注册表。
- [x] 迁移现有存储故障、任务、准备、页面、浏览器会话测试和冻结包探针导入，增加平台依赖规则的正反例；全量 Agent 回归、隔离 Chrome、wheel/sdist 和冻结 Sidecar 检查实际执行并记录结果。
- [x] 同步正式架构、发布设计、本仓职责/目录图、Workspace 平台规则源及生成副本；独立审查通过；使用现有 Agent #12 / Workspace #56 交付，保留 VERIFYING，不合并。

公共接口：Publisher.publish(payload, control, *, method=PublishMethod.BROWSER) -> PublishReceipt。PublishPayload 包含视频/封面本地路径、确认内容、预期 platform_uid；PublishControl 必填 stopped/on_prepared/before_submit。执行控制异常直接中止，不捕获为继续许可。

修改范围仅 Agent 和 Workspace。Cloud、Desktop、业务状态、数据库迁移和对外契约不变。已有 CHG101/UI 未提交内容保留，不纳入本轮提交。

- [ ] 用户对更新后的两个 PR 再次 Review；合并不在本轮执行范围。
