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


- T-07 **DONE**（desktop `9c938d0`）：三个新模块——`diagnostic.rs`（1768 行，规则本体）、
  `commands/diagnostic.rs`（784 行，接线 + 保留的 `#[ignore]` 真机探针）、`dto/diagnostic.rs`（262 行，线上形状），
  加 `main.rs`（`mod` + `DiagnosticHost` + **一份 `secrets` 两个读者**）、`paths.rs`/`config.rs`（`Source::code`/`Environment::code`）、
  `logging/backend.rs`（抽出唯一的 `stamp_with`）、`app_paths.rs`（日志根不在数据根里）。
  归档是**一个 gzip tar + 一棵目录树**（`summary.json` + `manifest.txt` + `logs/{desktop,agent}/…`），
  摘要值是**归档外的兄弟 `.sha256`**——放进包里会变成自指（Q-06 已裁定容器；+4 依赖，lockfile 514 → 516）。
  **脱敏不变量在门上**：每条进包的字符串都过 `mask`，日志条目**两次**（写它的那层一次、`bundle_files` 再一次），
  由 `masking_twice_leaves_the_bytes_alone` 钉住幂等这条依赖。
  **AC-10 的「不含用户媒体」靠布局不靠过滤器**：`reader::list` 本就不过滤名字（`Other` 照列，D-12），
  故改由两条新用例承担——每棵树**只读一层**（含阳性对照：直接躺在树里的 `clip.mp4` 会被收进来）
  与**本组件日志根不在数据根里**（两种布局）。**有意收进来的**与**有意省略的**都逐项写进 §6 D-13/D-14。
  计数 desktop **276 → 314**（+38 = 28+4+2 新模块 + 4 处改动文件，另有 1 条 `ignored` 探针）；
  **32 行实现变异 32 灭、0 等价**（19+6+7，三组各带阴性对照）。
  非测试警告 **27 条不变**（`grep -c '^warning'` 读 28；按文件归位后**无一条落在本次任何文件上**）。
  **只有跑起来才发现的三处**：落点目录可能不存在（探针报 `not a directory` ⇒ 写前 `create_dir_all`）、
  manifest 的脱敏声明被换行拆开、`bundle_files` 首跑漏了复脱敏（单测抓出）。
  **由变异表反推出来的覆盖缺口**：`AgentFacts::state()` 是第三处拼写且无人读（改成 `summary()` 也用它）、
  摘要值只有自洽读者（新增**独立读者**：调本机 `shasum -a 256` 对账，变异 d18 由它打掉）、
  `name_too_long` 无人读、dto 的 `bytes` 与 `source_bytes` 在夹具里恰好相等。
  证据 `evidence/task-07-diagnostic-export.md`；**边界**：启动 token 进 `DiagnosticHost::secrets` 是一条
  `main.rs` 接线行，类型上成立但**用例不可达**（登记为证据边界，不宣称已测）。
  **变异工具的两处缺陷（本次发现并修掉，已写进证据）**：①还原走 `shutil.copy2` 保住源 mtime ⇒
  cargo 认为树干净、**用上一次变异的产物**跑这一轮（症状：组内 7/7 灭而紧接着一次 `cargo test` 报红）；
  ②`finally` 在 SIGTERM 下不执行 ⇒ 一次被停掉的运行在工作区留下 **d16** 的源码。
  修法是墙钟推 mtime + 组末尾**再跑一次阴性对照**（断言留下的是**绿的**树）+ 注册 `SIGINT/SIGTERM/SIGHUP`；

