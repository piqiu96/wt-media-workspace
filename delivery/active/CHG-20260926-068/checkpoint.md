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

- **T-02 cloud**：新建 `scripts/verify/test-control.sh`（755，12 条判据／六类，**本仓 `scripts/verify/` 第一个真实文件**）；
  `scripts/test.sh` 末尾加一行**直接调用**（不写 `bash`）；`scripts/README.md` 补该行并改掉「两个子目录各只有一个 `.gitkeep`」。
  **每行带 `[control] ` 前缀**：`verify_m3_acceptance.py:1621-1632` 按 `^ok\s`／`^FAIL`／`Test Files N passed (N)`／`Tests N passed (N)` 解析本脚本日志。
  变异 ① `chmod -x` → 4 passed／8 failed；② index-only → **恰 1 failed**（与 desktop 同数同分布）。
  全跑 `exit=0`（`^ok\s` 56／`^FAIL` 0／vitest 25-166／`[control]` 12-0）。详见 `evidence/task-02-cloud-entry.md`。

- **T-03 agent**：新建 `tests/test_control_sh.py`（unittest，7 用例，`subprocess` **直接调用**；git 缺席时 `fail` 不 `skip`）。
  变异 ① `chmod -x` → 3 passed／4 failed；② index-only → **恰 1 failed**。全跑 `exit=0`、**`Ran 416`／`OK`**（基线 409，**+7 = 新增用例数**）；
  `.local/` 污染护栏未触发（该检出**有** `.local/`，护栏处于生效态；needle 在 `scripts/test.sh` 里命中 1 处）。
  详见 `evidence/task-03-agent-entry.md`。

- **T-04 workspace**：`scripts/test-control.sh` 判据 4 → 6 条（四条 `bash "$CONTROL"` 改**直接调用**，补判据 1／2）；
  新建 `tests/test_bin_control_entry.py`（跨仓 5 用例，判据 1-4、6；**不比对跨仓源码文本**；兄弟仓缺席 `skip` 并印分母）。
  变异 ① `chmod -x wt-media-desktop/bin/control.sh` → **恰 3 failed 全标 desktop**（本仓检查仍 `exit=0`）；
  ② `chmod -x bin/control.sh` → 恰 3 failed 全标 workspace ＋ 本仓检查 `exit=1`；
  缺席路径对照 `ran=5 skipped=5`、skip 文案含 `3/4`。六门禁全 `exit=0`、`sync_skills` `exit=0`、`Ran 106`（+5）。
  自造缺陷一处（生成器式循环中断）已修并登记。详见 `evidence/task-04-workspace-entry.md`。

- **T-05 四仓四动词真跑（16 格：13 端到端／3 止于既有前置／0 未覆盖——T-05A 修复后 desktop 那 3 格转端到端，最终 16/16）**：cloud 4/4（64839／64919，
  pid 文件＋监听＋`healthz` 三路旁证）、agent 4/4（58703／58731）、workspace 4/4（真起 cloud＋agent
  并跑完整条验收链：BitBrowser／DMG／登录冒烟全 `PASS`）；**desktop 3 格止于既有缺陷**——
  `beforeDevCommand` 的 `cd ../../wt-media-cloud/web` 多一段（实测 tauri 的 cwd 是 `wt-media-desktop`，
  不是 `src-tauri`，正确写法 `cd ../wt-media-cloud/web`），**CHG-067 用替身 cargo 掩盖了它**。
  清场靠按 pid 杀（`stop` 停不掉，§14 第 4／7 项；用户授权后 2 s 清空，比特浏览器未触碰）；
  环境留在运行态（cloud 70220／agent 70244），Desktop 应用已由 DMG 启动（pid 72068）。
  自纠一处：exit 读数曾因中间 `echo` 重置 `$?` 而错记（§14 第 8 项）。详见 `evidence/task-05-real-run.md`。

- **T-05A desktop `beforeDevCommand` 修复**（T-05 查出、用户裁定「修了」）：`cd ../../wt-media-cloud/web` → `cd ../wt-media-cloud/web`，
  **一行、一段路径**。根因两条独立证据（实测 cwd ＝ `wt-media-desktop`；同文件 `beforeBuildCommand` 用的是**一段** `../`，
  两条路径只有该 cwd 下才同时存在）。修复后真跑复跑：7 步读数全对（`start` 81359／`restart` 81755／`stop` 真停，
  5174 答 200），desktop 四格**由「止于既有前置」转为端到端** ⇒ **AC-03 成为 16/16 端到端**；
  `scripts/test.sh` `exit=0`（372／12／20，与修复前同读数）。改前查过**没有判据锚在该行**（四类读者只取 `version`／`devUrl`／CSP 键）。
  desktop `b0ae3c3`。详见 `evidence/task-05a-desktop-devcmd-fix.md`。

## Current

T-05A 完成；环境已按用户裁定**停掉**（cloud／agent 停、DMG 应用退出、挂载卷推出）。下一步 T-06 收尾。

## Next

T-06 workspace：归档 → `delivery/completed/`；LEDGER 同步；快照 `--no-active`；AC 矩阵逐条签字。
六门禁 ＋ `unittest discover -s tests -q` ＋ `sync_skills.py check` **取在最后一次改动之后**；
两遍失效指针扫描（各带阳性对照与分母，对照锚取**不变基线**）；四仓 `git status --porcelain` 对账。
**无待裁定项**：desktop 路径已修（D-06）、环境已停（D-07）。

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

