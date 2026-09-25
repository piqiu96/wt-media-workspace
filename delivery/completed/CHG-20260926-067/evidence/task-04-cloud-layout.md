# T-04 证据：cloud 脚本层分层

- CHG: `CHG-20260926-067`
- Task: T-04（`change.md` §8）
- 日期: 2026-09-26
- 锚: 开工前 cloud HEAD `0db02ab`
- 提交: `wt-media-cloud` **`e2ba4d8`**（`feat(chg-067): T-04 …`，10 files changed, +192/−86）；workspace 侧记录随本 Task 第二个提交落地

> 下文所有「T-04 改动在工作树里」的措辞都是**取数时**的事实——读数都取在该提交**之前**。

## 1. 改动文件

| 文件 | 改动 |
|---|---|
| `bin/control.sh` | **新建**（§2），合并 `scripts/start.sh`＋`stop.sh`＋`health.sh` |
| `scripts/{start,stop,health}.sh` | 删除（`git rm`） |
| `.gitignore` | `bin/` → `bin/*` ＋ `!bin/*.sh`（§5） |
| `scripts/README.md` | 重写为分类表＋落位规则＋指针行，补上缺失的 `local-env.sh` 行 |
| `README.md` | Verification 段的 foreground 三行命令块 → `bin/control.sh` |
| `DIRECTORY_MAP.md` | 公共表新增 `bin/` 行；`scripts/` 行改指 `scripts/README.md` |
| `scripts/dev/`、`scripts/verify/` | 新建，各一枚 `.gitkeep` |

**唯一迁移集就是这三个**；`verify-health.sh`（验收）、`local-env.sh`（共享库）、
`bootstrap.sh`／`build.sh`／`migrate.sh`／`test.sh`（开发）原地不动。

## 2. `bin/control.sh`

动词 `start|stop|restart|status|help`，与 workspace／desktop 同形状。

- **与旧脚本的差异只有两条**：新增 `status`；多了 `restart`。`start` 的构建命令、PID／LOG／BINARY
  三个落点、`GOCACHE`／`GOPATH` 兜底、50×0.1s 轮询、失败时打印日志尾部——逐行照搬旧 `start.sh`。
- **没有端口字面量**：探针地址读 `WT_MEDIA_CLOUD_HTTP_ADDR`，落点是 `scripts/local-env.sh:9`（旧 `start.sh:25`
  与 `health.sh:4` 各自还带一份 `${…:-127.0.0.1:18080}` 兜底，是同一值的第二、三个落点，本次**不予复制**；
  见 §14）。机检 `grep -nE '\b[0-9]{4,5}\b' bin/control.sh` 命中 **0**，阳性对照同模式在
  `scripts/local-env.sh` 命中 1 行。
- **`alive`／`health` 是两个读数**：前者问「PID 文件里那个人还在吗」（＝是否经本 harness 起），
  后者问「有没有东西在答」。`exit=0` 要求两者同时成立。

## 3. 四个动词的读数怎么取的

`artifacts/t04-cloud-control-arms.out` 共 15 臂（另有两段作废的读数，见 §6）：

- **真实树（臂 1–3）**：`status` → `cloud: pid=- alive=no health=ok url=http://…/healthz`，`exit=1`；
  `stop` → `exit=0`；`status` → 同前，`exit=1`。这个 `alive=no health=ok` 不是摆拍：读数时
  `.cache/wt-media-cloud.pid` 里是**已死的 pid 13457**（`kill -0` 报 `no such process`），而 18080 上另有
  一个**本 CHG 开工前就在**的监听者（pid 54420）在答两个端点 —— `alive` 与 `health` **取到了相反值**。
  **如实记**：臂 1 与臂 3 的打印行逐字相同——`stop` 对**过期** PID 文件的效果在随后的 `status` 里看不见，
  差别只在 `$PID_FILE` 的存废上；`status` 分不清「从未起过」与「起过后死了」，属设计使然。
- **隔离全套（臂 4–12）**：`WT_MEDIA_CLOUD_{PID,LOG,BINARY}_FILE` 三个覆盖点改指 `/private/tmp/t04`、
  `_HTTP_ADDR` 改指空闲端口、`PATH` 前置模拟 `go`（只实现 `go build -o <f> ./cmd/server`，产出物在两个探针
  路径上都答 200）。**仓内端口值一字未动。** 读数：`start` `exit=0` → 再 `start` 得 `already running` `exit=0`
  → `status` `alive=yes health=ok` `exit=0` → `restart` `exit=0`（新 pid）→ `status` `exit=0` → `stop` `exit=0`
  （`lsof` 上已无监听）→ 再 `stop` 得 `not running` `exit=0` → `status` `exit=1`（`alive=no health=down`）
  → 未知动词 `exit=2` → `help` `exit=0`。**每个动词都跑到了 0 与非 0 两侧。**

## 4. 探针归属：一个两仓共有的潜在缺陷（臂 13–15 实测）

`start` 的成功判据是「进程还活着 **且** 探针通」，但探针**不认领**它探到的是谁：

- 臂 13（对照）：替身产出物立刻退出 ⇒ `failed to stay running`，`exit=1`，PID 文件被清。
- 臂 14（变异）：先让一个**外部**进程占住该端口（不由 `control.sh` 起，故无 PID 文件），再让替身 3 秒后自杀
  ⇒ `started: <pid>`，**`exit=0`**。这就是假成功。
- 臂 15：3.5 秒后 `status` → `alive=no health=ok`，`exit=1`。**事后可识破，`start` 那一刻识破不了。**

