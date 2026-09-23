# 运行产物（T-09 取证的可重放副本）

这些文件是 T-09 验收时的**原始运行输出**。它们原先落在 `/tmp/`，而 `/tmp` 会在重启后
被清空，引用它们等于把证据寄存在一个会消失的地方。T-10 收尾时复制到此处，使本 CHG 自洽。

复制是**逐字节**的（`shasum -a 256` 两两相等），唯一的例外见下。

| 文件 | 来源 | 被引用处 |
|---|---|---|
| `ac05-run5.log` | `evidence/tools/ac05_desktop_launch.py` 的四次真实启动（M1…M4） | `evidence/task-09-desktop-launch.md`（**证据运行即此份**；run1–run4 为调试过程，不随行） |
| `ac0109.out` | `evidence/tools/ac01_ac09_agent_modes.py` | `evidence/task-09-acceptance.md` AC-01/AC-09 |
| `ac06.out` | `evidence/tools/ac06_local_chains.py` | `evidence/task-09-acceptance.md` AC-06 |
| `ac07.out` | `evidence/tools/ac07_three_repos.sh` | `evidence/task-09-acceptance.md` AC-07 |
| `ac10.out` | `evidence/tools/ac10_task_chain.py` | `evidence/task-09-acceptance.md` AC-10 |
| `ac11-mutants.py` | AC-11 的变异脚本（6 个变异体 + 探测器自检） | `evidence/task-09-acceptance.md` AC-11 |

另有两个**脚本**（不是输出，故放在 `evidence/tools/`）在 T-10 一并从 `/tmp` 收回，
因为 `task-07-desktop-config.md` 引用它们：`ac03-token-check.sh`、`ac03-datadir-check.sh`
（T-07 的真实副作用前提取证，逐字节复制）。两者里的 token 都是运行期
`uuid.uuid4()` 生成、只以 `$TOK` 变量出现，**不含任何字面量凭据**（已扫）。

## 一处脱敏（唯一改动）

`ac06.out` 的第 8 行是 `POST /api/v1/bind` 的响应。`bind` 会铸一个本机会话 token，
该响应把它打了出来，形如 64 位十六进制。**该值已替换为 `<redacted-local-session-token>`**，
其余每一字节保持原样（`diff` 只有这一行）。

理由：本 CHG 的约束是「敏感值不得进日志、不得进诊断」。该 token 属于已退出的一次性
scratch 实例（进程已停、端口已释放），不构成在用的凭据，但它与约束禁止的形状同类，
所以**按名脱敏而不是按「反正没用」放过**。

同文件里的 cookie **名称**清单（`DedeUserID`、`SESSDATA`、`bili_jct` 等）是刻意保留的：
AC-06 要证的恰是「值没泄漏」——同一份输出里明写 `none of the 31 searchable cookie values
appear in the agent's log`，且列了 5 个因过短而不可检索的名字。删掉名字会让那条断言失去上下文。

`ac0109.out` 与 `ac06.out` 里各有一个 32 位十六进制串（BitBrowser 的 `main_user_id` 与一个
profile id）。两者是**本机应用的标识符**，不是凭据，且 `task-09-acceptance.md` 的环境事实表
里已经记录过，故保留。

## 不复现的东西

- `ac05-run1.log` … `run4.log` 未随行：它们对应已被改写的工具文本，只在
  `task-09-desktop-launch.md` 里作为调试过程被提及，不是证据运行。
- `/tmp/ac10/` 的隔离 Cloud（`server`/`migrate` 二进制 + `root/config`）与其 scratch schema
  `wt_media_cloud_ac10` 已在 T-10 收尾时清除（见 `change.md` §12）。重跑 AC-10 按
  `evidence/tools/ac10_task_chain.py` 重新构建即可，本目录不含构建产物。

## 可重跑性

上表每一行的工具都在 `evidence/tools/`，复制回来即可重放。本目录是**输出**，
不是工具——重跑请用 `evidence/tools/`，不要照抄这里的文件当输入。
