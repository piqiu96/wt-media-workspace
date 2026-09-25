# T-06 证据：五类版本

CHG-20260923-059 T-06（`change.md` §8）／AC-06、AC-10，兼 AC-09 的「版本」那一半，
并关闭 Q-04（`change.md` §7）。原始转录见本目录 `task-06-*.out`。

判据（T-06 行）：五类逐个有可得来源（每条附命令）；版本不匹配的包**必须被拒**（先造一个不匹配的，看它红）。

---

## 1. 交付了什么

**一个来源，五条命令。** 新增 `wt-media-desktop/scripts/release-versions.sh`，它是五类版本的唯一读法：

| # | 类 | 来源 | 读取命令 | 出货读数（本机 2026-09-25） |
|---|---|---|---|---|
| 1 | Desktop | `src-tauri/tauri.conf.json` 的 `version` | `release-versions.sh --check` | `desktop_version=0.1.0` |
| 2 | Agent | `target/sidecar-manifest.json`（`build_desktop_sidecar.py` 从 `pyproject.toml` 写出） | 同上 | `agent_version=0.2.2` |
| 3 | 前端构建 | `.generated/frontend/frontend-build.json`，由 `--stamp-frontend` 从 `wt-media-cloud/web` 的检出写出 | 同上 | `frontend_build_version=0.1.0+f21bbcb` |
| 4 | Contract | `../wt-media-workspace/config/contract-map.yaml` | 同上 | `contracts=10`（10 条 `name=revision`，见 `task-06-reals.out`） |
| 5 | 组件与资源 | 产物自身：`Contents/Resources` 逐文件 sha256 | `release-versions.sh --verify <app>` | `components_resources_version=sha256:69f34a89…`、`components_resources_files=4` |

**五条命令合起来是一条**：`--check` 给前四类（第五类需要 `--app`，因为它算的是产物），
`--record`／`--verify` 给五类。判据命令与读数逐条落在 `evidence/task-06-reals.out`。

**Desktop ↔ sidecar 版本兼容**：新增 `wt-media-desktop/src-tauri/agent-compat.json`（pin），
`--check` 在 `pin != 构建出的 sidecar 版本` 时**拒绝**，报文点名 pin 文件与两侧版本。
它是**评审闸门**而不是语义证明——它不知道新 Agent 的本机 API 是否仍配得上这个 Desktop，
所以它把问题逼到唯一有人能回答的时刻：Agent 版本变了而包本来会静默带上这个变化时。
**改这个 pin 就是那次评审**（这句话写在 pin 文件自己的 `note` 里）。

**接线**（一个发布流程，五处）：

| 位置 | 动作 |
|---|---|
| `scripts/build-release-macos.sh` | `cargo tauri build` 之后跑 `--check`（sidecar manifest 与前端 marker 到那时才存在）；`DMG_PATH` 里写死的 `0.1.0` 改为读 `tauri.conf.json` |
| `scripts/repair-macos-signing.sh` | 写 sidecar manifest 之后、外层签名之前跑 `--record "$APP_PATH"` |
| `scripts/package-release-macos.sh` | 把包内记录复制成发布目录的 `versions.json`，并加进 `SHA256SUMS` 与 `README.txt` |
| `scripts/verify-release-macos.sh` | 挂载后跑 `--verify "$mount_dir/WT Media.app"` |
| workspace `scripts/build-desktop.sh` | 复制产物之后跑 `--stamp-frontend "$GENERATED_DIR"`，即前端构建版本的来源 |

另：`scripts/test.sh` 现在跑 `tests/*.test.sh`，`tests/README.md` 记了这两个 shell 套件（此前它们没有任何调用方）。

## 2. 先红读数

T-06 没有「实现不存在」以外的先红，如实登记：首轮 `task-06-red.out` 是
`No such file or directory` / `exit=127` × 20 —— 这种红什么都不证明（缺文件，不是行为）。
**本任务真正的红有两处**，都出自「造一个不匹配的，看它红」：

1. **真机、真产物**（`task-06-reals.out` 段 4）：记录写好后改一个随包资源 →
   `--verify` 拒绝，并**点名那个文件**：`resources/desktop.production.toml changed after the record was
   written (it records sha256:69f34a89… and the artifact now hashes to sha256:6a940388…)`，`exit=1`。
