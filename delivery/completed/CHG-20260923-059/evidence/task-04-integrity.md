# T-04 证据 — 运行期完整性校验（启动前验包内记录，篡改必拒）

日期：2026-09-25 ｜ 仓：`wt-media-desktop`（一个 commit：`04f46c3`）
｜ 覆盖验收点：**AC-04**

## 1. 交付了什么

`feat(chg-059): T-04 运行期完整性校验——启动前验包内记录，篡改必拒（CHG-20260923-059）`，`04f46c3`。

**新增 `src-tauri/src/sidecar/integrity.rs`**（644 行，含模块头的判定表与三条打包事实）：
启动前读 `Contents/Resources/sidecar-manifest.json`，按 SHA-256 比对**要启动的那个文件**。

- 三种答案：`Matched`（记录与文件一致，带 version / target / sha256）、`Absent`
  （没有 sidecar，不算失败）、`Unrecorded`（有 sidecar 没有记录，**工程树容忍、包里拒绝**）。
- 拒绝带路径与原因，三条文案各自指名是什么不对：缺记录、摘要不一致（记录与实测都写出来）、
  记录写的是别的组件/别的文件名/字段不可用。
- 不新增依赖：`sha2`、`hex`、`serde_json` 已是直接依赖。

**`src-tauri/src/sidecar/mod.rs`**：`start` 改为三步——先由 `Location::of(app)` 求位置，
再 `spawn_verified`（校验 → `note` 记录 → 用**解析出的那个路径**启动），失败按
`Attempt::{Started,Unavailable,Refused}` 收口；`may_fall_back` 只放行 `Unavailable`，
`Refused` 是终点（拒绝不许被 Python 调试路径答掉）。

**打包侧一半**（同一 commit，因为这是「记录从哪来」的另一面）：
`scripts/repair-macos-signing.sh` 在 sidecar 的 ad-hoc 签名**之后**、外层签名**之前**写记录；
`scripts/package-release-macos.sh` 增加相等性判定（包内记录的摘要 vs 对随包 sidecar 的独立测量）
并在 `README.txt` 里加一行说明。

## 2. 先红读数

转录：`task-04-desktop-red.out`

保留本次全部新用例，只把 `spawn_verified` 里那次校验去掉（回到修复前的形状：解析出路径就直接启动）：

```
a_tampered_sidecar_is_refused_and_an_intact_one_is_started ... FAILED
panicked at src-tauri/src/commands/agent.rs:1766:13:
a changed byte has to be refused, not started
test result: FAILED. 0 passed; 1 failed; 0 ignored; 0 measured; 365 filtered out
```

红的是**篡改那一 arm**，而且它红的方式是「被篡改的 sidecar 真的被启动了」（脚本的标记文件出现）——
不是「编译不过」也不是「断言写错」。同一条用例在未变异的树上是绿的（控制行见 §4.1 M1）。

## 3. 包内臂：AC-04 要的那条读数

**为什么必须另造一个包**：`inside_a_bundle` 读的是**本进程**可执行文件的路径，所以
`cargo test` 出来的进程永远不是包；而真包要么靠 GUI 启动（会在用户屏幕上开窗），
要么靠伪造签名。做法是把**签名脚本真写出的 sidecar 与记录**放进一个 `.app` 布局，
再把本次的测试二进制放在 `Contents/MacOS` 里，从那里运行：

```bash
# 1. 产物副本（output/ 只读，全程不碰）
cp -R "$WORKSPACE/output/WT-Media_0.1.0_macos-aarch64/WT Media.app" /tmp/chg059/t04/packaged/"WT Media.app"
# 2. 让签名脚本在副本上真写一份记录（ad-hoc 重签 → 记录 → 外层签名 → --verify --deep --strict）
bash scripts/repair-macos-signing.sh /tmp/chg059/t04/packaged/"WT Media.app"
# 3. 造包：sidecar + 记录 + 本次的测试二进制
mkdir -p /tmp/chg059/t04/"WT Media.app"/Contents/{MacOS,Resources}
cp .../packaged/"WT Media.app"/Contents/MacOS/wt-media-agent        .../t04/"WT Media.app"/Contents/MacOS/
cp .../packaged/"WT Media.app"/Contents/Resources/sidecar-manifest.json .../t04/"WT Media.app"/Contents/Resources/
cp src-tauri/target/debug/deps/wt_media_desktop_shell-<hash>        .../t04/"WT Media.app"/Contents/MacOS/t04-under-test
# 4. 从包里跑（不是 GUI，但 current_exe() 与 resource_dir() 取到的是真实的包内值）
cd /tmp/chg059/t04/"WT Media.app"/Contents/MacOS && ./t04-under-test --ignored bundled --nocapture
```

