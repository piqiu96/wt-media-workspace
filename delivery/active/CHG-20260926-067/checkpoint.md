# Checkpoint: CHG-20260926-067

- CHG: `CHG-20260926-067`（脚本层分层——四仓 bin 目录、scripts/dev 与 scripts/verify、每仓 scripts/README.md）
- Level: S
- Updated: 2026-09-26

## 状态

`IMPLEMENTING`（2026-09-26 激活；跨四仓）

State words come from §3 of `delivery/MASTER_IMPLEMENTATION_PLAN.md`. A record in
`delivery/active/` may only be `IMPLEMENTING` or `VERIFYING`.

## Completed

- **T-00 激活**：`delivery/active/CHG-20260926-067/` 三件齐备（`change.md`／`checkpoint.md`／`evidence/`）；§5 范围封闭（7 条 Add／11 条 Modify／4 条 Delete／9 条 Explicitly Not Doing）；LEDGER 表行；快照 `--change CHG-20260926-067`；四仓基线落 `artifacts/t00-repo-baseline.out`；脚本层清点与 `bin/` 忽略探针落 `artifacts/t00-script-inventory.out`；六门禁与套件两臂落 `artifacts/t00-gate-before.out`／`t00-gate-after.out`；`MASTER` §3 读数列按实测刷新三项并落 `artifacts/t00-status-words{,-after}.out`（量法**直接 import 门禁自己的 `status_word()`**）。详见 `evidence/task-00-activation.md`。
- **T-00 附带一条自造的红**：LEDGER 表行首版写成 `| [CHG-…](…) |` 且 H1 标题含 `|`，触发三条门禁红 + 套件 1 failure。两条约束（`LEDGER_ROW_RE` 要求 `|` 后紧跟 `CHG-`；`expected_row` 的标题取自 H1，故 H1 不得含 `|`）已登记 §14 第 8 项。
- **T-01 workspace 脚本层分层**：`scripts/local-control.sh` → `bin/control.sh`（加 `restart`／`status`）；`scripts/test-local-control.sh` → `scripts/test-control.sh`（判据 1→4 条）；`scripts/dev/`＋`scripts/verify/`（各 `.gitkeep`）；`scripts/README.md` 首建；`AGENT-INDEX.md` §3 加 `bin/` 行；`verify_delivery_governance.py` 扫描面改 `rglob`（两臂对照落 `artifacts/t01-scan-surface-arm-{a,b}.out`）；`m2b_local_acceptance.py` 新增 `status` 动词。详见 `evidence/task-01-workspace-layout.md`。

- **T-02 M0 门禁前置**：`verify_m0_config.py` 的 desktop needle 元组 7 → 3 条（docstring 同步）；`verify_m0_local.sh:39-45` desktop 块 4 → 1 条。四臂对照证明收窄承重（臂 3：旧 tuple × T-03 终态 workflow = 3 处红）且前瞻安全（臂 2：终态 × 新 tuple = 绿）。顺带量到两条改写 T-03 决策的读数：`npm run lint` 自 `7aabb1a` 起就坏而 needle 一直绿；两个 shell 套件都要 `node` 当 JSON 读取器 ⇒ `setup-node` 必须保留。详见 `evidence/task-02-m0-gate-preamble.md`。
- **T-03 desktop 脚本层分层**：删 11 个死脚本（`scripts/` 分母 20 → 9）；`m0-desktop.yml` → Rust-only（`setup-node` 保留、去掉 `cache:`）；`scripts/test.sh` 重写（缺 sidecar 时写自报家门的占位符）；新建 `bin/control.sh`（`cargo tauri dev` 的 `start|stop|restart|status`，地址读 `tauri.conf.json` 的 `devUrl`，PID／日志落 `.runtime/`）；`.gitignore` 加 `.runtime/`；`scripts/dev/`＋`scripts/verify/`；`README.md`／`DIRECTORY_MAP.md`／`scripts/README.md` 重写（含两处 `devUrl` 值去值留名）。详见 `evidence/task-03-desktop-layout.md`。
- **T-04 cloud 脚本层分层**：`bin/control.sh`（合并三脚本，`alive`／`health` 分列）；`.gitignore` `bin/` → `bin/*` ＋ `!bin/*.sh`；删三脚本；`scripts/README.md` 重写并补 `local-env.sh` 行；`README.md`／`DIRECTORY_MAP.md` 改指。cloud `e2ba4d8`。15 臂落 `artifacts/t04-cloud-control-arms.out`。**一处自己写坏的读数留痕**（首轮把第六个门禁错写成 `verify_m1_integration.py`）。详见 `evidence/task-04-cloud-layout.md`。