- T-08 **DONE**（desktop `5ee840c`、cloud `bb0136f`）：本机设置页与日志查看器。**先说范围补正**：§8 的 T-08 行
  把落点写成 `wt-media-cloud/web`，执行时实测那一半**不够**——AC-08 要「查看/修改保存位置」，而 T-04 的
  `settings.rs` **没有任何命令读它**（T-04 证据边界自己写着「设置页与命令面（T-05/T-08）负责」，T-05 没取这一半）；
  AC-09 要「一键打开日志文件夹」，而三仓范围内**没有任何打开目录的命令**（`plugin-shell` 不在 `web/package.json`）。
  故 T-08 实际是两半，**登记为范围补正而不是把两个 AC 留成 TODO**。
  **desktop 半**：三个新命令 `local_settings_get`/`local_settings_set`/`local_open_place`，加 `settings::check_save_dir`、
  `dto::SettingsView`、`commands::reveal::Place`（词汇复用 `Source::label()`——开的那棵树就是读的那棵树）。
  **cloud/web 半**：`local-settings/service.js`（九个命令 + 八个正常化器 + `createMockInvoke`）、两个纯派生模块
  （`local-settings-view.js` / `local-logs-view.js`）、`LocalSettingsPage.vue`、`LocalLogsPage.vue`
  （41 行硬编码桩 → 查看器）、路由/导航/免鉴权名单、四个测试文件。
  计数 desktop **314 → 336 passed / 2 ignored**（+22 = 4+2+9+7）；web **21 文件 101 → 25 文件 166 tests**；
  两套变异表 **70/70 灭（20 Rust + 50 JS）、0 等价、0「没编译过」**，8 组阴性对照先绿（37/9/7/2 + 20/19/17/12），
  还原后逐字节一致**且树仍绿**（两个不同的断言）；`npm run build:desktop` 成功。
  **三条先灭后补**（变异表抓出的真覆盖缺口，不是放宽断言）：`lw12`（原 fixture 的 agent 树是空的 ⇒
  「只比文件名」也满足断言；改成**两棵树各有一个 `error.log`** 并逐个断言被标记的行）、
  `sv13`（mock 按**精确**级别筛也能过原断言，差别恰在级别更高的那行；补一条 `error` 记录并逐级别列出）、
  `sv08`/`sw08`（`logFiles` 不逐文件正常化；「无文件可清」不列 kept）。
  **一处登记为等价**：`sw04`（本地时区 vs UTC）只在年边界有别，本机是 `CST +0800`，普通时刻两个 getter 相同，
  所以第一版用例看不见它；改法不是放宽而是**让用例在本机自己的时区里找一个两者不同的时刻**（跨 UTC 年边界
  取四个候选 + 阳性对照——同一时刻的 UTC 拼法与之**不相等**，证明不是在比同一个字符串）。在 `TZ=UTC` 的机器上
  它是**真等价**，用例走「偏移为 0」分支而不假装测过。
  **三处结构性的东西值得单独记**：①**mock 曾是第二套服务而不是 `invoke` 替身**——它直接返回 camelCase，
  绕过正常化，于是浏览器预览能渲染出一个应用里空白的页；改成 `createMockInvoke()` 按 Rust 拼写应答、
  两侧共用同一条正常化路径（我自己的用例 `expected undefined to be null` 抓到的）。
  ②**构建抓到 166 个单测结构上照不到的一条**：重写后的查看器从 `local-logs-view.js` 导 `logKindLabel`
  （它住在 `local-settings-view.js`）——本仓 vitest **从不编译 `.vue`**，页面里的错 import 只有构建看得见，
  而构建（6.35s + 写 `dist-desktop/`）不该是唯一在看的东西；补 `desktop page imports`（逐个具名绑定比对
  模块真实导出表 + 分母守卫），变异 `wr10`/`wr11` 证明它会红。③同一个文件里
  `names a component file that exists` 的第一版正则**匹配 0 次而通过**，分母守卫（`expect(checked).toBe(loaders.length)`）
  当场把它打掉，才发现 Vite 把 `import()` 改写成 `__vite_ssr_dynamic_import__("/src/…")`（路径已解析）。
  `router.ts` 因此把路由表导出为 `desktopRoutes`——建 router 要浏览器 history，路由表不需要（本仓 vitest 无 DOM）。
  **边界**：`commands::reveal` 最后那行 `open::that` 不可测（测它就会开窗口），留常驻 `#[ignore]` 用例；
  ~~**真机手工已验证**「打开设置文件夹」与两处「打开文件夹」都到预期目录~~ → **这句 2026-09-25 收回**：
  它与本 CHG `change.md` §10（AC-08/AC-09 都把这臂标为**未执行**）相反，正确的是 `change.md`；
  实机取到的是 `open::that` **开窗**本身（配对实验：关窗读 0 → `open /tmp` 读 `[tmp]` →
  跑该 `#[ignore]` 用例读 `[Agent]`，`target` = `~/Library/Logs/WTMedia/Agent/`），
  **页面按钮被真的点过没有发生**，那一臂并入 CHG-D。读数见 `evidence/task-08-local-settings-ui.md` §7。
  本机设置页**不能浏览目录**，
  只能手输路径（无 `plugin-dialog`；`check_save_dir` 把「路径不存在」变成一句人话）——登记为**能力缺口**而非偏好；
  `main.rs` 的接线行不可断言（与 T-07 的 `DiagnosticHost::secrets` 同类），前端那一半由 `wiring` 组覆盖
  （路由名 ↔ 免鉴权名单 ↔ 导航路径 ↔ 组件文件存在），Rust 那一半以 `npm run build:desktop`（见 T-08 证据 §4）
  + `open::that` 的配对实验（同证据 §7）为准；**「点一下」的端到端仍未做**，并入 CHG-D。
  证据 `evidence/task-08-local-settings-ui.md`。

