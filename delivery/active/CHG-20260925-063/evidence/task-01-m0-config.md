# Evidence: T-01 `verify_m0_config.py` 转绿

- CHG: `CHG-20260925-063`
- Task: `T-01`
- Date: 2026-09-25
- Type: command
- Status: PASS

## Purpose

消除 `verify_m0_config.py` 的 3 条红项：两条期望值落后于 `config/contract-map.yaml`，
一条与治理权威直接矛盾（要求本仓存在 CI 工作流，而 `AGENT-INDEX.md` §12 明写本仓不设 CI）。

## 改动清单（逐条对应 `change.md` §4.1）

| # | 位置 | 改动 | 依据 |
|---|---|---|---|
| 1 | `:94-95` 前 | `cloud_api` 的 `contract_revision` 期望值 `2026.07.14.4` → `2026.09.06.1` | `config/contract-map.yaml:12` 实测即 `2026.09.06.1`；D-01（契约层判据保留，只对齐现状） |
| 2 | `:105-106` 前 | `local_agent_api` 的 `contract_revision` 期望值 `2026.07.14.7` → `2026.09.06.1` | `config/contract-map.yaml:72` 实测即 `2026.09.06.1`；D-01 |
| 3 | `validate_ci_workflows` | 删除 `wt-media-workspace/.github/workflows/m0-workspace.yml` 整条；改成 docstring 说明**为何不得加回** | D-03；`AGENT-INDEX.md` §12「本仓库当前不设 CI」、`agent-workspace-conventions.md` §10「（`.github/workflows/` 已移除）」 |

**未改动、且有意保留的钉子**：`business_schemas.schema_revision == "2026.07.14.4"`（`:96-97`）。
它与 `cloud_api.contract_revision` 旧值字面相同但**是另一个合约的另一项**，`contract-map.yaml:32`
实测仍是 `2026.07.14.4`，故该钉子**是正确的**，不在本次改动内。此点单列，以免日后被「顺手一起改」。

## Method

```bash
python3 -B -X pycache_prefix=/tmp/pyc-none scripts/verify_m0_config.py
python3 -B -X pycache_prefix=/tmp/pyc-none -m unittest tests.test_verify_m0_config -q
```

原始输出：`artifacts/t01-baseline-verify_m0_config.out`（改前）、
`artifacts/t01-postfix-verify_m0_config.out`、`artifacts/t01-postfix-test_verify_m0_config.out`、
`artifacts/t01-diff-verify_m0_config.patch`、`artifacts/t01-mutation-control.out`。

改前读数（`artifacts/t01-baseline-verify_m0_config.out`）：

```
ERROR: cloud_api: expected contract_revision '2026.07.14.4'
ERROR: local_agent_api: expected contract_revision '2026.07.14.7'
ERROR: missing CI workflow: wt-media-workspace/.github/workflows/m0-workspace.yml
exit=1
```

改后读数：`Workspace config verification ok` / `exit=0`；
`tests.test_verify_m0_config` **Ran 4 tests / OK**（改前同一文件 4 条中 3 条失败）。

## Mutation controls（证明不是「改成恒真」）

改绿有三种坏法都必须被排除：期望值改错但恰好不触发、断言被删成空转、检查整体不再有判别力。
两次对照：

### 对照 1：新的期望值仍可失败

把 `config/contract-map.yaml:12` 的 `2026.09.06.1` 临时改成 `2099.01.01.1` 后实跑：

```
ERROR: cloud_api: expected contract_revision '2026.09.06.1'
exit=1
```

改回后 `git diff --stat config/contract-map.yaml` **0 行**——试验未留痕。
即：该钉子是**活的**，值错就报错，不是恒真。

### 对照 2：CI 检查器对三个运行仓仍有判别力

删掉 workspace 那条之后，「CI 检查是否整体失去判别力」必须排除。
把模块的 `OUTER_ROOT` 指向一个空目录，使三个运行仓的工作流都「不存在」：

```
empty OUTER_ROOT, allow_missing_repos=False ->
    missing CI workflow: wt-media-cloud/.github/workflows/m0-cloud.yml
    missing CI workflow: wt-media-agent/.github/workflows/m0-agent.yml
    missing CI workflow: wt-media-desktop/.github/workflows/m0-desktop.yml
empty OUTER_ROOT, allow_missing_repos=True  -> []
CONTROL OK: the CI checker still reports each missing runtime workflow (3/3).
```

**3/3 逐条报出**，且 `allow_missing_repos=True` 时保持静默（单仓检出下的预期行为，未被本次改动影响）。
即删除 workspace 那一条**只是移除了一个永远不可能通过的断点**，没有把检查器变成空转。

## 一处自我纠正（登记）

首轮取基线时我把 Python 调用写成变量 `PY="python3 -B -X pycache_prefix=/tmp/pyc-none"` 再 `$PY ...`。
zsh 不做词分割，整串被当成一个命令名，**三个产物文件全部只含 `exit=127`**——它们是**假产物**。
发现方式是核对 `exit=` 码：`exit=127` 与「红项 0 条」同时出现。
改用 shell 函数 `pyrun() { python3 … "$@"; }` 重跑，全部产物已替换；
`artifacts/t01-baseline-*` 均为重跑后的真实输出（`unittest` 4428 B、三个脚本 288/769/635 B）。
**教训**：产物落盘不等于产物正确——本次是靠 `exit=` 码与体量交叉核对抓出来的。

## 与 §14 遗留的关系

- 本次删除的断言在 `README.md:78` 有一句对应的描述（「the removed `m0-workspace.yml` workflow」），
  由 T-05 一并处理；§14 第 6 项登记「红项被文档化后就地固化」这一机制尚无对策。
- 本仓不设 CI ⇒ 门禁只在手工执行时才会被发现已经红（§4.5）。**T-01 把脚本转绿，但没有引入任何自动强制点**——§14 第 1 项。
