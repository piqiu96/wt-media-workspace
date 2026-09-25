# 计数汇总：CHG-20260923-059 各仓读数与出处

本文件是 `change.md` **AC-11**（计数只增不减）的读数出处。每个数都指向本目录里那份**原始转录**，
不是从记录里抄回来的。

起点（本 CHG 激活时，`change.md` §4）：

| 仓 | 命令 | 起点 |
|---|---|---|
| `wt-media-desktop` | `cargo test --workspace` | **336 passed / 0 failed / 2 ignored** |
| `wt-media-agent` | `bash scripts/test.sh` | **377 tests OK** |
| `wt-media-workspace` | `python3 -m unittest discover -s tests -q` | **69 tests / 4 failures**（4 条为既知红项） |

## 1. Desktop（`cargo test --workspace`）

| 时点 | 读数 | 出处 |
|---|---|---|
| 起点 | 336 passed / 0 failed / 2 ignored | `change.md` §4 |
| T-03（退出协议） | **353** passed / 0 failed / 4 ignored | `evidence/task-03-desktop-green.out` |
| T-04（完整性） | 同 353 段（只加 `--ignored real_agent` 两条真机臂） | `evidence/task-03-desktop-real-agent.out` |
| T-06（五类版本） | **363** passed / 0 failed / 5 ignored | `evidence/task-06-desktop-suite.out` |
| T-07（升级路径判据） | **372** passed / 0 failed / 5 ignored | `evidence/task-07-desktop-green.out` |
| 关闭时 | **372** passed / 0 failed / 5 ignored——**沿用 T-07 那一次读法，T-10 没有再跑一遍 desktop** | `evidence/task-07-desktop-green.out`；`change.md` AC-11 |

净增 **+36**（336 → 372），ignored 由 2 升到 5（新增的是 `real_agent` 真机臂与 CHG-057 遗留的两条）。
**无下降项。**

## 2. Agent（`bash scripts/test.sh`）

| 时点 | 读数 | 出处 |
|---|---|---|
| 起点 | 377 tests OK | `change.md` §4 |
| T-03（SIGTERM 停机） | **382** OK | `evidence/task-03-agent-green.out` |
| T-05（出货配置） | **397** OK | `evidence/task-05-suite.out` |
| T-06（版本契约） | **397** OK | `evidence/task-06-agent-suite.out` |
| T-07（路径判据） | **401** OK | `evidence/task-07-agent-suite.out` |
| T-09（吸收项／文档） | **407** OK | `evidence/task-09-agent-docs.out`、`evidence/task-09-gate.out` |
| **T-10**（D-08 的两条判据） | **409** OK | `evidence/task-10-agent-suite.out` |
| 关闭时 | **409** OK——**这一次是 OK，不等于「agent 套件全绿」** | `evidence/task-10-agent-suite.out`；`change.md` AC-11 |

净增 **+32**（377 → 409）。**无下降项。**（T-10 的 +2 来自 `tests/test_config_shipping.py`
新增的两条判据；更早一次本会话的读数误记为 407 作为关闭值，已按 `task-10-agent-suite.out` 订正。）

**一条口径限制（必读）**：`SigtermTests.test_a_request_in_flight_when_the_signal_arrives_is_waited_for`
是**既存间歇红**（原树 20 次 1 次，见 `evidence/task-10-flake.md`，登记为 D-27／Q-07）。
因此「agent 套件每次都是 OK」这句话**不成立**；上面每个 `OK` 都是**通过那一次的读法**，
分母与失败明细以本目录的 `.out` 转录为准。本 CHG 不用「本轮全绿」把这条盖过去。

## 3. Workspace（`python3 -m unittest discover -s tests -q`）

| 时点 | 读数 | 出处 |
|---|---|---|
| 起点 | 69 tests / 4 failures | `change.md` §4 |
| T-08（M2 回归） | 69 tests / 4 failures | `evidence/task-08-gate.out` |
| T-09（吸收项） | **73** tests / 4 failures | `evidence/task-09-gate.out` |
| T-10（回写与关闭） | 73 tests / 4 failures | `evidence/task-10-gate-green.out`、`evidence/task-10-workspace-suite.out` |

净增 **+4**（69 → 73，来自 T-09 新增的 `tests/test_skill_paths_resolve.py`），
**失败数恒为 4**，且四条名字自 T-06 起**逐条同名**：
`test_contract_map_matches_m1_cloud_agent_compatibility`、
`test_contract_map_provider_paths_exist_in_full_workspace`、
`test_static_cross_repo_contract_and_security_matrix`、
`test_current_product_master_and_governance_are_aligned`。

这 4 条是**既知红项**，判据不是「看着与我们无关」，而是 T-10 做的**同集合阳性对照**：
`git archive 54c87b2` 副本（落点在 `wt-media/` 之内）跑同一套件的失败名单与之**同集合**
（控制树独有 ∅、工作区独有 ∅）。详见 `evidence/task-10-gate-green.out` 末尾与
`evidence/task-10-writeback-and-close.md` §5。

## 4. 本 CHG 的计数边界

- 两个**曾下降**的数不属本 CHG，登记以免被误读：CHG-058 的 agent 379 → 377（断言的是已被裁定删除的
  `max_bytes`/`total_bytes` 互相约束）、CHG-056 的 agent 253（分母不同）。
  本 CHG 的起点取 **377**，故 379→377 这 −2 不在本 CHG 的账上。
- `cargo build` / `clippy` 的告警数：本 CHG 未设门禁（CHG-057 设过 `9` / `13`），
  故这里不报——**不报不等于没有**，只是本 CHG 没量。
- 计数只覆盖本 CHG 触碰到的三个仓；Cloud / `web` 在本 CHG 内未被改（那是 C 的范围），故无读数。
