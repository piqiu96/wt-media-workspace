# M2-B 多游戏真实切换与跨端验收（Task 8 / 计划 Task 6）

- Date: 2026-09-04
- Status: 自动化、真实 MySQL 与跨端门禁 PASS；手工页面业务操作待可访问本地页面的交互环境补验。

## 切换前检查

固定本地 Cloud MySQL 的迁移前只读检查结果：

- 非空旧 `media_accounts.game_id`: 6
- 无效或已停用的旧游戏关联: 0（可安全继续）
- 媒体账号: 6；标签: 5；含 Cookie 账号: 1；含检查项账号: 3；Profile 绑定账号: 2。

## 切换和真实数据库核验

`wt-media-workspace/scripts/m2b-local-acceptance.sh all --force-restart` 已运行迁移；迁移器报告 `20260903_025_media_account_games` 已应用（26 个迁移总数）。随后以只读 SQL 核验：

- `schema_migrations` 已有迁移 `20260903_025_media_account_games`。
- `media_account_games` 有 6 条记录，与非空旧关联数一致；重复关系为 0。
- `media_accounts.game_id` 列数为 0；关系表主键为 `(media_account_id, game_id)`。
- 在事务中尝试重复插入得到 MySQL `ERROR 1062 Duplicate entry '1-game1' for key 'media_account_games.PRIMARY'`；连接结束后重查关系数仍为 6。
- 标签、Cookie、检查项和 Profile 绑定计数分别保持 `5 / 1 / 3 / 2`。

## 当前源码跨端门禁

执行 `m2b-local-acceptance.sh all --force-restart`。强制停止旧 Cloud/Agent 后，从当前源码重启并通过：

- Cloud health、Agent health、经 Agent 的 BitBrowser 检查；
- Desktop 静态资源新鲜度、DMG 新鲜度与 DMG 启动；
- Cloud 登录 smoke（admin）。

最终回归：

- `go test ./internal/modules/mediaaccount/... ./internal/modules/migration/... -count=1` PASS；
- `npm run test -- --run` PASS（10 文件、40 测试）；
- Cloud `git diff --check` PASS。

相关运行时代码提交：Cloud `a7f16d9`、`4797621`、`0af1a91`、`3dc82d9`；Desktop 当前生成资产提交 `849f244`。

## 页面业务操作补验

已尝试在内置浏览器打开固定本地 Cloud URL 进行“创建双游戏 → 替换为单游戏 → 清空 → 任一游戏筛选 → 未绑定游戏不可执行”点验，但客户端返回 `ERR_BLOCKED_BY_CLIENT`，未访问页面、未登录且未修改任何账号数据。该浏览器限制不能通过绕过处理。

这五个行为已有 Cloud 服务/路由、MySQL Store 与 Cloud Web Vitest 覆盖；待在可访问本地 Cloud 的交互环境中对一个明确的可丢弃账号做一次页面补验后，才能把 Task 8 的手工页面项标记为完成。

## 2026-09-04 BitBrowser 重启后复验

用户重启 BitBrowser 后，重新执行 `scripts/m2b-local-acceptance.sh all --force-restart`，退出码为 0：迁移无待应用项（26 total），Cloud/Agent 从当前源码强制重启，BitBrowser via Agent、Desktop assets、DMG、login smoke 全部 PASS。

复验时内置浏览器与已连接 Chrome 访问 `http://127.0.0.1:18080/` 均仍返回 `ERR_BLOCKED_BY_CLIENT`。该结果证明拦截来自 Codex 浏览器客户端对本机 HTTP 地址的策略，而非业务 BitBrowser 或 Cloud/Agent 故障；未绕过该策略，也未产生账号数据变更。

已交付人工验收环境：Cloud `127.0.0.1:18080`、Agent `127.0.0.1:8765` 均处于监听状态；Agent 报告 `bitbrowser_status=normal`；DMG 挂载在 `/Volumes/WT Media`；进程 `/Volumes/WT Media/WT Media.app/Contents/MacOS/wt-media-desktop-shell` 正在运行。待用户在已打开的 WT Media 应用中完成页面操作验收并反馈结果。

## 2026-09-04 人工验收入口与游戏数据诊断

用户点验发现游戏下拉仅有“默认游戏”，并反馈访问 `http://127.0.0.1:18080` 无法登录管理员后台。只读核验与复现结果：

- `operation_games` 只有一条启用记录：`game1 / 默认游戏`；`user_game_scopes` 也只有 `game1`，不存在未进入游戏目录的历史游戏 ID。6 条 `media_account_games` 关系全部指向该游戏。因此页面只显示一个选项与当前数据库一致，不是多选控件丢数据；但当前数据不足以执行“双游戏”手工验收。
- `18080` 是 Cloud API 端口，不承载 Cloud Web，直接 `GET /` 返回 404；此前把它作为可登录后台地址交付属于环境入口描述错误。
- 已启动 Cloud Web Vite 服务 `http://127.0.0.1:5173/`，其 `/api` 代理指向 `18080`；首页和代理健康接口均验证通过，并已在系统浏览器打开。
- 经 `5173` 代理复现管理员登录返回 HTTP 409 / `errcode=20010`：登录 smoke 已占用 admin 会话。前端已提供“替换旧会话并登录”分支；用户在页面选择替换即可，未在诊断中代替用户提交该操作。
