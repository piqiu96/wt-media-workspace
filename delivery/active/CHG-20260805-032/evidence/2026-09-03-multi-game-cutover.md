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
