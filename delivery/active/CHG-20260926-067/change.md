# CHG-20260926-067: 脚本层分层——四仓 bin 目录（启停＋健康）、scripts/dev 与 scripts/verify、每仓 scripts/README.md

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

**锚点（Level S，按 CHG-060 §3、CHG-062 §3、CHG-063～066 §1 先例写散文，不引 Milestone）**：`delivery/milestones/` 下 5 篇（README 除外）**无一覆盖脚本层**——对 `bin/|control\.sh|scripts/dev|scripts/verify|脚本目录|启停脚本|scripts/README` 实测 **0 命中**；其中 `M-launch-engineering` 已于 2026-09-25 关闭为 `DONE`（`M2`／`M3` 亦然），`M4`／`M5` 为 `NOT_STARTED`。`scripts/verify_delivery_governance.py:293` 只对 `Level: M/L` 强制 `- Milestone:`，而本变更**没有**可锚的真实里程碑，故按实测取 `S`（与 CHG-065「四仓入口文件形态统一」同级同形）。

**本 CHG 与 CHG-065 的唯一形态差别**：065 写三仓的**入口文件**、零运行时代码；本 CHG 写三仓的**脚本层**（新增 `bin/`、删死脚本、改 CI 工作流），范围更大但性质相同——**零业务代码、零契约、零端口值**。

## 2. Change Goal

把四仓的脚本层从「扁平混装」变成「**目录即分类**」：

- **`bin/`**：每仓一个 `control.sh`，承载本仓本地开发环境的**启停与健康检查**（`start|stop|restart|status|…`，健康检查并入 `status`）；
- **`scripts/README.md`**：每仓一份，写清三分类（运营／开发／验收）与**新脚本落位规则**（新开发脚本进 `scripts/dev/`、新验收脚本进 `scripts/verify/`；**启停一律进 `bin/`**）；
- **`scripts/dev/`、`scripts/verify/`**：本次只建骨架与规则，**不迁移**任何现存脚本。

单一可验收结果：四仓各恰一个 `bin/control.sh` 且形状统一；四仓 `scripts/README.md` 齐备；desktop 的 11 个死脚本被删且**零引用**（带阳性对照与分母）；六个静态门禁 `exit=0`、套件 `OK`。

## 3. Baseline References

- 治理规范正文：`AGENT-INDEX.md`（§2 红线、§3 知识地图、§5 职责边界、§6 需求路由、§8 交付治理、§12 校验）
- 交付规则：`delivery/MASTER_IMPLEMENTATION_PLAN.md` §2、§3（状态词汇与读数列）、§4、§6
- 归档边界：`delivery/completed/README.md`（`READ-ONLY`）
- 入口与目录事实规范：`docs/engineering/specs/agent-workspace-conventions.md`（§3 入口文件、§10 校验分层、§11 写入边界）
- 先例：`delivery/completed/CHG-20260925-065/change.md`（跨四仓 Level S）、`.../CHG-20260925-066/change.md`（归档边界与记录成本界）
- 死脚本集的**原始登记**：`delivery/completed/CHG-20260923-056/evidence/task-06-desktop-split.md:254-264`
- 用户裁定：2026-09-26 计划模式五轮问答（见 §6）

## 4. Current Facts

全部为本 CHG 开工前实测，读数与命令见 `evidence/artifacts/t00-*.out`。

**F-01 脚本层清点（分母＝`git ls-files scripts`，只看得见已跟踪／已暂存文件）。** workspace **18**、cloud **10**、agent **10**、desktop **20**。四仓 `bin/` **磁盘上都不存在**。

**F-02 只有 cloud 会静默吞掉 `bin/`。** `wt-media-cloud/.gitignore:3` 的字面量就是 `bin/`。`git check-ignore -v bin/control.sh` 在 cloud 报「被 `.gitignore:3` 忽略」，在另外三仓报「不被忽略」——**探针有判别力**（它能报出相反结论），故三个否定读数可信。因四仓 `bin/` 均不存在（F-01），放开忽略**不会**让任何既有产物突然变成待跟踪。

**F-03 归档只读门禁的扫描面是非递归的。** `scripts/verify_delivery_governance.py:130` 为 `scripts_dir.glob("*.py")`，分母实测 `scanned 12 script(s)`（＝ workspace `scripts/` 下全部 `.py`）。⇒ 新建 `scripts/verify/` 后落在其中的 `*.py` 会**静默滑出**该门禁的扫描面（门禁照绿、分母缩小）。

**F-04 六门禁与套件在激活前全绿。** 六个静态门禁 `exit=0`、`sync_skills.py check` `exit=0`、`unittest discover` **Ran 100 / OK**。

**F-05 `MASTER` §3 读数列与实测逐词相等（当前无漂移）。** 量法**直接 import 门禁自己的 `status_word()`**：活记录 **19**（planned 19 ＋ active 0；`DISCUSSION` 7／`PLANNED` 3／`SUPERSEDED` 9）、归档记录 **41**（`DONE` 31／`CLOSED` 2／`HANDOFF` 2／`IN_PROGRESS` 4／`IMPLEMENTING` 1／`VERIFYING` 1）、归档列 **33**；闭合式 33＋2＋2＋4＝**41** ✓。与 CHG-066 归档时的刷新读数**逐词相同**。**本 CHG 激活会改三项**：`active/` 0→1 篇、活记录 19→20、活 `IMPLEMENTING` 0→1。

**F-06 开工时两处脏工作树（先于本 CHG 存在）。** `wt-media-agent` 的 `AGENT-INDEX.md` 有一处**未提交删除**（发生在 CHG-065 提交 `6d740fc` 之后）；`wt-media-cloud` 有未跟踪的 `dump.rdb`。基线 HEAD：workspace `71fd32f`／cloud `0db02ab`／agent `6d740fc`／desktop `7c1b0ad`。两者**都不触碰**（§14 第 1 项）。

**F-07 desktop 死脚本集的当前形态。** 11 个：`bootstrap.sh`／`build.sh`／`dev.sh`／`start.sh`／`stop.sh`／`health.sh`／`verify-real-scripts.mjs`／`health-check.mjs`／`start-dev.mjs`／`stop-dev.mjs`／`health-dev.mjs`。它们的共同特征是**依赖已不存在的 `package.json` 与 `node_modules`**（desktop 已 Rust-only，`package.json` 由 `7aabb1a` 删除）。活件 9 个：`README.md`／`test.sh`／`build-release-macos.sh`／`package-release-macos.sh`／`prepare-release-sidecar.sh`／`stage-release-config.sh`／`repair-macos-signing.sh`／`verify-release-macos.sh`／`release-versions.sh`。