## Next

- 无。T-09 已完成，本 CHG 已关闭并归档到 `delivery/completed/CHG-20260923-058/`。
- 交给后继：①**页面点击走查**（六个动作 + 诊断包开包核对）并入 CHG-D 的干净机 `manual_acceptance`；
  ②CHG-057 归档记录里指向 `active/CHG-20260923-058` 的那条链接已随本次归档改指 `completed/`；
  ③CHG-D（`059`）的硬前置「C 关闭」已满足，但它有**一条继承阻塞 Q-01**（生产真实 Cloud 地址），
  需先有用户裁定——**不在本 CHG 内**。

## Blocked

- 无。§7 的 Q-01…Q-08 全部 `Blocking = NO`；Q-01 是 CHG-D 的继承阻塞，本 CHG 的关闭不以它为条件。

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

- T-07 后：desktop `314 passed`（起点 276，+38，逐件对账 28+4+2+4；另有 1 条 `ignored` 探针，
  **不计入 passed**）；三组变异各带阴性对照（未变异字节必须 `0 failed`，读数 34/4/2 条），
  跑完三文件**逐字节还原**（`426ba2458357`/`d08373452616`/`c98fa6557d72`）**并各自再跑一次
  证明留下的是绿的树**；`cargo check` 非测试警告 **27**（与 T-05/T-06 同，`grep -c '^warning'` 读 28）。
  真机探针（只读、写进替身 HOME）读回 **6 条**（2 信封 + 4 日志）、归档 1593 字节、摘要值
  `87159bd6…` 与 `.sha256` 首字段逐字符相同；扫描模式**阳性对照 5/5**，真归档 **0 命中 / 1593 字节 / 4 条目**，
  两个凭据 `present=false`；真机两棵树的根不同（`.local/logs` 与 `~/Library/Logs/WTMedia/Agent`）。
  该探针**保留**为常驻 `#[ignore]` 用例（与 T-05/T-06 的「跑完即撤销」不同，理由见证据）。

- T-08 后：desktop `336 passed / 0 failed / 2 ignored`（起点 314，+22 = 4+2+9+7）、web `25 文件 / 166 tests`
  ——**两条都是在已提交的字节上复核的**（`5ee840c` / `bb0136f` 之后重跑；desktop 工作树除 13 个既有脏文件外干净、
  无变异残留字节，web 工作树除未跟踪的 `dump.rdb` 外干净）；两套变异表 70/70 灭、8 组阴性对照先绿、
  逐字节还原且**还原后各组再跑一次仍绿**；`npm run build:desktop` 成功。
  **未跑** workspace 门禁——与 T-05/T-06/T-07 同，留待 T-09 的关闭门禁（同集合阳性对照）。

