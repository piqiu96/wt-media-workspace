# Desktop 打开/关闭窗口验证

日期：2026-07-24

## 修改事实

- `wt-media-desktop/src-tauri/src/main.rs` 新增：
  - `local_agent_profile_open`
  - `local_agent_profile_close`
- 两个命令均通过 Rust 调用 Local Agent：
  - `/api/v1/bit-browser/profile-open`
  - `/api/v1/bit-browser/profile-close`
- 命令执行成功后会再次调用 `local_agent_profile_scan` 读回 BitBrowser 快照。
- `wt-media-cloud/web/src/apps/desktop/features/local-agent/service.js` 新增 `profileOpen`、`profileClose`。
- `wt-media-cloud/web/src/modules/profiles/pages/ProfilesPage.vue` 的打开/关闭按钮已改为调用 Desktop Local Agent service，不再调用 Cloud `/browser-profiles/:id/open|close`。

## 验证

- `cargo test`：PASS
- `npm test`：PASS
- `npm run build`：PASS

## 结论

打开/关闭窗口已经从“Cloud创建异步任务”改为“Desktop → Rust → Local Agent → BitBrowser”的同步本机操作路径。