转录：`task-04-bundle.out`。四条读数（四条 arm 都在同一个用例里，末尾还有一条复原读数）：

```
sidecar=/private/tmp/chg059/t04/WT Media.app/Contents/MacOS/wt-media-agent
record=/private/tmp/chg059/t04/WT Media.app/Contents/Resources/sidecar-manifest.json
arm 1 校验通过 version=0.2.2 target=aarch64-apple-darwin sha256=f92cbdee…（与对文件的独立 shasum 一致）
arm 2 …SHA-256 与包内记录不一致（记录 f92cbdee…，实际 8236dd64…）…
arm 3 …包内缺少记录文件 /private/tmp/chg059/t04/WT Media.app/Contents/Resources/sidecar-manifest.json…
arm 4 复原后仍为「校验通过」
```

- **arm 1 是阳性对照**（真记录 → 通过，且打印出的 sha256 与 `shasum -a 256` 对同一个文件
  的读数相同）；arm 2/3 是阴性对照；**arm 4 是必须有的收尾**——没有它，前面三条也与
  「第一次调用之后就一律拒绝」相容。
- 两条打印出的路径就是 `current_exe()` / `resource_dir()` 在真包布局下的取值，
  所以这一臂同时量了「`resolve_sidecar` 找得到文件」与「记录确实在资源目录里」——
  这两件事此前只与插件的源码比对过，没有实测过。

**对照（这条读数必须能变红）**：同一个用例从 `target/debug/deps` 运行 → 红在第一条断言，
并打印出工程树的两个路径（`target/debug/wt-media-agent` 与
`target/debug/resources/sidecar-manifest.json`）。若它在工程树里也是绿的，第一条断言等于没写。
两条读数都在 `task-04-bundle.out` 里。

## 4. 变异表

两张表都有控制行（先用未变异的树确认那条用例是绿的）与守卫（空过滤器也会报成功，读成「打掉了」）。

### 4.1 常规表 13/13（`/tmp/chg059/mutate_t04_desktop.py`）

转录：`task-04-desktop-mutations.out`

| # | 变异 | 必须被打掉的用例 | 读数 |
|---|---|---|---|
| M1 | 不校验就启动（**修复前的形状**） | `a_tampered_sidecar_is_refused_and_an_intact_one_is_started` | 打掉 ✓ |
| M2 | 拒绝也能回退到 Python | `a_refusal_is_never_answered_with_the_python_path` | 打掉 ✓ |
| M3 | 摘要只算文件开头 128 字节 | `a_sidecar_that_matches_its_record_passes_and_one_changed_byte_does_not` | 打掉 ✓ |
| M4 | 字段缺失时兜底成空串 | `a_record_that_cannot_be_compared_is_refused` | 打掉 ✓ |
| M5 | 不检查记录写的是不是这个文件 | 同上 | 打掉 ✓ |
| M6 | 一律当成「在包里」 | `a_cargo_test_run_is_not_a_package` | 打掉 ✓ |
| M7 | 一律当成「不在包里」 | `only_a_launch_from_inside_a_bundle_counts_as_one` | 打掉 ✓ |
| M8 | 解析时不做 deps 跳 | `the_sidecar_is_resolved_beside_the_app_and_out_of_deps` | 打掉 ✓ |
| M9 | 没有 sidecar 时也去读记录 | `no_sidecar_is_not_a_failure` | 打掉 ✓ |
| M10 | 启动时不给环境变量 | `a_tampered_sidecar_is_refused_and_an_intact_one_is_started` | 打掉 ✓ |
| M11 | 启动的是名字而不是被校验过的那个路径 | 同上 | 打掉 ✓ |
| M12 | 校验通过不写记录 | 同上 | 打掉 ✓ |
| M13 | 比的是「记录非空」而不是摘要相等 | `a_sidecar_that_matches_its_record_passes_and_one_changed_byte_does_not` | 打掉 ✓ |