**F-08 `health-check.mjs` 的活断言本已过期。** 它断言 `cloud_agent_api === "v1@2026.07.14.7"`，而 `wt-media-desktop/contracts.lock.json` 实际是 `v1@2026.07.15.1`。⇒ **不为它做移植**（§5 Explicitly Not Doing）——移植等于搬进一个假断言。

**F-09 `verify_m0_config.py:272-280` 的 desktop needle 元组有 7 项**（`runs-on: macos-latest`／`node-version: "26"`／`dtolnay/rust-toolchain@stable`／`scripts/bootstrap.sh`／`npm run lint`／`scripts/test.sh`／`scripts/build.sh`），其中**三项**指向将被删除的脚本或已不存在的能力。

**F-10 被移入 `bin/` 的脚本有若干跨仓／跨文件调用点。** 逐条实测见 §8 各 Task；要点：`verify_m3_acceptance.py:561`（`bash scripts/start.sh`，`cwd=CLOUD_ROOT`）与 `:1738`（`scripts/stop.sh` 标签）是**跨仓**调用点；`test-local-control.sh:7` 用 `grep -Fqx` 逐字断言 `local-control.sh:6` 的 usage 串；cloud `start.sh:7` 与 `migrate.sh:7` 各 source 一次 `scripts/local-env.sh`；**agent 与 cloud 的 `verify-health.sh` 实测都不调用**被移的启停脚本（grep 空），各自内联。

**F-11 端口事实的落点已实测。** `wt-media-agent/config/agent.toml:27` 与 `config_online/agent.toml:29` 为 `8765`；`src/wt_media_agent/local_api/server.py:645` 的默认值亦为 `8765`；`wt-media-desktop/src-tauri/resources/desktop.production.toml:17` 为 `8765`。**本 CHG 不改任何端口值**。README 里有 **3 处**端口字面量（agent `README.md:17` 的 54345、`README.md:48-49` 的 18765、`config_online/README.md:16` 的 18080），按用户裁定**去值留名**。

**F-12 `release-matrix.yaml` 的 `verification:` 行是历史证据，不改写。** 该文件 `:2 planning_note` 声明 verified releases 是历史证据；`validate_release_matrix()`（`:126-240`）只查状态与契约版本、**不查命令行**。

## 5. Scope

范围在 T-00 **封闭**；后续新发现只登记 §14，除非落在已列举项内。

### Add

- 四仓 `bin/control.sh`：本仓本地开发环境的启停＋健康检查入口，`start|stop|restart|status` 四动词形状统一，健康检查并入 `status`。workspace 的额外保留既有 `verify`／`help`（用户裁定原文为「start stop restart status **等**命令」）。
- 四仓 `scripts/README.md`：三分类表 ＋ 落位规则 ＋ 指针行（workspace 为该文件**首次**建立）。
- 四仓 `scripts/dev/`、`scripts/verify/`：各一枚 `.gitkeep`，**不迁移**任何现存脚本。
- desktop `bin/control.sh`：本仓**新增**的启停能力（`cargo tauri dev` 的启停与探针），是四仓里唯一一个不完全由既有脚本合并而来的。

### Modify

- `wt-media-cloud/.gitignore:3`：`bin/` → `bin/*` ＋ `!bin/*.sh`。**必须用 `bin/*` 而非 `bin/`**——被排除的目录无法用 `!` 反向包含其内容。
- `scripts/verify_delivery_governance.py:130`：扫描面 `glob("*.py")` → 递归，使新建的 `scripts/verify/` 仍在归档只读判据内。
- `scripts/verify_m0_config.py:272-280`：desktop needle 元组按 T-03 的 workflow **终态**收敛；`:243-253` docstring 同步。
- `scripts/verify_m0_local.sh:39-45`：desktop 块只剩 `scripts/test.sh`。
- `scripts/verify_m3_acceptance.py`：`:561` 与 `:1738` 的 cloud 启停路径改指 `bin/control.sh`；`:414-421` 的 `foreign` 清单逐条重算。
- `scripts/local-control.sh` → `bin/control.sh`（workspace）：加 `restart`／`status`，保留 `verify`／`help`。
- `scripts/test-local-control.sh` → `scripts/test-control.sh`：断言串与文件名同步（其**被断言的对象**移动了，属同一次移动的连带项，不是「迁移一个无关旧脚本」）。
- `scripts/m2b_local_acceptance.py`：新增 `status` 动词（`cmd_status()` ＋ `choices`），作为 workspace `bin/control.sh status` 的读数来源。`local-control.sh` 原有的 `start`／`verify`／`stop` 三个动词都是 `exec harness <verb>`，`status` 沿用同一形状；**不写在 shell 里**的理由见 §14 第 11 项（端口字面量会造出第三份真相）。
- **四仓** `README.md`／`DIRECTORY_MAP.md` 的脚本层段落；cloud／agent 的 `scripts/README.md` 按模板重写并补上各自缺失的行（cloud `local-env.sh`、agent `build_desktop_sidecar.py`）。
- `AGENT-INDEX.md`：指针行（workspace 的 `scripts/README.md` 指向 §12 命令清单）。
- **agent 两处注释性路径**（非逻辑）：`src/wt_media_agent/local_api/server.py:44` 与 `tests/test_local_api_server.py:154` 中指向被移脚本的注释串。
- agent 三处 README 端口字面量**去值留名**（F-11）。
- **desktop** `.github/workflows/m0-desktop.yml` → Rust-only。
- **desktop** `.gitignore`：加 `.runtime/`——`bin/control.sh` 的 PID 与日志落点，该目录此前不存在（第 16 项）。
- **desktop `DIRECTORY_MAP.md:24,82`**：`devUrl` 的值**去值留名**。原措辞只覆盖「脚本层段落」，这里按 D-06「端口值只在配置文件里呈现」的精神一并处理并留痕（第 17 项）。

### Delete

- **desktop 的 11 个死脚本**（F-07 全列），逐个列出、逐条留痕。
- cloud `scripts/start.sh`／`stop.sh`／`health.sh`（内容并入 `bin/control.sh`）。
- agent `scripts/start-health.sh`／`stop-health.sh`／`health.sh`（同上）。
- workspace `scripts/local-control.sh`（移动，非删除）。

