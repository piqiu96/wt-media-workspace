# T-05 证据 — `config_online → 产物/config`（产物带配置，且冻结侧真的读它）

日期：2026-09-25 ｜ 仓：`wt-media-agent` + `wt-media-desktop`（各一个 commit）
｜ 覆盖验收点：**AC-05**，以及 **AC-09 的一半**（配置来自 `config_online/`、不含开发态路径）

## 1. 交付了什么

**`wt-media-agent`**（一个 commit）

- `src/wt_media_agent/runtime/config.py`：`default_config_dir(*, frozen=None, exe=None)` 由**可执行文件的
  位置**推导配置目录（`<exe_dir>/../Resources/config` 优先，其次 `<exe_dir>/config`），两个候选都没有时
  回落到检出路径并**发一条 WARNING**（指名找过哪些位置）。`frozen`/`exe` 也穿透 `_read_document` 与
  `load_config`，于是一个用例可以让加载器**完整地**扮演一次打包进程（env > file > default 三层都走）。
  模块里那段「frozen 时指向解包目录、反正不存在，也没关系」的旧陈述被改写——它正是这次要修的那件事。
- `scripts/build_desktop_sidecar.py`：`sync_config()`（**先删后拷**的整目录替换 + **读回比对**）与
  `mirror_differences()`；`--config-dir` 可以单独使用（`--output-dir`/`--manifest` 变成可选且必须成对），
  因为产物里的那个目录要等 `cargo tauri build` 之后才存在。

**`wt-media-desktop`**（一个 commit）

- **新增 `scripts/stage-release-config.sh`**：把 `config_online/` 暂存进一个已打包好的 `app`。
- `scripts/build-release-macos.sh`：在 `cargo tauri build` **之后**、`repair-macos-signing.sh` **之前**调它。
- `scripts/verify-release-macos.sh`：对 DMG 里的产物做 `diff -r`（AC 的判据），外加两条防「空集通过」的判据。
- `scripts/repair-macos-signing.sh`：**订正一段成因写错的注释**（见 §5 第 5 条）。

## 2. 先红读数

转录：`task-05-red.out`、`task-05-frozen-reading.out`

1. **产物里今天根本没有 Agent 配置**：`output/…/WT Media.app/Contents/Resources/` 只有 `resources/`；
   AC 的判据命令因此以 `No such file or directory` 收场（`exit=2`）——不是「有差异」，是「没得比」。
   开发树里也没有：`bundle.resources` 只有 Desktop 自己的 `resources/*.toml`。
2. **修复前那份随包产物，真进程跑出来的读数**（`task-05-frozen-reading.out` 的 `pre` 段）：
   夹具把 `Contents/Resources/config/agent.toml` 放在它该在的位置、只改一个值
   `local_api.host = "localhost"`（内置默认是字面量 `127.0.0.1`，且没有任何环境变量在这里设它），
   端口走环境变量的临时端口。**它报 `listening on 127.0.0.1:…`**——文件没被读。
   两件事由同一条读数一起证明：端口来自环境（`18781`，不是文件里的 `8765`），主机来自内置默认值。

## 3. 修好之后：同一条夹具、真进程、真包布局

`task-05-frozen-reading.out` 的 `fixed` 段：**报 `listening on localhost:…`**。

对照组只有一处不同——**二进制**：`pre` 是 HEAD 的随包产物（`f92cbdee…`，最后一次发布构建），
`fixed` 是含本次改动的新构建（`d7f8040c…`）。夹具、目录布局、环境变量、跑法都一样。
两侧都没有碰过 8765 / 18080 / 54345。

同一条转录里还有两条辅助读数，都在这里如实登记：

- **`raw-build`：刚构建、没重签的产物在本机根本起不来**（`Failed to load Python shared library … different
  Team IDs`）。这不是夹具的问题，是**打包中间态**的问题：T-03 登记的「随包 onefile 在本机起不来」，
  今天量到的是「**未重签的构建产物**起不来，按发布流程重签之后就能起来」——`repair-macos-signing.sh`
  里那两步（`--remove-signature` + `--force --sign -`）正是修它的那一步。
- **`alias`：第一版夹具（`host = 127.0.0.2`）的读数**。macOS 只绑 `127.0.0.1`，除非加 `lo0` 别名（要
  sudo，不做），所以进程 `OSError: [Errno 49] Can't assign requested address` 自己退了。它其实也在
  说明配置被读了（进程去绑文件里那个地址），但「失败」不是一条看得清的成功读数，所以换了 `localhost`
  夹具把 `pre`/`fixed` 重跑了一遍。这条订正留在这里，而不是被换掉。

