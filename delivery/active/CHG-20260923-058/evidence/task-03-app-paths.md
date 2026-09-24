# Evidence: T-03 Desktop 运行目录解析（`AppPaths`）

## Purpose

`src-tauri/src/app_paths.rs`（新模块，753 行）+ `main.rs` 一行 `mod app_paths;`。
给出 Desktop 自己拥有的**四个目录**（data / versions / logs / cache）在**装机态**与**开发态**下的位置，
以及每个目录「能不能写」的诚实回答。本 Task 只交付解析面与 IO 边界，**消费方在 T-04/T-05**。
commit：`wt-media-desktop` `3a0ea08`。

## Method

```bash
cd wt-media-desktop && bash scripts/test.sh        # 起点 160 passed，只增不减
cd wt-media-desktop/src-tauri
rustfmt --edition 2021 src/app_paths.rs            # 只格式化单个文件（本仓不是 rustfmt-clean）
cargo test app_paths                               # 本模块 16 条，0 skipped
# 12 个实现变异：逐个改一处，跑 `cargo test app_paths`，跑完把文件还原并断言逐字节相同
```

## Actual

### 四个根（装机态 / 开发态）

`manifest_dir` 是 crate 目录（`CARGO_MANIFEST_DIR` = `src-tauri/`），与 T-02 落盘的
`src-tauri/.local/logs/desktop.log` **同一个基准**。

| 根 | 装机态 | 开发态 |
| --- | --- | --- |
| `Root::Data` | `~/Library/Application Support/WTMedia/Desktop` | `<crate>/.local/data` |
| `Root::Versions` | `…/Application Support/WTMedia/Desktop/versions` | `<crate>/.local/data/versions` |
| `Root::Logs` | `~/Library/Logs/WTMedia/Desktop` | `<crate>/.local/logs` |
| `Root::Cache` | `~/Library/Caches/WTMedia/Desktop` | `<crate>/.local/cache` |

形状**照抄 Agent 的 `runtime/paths.py`**（`wt-media-agent/src/wt_media_agent/runtime/paths.py`，本 Task 读的原文）：
`INSTALLED_DATA_DIR = ("Library","Application Support","WTMedia","Agent")`、`versions_dir = data_dir/"versions"`、
开发态 `.local/data` 与 `.local/logs`。逐条对应关系：

- Desktop ↔ Agent 的组件层同级：`WTMedia/Desktop` ↔ `WTMedia/Agent`，避免「一次清理摸到另一个组件的文件」。
- versions 在**数据根之内**，两侧同一规则（Agent 是 `versions_dir = data_dir / "versions"`）。
- 装机态数据根**就是**组件目录、开发态却要下沉一层（`.local/data`）——这条不对称**是照抄 Agent 的**，
  不是这里另立的规矩；写得整齐一点反而会让读惯另一个仓的人惊讶。
- **一处有意不照抄**：Agent 的 `resolve()` 有 override 分支（`data_dir` 赢了就整体跟着走）；
  Desktop 这四个根**没有 override 通道**，因为 AC-08 的「保存位置」是**素材下载/成片输出目录**（用户数据，
  由 T-04 的设置承载），不是这四个根。两者不可混为一谈，见下「登记的边界」第 5 条。

### 三个公开函数，一条分工

`directory()` **纯**（不碰文件系统、不读环境变量）；`resolve()` 面向调用方收拢四个根；
`prepare()` 是**唯一**碰文件系统的部分（`create_dir_all` + 真写探针）。
**读方只用 `directory()`，写方才用 `prepare()`**：查看占用不该是把缓存目录创建出来的理由。

### 测试计数（只增不减）

| 侧 | 起点 | 现在 | 差额 |
| --- | --- | --- | --- |
| desktop | 160 passed | **176 passed** | **+16**（全部为新模块用例，0 删除） |

16 条逐条（`cargo test app_paths`，**0 skipped**——注意 `a_root_that_exists_but_cannot_be_written`
那条的前提在本机成立，故它真的跑了断言而不是被跳过）：

