# 关闭时计数与逐仓提交（CHG-20260923-058）

只记事实。三条读数都在**归档前的同一棵工作树**上现取，命令原样可重放。

## 1. 三个运行仓的关闭时计数

| 仓 | 起点（激活时） | 关闭时 | 命令 | 判定 |
|---|---|---|---|---|
| `wt-media-agent` | **379** tests OK | **377** tests OK | `bash scripts/test.sh` | 绿（**一条登记过的例外**，见 §2） |
| `wt-media-desktop` | **175** passed / 0 failed | **336** passed / 0 failed / **2 ignored** | `cargo test --workspace` | 绿，单调不降 |
| `wt-media-cloud/web` | **21 文件 / 101 tests** | **25 文件 / 166 tests** | `npx vitest run` | 绿，单调不增文件外的降 |

desktop 的 `2 ignored` 是既有忽略项（非本 CHG 引入），不影响 `336 passed / 0 failed`。

## 2. agent 379 → 377 这条例外

少的 2 条断言的是 `max_bytes` 与 `total_bytes` 的**互相约束**（配置交叉校验），
而这两个键已由用户 2026-09-24 的裁定删除——**没有比较对象**，故只能随之删除。
逐条（测试名、被删的断言、删除理由）列在 `task-02-log-rotation.md`。
这不是回归：`git grep` 复核 `BoundedFileHandler` **8 命中 → 0**，
阳性对照 `TimedRotatingFileHandler` 3 命中 / 2 文件、阴性对照 0。

**AC-11 的「只增不减」在此处按住不动**：例外已登记在 §10 行内与 §13 第 4 项，
未以「测试通过」吸收，也未改动基线里那句计数。

## 3. 治理仓

| 命令 | 实际 |
|---|---|
| `python3 scripts/verify_delivery_governance.py` | `ok. Active CHG: CHG-20260923-058`（归档前）；归档后 `--no-active` 快照为 `Active CHG: none` / `Status: NONE` |
| `python3 scripts/verify_agent_entry.py` | `ok. 0 warning(s)`（快照 2159 字符 / 预算 8000） |
| `python3 scripts/verify_skills.py` | `verified 10 skill source files` |
| `python3 -m unittest discover -s tests -q` | `Ran 69 tests … FAILED (failures=4)` —— **4 条既知红项**，判据是 `git archive HEAD` 的**同集合阳性对照**（失败项**逐名相同**），见 `task-09-writeback-and-archive.md` §3.1 |

## 4. 逐仓提交（§13 最后一项的判据）

**一仓一 commit；「移动文件」与「改逻辑」不同 commit。**

### `wt-media-desktop`

| commit | 内容 |
|---|---|
| `3a0ea08` | T-03 `AppPaths`——四个运行目录的解析与可写性 |
| `7825a75` | T-04 用户设置持久化——`settings.toml` 的读、原子替换与拒绝损坏 |
| `45356d2` | T-05 存储与日志只读命令——读取失败是错误，不是 0 MB |
| `ffb9ff8` | T-06 清理闭环——保护是一条路径，不是一个名字清单 |
| `9c938d0` | T-07 脱敏诊断导出——脱敏在门口，不是在里面 |
| `5ee840c` | T-08 本机设置与日志查看器的三个开口 |
| `1cd8eeb` | **T-09 入口文档按 27 个命令与九个新模块回写** |
| `ba2964a` | **T-09（构建产物）刷新内嵌前端入口快照**——纯指纹，`-f` 跟踪 |

T-02（轮转与依赖）在本仓的提交早于上表，见 `task-02-log-rotation.md`。

### `wt-media-agent`

| commit | 内容 |
|---|---|
| `1160f3c` | T-02 日志按小时切到 `agent.log.<时间戳>`，只按天保留 |
| `ce9b891` | **T-09 入口文档按小时切割与按天保留回写** |

### `wt-media-cloud`（`web/` 部分）

| commit | 内容 |
|---|---|
| `bb0136f` | T-08 本机设置页与日志查看器 |
| `df9dc8f` | **T-09 入口文档补上本机设置页与日志查看器** |

### `wt-media-workspace`（治理）

T-01 激活、T-02…T-08 各任务的记录与证据、T-09 回写与归档，逐任务独立提交。
归档本身是 `git mv`（移动文件），与回写（改内容）分属不同 commit。

## 5. 未动的范围外事项（避免被读成漏提交）

- `wt-media-desktop` 剩余的 **13 个** 乱格式文件（`bootstrap.rs`、`commands/{account,agent,bind,webview}.rs`、
  `dto/config.rs`、`http/{cloud,local_agent,mod}.rs`、`logging/paths.rs`、`preflight.rs`、
  `sidecar/{drain,mod}.rs`）**保持脏**——本仓不是 rustfmt-clean 的，它们是别的线留下的格式差异，
  不属于本 CHG（只对单个文件跑 `rustfmt`，不跑全仓 `cargo fmt`）。
- `wt-media-cloud` 的 `AGENTS.md`（M4-M5 Compose Worker 那条线）与未跟踪的 `dump.rdb`
  （运行中的 redis 产物）**保持脏**。
- `wt-media-workspace` 根的 `AGENT-INDEX.md`、`AGENTS.md`、`CLAUDE.md`、`README.md`、
  `docs/engineering/specs/agent-workspace-conventions.md` 与三份 PRD **保持脏**——是用户既有的改动，
  本 CHG 未碰。
