# Checkpoint: CHG-20260926-068

- CHG: `CHG-20260926-068`（四仓 `bin/control.sh` 入口——修 desktop 执行位、补四动词实跑、加机检）
- Level: S
- Updated: 2026-09-26

## 状态

`IMPLEMENTING`（2026-09-26 激活；跨四仓）

State words come from §3 of `delivery/MASTER_IMPLEMENTATION_PLAN.md`. A record in
`delivery/active/` may only be `IMPLEMENTING` or `VERIFYING`.

## Completed

- **T-00 激活**：`delivery/active/CHG-20260926-068/` 三件齐备；§5 范围封闭（4 Add／4 Modify／0 Delete／8 Explicitly Not Doing）；
  LEDGER 表行；快照 `--change CHG-20260926-068`；四仓基线与监听面读数落 `artifacts/t00-baseline.out`；
  `MASTER` §3 按实测刷新三项（active 0→1、活记录 19→20、活 `IMPLEMENTING` 0→1），量法**直接 import 门禁自己的 `status_word()`**，
  落 `artifacts/t00-status-words.out`；六门禁 ＋ `sync_skills` ＋ 套件落 `artifacts/t00-gate-activation.out`（六个 `exit=0`、`Ran 101 / OK`）；
  记录体量落 `artifacts/t00-record-size.out`（`change.md` 14149 B = **越界 +176%**，同 CHG-067 T-00 的结构性越界、读数小一档，照报）。
  详见 `evidence/task-00-activation.md`。

- **T-01 desktop**：`bin/control.sh` 磁盘＋index → `100755`（**字节零改动**，`numstat` `0/0`；`help` **126 → 0**）；
  新建 `tests/control.test.sh`（755，12 条判据／六类，被 `scripts/test.sh` 的 glob 自动拾取，不需要 cargo 或窗口）；
  **先红**（真实缺陷）3 passed／9 failed；**两处变异**：`chmod -x` → 8 failed、`git update-index --chmod=-x` → **恰 1 failed = 判据 2**；
  全跑 `scripts/test.sh` `exit=0`（cargo 372 passed／`control.test.sh` 12／`release-versions` 20）。
  并实测到新事实：同一 126 在 `set -e` 里读作 **1**（登记 `change.md` §14 第 1 项）。详见 `evidence/task-01-desktop-entry.md`。

## Current

T-01 收尾：更新记录、量体量、在 desktop 提交。

## Next

T-02 cloud：新建 `scripts/verify/test-control.sh`（755，六条判据）＋ `scripts/test.sh` 末尾一行（前缀 `[control]`）＋ `scripts/README.md` 一行。

### 对后续 Task 直接适用的硬约束（本 CHG 已踩定）

- **判据 5 必须逐行锚定**：`restart` 含子串 `start`，裸 `grep -F start` 会被 `restart` 那一行喂饱（假绿）⇒ 用 `^  (start|stop|restart|status)\b`。
- **agent 的 usage 行不含动词**（`Usage: bin/control.sh <command>`），动词只在下方描述行 ⇒ 断言针对 `help` **输出**，不是 usage 行。
- **cloud 的新检查不得污染 `verify_m3_acceptance.py:1621-1632` 的解析**：输出行首不得出现 `ok\s`／`FAIL`／`Test Files N passed`；前缀统一 `[control]`。
- **变异式「先红」必须是关掉判定后失败**，不能是 `ImportError`；每处变异都要还原并复跑取绿。
- **报「0 命中／已通过」**：做阳性对照、报出分母，锚取**不变的基线**而非 `HEAD`；新建文件扫描必须带 `--untracked`（CHG-067 §14 第 24 项）。
- **`start` 的 `exit=0` 不等于「起来了」**：探针不认领它探到的是谁（CHG-067 §14 第 19 项）⇒ T-05 的读数要同时看 pid 与端点。
- **Python 一律 `python3 -B -X pycache_prefix=/tmp/pyc-none`**；跨仓取证用 `git -C <repo> grep`。
- **记录体量按每 Task 增量卡**（`change.md` ≤ 5120 B／`checkpoint.md` ≤ 4096 B／evidence md ≤ 9216 B），锚取上一 Task 提交后的 blob。

## Blocked

- None.

## Recent verification

| 判据 | 读数 |
|---|---|
| 六门禁（激活前） | 六个全 `exit=0`；见 `artifacts/t00-gate-before.out` |
| 四仓 HEAD（激活前） | workspace `5622622`／cloud `e2ba4d8`／agent `aa95332`／desktop `9ba5486` |
| 四仓 `bin/control.sh`（激活前） | index：另三仓 `100755`、desktop **`100644`**；`./bin/control.sh help` desktop **126**／另三仓 0 |
| 四仓工作树（激活前） | cloud ` D internal/architecture/boundary_test.go`（用户操作，不追）、agent ` M AGENT-INDEX.md`、desktop 干净——**前两条先于本 CHG 存在，不触碰** |
| 监听面（激活前） | 18080＝pid 54420、8765＝pid 54456、54345＝比特浏览器 pid 13947（**第三方，不杀**） |
| desktop 入口（T-01） | index `100644 → 100755`、磁盘 `-rw-r--r-- → -rwxr-xr-x`、5233 B 不变；`./bin/control.sh help` **126 → 0** |
| desktop 机检（T-01） | 先红 3 passed／9 failed；变异 ① `chmod -x` → 8 failed、② index-only → **恰 1 failed**；还原后 12 passed／0 failed |
| desktop 全跑（T-01） | `scripts/test.sh` `exit=0`：cargo 372 passed／0 failed／5 ignored、`control.test.sh` 12、`release-versions` 20 |