- None. （T-05 的 5 格已由用户授权按 pid 清场后补跑完毕。）

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
| cloud 机检（T-02） | 绿 12 passed／0 failed；变异 ① `chmod -x` → 8 failed、② index-only → **恰 1 failed**；还原后复读 `100755` |
| cloud 全跑（T-02） | `scripts/test.sh` `exit=0`：`go test` `^ok\s` 56／`^FAIL` 0、vitest `Test Files 25 passed (25)`／`Tests 166 passed (166)`、`[control]` 12 passed｜0 failed |
| 前缀承重性（T-02） | 剥 `[control] ` 后：green 日志 delta 0（**空转，如实记**）、**red 日志 `^FAIL` 0 → 9**；比较器阳性对照 1/1 |
| agent 机检（T-03） | 绿 7/7；变异 ① `chmod -x` → 4 failed、② index-only → **恰 1 failed**；还原后复读 `100755` |
| agent 全跑（T-03） | `scripts/test.sh` `exit=0`：`Ran 416`／`OK`（基线 409，+7）；`.local/` 护栏未触发 |
| 实况进程归属（T-03） | 8765＝pid 54456 `local_api.server --port 8765`（ppid 1）、18080＝pid 54420（ppid 54410）；**两条 `stop` 都停不掉**（见 §14 第 4 项，T-05 必读） |
| workspace 两件（T-04） | `scripts/test-control.sh` 全跑 `exit=0`（判据 6 条）；跨仓 5 用例绿；缺席路径 `ran=5 skipped=5`、分母 `3/4` |
| workspace 变异（T-04） | ① desktop `chmod -x` → 恰 3 failed（全 desktop），本仓检查仍 `exit=0`；② 本仓 `chmod -x` → 恰 3 failed（全 workspace）＋本仓检查 `exit=1` |
| workspace 门禁（T-04） | 六门禁 `exit=0`、`sync_skills` `exit=0`、`Ran 106`／`OK`（基线 101，+5）；分母 `tracked=974 / untracked=3`，与 `e4e1587..HEAD` 的 `16 A／2 M` 对账闭合 |
| agent 四动词（T-05） | 18765：`status` 空 exit 1 → `start` 58703 exit 0 → `status` alive=yes health=ok → `restart` 58731 → `status` → `stop` → `status` 空 exit 1；实况 54456 前后验活、18765 归零 |
| desktop 四动词（T-05） | `status` ×3 一致（`alive=no health=down` exit 1）；`start`／`restart` 止于 `beforeDevCommand`（exit 1）；`stop` "not running" exit 0；无 stray 进程 |
| desktop 根因（T-05） | 实测 tauri 的 `beforeDevCommand` cwd ＝ `wt-media-desktop`（非 `src-tauri`）⇒ `../../wt-media-cloud/web` 多一段；正确 `cd ../wt-media-cloud/web` |
| cloud 四动词（T-05） | 空 `exit 1` → `start` 64839 `exit 0`（18080 监听＋`healthz 200`）→ `status` alive=yes exit 0 → `restart` 64919 → `status` exit 0 → `stop` exit 0（监听归 0）→ `status` exit 1 |
| workspace 四动词（T-05） | 空 `exit 1` → `start` `exit 0`（迁移 `0 applied, 39 total`；cloud 65668＋agent 65686；BitBrowser／DMG／登录冒烟全 `PASS`）→ `status` exit 0 → `restart` 68061／68079 → `status` exit 0 → `stop` → `status` exit 1；最后 `restart` 留运行态 |
| 清场（T-05） | `stop` 停不掉实况（cloud `alive=no health=ok` exit 1；`stop` exit 0 而 54420 仍活）；用户授权 `kill 54420 54456` → 2 s 清空、两端口归 0、无残留；比特浏览器 13947 前后验活 |
| 收尾读取（T-05） | `status` exit 0：cloud 70220／agent 70244 双 `health=ok`；18080 监听＝70227（`go run` 的子进程）；Desktop 应用 pid 72068（DMG 挂载态） |
| 自纠（T-05） | 首版 exit 读数取在 `echo "$out"` 之后 ⇒ `$?` 被重置成 0（cloud `status` 错记 0／实为 1）；重测订正，错误读数未留档 |
| desktop 修复后复跑（T-05A） | 7 步全对：空 `exit 1` → `start` 81359 `exit 0`（5174 答 200）→ `status` `alive=yes health=ok` → `restart` 81755 → `status` → `stop` 真停 → 空 `exit 1`；无 stray 进程 |
| desktop 回归（T-05A） | `scripts/test.sh` `exit=0`：cargo 372 passed／0 failed／5 ignored、`control.test.sh` 12/0、`release-versions` 20/0——与修复前同读数 |
| 改前影响面（T-05A） | 全仓读 `tauri.conf.json` 的只有取 `version` 的三处、取 `devUrl` 的一处、`bootstrap.rs:250` 断言 CSP 键不存在；**无一读 `beforeDevCommand`** |
| 环境收尾（D-07） | cloud／agent `stop` 后 18080／8765 归零；DMG 应用 72068 退出、`/Volumes/WT Media` 推出；比特浏览器 13947 仍活、未触碰 |
