# CHG-20260926-068: 四仓 bin/control.sh 入口——修 desktop 执行位、补四动词实跑、加机检

## 1. Basic Information

- Level: S
- Status: IMPLEMENTING
- Created: 2026-09-26
- Current repository: `wt-media-workspace`
- Affected repositories:
  - `wt-media-workspace`
  - `wt-media-cloud`
  - `wt-media-agent`
  - `wt-media-desktop`

**锚点（Level S，按 CHG-060 §3、CHG-062～067 §1 先例写散文，不引 Milestone）**：`delivery/milestones/` 下 5 篇（README 除外）
对 `执行位|chmod|control\.sh|bin/ 目录|mode 100755` 实测 **命中 0**（分母 5）；M4／M5 为 `NOT_STARTED`。
`scripts/verify_delivery_governance.py` 只对 `Level: M/L` 强制 `- Milestone:`，本变更无可锚的真实里程碑，
故按实测取 `S`——与 CHG-065（四仓入口文件形态统一）、CHG-067（脚本层分层）同级同形：**零业务代码、零契约、零端口值**。

## 2. Change Goal

CHG-067 建了四仓统一的 `bin/control.sh`，其 AC-01（「四动词各跑一次并报读数」）被签为 PASS。收尾后实测发现
那条签字的两个缺口：**desktop 的入口没有执行位**（README 承诺的直接调用 `exit=126`），而 **AC-01 的判据看不见它**
（只跑 `bash -n`），16 格动词实跑也大多未真跑。

单一可验收结果：四仓 `bin/control.sh` **直接调用**都能跑（`help` `exit=0`、未知动词 `exit=2`）；
四仓各有一条**能失败**的机检守住「index 模式 100755 ＋ 磁盘执行位 ＋ 直接调用可用」；
四仓四动词**各真跑一次并报读数**，逐格标注覆盖面。

## 3. Baseline References

- 治理规范正文：`AGENT-INDEX.md`（§2 红线、§5 职责边界、§12 校验与判据分层 D-01）
- 交付规则：`delivery/MASTER_IMPLEMENTATION_PLAN.md` §2、§3（状态词汇与读数列）、§4、§6
- 归档边界：`delivery/completed/README.md`（`READ-ONLY`）
- 入口与目录事实规范：`docs/engineering/specs/agent-workspace-conventions.md`（§3、§10 判据纪律、§11 写入边界）
- 被补判据的母体：`delivery/completed/CHG-20260926-067/change.md` §10 AC-01、§14 第 8／17／19／29 项
- 用户裁定：2026-09-26 计划模式三轮问答（见 §6）

## 4. Current Facts

全部为本 CHG 开工前实测，读数落 `evidence/artifacts/t00-baseline.out`（F-01～F-04 与 `t00-status-words.out`）。

**F-01 只有 desktop 的入口缺执行位。** `git ls-files -s -- bin/control.sh`：workspace／cloud／agent **100755**，
desktop **100644**；磁盘同为 `-rwxr-xr-x` 对 `-rw-r--r--`。`./bin/control.sh help` desktop **126**（另三仓 0），
`bash bin/control.sh help` desktop 0 ⇒ 缺口正是「直接调用」。desktop `README.md:71` 写的直接调用。

**F-02 未知动词四仓同形，desktop 因为执行位连这条也取不到。** `./bin/control.sh bogus`：另三仓 **exit=2**
（stdout 0 字节、usage 全在 stderr）；desktop **exit=126**。

**F-03 cloud 的监听端口不可 env 覆盖。** `config/app.toml:8 http_addr = '127.0.0.1:18080'`；
`README.md:71` 明写 `WT_MEDIA_CLOUD_HTTP_ADDR` **只选探针地址**，`internal/config` 无 env 覆盖路径
⇒ `start` 无法用 scratch 端口与本机实况共存。workspace harness 的 `WT_MEDIA_CLOUD_PORT`（`:26`）**同病**：
它只改探针，调成非 18080 会探不到实例、转而起一个绑不上的子进程（§7 第 2 项）。

