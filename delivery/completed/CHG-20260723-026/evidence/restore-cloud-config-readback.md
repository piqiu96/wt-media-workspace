# Task 3 Evidence：恢复 Cloud 配置写回 BitBrowser 并读回验证

> 日期：2026-07-23  
> CHG：CHG-20260723-026  
> 范围：Desktop 从扫描 Diff 中选择 Cloud 已保存窗口，将 Cloud 安全配置写回本机 BitBrowser，并重新扫描读回验证

## 1. 用户操作

Desktop 浏览器窗口页：

```text
扫描本机窗口
→ 查看本机扫描结果
→ 点击「恢复Cloud配置并读回验证」
→ 二次确认
→ Desktop/Rust 写回 BitBrowser
→ Desktop/Rust 重新扫描读回
→ 读回一致后把新快照提交 Cloud 重新计算 Diff
→ 页面展示恢复结果或可理解失败原因
```

本 Task 不在 Cloud Web 提供恢复入口。

## 2. 系统行为

本 Task 已实现：

- Desktop Vue 只从当前 Diff 的 `changed` 和 `missing` 中选择 Cloud 已存在窗口作为恢复目标；
- 本地新增但 Cloud 没有正式镜像的窗口不会进入恢复 Cloud 配置，只能走“接受本地变化”；
- Vue 通过 Tauri invoke 调用 `local_agent_profile_restore`，不直接访问 Local Agent 端口或凭据；
- Rust 调用 Local Agent `/api/v1/bit-browser/profile-update` 同步写 BitBrowser；
- 写回完成后 Rust 调用 Local Agent `/api/v1/bit-browser/profile-scans` 重新读回；
- Rust 校验名称、分组和代理摘要等安全字段读回一致后才返回成功；
- 读回不一致、找不到窗口或 Local Agent / BitBrowser 写回失败时返回“恢复结果待确认/失败”，不会显示假成功；
- 成功后 Vue 将读回 snapshot 提交 Cloud，刷新本次扫描 Diff 和浏览器窗口列表。

## 3. 写回字段边界

恢复 Cloud 配置只写入 BitBrowser 窗口基础配置：

- `bit_profile_id` → BitBrowser `id`
- `name`
- `seq`
- `group_id`
- `group_name`
- `proxy_type`
- `proxy_host`
- `proxy_port`
- `remark`

不会写入：

- 系统用户授权；
- 媒体账号绑定；
- 游戏、标签、业务状态；
- Cookie；
- Agent 凭据、Token 或本地端口。

## 4. 自动验证

### Desktop Rust

命令：

```text
cargo test --manifest-path wt-media-desktop/src-tauri/Cargo.toml
cargo check --manifest-path wt-media-desktop/src-tauri/Cargo.toml
```

结果：PASS。

覆盖事实：

- 恢复 payload 只包含安全窗口字段，不包含 Cookie 或用户授权字段；
- 读回字段一致时通过；
- 读回名称不一致时失败，不会报告成功。

说明：现有 Rust warning 为历史 scaffold 未使用项，本 Task 未新增阻塞 warning。

### Frontend Local Agent Service

命令：

```text
npm --prefix wt-media-cloud/web test -- --run localAgentService
```

结果：PASS，1 个测试文件、2 个测试用例通过。

覆盖事实：

- `profileRestore` 通过 Tauri command `local_agent_profile_restore` 调用；
- 参数只经 Desktop/Tauri 通道传递，不暴露 Local Agent 动态端口。

### Web 构建

命令：

```text
npm run build:desktop --prefix wt-media-cloud/web
npm run build:cloud --prefix wt-media-cloud/web
```

结果：PASS。

说明：Vite chunk size warning 为当前体积提示，不阻断本 Task。

### Diff Check

命令：

```text
git -C wt-media-cloud diff --check
git -C wt-media-desktop diff --check
git -C wt-media-workspace diff --check
```

结果：PASS。

## 5. 尚未包含

本 Task 不包含：

- 窗口授权；
- 比特账号绑定摘要展示；
- 媒体账号台账与 Profile 绑定；
- 账号检查；
- 代理、Cookie 或上号流程。

这些继续按 CHG-20260723-026 Task 4 / Task 5 以及后续 M2-B3、M2-B4 执行。
