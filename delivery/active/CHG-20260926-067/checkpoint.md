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

- **T-05 workspace 回指收口**：`verify_m3_acceptance.py` 三处改指 cloud `bin/control.sh`（`:561`／`:566`／`:1738`；计划只点名 2 处，实测 3 处）。**回改 T-04 的假阴性读数**（§14 第 24 项）：`t04-cloud-sweep.out` 加「更正一」、T-04 证据 §8 改为「已作废（假阴性）＋更正读数」、`change.md`／`checkpoint.md` 同步；预算在文件内部重新分配，收在 9211/9216。`foreign` 清单逐条重查落点后结论不变。`bin/control.sh`／`test-control.sh` 系 T-01 已建，本 Task 只复核。**跨仓红窗自此关闭。** 详见 `evidence/task-05-workspace-repoint.md`。
- **T-06 agent 脚本层分层**：`bin/control.sh`（合并三脚本，`alive`／`health` 分列）；删 `start-health.sh`／`stop-health.sh`／`health.sh`（`scripts/` 分母 10 → 7）；三处 README 端口字面量去值、命令行改指 `bin/control.sh`；**三处**注释回指（计划点名 2 处，实测 3 处）。agent **`aa95332`**（13 文件，+221/−124）。12 臂落 `artifacts/t06-control-arms.out`。**本 Task 无红窗**——`scripts/verify-health.sh` 自内联启停，不调用被删的三个。详见 `evidence/task-06-agent-layout.md`。

## Current

无。T-06 已完成。四仓的运行仓改动**全部落地**（workspace／cloud／agent／desktop 各一次提交），下一步 T-07 只动 workspace 的收尾记录。

## Next

1. **T-07**（workspace 收尾）：归档、LEDGER 同步、快照 `--no-active`、两遍指针扫描、四仓对账、AC 矩阵签字、DONE Gate。

### 对后续 Task 直接适用的硬约束（本 CHG 已踩定）

