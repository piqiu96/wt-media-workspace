# CHG-20261026-104 Checkpoint

日期：2026-10-27 00:59（T-08 修订完成，待用户走查）

## 已完成

- Cloud 原实现与合同：团队可见性、三列使用事实、服务端筛选、个人下载门槛、`compose_task_not_retryable` 登记；提交 `d79aad6`、`0d66a97`、`4483280`。
- Cloud Web 共用页面：11 列素材库、三列状态、管理员团队筛选、列表/详情移除下载入口。
- T-08 负责人筛选修订：
  - 任务／成片页负责人下拉只列 `/compose-operators` 返回的团队成员（含本人），去掉“我的／团队全部”伪选项与默认 `mine`，不再发送 `operator_scope`。
  - 高级运营空 `operator_scope` 默认本团队全部；任务／成片列表、详情、取消与重试不再按本人负责游戏收窄；普通运营与管理员范围不变。
  - 同步 PRD 第五章、产品主文档、M4 里程碑；记录见 `change.md`、`plan.md`。
- 自动门禁：Cloud `go test ./...` 72 包通过、0 FAIL；Vitest（`web/` 下）79 文件 / 729 用例通过；Workspace 175 用例与全部校验通过。
- 真实读数（修订前）：团队 1 素材 59（hy/sjz/other = 14/19/26）、跨团队 403、加入/移出/恢复、真实任务 328→成片 72、真实下载 2 次、Worker 在关系移出后完成素材 17 源准备、真实任务 330→成片 73 与跨团队同外部作品分别计数。
- 证据：`evidence/T-06-team-scope-and-filters.md`、`T-06-usage-facts.md`、`T-06-download-and-worker-prep.md`、`T-06-role-scope.md`、`T-07-page-readback.md`、`T-08-operator-filter.md`。
- PR：Cloud #11、Workspace #13 已创建；T-08 提交后需重新推送并等 CI。

## 当前工作

记录仍为 `VERIFYING`；T-08 代码、测试和文档已完成，等待推送 PR 与用户按修订后的清单走查。

## 阻塞

1. **高级运营/管理员真实 HTTP 读数未执行**：本机检出没有这两个账号的口令，且未修改账号口令/状态、未以他人会话代登录。角色分支由 production service 的角色用例与真实团队数据覆盖，边界写在 `T-06-role-scope.md` 与 `T-08-operator-filter.md` 的“未覆盖/覆盖边界”。
2. **用户走查**：负责人下拉含本人与 `operator01`、未选显示团队 1 全部游戏任务、选成员后按 `operator_id` 收窄、任务 312 可重试 / 329 不可重试、成片 72/73 可见。
3. **合并批准**：走查通过后合并 Cloud #11 与 Workspace #13。

## 下一步

1. 提交 T-08 改动，推送 Cloud 分支与 Workspace 记录分支，等 PR CI。
2. 重启 Vite 5173；保留 Cloud API/MySQL；停 compose worker 与无头 Chrome，避免走查期间自动跑任务。
3. 向用户交付修订后的人工验收清单（A5、A8 已按新行为改写）。
4. 用户回报后，把结果写入 `evidence/T-08-operator-filter.md` 与 `T-06-role-scope.md`；不符项先修复并重走对应步骤。
5. 走查通过后合并 Cloud #11；`change.md` 置 `DONE`，移入 `delivery/completed/`，LEDGER 删行；更新里程碑 §3 与 `MASTER_IMPLEMENTATION_PLAN.md` §3；运行 `wt chg verify CHG-20261026-104`；合并 Workspace #13。
6. 清理验收夹具（见下），复核四仓 `main` 干净，再进入 CHG-105。

## 待清理夹具（收尾时执行）

- 策略 46、47、48；任务 328、329、330；成片 72、73；`material_usages` 92、93、94；`/tmp/chg104-*`；`.compose/task-330-*`（已随成功清理）。
- 保留审计日志，不删除；临时用户 9/10 保持 `disabled`。
- 运行中的本地服务：Cloud API、Vite 5173、无头 Chrome 9224、compose worker；收尾时停止。

## 最近验证

```text
Cloud go test ./...            72 packages ok, 0 FAIL（11 个包无测试文件）
Vitest (web/)                  79 files / 729 tests passed
Cloud PR #11 CI                待 T-08 提交后重跑
Workspace PR #13 CI            待记录提交后重跑
```
