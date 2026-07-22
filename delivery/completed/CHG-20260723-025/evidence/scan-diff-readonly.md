# Task 3 evidence：Cloud 只读 Diff

> 日期：2026-07-23  
> 范围：Cloud 接收 Desktop 扫描快照后，只计算 Diff，不读取本机 BitBrowser，不修改正式镜像

## 1. 本次边界

Cloud 在本任务中的职责是：

```text
接收 Desktop 提交的 Local Agent / BitBrowser 扫描快照
→ 校验当前用户与 Desktop node 本地信任
→ 对比 Cloud 已保存 browser_profiles 镜像
→ 生成 profile_sync_scan 和只读 Diff
→ 返回 Diff 给调用方
```

Cloud 不负责：

- 调用 Local Agent；
- 连接 BitBrowser；
- 读取本机环境；
- 应用 Diff；
- 修改正式 `browser_profiles`；
- 修改授权用户、媒体账号绑定或其他业务对象。

## 2. 本次事实变更

### Cloud API

- `POST /api/v1/bit-browser/profile-scans` 现在要求请求携带 `node_id`。
- Cloud 在接收扫描快照前调用 `CheckLocalTrust(user_id, node_id)`。
- 没有 `node_id` 时返回 `400`。
- 本地信任不可用时返回 `409`，并且不会创建 scan。

### Cloud Service

- `SubmitScan` 仍只处理扫描快照与 Cloud 镜像对比。
- `SubmitScan` 不调用 Local Agent / BitBrowser。
- `SubmitScan` 不写入正式 `browser_profiles` 或 binding。

### Web Client

- `profileBindings.submit(snapshot, { nodeId })` 支持提交 `node_id`。
- 该能力用于后续 Desktop 通过 Tauri/Rust 获取可信 node 后提交 Cloud。

## 3. 验证命令与结果

### Cloud profilebinding

命令：

```text
env GOROOT=/Users/aqiuye/Develop/workspace/devenv/go26/go GOPATH=/Users/aqiuye/Develop/workspace/devenv/go19/gopath GOCACHE=/Users/aqiuye/Develop/workspace/wt-media/wt-media-cloud/.cache/go-build /Users/aqiuye/Develop/workspace/devenv/go26/go/bin/go test ./internal/modules/profilebinding/...
```

结果：PASS。

覆盖：

- `SubmitScan` 生成 Diff 但不修改正式 profiles/bindings；
- Route 创建 scan 后正式 profiles 仍为空；
- 缺少 `node_id` 时拒绝请求，且不创建 scan；
- 本地信任不可用时拒绝请求，且不创建 scan；
- confirm / confirm-main-identity 仍作为后续能力保留，不属于本 Task 的只读扫描完成条件。

### Cloud Web

命令：

```text
npm test -- profileBindings
```

结果：PASS，3 tests。

覆盖：

- 前端提交扫描快照时可携带 `node_id`；
- 快照字段仍使用 allow-list；
- Cookie 和代理密码不会进入提交 payload。

## 4. 结论

Task 3 已按修正后的边界完成 Cloud 只读 Diff 约束：

- Cloud 只接收快照并计算 Diff；
- Cloud 不读取本机 BitBrowser；
- Cloud 不调用 Local Agent；
- Cloud 不修改正式 Profile 镜像、授权关系或媒体账号绑定；
- 没有可信 Desktop node 的扫描快照会被拒绝。
