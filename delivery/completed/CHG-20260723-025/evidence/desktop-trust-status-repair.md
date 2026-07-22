# Desktop可信状态修复 Evidence

> 时间：2026-07-23 05:14 CST  
> 范围：CHG-20260723-025 验收修复项

## 1. 触发问题

人工验收时，Desktop「浏览器窗口」页提示：

```text
当前Desktop尚未绑定可信本机节点，请先到环境状态页重新检测
```

但「Agent 状态」页显示：

```text
Cloud登录：operator01
BitBrowser：可用
主账号ID：已读取
可执行结论：本机环境可信
```

实际问题是：状态页只判断了 Cloud 登录、Local Agent、BitBrowser 和主账号 ID，没有把 `node_id` / Cloud 可信本机节点纳入“可执行结论”；同时页面没有重新检测或绑定入口。

## 2. 修复内容

### Cloud

- 新增 `POST /api/v1/bit-browser/main-identity`：
  - 只确认当前用户的 `bit_main_user_id`；
  - 不创建 Profile scan；
  - 不应用 Profile Diff；
  - 不写入正式 `browser_profiles` 镜像。
- Runtime report 允许在 M2-A/M2-B 前置阶段只上报 `main_user_id`，不强制要求 Cloud 已经存在正式 Profile 镜像。
- 同步更新 `contracts/cloud-api/v1/browser-profiles.openapi.yaml`。

### Desktop Rust

- 新增 `local_agent_bind_session` Tauri command：
  - Vue 只传入 Cloud 一次性绑定票据；
  - Rust 注册 Cloud 本机节点；
  - Rust 将 Cloud `node_id` 写入 Local Agent；
  - Rust 上报当前运行状态；
  - `node_credential` 只保留在 Rust 内存状态，不返回给 Vue。

### Desktop Web

- Agent 状态页新增：
  - 「重新检测」；
  - 「重新检测并绑定」。
- 状态页将“本地组件可用”和“本机节点可信”分开表达：
  - 未绑定 `node_id` 时显示“本机节点未绑定”；
  - 不再显示误导性的“本机环境可信”。
- 绑定流程：

```text
Desktop读取BitBrowser主账号
→ Cloud确认main_user_id
→ Cloud签发一次性绑定票据
→ Rust注册本机节点
→ Rust写入Local Agent node_id
→ Rust上报运行状态
→ 页面刷新可信状态
```

## 3. 验证命令

```text
env GOCACHE=/Users/aqiuye/Develop/workspace/wt-media/wt-media-cloud/.cache/go-build go test ./internal/modules/profilebinding ./internal/modules/runtimebinding
```

结果：PASS

```text
npm test -- profileBindings localAgentService
```

结果：PASS，4 tests passed

```text
npm run build:desktop
```

结果：PASS

```text
cargo check
```

结果：PASS，有既有 unused/dead_code warnings，不阻断。

## 4. 当前验收口径

修复后，人工验收应看到：

- Agent / BitBrowser 可用但未绑定时：
  - 显示“本机节点未绑定”；
  - 显示可信节点为“尚未绑定”；
  - 提供“重新检测”和“重新检测并绑定”入口。
- 点击“重新检测并绑定”成功后：
  - 可信节点显示 Cloud 分配的 `node_id`；
  - 可执行结论显示“本机节点可信”；
  - 浏览器窗口扫描不再因缺少 `node_id` 被前端阻断。

## 5. 未包含内容

- 不应用 Profile Diff；
- 不接受本地变化；
- 不恢复 Cloud 配置；
- 不创建、编辑、打开或关闭 BitBrowser 窗口；
- 不绑定媒体账号。

## 6. 追加登录验收修复

人工验收发现 Desktop 登录页在旧会话替换场景下表现不稳定：

```text
第一次点击无明显反馈
第二次显示“已取消登录，旧会话保持有效。”
```

原因是登录页使用浏览器原生 `window.confirm` 承载旧会话替换确认；在 Tauri Desktop 中该确认框表现不稳定，可能导致用户没有看到确认动作但前端按“取消”处理。

修复：

- 移除登录页 `window.confirm` 旧会话确认；
- 旧会话冲突时在页面内展示明确提示；
- 页面显示“替换旧会话并登录”和“取消”两个按钮；
- 用户点击“替换旧会话并登录”后才带 `replace_existing=true` 重新登录。

验证：

```text
npm test -- session
npm run build:desktop
```

结果：PASS。

## 7. 二次登录按钮事件修复

人工验收继续发现：页面已经显示“替换旧会话并登录”，但点击确认后没有反应。

原因是登录页仍使用 `t-form` 的 submit 事件作为登录入口，同时替换按钮位于表单内部；按钮点击可能被表单 submit 行为接管，导致 `replaceExisting=true` 参数没有稳定进入登录请求。

修复：

- 登录表单改为只阻止默认 submit，不再通过 submit 触发登录；
- “登录”“替换旧会话并登录”“取消”全部改为显式 click 事件；
- “替换旧会话并登录”点击时固定调用 `login({ replaceExisting: true })`；
- 登录方法只在明确收到 `replaceExisting === true` 时才发送 `replace_existing=true`。