两条在过程中被**改正**，都记在这里而不是悄悄换掉：

- **M3 最初存活**：把 `digest` 截到前 128 字节，对当时那个 34 字节的测试文件是**等价**的。
  对策是把测试文件改成 4097 字节（并在用例里写明为什么），M3 随即打掉。
- **M6 最初存活且瞄错了用例**：`inside_a_bundle` 恒真时，被它指的那条用例根本不调用它。
  对策是补 `#[cfg(test)] fn bundled()` 与 `a_cargo_test_run_is_not_a_package`（把「标志决定
  是否拒绝」与「标志来自可执行文件路径」两半钉在一起），M6 改指该用例后打掉。
- **M4 一开始写成了编译错误**（对 `String` 用 `?`），运行器的「读数无效」守卫拒绝计数，
  换成一个合法变异（`unwrap_or_default()` 并去掉五个 `?`）后才算数。

### 4.2 包内臂 5/5（`/tmp/chg059/mutate_t04_bundle.py`）

转录：`task-04-bundle-mutations.out`

| # | 变异 | 读数 |
|---|---|---|
| MB1 | 一律当成「不在包里」 | 打掉 ✓ |
| MB2 | sidecar 解析到包里的另一个名字 | 打掉 ✓ |
| MB3 | 记录读到资源目录以外的位置 | 打掉 ✓ |
| MB4 | 比的是「记录非空」而不是摘要相等 | 打掉 ✓ |
| MB5 | 包内缺记录也被容忍 | 打掉 ✓ |

这张表存在的理由：常规表只能从 `target/` 里跑用例，而包内臂**在 `target/` 里根本跑不起来**
（§3 的对照读数就是红的）。所以它的断言另用一张表验证，跑法与 §3 相同（重建二进制 →
放进构造的包 → 从 `Contents/MacOS` 跑），脚本每轮先把夹具从 `packaged/` 拷回来——
一次中途 panic 会把夹具留在改坏的状态，那会让下一轮的控制行因为错误的原因变红。

## 5. 打包侧：记录为什么写在那两步之间

转录：`task-04-packaging.out`（三条摘要读数 + 外层签名验证）

1. **构建期的摘要与随包的文件不是同一份字节。** 构建产物
   `src-tauri/binaries/wt-media-agent-aarch64-apple-darwin` 是 `e37653fa…`，而随包的那个
   （Tauri 装进 `Contents/MacOS` 后，`scripts/build-release-macos.sh:22` 调签名脚本做
   ad-hoc 重签）是 `f92cbdee…`。⇒ 拿构建期摘要当校验目标，每次发布都会拒。
2. **重复签名是逐字节可复现的**：对同一份输入再签一次仍是 `f92cbdee…`，所以「签名后量一次」
   是可重放的，不是掷骰子。
3. **记录写在两端之间**：先在 `Contents/Resources` 写记录，再签外层；实测
   `codesign --verify --deep --strict` 仍然通过（`exit=0`），说明这一文件被外层的封装盖住
   而不是破了它。反过来写在签名之后就会让外层签名失效。
4. 包内记录因此与运行期见到的是同一个文件：包内臂 arm 1 在包内重新量了一次 sidecar，
   与记录一致。

## 6. 前提读数：外层签名到底覆盖了什么

转录：`task-04-seal-probe.out`（三份**互相独立**的副本，各只做一件事）

| 探针 | 结果 |
|---|---|
| 基线（不改） | `valid on disk`，exit 0 |
| 只给 `Contents/MacOS/wt-media-agent` 追加一字节 | `main executable failed strict validation`，exit 1 |
| 只改 `Contents/Resources/sidecar-manifest.json` 的 version | `a sealed resource is missing or invalid`，exit 1 |

**第一版把三件事串在同一份副本上读，第二条读到的其实是第一条留下的损坏**（它报的仍是
`In subcomponent: …/wt-media-agent`），已按独立副本重测。这条订正留在转录里。