**desktop 的 `bin/control.sh` 判据同构**，故这是两仓共有的。本次**不修**（修法要引入归属
判据，超出 T-04 范围），登记 `change.md` §14。

## 5. `.gitignore` 与 `git check-ignore` 的陷阱

`.gitignore:3` 原是 `bin/`（Go 生态的编译产物目录），脚本放进去会静默不进版本控制。改为 `bin/*` ＋
`!bin/*.sh`——**必须点名内容而不是写 `bin/`**：`!` 无法反向包含已被排除的*目录*下的内容。
判据用三个判别力不同的读数（对照 `bin/wt-media-cloud`）：

| 命令 | `bin/control.sh` | 对照 |
|---|---|---|
| `git add -n <path>` | `add 'bin/control.sh'` | 不 add |
| `git status --porcelain -uall` | `?? bin/control.sh` | 不出现 |
| `git check-ignore -q <path>` | `exit=1`（＝不被忽略） | `exit=0` |

**陷阱**：`git check-ignore -v bin/control.sh` **打印 `.gitignore:8:!bin/*.sh` 且 `exit=0`**，而该文件
**并不被忽略**——`-v` 只表示「有规则命中」，包括被 `!` 取反的那条。方向要从规则文本里的 `!` 读，或改用 `-q`。

## 6. 本次写坏的读数（四处，留在产物里）

1. **替换件是错的**：隔离臂第一版的替身用 `python3 -m http.server`，`/healthz` 落在不存在的文件上答 **404** ⇒
   `curl --fail` 判失败，`start` 报 `did not become healthy`。非本脚本缺陷；该段仍保留，因为它证明**探针不会被
   404 骗过**（要求 2xx，不是「端口上有东西答话」），且顺手取到 `alive=yes health=down`。
2. **`bash` 在 PATH 搜索中遇到 EACCES 会跳过该条目继续往后找**：第二次建替身时漏了 `chmod +x`，于是 `go`
   落到**真实的** devenv go 上：真 go 编译出真 server，真 server 读 `config/app.toml` 的 18080、撞上既存
   监听者而 panic（产物里留着）。该臂作废；重做的臂每条先打印 `command -v go`。
3. **门禁清单写错**：首轮把 `verify_m1_integration.py` 当成第六个门禁（第六个实为 `verify_m2_acceptance.py`，
   清单唯一落点 `AGENT-INDEX.md:199-210`；`:209-210` 明写前者「不属上表」）。已按该节重跑。
4. **zsh 不对未加引号的变量做分词**：`out=$($PY …)` ⇒ 全部 `exit=127`。改用 `"$@"`。与 T-03 的
   `git check-ignore $args` 是同一坑。

## 7. 本次没有跑什么（如实记）

- **真实的 `go run ./cmd/server` 未作为本 Task 的判据跑**：18080 被一个开工前就在的进程占着，`start` 路径
  只在 `PATH` 前置的模拟 `go` 下跑（§3）。
- **`verify_m1_integration.py` 在本环境是红的**，且它**不是六门禁之一**（`AGENT-INDEX.md:209-210`）：`:153`
  `free_port()` 取的端口经 `:83` 设进 `WT_MEDIA_CLOUD_HTTP_ADDR`，但 cloud 的 Go 侧不读它（该名在 `*.go` 0 命中），
  服务端只从 `config/app.toml` 取监听地址 ⇒ 即使 18080 空闲，探针与监听也不同址。红因与本 CHG 无关，落
  `artifacts/t04-gate-after.out` 末段。
- **cloud 的 `scripts/test.sh`（Go＋Vitest）未跑**：T-04 验证项不含它，且需 npm 依赖。

## 8. 门禁与回指扫描

- `artifacts/t04-gate-after.out`：六门禁全 `exit=0`、`Ran 101 tests`／`OK`、`skills` 通过。
- **回指扫描**落 `artifacts/t04-cloud-sweep.out`；分母 `git ls-files` = **497**（**有缺口，见下**）。
  - **改写前**：三个名字各命中 **1**，全在 `README.md:64-66`。这组读数**现在取不到了**——`git grep` 读工作树
    内容，改写落地后旧文本已不存在，故产物标为「原样转录」。
  - **改写后：已作废（假阴性）**。四种写法都报 0，但取数时本 CHG 新建的 `bin/control.sh` 尚未跟踪、四种写法
    又都没带 `--untracked`，**被扫集合里没有那个文件**（验算：500 − 3 个已入索引的删除 = 497 = 产物自报的
    分母，497 + 3 个新增 = 提交后的 500）。**更正读数：2 条**，在 `bin/control.sh:4-5` 的表头，属叙述，判留
    ——详见 `t05-pointer-sweep.out` 与 §14 第 24 项。形态 B 裸名的 3 条子串假阳与形态 D 的边界写法对照不受影响。
  - 阳性对照 `local-env.sh` 命中 2 文件；反向对照（从未存在过的名字）命中 0。
- **`verify-health.sh` 不调用被删的三个脚本**：它自内联 `go run ./cmd/server` ＋ `trap` ＋ 探针循环 ⇒
  迁移自足、**无红窗**。
- **跨仓**：workspace 只两处引到这三个名字，都非本 Task 处置——`config/release-matrix.yaml:120`（历史证据行，
  按计划不改）与 `scripts/verify_m3_acceptance.py:561,1738`（归 T-05）。**T-04 提交后、T-05 提交前即登记的跨仓红窗。**
