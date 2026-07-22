# Task 6 evidence：自动验证与收口检查

> 日期：2026-07-23  
> 范围：CHG-20260723-025 自动测试、构建、边界关键词和工作区差异检查

## 1. Agent 扫描快照测试

命令：

```text
python3 -m unittest tests/test_local_profile_scan.py
```

目录：

```text
wt-media-agent
```

结果：PASS。

覆盖事实：

- Local Agent Profile scan 返回安全快照；
- 快照包含运行状态和代理摘要；
- 测试未要求 Cookie、平台密码、代理密码等敏感明文进入响应。

## 2. Cloud Profile Diff 测试

命令：

```text
go test ./internal/modules/profilebinding/...
```

目录：

```text
wt-media-cloud
```

实际执行命令使用本地 Go 环境：

```text
env GOROOT=/Users/aqiuye/Develop/workspace/devenv/go26/go GOPATH=/Users/aqiuye/Develop/workspace/devenv/go19/gopath GOCACHE=/Users/aqiuye/Develop/workspace/wt-media/wt-media-cloud/.cache/go-build /Users/aqiuye/Develop/workspace/devenv/go26/go/bin/go test ./internal/modules/profilebinding/...
```

结果：PASS。

覆盖事实：

- Cloud 接收 Desktop 提交的扫描快照；
- Cloud 基于快照与已保存 `browser_profiles` 镜像计算只读 Diff；
- 扫描快照提交前校验本地可信 `node_id`；
- 不调用 Local Agent，不连接 BitBrowser，不应用 Diff。

## 3. Web 单元测试

命令：

```text
npm test -- profileBindings localAgentService
```

目录：

```text
wt-media-cloud/web
```

结果：PASS，2 个测试文件、4 个测试用例通过。

覆盖事实：

- `profileBindings.submit(snapshot, { nodeId })` 会把可信 `node_id` 提交给 Cloud；
- `createLocalAgentService.profileScan()` 通过 Tauri command `local_agent_profile_scan` 调用 Desktop Rust；
- Web 层不直接持有 Local Agent token，也不直接发起 Profile 扫描 HTTP 请求。

## 4. Desktop Rust 检查

命令：

```text
cargo check
```

目录：

```text
wt-media-desktop/src-tauri
```

结果：PASS。

说明：命令输出存在既有 unused warning，本 Task 未新增阻塞性 Rust 编译错误。

覆盖事实：

- `local_agent_profile_scan` Tauri command 所在 Desktop Rust 工程可以通过编译检查；
- Desktop 侧继续由 Rust 桥接 Local Agent，而不是让 Vue 直连 Local Agent 动态端口或 token。

## 5. Web 构建

命令：

```text
npm run build:cloud
npm run build:desktop
```

目录：

```text
wt-media-cloud/web
```

结果：PASS。

说明：Vite 输出 chunk size warning，为当前构建体积提示，不阻断本 CHG。

覆盖事实：

- Cloud Web 构建通过；
- Desktop Web 构建通过；
- 浏览器窗口页面的 Cloud / Desktop 条件展示可进入构建产物。

## 6. 页面边界关键词检查

命令：

```text
rg -n "触发扫描|扫描本机窗口|确认同步窗口|仅确认主账号|接受本地变化|恢复Cloud配置|127\\.0\\.0\\.1:8765" wt-media-cloud/web/src/modules/profiles/pages/ProfilesPage.vue wt-media-cloud/web/src/apps/desktop/features/local-agent
```

结果：

- `ProfilesPage.vue` 仅保留 Desktop 专用的“扫描本机窗口”入口；
- 不再存在可点击的“确认同步窗口”；
- 不再存在“仅确认主账号”动作；
- “接受本地变化”“恢复Cloud配置”仅作为后续 CHG 的禁用提示；
- 业务页面未直连 `127.0.0.1:8765`；
- `127.0.0.1:8765` 仅存在于 Desktop Local Agent 初始化/状态服务，不属于浏览器窗口业务页直连。

## 7. 工作区差异检查

命令：

```text
git -C wt-media-agent status --short
git -C wt-media-desktop status --short
git -C wt-media-cloud status --short
git -C wt-media-workspace status --short
```

结果：

- `wt-media-agent`：干净；
- `wt-media-desktop`：干净；
- `wt-media-cloud`：干净；
- `wt-media-workspace`：仅存在既有 `docs/engineering/.DS_Store` 脏文件，本 Task 未纳入提交。

## 8. 结论

Task 6 的自动验证部分已完成：

- Cloud 只读 Diff 自动测试通过；
- Desktop / Rust / Local Agent 路径编译与 Web 单测通过；
- Cloud Web 与 Desktop Web 构建通过；
- 关键词检查证明 Cloud Web / Desktop 页面边界没有再次混淆；
- 当前仍需要真实页面人工验收后，才能把本 CHG 从实现收口推进到最终关闭。