它说明的是**本校验的定位**：换掉文件不是没人拦，但拦它的签名验证不指名是哪个文件对不上
哪份记录，也不区分「被改坏」与「记录与文件来自不同构建」；而「两边各自都是合法签名、
只是互不相符」（例如记录来自另一个构建）这一类签名验证**不报**——文件本身签名有效。
那正是运行期校验与打包侧相等性判定各自要抓的那一类。

## 7. 设计裁定

1. **校验的文件必须是启动的文件**：`start` 自己解析路径（与
   `tauri-plugin-shell-2.3.5/src/process/mod.rs:120-152` 的 `relative_command_path` 同一算法，
   含 `deps` 跳）后 `command(resolved)`，而不是按名字交给插件解析第二遍——否则「校验的」
   与「启动的」可以不是同一个文件（M11 就是这条的读法）。
2. **`Refused` 是终点**：包不对时回退到 Python 调试路径，是唯一能把「包不对」藏起来的应答
   （应用照常起来，之后每次调用都由一个没人校验过的 Agent 回答）。
3. **工程树容忍、包里拒绝**：`tauri-build-2.6.3/src/lib.rs:56,546` 会把 `externalBin` 拷进
   cargo 目标目录，工程树里因此可能有没记录的 sidecar。不这样区分，`cargo test` 出来的树
   就起不了 Agent。实测本机 `cargo build` 当时并没有重新拷贝（构建脚本未重跑），所以这条
   是**潜在**而非现发的风险——判定表按潜在风险写。
4. **不引入环境变量逃生门**：一个 `WT_MEDIA_*SKIP*` 会把这项控制直接作废。
5. **威胁模型如实登记**：ad-hoc 签名（`signingIdentity: "-"`）没有信任锚，所以这是
   **包一致性检查，不是对抗能改包者的安全边界**。这条写进了模块头。

## 8. 读数

| 项 | T-03 结束时 | 现在 | 差 |
|---|---|---|---|
| desktop `cargo test` | 353 passed / 0 failed / 4 ignored | **363 passed / 0 failed / 5 ignored** | +10 passed，+1 ignored |
| desktop 编译警告 | 7 | **7** | +0 |

新增 10 条：`integrity.rs` 7 条（含 6 个「记录不可比对」的分支与一个真 `shasum` 对照）、
`a_refusal_is_never_answered_with_the_python_path`、`a_cargo_test_run_is_not_a_package`、
以及 `a_tampered_sidecar_is_refused_and_an_intact_one_is_started`；另加 1 条 `#[ignore]`
的包内臂（默认不跑）。警告 7 条逐条都在未触碰的文件里（四个空壳 + `rolling.rs` ×5 +
`storage.rs` ×2 + `settings.rs`）。

## 9. 未覆盖项与已知极限（登记，不静默吸收）

1. **没有「真机双击启动一个被篡改的包」的读数。** 需要 GUI 启动（会在用户屏幕上开窗），
   且 macOS 在 `exec` 时的行为与 `codesign --verify` 是两条不同的路径。本任务证的是
   **校验逻辑本身**在真包布局下成立（§3），证不了「真包被篡改后 App 会怎样」。
2. **Windows / x86_64 未测**（Q-03）：`resolve_sidecar` 里 `.exe` 的处理是从插件源码抄的，
   本机没有可跑的目标。
3. **`Location::of` 的两次 `current_exe()` / `resource_dir()` 失败**只走 `Attempt::Unavailable`
   （视同「没有包可拒」），没有用例——那条分支需要让系统调用失败，本机造不出来。
4. **`note` 的三条记录没有用例**：它们写进 `tracing`，而套件里没有装 subscriber 的读法；
   §3 打印的 `arm 1 …校验通过` 是用例自己的 `println!`，不是记录本身的读数。
   （T-03 的 `real_agent` 臂有真日志读数，本任务没有等价的真机臂。）
5. **`sha2` 的流式读取对 10 MB 的 sidecar 是每次启动一次全文件读**：没有做「先看大小/时间戳
   再决定是否细算」的优化，也没有量过启动延迟代价。本轮不改。
6. **`package-release-macos.sh` 的相等性判定没有真跑过出包**（那会重建 release 产物、
   需要 `output/` 的写权限）。判定本身在 §5 用同样的两条测量复现过（`node -p` 读记录 +
   `shasum` 独立测量），但「整段脚本在真实出包时走通」这一条**未做**。