**F-04 前置与占位（开工前）。** 四仓 HEAD：workspace `5622622`／cloud `e2ba4d8`／agent `aa95332`／desktop `9ba5486`。
脏项三条，**全部先于本 CHG 存在、全程不触碰**：cloud ` D internal/architecture/boundary_test.go`、agent ` M AGENT-INDEX.md`、
workspace 仅本 CHG 的新目录。监听：18080 由 pid 54420（`server`）、8765 由 pid 54456（python）占；
54345 是 `/Applications/比特浏览器.app`（pid 13947，**第三方，不杀**，harness 的 `verify_bitbrowser` 依赖它）。
就绪：`cargo-tauri`／agent `.venv`／go26／`src-tauri/binaries/wt-media-agent-aarch64-apple-darwin`／DMG 产物 均在。
cloud `.cache/wt-media-cloud.pid` **不存在**（`stop` 不会误杀）；agent 有陈旧 pid 文件（`75067`，已死）。

**F-05 六门禁与套件在激活前全绿。** 激活**后**实测读数落 `evidence/artifacts/t00-gate-activation.out`（六个 `exit=0`、
`Ran 101 / OK`、分母 951 已跟踪）。**激活前**的读数不是本次量的，而是**继承** `5622622` 上 CHG-067 收尾的最后一次读数
（`delivery/completed/CHG-20260926-067/evidence/artifacts/t07-gate-final.out`，同为 `exit=0`／`Ran 101 / OK`）——
该 commit 就是本 CHG 的开工锚，未被打断，故这份继承读数成立；此处如实标注来源，不写成「本次实测」。

**F-06 `MASTER` §3 读数列实测与文本相等，激活会改三项。** 量法直接 import 门禁的 `status_word()`（`t00-status-words.out`）：
活记录 **19**（planned 19 ＋ active 0；`DISCUSSION` 7／`PLANNED` 3／`SUPERSEDED` 9）、归档列 **34**（`DONE` 32／`VERIFYING` 1／`IMPLEMENTING` 1）
＋退役 `CLOSED` 2／`HANDOFF` 2／`IN_PROGRESS` 4 ＝ **42** ✓。本 CHG 激活改：`active/` 0→**1** 篇、活记录 19→**20**、活 `IMPLEMENTING` 0→**1**。

## 5. Scope

范围在 T-00 **封闭**；后续新发现只登记 §14，除非落在已列举项内。

### Add

- **desktop** `tests/control.test.sh`（模式 755）：六条判据的机检，被 `scripts/test.sh:57-60` 的 glob 自动拾取。
- **cloud** `scripts/verify/test-control.sh`（模式 755）：同六条判据；**本仓 `scripts/verify/` 的第一个真实文件**。
- **agent** `tests/test_control_sh.py`：同六条判据的 unittest，被 `unittest discover -s tests` 自动拾取。
- **workspace** `tests/test_bin_control_entry.py`：跨仓复证四仓的判据 1-4、6（**不匹配跨仓源码文本**）。

### Modify

- **desktop** `bin/control.sh`：**只改模式**（磁盘 ＋ git index → `100755`），字节内容零改动。
- **cloud** `scripts/test.sh`：末尾加**一行**调用新检查（输出前缀 `[control]`，**不得出现行首 `ok\s`／`FAIL`／`Test Files N passed`**
  ——`verify_m3_acceptance.py:1621-1632` 靠这三类正则解析该脚本的日志）。
- **cloud** `scripts/README.md`：补新脚本一行。
- **workspace** `scripts/test-control.sh`：把 `bash "$CONTROL"` 改为**直接调用**，补判据 1-4（原文件只有判据 4-6）。

### Delete

None.

### Explicitly Not Doing

- **不改任何端口值**；不改 `config/app.toml`、`scripts/local-env.sh` 的默认值。
- **不给 cloud 加监听端口的 env 覆盖**（F-03）：那要同时改实现与 `README.md:71` 写明的设计，另起 CHG。
- **不给 cloud／desktop 加「端口字面量不进 README」机检**（CHG-067 §14 第 17 项）：跨仓源码字面量按 D-01 不作门禁。
- **不新增门禁、不改 `AGENT-INDEX.md` §12 的口径**：workspace 侧的跨仓检查落在 `tests/`（unittest），不占「六个门禁」。
- **不动** `verify_m1_integration.py`／`verify_m3_acceptance.py`／`m2b_local_acceptance.py` 的既有缺陷（CHG-067 §14 第 22 项等）。
- **不修 `wt-media-desktop/tests/package-release-macos.test.sh` 的 644**（§7 第 1 项）。
- **不杀比特浏览器**（pid 13947，第三方），不动它监听的 54345。
- 不自动改写运行仓文件（`conventions §11`）；跨仓各自提交。

## 6. Confirmed Decisions

