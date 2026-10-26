# T-01：激活与依赖提交补齐

## 激活

| 项目 | 实际 |
| --- | --- |
| 激活记录 | `5dee255 docs(delivery): activate CHG-20261026-103`；`change.md` 状态 `IMPLEMENTING`，`plan.md` 入库，LEDGER／planned／M4／MASTER 同步 |
| 分支 | Cloud 与 Workspace 均为 `chg/CHG-20261026-103` |
| `wt chg start` | 通过：确认依赖归档、依赖提交是各仓 `main` 祖先、工作树与分支后进入实施（启动时执行） |
| 依赖来源 | CHG-102 归档只登记 Cloud `cb26c66`；本 CHG 的 `dependency_merge_commits` 补齐 Workspace `55ee841` 与 Desktop `4bf633c`，两者均可在对应仓 `main` 上解析 |

## 依赖校验修正

`0d5bd35 fix(chg): accept supplementary dependency commits` 让依赖校验采用“归档提交 + 本 CHG 补充提交”的并集，且补充项不替换归档项；找不到补充提交时仍拒绝启动。

```text
$ PYTHONDONTWRITEBYTECODE=1 python3 -m unittest \
    tests.test_wt_cli.WTCLITests.test_dependent_chg_supplements_archived_repository_commits \
    tests.test_wt_cli.WTCLITests.test_dependency_requires_machine_checked_main_commit
..
Ran 2 tests in 0.436s
OK
```

## 结果

- 依赖缺口已在本 CHG 内补齐并留下回归测试，未修改 CHG-102 的归档记录。
- 后续所有实施提交都在 `chg/CHG-20261026-103` 上，未直推 `main`。
