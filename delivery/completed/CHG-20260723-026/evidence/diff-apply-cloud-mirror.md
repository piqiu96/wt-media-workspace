# Task 2 Evidence：接受本地变化应用 Cloud 镜像

> 日期：2026-07-23  
> CHG：CHG-20260723-026  
> 范围：Desktop 接受本机扫描 Diff，按允许字段更新 Cloud 浏览器窗口镜像

## 1. 用户操作

Desktop 浏览器窗口页：

```text
扫描本机窗口
→ 查看本机扫描结果
→ 点击「接受本地变化」
→ 二次确认
→ Cloud浏览器窗口镜像按允许字段更新
→ 列表刷新
```

Cloud Web 仍不展示本机扫描和 Diff 处理入口。

## 2. 系统行为

本 Task 已实现：

- `POST /api/v1/bit-browser/profile-scans/{scan_id}/confirm` 要求提交 `node_id`；
- Cloud 在应用 Diff 前校验当前用户与本机节点可信关系；
- Desktop 前端确认后通过当前本机 `node_id` 调用 confirm；
- confirm 成功后刷新浏览器窗口列表。

## 3. 允许更新字段

接受本地变化时，Cloud 允许同步 BitBrowser 读回的窗口镜像字段：

- `main_user_id`
- `profile_user_id`
- `name`
- `seq`
- `group_id`
- `group_name`
- `bit_status`
- `bit_updated_at`
- `proxy_type`
- `proxy_host`
- `proxy_port`
- `local_status`
- `last_synced_at`

## 4. 被保护字段

接受本地变化不会覆盖：

- 授权用户；
- 运营分组/团队归属；
- 媒体账号绑定；
- 游戏、标签、业务状态；
- Cookie；
- Cloud 备注 `remark`。

实现约束：

- 新增窗口可以使用扫描候选的 `remark` 初始化；
- 已存在窗口再次接受本地变化时，不会用本机扫描备注覆盖 Cloud 备注。

## 5. 自动验证

### 后端

命令：

```text
env GOCACHE=/Users/aqiuye/Develop/workspace/wt-media/wt-media-cloud/.cache/go-build go test ./internal/modules/profilebinding ./internal/modules/runtimebinding
```

目录：

```text
wt-media-cloud
```

结果：PASS。

覆盖事实：

- confirm scan 需要可信 `node_id`；
- 缺少 `node_id` 或本机节点不可信时不会应用 Diff；
- 已存在窗口接受本地变化时保留 Cloud 备注；
- 缺失窗口仅标记为 `local_missing`，不物理删除。

### 前端 API / Local Agent

命令：

```text
npm test -- profileBindings localAgentService localAgentStatus
```

目录：

```text
wt-media-cloud/web
```

结果：PASS，3 个测试文件、6 个测试用例通过。

覆盖事实：

- `confirm(scanId, { nodeId })` 会把 `node_id` 发给 Cloud；
- 本机扫描仍通过 Desktop/Tauri/Local Agent 路径；
- 本机状态读取未被本 Task 改坏。

### Web 构建

命令：

```text
npm run build:desktop
npm run build:cloud
```

目录：

```text
wt-media-cloud/web
```

结果：PASS。

说明：Vite chunk size warning 为当前体积提示，不阻断本 Task。

## 6. 尚未包含

本 Task 不包含：

- 恢复 Cloud 配置写回 BitBrowser；
- 窗口授权；
- 比特账号绑定摘要展示；
- 媒体账号绑定；
- 账号检查；
- Cookie 或代理写入。

这些继续按 CHG-20260723-026 Task 3 / Task 4 执行。
