# Local trust binding fix evidence

## 时间

2026-07-24

## 问题

真实 Desktop 环境中，用户登录后进入「环境状态」，Local Agent 与 BitBrowser 均可用，但点击绑定/刷新本机可信状态后失败。

## 定位

Local Agent 能读取真实 BitBrowser 主账号和大量本机窗口 ID。原 Cloud runtime report 逻辑要求上报的每个 BitBrowser Profile 都已经在 Cloud 中属于当前用户。

真实使用中，用户本机 BitBrowser 可能存在大量尚未同步到 Cloud 的窗口；这些窗口应由 M2-B Profile Diff/接受本地变化流程处理，不应该阻断“本机可信绑定”。

## 修改

- Runtime report 仍接收 `bit_profile_ids`。
- 本机可信绑定只校验：
  - 用户会话有效；
  - Local Agent 节点凭证有效；
  - BitBrowser 主账号与系统绑定主账号一致；
  - BitBrowser 状态正常。
- 对已在 Cloud 建档的 Profile，继续写入 runtime presence。
- 对未知本机 Profile，不再拒绝本机可信绑定，后续由 Profile Diff 流程处理。

## 验证

自动测试：

```text
go test ./internal/modules/runtimebinding ./internal/modules/profileguard ./internal/modules/profilebinding
npm --prefix web test -- --run localAgentStatus profileBindings
```

结果：PASS。

真实接口模拟：

```text
登录 operator01
→ 创建 binding ticket
→ 注册 local agent node
→ 使用真实 Local Agent status 中的 main_user_id 与 bit_profile_ids 上报 runtime report
```

实际结果：

```text
runtime_report 200 {"errcode":0,"message":"success","data":null}
```

## 结论

本机可信绑定不再被“本机存在 Cloud 未同步窗口”阻断；用户可重新登录 Desktop 后执行绑定/刷新本机可信状态。
