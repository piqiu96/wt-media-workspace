# ADR-0034：Agent 平台业务能力与发布执行边界

- Status: Accepted
- Date: 2026-11-19
- Scope: Agent 平台业务主体、浏览器公共能力与发布执行控制
- Supersedes: [ADR-0016](0016-agent-runtime-layering-and-dependency-boundaries.md) 第 5 条的平台目录决定，以及第 1–3 条中与本决定冲突的目录、依赖部分；其余约束继续有效。

## Context

发布流程和页面操作放在 clients 中混淆了外部协议与业务执行。用户确认将发布作为独立平台能力，保留按需扩展点赞、互动的边界；不新增 workflow 或通用执行引擎。

## Decision

1. `platforms/publish.py` 定义 Publisher、PublishPayload、PublishReceipt 和 PublishControl。接口不暴露 Playwright Page、Cloud Token、正式任务模型或 SQLite。
2. `platforms/baidu/publisher.py` 同文件组织 BaiduPublisher 与 BrowserPublisher。前者选择实现并组织发布步骤；后者管理本次连接、页面动作及平台回执，必要时调用 clients API。无须单独 browser 目录或 ApiPublisher 占位。
3. clients 继续封装 Cloud、BitBrowser、平台身份及其他实际 API 请求；services/browser 维护通用会话、CDP、Cookie；services/files 维护文件落盘与完整性校验。平台能力可组合 API 和浏览器；不是所有平台逻辑都迁出 clients。
4. 一期 `method` 默认并显式传入公共 `PublishMethod.BROWSER`；其他值在执行发布动作前拒绝。不增加用户选择页面、Cloud 字段或 API 投稿实现。未来独立能力按需增加协议和平台实现，不扩充成万能 Publisher。
5. runner 领取与准备所属任务，负责心跳、阶段持久化、Cloud 提交前许可、现场关闭核实、原结果保存和恢复补报。平台发布器通过必填的准备完成和提交前回调衔接；未知结果不自动重试或换通道。准备完成的持久化和 ready 报告必须发生在初次实读 UID 通过后，上传后再次核实 UID，提交屏障先于一次最终提交。
6. 新增依赖：bootstrap → platforms/services，runner → platforms/services，platforms → clients/services/runtime/utils，services → clients。platforms 不直接导入 runner/executors/storage/bootstrap/local_api、Cloud 任务客户端或底层 HTTP/数据库模块；API 请求经 clients。clients/services 不依赖 platforms；不通过放宽例外绕过现有依赖检查。
7. 业务状态、持久化结构、外部接口及已有恢复语义不变。浏览器断开不代表现场关闭；同一旧尝试不能凭检查点重放。Playwright 仍在同一执行线程，心跳仅传递停止信号。
8. **发布与原稿核验职责（2026-11-24 用户确认）。** `platforms/publish.py` 与 `platforms/publication_check.py` 分别定义发布和指定原稿核验的对外接口、输入、执行控制与结果。`platforms/baidu/publisher.py` 完整承担上传、文案解析与表单校验、提交及回执；原稿公开核验独立于本次投稿，在 `platforms/baidu/publication_check.py` 内完整组织 API 查询、浏览器降级、匿名公开证据，不按 API/浏览器手段拆出对外能力。真实复用的浏览器身份读取可独立保留；不为单项能力内部的解析、校验或异常单独拆文件。
9. runner 可以直接使用 services，平台能力可以使用 services/clients；不要求调用逐层经过。runner 管任务身份、授权、Profile 互斥、结果持久化与上报，并向核验接口提供受控资源入口；百度的通道选择和降级条件留在百度实现。`services/browser/session.py` 管只读 Profile 的打开、连接及关闭证据，任何打开尝试前清除原关闭证据，打开结果不明不接管或盲目关闭现场。clients 仅报告协议事实或协议错误，不决定切换浏览器。正式状态仍由 Cloud 裁决，对外 HTTP 契约不变。

## Consequences

当前架构基线、发布工程设计、Agent 目录规则、依赖测试和平台适配规则同步更新。业务主体可供其他已授权调用方使用，但必须传入执行控制，没有默认许可；正式状态仍由 Cloud 裁决。不改变 Cloud-owned 内容发现和合成范围。
