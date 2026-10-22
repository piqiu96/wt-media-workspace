# Checkpoint: CHG-20261022-099

- CHG: `CHG-20261022-099`
- Updated: 2026-10-22

Status stays in `change.md`; this file records progress, not a second state copy.

## Completed

- **T-01 现状审计与三条边界**: CHG-098 保留旧 `main` 工作流；依赖必须归档且有合并依据；`parent` 用 Milestone 锚点或 `none`。旧归档缺依据时阻止启动。
- **T-02 CHG 元数据与多 Active**: 新格式最小字段与模板；多个独立 Active CHG 可共存，一个工作树只选一个执行；`wt status/start/resume/verify` 可用。
- **T-03 生成式上下文**: `.ai/CURRENT_CONTEXT.md` 由 `prepare_ai_workspace.py` 生成并忽略；删去第三份 `Status:`，补齐 `CHG Location`/`Affected Repositories`；连续两次 `resume` 生成结果一致。
- **T-04 薄 `wt` CLI**: `scripts/wt.py` 保留唯一入口，`scripts/chg/{__init__,start,resume,verify}.py` 承载三个动词与共享前置条件；legacy CHG 不切分支，`resume` 输出 main 漂移警告，L/M/H 场景策略落地。
- **T-05 脚本按用途分层**: `scripts/lib/`、`scripts/chg/`、`scripts/docs/`、`scripts/dev/`、`scripts/verify/` 归位；删除纯转发 `scripts/m2b-local-acceptance.sh`；`bin/control.sh` 直接调用 `scripts/dev/local_env.py`；逐文件 `scripts/README.md` 与机检索引。
- **T-06 文档治理**: `docs/README.md` 写明分类、权威、生命周期与默认加载；补齐 16 个必需索引与标记；历史目录 `historical/never`；修 G22/G23 死链；新增 `scripts/docs/check.py`。
- **T-07 入口与模板收口**: `AGENT-INDEX` §3–§6、`AGENTS.md`/`CLAUDE.md`、MASTER §5、根 README、devops、架构/前端文档、checkpoint 模板、Review Gate、状态词映射全部对齐。
- **T-08 验证**: 全量单测 `Ran 158 tests — OK`；六个治理门禁与 `docs/check.py` 全 exit 0；`verify-control.sh` PASS；旧路径活文件 0 命中（历史叙述阳性对照 25 个文件）。实现与文档提交 `e4347c9`。

## Current

- 实现与文档已提交；本记录提交后 CHG 保持 `VERIFYING`，等待独立 Review 与 PR 合并。

## Next

1. 对照 `## Done When` 逐条 Review 本次 diff；小改可轻审，但 Done When 不可跳过。
2. 提交引用 `CHG-20261022-099` 的 PR 并合并 `main`。
3. 合并后把本记录移入 `delivery/completed/`，并从 `delivery/LEDGER.md` 移除。

## Blockers

- None.

## Known open items (not blocking this CHG)

- `scripts/verify/verify_m1_integration.py` 的结构性阻塞（Cloud 不读 `WT_MEDIA_CLOUD_HTTP_ADDR`、契约版本断言、Desktop 无 `npm run verify`）只登记，未修。
- 契约版本在 `compatibility.go`、三个 OpenAPI 与 `config/contract-map.yaml` 之间仍不一致，本轮不裁定。
- 真实双执行器并行演练、e2e/real 实跑未执行；按方案留到条件出现时。
- 三个运行仓的业务测试套件本轮未重跑：本轮未改运行时代码，四仓入口契约由 `tests/test_bin_control_entry.py` 覆盖。

## Recent verification

| 判据 | 读数 |
|---|---|
| Workspace 全量单测 | `Ran 158 tests — OK`（记录变更后重跑） |
| `verify_m0_config` / `verify_delivery_governance` / `verify_ai_workspace` | exit 0；AI snapshot 701 chars |
| `verify_skills` / `verify_product_master_alignment` / `verify_m2_acceptance` | exit 0；10 个 Skill 源 |
| `scripts/docs/check.py` | `docs governance ok (16 indexes)` |
| `scripts/verify/verify-control.sh` | PASS；status 六行含 compose-worker；无端口字面量 |
| 旧路径清扫 | 活文件 0 命中；历史叙述阳性对照 25 个文件 |

详细命令、输出与未覆盖项见 [`evidence/verification.md`](evidence/verification.md)。