## Current

无。T-04 已完成，下一步是 T-05（workspace），且**必须紧接**——跨仓红窗此刻是开着的。

## Next

1. **T-05 必须紧接 T-04**：workspace 的 `verify_m3_acceptance.py:561`／`:1738` 与 `:414-421` 回指 cloud `bin/control.sh`。这是本 CHG **唯一的跨仓红窗**，中间不插任何工作。
2. **T-06**（agent）→ **T-07**（收尾）。

### 对后续 Task 直接适用的硬约束（本 CHG 已踩定）

- **建 `bin/control.sh`**：不得承载端口字面量；`status` 的 `exit=1` 语义统一为「不是经本仓 harness 起的」而非「服务挂了」，且 `alive` 与 `health` **分开打印**；只分派动词。（§14 第 10、11 项）
- **不把地址写进脚本，是「读配置」而不是「抄配置」**：`node -p`／`jq` 对**缺键**返回字符串 `undefined` 而 `exit=0`，空判断抓不住它。取值表达式必须对缺键返回空，并先判配置文件在不在。（§14 第 15 项，T-03 实测踩到）
- **写记录**：`change.md` 的 H1 标题里不得出现 `|`；LEDGER 表行必须是 `| CHG-… | 标题 | 状态 | 仓库 |` 四格、无反引号无链接。（§14 第 8 项）
- **报「0 命中／已收口」**：做阳性对照、报出分母，锚取**不变的基线**而非 `HEAD`；**枚举输入形态**——T-03 实测「端口值」有三种写法，只有其中一种抓得到 `devUrl 5174` 这种散文形态。**正文扫描用 `git grep -F`**：`-E` 里的 `\b` 会静默匹配不到，名字里的 `.` 在正则下是通配符（`build.sh` 命中过 `build_sha256`）；新文件是未跟踪的，要带 `--untracked`（并证明它真的覆盖到了）。
- **判据「绿」不等于那件事成立**：needle 是对文本的字符串检查（§14 第 12 项）。改判据前先问它实际保证的是什么。
- **六门禁的清单只在 `AGENT-INDEX.md:199-210`**：第六个是 `verify_m2_acceptance.py`，**不是** `verify_m1_integration.py`（后者与 `verify_m3_acceptance.py` 同属「需真实运行实例、不属上表」）。T-04 首轮写错过一次。
- **`git check-ignore` 的退出码不表示方向**：`-v` 对被 `!` 取反的规则也 `exit=0`。判「是否被忽略」用 `-q`，或用 `git add -n`／`git status --porcelain -uall` 三读数并各带阳性对照。（§14 第 20 项）
- **`start` 的探针不认领它探到的是谁**：端口上有别人的进程在答时，`start` 可能报 `exit=0` 而它起的那个人已经死了。**两仓共有，本次不修**；写记录时不得把 `start` 的 `exit=0` 当作「起来了」。（§14 第 19 项）
- **替身/工具本身出错要有判据**：`PATH` 前置替身时必须先 `command -v <cmd>` 断言落点（`bash` 遇 `EACCES` 会跳过该条目继续往后找，静默落到真程序上）；被测对象的替身先自检它自己的前提（如「探针路径答 200」）。

## Blocked

- None.

## Recent verification