### Explicitly Not Doing

- **不迁移任何现存脚本**进 `scripts/dev/`、`scripts/verify/`——两个目录本次只建骨架与规则。用户裁定。
- **不改任何端口值**；**不把脚本里的 env 兜底端口挪进配置文件**——实测 agent `health.sh:9` 的 18765 是**隔离台自身的默认值**（`README.md:48-49` 与 CHG-056／057 证据均如此称），挪走会破坏隔离设计。
- **不改写 `release-matrix.yaml` 的 `verification:` 行**（F-12）。设计代理曾提议改掉 5 处 `npm run verify` 与 cloud／agent 的三处启停行，**撤销**：这些行写下时是真的，改写＝伪造历史。
- **不为 `health-check.mjs` 的活断言做移植**（F-08）。
- 不动 desktop 的发布链七件（`build-release-macos.sh` 一线）与两个 live shell 套件——实测零引用死名字。
- 不修改 `delivery/completed/CHG-20260923-056/evidence/task-06-desktop-split.md:254-264`（归档区只读）。
- **不把 `m2b-local-acceptance.sh`／`m2b_local_acceptance.py` 移进 `bin/`**：它们是 harness 而非入口（自带 `verify` 子命令），且 `m2b_local_acceptance.py` 被 F-03 的门禁扫描面与 8 个测试模块按字面路径引用。
- 生产部署与监控是独立 CHG，不在本计划内（用户裁定「线上运营＝本地开发环境」）。

## 6. Confirmed Decisions

| ID | Decision | Status |
|---|---|---|
| D-01 | **建 `bin/`**（运营：启停＋进程状态监控），并**建 `scripts/README.md`**；服务启停相关要分开。 | CONFIRMED（用户 2026-09-26 裁定） |
| D-02 | **`bin/` 只收「启停＋健康检查」**，全部移进去；**其余旧脚本一律维持现状**。 | CONFIRMED（用户 2026-09-26 裁定） |
| D-03 | **四仓统一用 `control.sh`**，含 `start|stop|restart|status` **等**命令；desktop 的 `start.sh`／`stop.sh` 合并为它。 | CONFIRMED（用户 2026-09-26 裁定） |
| D-04 | `scripts/dev/`、`scripts/verify/` **现在建，带规则说明**；**只服务新产生的脚本**。 | CONFIRMED（用户 2026-09-26 裁定） |
| D-05 | 「线上运营」＝ **本地开发环境**，非生产。 | CONFIRMED（用户 2026-09-26 裁定） |
| D-06 | **端口只在配置文件里呈现，不进 README**；**不改任何端口值**。 | CONFIRMED（用户 2026-09-26 裁定） |
| D-07 | desktop 删 **11** 个死脚本，CI 改写为 Rust-only。 | CONFIRMED（用户 2026-09-26 裁定） |
| D-08 | 调整历史**直接覆盖旧的**，不留取代注记，理由记进本 CHG 的 `change.md`。 | CONFIRMED（用户既有政策，本轮沿用） |

## 7. Pending Questions

None.

## 8. Implementation Tasks