## 4. 发布闸门：`verify-release-macos.sh` 的五个臂

转录：`task-05-gate.out`。跑法见 `/tmp/chg059/t05/gate_arms.sh`：**闸门脚本是真的那份**（复制到一个
伪造的工作区根下运行，它自己算出来的每个路径都照常），DMG 里的 app 也是真的那份（`output/` 里最后一次
发布构建的结果），配置按管线的顺序加进去——先加进 `Contents/Resources`，再签外层。

| 臂 | 布局 | 读数 |
|---|---|---|
| `green` | 产物带配置、与 `config_online/` 逐字节相同 | `diff -r` 无输出，退出 0；打印「a 2-file mirror of config_online/」 |
| `changed` | 产物里的 `environment` 改成 `staging`（合法 TOML、签名**有效**） | `diff -r` 指名 `agent.toml` 第 15 行，退出 1 |
| `absent` | 产物里没有 `Contents/Resources/config`（= 本次修复前的产物） | 退出 1，指名缺哪个目录，并指向 `stage-release-config.sh` |
| `empty-source` | 产物正常，但 `config_online/` 是空目录 | 退出 1：「a mirror of it would prove nothing」 |
| `resealed` | 签完之后再改密封区里的配置 | `codesign --verify --deep --strict` 自己就报 `a sealed resource is missing or invalid`，并指名 `Contents/Resources/config/agent.toml` |

两条结论：

- `changed` 那一臂的两侧**签名各自都是合法的**，签名验证**不报**——判据只能是内容比对。这与 T-04 §6
  的描述同源：签名抓「被改坏」，抓不到「两边各自合法、只是互不相符」。
- `resealed` 那一臂是**位置裁定的实测依据**：`Contents/Resources` 的封条盖住配置，所以它必须在
  外层签名**之前**进包（D-15）。顺序反了不是「没封住」，而是把外层签名弄坏。

## 5. 设计裁定

1. **D-12 位置：产物里的 Agent 配置落 `Contents/Resources/config`。** 依据是 §4 的 `resealed` 臂
   （封条盖住它）与 T-04 §6 的实测（`Contents/Resources` 由外层签名封住，`Contents/MacOS` 里的数据
   文件不被封）。它同时也是 Tauri 放资源的那个目录，所以 `bundle.resources` 本来也能送来——**但那条路
   被实测否掉，见第 5 条**。
2. **D-13 推导：冻结侧由可执行文件的位置推导配置目录，不引入任何环境变量或参数开关**（ADR-0016 §6
   明禁）。两个候选（`.app` 布局优先，其次是可执行文件旁边的 `config/`）都无法命中时**回落到检出路径
   并报 WARNING**：静默回落会让「这次修的东西又没了」表现得和「配置正确」一模一样，而这正是本次缺陷
   原来的样子。
3. **D-14 替换是整目录、且读回比对。** 先删后拷（不是合并），因为 `config_online/` 是**替换源**：
   从源里删掉的文件必须也从产物里消失，否则「1:1 镜像」只在第一次拷贝那天成立。拷完把文件集合与逐字节
   都比一遍，不一致就拒绝构建；并把**拷了哪些文件**报出来（分母）。
4. **D-15 顺序：`cargo tauri build` → 暂存配置 → `repair-macos-signing.sh`。** 与 T-04 写 sidecar 记录
   的位置、顺序完全一致（同一段理由：外层签名封住 `Contents/Resources`）。
5. **被否掉的那条路（`bundle.resources: config/*`）与它否掉的原因。** 先做的是那条路，代价是实测出来的：
   Tauri 拒绝一个匹配不到任何文件的 glob，`cargo build` 直接失败——
   `glob pattern config/* path not found or didn't match any files.` 于是**任何一个还没跑发布步骤的
   检出**（干净 clone、`cargo test`、`cargo tauri dev`）都编译不过。**发布步骤不该长在每个人的编译里**，
   所以配置改为在**产物**上暂存。这一条留在证据里，因为「Tauri 也能送」是下一次会有人重新提出的想法。
