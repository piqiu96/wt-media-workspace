# ADR-0008: Local BitBrowser Operation Execution Model

- Status: Accepted
- Date: 2026-07-22
- Scope: M2 Browser Profile、代理、Cookie、账号检查和上号

## Context

BitBrowser Local API 的创建、修改、打开、关闭、Cookie和代理接口是同步调用。此前工程基线把浏览器自动化统一描述为 Cloud 异步 task，导致短操作只返回“任务已创建”、页面无法立即看到读回结果，也把批量业务过程与底层API调用混为一谈。

## Decision

- 单项且可在一次用户操作内完成并读回的 BitBrowser 操作，使用 Desktop 经 Tauri 调用 Local Agent 的同步链路；
- 调用前由 Cloud 校验会话、角色、运营分组、游戏范围、Desktop节点、`main_user_id`、Profile授权和敏感操作互斥；
- Agent 同步调用 BitBrowser 并立即读回，Cloud 只接受经过验证的结果作为正式事实；
- 批量Profile、批量代理、批量检查和三种上号方式使用各自的 batch/item 业务过程，Agent 在每个item内同步调用BitBrowser；
- 发布、互动、合成等长耗时、可恢复流程继续使用通用异步task；
- 同步调用超时但外部结果无法证明时，进入结果待确认，不自动重试。

## Consequences

- 页面可以在单项操作后直接显示真实结果，不再用“任务已创建”冒充成功；
- Cloud仍是正式业务事实中心，Agent仍是BitBrowser唯一执行入口，Desktop仍是本地安全控制壳；
- 现有Profile、代理、Cookie和账号检查任务接口需要审计，按单项同步与批量过程重新归类；
- Tauri与Local Agent需要受控同步调用Contract，Vue不得直接访问Agent端口或动态凭据。