| Task | Goal | Status | Verification |
|---|---|---|---|
| T-00 | 激活：`change.md`／`checkpoint.md`／`evidence/`；§5 封闭；LEDGER 表行；快照 `--change`；四仓 `git status` 基线；`MASTER` §3 读数列按 F-05 刷新（仅本 CHG 激活带来的三项） | DONE | 六门禁 `exit=0`；LEDGER 表行逐字合 `validate_active_change`；§7 为 `None.`。见 `evidence/task-00-activation.md` |
| T-01 | **workspace 脚本层分层**：`bin/control.sh`（由 `scripts/local-control.sh` 改：加 `restart`／`status`，保留 `verify`／`help`）；`scripts/test-local-control.sh` → `scripts/test-control.sh`；`scripts/dev/`＋`scripts/verify/`（各 `.gitkeep`）；`scripts/README.md`（**首建，终态**）；`AGENT-INDEX.md` 指针行；`verify_delivery_governance.py` 扫描面改递归 | DONE | 见 `evidence/task-01-workspace-layout.md`。要点：扫描面两臂对照落 `artifacts/t01-scan-surface-arm-{a,b}.out`（臂 A 分母 12／0 处、臂 B 分母 13／点名）；`test-control.sh` 四条判据的**五处变异全红**（`artifacts/t01-test-control-mutations.out`）；`status` 实读落 `artifacts/t01-control-status.out`；六门禁 ＋ `Ran 101 / OK` 落 `artifacts/t01-gate-{after,final}.out` |
| T-02 | workspace：**门禁前置（必须早于 T-03）**——`verify_m0_config.py:272-280` needle 收敛到 T-03 的终态、`:243-253` docstring 同步；`verify_m0_local.sh:39-45` desktop 块 → 只剩 `scripts/test.sh` | DONE | 见 `evidence/task-02-m0-gate-preamble.md`。要点：CI needle 判据**四臂**对照落 `artifacts/t02-m0-gate-arms.out` §A（臂 0 现状×新 tuple 绿／臂 1 变异点名／臂 2 **终态×新 tuple 绿**／臂 3 旧 tuple×终态 **3 处红**，证明收窄承重）；desktop 块两臂落同文件 §B（旧块 `exit=1` 停在 `npm ci`、单跑 `npm run lint` `exit=254`、新块 `exit=0` ＋ `377 tests`）；六门禁落 `artifacts/t02-gate-final.out` |
| T-03 | **desktop**：①干净克隆先测；②CI → Rust-only；③删 11 个死脚本；④新建 `bin/control.sh`；⑤`README.md`／`DIRECTORY_MAP.md`／`scripts/README.md` | DONE | desktop **`9ba5486`**（+277/−346）。见 `evidence/task-03-desktop-layout.md`。要点：`ls scripts/` 分母 **20 → 9**；11 个被删名字 `git grep -F --untracked` **各命中 0**（分母 109 个已跟踪文件；阳性对照 `release-versions.sh` 10 文件／`test.sh` 8，反向对照 0；`--untracked` 覆盖面另用 `cargo tauri` 两臂证明），落 `artifacts/t03-deleted-name-sweep.out`；`bin/control.sh` 十臂 ＋ 六处变异（含一处**自己踩到并修掉**的读端口静默坏法）落 `artifacts/t03-desktop-control-arms.out`；`scripts/test.sh` 全跑 `exit=0`／`372 passed; 0 failed; 5 ignored` ＋ `release-versions 20 passed` 落 `artifacts/t03-desktop-test-sh.out`；无 sidecar 的克隆上占位分支生效且读数逐字相同落 `artifacts/t03-clean-clone.out`；文档端口值三形态扫描落 `artifacts/t03-doc-port-literals.out`。**如实记：GitHub Actions 本身未在此运行；真实 `cargo tauri dev` 未跑（第 18 项）**。**① 的输入已由 T-02 先行量到一条**：两个 shell 套件都要 `node` 当 JSON 读取器（`node -p`／`node -e`，共 4 处，分母 2），故 `setup-node` 必须保留、只去掉 `cache:` 与 `cache-dependency-path:`（§14 第 13 项） |
| T-04 | **cloud**：`bin/control.sh`；`.gitignore` `bin/` → `bin/*`＋`!bin/*.sh`；删三个原脚本；`README.md`／`DIRECTORY_MAP.md`／`scripts/README.md` | DONE | cloud **`e2ba4d8`**（+192/−86）。见 `evidence/task-04-cloud-layout.md`。要点：**15 臂**落 `artifacts/t04-cloud-control-arms.out`——真实树 3 臂取到 `alive=no health=ok` `exit=1`（PID 文件里是**已死的 pid 13457**，18080 上另有开工前就在的监听者在答）＋ `stop` `exit=0`；隔离 9 臂（三个落点 env 覆盖＋`PATHPREPEND` 模拟 `go`）逐动词跑到 0 与非 0 两侧；变异 3 臂**实测出一个两仓共有的缺陷**——外部进程占端口时 `start` 假成功 `exit=0`，3.5 秒后 `status` 才识破（§14 第 19 项）。`.gitignore` 三读数落 §5 表，并实测 `git check-ignore -v` **对被 `!` 取反的规则也 `exit=0`**（§14 第 20 项）；`bash -n` `exit=0`；端口字面量 0 命中（阳性对照 `local-env.sh` 1 行）。回指扫描四种写法落 `artifacts/t04-cloud-sweep.out`（分母 497；形态 B 裸名有 3 条 `verify-health.sh` 子串假阳，故作废该形态；**A／C／D 三形态的 0 后经 T-05 复扫判定为假阴性——分母不含本 CHG 新建的未跟踪文件，更正读数 2 条，见 §14 第 24 项**）；`verify-health.sh` 自内联启停 ⇒ **本仓无红窗**。**如实记：本文件首轮把第六个门禁写成 `verify_m1_integration.py`（实为 `verify_m2_acceptance.py`，见 `AGENT-INDEX.md:209-210`），已重跑** |
| T-05 | workspace：**必须紧接 T-04**——`verify_m3_acceptance.py:561`／`:1738` 与 `:414-421` 回指 cloud `bin/control.sh` | DONE | 见 `evidence/task-05-workspace-repoint.md`。**实测计划只点名了 2 处，改的是 3 处**（另有 `:566` 的 `record` 标签，同为活体指针）。**活体面（`:!delivery`）逐形态 8 → 5 行，差 3 与三行编辑逐行对上**；余 5 行全在 `release-matrix.yaml` 的 `verification:` 历史证据行，按 §5 判留 ⇒ **可解析指针 = 0**。cloud 同口径 **2 行**（`bin/control.sh:4-5` 表头叙述）。阳性对照 `bin/control\.sh` workspace 23 文件/124 行、cloud 3 文件；反向对照（排除记录产物）0。**本 Task 实质产出是一次更正**：T-04 的「四种写法各 0」是**假阴性**——分母 497 不含未跟踪的新文件、四形态又都没带 `--untracked`（验算 500−3=497、497+3=500），更正读数 2 条，回改落三处（§14 第 24 项）。`foreign` 清单逐条重查落点后**结论不变**（§4）。`bin/control.sh`／`test-control.sh` 系 T-01 已建全，本 Task 只复核：`bash -n` 两个 `exit=0`、`test-control.sh` 全跑 `exit=0`（`artifacts/t05-test-control.out`）。**如实记：`verify_m3_acceptance.py` 未跑**（需真实运行实例，不属六门禁）⇒ 三行改动的**运行期**正确性未验证；**首版产物自己进了分母并毒化反向对照**（205 行），重做为紧凑版（§6） |
| T-06 | **agent**：`bin/control.sh`；删三个 health 脚本；三处 README 端口去值；两处注释路径；`README.md`／`DIRECTORY_MAP.md`／`scripts/README.md` | DONE | agent **`aa95332`**（13 文件，+221/−124）。见 `evidence/task-06-agent-layout.md`。要点：`scripts/` 分母 **10 → 7**；**12 臂**落 `artifacts/t06-control-arms.out`（10 条功能臂对**真实健康台**跑——`status` 运行中 `alive=yes health=ok` `exit=0`／停止后 `alive=no health=down` `exit=1` 两个方向都取到、`restart` pid 86409→86446、重复 start 幂等、未知动词 `exit=2`；臂端口由内核分配、PID/日志改到 `/private/tmp`，**不碰本机 18765、不写本仓 `.cache/`**；2 条变异臂复现 §14 第 19 项，**证明该危害是三仓共有**）。**端口判据有一个覆盖缺口**：计划给的 `127\.0\.0\.1:[0-9]{2,5}|:[0-9]{4,5}` 两段都要求数字前有冒号，抓不到 `VAR=18765` 形态（改前读数可证），**已补第三种写法**；三形态改前/改后＋分母（57/17/16 行）＋阳性对照落 `artifacts/t06-doc-port-literals.out`，改后冒号两形态 **0**、裸数值形态 3 行全是同文件的历史 CHG 编号、**端口事实 0 条**。回指扫描四形态落 `artifacts/t06-pointer-sweep.out`：带边界精确形态 **2 行**（全在新文件表头的过去时叙述，判留）⇒ **可解析活指针 = 0**；阳性对照 `bin/control.sh` 6 文件／12 行；**该产物当场复现了 §14 第 24 项那个坑**（同一命令只差 `--untracked`，读数 0 → 2）。**计划点名 2 处注释路径，改的是 3 处**（另有 `tests/test_runtime_config.py:145`，§14 第 26 项）。`unittest discover -s tests -q` → `Ran 409 tests` / `OK`，rc=0，与激活前基线**逐字相同**；`bin/control.sh` `bash -n`／`sh -n` 均 `exit=0` |
| T-07 | workspace：收尾——归档 → `delivery/completed/`；LEDGER 同步；快照 `--no-active`；AC 矩阵逐条签字 | TODO | 六门禁 ＋ `unittest` ＋ `sync_skills.py check`，**取在最后一次改动之后**；两遍失效指针扫描（各带阳性对照与分母）；四仓 `git status --porcelain` 对账 |

