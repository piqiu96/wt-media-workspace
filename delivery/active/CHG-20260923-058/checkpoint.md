# CHG-20260923-058 Checkpoint

## Completed

- 2026-09-24：草案由 `delivery/planned/` 移入 `delivery/active/` 并改写为十三节执行记录。
- `change.md` §4 的每条现状都是激活时**实测**得到的 file:line 与命中数（不是从草案推想）：
  `AppPaths`/`settings.toml`/`UserSettings`/`schema_version`/`cache`/`versions` 在 Desktop 全为零命中；
  `paths.rs` 是配置文件定位器、**不可就地扩展**；`logging/rolling.rs:629 list` 私有且**生产路径零读日志**；
  Cargo 里**无 zip/tar、无哈希**；`LocalLogsPage.vue` 是 40 行纯桩；`本机设置` 在 `web/src` 零命中但
  `features/local-settings/.gitkeep` 占位已预留；Agent 的四个界各自有明确住处（§4.6）。
- 用户 2026-09-24 的六条裁定落在 §6 D-01…D-06；四条既有裁定按 D-07/§5 原样保留。
- 规格探针先行取得（`/tmp/cratecheck/probe`）：证明 `file-rotate` 0.8.0 给出稳定活文件 +
  `X.log.<YYYY-MM-DD-HH>` 归档 + **真按天删除**（20 天删 / 15 天删 / 2 天留），
  并推翻我此前「没有现成工具能按天删除」的判断。§7 Q-01…Q-08 已把由此产生的代价逐条登记。
- 本机环境已收拢：app / sidecar / cloud / redis 全部停止；旧日志存档 `/tmp/chg058/preexisting/`。
- 顺带实测到 **CHG-D 范围内**的一条真缺陷：`osascript quit` 后两个 `wt-media-agent` 存活、
  PPID 被 launchd 收编、仍占 `127.0.0.1:8765`（`/tmp/chg058/preexisting/orphan-sidecar-after-quit.out`）。

## Current

- T-01 **DONE**（`12ae5e9` 激活、`a2380a4` 证据）：十三节执行记录、`checkpoint.md`、`status/`×3、
  LEDGER 表行、`planned/README.md` 的 C 行改 ACTIVE、程序总纲状态行改指 `active/`；
  快照再生成 **2159 字符**；三验证器绿；定向检查「无残留 planned 指针」附阳性对照（12 处）。
- T-02 **代码 DONE**（desktop `b344511`/`a4abcd6`/`f95cb28`、agent `1160f3c`；证据
  `evidence/task-02-log-rotation.md`）。两侧形态一致：活文件 `X.log` + 归档 `X.log.<YYYY-MM-DD-HH>`、
  按小时**整点**切割、只按天保留 14 天、出货值同为 14 天 / 1 MiB、单条截断标记同形。
  计数：agent **377 OK**（基线 379，差额 2 逐条登记）、desktop **160 passed**（基线 175，34 删 19 增，
  按类目全列）。Agent 10 项实现变异全灭；Desktop 每步先红。
  **T-02 期间的实测发现**（已落进 §6 D-09/D-10 与证据）：标准库小时档自选下划线 suffix、
  `computeRollover` 对小时档**不对齐**（归档名与内容差近一小时）、crate 的 `too_old` 比的是
  **归档名字符串而非 mtime**；并纠正了本任务自己一条**空转的用例**（`_live` 保护原先靠年龄而非保护通过）。
- T-02 的**基线回写 DONE**：程序总纲 §3 CHG-B 四条、架构基线 §5.8、里程碑成功事实 #5
  （「受容量限制」→「按天保留」）、CHG-057 归档记录顶部取代注记（正文按 D-08 不动）。
- T-02 的**记录与证据 DONE**：`evidence/task-02-log-rotation.md`（形态表、两侧计数差额逐条登记、
  10 项实现变异、四条真机探针、三条实测发现、七条边界登记、探针方法论更正，
  以及新补的**收口门禁同集合对照**一节）；`change.md` 加 D-09/D-10、D-04 补实测排序事实。
  workspace 侧按 Task 一个 commit。

