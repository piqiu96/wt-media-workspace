# Checkpoint — CHG-20260925-063

- 状态：IMPLEMENTING（2026-09-25 激活）。
- 性质：处置三个常年红的校验脚本（僵尸门禁），按判据稳定性分层——跨仓源码字面量与
  已关闭里程碑的候选关键词不再作门禁，契约层判据保留并加固。Level S，仅 `wt-media-workspace` 一仓。
- 来源：本次会话 `/doctor` 诊断的 B-7（僵尸门禁）与 G-1，经用户 2026-09-25 裁定
  「按稳定性分层」+「删掉 CI 断言」后立此 CHG。

## Completed

- 2026-09-25 Start Gate 勘查（只读，无任何写入）：三个脚本实跑读数 exit 1，
  红项 **3 / 5 / 8** 条；16 条逐条追到具体行与具体文件（`change.md` §4）。
  工作区开工时只有 2 个已知脏文件（`CLAUDE.md`、`docs/engineering/specs/agent-workspace-conventions.md`，
  均为上一任务的工作区编辑，非本 CHG 产物，开工前已核实归属）。
- 2026-09-25 两项实测发现（均为本轮新查、非推断）：
  1. **M3 的禁用对象检查今天恒真**——`candidate_block(sections[3])` 返回空串，
     而 `crawl_result` 实际出现在 M3 段正文里；照 M2 补兜底会把它从恒真翻成恒假。
  2. **测试套件里有一处假通过**——`test_rejects_stale_operational_object_in_candidate_chg`
     的变异字符串 `M3-C6 source_content 全局去重、状态和最新原始 JSON` 在 MASTER 中
     **不存在**，`str.replace` 是空操作，该用例从未验证过禁用对象机制。
- 2026-09-25 T-01：建 `delivery/active/CHG-20260925-063/`（`change.md` 十四节、本 `checkpoint.md`、
  `evidence/artifacts/`）。单仓实施，**不建** `status/`。

## Completed

- 2026-09-25 Start Gate 收尾：LEDGER 加表行、快照经 `prepare_ai_workspace.py --change` 再生成
  （`active_milestone=null`，Level S 预期）。`verify_delivery_governance.py` / `verify_agent_entry.py` /
  `verify_skills.py` 三者 exit 0。**形状限制导致一处记录改动**：`verify_product_master_alignment.py`
  要求 active CHG 的 §7 为字面 `None.`（不接受「非阻塞」档位），故原拟的 Q-01 移入 §14 遗留第 1 项。
- 2026-09-25 T-01 完成：`verify_m0_config.py` 由 `exit=1`／3 红 转为 `exit=0`，
  `tests.test_verify_m0_config` **Ran 4 tests / OK**。两次**变异对照**（改坏 contract-map 的
  `cloud_api` revision → 报错；空 `OUTER_ROOT` → 三个运行仓工作流 3/3 报缺）证明未改成恒真、
  亦未使 CI 检查器整体失去判别力。**纠正一处自我错误**：首轮基线用 `PY="…"` 变量拼接，
  zsh 不做词分割致三个产物只含 `exit=127`，已用 shell 函数重跑替换（靠 `exit=` 码与体量交叉核对发现）。
  证据：`evidence/task-01-m0-config.md`。
- 2026-09-25 T-02 完成：`verify_m2_acceptance.py` 由 `exit=1`／5 红 转为 `exit=0`，
  `tests.test_verify_m2_acceptance` **Ran 1 test / OK**。**D-01/D-02 的张力经测量解开**——
  真正的强制点在 Cloud，且行为覆盖已在 Cloud 自己的
  `TestRegisterConsumesTicketOnceAndIssuesHashedCredential`；本仓改断**已应用 migration 的 schema**
  （append-only ⇒ 文本冻结，故满足稳定性分层）。**三条自我纠正**（同源：判据自己写错时输出照样「像量过的」）：
  ①首版变异对照**没有重定向 `m.CLOUD`**，三条变异全报 0 error，是空转；
  ②AC-04 用 `grep -c` 不具判别力（被删字符串出现在我写的删除说明注释里），改 **AST 枚举**
  证明 **9 个被删 needle 中 0 个仍在断言集合内**；③AC-05 首版判据把路径当 needle 找，误报 3 个 MISSING，
  修正后六类契约层目标全部 present。证据：`evidence/task-02-m2-acceptance.md`。

## Current

- T-03 开工：`verify_product_master_alignment.py`。

## Next

- T-03 `verify_product_master_alignment.py` 转绿（状态词对齐 + 候选块断言按状态分层 + 消除两处空转）。
- T-04 修正测试套件的假通过与失效用例。
- T-05 文档同步（README §Verification、conventions §10、`AGENT-INDEX.md` §12）。
- T-06 收尾：验收矩阵、DONE Gate 签字、归档与失效指针扫描。

## Blockers

- None。（Q-01 已标 NON-blocking。）

## Recent verification

- 见 `change.md` §4 与 `evidence/artifacts/`：三个脚本的原始红项输出、逐里程碑状态与候选块实测表、
  三处测试变异字符串的存在性探针。