6. **顺带订正一处成因写错的注释。** `repair-macos-signing.sh` 原写「Tauri 的硬运行时签名让 macOS 26
   拒绝那个嵌套库」。实测：**未重签的构建产物**（Tauri 还没碰过）就已经带着 `flags=0x10002(adhoc,runtime)`
   且起不来，而 PyInstaller 6.22.2 的 `utils/osx.py:413-421` 只在 identity 为假时才跳过硬运行时——
   我们传的是字面量 `-`，它是真值。⇒ 加这个标志的是**构建脚本自己的参数形态**，不是 Tauri。注释已按
   这条实测改写（`evidence/task-05-packaging.out` 第 3 节）。**只改注释，不改行为**：行为上「重签」这一步
   今天仍然必要，且是让 sidecar 能起来的那一步。

## 6. 变异表 17/17

转录：`task-05-mutations.out`（`/tmp/chg059/t05/mutate_t05_agent.py`）。每轮先跑控制行（未变异的树上
每条被点名的用例都必须绿），再逐个变异、每个变异只跑它点名的那一条用例；跑到的用例数不是 1 就不计数；
每轮结束把文件从原样复原并比对。

| # | 变异 | 必须被打掉的用例 | 读数 |
|---|---|---|---|
| M1 | 回到修复前的形状：不看 `frozen`，恒返回检出的 `config/` | `…_reads_the_configuration_in_its_resources` | 打掉 ✓ |
| M2 | 忽略传入的 `exe`，恒用本进程的 `sys.executable` | 同上 | 打掉 ✓ |
| M3 | 候选顺序反过来（先看 exe 旁边） | `…_the_app_layout_wins_over_a_directory_beside_the_executable` | 打掉 ✓ |
| M4 | 找不到时不发 WARNING | `…_a_bundle_with_nothing_shipped_falls_back_and_says_so` | 打掉 ✓ |
| M5 | 忽略 `frozen`：任何进程都按「在包里」解析 | `…_a_checkout_ignores_a_bundle_shaped_directory` | 打掉 ✓ |
| M6 | 去掉「exe 旁边」那个候选 | `…_reads_a_flat_configuration_next_to_the_executable` | 打掉 ✓ |
| M7 | `sync_config` 改成合并（只覆盖同名文件、不删多余文件） | `…_a_copy_over_an_existing_directory_drops_what_the_source_lost` | 打掉 ✓ |
| M8 | 镜像校验只比文件名、不比字节 | `…_names_every_way_a_copy_can_disagree` | 打掉 ✓ |
| M9 | 镜像校验漏掉「多出来的文件」这一支 | 同上 | 打掉 ✓ |
| M10 | 拷完不读回校验（整段去掉） | `…_a_copy_that_did_not_reproduce_the_source_is_refused` | 打掉 ✓ |
| M11 | 不给「源目录不存在」设错误 | `…_syncing_from_a_source_that_is_not_there_is_an_error` | 打掉 ✓ |
| M12 | 不报告拷了哪些文件（返回空表） | `…_the_product_configuration_is_a_wholesale_mirror` | 打掉 ✓ |
| M13 | 敏感键按整条点路径比，而不是叶名 | `…_finds_both_shapes_it_claims_to` | 打掉 ✓ |
| M14 | 敏感键大小写敏感（去掉 `.lower()`） | 同上 | 打掉 ✓ |
| M15 | 不看值里的 userinfo（只看键名） | 同上 | 打掉 ✓ |
| M16 | 什么都不给也算成功（去掉「无事可做」的报错） | `…_a_call_with_nothing_to_do_is_an_error` | 打掉 ✓ |
| M17 | 不检查 `--output-dir`/`--manifest` 必须成对 | `…_the_build_arguments_still_go_together` | 打掉 ✓ |

M10 是**为它补过用例的**：把读回校验整段删掉时没有任何用例会红（拷对了就是拷对了），那条分支等于没有
覆盖。补法不是改断言，而是让**拷贝本身说谎**——用 `mock.patch.object` 把 `shutil.copytree` 换成
「拷完再删掉 `agent.toml`」的版本，于是「copy 只看起来成功」这一条真的有读数。

## 7. 凭据：AC-05 的另一半

`config_online/` 是「产物里的配置」的**逐字节来源**（§4 的 `green` 臂就是这条相等性），所以扫描它等于
扫描产物。扫描规则与加载器同一条：**叶名**（大小写不敏感）落在 `SENSITIVE_KEY_NAMES` 里，**或**某个值
里带 userinfo（`scheme://user:password@host`）——后者是键名检查看不见的那一类泄漏。