| 判据 | 读数 |
|---|---|
| 六门禁（激活前） | 六个全 `exit=0`；`sync_skills.py check` `exit=0`；见 `artifacts/t00-gate-before.out` |
| `unittest discover -s tests -q`（激活前） | `Ran 100 tests` / `OK` |
| 四仓 HEAD（激活前） | workspace `71fd32f`／cloud `0db02ab`／agent `6d740fc`／desktop `7c1b0ad`（`artifacts/t00-repo-baseline.out`） |
| 四仓工作树（激活前） | workspace 仅本 CHG 新目录；cloud 仅未跟踪 `dump.rdb`；agent ` M AGENT-INDEX.md`；desktop 干净——**后两条先于本 CHG 存在，不触碰** |
| 脚本层清点（分母＝`git ls-files scripts`） | workspace **18**／cloud **10**／agent **10**／desktop **20**；四仓 `bin/` 均不存在（`artifacts/t00-script-inventory.out`） |
| `bin/` 忽略探针 | **只有 cloud** 报被 `.gitignore:3` 忽略；另外三仓报不被忽略（探针能报出相反结论 ⇒ 否定读数可信） |
| `MASTER` §3 读数列 vs 实测 | **逐词相等**：活列 19／归档列 33／归档 `DONE` 31／分母 41；闭合式 33＋2＋2＋4＝41 ✓（`artifacts/t00-status-words.out`） |
| 里程碑覆盖（分母 5 篇，README 除外） | 脚本层关键词 **0 命中** ⇒ 无可锚里程碑，取 `Level: S` |
| 六门禁 + 套件（激活后） | 六个全 `exit=0`；`sync_skills.py check` `exit=0`；`Ran 100 / OK`（`artifacts/t00-gate-after.out`） |
| LEDGER 表行合 `validate_active_change` | 首版**不合**（表行形态 + H1 含 `|`）→ 三条门禁红 + 1 failure；改后**合**（§14 第 8 项） |
| 本 Task 记录体量 | 见 `artifacts/t00-record-size.out`——**不在此内联**，本表的字节数会随写入而改变 |
| 归档只读扫描面（T-01 两臂） | 臂 A（`glob`）：分母 12／`0 write(s)`／探针未点名；臂 B（`rglob`）：分母 13／`1 write(s)`／点名 `scripts/verify/probe-archive-write.py:8`。探针删除后分母回 12（`artifacts/t01-scan-surface-arm-{a,b}.out`） |
| `test-control.sh`（T-01） | 四条判据全过；**五处变异全红**且各自报出是哪一条（`artifacts/t01-test-control-mutations.out`） |
| `bin/control.sh status`（T-01 实读） | `cloud: … alive=no health=ok`／`agent: … alive=no health=ok`／`exit=1`；独立探针 `lsof` 证实 18080／8765 确在监听（`artifacts/t01-control-status.out`） |
| 失效指针扫描（T-01，分母 902） | 三种写法：`scripts/local-control\.sh` 命中 1、裸名命中 2、`test-local-control` 命中 **0**；**阳性对照** `bin/control\.sh` 命中 7 ⇒ 否定读数非空转；两处残留均在 `docs/superpowers/`，判留并登记 §14 第 9 项 |
| 六门禁 + 套件 + `sync_skills check`（T-01 后） | 六个全 `exit=0`；`sync_skills check` `exit=0`；`Ran 101 / OK`（激活前 100，+1 为本 Task 新增用例）（`artifacts/t01-gate-after.out`） |
| 六门禁 + 套件（T-01 记录写完后复跑） | 见 `artifacts/t01-gate-final.out`——**不在此内联** |
| CI needle 四臂（T-02） | 臂 0 现状×新 tuple `errors: []`；臂 1 变异点名 `missing 'scripts/test.sh'`；臂 2 **T-03 终态×新 tuple `errors: []`**；臂 3 旧 tuple×终态 **3 处红**（`scripts/bootstrap.sh`／`npm run lint`／`scripts/build.sh`）（`artifacts/t02-m0-gate-arms.out` §A） |
| desktop 块两臂（T-02） | 旧块 `exit=1`（停在 `npm ci`）；单跑 `npm run lint` `exit=254`；新块 `exit=0` ＋ `running 377 tests`／`372 passed; 0 failed; 5 ignored` ＋ 2 个 shell 套件各 `exit=0`（同文件 §B） |
| desktop 套件的读数缺口 | 2 个 shell 套件里**只有 1 个自带计数**（`release-versions` 20 passed）；`package-release-macos.test.sh` 静默通过，唯一证据是退出码 |
| 六门禁 + 套件（T-02 记录写完后复跑） | 见 `artifacts/t02-gate-final.out`——**不在此内联** |
| desktop `scripts/` 分母（T-03） | **20 → 9**；11 个被删名字各命中 **0**（分母 109 个已跟踪文件，`git grep -F --untracked`），阳性对照 `release-versions.sh` 10 文件／`test.sh` 8，反向对照 0（`artifacts/t03-deleted-name-sweep.out`） |
| desktop `bin/control.sh`（T-03） | `bash -n` `exit=0`；端口字面量 **0 命中**；十臂 ＋ 六处变异全按预期（`artifacts/t03-desktop-control-arms.out`）。**含一处自己踩到并修掉的缺陷**：`node -p` 对缺键打印 `undefined` 而 `exit=0`，首版把它当地址打了出来（§14 第 15 项） |
| desktop `scripts/test.sh`（T-03，最后一次改动之后） | `exit=0`；`372 passed; 0 failed; 5 ignored` ＋ `release-versions 20 passed`；14.19s（`target/` 是热的，非冷启动）（`artifacts/t03-desktop-test-sh.out`） |
| desktop 无 sidecar 的克隆（T-03） | 占位分支生效（`no sidecar at …; writing a placeholder`），读数与有 sidecar 时逐字相同：`372 passed; 0 failed; 5 ignored` ＋ `20 passed`，`exit=0`；占位符被 `.gitignore:10` 挡住（`artifacts/t03-clean-clone.out`） |
| cloud `bin/control.sh`（T-04） | 真实树 `status` → `alive=no health=ok` `exit=1`（PID 文件里是**已死的 13457**，18080 上另有开工前就在的监听者）＋ `stop` `exit=0`；隔离 9 臂逐动词跑到 0 与非 0 两侧；`bash -n` `exit=0`；端口字面量 0 命中（`artifacts/t04-cloud-control-arms.out`） |
| cloud `start` 的探针归属（T-04 变异臂） | 外部进程占端口 ＋ 替身 3 秒后自杀 ⇒ `start` **`exit=0` 假成功**；3.5 秒后 `status` → `alive=no health=ok` `exit=1`。desktop 同构（§14 第 19 项） |
| cloud 回指扫描（T-04，分母 497） | 改写前三个名字各命中 1（全在 `README.md:64-66`）→ 改写后四种写法各 **0**；形态 B 裸名有 3 条 `verify-health.sh` 子串**假阳**故作废；阳性对照 `local-env.sh` 2 文件、反向对照 0（`artifacts/t04-cloud-sweep.out`） |
| `git check-ignore` 陷阱（T-04） | `-v bin/control.sh` 打印 `!bin/*.sh` 且 **`exit=0`**（文件并不被忽略）；`-q` 才 `exit=1`；对照 `bin/wt-media-cloud` 两命令一致报被忽略（§14 第 20 项） |
| 六门禁 + 套件（T-04 记录写完后复跑） | 见 `artifacts/t04-gate-final.out`——**不在此内联**；首轮（记录未写完时）那份含一次把第六个门禁写错的自造红，落 `t04-gate-after.out` |
| desktop 文档端口值（T-03，三种写法） | 改前：写法 1 命中 0／写法 2 命中 **5**／写法 3 命中 0；改后写法 2 **5 → 3**（余下 3 条是契约版本号，非运行参数）；阳性对照：同模式在 `tauri.conf.json` 命中（`artifacts/t03-doc-port-literals.out`） |