| 用例 | 钉住什么 |
| --- | --- |
| `the_installed_layout_is_the_architecture_baselines` | 四条装机态路径逐个字面量 |
| `the_development_layout_is_under_the_crates_local_directory` | 四条开发态路径逐个字面量 |
| `the_log_root_is_the_logging_modules_own_answer` | Logs 与 `logging::paths::directory` **两侧都对得上**（委托而非复述） |
| `cache_is_never_inside_the_data_root` | cache 不在 data 之下、**且** versions 在 data 之下（一对，反向也钉住） |
| `each_layout_reads_one_input_and_ignores_the_other` | 四个根 × 两态：装机态不落 manifest、开发态不落 home |
| `the_four_roots_are_distinct` | 两两互不相同（返回同一个路径的变异否则可蒙混过关） |
| `resolve_gathers_the_four_roots_directory_reports` | `resolve` 的四个字段逐个等于 `directory` |
| `an_installed_layout_without_a_home_is_an_error` | 拒绝；**并断言被拒绝的那个替代方案是相对路径** |
| `a_development_layout_resolves_without_a_home` | 开发态不需要 home（`None` 与 `Some` 结果相同） |
| `prepare_creates_the_root_and_reports_the_same_path` | 四个根各自创建并回报同一路径 |
| `preparing_one_root_does_not_create_the_others` | 懒创建：准备 data 不产生 versions/logs/cache |
| `prepare_is_repeatable` | 同日第二次启动不因目录已存在而失败 |
| `prepare_leaves_no_probe_file` | 探针不留残留 |
| `a_stale_probe_file_does_not_make_the_root_unusable` | 崩溃残留的探针不被误判为不可写 |
| `a_root_occupied_by_a_file_is_an_error_rather_than_a_panic` | `Err` 而非 panic，且 `kind == AlreadyExists`、root 与 path 都被点名 |
| `a_root_that_exists_but_cannot_be_written_is_an_error` | 只读目录 ⇒ `PermissionDenied`（前提自证，不成立则 skip） |

### 实现变异：12/12 全灭

`rustfmt` 之后**重跑了一遍**，所以这张表指的就是将提交的那份字节（跑完断言文件逐字节还原）。

| # | 变异 | 判据（打掉它的用例） |
| --- | --- | --- |
| M1 | cache 改放 `Application Support` | `cache_is_never_inside_the_data_root`、`the_installed_layout…`、`the_four_roots_are_distinct` |
| M2 | versions 直接返回数据根 | `the_development_layout…`、`the_installed_layout…`、`the_four_roots_are_distinct`、`preparing_one_root…` |
| M3 | 开发态 data 分支读 home | `each_layout_reads_one_input…`、`a_development_layout_resolves_without_a_home`、`the_development_layout…` |
| M4 | 装机态 data 分支读 manifest | `each_layout_reads_one_input…`、`an_installed_layout_without_a_home…`、`the_installed_layout…` |
| M5 | Logs 在这里自己拼、组件拼成 `Agent` | `the_log_root_is_the_logging_modules_own_answer`（**等** 4 条） |
| M6 | `resolve` 不再拒绝缺 home | `an_installed_layout_without_a_home_is_an_error` |
| M7 | `prepare` 去掉写探针 | `a_root_that_exists_but_cannot_be_written…`、`a_stale_probe_file…` |
| M8 | 探针改用 `create_new` | `a_stale_probe_file_does_not_make_the_root_unusable` |
| M9 | `prepare` 顺手把四个根都建了 | `preparing_one_root_does_not_create_the_others` |
| M10 | 开发态 data 丢掉 `data` 这一层 | `the_development_layout…`、`cache_is_never_inside_the_data_root` |
| M11 | 吞掉 `create_dir_all` 的错误 | `a_root_occupied_by_a_file_is_an_error_rather_than_a_panic` |
| M12 | `NoHome` 的文案不再提 HOME | `an_installed_layout_without_a_home_is_an_error` |

M5 值得单独说：去掉委托、在这里自己拼路径时，**只有** `the_log_root_is_the_logging_modules_own_answer`
是那个「专门为漂移而写」的用例，另 4 条是顺带命中——所以委托这件事不是装饰。

### 定向检查（都带分母与阳性对照）

1. **本模块不读环境变量**（这是「注入式」的实质，不是风格）：
   `grep -nE 'env::var|env!\(|home_dir|Path::home|var_os' src/app_paths.rs` 分母 753 行 →
   **1 命中**，`app_paths.rs:130`，是**模块 doc 里的散文**（`/// test that called `std::env::home_dir` would…`）。
   去掉注释行后 **0 命中**；同一条去注释模式在 `main.rs` 上 **3 命中**（`:40`/`:194`/`:195`，真读 `WT_MEDIA_*`、
   `HOME`、`CARGO_MANIFEST_DIR`）⇒ 模式抓得住，本模块的 0 是真 0。