2. **真机、真 pin**（同文件段 5）：pin 从 `0.2.2` 改成 `0.2.3` →
   `--check` 拒绝：`the packaged Agent is 0.2.2 but this Desktop release pins 0.2.3 (…agent-compat.json):
   review the Agent's local API changes against this Desktop and update the pin, or build the pinned Agent`，`exit=1`。
   段 6 是同一条命令的阳性对照：pin 还原后 `versions ok`、`exit=0`，pin 文件 sha256 前后一致
   （`2f6076fa…`）。**没有这个阳性对照，段 5 的红只说明命令坏了。**

另有一处实现内的先红：A7/A14 首轮转红，因为拒绝报文只说「摘要变了」而**不说哪个文件变了**。
这是判据本身在要求实现改进（拒绝必须点名），改的是实现不是用例：记录与前端 marker 各自带上
逐文件清单，拒绝时用它差异出名字。

## 3. 修好之后

**发布流程真的跑了一遍**（`task-06-release.out`，`build-release-macos.sh`，exit=0，产出
`WT Media_0.1.0_aarch64.dmg`，17,129,049 字节）。顺序读数：

1. 前端重建由 workspace 的 `build-desktop.sh` 完成（它是 `tauri.conf.json` 的 `beforeBuildCommand`），
   并在同一步打出 marker：`stamped=… version=0.1.0+f21bbcb files=47 digest=74d4b003…`。
   这个 digest 与我先前手工 stamp 同一次构建得到的**完全相同**——同源同产物两次构建摘要一致。
2. `cargo tauri build` 之后 `--check` 通过（`versions ok`），说明「构建产物 → marker 仍描述这棵树」
   这条链在真实流程里成立；若 stamp 的位置或参数错了，这里就会拒。
3. `--record` 在签名窗口内跑：`components_resources_files=4`、`sha256:69f34a89…`。
4. 挂载 DMG 后 `--verify` 复算出**同一个** `sha256:69f34a89…`（`task-06-reals.out` 段 7：该摘要在
   发布转录里出现 2 次，第 279 行是 `--record`、第 299 行是 `--verify`）。

第 4 条是这份证据里最强的一条：它同时证明了三件事——暂存配置、写记录、外层签名与 DMG 装配
都**不改变** `Contents/Resources` 的字节；记录里那份逐文件清单（`config/README.md`、`config/agent.toml`、
`resources/desktop.production.toml`、`sidecar-manifest.json`）覆盖了 sidecar manifest 本身，
即 D-15 的顺序（记录写在 sidecar manifest 之后、外层签名之前）在产物上成立。

## 4. 闸门表

`--check`／`--record`／`--verify` 的拒绝条件与各自的判据（A 号见第 6 节的变异表）：

| 条件 | 报文点名 | 用例 |
|---|---|---|
| 没有 pin 文件 | pin 路径 + 「nothing states which Agent build」 | A20 |
| pin ≠ 构建出的 sidecar 版本 | 两侧版本 + pin 路径 | A2（正）／A3（反） |
| Agent 两处自述不一致（`pyproject.toml` vs `runtime/version.py`） | 两处路径与两个版本 | A4 |
| sidecar 来自另一个 Agent 修订（manifest ≠ 源） | manifest 路径与两侧版本 | A5 |
| 没有前端 marker | marker 路径 + 该跑哪条命令 | A6 |
| marker 不再描述这棵树 | **变动的文件名** + 记录摘要 vs 现摘要 | A7 |
| 合同表读不出任何 revision | 分母为 0 时拒绝而不是「0 条也算过」 | A9（正）／A10（反） |
| 资源目录没有文件 | 「digest of nothing」 | A17 |
| 记录不存在 | 「carries no …」 | A15 |
| 记录 ≠ 产物（逐文件清单差异） | **变动的文件名** + 两个摘要 | A12（正）／A14（反） |
| 记录里的三类标量与构建设不一致 | 字段名 + 两侧值 | A18 |
| 前端源不是 git 检出 | 路径 + 「not a git checkout」 | A19 |
| 前端源脏 | **不拒**，标记 `.dirty` 并在 stderr 警告 | A8 |

## 5. 设计裁定

- **D-17（Q-04 的口径）**：「组件与资源版本」是**内容摘要**，不是被人手工递增的号。
  它是产物 `Contents/Resources` 逐文件 sha256 的合并摘要（排除记录自身），因此
  ① 只在随包集合真的变了时才变；② 不可能过期，因为它由字节算出；③ 没有「谁来 bump 它」这个问题——
  这正是 Q-04 问的「版本从哪算」的答案：**不从哪算，它是恒等式**。资源清单**不是它的输入**，
  而是它的产物：清单用于把摘要差异翻译成文件名。