- T-09 后（关闭门禁，归档前的同一棵树）：三个校验器全绿（`Active CHG: CHG-20260923-058` /
  快照 2159 字符 / 10 个 skill 源）；`unittest discover` **69 tests / 4 failures**，四个失败项**名字**
  与 `git archive HEAD` 的同集合阳性对照**逐名相同**——对照树取在真实 `wt-media/` 之内，
  故路径敏感的兄弟仓用例不会静默 `skipTest`（那正是 CHG-057 把 4 条读成 2 条的原因）。
  三仓现取读数：agent `Ran 377 tests … OK`、desktop `336 passed; 0 failed; 2 ignored`、
  web `25 文件 / 166 tests`；见 `evidence/test-summary.md`。
  **端到端（出货包）**：稳定名 `desktop.log` 落盘、强制轮转产出 `desktop.log.2026-09-24-23`
  并**重建**活文件、15 天前归档被删而 1 天前的留下、九个新命令同时在内嵌前端产物（9/9）
  与出货二进制里（且两个页面 chunk 名作为内嵌资源键出现在二进制中）；单实例守卫用
  **同一调用路径的配对观测**证得——对照（无同伴）存活且 +3 行、受试（有同伴）退出码 0 且 +0 行。
  `open -a` 那个观测方式**被否证**：LaunchServices 层就不会起第二个进程，它什么都证明不了。
  **未做**：页面点击走查六个动作与诊断包开包核对——执行时会话锁定（`CGSSessionScreenIsLocked = Yes`）
  且无 System Events 权限，没有点击通路；该臂并入 CHG-D 的干净机 `manual_acceptance`。
  回写由先失败检查钉着（8/8 事实进基线、4/4 旧口径清零、5/5 阳性对照在活）；归档后**主动扫两遍**：
  字符串扫描档外 **2 → 0**（档内 3 处判为 T-01 的过去时命令，照 CHG-057 先例保留）、
  链接 resolve 分母 62 坏 **0**——并抓到一条字符串扫描**结构上**看不见的坏链
  （`../completed/` 在移动后成了 `completed/completed/`）。
  详见 `evidence/task-09-writeback-and-archive.md`。
- **归档后核对记录时抓到一条自相矛盾，已更正**（2026-09-25）：本文件 T-08 段与
  `evidence/task-08-local-settings-ui.md` §3 各有一句「**真机手工已验证**…三个按钮都打开了预期目录」，
  而 `change.md` §10（AC-08/AC-09）与 §13 第 5 项把**同一臂**记为**未执行**。同一份归档两处相反，
  以 `change.md` 为准，那两句**收回**（原文留删除线 + 收回说明，不抹掉）。
  同时把**确实取得到**的那一半做实：`open::that` 开窗由**配对实验**证到——
  关掉全部 Finder 窗口读 `0`（控制：探针能读出「无」）→ `open -a Finder /tmp` 读 `[tmp]`
  （控制：窗口能与哪一次 open 对上）→ 跑常驻 `#[ignore]` 用例 `reveal_opens` 读 `[Agent]`，
  窗口 `target` = `~/Library/Logs/WTMedia/Agent/`，与 `agent_directory()` 解出的同一路径。
  取证时会话处于锁定态，锁定不阻止窗口被创建，只让人看不见——**「有窗口」与「有人看见过」是两件事**。
  该用例自身还有一处精度已登记：`reveal.rs:336` 的 `assert_eq!(opened, …)` 结构上不可能失败
  （比的是 `reveal()` 内部算出的同一表达式），真正的内容在 `:334` 的 `.expect(...)`。
  故读数由窗口计数承担。改那行属于新任务——**C 已归档，运行时代码不在本 CHG 内再动**。
  未证的三件（四个按钮被点过、`local_open_place` 经 IPC、另外三个「打开文件夹」）**不重复计数**，
  仍在 §12「未做」里，并入 CHG-D。证据 `evidence/task-08-local-settings-ui.md` §7。

## 记录口径的一处更正

- `change.md` §9 的 `- [ ]` 复选框是**立项时的分工清单，不是进度跟踪器**：执行期间它**不逐任务回勾**
  （T-02 已 DONE 而它的框长期未勾），进度以 §8 任务状态列与本文件为准，免得两处口径互相打架。
  **关闭时一次性勾齐**——此刻每一项都确实完成，全勾才是准确状态；这条只适用于关闭时，不适用于执行期间。