- T-03 **DONE**（desktop `3a0ea08`）：新模块 `src-tauri/src/app_paths.rs`（753 行）+ `main.rs` 一行
  `mod app_paths;`，**未动 `paths.rs`、未动 `logging/paths.rs`**。四个根：
  装机态 `Application Support/WTMedia/Desktop`(data) / `…/Desktop/versions` / `Logs/WTMedia/Desktop` /
  `Caches/WTMedia/Desktop`，开发态 `<crate>/.local/{data,data/versions,logs,cache}`——
  形状照抄 Agent 的 `runtime/paths.py`（含「装机态数据根即组件目录、开发态下沉一层」那条不对称）。
  `directory`（纯）/ `resolve`（收拢，装机态缺 `HOME` 即 `Err`）/ `prepare`（唯一碰盘：建目录 + 真写探针）；
  **读方只用 `directory`，写方才 `prepare`**。logs 一根本模块**不复述**、委托 `logging::paths`。
  计数 desktop **160 → 176**（+16，0 删除，0 skipped）；**12 个实现变异全灭**（rustfmt 之后重跑过，
  故表指的是将提交的字节）。非测试构建警告 9 → 23（+14 全为本模块 `never used`，测试构建 0 条，
  消费方在 T-04/T-05，**不用 `allow` 盖掉**）。证据 `evidence/task-03-app-paths.md`。
  **待 T-09 承接**：cache 落在 `~/Library/Caches` 而**不在**数据根之内，§5.8 目录树要照此写，见证据边界 1。

- T-04 **DONE**（desktop `7825a75`）：新模块 `src-tauri/src/settings.rs`（817 行）+ `main.rs` 一行
  `mod settings;`。落到 **`AppPaths` 的数据根**之下（装机态 `Application Support/WTMedia/Desktop`、
  开发态 `<crate>/.local/data`），`save` 不创建那个目录（建目录是 `prepare` 的职责）。
  替换走**同级临时文件 + `sync_all` + `rename`**，写动作注入成参数 ⇒「写到一半中断」可测：
  目标逐字节不变、临时文件清掉、返回 `Err`。坏形态（不可读 / 解析失败 / 版本不认识）一律 `Err`
  且**原文件一个字节都不动**；只有「文件不存在」才是首次启动。版本判定用 `!=`（v1 是第一版）。
  **`save` 读得通才写**——把「调用方拿 `Err` 却用默认值写回去」这条静默清空路径变成不可达，
  代价是用户想重置得自己删文件。
  计数 desktop **176 → 198**（+22，0 删除，0 skipped）；**16 个变异全灭 + 1 个登记为等价**
  （toml 0.9 自己就省略 `None`，`skip_serializing_if` 在该 crate 上不承载语义）；
  非测试警告 23 → 35（+12 全为本模块 `never used`，测试构建 0 条）。证据 `evidence/task-04-user-settings.md`。
  **边界**：`save_dir` = 素材下载/成片输出目录，**今天 0 个消费方**（`UserSettings` 全仓 0 命中），
  T-08 的页面能改它不等于任务会按它落盘——收尾时别把 T-04 当成端到端可用；文件无目录 `fsync`；
  `save` 不校验路径合法性；它**不是**四个运行目录的 override 通道。
  **harness 教训**：第一版变异脚本用 `--quiet`，逐条用例名被吞 ⇒ 把「失败」读成「没编译」，
  整批误报 0/16；现已内建「未变异字节必须 0 failed」的阴性对照。

- T-05 **DONE**（desktop `45356d2`）：四个新模块——`logging/reader.rs`（1189 行，读取面）、
  `storage.rs`（517 行，`available_bytes_for`）、`commands/storage.rs`（692 行，三个命令）、
  `dto/storage.rs`（273 行，线上词汇），加 `logging/paths.rs` 的 `agent_directory`（+292，**T-03 的开口在这里关**）。
  三条命令**追加**在 `invoke_handler!` 末尾。两条承重契约：**列表即白名单**（`local_log_tail`
  先列目录再按名查找，从不把名字拼到目录上 ⇒ 5 个越界名字的分母 + 阳性对照）、**归档名与
  `file-rotate` 的判定逐字一致**（6 种戳形状；`TooShort` 三种是我第一版猜错的）。分界：
  **不在 ⇒ 0、读不到 ⇒ `Err`**，画在 `io::ErrorKind` 上而不是 `Path::exists()`。
  计数 desktop **198 → 255**（+57，0 删除，0 skipped）；**50 行实现变异 48 灭 + 2 登记为等价**
  （R2 切点有 case 分析；S6 `f_bfree` vs `f_bavail` 本卷实测相等 ⇒ **平台性**等价），另补一行聚焦变异。
  非测试警告 35 → 27（消费方用掉了 T-03/T-04 留下的 `never used`；**未在 T-04 树上复测**，故只作趋势）。
  **变异表反过来改了实现三处**：C2 存活 ⇒ 抽 `tree_usage`；**S7 存活** ⇒ 空闲空间用例的上界从
  「小于 1 EiB」改成「不超过卷总容量」（本机 `f_bsize` 1 MiB ≠ `f_frsize` 4096，错乘报 23.8 TB，
  旧上界过得去）；一次可疑的「灭」定位为**用例自身竞态**（活卷两次读数不等），改 `readings_agree` 重试。
  **登记偏离**：读取面落 `reader.rs` 而非 `rolling`（理由已写进 `change.md` 的 T-05 行与模块头）。
  证据 `evidence/task-05-storage-read.md`。**边界**：命令体（收 `State`）无单测，由真机探针覆盖
  （探针跑完即撤销）；`paths.rs` 只做半格式化（其余 3 处是 CHG-057 已提交字节）；Agent 的
  **非 frozen 开发分支**仍不镜像（T-03 的开口，此处仍开）。