- **建 `bin/control.sh`**：不得承载端口字面量；`status` 的 `exit=1` 语义统一为「不是经本仓 harness 起的」而非「服务挂了」，且 `alive` 与 `health` **分开打印**；只分派动词。（§14 第 10、11 项）
- **不把地址写进脚本，是「读配置」而不是「抄配置」**：`node -p`／`jq` 对**缺键**返回字符串 `undefined` 而 `exit=0`，空判断抓不住它。取值表达式必须对缺键返回空，并先判配置文件在不在。（§14 第 15 项，T-03 实测踩到）
- **写记录**：`change.md` 的 H1 标题里不得出现 `|`；LEDGER 表行必须是 `| CHG-… | 标题 | 状态 | 仓库 |` 四格、无反引号无链接。（§14 第 8 项）
- **报「0 命中／已收口」**：做阳性对照、报出分母，锚取**不变的基线**而非 `HEAD`；**枚举输入形态**——T-03 实测「端口值」有三种写法，只有其中一种抓得到 `devUrl 5174` 这种散文形态。**正文扫描用 `git grep -F`**：`-E` 里的 `\b` 会静默匹配不到，名字里的 `.` 在正则下是通配符（`build.sh` 命中过 `build_sha256`）；**新建文件必须带 `--untracked` 并证明它覆盖到了**——T-04 就栽在这：分母少了本 CHG 新建的三个未跟踪文件，而两条命中恰在其中（§14 第 24 项，机制已在合成仓复现）。**「判别力」与「分母」是两件事**：形态 D 的边界写法挡得住子串假阳，挡不住空集。**扫描产物自己会进分母**：首版 T-05 产物把原始 dump 写进被扫树，既把自己算进 205 行、又毒化了反向对照 ⇒ 报数时把自指单列，优先报与轮次无关的子集。**判据的「改后 0」要配「改前非 0」**：T-06 实测计划给的端口正则**抓不到** `VAR=18765` 形态（两段都要求数字前有冒号），改前读数可证——只报改后 0、不跑改前那几条，等于没有判别力证据（§14 第 27 项）。
- **按名字点清单会漏项**：T-05（计划 2 处 / 实测 3 处）与 T-06（计划 2 处注释 / 实测 3 处）各栽一次，两次漏的都是「同一事实的另一种表述」⇒ 扫描按**形态**跑，不按清单跑（§14 第 26 项）。
- **判据「绿」不等于那件事成立**：needle 是对文本的字符串检查（§14 第 12 项）。改判据前先问它实际保证的是什么。
- **六门禁的清单只在 `AGENT-INDEX.md:199-210`**：第六个是 `verify_m2_acceptance.py`，**不是** `verify_m1_integration.py`（后者与 `verify_m3_acceptance.py` 同属「需真实运行实例、不属上表」）。T-04 首轮写错过一次。
- **`git check-ignore` 的退出码不表示方向**：`-v` 对被 `!` 取反的规则也 `exit=0`。判「是否被忽略」用 `-q`，或用 `git add -n`／`git status --porcelain -uall` 三读数并各带阳性对照。（§14 第 20 项）
- **`start` 的探针不认领它探到的是谁**：端口上有别人的进程在答时，`start` 可能报 `exit=0` 而它起的那个人已经死了。**三个仓（cloud／workspace／agent）各有一次实测，四仓的 `control.sh` 共享这一判据形状，本次不修**；写记录时不得把 `start` 的 `exit=0` 当作「起来了」。（§14 第 19 项）
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
| cloud 回指扫描（T-04 原读数**已于 T-05 作废**） | 改写前三个名字各命中 1（全在 `README.md:64-66`）；改写后四种写法报 0，但该 0 是**假阴性**——分母 497 不含新建且未跟踪的 `bin/control.sh`，四形态又都没带 `--untracked`。**更正读数 2 条**（`bin/control.sh:4-5` 表头叙述，判留）。验算 500−3=497、497+3=500（§14 第 24 项，`artifacts/t04-cloud-sweep.out` 文末「更正一」） |
| `git check-ignore` 陷阱（T-04） | `-v bin/control.sh` 打印 `!bin/*.sh` 且 **`exit=0`**（文件并不被忽略）；`-q` 才 `exit=1`；对照 `bin/wt-media-cloud` 两命令一致报被忽略（§14 第 20 项） |
| 六门禁 + 套件（T-04 记录写完后复跑） | 见 `artifacts/t04-gate-final.out`——**不在此内联**；首轮（记录未写完时）那份含一次把第六个门禁写错的自造红，落 `t04-gate-after.out` |
| desktop 文档端口值（T-03，三种写法） | 改前：写法 1 命中 0／写法 2 命中 **5**／写法 3 命中 0；改后写法 2 **5 → 3**（余下 3 条是契约版本号，非运行参数）；阳性对照：同模式在 `tauri.conf.json` 命中（`artifacts/t03-doc-port-literals.out`） |
| workspace 回指扫描（T-05，活体面＝`:!delivery`） | 逐形态 **8 → 5 行**，差 **3** 与三行编辑逐行对上；余 5 行全在 `release-matrix.yaml` 的 `verification:` 历史证据行（判留）⇒ **可解析指针 0**。cloud 同口径 2 行（`bin/control.sh:4-5` 叙述）。阳性对照 `bin/control\.sh` 23 文件/124 行 ＋ cloud 3 文件；反向对照排除记录产物后 0（`artifacts/t05-pointer-sweep.out`） |
| `bin/control.sh`／`test-control.sh`（T-05 复核） | 两个 `bash -n` `exit=0`；`test-control.sh` 全跑 `exit=0`（聚合 PASS：`usage, dispatch, status wiring, and no-port-literal`）；`bin/control.sh` 端口字面量 0 命中（`artifacts/t05-test-control.out`） |
| T-04 假阴性更正（T-05） | 复扫 cloud 得 **2** 条（`bin/control.sh:4-5`，叙述判留）；验算 500 − 3 已入索引的删除 = **497** = 产物自报分母、497 + 3 新增 = 500；机制在合成仓复现（同内容一跟踪一未跟踪，默认 `git grep` 只命中前者）|
| 六门禁 + 套件（T-05 记录写完后复跑） | 见 `artifacts/t05-gate-final.out`——**不在此内联** |
| agent `scripts/` 分母（T-06） | **10 → 7**（`git ls-tree --name-only HEAD scripts/` = 10；`git ls-files scripts/` = 7） |
| agent `bin/control.sh`（T-06） | `bash -n`／`sh -n` 均 `exit=0`；**12 臂**全按预期：10 条功能臂对**真实健康台**跑（`status` 运行中 `alive=yes health=ok` `exit=0`／停止后 `alive=no health=down` `exit=1`、`restart` pid 86409→86446、重复 start 幂等、未知动词 `exit=2`）；2 条变异臂复现 §14 第 19 项 ⇒ **该危害三仓共有**（`artifacts/t06-control-arms.out`） |
| agent 端口字面量（T-06，三形态） | 分母 57／17／16 行。改前：冒号两形态各命中 **2**（`:17` 的 54345、`:16` 的 18080）、裸数值形态命中 **7**；改后：冒号两形态 **0**、裸数值形态 **3**（全是同文件的历史 CHG 编号，非端口）。阳性对照：副本里放回两个数字 ⇒ 冒号形态 1、裸形态 5。**计划的模式抓不到 `VAR=18765` 形态（无冒号）**（`artifacts/t06-doc-port-literals.out`，§14 第 27 项） |
| agent 回指扫描（T-06，四形态） | 带边界精确形态：只读已跟踪 **0**、`--untracked` **2** 行（全在 `bin/control.sh:4-5` 表头的过去时叙述，判留）⇒ **可解析活指针 = 0**；带目录路径形态去重后同这 2 行；裸 `health\.sh` 形态 **10** 行全是子串重叠（8 行在幸存的 `verify-health.sh` 上）。阳性对照同命令同集合 `bin/control.sh` **6 文件／12 行**，反向对照 0。**当场复现 §14 第 24 项**：同一命令只差 `--untracked`，读数 0 → 2（`artifacts/t06-pointer-sweep.out`） |
| agent 套件（T-06，最后一次改动之后） | `PYTHONPATH=src .venv/bin/python -B -X pycache_prefix=/tmp/pyc-none -m unittest discover -s tests -q` → `Ran 409 tests in 11.590s` / `OK`，rc=0，与激活前 `Ran 409 tests` / `OK` **逐字相同**。**归因声明**：工作树带一处开工前就存在的 `AGENT-INDEX.md` 未提交改动，未触碰 ⇒ 这是「脏工作树上的绿」 |
