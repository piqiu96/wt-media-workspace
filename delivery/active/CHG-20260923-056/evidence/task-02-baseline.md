# Evidence: Agent 测试基线实测

- CHG: `CHG-20260923-056`
- Task: `T-02`
- Date: 2026-09-23
- Type: command
- Status: PASS

## Purpose

在 T-02 的 13 个纯移动 commit 开始前，钉死「重构不得减少用例数」的基线。
后续每个 commit 的 `Ran N tests` 与本次比较，`N < 85` 或非 `OK` 即按失败处理。

## Method

在 `wt-media-agent` 仓（`HEAD = 99f408c`，分支 `main`，工作区干净）执行：

```bash
bash scripts/test.sh
```

`scripts/test.sh` 固定使用 `$ROOT_DIR/.venv/bin/python`，即本机 venv 解释器，
而非裸 `python3`。

## Expected

`Ran 85 tests` 且 `OK`（与 CHG-20260923-053 记录作者实测同值）。

## Actual

```
......................................................local_api.profile_open.failure profile_id=profile-1 duration_ms=0 error=BitBrowser request failed: 浏览器正在打开中
........................agent session invalidated; draining runner: session invalid
.......
----------------------------------------------------------------------
Ran 85 tests in 1.628s

OK
wt-media-agent scaffold ready: mode=local
```

- 用例数：**85**，结果 **OK**，耗时 1.628s。
- 测试文件数：19（`tests/test_*.py`）。
- 末尾 `scaffold ready: mode=local` 一行来自 `test_app.py` 的入口测试，
  是本 CHG 要删除的 scaffold 行为，故计数中含 1 个将被替换的用例
  （T-04 净变为 85-1+5 = 89）。

解释器事实（决定可用语法与标准库范围）：

| 环境 | 版本 | 约束 |
|---|---|---|
| 本机 venv（`test.sh` 实际使用） | 3.14.4 | 不能据此使用 3.13+ 语法 |
| 裸 `python3` | 3.14.6 | 同上 |
| CI（`.github/workflows/m0-agent.yml:19`） | 3.12 | `requires-python = ">=3.12"`，**这是真实下限** |

## Follow-Up

- 基线 = 85 tests OK，以此为闸门逐 commit 执行 T-02。
- 为避免「本机 3.14 能跑、CI 3.12 跑不了」，实现与测试一律不引入 3.13+ 语法
  或 3.13+ 新增标准库。
