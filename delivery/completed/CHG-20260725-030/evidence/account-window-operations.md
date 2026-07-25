# 媒体账号行打开/关闭窗口验证

日期：2026-07-25

## 修改事实

- `AccountsPage.vue` 在 Desktop 账号行新增：
  - 打开窗口；
  - 关闭窗口。
- 账号详情页也提供打开/关闭绑定窗口入口。
- 打开/关闭入口复用 B5 已完成的 Desktop 本机路径：
  - `createLocalAgentService().profileOpen(bit_profile_id)`；
  - `createLocalAgentService().profileClose(bit_profile_id)`；
  - Tauri/Rust → Local Agent → BitBrowser。
- Cloud Web 不展示账号行打开/关闭窗口入口。
- 只有账号已绑定 active 浏览器窗口，且能解析出 BitBrowser Profile ID 时，按钮才可用。

## 验证

- `npm test`：PASS，新增测试确认 account row window operations 通过 Tauri invoke：
  - `local_agent_profile_open`；
  - `local_agent_profile_close`。
- `npm run build`：PASS。

## 结论

媒体账号行打开/关闭窗口已接入 Desktop 本机同步操作路径；Cloud Web 仍只展示 Cloud 已保存事实。
