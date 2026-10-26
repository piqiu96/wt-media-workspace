# CHG-20261026-104 Checkpoint

日期：2026-10-27 03:10（用户复走查通过、T-13 清理已执行，待门禁/合并/归档）

## 已完成

- Cloud 原实现与合同：团队可见性、三列使用事实、服务端筛选、个人下载门槛、`compose_task_not_retryable` 登记；提交 `d79aad6`、`0d66a97`、`4483280`。
- Cloud Web 共用页面：11 列素材库、三列状态、管理员团队筛选、列表/详情移除下载入口。
- T-08 负责人筛选修订：任务／成片页负责人下拉只列 `/compose-operators` 返回的团队成员（含本人），去掉“我的／团队全部”伪选项与默认 `mine`，不再发送 `operator_scope`；高级运营空 `operator_scope` 默认本团队全部，任务／成片列表、详情、取消与重试不再按本人负责游戏收窄；普通运营与管理员范围不变；同步 PRD 第五章、产品主文档、M4 里程碑。
- T-09 空负责人守卫：新增 `web/src/modules/compose/operatorFilter.js`；任务页与成片页改用 `operatorIdFromOption` / `missingOperatorOption`，清空/非法值按“全部”处理。
- T-10 素材库：游戏选项改为启用游戏全量，默认“负责 ∩ 启用”；普通运营不渲染使用情况列/筛选/详情段；高级运营/管理员一行可点摘要 + 弹窗，无数据 `—`、无负责人 `成片 N`，移除占位文案。
- T-11 成片游戏筛选与列：`game_id` 服务端只收窄、普通运营越界 403；页面筛选、重置、参数、游戏列；OpenAPI 与 contract-map bump 到 `2026.10.27.1`。
- T-12 高级运营核对：允许管理员或同团队高级运营；普通运营 403、跨团队高级运营 404；文案“人工核对/核对人”；成功任务不渲染残留失败块。
- 文档：PRD 第五章、工程规格、M5-C6 追加、ADR-0023 2026-10-27 决议、M4/M5 里程碑增量。
- **用户复走查（2026-10-27）通过**：A1～A8/A6a、B1～B5、C1～C5 全部确认；实际产生 331 高级运营核对（review 12、attempt 262、成片 75）与 312 重试（attempt 264、成片 76）。结果已写入 `evidence/T-09`～`T-12`。
- **T-13 清理已执行**：停 compose worker（pid 68767）；单事务删除无负责人任务 19、成片 17、策略 7、attempts 23、transfer 2、schedule_runs 16；审计 1213 条全部保留（52 条悬挂引用）；17 个对象键 SigV4 Range GET 均 206；删除后复核见 `evidence/T-13-data-cleanup.md`。
- 自动门禁：Cloud `go test ./...` 72 包 ok、0 FAIL（11 个包无测试文件）；Vitest（`web/` 下）80 文件 / 736 用例通过；Workspace `verify_m0_config.py` 通过。
- PR：Cloud #11、Workspace #13 已创建；T-08 代码提交 `e741a12`、`fa41428`，T-09～T-12 代码提交 `86a2c09`（后端/合同）、`5dc5bfa`（Web），Cloud `verify` 通过（2m19s）；Workspace 文档提交 `eede4db`、`3244079`、`6ae4669`、`b4153d0`，`Workspace checks` 通过（13s）。

## 当前工作

记录仍为 `VERIFYING`；代码/合同/文档/走查/清理均完成。剩余：提交推送 T-13 证据与记录更新 → `wt chg verify` → 合并 Cloud #11 → Workspace 置 DONE/归档 → 合并 #13 → 清理剩余夹具。

## 阻塞