### 顺序与红窗（硬约束）

- **T-02 必须先于 T-03**：反向顺序会让 `verify_m0_config.py` 与 `verify_m0_local.sh` 在 desktop 提交与 workspace 修复之间走红。T-02 收敛 needle 是**无红**的（终态元组是新 workflow 文本的子集）。
- **T-05 必须紧接 T-04，中间不插任何工作**：这是本 CHG **唯一的跨仓红窗**——`verify_m3_acceptance.py:561` 在 T-04 之后、T-05 之前指向一个已不存在的 `scripts/start.sh`。**如实记录**并说明可接受的理由：该脚本**不是六个静态门禁之一**、`release-matrix.yaml` 不驱动它、无 CI 消费它，全程六门禁与单元套件保持绿。备选的零红窗走法（先加 `bin/control.sh`、回指、再删原脚本，多两次提交）登记为**已考虑未采用**。
- **T-06 无红窗**：agent 的 `verify-health.sh` 实测不调用被移的三个脚本（F-10），迁移自足。

## 9. Repository Checklist

### wt-media-workspace

- [x] `delivery/active/CHG-20260926-067/` 三件齐备；LEDGER 表行；快照 `--change`（T-00）
- [x] `bin/control.sh`；`test-control.sh`；`scripts/dev/`＋`scripts/verify/`；`scripts/README.md`；`AGENT-INDEX.md` 指针；扫描面改递归（T-01）
- [x] `verify_m0_config.py`／`verify_m0_local.sh` 门禁前置（T-02）
- [x] `verify_m3_acceptance.py` 回指 cloud `bin/control.sh`（T-05）；连同 T-04 假阴性的回改
- [ ] 归档、LEDGER 同步、快照 `--no-active`、两遍指针扫描（T-07）

### wt-media-cloud

- [x] `bin/control.sh`；`.gitignore`；删三脚本；`README.md`／`DIRECTORY_MAP.md`／`scripts/README.md`（T-04）

### wt-media-agent

- [x] `bin/control.sh`；删三脚本；README 端口去值；三处注释路径（T-06）

### wt-media-desktop

- [x] CI → Rust-only；删 11 死脚本；`bin/control.sh`；`README.md`／`DIRECTORY_MAP.md`／`scripts/README.md`；`.gitignore` 加 `.runtime/`；`scripts/dev/`＋`scripts/verify/`（T-03）

## 10. Acceptance Matrix

| AC | Requirement | Verification | Status |
|---|---|---|---|
| AC-01 | 四仓各恰一个 `bin/control.sh`，形状统一（同一组动词、`status` 含健康检查） | 四仓 `ls bin/` 分母各为 1；四动词各跑一次并报读数；`bash -n` 全过 | TODO |
| AC-02 | 四仓 `scripts/dev/`、`scripts/verify/` 存在，且 `scripts/README.md` 写清落位规则 | 四仓目录存在（分母 4／4）；README 含规则段；**无现存脚本被迁入**（迁入数 0） | TODO |
| AC-03 | cloud 的 `.gitignore` 不再吞掉 `bin/` 下的脚本 | `git check-ignore -v bin/control.sh` 改读数；**阳性对照**：同命令对 `bin/wt-media-cloud` 仍报被忽略 | TODO |
| AC-04 | desktop 的 11 个死脚本全删且**零引用** | 删除后每个名字 `git -C wt-media-desktop grep` 命中 **0**（报分母）；阳性对照 `release-versions.sh` 命中 >0 | TODO |
| AC-05 | desktop CI 为 Rust-only，且 `verify_m0_config.py` 的 needle 与 workflow 文本**一致且能失败** | 门禁 `exit=0`；**变异红**：改 workflow 里一处 needle → 报出并点名，还原 | TODO |
| AC-06 | `verify_m0_local.sh` 的 desktop 块只含活脚本 | `sh -n`；**变异红**：放回 `npm run lint` → 失败（证明该行承重） | TODO |
| AC-07 | 跨仓回指充分：旧启停路径在 workspace＋cloud 零命中 | `git grep -nE 'scripts/(start\|stop\|health)\.sh'` 命中 **0**，报分母；阳性对照命中 >0 | TODO |
| AC-08 | 新建的 `scripts/verify/` **在**归档只读门禁的扫描面内 | 扫描面改递归后分母打印；**变异红**：放一个写归档的临时 `.py` → 点名 | TODO |
| AC-09 | agent 三处 README 无端口字面量 | 正则命中 **0**；**报分母（三文件行数）＋阳性对照**（副本里放回一个数字必须命中） | TODO |
| AC-10 | 六个静态门禁 `exit=0` ＋ 套件 `OK`，取在最后一次改动之后 | 读数落 `evidence/artifacts/`；带分母 | TODO |
| AC-11 | 四仓改动逐条落在 §5 范围；**业务代码／契约／端口值零改动** | 逐仓 `git status --porcelain` ＋ 改动路径逐条归属 §5；锚 T-00 基线；端口值改动的 diff **0** | TODO |

## 11. Evidence

证据在 `evidence/`，只记事实、不复述需求。原始输出进 `evidence/artifacts/`。

