# T-14 门禁、合并与归档

日期：2026-10-27

## `wt chg verify` 读数（2026-10-27，状态 `VERIFYING`）

```text
PYTHONDONTWRITEBYTECODE=1 python3 scripts/wt.py chg verify CHG-20261026-104
```

结果：`repo` 场景通过，`integration` 场景在 `verify_m1_integration.py` 失败：

```text
wt-media-workspace: unittest discover -s tests     Ran 175 tests ... OK
wt-media-cloud: go test ./internal/modules/...     ok（全部包）
wt-media-workspace: python3 scripts/verify/verify_m1_integration.py
ModuleNotFoundError: No module named 'wt_media_agent.cloud_agent_client'
exit 1
```

### 基线既有失败，不计入 104 回归

- `verify_m1_integration.py:161` 仍从 `wt_media_agent.cloud_agent_client` 导入 `AgentIdentity`/`CloudAgentClient`。
- 该模块在 Agent 仓已由 `e034910`（`feat(agent): adopt session-bound Agent Token and durable task outbox`）删除；`51f2ee4` 曾保留 re-export shim，shim 已随 `e034910` 退役。
- 当前 Agent 仓源码只有 `src/wt_media_agent/clients/cloud/`；`src/wt_media_agent/cloud_agent_client.py` 不存在，只剩旧的 `__pycache__`。
- CHG-104 未修改 Agent 仓，也未修改该脚本；该失败在 104 分支与 `main` 上同样存在。

### 其余 Workspace 门禁（单独运行，全部通过）

```text
python3 scripts/wt.py test repo --repo wt-media-workspace
  unittest discover -s tests                     Ran 175 tests ... OK
  verify_delivery_governance.py                  ok（Active: CHG-20261015-098, CHG-20261026-104）
  verify_ai_workspace.py                         ok（snapshot 860 chars）
  verify_skills.py                               verified 10 skill source files
  verify_product_master_alignment.py             ok
  verify_m0_config.py                            ok
  scripts/docs/check.py                          docs governance ok (15 indexes)
  scripts/verify/verify-control.sh               PASS
```

## 目标仓门禁

```text
Cloud go test ./...                ok=72 fail=0 no_test_files=11
Cloud go build ./...               pass
Vitest（Cloud web/）               80 files / 736 tests passed
Cloud web npm run build            pass
Cloud PR #11 CI                    pass 2m19s（含 86a2c09）
Workspace PR #13 CI                pass 13s（b4153d0；T-13 记录提交后重跑）
```

## 走查与清理

用户已在 2026-10-27 确认 A1～A8/A6a、B1～B5、C1～C5 全部通过；结果写入 `evidence/T-09`～`T-12`。T-13 清理与删除后复核见 `evidence/T-13-data-cleanup.md`。

## 合并与归档

- Cloud PR #11 已合并：`fc8504e75a69ac8010b053582be808cebfbb51f6`（2026-10-27，merge commit）。
- Workspace 归档经 PR #13 合入 `main`；本记录随归档提交进入 `delivery/completed/CHG-20261026-104/`。按规则不在归档内容里预填本 PR 尚未产生的 merge SHA，`origin/main` 读回在合并后另行确认。
- 归档前 `wt chg verify` 已在 `VERIFYING` 状态运行；`verify_m1_integration.py` 的基线失败见上。
