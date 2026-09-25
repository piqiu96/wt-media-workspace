# T-03 证据：desktop 脚本层分层

- CHG: `CHG-20260926-067`
- Task: T-03（`change.md` §8）
- 日期: 2026-09-26
- 锚: 开工前 desktop HEAD `7c1b0ad`
- 提交: `wt-media-desktop` **`9ba5486`**（`feat(chg-067): T-03 …`，20 files changed, +277/−346）；本文件的 workspace 侧记录随本 Task 的第二个提交落地

> 下文所有「T-03 改动在工作树里」的措辞都是**取数时**的事实——读数都取在 `9ba5486` **之前**。

## 1. 改动文件

| 文件 | 改动 |
|---|---|
| `scripts/` 下 11 个文件 | 删除（`git rm`）：`bootstrap.sh`、`build.sh`、`dev.sh`、`health.sh`、`health-check.mjs`、`health-dev.mjs`、`start.sh`、`stop.sh`、`start-dev.mjs`、`stop-dev.mjs`、`verify-real-scripts.mjs` |
| `.github/workflows/m0-desktop.yml` | 重写为 Rust-only：`checkout` → `setup-node`（保留，无 `cache:`／`cache-dependency-path:`）→ `dtolnay/rust-toolchain@stable` → `scripts/test.sh` |
| `scripts/test.sh` | 重写：缺 sidecar 时写一个自报家门的占位符（§5） |
| `bin/control.sh` | **新建**（§3） |
| `.gitignore` | 加 `.runtime/`（`bin/control.sh` 的 PID 与日志落点） |
| `scripts/dev/`、`scripts/verify/` | 新建，各一枚 `.gitkeep` |
| `scripts/README.md` | 重写为分类表＋落位规则＋指针行 |
| `README.md` | Bootstrap 段与 Verification 段；删掉 CHG-056 的「npm/vite 不一致」注记（该不一致已由本 Task 消除） |
| `DIRECTORY_MAP.md` | 四、更新与跨平台打包 的脚本行重算；两处 `devUrl` 的值去值留名（§6） |

## 2. 十一个名字「零引用」是怎么量的

命令 `git grep -F --untracked -l -- <name>`，逐名一遍，落 `artifacts/t03-deleted-name-sweep.out`。

- **分母**：`git ls-files` = **109** 个已跟踪文件（另含未跟踪但未被忽略者）。
- **读数**：11 个名字**各命中 0**。
- **`-F` 不是选项问题**：早一轮用 `-E '\b(...)\b'` 扫，每个名字都返回 0——**阳性对照**（`release-versions.sh`）证明那是模式的问题而不是仓库的问题；换成裸名后发现真命中只在正要改写的三个文件里，且 `git grep "build.sh"` 把 `package-release-macos.sh:111` 的 `build_sha256` 当成命中（`. ` 在正则下是通配符）。
- **阳性对照**：`release-versions.sh` 命中 **10** 个文件、`test.sh` 命中 **8** 个文件；**反向对照**：一个从未存在过的名字命中 0。
- **覆盖面**：新文件是未跟踪的，故带 `--untracked`；这一点**另行证明**过——`cargo tauri` 一词在不带该开关时找不到 `bin/control.sh`，带上就找得到（同文件）。

## 3. `bin/control.sh`

动词 `start|stop|restart|status|help`，与 workspace 同形状（含未知动词 `exit=2`、usage 走 stderr、`help` 走 stdout）。

- **地址读配置，不抄配置**：`build.devUrl` 由 `node -p` 从 `src-tauri/tauri.conf.json` 读出。变异臂 M3 把**副本**的 `devUrl` 指到一个无应答的端口（模拟服务器仍在原端口上答）⇒ `alive=yes health=down`。这条变异过了；见 §4。
- **`alive`／`health` 是两个读数**：臂 H 取到 `alive=no health=ok`（有东西在答但非本 harness 所起），M3 取到 `alive=yes health=down`。**两个方向都取到了**，故两个信号不是同一个数打印两遍。`exit=1` 的含义固定为「不是经本 harness 起的」。
- **`stop` 回收整个进程组**：`set -m` 让后台作业自成进程组，`kill -TERM -- -<pid>` 打整组；臂 D 后 `lsof` 在 dev 端口上无监听、替身的子进程 `pgrep` 也空。
- **十臂读数**（`artifacts/t03-desktop-control-arms.out`）：A 起、B 运行中 `status`（`exit=0`）、C `restart`、D 停、E 停后 `status`（`exit=1`）、F PATH 无 cargo 时快速失败、G 日志、H 无 pid 有应答、M1–M5 变异、M5c 阳性对照。