| ID | Decision | Status |
|---|---|---|
| D-01 | 起 **S 级 CHG**：修执行位 ＋ 补四仓动词实跑 ＋ 给四仓加机检（执行位＋直接调用可跑）。 | CONFIRMED（用户 2026-09-26 裁定） |
| D-02 | 实况 cloud／agent **直接全部杀掉重跑**：四仓四动词按**默认端口与默认路径**真实端到端跑，不用隔离旋钮；desktop 的 `start` **真调 `cargo tauri dev`**（不用替身）。 | CONFIRMED（用户 2026-09-26 裁定） |
| D-03 | cloud 里 `internal/architecture/boundary_test.go` 的删除与 `dump.rdb` 的消失**是用户自己的操作**，不追。 | CONFIRMED（用户 2026-09-26 裁定） |
| D-04 | 比特浏览器（54345）**不在「全部杀掉」范围内**——第三方应用且被 harness 依赖（我的判断，登记待纠）。 | ASSUMED（本 CHG 登记） |
| D-05 | 调整历史**直接覆盖旧的**，不留取代注记，理由记进本 CHG 的 `change.md`。 | CONFIRMED（用户既有政策，沿用） |

## 7. Pending Questions

None.

## 8. Implementation Tasks

| Task | Goal | Status | Verification |
|---|---|---|---|
| T-00 | 激活：`change.md`／`checkpoint.md`／`evidence/`；§5 封闭；LEDGER 表行；快照 `--change`；四仓基线与监听面读数；`MASTER` §3 按 F-06 刷新三项 | DONE（`e4e1587`） | 六门禁 `exit=0`；LEDGER 表行逐字合 `validate_active_change`；§7 为 `None.`。见 `evidence/task-00-activation.md` |
| T-01 | **desktop**：`bin/control.sh` 模式 → `100755`（磁盘＋index）；新建 `tests/control.test.sh`（755，六条判据） | DONE | 改前 `./bin/control.sh help` **126**／改后 **0**；先红 3/9；**变异红** 8 failed（`chmod -x`）与恰 1 failed（`git update-index --chmod=-x`）；`scripts/test.sh` `exit=0`（372／12／20）。见 `evidence/task-01-desktop-entry.md` |
| T-02 | **cloud**：新建 `scripts/verify/test-control.sh`＋`scripts/test.sh` 一行＋`scripts/README.md` 一行 | TODO | `bash scripts/test.sh` 全跑；**变异红**；`git ls-files -s` 仍 100755 |
| T-03 | **agent**：新建 `tests/test_control_sh.py` | TODO | `unittest discover -s tests -q` 新基线；**变异红**；`.local/` 污染护栏仍绿 |
| T-04 | **workspace**：强化 `scripts/test-control.sh`（直接调用＋判据 1-4）；新建 `tests/test_bin_control_entry.py`（跨仓） | TODO | 两条绿；**变异红**：`chmod -x wt-media-desktop/bin/control.sh` → 跨仓用例在 desktop 那格红（CHG-067 漏掉的缺陷类别）→ 还原；六门禁 `exit=0` |
| T-05 | **workspace**：四仓四动词**真跑**（16 格），先停实况，逐仓 `status → start → status → restart → status → stop → status`，原始读数落 `evidence/artifacts/t05-*-verbs.out`；收尾留在运行态 | TODO | 逐格标注「端到端／止于既有前置／未覆盖」；仓序 cloud → agent → desktop → workspace；副作用登记 |
| T-06 | **workspace**：收尾——归档 → `delivery/completed/`；LEDGER 同步；快照 `--no-active`；AC 矩阵逐条签字 | TODO | 六门禁 ＋ `unittest` ＋ `sync_skills.py check`，取在最后一次改动之后；两遍指针扫描（各带对照与分母，锚取**不变基线**）；四仓 `git status` 对账 |

### 顺序与红窗（硬约束）

- **T-01 先于 T-04**：T-04 的跨仓用例在 desktop 仍是 644 时必然红。按上表顺序无红窗。
- **T-05 在 T-01…T-04 之后**：先让机检就位，真跑时四条机检本身就是环境旁证。
- **本 CHG 无跨仓红窗**：不改 workflow、不改 `AGENT-INDEX.md` §12 口径、不改任何端口值。

## 9. Repository Checklist

### wt-media-workspace

