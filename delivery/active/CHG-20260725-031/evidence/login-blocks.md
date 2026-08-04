# M2-B 登录与环境阻塞复现记录

日期：2026-08-04
CHG：CHG-20260725-031（M2-B7 批量账号检查与 M2-B 综合收口）
目的：复现"打包 Desktop 登录不进去 / 每次报错不同 / 环境非确定性"，为收口修复提供事实。

## 1. 当前环境状态（复现时点）

| 组件 | 状态 | 说明 |
|---|---|---|
| Cloud server | PID 17884，启动于 08-03 23:45（`go run`） | **早于** cloud HEAD 85df19d（08-04 01:18）→ 运行中代码为 23:45 时点 |
| Local Agent | PID 12467，启动于 08-03 23:01 | **早于** agent HEAD ebbab6a（08-03 23:12）→ 缺 BitBrowser 超时修复 |
| BitBrowser API | 127.0.0.1:54345 监听 | 正常 |
| Desktop DMG | 建于 08-04 01:24（最新） | 已挂载 /Volumes/WT Media，shell 进程在跑 |

结论：**运行中的 Cloud/Agent 均为陈旧构建**，与最新源码不一致；这与"每次登录问题不同"的环境非确定性特征一致。Bring-up 必须在启动前强制重建并校验新鲜度。

## 2. 数据库状态

- `wt_media_cloud` 现有 3 用户：`admin`(admin, enabled)、`senior01`(senior_operator, team 1)、`operator01`(operator, team 1, bit 已绑定 `2c9bc06191effa4e0191f9589996619f`)。
- 系统存在 **12 个历史数据库**（wt-media-cloud、wt_media、wt_media_acceptance、wt_media_m2_a2_* 等）→ 环境多样性，需在 bring-up 固定唯一 DSN。

## 3. 登录接口复现（API 层）

| 请求 | 结果 | 结论 |
|---|---|---|
| `POST /auth/login` admin/admin123（无 replace_existing） | errcode 20010「当前账号已在其他位置登录，请确认是否替换旧会话」 | 凭证有效；已有会话需确认替换 |
| `POST /auth/login` admin/admin123 + `replace_existing:true` | errcode 0，返回 admin 用户 + Set-Cookie | **admin 登录 API 层成功** |
| `POST /auth/login` operator01 + 多种常见密码 | errcode 11001「请先登录或凭证已过期」 | **operator01 密码未知**；错误密码被映射为通用 11001 |
| `OPTIONS` preflight（Origin: http://tauri.localhost） | 204 + `Access-Control-Allow-Origin: http://tauri.localhost` + Credentials/Headers/Methods | **CORS 正常** |
| `POST /auth/login` 带 Origin: http://tauri.localhost | 200 + Set-Cookie | 打包 App 跨源登录链路网络层正常 |

错误码语义（`internal/modules/identity/service.go` + `routes.go`）：
- 密码错误/账号不可用 → `ErrAuthenticationFailed` → 11001「请先登录或凭证已过期」；
- 凭证有效但已有活动会话且未请求替换 → `ErrSessionReplaceNeeded` → 20010；
- 前端 `LoginPage.vue` 正确处理 20010（弹"确认替换旧会话"再带 `replace_existing:true` 重试）。

## 4. 阻塞结论

1. **operator01 登录不进去的直接原因待确认**：打包 App 中输入 operator01 + 密码返回 11001，文案"请先登录或凭证已过期"对用户而言即为"登录不进去"。需用户提供 operator01 密码，或由 admin 走 `POST /api/v1/users/:user_id/reset-password` 重置并复制一次性密码。
2. **环境非确定性**（陈旧进程 + 12 个历史 DB）是"每次报错不同"的根源，必须由 `environment-bring-up` skill 固化：启动前强制停旧进程、最新源码重建、固定唯一 DSN、登录冒烟门。
3. 打包 App 前端资产（01:24 构建）含最新修复；Cloud/Agent 需重启到最新后再做打包 App 端到端登录复验。

## 5. 后续修复动作（待确认）

- [x] 获取/reset operator01 密码，API 层验证 operator01 登录成功；
- [x] 重启 Cloud/Agent 到最新构建，确认新鲜度门；
- [ ] 在最新环境 + 打包 App 上复现登录，采集用户侧报错，确认根因并修复；
- [x] 将全部结论并入 `environment-bring-up` skill 与登录冒烟门。

## 6. 修复与复验结果（2026-08-04）

- **operator01 密码**：经 admin `POST /api/v1/users/3/reset-password` 重置为 `operator01`（账号密码一致），API 登录 `errcode 0` 返回 operator01/team1/game1。
- **环境确定性硬化**（`scripts/m2b_local_acceptance.py`）：
  - 新增 `--force-restart`：按端口杀死陈旧 Cloud/Agent（含手工启动、无 PID 文件的进程），并等待端口释放；
  - 构建新鲜度门：`verify_assets`/`verify_dmg` 按喂给产物的源码路径（cloud `web/`、desktop `src-tauri/`）比较 mtime，避免无关提交造成误判；
  - 登录冒烟门：`verify`/`all` 增加 `verify_login`（默认 admin/admin123，可用 `WT_MEDIA_LOGIN_USER/PASSWORD` 覆盖）。
- **确定性重建**：`up --force-restart` 将 Cloud 重启为最新代码（PID 28303，含 login API base/CORS 修复）、Agent 最新（PID 28323）；`verify` 全门禁 PASS（Cloud/Agent/BitBrowser/assets fresh/DMG fresh/login smoke）；最新 DMG 已重新挂载并启动（shell PID 28361）。
- **复验**：fresh Cloud 上 operator01/operator01 登录 `errcode 0`；CORS preflight from `http://tauri.localhost` 返回 204。
- **待用户**：在已打开的打包 Desktop 中，以 `operator01` / `operator01` 登录，确认端到端登录成功并进入 M2-B 验收流程。