- `evidence/task-00-activation.md` ＋ `artifacts/t00-*.out`
- `evidence/task-01-workspace-layout.md` ＋ `artifacts/t01-*.out`（7 个）
- `evidence/task-02-m0-gate-preamble.md` ＋ `artifacts/t02-*.out`
- `evidence/task-03-desktop-layout.md` ＋ `artifacts/t03-*.out`（7 个）
- `evidence/task-05-workspace-repoint.md` ＋ `artifacts/t05-*.out`（2 个：`t05-pointer-sweep.out`、`t05-test-control.out`）
- `evidence/task-06-agent-layout.md` ＋ `artifacts/t06-*.out`（5 个：`t06-control-arms.out`（12 臂）、`t06-doc-port-literals.out`（三形态＋分母＋阳性对照）、`t06-pointer-sweep.out`（四形态＋分母＋双向对照＋提交后复核）、`t06-gate-final.out`（六门禁＋`sync_skills`＋workspace 套件）、`t06-record-size.out`（按 Task 增量，自指单列））
- `evidence/task-04-cloud-layout.md` ＋ `artifacts/t04-*.out`（5 个：`t04-cloud-control-arms.out`、`t04-cloud-sweep.out`、`t04-gate-after.out`（六门禁首轮，含一次写错清单的自造红）、`t04-gate-final.out`（记录写完后复跑）、`t04-record-size.out`（自指项不计入自身分母））
- 其余各 Task 的 evidence 与 artifacts 随 Task 落地。

每条记录含：命令或手工动作、期望、实测、通过与否、相关 commit。

## 12. Current Checkpoint

进度写在同目录的 `checkpoint.md`，**不在本文件内联**。`scripts/verify_delivery_governance.py` 强制这一对。

## 13. DONE Gate

- [ ] Scope completed.
- [ ] No blocking `Q-xx`.
- [ ] Acceptance matrix all PASS.
- [ ] Automated tests passed or justified.
- [ ] Manual verification evidence recorded where required.
- [ ] Diff checked for out-of-scope changes.
- [ ] Runtime repositories touched only if listed in scope.
- [ ] Required baselines updated.
- [ ] Affected repositories committed independently.

## 14. 实测推翻或补齐预想（本 CHG 登记，逐项在对应 Task 落地）