- T-06 **DONE**（desktop `ffb9ff8`）：三个新模块——`cleanup.rs`（768 行，规则本体）、
  `commands/cleanup.rs`（387 行，接线）、`dto/cleanup.rs`（158 行，线上形状），
  加 `commands/storage.rs` 的 `Resolved`/`resolve` 升 `pub(crate)` 与抽出 `tree(source)`
  （两个解析器会是两条没人保证一致的规则 ⇒ 页面可列一棵树、清另一棵）。两个命令**追加**在
  `invoke_handler!` 末尾。**保护是一条路径不是一个名字清单**：白名单六类里五类住在数据根下，
  而清理**不收路径参数**（缓存命令什么都不收，日志命令收来源标签）⇒ 分母
  **5 类 × 3 个可达根 × 2 种布局 = 30 次比较** + 阳性对照；第六类在可达树内按**种类**保护
  （`live`/`unrecognised`/`symlink`/`special` 留，空子目录删，树本身与缓存根留）。
  `freed_bytes` = 被删文件的**逻辑大小之和**，由**独立 walk**（`storage::directory_bytes`）对账，
  **不是**可用空间差值（那个差值在活卷上可以为负）。两种失败两种处置：树读不出 ⇒ 整次 `Err`；
  单个 `remove_file` 失败 ⇒ 报告里一行，`freed_bytes` 只累计返回 `Ok` 的。
  计数 desktop **255 → 276**（+21 = 14+5+2）；**26 行实现变异 26 灭、0 等价**（14/14 + 7/7 + 5/5，
  三组各带阴性对照、跑完逐字节还原 `e9048f66c36f`/`34ee2c9c4ea2`/`c78c0b40aa63`）。
  非测试警告 **27 条不变**（另有 1 行汇总；按文件归位后**无一条落在本 Task 的三个新模块上**）。
  **新用例如是抓出一个真缺陷**：`a_failed_removal_reaches_the_page` 首跑 `left: 2, right: 1`——
  同一个文件被报两条（文件 `Permission denied` + 父目录 `Directory not empty`），根因是文件失败臂
  没置 `empty = false`，父目录仍去 `remove_dir`；现已由变异 **C10** 钉住。
  **本轮定下的两件事**：§6 **D-11**（日志清理一次只清一棵树——Q-08 的裁定覆盖**读**，
  把「删」延伸过去是本 Task 的决定，不是用户的）、**D-12**（`FileKind::Other` **永不删**：
  真机上的 `desktop-20260924-1.log` 在查看器里可见、留在原地——`Other` 是**显示**类目不是**删除**类目，
  这回答了上一版 Next 里留的那个问题）。
  证据 `evidence/task-06-cleanup.md`。**边界**：真机探针（只读）读出两个按钮**会删 0 个文件**
  ⇒ 破坏性路径**没有**在真机验证过（有意：为了证明删除能用而删用户的真日志不是验证）；
  命令体（收 `State`）无单测，与 `commands::agent`/`commands::storage` 同先例。
  **仓库卫生（未纳入本次提交）**：收尾时 `git status` 有 **14 个本 Task 之外**的文件带改动，
  机械核验（`rustfmt(HEAD)` 逐字节等于当前字节）证明**全是格式化**、无语义变化，
  mtime 落在本 Task 时间窗内（22:31–22:32）——来源是一次**没走单文件路径**的格式化调用
  （本仓不是 rustfmt-clean，规则要求只对单个文件跑）。本次**只 add T-06 的路径**，
  这些改动留在工作区未动，完整 diff 存 `/tmp/chg058/fmt-stray/stray-formatting.patch`。

## Next

