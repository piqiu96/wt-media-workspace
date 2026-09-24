# Evidence: T-04 用户设置持久化（`UserSettings` / `settings.toml`）

## Purpose

`src-tauri/src/settings.rs`（新模块，817 行）+ `main.rs` 一行 `mod settings;`。
交付 AC-05 的三件事：设置落在**用户数据目录**、替换是**原子**的、**损坏时保留原文件并明确提示**
（不得静默清空）。消费方（只读命令、设置页）在 T-05/T-08，本 Task 只交付读写面与它的边界。
commit：`wt-media-desktop` `7825a75`。

## Method

```bash
cd wt-media-desktop && bash scripts/test.sh          # 起点 176 passed，只增不减
cd wt-media-desktop/src-tauri
rustfmt --edition 2021 src/settings.rs              # 只格式化单个文件（本仓不是 rustfmt-clean）
cargo test settings                                 # 本模块 22 条，0 skipped
cargo check                                         # 非测试构建警告分母
python3 /tmp/chg058/mutate_settings.py              # 16 个实现变异 + 1 个等价探针 + 自带阴性对照
```

## Actual

### 它落在哪，以及「谁创建那个目录」

| 环境 | 设置文件 |
| --- | --- |
| 装机态 | `~/Library/Application Support/WTMedia/Desktop/settings.toml` |
| 开发态 | `<crate>/.local/data/settings.toml` |

数据根由 **`AppPaths` 给**（T-03 的 `Root::Data`），本模块不自己拼系统目录——`path()` 只接受一个数据根，
`the_settings_file_lands_in_the_data_root_app_paths_resolves` 读的是 `app_paths::resolve` 而不是复述它的规则，
两个模块对「设置住哪儿」给出不同答案时会红。

**`save` 不创建那个目录**：建目录是 `app_paths::prepare` 的职责。一个会顺手把数据根造出来的设置写入者，
会把「数据根因为某个原因不在」这件事从报告变成静默。

### 三个 API，一条分工

| 函数 | 性质 | 说明 |
| --- | --- | --- |
| `path(data_root)` / `temp_path(target)` | 纯 | 只算路径；`temp_path` 公开是因为「与目标同目录」是正确性要求，不是实现细节 |
| `parse(text)` / `load(target)` | 只读 | 缺失 ⇒ `Ok(默认值)`；不可读/解析失败/版本不认识 ⇒ `Err` 且**一个字节都不动** |
| `save(target, settings)` | 写 | 先读通才写（见下）；临时文件 + `sync_all` + `rename` |
| `write_atomically(target, bytes, write)` | 私有 | 写动作作为**参数**注入，于是「写到一半中断」是可测的 |

### 坏形态一律 `Err`，原文件一律保留

| 输入 | 结果 | 原文件 | 用例 |
| --- | --- | --- | --- |
| 文件不存在 | `Ok(UserSettings::default())` | **不被创建** | `a_missing_file_is_a_first_launch_and_is_not_created_by_looking` |
| 语法错（`save_dir = /未加引号`） | `Err(Unparsable)` | 逐字节相同 | `corrupt_settings_are_an_error_and_the_file_is_left_untouched` |
| `schema_version = 2`（未来版本） | `Err(UnknownSchema { found, supported })` | 逐字节相同 | `a_file_from_a_newer_schema_is_refused_and_left_untouched` |
| `schema_version = 0` | `Err(UnknownSchema)` | — | `a_file_claiming_version_zero_is_refused` |
| 未知键 `save_dirs`（打字错） | `Err(Unparsable)` | — | `an_unknown_key_is_refused_rather_than_dropped` |
| 该位置是个**目录** | `Err(Unreadable)` | — | `a_directory_where_the_file_belongs_is_an_error_not_a_default` |

版本判定用 `!=` 而不是 `>`：**v1 是第一版**，0 与 2 同样不可读。将来加 v2 时迁移逻辑才落在这里。

### 「静默清空」的两个半边都被钉住，而不是只写进文档

里程碑禁的是「**配置写入一半损坏用户设置且静默清空**」，它是两件事：

1. **写入一半** —— 结构上消掉：临时文件 + `rename`，且**从不以写方式打开设置文件本身**。
   掉电最坏失去的是「最近一次修改」，不会留下半个文件（没有目录 `fsync`，见边界 3）。