- **D-18（边界，避免过度声称）**：这一类的范围是 `Contents/Resources`，**不含 `Contents/MacOS`**。
  随包 sidecar 二进制由 T-04 的运行期完整性校验负责（app 启动前按包内 manifest 的 sha256 校验），
  那是比摘要更强的判定，不在这里重复。**记录也不覆盖整个 `.app`**：外层签名会写
  `Contents/_CodeSignature/`，签名后全包摘要必然与签名前不同，那样的摘要永远不可复算。
- **D-19（Desktop ↔ sidecar 的规则是 pin，不是版本相等）**：Desktop 与 Agent 是两个产品，
  让它们的版本号相等是假的语义。真正的兼容事实是「这个 Desktop 配得上这个 Agent 的本机 API」，
  没有机械判据，于是做成 pin：不匹配必拒，改 pin 即评审。**这是评审闸门，不是证明**，如实写在
  pin 文件与脚本头部注释里。
- **D-20（前端构建版本的来源在 workspace，不在 desktop）**：Desktop 仓没有 `package.json`，
  也看不到来源仓，所以这个值只能由 `build-desktop.sh` 在复制产物后立即 stamp。
  **已知局限**：marker 记的是 **stamp 时刻**的源提交，不是「产物真正的构建提交」；
  对先于 stamp 存在的旧产物，它会归因到当时的 HEAD。保证两者同时刻的流程是
  `build-desktop.sh`（紧跟复制），这也是 `tauri.conf.json` 的 `beforeBuildCommand` 走的路径。
- **D-21（记录写在签名窗口内）**：`--record` 放在 `repair-macos-signing.sh` 的 sidecar manifest
  之后、外层签名之前，与 T-04/D-15 的同一条理由：`Contents/Resources` 被外层签名封住，
  签名后写入会破坏封印；而记录要覆盖它描述的一切，就必须在该文件写入之后才能算。
- **D-22（不加 `version_classes:` 块到 `release-matrix.yaml`）**：五类的来源已经在
  `release-versions.sh`（运行时唯一读法）与制品内的 `versions.json`（每份包自带）各声明一次；
  再往 `release-matrix.yaml` 抄一份，就是第二份没人校验的声明，正是治理规范要避免的漂移。
  workspace 侧本任务的实际交付是 `build-desktop.sh` 的 stamp——那条没有它前端构建版本就无来源。
- **D-23（订正一处真的 bug）**：`build-release-macos.sh` 的 `DMG_PATH` 原为写死的 `WT Media_0.1.0_…`，
  而 `verify-release-macos.sh` 与 `package-release-macos.sh` 都按 `tauri.conf.json` 算名字——
  版本一升，构建出的 DMG 名字与验证要找的名字分叉。改为同一来源。
  **今日不可分辨**（`0.1.0` 恰好就是写死的那串），见第 9 节。

## 6. 变异表（15/15）

`tests/release-versions.test.sh` 20 条臂（A1…A20），全部在 `/private/tmp` 自造假树，
不依赖任何兄弟仓检出。变异逐条贴在 `scripts/release-versions.sh` 上、`bash -n` 通过后跑整套，
每次跑完从 pristine 还原并以 sha256 校验还原成功（转录 `task-06-mutations.out` 首行是 pristine 摘要）。

| 变异 | 打掉的臂 | 读数 |
|---|---|---|
| M1 pin 永不比对 | A3 | 恰好 |
| M2 Agent 两处自述不比对 | A4 | 恰好 |
| M3 manifest 与 Agent 源不比对 | A5 | 恰好 |
| M4 缺 marker 被容忍（两处守卫同改） | A6 | 恰好 |
| M5 marker 摘要永不比对 | A7 | 恰好 |
| M6 合同表读不出 revision 也照样过 | A10 | 恰好 |
| M7 记录自身算进产物摘要 | A12、A13（另及 A18） | 多打一个：产物级判定先于字段级判定触发，A18 因此提前红 |
| M8 拒绝不再点名变动文件（两处） | A7、A14 | 恰好 |
| M9 没有记录的产物照样 verify 通过 | A15 | 恰好 |
| M10 空前端也允许 stamp | A16 | 恰好 |
| M11 脏源被记成干净 | A8 | 恰好 |
| M12 资源目录空也照样摘要 | A17 | 恰好 |
| M13 记录的三个标量不与构建比对 | A18 | 恰好 |
| M14 非 git 检出也照样 stamp | A19 | 恰好 |
| M15 缺 pin 被当成「没什么可比」 | A20 | 恰好 |