- T-07 **脱敏诊断导出**：版本 + 组件状态 + 已脱敏日志 + 失败任务摘要，打成单个归档；
  不得含完整凭证/Cookie/代理密码/用户媒体文件。先红的口径写在 T-07 行里：**归档内容逐项枚举**、
  **凭据阳性对照**（先证明针抓得住再报「0 命中」）、文件名与大小上限。
  （本 CHG §4.3 已实测：Cargo 里**无 zip/tar、无哈希**，归档依赖要新引，走代理的那次调用。）
- T-08 前端「本机设置」页与 `LocalLogsPage` 重写（`wt-media-cloud/web`）：两条硬约束仍未触碰——
  `localAgentBoundary.test.js` 禁页面出现 `127.0.0.1`/`fetch(`；`localAgentService.test.js` 断言
  `invoke` 的**精确**参数对象（三个只读命令 + 两个清理命令都追加在 `invoke_handler!` 末尾，未插队）。
- T-09 回写基线（含 §5.8 的 `cache/`，承 T-03 的开口）与归档收尾。

## Blocked

- 无。§7 的 Q-01…Q-08 全部 `Blocking = NO`。

## Recent verification

- 激活时基线：agent `379 tests OK` / desktop `175 passed, 0 failed` / web `21` 个测试文件 /
  workspace 两验证器绿；`unittest discover` 的 **4 条红项为既知**（见 `README.md`），
  判定要用 `git archive HEAD` 的**同集合阳性对照**，不用「看着无关」。
- T-02 收口时的同集合对照**已按真实路径做**（`git archive` 到 `/tmp` 是**无效对照**：
  路径敏感的兄弟仓用例在那里被 skip，把 4 红读成 2 红，见证据末节）。就地读数：
  HEAD **4 红** vs 工作树 **4 红**，**逐名相同**（`test_contract_map_matches_m1_cloud_agent_compatibility`、
  `test_contract_map_provider_paths_exist_in_full_workspace`、
  `test_current_product_master_and_governance_are_aligned`、
  `test_static_cross_repo_contract_and_security_matrix`）；还原后 `git status` 与交换前 **IDENTICAL**。
  三验证器绿：governance ok（Active CHG: CHG-20260923-058）、快照 **2159 字符** / 0 warning、
  `verified 10 skill source files`。
- T-03 后：desktop `176 passed`（起点 160，+16）；`cargo test app_paths` 16 条 **0 skipped**
  （只读目录那条的**前提在本机成立**，所以它真的跑了断言）；非测试构建警告 **23**（起点 9，+14 见上）。
- T-04 后：desktop `198 passed`（起点 176，+22）；`cargo test settings` 22 条 **0 skipped**；
  非测试构建警告 **35**（+12 全归本模块）；变异脚本自带阴性对照，跑完文件逐字节还原
  （`sha256:4e38ccc7b296aee5`）。
- T-05 后：desktop `255 passed`（起点 198，+57，逐件对账 26+13+10+2+6）；四组变异各带阴性对照
  （未变异字节必须 `0 failed`），跑完四文件**逐字节还原**（`0ff1a2560b31` / `7ca3d49e9148` /
  `f121df555ac0` / `1bbc657a7df6`）；`cargo check` 非测试警告 **27**（另有 1 行汇总，
  `grep -c '^warning'` 读 28）。**独立对账**：可用空间三来源逐字节相同
  （本模块 = `os.statvfs` = `df -k`×1024 = **91 757 240 320**）。真机探针四件事是实测不是推断：
  两棵树各自解析到真目录、Agent 三个 live 名、两侧级别拼写、筛选在真数据上按级别工作。
  `cargo test` 之外未跑 workspace 门禁——**留待 T-09 的关闭门禁**（同集合阳性对照）。
- T-06 后：desktop `276 passed`（起点 255，+21，逐件对账 14+5+2）；三组变异各带阴性对照
  （未变异字节必须 `0 failed`，三组读数分别为 21/5/2 条），跑完三文件**逐字节还原**；
  `cargo check` 非测试警告 **27**（与 T-05 同，`grep -c '^warning'` 读 28）。真机探针（只读、跑完即撤销）
  读出缓存根 0 项 / `.local/logs` 1 个活文件 / Agent 树 3 个活文件、**两棵树 `would_remove` 均为 0**
  ——健康机器上清理是空操作（探针**不删任何文件**）。

## 记录口径的一处更正

- `change.md` §9 的 `- [ ]` 复选框是**立项时的分工清单，不是进度跟踪器**（T-02 已 DONE 而它的框仍未勾）。
  进度以 §8 任务状态列与本文件为准；§9 不逐任务回勾，免得两处口径互相打架。
