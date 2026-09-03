# 2026-09-03 当前环境与回归证据

CHG：CHG-20260805-032（M2-B 社媒账号收口）

范围：从当前源代码重建 M2-B 本地环境、迁移 024 核验及相关回归

状态：PASS（真实受限账号检查项 7/8 不在本证据的通过范围内）

## 1. 当前源代码环境重建

执行 `wt-media-workspace/scripts/m2b-local-acceptance.sh all`。首次执行准确失败在 BitBrowser 不可达；启动本机 BitBrowser 后从完整入口重新执行，而非复用半成品进程。

最终完整执行结果：

- Cloud health：PASS
- Local Agent health/dependencies：PASS，BitBrowser 状态 `normal`
- BitBrowser：通过 Agent 真实连接，PASS
- Desktop 前端资产：从当前源代码重建且 freshness 检查 PASS
- Desktop DMG：Tauri 重建、挂载与 freshness 检查 PASS
- Cloud 登录冒烟：管理员替换既有会话后登录 PASS
- 迁移：`0 applied, 25 total`，当前固定本地数据库已包含全部 25 个迁移

构建过程只有 Vite 大 chunk 提示和 Rust 未使用代码警告，无构建或验收失败。

## 2. 迁移 024 数据库核验

固定本地 MySQL 数据库中：

- `schema_migrations` 已记录 `20260814_024_media_account_tags_unique_account_scope.sql`
- `SHOW INDEX FROM media_account_tags` 确认唯一键 `uq_media_account_tags_owner_account_name` 顺序为 `user_id, media_account_id, tag_name`

该结果证明同一用户可以在不同账号复用同名标签，同时同一账号内仍保持标签名唯一。

## 3. 相关自动化回归

| 仓库 | 命令/范围 | 结果 |
|---|---|---|
| Cloud | `go test ./internal/modules/mediaaccount/... ./internal/modules/migration/...` | PASS |
| Cloud Web | `npm run test -- --run` | PASS，10 files / 38 tests（环境重建时）；随后增加 Decision 0010 两态回归，目标文件 9 tests PASS |
| Agent | `.venv/bin/python -m unittest tests.test_local_account_check tests.test_profile_guard tests.test_proxy_check` | PASS，13 tests |
| Desktop | `cargo test` | PASS，10 tests |
| Workspace | `git diff --check` | PASS |

Agent 虚拟环境未安装 pytest，因此未用缺失依赖掩盖结果，改以仓库现有 `unittest` 入口执行同一组目标测试。

## 4. 尚未被本证据关闭的事项

- 检查项 7（验证码/安全验证）和 8（账号限制）仍只有 `na` 骨架，缺少真实受限账号样本验收。
- 检查项 3/4 依赖 M2-C 的代理闭环。
- 账号与游戏的基数在 Milestone（多游戏）和最终 PRD（首版单游戏）间存在冲突，必须先形成决策记录再修改数据模型。

## 5. Decision 0010 两态残留修复

审计发现 `AccountsPage.vue` 的 `canCheckAccount` 仍允许历史 `draft` 状态执行检查，与已经生效的 `enabled`/`disabled` 两态决策冲突。先增加失败回归断言，确认旧分支导致 1 test failed；再删除 `draft` 分支，仅允许 `enabled`，目标文件 9 tests PASS。

## 6. 独立提交

- Cloud：`56fc86e fix(m2-b): close account ledger regressions`
- Desktop：`95db0e8 build(m2-b): refresh desktop frontend assets`
