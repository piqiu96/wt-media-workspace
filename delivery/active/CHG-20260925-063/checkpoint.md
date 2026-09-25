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

## Current

- T-01 收尾：LEDGER 加表行、快照经 `prepare_ai_workspace.py --change` 再生成。

## Next

- T-01 `verify_m0_config.py` 转绿（两条 revision 对齐 + 删 workspace CI 断言，D-03）。
- T-02 `verify_m2_acceptance.py` 转绿（删 3 处源码字面量断言 + 新增 Cloud 原子单次使用断言，D-01/D-02）。
- T-03 `verify_product_master_alignment.py` 转绿（状态词对齐 + 候选块断言按状态分层 + 消除两处空转）。
- T-04 修正测试套件的假通过与失效用例。
- T-05 文档同步（README §Verification、conventions §10、`AGENT-INDEX.md` §12）。
- T-06 收尾：验收矩阵、DONE Gate 签字、归档与失效指针扫描。

## Blockers

- None。（Q-01 已标 NON-blocking。）

## Recent verification

- 见 `change.md` §4 与 `evidence/artifacts/`：三个脚本的原始红项输出、逐里程碑状态与候选块实测表、
  三处测试变异字符串的存在性探针。
