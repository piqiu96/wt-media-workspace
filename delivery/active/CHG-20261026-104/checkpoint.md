# CHG-20261026-104 Checkpoint

日期：2026-10-26 23:40（本地验收结束时）

## 已完成

- Cloud 实现与合同：团队可见性、三列使用事实、服务端筛选、个人下载门槛、`compose_task_not_retryable` 登记；提交 `d79aad6`、`0d66a97`、`4483280`。
- Cloud Web 共用页面：11 列素材库、三列状态、管理员团队筛选、列表/详情移除下载入口。
- 自动门禁：Cloud `go test ./...` 72 包通过；Vitest 79 文件/729 用例通过；Workspace 全量门禁通过。
- 真实读数：团队 1 素材 59（hy/sjz/other = 14/19/26）、跨团队 403、加入/移出/恢复、真实任务 328→成片 72、真实下载 2 次、Worker 在关系移出后完成素材 17 源准备、真实任务 330→成片 73 与跨团队同外部作品分别计数。
- 证据：`evidence/T-06-team-scope-and-filters.md`、`T-06-usage-facts.md`、`T-06-download-and-worker-prep.md`、`T-06-role-scope.md`、`T-07-page-readback.md`。
- PR：Cloud #11（CI pass）、Workspace #13（CI pass）。

## 当前工作

记录已置 `VERIFYING`；两个 PR 等待用户批准合并。

## 阻塞

1. **合并批准**：合并 Cloud #11、Workspace #13 需要用户明确同意。
2. **高级运营/管理员真实 HTTP 读数未执行**：本机检出没有这两个账号的口令，且未修改账号口令/状态、未以他人会话代登录。角色分支由 production service 的角色用例与真实团队数据覆盖，边界写在 `T-06-role-scope.md` 的“未覆盖”。若用户提供 mode-600 临时口令文件，可补三条真实 HTTP 读数。

## 下一步

1. 获准后合并 Cloud #11，更新本地 `main` 到 merge commit。
2. `change.md` 置 DONE，移入 `delivery/completed/`，LEDGER 删行；合并 Workspace #13。
3. 更新里程碑 §3 与 MASTER §3 的进度。
4. 清理验收夹具（见下），再进入 CHG-105。

## 待清理夹具（收尾时执行）

- 策略 46、47、48；任务 328、329、330；成片 72、73；`material_usages` 92、93、94；`/tmp/chg104-*`；`.compose/task-330-*`（已随成功清理）。
- 保留审计日志，不删除；临时用户 9/10 保持 `disabled`。
- 运行中的本地服务：Cloud API、Vite 5173、无头 Chrome 9224、compose worker；收尾时停止。

## 最近验证

```text
Cloud go test ./...           72 ok, 0 FAIL
Vitest (web/)                 79 files / 729 tests passed
Workspace repo gates          ok（含 M0 配置校验与 docs governance）
Cloud PR #11 CI               pass (2m58s)
Workspace PR #13 CI           pass (12s)
```