## 4. 一处自己踩到的缺陷（已修，留痕）

首版 `dev_url` 用 `node -p 'require(…).build.devUrl'` 并「取值为空即报错」。**键不存在时 `node -p` 打印字符串 `undefined` 且 `exit=0`**，空判断永不触发，于是把 `url=undefined` 当地址打了出来——`exit=1` 由 health 侧兜住，掩盖了它。改为表达式对缺键返回空串（`|| ""`）＋先判配置文件在不在；回归臂 M4（缺键）、M5（缺文件）现在都报出人话。已登记 `change.md` §14 第 15 项。

## 5. `scripts/test.sh` 在没有 sidecar 的克隆上写占位文件

`src-tauri/tauri.conf.json` 的 `externalBin` 存在性检查**没有开关**，真 sidecar 由跨仓的 `prepare-release-sidecar.sh` 产出（需要兄弟仓与它的构建 venv），而套件**不读文件内容**（`the_bundled_sidecar_is_resolved…` 是 `#[ignore]`）。

- 处置：只在路径缺失时写一个 `exit 1`、自称 `NOT the Local Agent` 的占位符，并把理由写在脚本里。
- **两臂读数逐字相同**：有真 sidecar 与有占位符，都是 `372 passed; 0 failed; 5 ignored` ＋ `release-versions 20 passed`。
- **到不了发布**：占位符被 `.gitignore:10` 挡住（`git check-ignore -v` 有判别力的读数）；`release-versions.sh --check` 拒绝任何没有 `target/sidecar-manifest.json` 的包，而该文件只有真构建写得出。
- 干净克隆臂（`/private/tmp/desktop-clean`，HEAD + T-03 工作树）实测：`no sidecar at …; writing a placeholder` 分支生效，随即 `exit=0`、读数同上。**该克隆的 `target/` 是热的**，故其中的编译时间不是冷启动读数——本臂验的是 sidecar 路径，不是构建速度。

## 6. 文档里的端口值：三形态 + 去值留名

`artifacts/t03-doc-port-literals.out`。三种输入形态各扫一遍：`:[0-9]{4,5}` 命中 0、裸 4-5 位数字组命中 **5**、`127.0.0.1` 命中 0。**只有第二种抓得到**——这个值在这里是散文（`devUrl 5174`），不是地址。改后同一形态 5 → 3，余下 3 条是契约版本号（`v1@…`，读者必须看见的标识符，非运行参数）。阳性对照：同模式在 `tauri.conf.json` 上命中。

去值留名的两处是 `DIRECTORY_MAP.md:24,82`。**这条裁定的措辞是「不进 README」，而实际漏网处是目录地图**——超出 §5 的「脚本层段落」，按 D-06 的精神一并处理并登记 §14 第 17 项。

## 7. 本次没有跑什么（如实记）

- **GitHub Actions 本身未运行**。改的是 workflow 文本；`verify_m0_config.py` 对它的断言是**字符串检查**（§14 第 12 项），不等于那一步真能跑。
- **真实 `cargo tauri dev` 未跑**：它会编译并打开窗口。`start` 路径只在 `PATH` 前置的模拟 cargo 下跑（§3）。
- **`verify_m0_local.sh` 在本环境是红的，红在别的仓**：它在 agent 块 `wt-media-agent/scripts/build.sh`（脚本第 36 行）中止——`uv build` 要从 PyPI 取 `hatchling`，本沙箱无网络。desktop 块是**最后一步**，因此没被这个脚本跑到；该块另跑直测（§5）。该脚本不是六个静态门禁之一。

## 8. 门禁读数

六门禁 + `unittest discover -s tests -q` + `sync_skills.py check` 落 `artifacts/t03-gate-after.out`：六个全 `exit=0`、`Ran 101 tests`／`OK`、`skill outputs are up to date`。其中 `verify_m0_config.py` 与 `verify_m0_local.sh` 的 desktop 断言正是 T-02 前置收窄的那两条——T-03 落地后仍绿，即 T-02 的前置有效。