- 分母：`config_online/agent.toml` 里 **12** 个叶子，命中 **0**。
- **阳性对照**（同一次运行里种下）：一个 `[agent] Runtime_Token = "…"` 与一个
  `base_url = "http://user:hunter2@cloud.invalid"` ⇒ 两条都被抓到，且扫描到的叶子数是 3 而不是 0。
  种的是**嵌套 + 大小写混合**的键，因为那正是「叶名 + 大小写不敏感」与「整条点路径 + 大小写敏感」
  两种规则唯一能区分开的地方。
- 因此本轮结论的**范围**是：`config_online/` 今天不带凭证键、不带 userinfo ⇒ 产物也不带。
  它**不**证明别的通路（例如日后有人往 `[cloud] base_url` 里塞一个带凭据的地址而不带 `@`——
  那是格式问题，不是这条规则能覆盖的）。这类判定仍归 D-05：凭证只走环境变量。

## 8. 读数

| 项 | T-04 结束时 | 现在 | 差 |
|---|---|---|---|
| agent `scripts/test.sh` | 382 OK（`git archive HEAD` 的树，本次实测） | **397 OK** | +15 |
| desktop `cargo test --workspace` | 363 passed / 0 failed / 5 ignored | **363 passed / 0 failed / 5 ignored** | +0（本次未改任何 Rust 文件） |
| desktop 编译警告 | 7 | 7 | +0（同上；T-04 的那次读数是同一份源码） |

新增 15 条：`BundledConfigDirTest` 5 条（`.app` 布局 / 平铺布局 / 两者都在时的顺序 / 没有配置时的
回落与 WARNING / 检出忽略包形状的目录）、`ConfigSyncTest` 5 条（整替镜像 / 删掉多余文件 / 源不存在 /
校验能指名三种差异 / 拷贝说谎必被拒）、`ConfigSyncCliTest` 3 条（只暂存不冻结 / 无事可做要报错 /
构建参数必须成对）、`ShippedConfigurationTest` 2 条（不带凭证 + 扫描的阳性对照）。

## 9. 未覆盖项与已知极限（登记，不静默吸收）

1. **没有真跑过一次完整出包**（`cargo tauri build` → 暂存 → 签名 → 打 DMG → 闸门）。§4 的五个臂用的
   是真闸门脚本与真产物 app，但 DMG 是手工造的：那条 `bundle.resources`→产物的**唯一没被量到的一步**
   （Tauri 的资源拷贝）在本方案里已经不存在了（配置不进 `bundle.resources`，见 D-15 第 5 条），
   而「整条出包脚本连起来跑通」与 T-04 §9 第 6 条同一性质，**未做**。
2. **`--config-dir` 指向的目录若不存在**（例如 `cargo tauri build` 没产出 `Contents/Resources`）：
   `stage-release-config.sh` 的 `test -d` 会先拦，但 `sync_config` 自己会**创建**它（`copytree` 建父目录）。
   也就是说脚本层挡住了、库函数层不会报错——这个错配没有用例。
3. **`sync_config` 的只读文件系统 / 权限失败**没有用例（本机造不出来），它会是 `shutil` 自己的异常。
4. **Windows 与 Linux 的产物布局未测**（Q-03）：`stage-release-config.sh` 只在 macOS 出包路径上被调用；
   `default_config_dir` 的 `.app` 候选在别的平台不会命中，会走「exe 旁边的 `config/`」那条候选——**那条
   候选本身在本机也只有单测覆盖**（没有一个真产物是那个布局）。
5. **开发树里的冻结 sidecar**（`target/debug` 下那份）会命中「找不到随包配置」的 WARNING 并回落到默认值。
   这是**如实**的读数（开发树确实没有随包配置，Desktop 照常用环境变量配它），但本任务没有对它做真机读数。
6. **`load_config` 的三层优先级在打包场景下只被单测覆盖**：`WT_MEDIA_LOCAL_API_PORT` 覆盖文件里 `8765`
   这件事在 §3 的真机读数里**顺带**发生过（`pre`/`fixed` 都绑的是环境变量的端口），但「环境变量覆盖
   文件里的每一个键」没有逐键量过（那是 CHG-056 的 `EnvLayerTest` 的覆盖范围）。
