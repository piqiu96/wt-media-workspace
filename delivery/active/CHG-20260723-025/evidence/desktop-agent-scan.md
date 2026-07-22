# Task 4 evidence：Desktop / Rust / Local Agent 同步扫描路径

> 日期：2026-07-23  
> 范围：浏览器窗口页扫描路径从 Vue 直连 Local Agent 改为 Desktop Rust 代理

## 1. 本次事实变更

### Desktop Rust

- 新增 Tauri command：`local_agent_profile_scan`。
- 该命令由 Rust 调用 Local Agent：

```text
POST http://127.0.0.1:8765/api/v1/bit-browser/profile-scans
```

- Vue 不再直接访问 Local Agent 端口，也不持有 Local Agent token。
- Rust 只透传 Agent 返回的安全快照，不解释业务字段。

### Cloud Web / Desktop Web

- `createLocalAgentService` 增加 `profileScan()`，通过 Tauri `invoke("local_agent_profile_scan")` 调用 Rust。
- `ProfilesPage.vue` 扫描流程改为：

```text
Desktop Vue
→ Tauri invoke local_agent_status 读取可信 node_id
→ Tauri invoke local_agent_profile_scan 读取 BitBrowser 快照
→ Cloud profileBinding.submit(snapshot, { nodeId })
→ Cloud 计算只读 Diff
```

- 浏览器窗口页不再直连 `127.0.0.1:8765`。
- 非 Tauri Desktop 客户端环境会阻断扫描并提示只能在 Desktop 客户端执行。

## 2. 明确未做

- 未应用 Diff；
- 未接受本地变化；
- 未恢复 Cloud 配置；
- 未创建、打开、关闭或更新窗口；
- 未绑定媒体账号；
- 未修改 Agent BitBrowser adapter。

## 3. 验证命令与结果

### Desktop Rust

命令：

```text
cargo check
```

结果：PASS。

说明：存在既有 unused warning，不影响本 Task。

### Web 单元测试

命令：

```text
npm test -- profileBindings localAgentService
```

结果：PASS，4 tests。

覆盖：

- `profileBindings.submit(snapshot, { nodeId })` 将可信 `node_id` 提交给 Cloud；
- `createLocalAgentService.profileScan()` 通过 `local_agent_profile_scan` Tauri command 调用 Rust；
- 扫描快照仍使用 allow-list，不提交 Cookie 或代理密码。

### Web 构建

命令：

```text
npm run build:cloud
npm run build:desktop
```

结果：PASS。

说明：项目当前跟踪 `web/dist-cloud` 与 `web/dist-desktop` 构建产物，本次构建产物随 Cloud Web 源码一起提交。

## 4. 结论

Task 4 已完成 Desktop / Rust / Local Agent 同步扫描路径：

- Desktop Vue 不再直接访问 Local Agent 动态端口；
- 本机扫描由 Tauri/Rust 代理；
- Cloud 仍只接收 Desktop 提交的快照并计算只读 Diff；
- 本任务没有引入异步任务，也没有产生 Diff 应用副作用。