2. **没有第二处拼这两个系统目录**：`grep -rn 'Application Support\|Caches' src --include=*.rs` 排除本模块后
   **0 命中**。所以这四个根目前只有一处定义。
3. **与磁盘上的真实目录对得上**：本机 `src-tauri/.local/logs/` 实际存在（T-02 真机启动留下的
   `desktop.log`，248 字节），而 `directory(Root::Logs, "", Development, manifest_dir)` 给出的正是
   `<crate>/.local/logs`——纯规则的答案与 T-02 真机落盘的目录是同一条路径。
4. **警告增量**：非测试构建 `cargo check` **9 → 23**（+14，全部是本模块的 `never used`/`never constructed`）；
   测试构建 `cargo test --no-run` 里本模块 **0 条**——因为 16 条用例把每个条目都用到了。
   这 14 条是「模块已写好、消费方还没到」的必然产物，T-04（设置落盘）与 T-05（只读命令）会消化掉，
   且仓内既有的四个空壳（`filesystem`/`secure_store`/`system`/`updater`）本来就是同一状态（各 1 条）。
   **如实登记，不写 `#[allow(dead_code)]` 去盖掉它**。

### 格式

本仓**不是 rustfmt-clean**（见 `.ai` 记忆与 CHG-057 的先例），所以只对**单个文件**跑了
`rustfmt --edition 2021 src/app_paths.rs`，跑完 `--check` 通过；`git status` 全程只有
`app_paths.rs`（新）+ `main.rs`（**一行** `mod app_paths;`），没有第二处被动过。

## 登记的边界（不静默吸收）

1. **cache 放在 `~/Library/Caches` 而不是数据根里面——这是一条设计裁定，T-09 回写基线时必须跟着改。**
   现有架构基线 §5.8 的目录树写的是「用户数据目录内部再分三类：`data/`、`logs/`、`versions/`」，
   T-09 计划往里加 `cache/`；按本 Task 的实现，加的位置**不是**数据根内，而是
   `~/Library/Caches/WTMedia/Desktop`（开发态 `<crate>/.local/cache`）。理由：清理命令的全部工作就是删文件，
   而里程碑的失败行为明写「升级或清理删除业务数据」；cache 与 `settings.toml` 同父，等于把这条禁令
   押在「白名单永远对」上，而分到另一棵树里，删错东西需要的是**路径**错而不是**名单**错。
   macOS 另有同向的理由：`~/Library/Caches` 不进 Time Machine、系统可自行清理，这正是「可再生」的定义。
2. **`PROBE_PREFIX` 的字面量在两个模块各存一份**（`logging::paths` 与 `app_paths`，都是
   `.wt-media-write-probe-`）。刻意同形，让任意一个目录里看到的 dot-file 只一种；改名只影响残留文件的**名字**，
   不影响任何规则。不为此把 `logging::paths` 的私有常量开成 `pub`（那会动到 T-02 已验收的字节）。
3. **`Root::Versions` 在数据根之内 ⇒ 创建 versions 会连带创建它的父目录 data**。这是文件系统的性质，
   不是第二条规则（用例只钉住反方向：建 data 不建 versions）。
4. **Windows 未覆盖**（承 `logging::paths` 的既有登记）：`~/Library/...` 是 macOS 形状，没有量过 Windows 布局。
5. **四个根没有 override 通道**（Agent 有 `data_dir` 这一支）。AC-08 的「保存位置」是素材下载/成片**输出**目录，
   属用户数据（T-04 的设置面），**不是**这四个根之一。T-08 前端与 T-04 设置都不得把它接成「改运行目录」。
6. **Agent 的日志树没有在这里命名**。Q-08 已定「Desktop 侧的只读命令覆盖两棵树」，但那是 T-05 的读取面；
   本模块只有 Desktop 自己的四个根。T-05 要给 `~/Library/Logs/WTMedia/Agent` 找一个住处（是加一个 `Root`
   还是另有常量），**不要默认它已经存在于此**。
7. `Root::name()` 对 `Data` 是**两个名字**：装机态它是组件目录（`Desktop`），开发态是 `.local/data`。
   模块 doc 写明，免得后来者以为是笔误。
