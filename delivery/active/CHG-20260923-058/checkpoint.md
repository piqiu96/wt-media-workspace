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

## Next

- T-05 `UserSettings` 的**消费面**（只读命令）：可用空间、缓存占用、日志占用、列出日志文件
  （含两棵树，见 Q-08）；`logging::rolling` 补公开读取面；**读取失败必须是错误而非 0 MB**
  （AC-06）。T-03 留的开口要在这里关：Agent 的日志树 `~/Library/Logs/WTMedia/Agent`
  在 Desktop 侧**尚无住处**，不要默认它已经存在。

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

## 记录口径的一处更正

- `change.md` §9 的 `- [ ]` 复选框是**立项时的分工清单，不是进度跟踪器**（T-02 已 DONE 而它的框仍未勾）。
  进度以 §8 任务状态列与本文件为准；§9 不逐任务回勾，免得两处口径互相打架。