1. **两处开工前就存在的脏工作树**（§4 F-06）：agent `AGENT-INDEX.md` 的未提交删除、cloud 未跟踪的 `dump.rdb`。**都不触碰**，但会让收尾时 agent 仓的读数**失去归因**，须在读数旁注明。
2. **分级从计划里的 M 改为 S**（§1 锚点）：计划写 `Level M` 时未核实是否有可锚的里程碑；实测 5 篇里程碑对脚本层 **0 命中**，且 Level M/L 会被 `verify_delivery_governance.py:293` 强制要 `- Milestone:`。按 CHG-065 先例取 `S`。
3. **`bin/` 的第二权威风险**：`AGENT-INDEX.md:114` 把「修改 Agent Sidecar 启停」路由给 **Desktop**，其生命周期实现在 Rust（`src-tauri/src/sidecar/`）。本次建的 `bin/control.sh` 只覆盖**本地开发环境**的进程启停，与 sidecar 生命周期是两件事——这条边界必须写死，否则日后会被读成「启停有两个所有者」。
4. **架构基线 §7.5 的统一动词表**是 `bootstrap/dev/test/lint/generate/build/package/verify`，**不含 `start`/`stop`/`status`**；而 `MASTER:202-204` 的 M0 验收要求每仓有 `start`/`stop`。本 CHG 建的 `bin/control.sh` **使这个缺口更显**，但基线归 architecture 所有，不在本 CHG 处置。
5. `contracts.lock.json` 在删除 `health-check.mjs` 后**失去唯一读取者**（仅剩两处叙述），且被删文件里那条断言本已过期（F-08）。
6. `docs/engineering/architecture/…_V1.md` §6.3 与 A.5 仍写 desktop 有 `src/`、`package.json`、`packaging/`，三者实测自 `7aabb1a` 起不存在——独立 CHG。
7. `m2b_local_acceptance.py:36` 的 `AGENT_PORT` 默认 `8765` 与 `config/agent.toml:27` 重复；`m2b_local_acceptance.py:48` 硬编码 DMG 版本 `0.1.0`；`verify_m0_local.sh:39-45` 与 `verify_m0_config.py:272-280` 是同一事实的两个落点（本 CHG 只各自缩小、不合并）。T-01 的 `status` 因此**没有**把端口抄进 shell，而是复用本文件的常量（第 11 项）。
8. **LEDGER 表行的形态有两个硬约束，而第一条的报错措辞指向错误的方向**（T-00 自己踩到）。首轮激活后三条门禁红：`LEDGER_ROW_RE`（`^\|\s*(CHG-\d{8}-\d{3})\s*\|`）要求 `|` 后**紧跟** `CHG-`，写成 `| [CHG-…](…) |` 则**表行不被识别**，报错是 `current context and ledger disagree: … != none`——读起来像「台账为空」，与真实成因（表行形态）不是同一个说法；同时 `expected_row` 的 `title` 取自 H1，故 **H1 标题里出现 `|` 会把表行劈成 5 格**，子串比对不中，报错换成「Ledger is not aligned」。⇒ 两条约束（**表渲染**与**门禁比对**）都要满足：H1 无 `|`，表行为 `| CHG-… | 标题 | 状态 | 仓库 |` 四格、无反引号无链接。详见 `evidence/task-00-activation.md` §5。
9. **`local-control.sh` 的失效引用只剩 `docs/superpowers/` 两处，判留不处理。** 一处是 plan 里的可重放命令（`./scripts/local-control.sh start`），一处是 spec 里的时序叙述；该目录被 `AGENT-INDEX.md:58` 声明为**非权威分析材料**（「不作为新开发依据」）。改它等于改写历史分析材料，且不在 §5 范围内 ⇒ **登记不处理**。同一次扫描里其余命中（`delivery/completed/` 各篇）都是过去时叙述，按判留保留。分母 902 个已跟踪文件，阳性对照 `bin/control.sh` 命中 >0。
10. **`status` 的两个信号会不一致，退出码的含义要写死。** pid 文件回答「是不是**经 harness** 起的」，health 探针回答「现在**有没有东西在答**」。T-01 实测本地环境**在跑**（`lsof` 报 54420／54456，两个 health 端点各答 `{"status":"ok"}`）而 `<root>/.local/m2b/pids` **不存在** ⇒ 读数是 `alive=no health=ok`、`exit=1`。故 **`exit=1` 的含义是「本环境不是由 harness 起的」，不是「服务挂了」**——两行读数分开打印正是为了不把这两件事压成一个 yes/no。四仓的 `control.sh status` 必须沿用同一语义，否则同名动词在四仓不同义（AC-01 的「形状统一」含此条）。
11. **`bin/control.sh` 不得承载端口字面量，并已机检。** `status` 若在 shell 里直接 curl，就会在 `config/agent.toml` 与 `m2b_local_acceptance.py:36` 之外造出**第三份**端口真相（第 7 项）。因此 workspace 的 `status` 是 harness 的新动词，读同一批常量。约束由 `scripts/test-control.sh` 第 4 条机检，变异红（`artifacts/t01-test-control-mutations.out`）。此机检落在 `test-control.sh` 而非六门禁之一，不违反「不加机检」——后者针对的是 `scripts/README.md` 的**规则句外溢**。
12. **CI needle 是「workflow 文本里有这个字符串」，从不证明那一步能跑**（T-02 实测）。`m0-desktop.yml` 的 `npm run lint` 自 `7aabb1a`（`package.json` 在那次提交被删）起就已经坏了，而 needle 一直绿——**判据与它想保证的事之间差了一整层**。本案实测：`npm run lint` 在 desktop `exit=254`；旧 desktop 块的第一颗钉 `scripts/bootstrap.sh`（`npm ci`）`exit=1` 就停住，**根本走不到 lint**。故计划里写的变异（「把 `npm run lint` 放回 → 脚本失败」）成立但**降级**：它不是被第二个动词抓到的，是第一个动词就断了。⇒ 这一条不改任何判据（needle 的形态正是 CHG-065 D-01 要的稳定判据），只作**已知限制**登记。
13. **「Rust-only」= 没有 Node 包工具链，不是没有 `node`**（T-02 实测，直接改写 T-03 ① 的待决项）。desktop 的两个 shell 套件都调 `node`，但只当 JSON 读取器：`tests/package-release-macos.test.sh:15` 与 `tests/release-versions.test.sh:168,267,314`（`node -p`／`node -e`，分母 2 个套件共 4 处）。⇒ `setup-node` **保留**，只去掉 `cache:` 与 `cache-dependency-path: package-lock.json`（锁文件不存在）。计划把这一项留给 T-03 ① 决定，现已提前量到并写进 T-03 行。
14. **T-02 收窄的 4 条 needle 里只有 3 条是被迫的。** 臂 3（旧 tuple × T-03 终态 workflow）只报 3 处红：`scripts/bootstrap.sh`／`npm run lint`／`scripts/build.sh`。第 4 条 `node-version: "26"` 在终态文本里仍在（`setup-node` 保留），删它是**主动**决定——理由见第 13 项：node 已不是本仓工具链，把它当契约来卡会让判据的可满足性取决于一个尚未做的决定。**如实记：这一条不是被迫的。**
15. **读端口的那一行有个静默坏法**（T-03 自己踩到，已修）。首版用 `node -p '…devUrl'` 并「为空即报错」，但**键不存在时 `node -p` 打印字符串 `undefined` 且 `exit=0`**，空判断永不触发，读数把 `url=undefined` 当地址打出来（`exit=1` 由 health 侧掩盖了它）。改为表达式对缺键返回空串 ＋ 先判配置文件在不在；回归臂 M4／M5。第 10 项那对信号在 desktop 实测互为镜像：`alive=no health=ok`（有东西在答但非本 harness 所起）与 `alive=yes health=down`（进程在、配置指到的地址无应答）**两个方向都取到了**。
16. **`scripts/test.sh` 在没有 sidecar 的克隆上会写一个占位文件**（T-03 的必要偏离）。`externalBin` 的存在性检查没有开关，真 sidecar 由跨仓的 `prepare-release-sidecar.sh` 产出，而套件**不读它的内容** ⇒ 只在路径缺失时写一个自报家门、`exit 1` 的占位符。实测有／无 sidecar 读数逐字相同（`377 tests`／`372 passed; 0 failed; 5 ignored`）；占位符被 `.gitignore:10` 挡住；`release-versions.sh --check` 拒绝任何没有 `target/sidecar-manifest.json` 的包（只有真构建写得出）⇒ 到不了发布。
17. **端口字面量的常驻机检只有 workspace 有**（`scripts/test-control.sh` 第 4 条，见第 11 项）。desktop／cloud／agent 本次只有一次性 grep，因为 §8 的 T-03／T-04／T-06 三行都没写「建本仓 `test-control.sh`」——**计划级缺口，登记不补**。连带：desktop `DIRECTORY_MAP.md:24,82` 原把 `devUrl` 的值写进了正文（`devUrl 5174`），按 D-06 的精神去值留名（§5 Modify 末条）——**这条裁定的措辞是「不进 README」，而实际漏网处是目录地图**，故留痕。
18. **desktop `start` 只在模拟 cargo 下跑过。** 真实 `cargo tauri dev` 会编译并打开窗口，不适合在本 Task 里跑；`PATH` 前置一个只实现 `tauri --version`／`tauri dev` 的替身，把 `.runtime/` 的落点、进程组、探针、`stop` 的整组回收都跑到（`artifacts/t03-desktop-control-arms.out`）。**如实记：真实 `cargo tauri dev` 未跑；GitHub Actions 未跑。**
19. **`start` 的探针不认领它探到的是谁**（T-04 实测，**T-06 补测后确认为三仓共有**，本次不修）。判据是「进程还活着 **且** 探针通」，但探针只问「有没有东西在答」。T-04 臂 14 实测：先让一个外部进程占住端口（不由 `control.sh` 起，故无 PID 文件），再让本脚本起的那个人 3 秒后自杀 ⇒ `start` 打印 `started: <pid>` 并 **`exit=0`**；臂 15 在 3.5 秒后 `status` → `alive=no health=ok` `exit=1`。即**假成功事后可识破，`start` 那一刻识破不了**。desktop 版判据同构、有同一形状的缺陷。修法要引入归属判据（比对监听者 pid 与 `$PID_FILE`），超出 T-04／T-03 范围，**登记不修**。**T-06 补记**：agent 版的变异臂复现了同一形状（`arm11` 对照：端口无人应答 ⇒ `start` 报 `failed to stay running` `exit=1`，窗口关着；`arm12` 变异：外来进程先占端口、自己的子进程 2 秒后自杀 ⇒ `start` 报 `started: 86699` **`exit=0`**，3 秒后 `status` 读到 `alive=no health=ok` `exit=1`）。⇒ 这条缺陷**不是某一仓的实现瑕疵，是四个 `control.sh` 共享的判据形状**；`artifacts/t06-control-arms.out`。
20. **`git check-ignore -v` 对被 `!` 取反的规则也返回 0**（T-04 实测）。`git check-ignore -v bin/control.sh` 打印 `.gitignore:8:!bin/*.sh` 且 **`exit=0`**，而该文件**并不被忽略**；`-q` 才给出方向（`exit=1`＝不被忽略）。**只看退出码会把「已放开」读成「仍被忽略」**，而本 CHG 的 T-04 验证项恰好写的就是这条命令。判别力足够的三读数（`git add -n`／`git status --porcelain -uall`／`check-ignore -q`，各带阳性对照）落 `evidence/task-04-cloud-layout.md` §5。
21. **`bash` 在 PATH 搜索中遇到 `EACCES` 会跳过该条目继续往后找**（T-04 踩到，只对 `ENOEXEC` 才停）。第二版替身漏了 `chmod +x`，于是 `go` 落到**真实的** devenv go 上：真 go 编译出真 server，真 server 读 `config/app.toml` 的 18080、撞上既存监听者而 panic。**该臂作废**，重做的每一条都先打印 `command -v go` 作判据。与「zsh 不对未加引号的变量做分词」同属**取数工具本身出错**这一类。
22. **同一个端口在 cloud 有三处落点，且有一个脚本把它当错了用途。** 监听地址在 `config/app.toml`；探针地址在 `scripts/local-env.sh:9`；**`scripts/verify-health.sh:5` 另带一份同值的自带兜底**（本次按「不改端口值」不动，登记）。连带：`scripts/verify_m1_integration.py:83` 把 `WT_MEDIA_CLOUD_HTTP_ADDR` 当**监听**地址用（`:153` 取一个空闲端口设进去），但 **cloud 的 Go 侧从不读这个名字**（`*.go` 里 0 命中，与 `local-env.sh:8` 的自述一致）⇒ 探针地址与监听地址必然不同，**该脚本在本仓结构上不可能通过**。它不是六门禁之一（`AGENT-INDEX.md:209-210`），本次只登记、不处置。
23. **cloud `scripts/README.md` 原有两段被本次删除**（不属于「重写为模板」的必然结果，单独留痕）：一是「runtime connection values come from `config/`」那段（与根 `README.md:12-35` 重复，且 `local-env.sh:1-6` 的头部注释也讲同一件事）；二是 `WT_MEDIA_CLOUD_HTTP_ADDR` 那句（与根 `README.md:69` 逐字同义）。**留下的**是「进程入口」那段（`cmd/server` 与 scheduler／worker 的边界），因为它在别的文件里没有等价落点。
24. **T-04 的回指扫描报了假阴性，T-05 复扫时发现并已回改**（判据形态对、**分母错**）。`artifacts/t04-cloud-sweep.out` 的形态 A／C／D 都报「改写后 0」，但取数时本 CHG 新建的 `bin/control.sh`（连同 `scripts/dev/.gitkeep`、`scripts/verify/.gitkeep`）**尚未跟踪**，而三种形态**都没带 `--untracked`** —— `git grep` 与 `git ls-files` 一样只看得见已跟踪/已暂存的文件，于是**被扫集合里没有那个文件**，命中的两条恰好就在它里面。计数验算可复算：`0db02ab` 500 → 三个删除已 `git rm` 进索引得 **497**（＝产物自报的分母）→ 提交后 500（＝497＋那三个新增）。**更正读数：2 条**，均在 `bin/control.sh:4-5` 的表头，是「过去时叙述」（说明该文件合并了哪三个脚本），按「路径判修、叙述判留」**判留不改**。回改落三处（均在 T-05 的提交里）：产物加「更正一」、`evidence/task-04-cloud-layout.md` §8 改为「已作废（假阴性）＋更正读数」、本表 T-04 行与本 CHG `checkpoint.md` 对应行同步。**连带教训**：形态 D 的边界写法证明的是「判别力」，与「分母是否含目标文件」是两件事 —— 前者挡住子串假阳，后者挡不住空集；`--untracked`（且先证明它真的覆盖到了）是新建文件的**必带**参数。