**这张表反过来改了两条臂的判据，如实登记**：M1 首轮**没有**打掉 A3、M15 首轮**没有**打掉 A20，
原因是这两条臂的 needle（`0.2.3`／`agent-compat.json`）会被**另一条**拒绝路径的报文满足——
臂会在错误的原因上变绿。改法是把 needle 收窄到**只有目标守卫会产出**的措辞
（A3 → `agent-compat.json`；A15 → `carries no`；A20 → `nothing states`），改完两条变异各自恰好打掉自己的臂。
M10/M12 首轮 `bash -n` 不过（把三行 `if…fi` 换成一个裸 `if false; then`），补成 `if false; then :; fi`。

## 7. 凭据

本任务新增的文件是脚本、测试、一个 pin JSON 与一份记录，**都不含凭证**：
pin 只有版本号与一句话说明；`versions.json` 只有版本、合同修订、路径与 sha256。
`--record` 的输入里唯一可能带凭据的是 `config_online/agent.toml`，而它按 CHG-056 D-07
**不携带凭证**（凭证只走环境变量），T-05 已用阳性对照扫过它；本任务的摘要与清单**只记路径与哈希，
不记内容**。分母：新增 5 个文本文件（脚本、测试、pin、README 段落、记录），逐个看过内容。

## 8. 读数

| 项 | 读数 | 来源 |
|---|---|---|
| shell 臂 | **20 passed, 0 failed** | `task-06-green.out` |
| 变异 | **15/15**，0 unproven | `task-06-mutations.out` |
| 真机五类 | 前四类 + `contracts=10`；第五类 `files=4`、`sha256:69f34a89…` | `task-06-reals.out` |
| 真机记录 vs 产物 | `--record` 与挂载 DMG 的 `--verify` **同一摘要** | `task-06-release.out:279,299` |
| 发布流程 | `build-release-macos.sh` exit=0，产出 DMG 17,129,049 字节 | `task-06-release.out` |
| 前端摘要可复现 | 手工 stamp 与发布流程内 stamp 同值 `74d4b003…` | 本节与第 3 节 |
| desktop 套件（`scripts/test.sh`） | Rust **363 passed / 0 failed / 5 ignored**，两个 shell 套件各绿 | `task-06-desktop-suite.out` |
| agent 套件 | **Ran 397 tests … OK** | `task-06-agent-suite.out` |

## 9. 未覆盖项

1. **`DMG_PATH` 的订正无法在今日分辨**：`0.1.0` 恰好等于原来写死的值，真机跑出来的名字与改动前一致。
   这条只有版本号真的升上去才会显出差别，故它是**读证**，不是跑证。
2. **前端 marker 的归因局限**（D-20）：marker 记 stamp 时刻的源提交。对「先有产物、后 stamp」的路径，
   它会把产物归因到当时的 HEAD。本任务的真实流程（`beforeBuildCommand` → `build-desktop.sh`）
   不经过这条路径，但手工 stamp 旧产物会。
3. **不加 `version_classes:` 到 `release-matrix.yaml`**（D-22）：五类来源不在那份 yaml 里，
   这是裁定而非遗漏；若 T-10 回写基线时需要一处文字说明，落点应是里程碑文件而不是第二份配置。
4. **第五类不含 `Contents/MacOS`**（D-18）：随包二进制的完整性由 T-04 的运行期校验负责，
   本摘要**不**覆盖它，两条机制不重叠也不互相替代。
5. **x86_64 / Windows 目标**仍在本机做不到（既有登记）；五类版本与 pin 的读取与平台无关，
   但真机读数只有 arm64 macOS 这一份。
6. **`--stamp-frontend` 对空目录的判据只有一条**（A16）：`package.json` 缺 `version` 的拒绝路径
   没有独立臂（M10 首轮的红是它冒出来的副产品），登记为覆盖不足。
7. **`tests/package-release-macos.test.sh` 与 T-06 的接线**：本次把它一并接进 `scripts/test.sh`
   （此前无人调用），它的绿是本任务顺带读到的，不是 T-06 的判据。