- [ ] `delivery/active/CHG-20260926-068/` 三件齐备；LEDGER 表行；快照 `--change`；`MASTER` §3 刷新（T-00）
- [ ] `scripts/test-control.sh` 强化；`tests/test_bin_control_entry.py`（T-04）
- [ ] 四仓四动词真跑与逐格覆盖面（T-05）
- [ ] 归档、LEDGER 同步、快照 `--no-active`、两遍指针扫描、四仓对账、AC 签字、DONE Gate（T-06）

### wt-media-cloud

- [ ] `scripts/verify/test-control.sh`；`scripts/test.sh` 一行；`scripts/README.md`（T-02）

### wt-media-agent

- [ ] `tests/test_control_sh.py`（T-03）

### wt-media-desktop

- [x] `bin/control.sh` 模式 `100644 → 100755`；`tests/control.test.sh`（T-01）

## 10. Acceptance Matrix

| AC | Requirement | Verification | Status |
|---|---|---|---|
| AC-01 | desktop `bin/control.sh` 可直接调用 | 改前 `help`=**126**／改后 **0**；index 与磁盘均 `100755` | PASS（T-01） |
| AC-02 | 四仓各有一条机检守住「index 100755＋磁盘执行位＋直接调用 `help`＝0＋未知动词＝2」 | 四条检查各自跑绿；**各做一次 `chmod -x` 变异红**并还原 | PARTIAL：desktop 已绿＋两处变异（T-01）；cloud／agent／workspace 待 T-02～T-04 |
| AC-03 | 四仓四动词**各真跑一次**且逐格标注覆盖面 | 16 格读数落 `t05-*-verbs.out`；每格属「端到端／止于既有前置／未覆盖」之一 | TODO |
| AC-04 | 机检**有判别力**（能失败），不是空转 | 变异红读数留档；报分母与阳性对照 | PARTIAL：desktop 已证（磁盘变异 8 failed／index 变异恰 1 failed）；余三仓待 T-02～T-04 |
| AC-05 | 跨仓回指与既有判据不被本 CHG 打红 | 六个静态门禁 `exit=0` ＋ `unittest` 套件 `OK` | TODO |
| AC-06 | 改动逐条落在 §5；**业务代码／契约／端口值零改动** | 逐仓 `git status --porcelain` ＋ 路径逐条归属；端口值 diff **0** | TODO |
| AC-07 | 记录体量按**每 Task 增量**在界内 | `change.md` ≤ 5120 B／Task、`checkpoint.md` ≤ 4096、evidence md ≤ 9216；锚取上一 Task 提交后的 blob | TODO |

## 11. Evidence

证据在 `evidence/`，只记事实、不复述需求。原始输出进 `evidence/artifacts/`。

- `evidence/task-00-activation.md` ＋ `artifacts/t00-*.out`（`t00-baseline.out`、`t00-status-words.out`、`t00-gate-activation.out`、`t00-record-size.out`）
- `evidence/task-01-desktop-entry.md` ＋ `artifacts/t01-entry-red.out`、`t01-entry-fix-and-mutations.out`、`t01-desktop-test-sh.out`
- 其余各 Task 的 evidence 与 artifacts 随 Task 落地。

## 12. Current Checkpoint

进度写在同目录的 `checkpoint.md`，**不在本文件内联**。`scripts/verify_delivery_governance.py` 强制这一对。

## 13. DONE Gate

- [ ] Scope completed.
- [ ] No blocking `Q-xx`.
- [ ] Acceptance matrix all PASS.
- [ ] Automated tests passed or justified.
- [ ] Required manual verification recorded.
- [ ] Diff checked for out-of-scope changes.
- [ ] Affected runtime repositories touched only when listed in scope.
- [ ] Required baselines updated.
- [ ] Affected repositories committed independently.
- [ ] Completed active records removed from `delivery/active` and `delivery/LEDGER.md`.

## 14. 实测推翻或补齐预想（本 CHG 登记，逐项在对应 Task 落地）

（T-00 无：激活期未发现与计划冲突的读数，F-01～F-06 均与计划一致。）

1. **T-01：同一缺陷在两个上下文里退出码不同——只有 `set -e` 改读数（126 → 1）。** 矩阵实测（`artifacts/t01-entry-red.out` 末段）：
   无选项／`set -u`／`set -o pipefail` → **126**；`set -e`／`set -eu` → **1**，且 `set -e` 同时改脚本自身退出码。
   ⇒ 计划里「改前读数 126」只在非 `set -e` 上下文成立；本 Task 的机检因此断言**属性**（`exit=0`）而非字面码，
   并把矩阵写进 `tests/control.test.sh` 的头注释。bash 内部机制未定位，只记可复现读数。