验证：

```text
npm test -- session desktopRoleGuard
npm run build:desktop
```

结果：PASS。

## 8. 三次登录按钮原生化修复

人工验收继续发现：页面显示“替换旧会话并登录”，但点击仍无明显反应。

进一步处理：

- 登录页关键操作不再使用 `t-button` 承载；
- “登录”“替换旧会话并登录”“取消”改为原生 `button type="button"`；
- 表单 submit 仅作为 Enter 键兜底，并显式路由到当前状态对应动作；
- 点击登录或替换登录时，页面会立即显示“正在登录…”或“正在替换旧会话…”，用于确认按钮事件已触发。

验证：

```text
npm test -- session desktopRoleGuard
npm run build:desktop
```

结果：PASS。

## 9. 后端 Cookie Secure 配置确认

人工继续验收时发现：点击“替换旧会话并登录”后页面仍停留在登录页。

通过 Cloud 日志确认：

```text
POST /api/v1/auth/login 200
GET /api/v1/auth/me 401
```

这说明登录接口本身成功，但后续会话读取失败。

进一步检查本地 Desktop 同源请求：

```text
POST http://127.0.0.1:5174/api/v1/auth/login
```

旧响应头包含：

```text
Set-Cookie: wt_media_session=...; HttpOnly; secure; SameSite=Lax
```

当前 Desktop dev 页面是 `http://127.0.0.1:5174`，不是 HTTPS；`secure` cookie 在该环境下不会被 WebView 稳定保存，导致登录成功后 `/auth/me` 仍为未登录。

处理：

- 重启本地 Cloud API；
- 显式设置 `WT_MEDIA_SESSION_COOKIE_SECURE=false`；
- 保持生产默认 secure cookie 不变。

验证：

```text
curl -i -c /tmp/wtmedia_login_cookie2.txt \
  -X POST http://127.0.0.1:5174/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  --data '{"username":"operator01","password":"operator123","replace_existing":true}'
```

结果：PASS，新的 `Set-Cookie` 不再包含 `secure`。

```text
curl -b /tmp/wtmedia_login_cookie2.txt \
  http://127.0.0.1:5174/api/v1/auth/me
```

结果：PASS，返回 `operator01` 当前用户信息。

数据库确认：

```text
active_sessions = 1
```

## 10. Agent状态页可信口径修复

人工验收继续发现：浏览器窗口页提示“当前Desktop、Local Agent或BitBrowser身份不可信”，但 Agent 状态页显示“本机节点可信”。

排查结果：

- Local Agent 实时状态可读取到 `node_id`、`bitbrowser_status=normal` 和当前 BitBrowser `main_user_id`；
- Cloud 用户 `operator01` 已绑定相同的 `bit_main_user_id`；
- 但 Cloud `local_agent_nodes` 中该节点的 `reported_main_user_id` 与 `bitbrowser_status` 为空；
- 浏览器窗口扫描走 Cloud `CheckLocalTrust`，它要求 Cloud 节点运行态已上报，因此拦截是合理的；
- Agent 状态页只凭本地 `node_id` 显示“本机节点可信”，口径错误。

修复：

- Agent 状态页不再把本地 `node_id` 等同于 Cloud 可信；
- 文案从“本机节点可信”调整为“本机节点已绑定”；
- 有本地 `node_id` 且组件就绪时，也继续展示“重新检测并绑定”按钮，用于重新向 Cloud 注册/上报运行状态；
- 提示文案明确：如业务页仍提示不可信，点击“重新检测并绑定”刷新 Cloud 可信状态。

验证：

```text
npm test -- localAgentStatus localAgentService profileBindings
npm run build:desktop
```

结果：PASS。

## 11. 重新检测并绑定 runtime-report 修复

人工验收继续发现：Agent 状态页显示本机节点已绑定，但点击“重新检测并绑定”后提示：

```text
绑定可信本机节点失败
```

Cloud 日志显示：

```text
POST /api/v1/local-agent/nodes/register 201
POST /api/v1/local-agent/nodes/{node_id}/runtime-report 400
```

数据库确认最新 `local_agent_nodes` 已创建，但运行态字段为空：

```text
reported_main_user_id = NULL
bitbrowser_status = NULL
```

原因：

- 注册本机节点成功；
- 但 Desktop Rust 上报 runtime-report 时没有使用 Local Agent 实际返回的运行环境字段；
- 原上报将 `ffmpeg.status` 写为 `normal` 但没有携带 `ffmpeg.version`，不满足 Cloud `validDependency` 校验；
- 同时本机可信绑定不应携带完整 `bit_profile_ids`，否则会把 M2-B Profile Diff/归属验证提前塞进主账号可信绑定，形成业务循环依赖。

修复：

- Desktop Rust `local_agent_bind_session` 读取 Local Agent `/api/v1/status` 的真实运行环境字段；
- runtime-report 上报 `python_version`、`ffmpeg`、`workdir_status`、`disk`、`bitbrowser_status` 和 `main_user_id`；
- 本机可信绑定只证明当前 Desktop / Local Agent / BitBrowser 主账号身份可信，不上报 `bit_profile_ids`；
- `bit_profile_ids` 仍保留在 Local Agent status 中，供 M2-B 浏览器窗口扫描与 Diff 独立使用。

