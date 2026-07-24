# Desktop 新建窗口验证

日期：2026-07-24

## 修改事实

- `wt-media-agent` 新增 Local Agent HTTP 入口：
  - `/api/v1/bit-browser/profile-groups`
- `wt-media-agent/contracts/local-agent-api/v1/local-agent.openapi.yaml` 已补充分组读取契约。
- `wt-media-desktop/src-tauri/src/main.rs` 新增：
  - `local_agent_profile_groups`
  - `local_agent_profile_create`
- 新建窗口必须提供：
  - 窗口名称；
  - BitBrowser真实分组ID。
- Rust 创建成功后会立即扫描 BitBrowser，并校验读回快照包含新窗口 ID。
- `ProfilesPage.vue` 新建窗口弹窗已改为：
  - 读取 BitBrowser 分组；
  - 用户选择真实分组；
  - 调用 Desktop 本机创建；
  - 读回后提交 Cloud scan 并确认同步 Cloud 镜像。

## 验证

- `python3 -m unittest tests/test_local_profile_operations.py tests/test_local_account_check.py`：PASS
- `cargo test`：PASS
- `npm test`：PASS
- `npm run build`：PASS

## 结论

新建窗口不再只创建 Cloud 记录；必须真实调用 BitBrowser 创建并读回确认。
