# T-04：Desktop 三角色登录与 M2 本机边界

## 环境

- Cloud `chg/CHG-20261026-102` HEAD `1f54e42`；Desktop 仓无源码改动，工作树干净。
- Desktop 前端由 `scripts/build-desktop-frontend.sh` 从 Cloud 当前提交构建，写入 Desktop `.generated/frontend`（gitignored）。
- `cargo tauri build --no-bundle` 成功，产物 `wt-media-desktop/target/release/wt-media-desktop-shell`（24,509,280 bytes，18:08）。

## Agent Token 服务端门禁（真实请求）

| 场景 | 请求 | 期望 | 实际 | 结果 |
| --- | --- | --- | --- | --- |
| senior01 Desktop 登录 | `POST /auth/login`，`Origin: tauri://localhost` | 200 + Desktop 会话 token | errcode 0，role=senior_operator，token 长度 64 | PASS |
| senior01 换 Agent Token | `POST /local-agent/agent-token` + `X-Session-Token` | 403/11003 `DESKTOP_ROLE_FORBIDDEN` | HTTP 403，11003，`DESKTOP_ROLE_FORBIDDEN` | PASS |
| admin Desktop 登录 | 同上 | 200 + Desktop 会话 token | errcode 0，role=admin | PASS |
| admin 换 Agent Token | 同上 | 403/11003 `DESKTOP_ROLE_FORBIDDEN` | 11003，`DESKTOP_ROLE_FORBIDDEN` | PASS |
| operator01 Web 会话换 Agent Token | `POST /local-agent/agent-token` | 401/11001 `DESKTOP_LOGIN_REQUIRED` | 11001，`DESKTOP_LOGIN_REQUIRED` | PASS |

Desktop 会话冲突与替换（admin 探针）：

| 步骤 | 实际 | 结果 |
| --- | --- | --- |
| 首次 Desktop 登录 | errcode 0，生成 active 会话 `session_1b9573…` | PASS |
| 再次登录且不替换 | errcode 20010，details 带同一 active_session_id | PASS |
| 带 `replace_existing` + 该 session id 登录 | errcode 0，新 token | PASS |
| 用被替换的旧 token 换 Agent Token | HTTP 401 | PASS |
| 验收后登出新会话 | HTTP 200（实测补测） | PASS |

## 页面读回（Desktop 入口 5174，真实浏览器）

| 场景 | 读回 | 结果 |
| --- | --- | --- |
| senior01 直接访问 `/browser-windows` | 落到 `/content-pool`；侧栏无社媒账号/浏览器窗口/代理管理/桌面环境/本地日志 | PASS |
| admin 直接访问 `/accounts` | 落到 `/content-pool`；侧栏同样五项均无 | PASS |
| senior01 `/personal-info` | 无比特浏览器绑定卡、无「Agent 状态」本机区块 | PASS |
| operator01 `/content-pool`（阳性对照） | 侧栏五项全部存在，停留 `/content-pool` | PASS |

阳性对照说明：第一版读 `.app-aside` 的 `innerText` 时，operator01 只读到「桌面环境」，其余三项因 TDesign 折叠子菜单不可见而被误判为缺失。改为读 `textContent` 后同一断言对 operator01 变为全绿、对 senior/admin 仍全为假，证明这组「菜单缺失」断言本来能失败，不是空转。

## 产物闭合

| 证据 | 读数 |
| --- | --- |
| `frontend-build.json` | `source_commit=1f54e42`，`source_dirty=false`，files=86，digest=`4d867c97137722fd794ba4dd38aec0cece022377031a76d3460ef428c783ff9c` |
| 当前构建资产 | `assets/LoginPage-CIHsk3VA.js`、`assets/index.desktop-npf2hw6w.js` 均在 manifest 中 |
| Desktop 二进制字符串 | `index.desktop-npf2hw6w.js` 命中 1 次、`LoginPage-CIHsk3VA.js` 命中 1 次 → 新前端资产表已嵌入 |
| 旧文案 | 「管理员和高级运营不能登录 Desktop」0 命中；新文案「当前角色不能登录 Desktop」在 `LoginPage-CIHsk3VA.js` 命中 1 次 |

Tauri 资产在二进制中压缩存放，业务字符串不能直接 grep；这里用当前构建的资产文件名（内容哈希命名）作为锚，闭合「二进制使用的是这一版前端」。

## 边界与未覆盖项

- Rust 本机命令没有新增角色判断；本 CHG 的边界是产品界面隔离 + Cloud 只在 `operator` 的 Desktop 会话上签发 Agent Token。高级运营／管理员即使拿到 Desktop 会话，也无法取得本机执行凭证。这一点按计划如实记录，未扩 Desktop Rust 范围。
- `operator01` 换 Agent Token 的正向链路没有在现场重跑：开发库里 operator01 只有一条真实 Desktop 会话（属于用户本机），登录会触发 20010 替换并把用户踢下线。该路径由 `TestIssueAgentTokenBindsTheTokenToTheDesktopSession` 覆盖（测试中的 Desktop 会话显式带 `RoleOperator`），现场只验证了 Web 会话被拒。
- Tauri 安装包 GUI 走查不在本次机器验收内，留给用户。
