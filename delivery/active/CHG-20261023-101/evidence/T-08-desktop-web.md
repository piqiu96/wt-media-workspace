# T-08 Desktop / Web 证据

日期：2026-10-23
CHG：CHG-20261023-101
仓库与提交：

| 仓库 | 分支 | 提交 |
| --- | --- | --- |
| `wt-media-cloud` | `chg/CHG-20261023-101` | `9e32a4a feat(profilebinding): expose the bound BitBrowser account as a masked view`、`b3e224e feat(web): run Desktop on session-bound credentials and BitBrowser binding` |
| `wt-media-desktop` | `chg/CHG-20261023-101` | `3de1a94 feat(desktop): drive the local agent from the desktop session, not a device identity` |

## 范围

### Desktop（Rust / Tauri）

- 设备身份退场：删除 `device_identity.rs`、`commands/bind.rs`、`dto/bind.rs`、`local_agent/mod.rs`；`preflight.rs` 不再维护节点凭证、运行时事实同步与本地重复检查（694 行改动，净减为主）。
- 新增 `local_agent_configure_token`：用当前 Desktop 会话向 Cloud 换 Agent Token，并写入 sidecar 内存（`POST /api/v1/agent-token`）。Token 不落盘、不进 WebView；返回值只有 `{configured, expires_at}`。
- 新增 `local_agent_token_facts`：只读问 sidecar「手里有没有凭证」，不发任何请求；页面用它说「执行凭证」这一行。
- 新增 `local_agent_bit_account_bind`：请 sidecar 实读 BitBrowser 主账号后调 Cloud 绑定，页面只传 `rebind` 意图；失败时把 `GuardRefusal` 原样回流，Web 按 `code` 分支。
- 被替换语义：`AUTH_DESKTOP_REPLACED` 只清用户会话与跳登录，不停止 sidecar、不清其内存 Agent Token（运行中任务仍用上报档收尾）。
- 诊断包对持有的 Agent Token 掩码，不输出明文。

### Web

- 登录：`DESKTOP_LOGIN_CONFLICT`（errcode 20010）弹确认；取消不重发、不写服务端；确认带 `replace_existing=true` + `replace_session_id` 重发；期间会话再变则更新弹窗里的 ID，不静默重试。`?reason=desktop-replaced` 展示「你的账号已在另一台电脑登录」。
- 401 拦截先读 `error.code`：`AUTH_DESKTOP_REPLACED` 才带 reason 跳转，其余仍是通用登录；`ApiError` 暴露 `code` / `recovery_action`。
- 凭证：登录成功 `ensureAgentToken({ force: true })`，应用启动 `ensureAgentToken()`；无刷新定时器。token 事实只用于展示。
- 个人信息页：设备绑定区换成 BitBrowser 绑定卡（掩码账号、绑定/最近验证时间、当前比特浏览器账号、不一致告警、换绑确认弹窗）。无手工 `main_user_id` 输入。
- Profile 页、账号页、下载中心：删除 `deviceBinding` / `runtimeBinding` 客户端与调用点、设备 id 与节点参数、重取（re-take）整套逻辑；账号检查与 Cookie 读取直接使用任务返回的 `taskId`。
- 错误文案：`executionErrors.js` 按 `code` 映射 `BIT_NOT_BOUND` / `BIT_MAIN_USER_MISMATCH` / `BIT_BROWSER_OFFLINE` / `PROFILE_*` / `FILE_PREPARE_FAILED` / `EXECUTION_INTERRUPTED` / `RESULT_UNKNOWN` / `STALE_ATTEMPT` / `AUTH_*`，超时另走 `timeout`。
- Cloud 侧为个人信息页补 `GET /api/v1/local-agent/bit-account`：只回 `bound`、`main_user_id_masked`、`bound_at`、`last_verified_at`；掩码规则 `≤8 → ****`，否则前 4 + `****` + 后 4。

## 测试读数

### Web（`cd wt-media-cloud/web && npx vitest --run`）

- 改写前基线（同一实现迁移后的第一次全量）：`38 failed | 683 passed (721)`，失败全部来自旧设备/重取模型的期望。
- 改写后：`77 files passed`，`710 passed (710)`。
- 分母 721 → 710 是删除的旧模型用例（重取按钮/重取流程/重取后刷新、本机 device_id 穿行、`canRetake` 断言）与就地改写共同的结果；删除发生在被测行为本身被删除之后，不是被跳过的红。

### Desktop（`cd wt-media-desktop && ./scripts/test.sh`）

- `test result: ok. 536 passed; 0 failed; 6 ignored`。
- `release-versions tests: 20 passed, 0 failed`。
- 只对改动文件跑 `rustfmt --check`（仓不是全仓 rustfmt-clean），无输出。

### 实施中修复

- `startDesktopLocalAgent` 补凭证时没有把自己收到的 `tauri` 传下去：显式以 Desktop 方式启动时，凭证检查仍按 `isTauri()` 判成「不在 Desktop」而直接跳过。改为透传 `tauri`。该缺陷由 `localAgentService.test.js` 的「启动后补一次凭证」用例暴露（此前因默认路径不触发而一直绿）。

## 旧事实扫描（Cloud `web/src`）

```bash
git grep --untracked -c -E 'local_device_identity|deviceBinding|runtimeBinding|canRetake|confirmMainIdentityDirect|local_agent_nodes|assigned_device_id|assigned_node_id|device_id' -- web/src
```

- 结果：无匹配（exit 1）。
- 阳性对照：同一命令形态对 `local_agent_token_facts`、`bitAccountBind` 均有命中，证明模式与路径可用。

Desktop `src-tauri` 同样扫描 `local_device_identity|device_identity|register_local_node|RegisterLocalNode|runtime_report|runtime-report|node_credential|current-login`：无匹配。

## 未覆盖项

- 真实第二台 Desktop、真实旧 Desktop 收到 `AUTH_DESKTOP_REPLACED` 后的 sidecar 上报，留 T-10 真实环境回归；本任务为 Rust 单测 + Web 单测。
- 打包 Desktop 的界面逐屏视觉确认本机无法程序化截取，留用户确认。
- Cloud 仓 `internal/modules/production/*` 的未提交格式重排不是本 CHG 的改动，未纳入提交。
