# CHG-20261026-104 Checkpoint

日期：2026-10-27 02:30（第二次验收修订 T-09～T-12 完成，待夹具 331 与用户复走查）

## 已完成

- Cloud 原实现与合同：团队可见性、三列使用事实、服务端筛选、个人下载门槛、`compose_task_not_retryable` 登记；提交 `d79aad6`、`0d66a97`、`4483280`。
- Cloud Web 共用页面：11 列素材库、三列状态、管理员团队筛选、列表/详情移除下载入口。
- T-08 负责人筛选修订：
  - 任务／成片页负责人下拉只列 `/compose-operators` 返回的团队成员（含本人），去掉“我的／团队全部”伪选项与默认 `mine`，不再发送 `operator_scope`。
  - 高级运营空 `operator_scope` 默认本团队全部；任务／成片列表、详情、取消与重试不再按本人负责游戏收窄；普通运营与管理员范围不变。
  - 同步 PRD 第五章、产品主文档、M4 里程碑；记录见 `change.md`、`plan.md`。
- 第二次验收修订：
  - T-09 空负责人守卫：新增 `web/src/modules/compose/operatorFilter.js`；任务页与成片页改用 `operatorIdFromOption` / `missingOperatorOption`，清空/非法值按“全部”处理。
  - T-10 素材库：游戏选项改为启用游戏全量，默认“负责 ∩ 启用”；普通运营不渲染使用情况列/筛选/详情段；高级运营/管理员一行可点摘要 + 弹窗，无数据 `—`、无负责人 `成片 N`，移除占位文案。
  - T-11 成片游戏筛选与列：`game_id` 服务端只收窄、普通运营越界 403；页面筛选、重置、参数、游戏列；OpenAPI 与 contract-map bump 到 `2026.10.27.1`。
  - T-12 高级运营核对：允许管理员或同团队高级运营；普通运营 403、跨团队高级运营 404；文案“人工核对/核对人”；成功任务不渲染残留失败块。
  - 文档：PRD 第五章、工程规格、M5-C6 追加、ADR-0023 2026-10-27 决议、M4/M5 里程碑增量。
- 证据：`evidence/T-06-*`、`T-07-page-readback.md`、`T-08-operator-filter.md`、`T-09-operator-filter-guard.md`、`T-10-material-library-usage.md`、`T-11-output-game-filter.md`、`T-12-senior-uncertain-review.md`。
- 自动门禁：Cloud `go test ./...` 72 包 ok、0 FAIL（11 个包无测试文件）；Vitest（`web/` 下）80 文件 / 736 用例通过；Workspace `verify_m0_config.py` 通过。
- PR：Cloud #11、Workspace #13 已创建；T-08 代码提交 `e741a12`、`fa41428` 已推送，Cloud `verify` 通过（2m47s）；Workspace 文档提交 `eede4db`、`3244079` 已推送，`Workspace checks` 通过（10s）。

## 当前工作

记录仍为 `VERIFYING`；T-09～T-12 代码、合同、测试和文档已完成，待提交推送、创建夹具 331、用户按修订清单复走查。

## 阻塞

1. **高级运营/管理员真实 HTTP 读数未执行**：本机检出没有这两个账号的口令，且未修改账号口令/状态、未以他人会话代登录。角色分支由 production service 的角色用例与真实团队数据覆盖，边界写在 `T-06-role-scope.md` 与 `T-12-senior-uncertain-review.md` 的“覆盖边界”。
2. **用户复走查**：A1～A8/A6a、B1～B5、C1～C5；重点为清空负责人不报错、成片游戏筛选/列、使用情况可见性、夹具 331 高级运营核对。
3. **合并批准**：走查通过后合并 Cloud #11 与 Workspace #13。

## 329 历史与夹具 331

2026-10-27 01:42:26 管理员已核对任务 329 的 review 11；01:42:28–01:42:36 第 2 次执行成功，生成成片 74（团队 1 / `other` / 负责人 `operator01` / 素材 17 / 策略 47 / `pending_publish`）。329 现为 `success`，不能再用它走查高级运营核对；不回退、不改写 329、成片 74 或 review 11。

走查前在本地开发库建同形态夹具 331（SQL，仅本地；字段见 `evidence/T-12-senior-uncertain-review.md`），插入 `status=failed`、`error_code=execution_uncertain`、`attempt_count=1` 的任务及第 1 次 failed attempt；走查后随夹具清理删除。

## 走查环境数据变更（2026-10-27 00:56～00:57）

审计日志 `audit_deaaafed81f202c3bd1e5b02`、`audit_e3f290abfd2f5e06fb60ff2b`、`audit_fb60ae6d9957c55b5b214340` 记录：管理员把 `senior01` 的负责游戏从 `hy,other,sjz` 改为 `hy,sjz`，随后停用 `other` 游戏。未回退该数据变更；验收清单已按当前事实调整（`other` 任务 329/330 仍在团队 1，任务/成片列表按团队返回，不按游戏启停过滤；素材库清空游戏筛选后仍列出 `other` 素材）。

## 下一步

1. 提交并推送 Cloud T-09～T-12 代码、Workspace 文档与证据；确认两仓 PR CI。
2. 停 compose worker/scheduler 与无头 Chrome；保留 Cloud API（127.0.0.1:8188）、Vite 5173、MySQL。
3. 在本地开发库创建夹具 331，记录守卫查询结果；向用户交付修订后验收清单。
4. 用户回报后把结果写入 `evidence/T-09`～`T-12`；不符项先修复并重走对应步骤。
5. 走查 1–7 通过后执行 T-13 清理并写 `evidence/T-13-data-cleanup.md`；复核计数、审计多不少、对象键未处理。
6. `change.md` 置 `DONE`，移入 `delivery/completed/`，LEDGER 删行；更新里程碑 §3 与 `MASTER_IMPLEMENTATION_PLAN.md` §3；运行 `wt chg verify CHG-20261026-104`；合并 Cloud #11 与 Workspace #13。
7. 清理本 CHG 自建夹具（任务 328/329/330/331、成片 72/73/74、策略 46/47/48、`material_usages` 92/93/94、`/tmp/chg104-*`）；保留审计日志与用户 9/10 的 `disabled`；对象存储对象不删；停本地服务。

## 待清理夹具（收尾时执行）

- 策略 46、47、48；任务 328、329、330、331；成片 72、73、74；`material_usages` 92、93、94；`/tmp/chg104-*`。
- 保留审计日志，不删除；临时用户 9/10 保持 `disabled`；对象存储对象不删。
- 运行中的本地服务：Cloud API、Vite 5173、MySQL；无头 Chrome 与 compose worker/scheduler 在走查前停止。

## 最近验证

```text
Cloud go test ./...            ok=72 fail=0 no_test_files=11
Vitest (web/)                  80 files / 736 tests passed
verify_m0_config.py            Workspace config verification ok
Cloud PR #11 CI                pass 2m47s（T-08 提交 e741a12、fa41428）
Workspace PR #13 CI            pass 12s（8c67059；待本次文档/证据 push 后重跑）
```
