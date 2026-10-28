# CHG099 · 当前接续点

## 状态

- CHG099 状态以 [change.md](change.md) 为准：`IMPLEMENTING`。
- 范围已扩展为社媒账号、浏览器窗口、代理三个功能块。
- 当前正式依赖：[CHG-20261029-107](../../planned/CHG-20261029-107/change.md)。CHG107 合入前，不继续修改社媒账号类目字段和依赖该字段的页面。

## 已完成

- 已核对 Cloud 实际 MySQL 结构、行数和现有接口边界，报告写入 [plan.md](plan.md)。
- 已确定 Cloud / Desktop / Local Agent 边界：Cloud 不直接执行运营电脑本机代理写入。
- 已验证 Cloud 迁移与代码当前状态；既有实现只作为候选，不视为本轮完成。

## 下一步

1. 完成 CHG107：`operation_games -> categories`、`game_id -> category_id`；社媒账号允许零类目，内容/策略新增必选，不自动创建 `other`。
2. 回到 CHG099，先做 Cloud 数据/接口收敛，再做 Desktop/Agent 桥和三块页面。
3. 同步删除旧 Cookie 异步任务入口、Cloud Agent 通用任务接口和 `tasks` 表。

## 阻塞与约束

- 真实比特、目标网络、跨端组合和人工视觉验收仍未完成。
- CHG099 的代理临时额度预留、统一 `enabled`、`bit_`/`platform_`/`last_check_` 命名是当前基线。异常结果按失败清除预留并允许直接重试。
- 不执行新的存量代理清理迁移；不把 `profile_sync_candidates`、通用任务历史或敏感许可扩进本域。
- Cookie 改为同步读取；不保留异步任务双路径。
- 保留现有未跟踪社媒分析报告，不纳入提交。

## 最近验证

- 实际表行数：`media_accounts=7`、`browser_profiles=40`、`proxy_configs=0`、`profile_sync_scans=70`、`profile_sync_candidates=2711`。
- 实际类目：`operation_games=4`，并已确认 7 个 `game_id` 依赖列及 `other` 历史引用。
- 本轮为设计与文档收敛，不代表代码或真实业务验收通过。