验证：

```text
curl http://127.0.0.1:8765/api/v1/status
cargo check
```

结果：

- Local Agent status 返回 `python_version=3.14.6`、`ffmpeg.status=normal`、`ffmpeg.version=8.1.2`、`bitbrowser_status=normal`、`main_user_id=2c9bc06191effa4e0191f9589996619f`；
- `cargo check` PASS；
- 已重新启动 Desktop 壳，等待用户再次点击“重新检测并绑定”完成人工验证。

## 12. 最终可信绑定语义与文案收口

人工确认后，最终产品口径修订为：

- 「重新检测本机环境」只做本机状态读取：检查 Desktop / Local Agent / BitBrowser 是否可用，读取当前比特浏览器账号；不重启 Agent，不写 Cloud，不扫描窗口，不生成 Diff。
- 「绑定当前比特浏览器账号」只用于首次绑定：系统用户尚未绑定比特浏览器账号时，允许把当前读到的比特浏览器账号写为该用户的绑定账号。
- 「刷新本机状态」用于已绑定账号：仅当当前比特浏览器账号与系统已绑定账号一致时，刷新本机运行状态和本地执行凭据。
- 如果当前比特浏览器账号与系统已绑定账号不一致，必须阻断，不能静默从账号 A 重新绑定到账号 B，避免 Cloud 已保存窗口与本地扫描结果整体错位。
- 若系统故障导致绑定关系错误，低成本修复路径是管理员在 Cloud 用户管理中解除该用户的比特浏览器绑定；解除不会删除浏览器窗口、媒体账号或历史记录。之后运营在 Desktop 重新绑定正确账号。
- Cloud Web 对所有角色都只展示 Cloud 已保存数据，不展示或执行依赖本机 Agent / BitBrowser 的实时能力；Desktop 才展示本机环境、扫描窗口、配置代理和账号检查等操作。

用户可见文案同步收口：

- 不再使用「M2」「敏感操作」「可信节点」「可执行结论」「当前Desktop身份不可信」等内部工程表达。
- 成功状态显示为：当前电脑已完成可信绑定，可以扫描窗口、配置代理和检查账号。
- 阻断状态显示为：当前电脑尚未完成本地环境确认，暂时不能扫描或操作浏览器窗口。
- 比特浏览器账号不一致时显示：当前比特浏览器登录账号与系统绑定账号不一致，需要切换回正确账号；如系统绑定错误，请联系管理员解除绑定后重新绑定。

验证：

```text
env GOCACHE=/Users/aqiuye/Develop/workspace/wt-media/wt-media-cloud/.cache/go-build go test ./internal/modules/profilebinding ./internal/modules/runtimebinding
```

结果：PASS。

```text
npm test -- localAgentStatus usersApi UsersPage profileBindings localAgentService session desktopRoleGuard
```

结果：PASS，7 test files / 18 tests passed。

```text
npm run build:desktop
npm run build:cloud
```

结果：PASS。

关键词检查：

```text
rg -n "敏感操作|可信节点|可执行结论|当前Desktop|身份不可信|绑定可信本机节点|主账号ID|M2 本地|可以执行 M2|本机环境可信" wt-media-cloud/web/src wt-media-cloud/internal/modules/profilebinding wt-media-cloud/web/dist-cloud wt-media-cloud/web/dist-desktop -S
```

结果：无匹配。

## 13. Product / Milestone 同步检查

已将最终结论同步回正式事实源，避免后续 CHG 只继承临时实现口径：

- `docs/product/prd/详细文档/第三章_用户与账号管理.md`
  - 首次绑定改为只读取并确认当前 BitBrowser 主账号 `main_user_id`；
  - 明确不在 M2-A 读取完整 Profile 列表、不校验 `profile_user_id`、不创建或更新正式 `browser_profile`；
  - 明确已绑定用户刷新本机状态时必须校验当前 BitBrowser 主账号与已绑定账号一致；
  - 明确不允许静默从旧比特账号改绑到当前比特账号；
  - 明确管理员解除错误绑定的修复路径，且不删除 Profile、媒体账号、代理关系或历史记录。
- `delivery/milestones/M2-account-runtime.md`
  - M2-A 主账号绑定口径与 PRD 对齐；
  - M2-B Profile 扫描、Diff 和授权同步继续保留在 M2-B；
  - 用户可见和业务描述统一使用“本地浏览器操作”等运营可理解表达。

反向检查：

```text
rg -n "读取全部 Profile|扫描可见Profile|profile_user_id.*完整|新敏感操作|敏感操作|M2敏感|可信节点|可执行结论|可以执行 M2|重新绑定比特浏览器账号" wt-media-workspace/docs/product/prd/详细文档/第三章_用户与账号管理.md wt-media-workspace/delivery/milestones/M2-account-runtime.md -S
```

结果：无匹配。
