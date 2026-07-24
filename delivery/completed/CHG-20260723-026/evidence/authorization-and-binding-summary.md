# CHG-20260723-026 Task 4 Evidence：窗口授权与只读摘要展示

> 日期：2026-07-23

## 验证目标

验证 M2-B2 的窗口授权与只读摘要只改变 Cloud 业务授权关系，不触发 Desktop、Local Agent 或 BitBrowser 操作。

## 实现事实

- 新增 Cloud API：`POST /api/v1/browser-profiles/:id/assign-owner`。
- 仅管理员可以分配浏览器窗口授权。
- 目标用户必须是启用中的普通运营，并且必须有运营分组。
- 已被 `media_accounts.browser_profile_id` 引用的窗口会被拒绝分配，避免造成媒体账号与窗口关系错乱。
- 分配动作只更新 Cloud `browser_profiles.user_id`、`team_id` 和审计日志，不调用 Agent，不写 BitBrowser。
- 浏览器窗口列表增加“授权用户”列。
- 浏览器窗口详情增加只读摘要：脱敏主账号、授权用户、最近同步时间。
- 管理员可在 Cloud 窗口列表中打开“分配浏览器窗口”弹窗；弹窗明确提示不会操作本机 BitBrowser。

## 自动验证

### 后端测试

命令：

```bash
env GOCACHE=/Users/aqiuye/Develop/workspace/wt-media/wt-media-cloud/.cache/go-build go test ./internal/modules/profilebinding ./internal/modules/identity
```

结果：PASS

覆盖点：

- 管理员可以分配未被媒体账号引用的窗口；
- 非管理员不能分配窗口；
- 高级运营不能作为窗口授权目标；
- 已被媒体账号引用的窗口不能直接分配；
- 路由层返回可理解的冲突错误。

### 前端 API 测试

命令：

```bash
npm --prefix wt-media-cloud/web test -- --run profileBindings usersApi
```

结果：PASS

覆盖点：

- `assignProfileOwner` 使用 Cookie 凭据；
- 请求路径为 `/api/v1/browser-profiles/:id/assign-owner`；
- 请求体只包含目标 `user_id`。

### 前端构建

命令：

```bash
npm run build:desktop --prefix wt-media-cloud/web
npm run build:cloud --prefix wt-media-cloud/web
```

结果：PASS

## 结论

Task 4 通过自动验证。当前实现符合 CHG 边界：Cloud 可展示并管理窗口授权关系；本操作不触碰本机 BitBrowser，不执行 Agent 动作，不改变媒体账号绑定、Cookie 或代理。