25. **README 里同类的数值字面量不止「端口」这一种，而裁定只写了端口**（T-06 发现，**登记不改**）。`wt-media-agent/README.md:20` 是 `` `WT_MEDIA_BITBROWSER_TIMEOUT_SECONDS`: request timeout, default `5`. `` ——一个**超时默认值**，与 T-06 刚去值的 `:17` 端口行**同属一类**（都是把 `config/agent.toml` 的值复述进 README：该值的落点实测是 `config/agent.toml:31` 的 `timeout_seconds = 5.0`）。D-06 的措辞是「**端口**只在配置文件里呈现」，而本 CHG 写进 `scripts/README.md` 的规则句是「数值型运行参数——**端口、地址、凭据、超时/保留期默认值**」——**规则比裁定宽一档，这个不对称本身在此留痕**。按 §5 开头「范围在 T-00 封闭；后续新发现只登记 §14」，**不改**。（同文件 `:61` 的 `~/.wt-media-agent` 是**历史叙述**「默认值曾在 CHG-056 T-03 改动」，属叙述判留，与第 25 项不同类。）
26. **计划点名 2 处注释回指，实测是 3 处**（T-06）。计划列了 `local_api/server.py:44` 与 `tests/test_local_api_server.py:154`；`tests/test_runtime_config.py:145` 的 docstring（`bin/control.sh redirects *its*`）指向同一件被删事实，是第三处活指针。三处均已改，旧名在三文件 `grep` rc=1。**形状与 T-05 的「计划点名 2 处、实际 3 处」相同**（`:566` 的 `record` 标签）——两次都说明：**按名字点清单会漏掉「同一事实的另一种表述」**，故 T-06 的回指扫描按**四个形态**而非按清单跑。
27. **计划给的端口正则有一处覆盖缺口，实测才发现**（T-06）。`127\.0\.0\.1:[0-9]{2,5}|:[0-9]{4,5}` 的两段都要求数字前有冒号，而 `README.md:48-49` 的真实形态是 `WT_MEDIA_AGENT_HEALTH_PORT=18765`（**无冒号**）——计划的判据按自己的模式**看不到**这一处，改前读数可证（该模式下 `:48/:49` 从未出现）。已补第三种写法 `[0-9]{4,5}`。**教训**：判据的「命中 0」要先证明它有本事命中**改前**的那几条；只报改后 0 而没跑改前，等于没有判别力证据。落 `artifacts/t06-doc-port-literals.out`。