2. **静默清空** —— 调用方拿到 `Err`、改用默认值、把默认值写回去。只在模块文档里叮嘱不够，
   所以 **`save` 读得通才写**：损坏的、别的 schema 的、打不开的文件，`save` 一律 `Err` 且原样保留
   （`save_refuses_to_replace_a_file_it_cannot_read` / `…_from_another_schema`）。
   **代价**：用户想重置必须自己删掉那个文件——而这个手动动作本来就只该由人来做。
   变异 M17 专门打掉这行前置检查，被这两条用例打死。

### 错误文案不回声文件内容

照 `config::parse_error` 的先例只保留 `error.message()`：`toml` 的 `Display` 会把出问题的**整行**渲染出来，
而那行就是内容，这条通路最终会进日志。用例 `an_error_never_echoes_the_files_contents` 自带**阳性对照**——
先断言 toml 自己的 `Display` **确实**含有那串内容（所以这个断言不是空转），再断言我们的 `Error` 不含，且**点名文件**。

### 测试计数（只增不减）

| 侧 | 起点 | 现在 | 差额 |
| --- | --- | --- | --- |
| desktop | 176 passed | **198 passed** | **+22**（全部为新模块用例，0 删除，0 skipped） |

### 实现变异：16/16 全灭 + 1 个登记为等价

harness 自带**阴性对照**：先在未变异的字节上跑同一条命令，必须报「0 failed」，否则整批读数作废。
跑完断言文件逐字节还原（`sha256:4e38ccc7b296aee5`，33 769 字节）。

| # | 变异 | 判据（打掉它的用例，摘） |
| --- | --- | --- |
| M1 | 不可读 ⇒ 悄悄给默认值 | `a_directory_where_the_file_belongs_…` |
| M2 | **解析失败 ⇒ 悄悄给默认值**（正是被禁的那条） | `corrupt_settings_…`、`a_file_from_a_newer_schema_…`、`save_refuses_…`×2 |
| M3 | 去掉 `schema_version` 检查 | `a_file_claiming_version_zero_…`、`a_file_from_a_newer_schema_…`、`save_refuses_to_replace_a_file_from_another_schema` |
| M4 | 版本检查 `>` 而非 `!=` | `a_file_claiming_version_zero_is_refused`（**只有它**——这正是写它的理由） |
| M5 | 允许未知键 | `an_unknown_key_is_refused_rather_than_dropped` |
| M6 | 错误回显 toml 整行 | `an_error_never_echoes_the_files_contents` |
| M7 | 直接写目标、不走临时文件 | `a_half_written_replacement_…` 等 6 条 |
| M8 | 临时文件放到系统临时目录 | `temp_path_is_a_sibling_of_the_target` 等 6 条 |
| M9 | 打开目标时不截断 | `a_stale_temp_file_does_not_break_the_next_save` |
| M10 | 用调用方给的版本号（不盖章） | `save_stamps_the_version_this_build_understands` |
| M11 | `save` 顺手把缺的父目录建出来 | `save_reports_a_missing_directory_rather_than_creating_it` |
| M12 | `Default` 自称 `schema_version = 0` | `the_default_is_this_builds_schema`、`an_unchosen_directory_…` |
| M13 | 「文件不存在」也报错 | `a_missing_file_is_a_first_launch_…` 等 7 条 |
| M14 | `load` 顺手把文件建出来 | `a_missing_file_…` 等 8 条 |
| M15 | 写失败后留着半个临时文件 | `a_half_written_replacement_leaves_the_previous_file_untouched` |
| M17 | 去掉「读得通才写」的前置检查 | `save_refuses_to_replace_a_file_it_cannot_read`、`…_from_another_schema` |
| M16 | **等价探针**：去掉 `skip_serializing_if` | **应当存活**，见下 |

**M16 不是变异，是等价。** 实测（把该属性去掉后打印序列化结果）：
`toml` 0.9 自己就省略值为 `None` 的键，输出仍是 `schema_version = 1\n`，没有 `save_dir` 行。
所以在这个 crate 上 `skip_serializing_if` 不承载语义，**去掉它没有可观测差别**——「存活」是预期读数而非漏洞。
属性**保留**：它把「未选择 = 键不存在」这条意图写在字段上，且换轮子/升级 crate 时不必回头再论证一次。
这条以**等价**登记，不冒充一次击杀。

### 定向检查（都带分母与阳性对照）