1. **高级运营/管理员真实 HTTP 读数未执行**：本机检出没有这两个账号的口令，且未修改账号口令/状态、未以他人会话代登录。角色分支由 production service 的角色用例、真实团队数据与用户复走查覆盖，边界写在 `T-06-role-scope.md` 与 `T-12-senior-uncertain-review.md` 的“覆盖边界”。
2. **合并批准**：走查已确认；还需用户批准合并 Cloud #11 与 Workspace #13（当前未获合并授权）。

## 329 历史与夹具

2026-10-27 01:42:26 管理员已核对任务 329 的 review 11；01:42:28–01:42:36 第 2 次执行成功，生成成片 74。329 现为 `success`，不回退、不改写。331 为走查夹具，由 `senior01` 在 02:40:46 核对（review 12）并执行成功（attempt 262、成片 75）。312 由 `senior01` 在 02:41:20 重试，attempt 264 于 02:42:13 成功，生成成片 76（任务 312/素材 153，不是素材 161）。

## 走查环境数据变更（2026-10-27 00:56～00:57）

审计日志 `audit_deaaafed81f202c3bd1e5b02`、`audit_e3f290abfd2f5e06fb60ff2b`、`audit_fb60ae6d9957c55b5b214340` 记录：管理员把 `senior01` 的负责游戏从 `hy,other,sjz` 改为 `hy,sjz`，随后停用 `other` 游戏。未回退该数据变更；验收清单已按当前事实调整。

## 下一步

1. 提交并推送 T-13 证据与本轮记录更新到 `chg/CHG-20261026-104`；确认 Workspace PR #13 CI。
2. 在 `VERIFYING` 状态下运行 `python3 scripts/wt.py chg verify CHG-20261026-104`；预期仍有已知 `verify_m1_integration.py` 基线失败（`wt_media_agent.cloud_agent_client` 已退役），登记为基线问题，不计入 104 回归。
3. 合并 Cloud PR #11，记录 merge SHA。
4. Workspace：`change.md` 置 `DONE`，`merge_commits` 只登记 Cloud SHA；`git mv` 到 `delivery/completed/CHG-20261026-104/`；`LEDGER.md` 删行；M4-J `IMPLEMENTING → DONE` 并改链接；M4 总体保持 `IN_PROGRESS`；`MASTER_IMPLEMENTATION_PLAN.md` §3 按目录实际数重算（104 归档后 planned 5 / active 1 / completed 78）；跑治理与产品对齐校验；推送 #13。
5. 合并 Workspace PR #13；确认 `origin/main` 含归档提交；删两个分支。
6. 归档后清理剩余夹具：reviews 11/12 → attempts 256/257/258/259/261/262 → 成片 72/73/74/75 的 transfer（若有）→ 成片 72/73/74/75 → 任务 328/329/330/331 → `material_usages` 92/93/94 → 策略 46/47/48；保留审计日志、usage 62、素材 170、用户 9/10 的 `disabled`；对象存储不删；删 `/tmp/chg104-*`；停 Cloud API、Vite、Chrome、worker。
7. 复核 LEDGER 只剩 CHG-098，四仓 `main` 干净。

## 待清理夹具（归档后执行）

- 策略 46、47、48；任务 328、329、330、331；成片 72、73、74、75；reviews 11、12；attempts 256、257、258、259、261、262；`material_usages` 92、93、94；`/tmp/chg104-*`。
- 保留：审计日志、`material_usage` 62（任务 328 在用）、素材 170、用户 9/10 的 `disabled` 状态、对象存储对象。

## 最近验证

```text
Cloud go test ./...            ok=72 fail=0 no_test_files=11
Cloud go build ./...           pass
Vitest (web/)                  80 files / 736 tests passed
Cloud web npm run build        pass（6.86s）
verify_m0_config.py            Workspace config verification ok
Cloud PR #11 CI                pass 2m19s（5dc5bfa；含 86a2c09）
Workspace PR #13 CI            pass 13s（b4153d0；本轮提交后需重跑）
T-13 清理后复核                 unowned 0/0/0；audit 1213；孤儿 0；17 对象 206
```