1. **本模块不读环境变量**（注入式的实质）：
   `grep -nE 'env::var|env!\(|home_dir|Path::home|var_os|temp_dir' src/settings.rs` 分母 **817 行 → 1 命中**，
   `settings.rs:333`，在测试模块内（`scratch()` 用 `std::env::temp_dir()` 造用例目录，`#[cfg(test)]` 起于 `:319`）。
   **非测试代码 0 命中**；同一条模式在 `main.rs` 上 **3 命中** ⇒ 模式抓得住，本模块的 0 是真 0。
2. **非测试代码不 panic**：测试模块之前 **0 命中** `unwrap()/expect()/panic!/unreachable!/todo!`（分母同 817 行）。
3. **文件名只定义一处**：`grep -rn 'settings\.toml' src --include='*.rs'` 共 **11** 命中，
   1 处是常量 `pub const FILE_NAME`（`settings.rs:70`），其余是测试字面量与
   `app_paths.rs:14/24` 的**文档散文**（`//!`，不是第二处定义）。去掉注释与测试后 **0 处**。
4. **目前没有消费方**（**如实登记，不假装已完成**）：
   `grep -rn 'UserSettings\|settings::' src --include='*.rs'` 排除本模块与 `main.rs` 的 `mod` 行 ⇒ **0 命中**。
   即 `settings.rs` 现在没有任何调用者，T-03 的 `never used` 警告里 12 条属于本模块。
5. **测试构建里本模块 0 条警告**：`cargo test --no-run` 输出中 `settings.rs` 出现 **0** 次——
   22 条用例把每个条目都用到了。非测试构建警告 **23 → 35**（+12，全为本模块 `never used`/`never constructed`）。
   **不用 `#[allow(dead_code)]` 盖掉**：消费方在 T-05/T-08，届时自行消掉。

### 格式

本仓**不是 rustfmt-clean**，故只对**单个文件**跑 `rustfmt --edition 2021 src/settings.rs`，`--check` 通过；
`git status` 全程只有 `settings.rs`（新）+ `main.rs`（**一行**），无第二处被动过。

## 登记的边界（不静默吸收）

1. **`save_dir` 的含义是「素材下载/成片保存位置」，且今天没有任何代码读它。** 这不是「已完成的设置」，
   而是「已经能安全存下来的设置」。`None` 对消费者意味着什么，由消费者决定（本模块只存选择，不做决定）。
   T-08 的页面可以查/改它，但从「页面能改」到「任务真的按它落盘」之间还差一个消费方，
   **不要在收尾时把 T-04 当成端到端可用**。
2. **不是 UTF-8 的路径存不进 TOML**：`serde` 会拒绝而不是改名，表现为 `save` 的 `Err(Unwritable)`。
   没有绕过——绕过的形态（改名、转义、base64）都会让用户看到一个不是他选的路径。
3. **没有目录 `fsync`**：`rename` 本身可能因掉电而丢失，最坏结果是**回到上一版设置**，不是半个文件。
   「文件永远可解析」这条不依赖目录 `fsync`；「这次修改一定保住」这条不承诺。
4. **`save` 不校验 `save_dir` 是否合法**（存在？可写？绝对路径？）。设置页与命令面（T-05/T-08）负责在改之前
   给出提示；模块把它当**用户意图**原文存下，不当成待执行的路径。校验写在这里会让「用户选了一个还没挂载的盘」
   变成「设置根本存不下来」。
5. **它不是四个运行目录的 override 通道**（承 T-03 边界 5）：改 `save_dir` 不得影响 `data/logs/versions/cache`
   的位置，反之亦然。T-05/T-08 接线时不得把两者接成同一个东西。
6. **`SCHEMA_VERSION` 只有一版**，所以没有任何迁移代码；`!=` 判定的含义是「本二进制只认识这一种形状」。
   加 v2 时这里要长出真正的迁移分支，而不是把 `!=` 改回 `>`。
7. **harness 自己出过一次错，值得记下**：第一版变异脚本用 `cargo test --quiet`，而 `--quiet` 会把
   逐条用例名吞掉，于是脚本把「用例失败」读成「没编译」，整批报成 0/16 存活——**读数错在工具上**。
   修法是：不加 `--quiet`、按用例名收集失败、并把「未变异字节必须 0 failed」写成脚本内建的**阴性对照**。
   与 T-02 那次的教训同形：**报「全灭」之前先证明这个判定能失败**。
