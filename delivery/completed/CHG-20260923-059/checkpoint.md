# CHG-20260923-059 Checkpoint

## Completed

- 2026-09-25：草案由 `delivery/planned/` 移入 `delivery/active/` 并改写为十三节执行记录
  （`change.md`、`checkpoint.md`、`status/`、`evidence/`）。
- `change.md` §4 的每条现状都是激活时**实测**得到的 file:line 与命中数。**两条草案预想被实测推翻并已更正**：
  ①草案说「Cargo 里没有哈希依赖」——实测 `sha2 = "0.10"` **已是直接依赖**（`src-tauri/Cargo.toml`），
  故 T-04 是「复用既有依赖」而非「新增依赖」；②草案未提 `config_online/agent.toml:17-21` 那段
  **过期的 Q-01 注释**，实测存在且与新裁定冲突 ⇒ 并入 T-10 回写。
- 其余 §4 事实逐条在案：就绪行打得出来（`server.py:627` 在 bind+listen 之后、`serve_forever()` 之前）
  但**消费者为零**、`start_timeout_ms` 是死配置；`already_running` 读的是**受管槽位里那个
  `CommandChild` 句柄**（`commands/agent.rs:163-168`）——**此处激活时写成了 `session.current()`，
  是错的**，T-02 收尾时按 `f1d1fba^` 原文回改，缺陷结论不变（§4.2 的注记）；CHG-057 登记的实缺陷仍在；退出侧 `RunEvent`/`on_window_event`/`ExitRequested`
  **零命中**、`sidecar::stop` = `child.kill()`、Agent 只捕 `KeyboardInterrupt`；
  `tauri.conf.json:26` 的 `bundle.resources` 只含 Desktop 自己的 toml 且 `build_desktop_sidecar.py`
  对 `config_online` 零命中；两个版本号各读一处（`:53`/`:82`）**从不比对**。
- 用户 2026-09-25 的两条裁定落在 §6：**D-08**（Q-01 关闭＝生产 Cloud 保持本机 `http://127.0.0.1:18080`，
  两份出货配置的值与 CSP 均不改，只回写过期注释）、**D-09**（「干净机」安装验收**登记为未做**，
  `0.2.5` 的 status 保持 `verifying`，D 的 DONE Gate 因此**带一条登记过的例外**）。
- 本机环境：起改前已确认 18080 / 8765 空闲；54345 是用户自己的 BitBrowser，**全程不占用**。
- **激活当天被本仓门禁抓过一次**：`LEDGER.md` 的活动行第一格我写成了 markdown 链接，而
  `verify_delivery_governance.py:37` 的 `LEDGER_ROW_RE = ^\|\s*(CHG-\d{8}-\d{3})\s*\|` 要求第一格是**裸 id**，
  报 `CHG-20260923-059 != none`。改成裸 id、把链接移进标题格后两个验证器转绿。**这条留着当阳性样本**：
  门禁确实会红，不是摆设。

## Current

- **T-01…T-10 全部收尾；本 CHG 已于 2026-09-25 归档 `DONE`，联合工程优化程序四阶段全部关闭。**
- 记录链：激活记录见 `0449604`；T-01 的代码、证据与回写见 `evidence/task-01-readiness.md`
  与对应的两个仓提交；T-02 见 `evidence/task-02-identity.md` 与 desktop 的 `15951a4`、`c54025a`；
  T-03 见 `evidence/task-03-exit.md` 与 agent 的 `70a1647`、desktop 的 `242f61e`；
  T-04 见 `evidence/task-04-integrity.md` 与 desktop 的 `04f46c3`；
  T-05 见 `evidence/task-05-shipped-config.md` 与 agent / desktop 各一个提交；
  T-06 见 `evidence/task-06-versions.md` 与 desktop / workspace 各一个提交；
  T-07 见 `evidence/task-07-upgrade.md` 与 desktop 的 `293806f`、agent 的 `feb532d`；
  T-08 见 `evidence/task-08-m2-regression.md`——**本任务未改任何仓的运行时代码**，故无代码提交，
  只有本仓的记录与证据（D-25、Q-05、AC-08 的例外）；
  T-09 见 `evidence/task-09-absorbed.md` 与 workspace 的 `dac853f`（skill 改指 + resolve 判据）、
  agent 的 `2b26808`（入口文档 + 契约文档判据 + 两份重生成的 skill 副本）——
  **本任务同样未改运行时代码**，两个仓各新增一个测试文件；
  T-10 见 `evidence/task-10-writeback-and-close.md` 与 workspace 的 `54c87b2`（归档移动，**纯移动**）
  与写回提交、agent 的注释与判据提交——**本任务未改任何运行时代码**（agent 侧只改注释 + 新增判据）。

## Next

- 无。本 CHG 已关闭；程序层面剩两个未裁定项（Q-05 的 DMG 腿与 8765 归属、Q-07 那条间歇红的处置方向），
  都已登记、都不阻塞任何已完成的事实。

## T-01（已收尾，2026-09-25）

- desktop `sidecar/readiness.rs`（新，两段式闸门）+ `sidecar/mod.rs` 注册 + `commands/agent.rs` 接线；
  agent `tests/test_sidecar_entry.py` 钉死就绪行的格式与顺序。
- **实测推翻预想一条并改了设计**：`/healthz` 在 `_check_auth` 之后（`server.py:448`→`:451`），
  故令牌漂移时它答 **401**。于是第二段闸门把应答分三态（2xx 就绪 / **401 致命立即失败** / 连不上继续等），
  顺带覆盖 `sidecar/mod.rs:30-37` 那段注释担心、而**构建期无人检查**的漂移。见 §4.1 补记。
- 计数：desktop 336→**344** passed / 0 failed（ignored 2→3）；agent 377→**378** OK；
  编译警告 7→**7**（新增 0——基线是**把三个文件还原成 HEAD 版单独跑一次测出来的**，不是推的）。
- 变异 **8/8**：desktop 6 条（前缀、端口判定、状态码、单次读缓冲、常量超时、到点返 Ok）+
  agent 2 条（就绪行改词、**把打印挪到建服务器之前**）。A2 是这条用例的真价值：测的是顺序不是格式。
- 真机臂：`cargo test -- --ignored real_agent` 通过——**本 crate 的 `gate` 对上真实的 Agent 进程**。
  它太快（0.17s），故做了**阳性对照**（故意写错期望，读到真机那行
  `…127.0.0.1:54606`）才算数。
- **两次「验证工具本身出错」已记录**（都会把红读成绿）：脚本先写变异后读基线；以及
  `python3` 字节码缓存——`on`→`at` 长度不变、`.pyc` 的源 mtime 只到秒，同秒写入的变异被上一轮缓存服务。
- **workspace 4 条既知红项的控照这一次真的跑了**（§4.8 要求的方法）：用
  `git stash push -- <那两个记录文件>` 把记录改回 HEAD（**只动这两个，其余 5 个无关脏文件未碰**），
  在**真实 `wt-media/` 之内**的同一棵树上重跑 ⇒ **同样 4 条、逐条同名**。
  同时**复现了 §4.8 预警的陷阱**：先把 `git archive HEAD` 解到 `/tmp` 再跑，路径敏感的用例
  `skipTest`，读数变成 **2 红**——正是「4 红读成 2 红」的原样。故本条的控照**不能**在图外做。

## T-02（已收尾，2026-09-25）

- desktop `commands/agent.rs`：`Occupancy{Vacant,Running,Stale}` + `occupancy()`（空槽**一次请求都不发**）
  + `discard()`（记录 → 取走句柄 → 试一次 kill → 清会话），`start` 的守卫由读句柄换成 `match occupancy(...)`。
- **缺陷复现**：把守卫整块还原成修复前形状重跑同一条用例 ⇒ `Ok("already_running")` 对着一具尸体
  （转录 `evidence/task-02-red.out`）。用例里没有替身：真 `CommandChild`（`sh -c "exit 0"`，
  等到 `Terminated` 才算数）+ 真没人听的端口。
- `tauri` 的 `test` feature 作 **dev-dependency**（`15951a4`）：`MockRuntime` 之上的
  `tauri-plugin-shell` 是同一个 crate、同一条 spawn 路径，所以槽位里能放**真的** `CommandChild`。
  出货构建看不到它——`cargo tree -e features,no-dev -i tauri` 命中 `feature "test"` **0**，
  同一查询不加 `no-dev` 命中 **1**（**两行都要报**，否则分不清「真的不在」与「查询抓不到」）。
- 计数：desktop 344→**348** passed / 0 failed（ignored 仍 3）；警告 7→**7**；套件 2.36s→**1.93s**。
- 变异 **8/8**。**第一轮只有 6/8，两个存活变异各查出一处真洞**：①一条断言在说自己证明不了的事
  （「事后槽位是空的」同时被失败分支的 `stop` 满足，区分不了「丢弃」与「留着后来被清理」）
  ⇒ 改成断言**那条记录**，并把该断言删掉、写明由 `discard` 那条用例独占；
  ②一条变异**被错派**给看不见它的用例 ⇒ 改派。两处都不是调断言了事。详见证据 §4.1。
- **AC-02 只算一半**：先红后绿已成，**真机读数未做**（判据是「槽里那个句柄的性质」，套件内已用真句柄
  覆盖；不像 T-01 必须起真 Agent 进程）。按 D-09 的方式如实登记，不以文字充当证据。
- **`desktop.log` 与本次提交的格式状态**：`commands/agent.rs` 在提交前带着**未提交的 rustfmt 重排**。
  按 T-01 的同一做法，先把 rustfmt 输出反推掉、只提交语义改动（`diff` 的**忽略空白后**仍差 356/11，
  与逐片段枚举一致——即没有一处纯重排混进提交），提交后再把重排原样放回。收尾时 13 个脏文件
  逐个核对为 `工作区 == rustfmt(HEAD)`，一并对 `sidecar/mod.rs` 补回了它此前丢掉的 churn。

## T-03（已收尾，2026-09-25）

- agent `local_api/server.py`（`70a1647`）：`serve()` 安置 SIGTERM 处理器并把 `shutdown()`
  **派到自己的线程**（信号只投主线程，就地调用会死锁）；`httpd.daemon_threads = False`
  ——实测出来的承重行，`ThreadingHTTPServer` 默认 `True` 时 `_Threads` **不登记守护线程**，
  `server_close()` 的 join 是空转；「stopped」挪到 `server_close()` 之后；结束时还原被顶掉的处理器。
- desktop（`242f61e`）：`sidecar::{ask,alive,force}`（`test_kill_process` + `Errno::PERM` 算「在」，
  `Pid::from_raw(0)` 为 `None` 故 0 必拒）+ `commands::agent::stop()` 的请停→50ms 轮询→到点强杀
  + `main.rs` 的 `RunEvent::Exit` 钩子 + 新键 `[sidecar] stop_timeout_ms`（出货 5000，`validate()` 拒 0）。
- **先红**：保留全部新用例，把 `stop` 的函数体还原成 HEAD 的 `kill(process, session)` ⇒ 两条用例都红
  （转录 `evidence/task-03-desktop-red.out`）：两条 arm 的日志**都只有**「Local Agent 已停止」（事后
  读不出差别）；「答」的那条报 `(None, Some(9))`（SIGKILL，trap 从未跑到）；「不答」的那条报
  `the kill came at 900.875µs`（窗口根本不存在）。
- **真机两条读数**（`--ignored real_agent`，Desktop 自己的停路对上真 Agent 进程；不是替身）：
  「答」= `已请（pid）→ 在宽限内自行退出（518 ms）→ 已停止`、退出码 `Some(0)`；
  「杀」= `已请 → 宽限已到，强杀（1 ms）→ 已停止`、`signal: Some(9)`。杀的那条窗口**故意**短于
  Agent 自己半秒的轮询，故读数由「截止时间到」决定而非两个时钟赛跑。连跑 **5 次 5/5**。
- 计数：desktop 348→**353** passed / 0 failed（ignored 3→**4**，多的那条就是真机臂）；
  agent 378→**382** OK；警告 7→**7**；变异 agent **5/5** + desktop **9/9**。
- **两处订正落库**：`rustix` 的 `process` **不在**默认 feature 里（上一轮记录写反了）；
  `sidecar.stop_timeout_ms` 补进 `validate()`。
- **churn 口径与 T-01/T-02 同**：三个混合文件（`commands/agent.rs`、`sidecar/mod.rs`、`dto/config.rs`）
  用**三路合并**（HEAD / `rustfmt(HEAD)` / 工作区）反推掉重排后再提交，两条判据都报——
  `rustfmt(候选) == rustfmt(工作区)`，且候选内容跑出同样的 `353 passed; 0 failed`。
  提交后 13 个脏文件逐个复核为 `工作区 == rustfmt(HEAD)`（**13/13**）。
  **过程中踩到一个坑并已还原**：`rustfmt` 会**顺着 `mod` 声明递归**格式化子模块，我的探针文件
  因此把当时**干净**的 `sidecar/readiness.rs` 也重排了；已 `git checkout` 还原，工作区回到
  恰好那 13 个文件（这版 rustfmt 不认 `--skip-children`）。
- **一条按 D-09 方式登记的例外**（不静默吸收，见 `evidence/task-03-exit.md` §7）：随包 onefile
  sidecar 在本机**起不来**（引导器解出的 `libpython3.14.dylib` 被 macOS 以「Team IDs 不同」拒
  `dlopen`），故「**引导器是否把 SIGTERM 转发给真正在服务的那进程**」**未测**；另两处：
  `RunEvent::Exit` 钩子本身只有阅读级覆盖；宽限内 pid 被复用是 `alive`/`force` 的已知窄极限。

## T-04（已收尾，2026-09-25）

- desktop（`04f46c3`，一个 commit 含打包侧一半）：新增 `src-tauri/src/sidecar/integrity.rs`——启动前
  读 `Contents/Resources/sidecar-manifest.json`，按 SHA-256 比对**要启动的那个文件**；
  `sidecar/mod.rs` 的 `start` 改为「求位置 → 校验 → 用**解析出的路径**启动」，`Attempt::Refused`
  不许被 Python 调试路径答掉（`may_fall_back` 只放行 `Unavailable`）；没有记录时
  **工程树容忍 / 包里拒绝**（`tauri-build` 会把 `externalBin` 拷进 `target/<profile>/`，
  不这样区分 `cargo test` 出来的树就起不了 Agent）。不新增依赖（`sha2`/`hex`/`serde_json` 已在）。
- **打包侧一半**：`repair-macos-signing.sh` 在 sidecar 的 ad-hoc 签名**之后**、外层签名**之前**
  写这份记录——签名会改写文件（构建期 `e37653fa…` ≠ 随包 `f92cbdee…`，实测），而
  `Contents/Resources` 被外层封装盖住（加在签名**之前**实测 `--verify --deep --strict` 仍 exit=0）；
  `package-release-macos.sh` 加相等性判定（包内记录的摘要 vs 对随包 sidecar 的独立测量）。
- **先红**：把 `spawn_verified` 里那次校验去掉（回到修复前形状）⇒ 那条用例红在
  `a changed byte has to be refused, not started`，且**被篡改的 sidecar 真的被启动了**（脚本的标记
  文件出现）。转录 `evidence/task-04-desktop-red.out`。
- **包内臂（AC-04 的阳性对照所在）**：新增 `#[ignore]` 用例，只在 `<x>.app/Contents/MacOS` 里跑得动。
  用签名脚本**真写出的** sidecar 与记录造 `.app` 布局后从那里运行，四条读数：真记录→通过
  （version 0.2.2 / target aarch64-apple-darwin，sha256 与对同一文件的独立 `shasum` 一致）、
  追加一字节→「SHA-256 与包内记录不一致」必拒、删记录→「包内缺少记录文件」必拒、复原→仍通过。
  **对照**：同一个用例从 `target/debug/deps` 跑**必红**（并打印出工程树那两条路径）。
  两条都在 `evidence/task-04-bundle.out`。*（`output/` 全程只读；副本与构造的包都在 `/tmp`。）*
- 计数：desktop 353→**363** passed / 0 failed（ignored 4→**5**，多的那条就是包内臂）；警告 7→**7**。
- 变异：常规表 **13/13**（`evidence/task-04-desktop-mutations.out`）+ 包内臂 **5/5**
  （`evidence/task-04-bundle-mutations.out`）。常规表只能从 `target/` 里跑用例，而包内臂在那里
  根本跑不起来，所以它的断言另用一张表验证。
- **三处过程订正留在证据里**（不是调断言了事）：① M3 最初**存活**——把 `digest` 截到前 128 字节对
  当时 34 字节的测试文件是**等价**的，测试文件改成 4097 字节后打掉；② M6 最初存活且**瞄错了用例**
  （`inside_a_bundle` 恒真时，它指的那条用例根本不调用它）——补 `#[cfg(test)] bundled()` 与
  `a_cargo_test_run_is_not_a_package` 把两半钉在一起；③ 封印探针**第一版把三件事串在同一份副本上读**，
  第二条读到的其实是第一条留下的损坏（报的仍是 `In subcomponent: …/wt-media-agent`），已按
  **三份独立副本**重测（`evidence/task-04-seal-probe.out`）。
- **威胁模型如实写进模块头**：ad-hoc 签名没有信任锚 ⇒ 这是**包一致性检查，不是对抗能改包者的安全边界**；
  且外层签名/嵌套校验虽能发现篡改，却不指名哪个文件对不上哪份记录，也不区分「被改坏」与
  「记录来自另一个构建」——「两边各自都是合法签名、只是互不相符」这一类签名验证**不报**，
  那正是本校验与打包侧相等性判定各自要抓的。
- **churn 口径与 T-01/T-02/T-03 同**：两个混合文件（`commands/agent.rs`、`sidecar/mod.rs`）用三路合并
  （HEAD / `rustfmt(HEAD)` / 工作区）反推掉重排后再提交，判据两条都报——`rustfmt(候选) == rustfmt(工作区)`，
  且候选跑出同样的 `363 passed / 0 failed / 5 ignored`；提交后 13 个脏文件逐个复核为
  `工作区 == rustfmt(HEAD)`（**13/13**）。**这次没有踩 T-03 那个坑**：临时文件用
  `--config skip_children=true` 格式化（有效形式，与 T-03 记的 `--skip-children` 不同——那个不被认）；
  且第一遍因忘了这个参数而**假绿**过一次（`rustfmt` 对 `mod.rs` 报 `failed to resolve mod drain`
  并**不写文件**，于是「候选 == 工作区」的平坦比较其实什么都没比）——发现后重做，并改用
  「候选 vs 工作区」「候选 vs HEAD」「工作区 vs HEAD」三个行数一起报。
- 未覆盖项（写进 `evidence/task-04-integrity.md` §9）：没有「双击启动一个被篡改的包」的读数（需要 GUI）；
  Windows/x86_64 未测（Q-03）；`Location::of` 两次系统调用失败那条分支无用例；`note` 的三条记录没有
  用例（套件里没有装 subscriber 的读法）；`sha2` 每启动一次全文件读、未量代价；
  `package-release-macos.sh` 的相等性判定没有真跑过一次完整出包。

## T-05（已收尾，2026-09-25）

- agent `runtime/config.py`：`default_config_dir(*, frozen, exe)` 由**可执行文件的位置**推导
  （`.app` 布局优先、其次 exe 旁边、都命中不了回落并 WARNING），`frozen`/`exe` 穿透
  `_read_document`/`load_config`；`scripts/build_desktop_sidecar.py`：`--config-dir` = 先删后拷的
  整目录替换 + 读回比对 + 报出文件清单。desktop：**新增** `scripts/stage-release-config.sh`，
  `build-release-macos.sh` 一行接线（`cargo tauri build` 之后、`repair-macos-signing.sh` 之前），
  `verify-release-macos.sh` 加 DMG 内配置的 `diff -r` 判定与两条防「空集通过」的判据。
- **设计被实测改过一次**：原计划走 `tauri.conf.json` 的 `bundle.resources: ["config/*"]`。
  Tauri 会拒绝匹配不到任何文件的 glob（`glob pattern config/* path not found or didn't match any
  files.`）⇒ **任何还没跑过发布步骤的检出**（干净 clone、`cargo test`、`cargo tauri dev`）都编译不过。
  三条改动（`.gitignore`、`tauri.conf.json`、`prepare-release-sidecar.sh`）**已回退到 HEAD**，
  改为在**产物**上暂存（§6 D-12 记了这条否掉的路与原因，因为「Tauri 也能送」下次还会被提出来）。
- **真机读数**（`evidence/task-05-frozen-reading.out`）：夹具把 `Contents/Resources/config/agent.toml`
  放在它该在的位置、只改 `local_api.host = "localhost"`（内置默认是字面量 `127.0.0.1`，没有环境变量
  在这里设它），端口走环境变量的临时端口。**修复前那份随包产物报 `127.0.0.1`**（文件没被读），
  **含本次改动的新构建报 `localhost`**。两侧只有二进制不同。
  同一条转录里另有两条辅助读数：`raw-build`（刚构建、未重签的产物体起不来 ⇒ `repair-macos-signing.sh`
  是承重的一步，同时解释了 T-03 记的「随包 sidecar 在本机起不来」）与 `alias`（第一版夹具用
  `127.0.0.2`，macOS 绑不上，`[Errno 49]`；换 `localhost` 重跑，失败那条留档不删）。
- **发布闸门五臂**（`evidence/task-05-gate.out`，真闸门脚本 + 真产物 app，DMG 手工造）：
  `green` exit 0；`changed` 两侧签名各自合法而内容不符 ⇒ 只有内容比对抓得住；`absent` 指向
  `stage-release-config.sh`；`empty-source` 拒绝「空集通过」；`resealed` 让
  `codesign --verify --deep --strict` 报 `a sealed resource is missing or invalid` 并指名那个文件
  ⇒ **封条盖住配置**，位置与顺序由此定下（D-12/D-15）。
- 计数：agent 382→**397** OK（+15）；desktop **363 passed / 0 failed / 5 ignored**（未改任何 Rust 文件，
  读数与 T-04 相同）、警告 7→**7**。变异 agent **17/17**（M10 是为它补的：删掉读回校验起初没有用例会红，
  补法是让**拷贝本身说谎**——`mock.patch.object` 把 `copytree` 换成「拷完再删掉 `agent.toml`」的版本）。
- 凭据（AC-05 的另一半）：`config_online/agent.toml` **12** 个叶子、命中 **0**；**阳性对照在同一次运行里**
  抓得住两种形态（嵌套且大小写混合的键名 + 值里的 userinfo），扫描到的叶子数 3 而不是 0。
- 顺手订正一处**成因写错的注释**（D-16，只改注释）：`repair-macos-signing.sh` 原把
  `different Team IDs` 归给 Tauri。实测是 PyInstaller 6.22.2 `utils/osx.py:413-421`——identity 为假时
  才跳过硬运行时，而我们传的字面量 `-` 是真值；未重签的**构建产物**已经带 `flags=0x10002(adhoc,runtime)`。
- 未覆盖项（`evidence/task-05-shipped-config.md` §9）：没有真跑过一次完整出包（DMG 手工造）；
  `--config-dir` 指向不存在的目录时脚本层拦、库函数层会自建，这个错配没有用例；
  只读文件系统/权限失败无用例；Windows/Linux 布局未测（Q-03）；开发树里的冻结 sidecar 未做真机读数；
  打包场景下 env > file 的三层优先级只被单测逐键覆盖。

## T-06（已收尾，2026-09-25）

- desktop 新增 `scripts/release-versions.sh`（五类的唯一读法：`--check` / `--record` / `--verify` /
  `--stamp-frontend`）与 `src-tauri/agent-compat.json`（Desktop → Agent 的 **pin**）；新增
  `tests/release-versions.test.sh`（20 条臂，自造假树）；发布脚本五处接线（`build-release-macos.sh`
  构建后 `--check`、`repair-macos-signing.sh` 签名窗口内 `--record`、`verify-release-macos.sh` 挂载后
  `--verify`、`package-release-macos.sh` 记录进发布目录与 `SHA256SUMS`、`scripts/test.sh` 跑
  `tests/*.test.sh`——此前无人调用）。workspace 侧：`scripts/build-desktop.sh` 复制产物后
  `--stamp-frontend`（前端构建版本的**唯一**来源，Desktop 仓看不到来源仓）。
- **Q-04 关闭（D-17）**：「组件与资源版本」是**内容摘要**而非被人递增的号——它是产物
  `Contents/Resources` 逐文件 sha256 的合并摘要（排除记录自身），只在随包集合真变了时才变，
  不可能过期，也没有「谁来 bump」。逐文件清单是它的**产物**（用来把摘要差异翻译成文件名），不是输入。
- **发布流程真跑了一遍**（`build-release-macos.sh` exit=0，产出 DMG 17,129,049 字节）：
  前端由 workspace 脚本重建并 stamp（`74d4b003…`，与我手工 stamp 同一次构建**同值**）→ 构建后
  `--check` 通过 → 签名窗口内 `--record` → 挂载 DMG 后 `--verify` **复算出同一摘要**
  `sha256:69f34a89…`（`evidence/task-06-release.out:279,299`）。这一条同时证明暂存配置、写记录、
  外层签名与 DMG 装配**都不改变** `Contents/Resources`。顺带**关闭了 T-05 登记的那处例外**
  （「没有真跑过一次完整出包」），AC-05 行已加注。
- **两条真机红，各带阳性对照**：① 改一个随包资源 → `--verify` 拒绝并点名
  `resources/desktop.production.toml`（改前同一命令 exit=0）；② pin 改 `0.2.3` → `--check` 拒绝并点名
  pin 路径与两侧版本，pin 还原后同一条命令转绿、pin 文件 sha256 前后一致（`2f6076fa…`）。
- 计数：desktop **363 passed / 0 failed / 5 ignored**（未改 Rust 文件，与 T-04／T-05 相同）+ 两个 shell
  套件各绿；agent **397 OK**（未改）；shell 臂 **20 passed / 0 failed**；变异 **15/15**。
- **两条臂的判据被变异改掉**（如实登记）：首轮 M1 打不掉 A3、M15 打不掉 A20——两条 needle 会被
  **另一条**拒绝路径的报文满足，即臂会在错误的原因上变绿。收窄到只有目标守卫会产出的措辞
  （A3 → `agent-compat.json`、A15 → `carries no`、A20 → `nothing states`）后各自恰好成立。
  M10/M12 首轮 `bash -n` 不过（`if…fi` 换成裸 `if false; then`），补成 `if false; then :; fi`。
- 设计裁定：D-17（Q-04 口径）、D-18（摘要边界是 `Contents/Resources`，不含 `MacOS`／不含整包——整包
  摘要因外层签名写 `_CodeSignature/` 而**永远不可复算**）、D-19（pin 是**评审闸门不是证明**，
  「改 pin 即评审」写进 pin 文件）、D-20（前端 version 的归因局限：记的是 stamp 时刻的源提交）、
  D-21（记录写在签名窗口内）、D-22（**不加** `version_classes:` 到 `release-matrix.yaml`：第二份没人
  校验的声明即漂移）、D-23（订正 `DMG_PATH` 里写死的 `0.1.0`；今日不可分辨，是读证不是跑证）。
- **「13 个 rustfmt 变更文件仍是纯重排」这条核对本次换过判据，两种错法都登记**（原判据只说不出来）：
  ① `rustfmt --emit stdout` 会在输出**前面加一行 `<路径>:` 加一个空行**——按「原样比对」用它会得出
  **13/13 全是真改动**的假警报；② 把 HEAD 版本写到 `src-tauri/src/sidecar/mod.rs` **旁边**去格式化的做法，
  rustfmt 会**顺着 `mod` 声明把自己的兄弟模块也格式化**，于是误改了工作区里的 `sidecar/readiness.rs`
  （已用 `git show HEAD:… >` 还原，diff 归零）。最终判据：`git archive HEAD src-tauri/src` 镜像到
  `/tmp` 后逐文件 `--emit files`，再与工作区比对 ⇒ **13/13 纯重排**，且工作区仍**恰好 13** 个脏文件。
  教训是「验证手段自己会写进被验证的仓库」这一类错法要留档。
- 未覆盖项（`evidence/task-06-versions.md` §9）：`DMG_PATH` 的订正今日不可分辨；前端 marker 的归因局限；
  第五类摘要不含 `Contents/MacOS`（那里的二进制由 T-04 的运行期校验负责，两条机制不重叠）；
  x86_64／Windows 未测；`--stamp-frontend` 对「`package.json` 无 version」的拒绝路径没有独立臂；
  真机五类只有 arm64 macOS 一份。

## T-07（已收尾，2026-09-25）

- **交付物是判据，不是行为**（D-24）。本 CHG 不实现升级器（`updater/`、`filesystem/` 仍是空壳），
  否定命题「升级不写用户数据」没有动作可改 ⇒ desktop 新增 `src-tauri/src/upgrade.rs`
  （**故意是 `#[cfg(test)]` 模块**：一个没有调用方的守卫等于一个 `dead_code` 警告加一句没人执行的
  声明），`main.rs` 只多 `#[cfg(test)] mod upgrade;` 一行；agent 侧新增
  `tests/test_upgrade_preserves_data.py`，**不改任何实现文件**。
- 判据只有一条规则：`inside` = `Path::starts_with`，即**按路径分量**比较。声明两个写入点
  （`settings::path`、`Root::Versions`），数据根下其余一切**都是用户数据**；Agent 的数据根
  由 `WTMedia/<Component>` 的同一形状解析——归另一侧所有的位置，无论文件叫什么。
- **两侧的「升级面」不是同一件事**：Desktop 是它自己的数据根；Agent 是 `storage/migration.py`
  的**迁移**（新版本跑在旧版本写的库上）。这就是这个仓今天真的会做的升级。
- **先红是判据本身**：desktop 首轮把 `refuse` 写成**名字清单** ⇒ 3 passed / 6 failed，
  六条失败臂正是「名字 vs 路径」的判别力（改名过的文件、目录、另一侧的位置、带点的兄弟目录、
  检出布局，以及清单连自己该放行的 `<data>/settings.toml` 也拒掉）。转录 `task-07-desktop-red.out`。
- **Agent 侧没有实现级的先红**（迁移本来加性、本来只写一个路径）⇒ 如实登记，红全部来自变异。
  这一条必须留着：`no such file` 式的红什么都不证明，而「已经在做正确的事」的代码也没有可红的实现。
- 变异 desktop **9/9**、agent **6/6**、0 unproven（每次跑完从 pristine 还原并校验 sha256）。
  **第一轮 desktop 是 7 条，有两条臂没有任何变异能打掉**（`the_two_roots_are_siblings_with_disjoint_sites`、
  `allows_a_path_outside_both_roots`）——不是记分问题而是判据上的洞：关掉「拒绝」到不了量常量关系
  与量作用域的两条臂。补 M8（组件常量抄错，两个根重合）与 M9（去掉数据根那个合取项，于是判据会拒掉
  包内暂存的 `agent.toml`）后逐条有主。
- **两处过程订正（都不静默）**：① agent M4 首轮「打不掉任何用例」，根因是那条路径臂有个**真盲点**
  ——它的 planting 先调了一次 `apply_migrations`，于是「每次 apply 都产生的路径」在 before 快照里
  已经有了，该臂原来只量得到**第二次**（升级那一次）的写入集 ⇒ 补第二个比较（以「用例动手之前的
  目录」为基准，`after - empty - planted` 必须恰好是 `{DEFAULT_DB_NAME}`），补法是**补一个比较**
  而不是改断言；② agent M6 首版锚在迁移循环**之前**，四条臂是被 `sqlite3.OperationalError:
  no such table` 打红的——**一个异常不是那条被禁止的写入** ⇒ 锚点移到循环之后，现在只打掉加性臂、
  报文是丢行。M6 本身就是里程碑那条禁止行为的形态（升级清掉它以为是过期的待回传结果）。
- 计数：desktop **372 passed / 0 failed / 5 ignored**（363→372，+9 = 九条臂；警告 7→7，
  `#[cfg(test)]` 不引入 `dead_code`）；agent **401 OK**（397→401，+4）。
- **作用域如实登记**：两个根之外的路径（要暂存的产物、cache、日志树）不在本判据之内。
  Agent 侧的用户设置/检查点/待回传结果**在库里的表**上（由加性臂逐行覆盖），
  「库旁的一切」由路径臂覆盖——两侧看起来不对称，是因为承载数据的方式本来就不同。

## T-08（已收尾，2026-09-25）

- **没有代码改动**：T-08 的交付是**读数与覆盖标注**（任务行的判据），`m2b_local_acceptance.py` 与
  `verify_m2_acceptance.py` **都原样未改**（§5 Add 只列「重跑记录」，Not Doing 明写不重写稳定脚本）。
- **链路自己全绿**：`m2b-local-acceptance.sh all` 的十三个阶段逐条 PASS，0 ERROR
  （迁移 `0 applied, 39 total`；Cloud／Agent／BitBrowser via Agent／assets fresh／DMG fresh／
  login smoke）。真 MySQL 另有一条独立读数（26 表／39 迁移／`source_contents` 570／`crawl_tasks` 73），
  迁移目录最新一条正是 `20260922_038` ⇒ 这一步是**幂等空跑**，不是「有新迁移没应用」。
- **三条链路够不到的读数**（这是本任务真正的产出）：
  ① `verify_m2_acceptance.py` 的 5 条 ERROR **全部是指针过期**且逐条落到提交——移动 3 条
  （`bf499d9`／`51f2ee4`（留 shim、值不变）／`3bcf2c7`）、**有意删除 2 条**（`30b9ebf`，
  不是移动）。0 命中带分母与阳性对照（同两条模式对 `30b9ebf^` 命中 3／1）。repointed 副本
  exit=0 **只作控制**（#4/#5 那两处是我换的 needle，是**替代**不是**复原**）。它是既知红项
  （`test_verify_m2_acceptance` ×1），README 那句「a Cloud file that no longer exists」**只覆盖 5 条里的
  1 条**——README 与 conventions 都在不得触碰的脏文件之列 ⇒ 只登记。
  ② 链路的 DMG 腿只证「文件存在且新鲜」（`verify_dmg`：`is_file` + 非 0 + `check_fresh`），按 D 的契约
  它造的包**不完整**（`Contents/Resources` 只有 `resources/`、sidecar `flags=0x10002(adhoc,runtime)`、
  app 日志说「这个安装包不完整」）。在链路之外换成发布包（受控对照，`build-release-macos.sh` exit=0）
  后拿到 **T-01／T-04 在真包上的首条读数**：校验**通过**（`sha256=355dc0da…`，与包内记录同值）、
  sidecar 真的被拉起、就绪闸门按出货 `15000ms` **真的超时**并附末 10 行、`Local Agent 已停止`。
  ③ 但 app 的 Local Agent **仍然**起不来——`OSError: [Errno 48] Address already in use`：8765 被
  **链路自己**起的 Agent 占着（pid 54456），而 D-02 规定槽位为空时不发探针 ⇒ app 不知道端口有人。
  **两条独立成因，只修一不够**；**这不是 D 造成的回归**（②旧有，①在 D 之前是「spawn 后立刻死」，
  D 让它变成「启动前说清原因」——那一半是**读证**，未跑 D 之前的树）。
- **覆盖情况逐条**：真 MySQL ✅、真 BitBrowser（54345，`profile_count=40`）✅、**实网 ❌**
  （Cloud 的 `logs/external.log` 今天零写入，mtime 停在 2026-09-23，那是 CHG-052 的 M3 E3 留下的）、
  **实凭据 ❌**（`wt-media-cloud/.env.local` 不存在 ⇒ 不注入 `WT_MEDIA_DOUYIN_*`；`config/credentials/douyin.toml`
  存在且 Cloud 启动时读它，但没有任何一步用它发请求；其值未读取）、**GUI ❌**（只 `open`，无交互）。
- **一处我造成的状态变化如实登记**：链路的 DMG 路径上现在是**发布流程**那份（17,125,121 字节，
  对照链路那份 16,373,051）；重跑链路会换回去。环境照旧：Cloud 54410、Agent 54456、app 66413。
- 新增的 9 份转录落盘前扫过凭据形态：0 命中，阳性对照 `primary.toml`／`douyin.toml` 分别 1／2 命中。
- **本仓门禁**：三个校验器全绿 + `unittest discover -s tests -q` **Ran 69 / failures=4**，四条逐条同名于
  T-06／T-07 ⇒ 无新增红、无意外转绿（`task-08-gate.out`）。

## T-09（已收尾，2026-09-25）

- **两条吸收项，两条判据都是行为判据**（不是字符串包含）：
  ① **skill 路径真的 resolve**——`skills/agent/agent-platform-adapter-change/SKILL.md:12` 指着
  `src/wt_media_agent/platforms`，那个目录**不存在**（平台代码早搬到 `clients/` 下了）。
  新增 `tests/test_skill_paths_resolve.py`（4 条）先红点名它，改指 `clients/<platform>` 后转绿。
  ② **生成副本与源一致**——`sync_skills.py check` 先红且**逐份点名 4 份**，`sync` 后绿；
  再用**剥掉 3 行生成头后的逐字节比对**独立复核（**不采信 `sync_skills.py` 的自述**），4/4 `IDENTICAL`。
- **分母与阳性对照都在案**：候选路径 **33 个 / 10 个 skill**（逐文件分布见转录段 C），
  下界 `>=20` 使「一个候选都没匹配到还报绿」不可能；被排除形态的**基底逐条 `exists`**
  （8 个目录 + `delivery/milestones/M*.md` 5 个文件）——反面论证的证据在这里，不然「筛掉真问题」无从排除；
  解析步另有独立阳性对照（`skills/__definitely-not-here__/x` 必被报出）。
- **判据证不到什么已写进模块注释与证据 §2.5**（三条）：首段拼错（`delvery/milestones`）会被当成
  「不是路径」**静默跳过**，不是在报红；不检查符号级搬迁（文件在、函数搬走）；写错**仓**时
  只要该仓里恰好同名也不会红。不要把它读成「skill 已经没问题了」。
- **Agent 侧文档**：新增 `tests/test_contract_docs.py`（6 条）先红点名 **3 条 dangling revision**
  （`local-agent-api` 写 `2026.09.06.1` 而定义文件是 `2026.09.24.1`；`local-event-schemas` 与
  `local-status-enums` 写 `2026.07.14.6` 而定义文件已到 `.9`／`.8`；`local-error-codes` 那对**本来就对**）
  与 **3 条漏列端点**。revision 一律**从定义文件读**（`revision:`／OpenAPI 的 `info.version`），
  YAML 仍是唯一源；端点列表做成**双向相等**——首版写 `checked >= 10` 的下界**把有用的报文吃掉了**
  （只报 `7 not greater than or equal to 10`），改成相等 + `assertGreater(checked, 0)` 后才报出
  「omits `/api/v1/health`」。另清掉两句**自相矛盾**的「尚无正式定义」（而同一目录 `v1/*.yaml` 全是活的），
  给 `AGENTS.md` 补 `## Configuration` 段（`config/` vs `config_online/`、冻结侧推导、凭证规则）
  与三处漏列（`clients/platform_urls.py`、`local_api` 的 `health.py`/`reporting.py`、`utils`）。
- **两处过程订正，都不静默**：① skill 转录**第一遍先跑了 `sync` 再取「同步前」读数**，
  于是那张表显示 `up to date / exit=0`——**那一次的表什么都不证明**；把 4 份副本还原到任务起点后
  按正确顺序重跑，才有 `out of date ×4 / exit=1`。② `git grep` 旧路径返回的是 **2 而不是 0**，
  因为 agent 树里那两份**还没跟上的副本**也含它——**那正是「源改了、副本没跟上」这件事本身**，
  不是判据坏了，转录里按这个说法标注。
- 计数：workspace **Ran 73 / failures=4**（69→73，**+4** = 新文件 4 条，**失败数与四条名字都不变**，
  与 T-06／T-07／T-08 逐条同名）；agent **Ran 407 / OK**（401→407，**+6**）；三个校验器绿。
  **增量来源做了对照**：把新文件移走重跑 `Ran 69 / failures=4`，放回 `Ran 73 / failures=4`。
- **三处顺手发现按 Q-06 登记、不修改**（`evidence/task-09-absorbed.md` §6，都不在 §5 的 Add/Modify 清单内）：
  ① `config/contract-map.yaml:72` 的 `local_agent_api.contract_revision` 停在 `2026.09.06.1`，
  而它指向的定义文件已是 `2026.09.24.1`——成因钉在 git 上（`87b1264` 改了文件没改 map），
  而 T-06 又把 map 定为契约版本的**唯一权威**，于是发布记录如实引用了一份过期的声明。
  **这与已知红项 #1 不是同一件事**：那条比的是「`verify_m0_config.py` 的 M0 期望值 vs map」，
  「map vs 定义文件」这一对**今天没有任何守卫**。
  ② OpenAPI 的 `paths:` 只有 10 条，而 `server.py` **实际提供 16 条 `/api/v1/*`**（含 `/healthz` 共 17），
  差的 7 条里 **6 条在 Desktop 的 Rust 里有真实调用点**（阳性对照 `profile-scans` 1、`account-check` 3），
  **第 7 条 `profile-delete` 两个仓都没有消费方**（desktop 仓 0 命中，agent 仓只有它自己那一行，
  连同名测试都没有）——既是文档缺口，也是**没人用过的代码路径**。
  ③ `wt-media-agent/scripts/README.md` 漏列 `build_desktop_sidecar.py`（CHG-053 Task 7 点名过，
  但不在本 CHG 的 Add 清单）。
- 本次**没有跑真机**：产物全是文档与静态判据，没有需要真进程的部分。

## T-10（已收尾，2026-09-25）

- **先红不是我编的检查，是治理门禁自己给的**（`evidence/task-10-gate-red.out`）：`git mv` 归档之后、
  回写之前，`verify_delivery_governance.py` 报 `ERROR current context references missing CHG:
  CHG-20260923-059` + `ERROR ledger references missing active CHG`（exit=1），`verify_agent_entry.py`
  报同名两条。「回写」这个任务因此不是顺手更文档，而是**逐条消掉这两条 ERROR**。
- **回写清单**（每条都指到文件与位置）：架构基线**五处**——§2.7 退出（请停→宽限→强杀、报告要能区分）、
  §6.5 启动/退出（包一致性校验**不回退**、两段式就绪 + 401 致命第三态、`daemon_threads = False`）、
  §7.9 五类版本各一来源 + Desktop↔sidecar 是 **pin 不是等值**、§7.10 升级不覆盖是**路径判据**
  （并写明本程序**不实现升级器**，故 #8 是判据不是读数）、§1244 配置随产物分发（补暂存发生在产物上、
  不进 `bundle.resources`、冻结侧由可执行文件位置推导）；里程碑状态改 **已完成（2026-09-25）**
  （四阶段链接 + 三处例外 + Q-05）；程序总纲的状态行与承载 CHG 列表改指 `completed/`；
  `config/release-matrix.yaml` **只加** `acceptance_notes` 三条（`0.2.5` 的 status 与三条
  `manual_acceptance` 一字未动）；`LEDGER.md` 撤活动行、加归档段、重写「后续阶段」段；
  `planned/README.md` 两处（顶栏与阶段表）；`delivery/planned/CHG-20260923-053/change.md:9`
  那条**CHG-057 归档时点名「等 059 自己关闭时处置」**的坏链按同一做法订正；快照 `--no-active`
  重生成（`Active CHG: none`）。**回写后同一对命令 exit=0**（`evidence/task-10-gate-green.out`）。
- **D-08 的落点（D-26）**：`config_online/agent.toml:17-21` 与 `config_online/README.md:14-16` 里那段
  「still open … Resolve before release」改写为「已裁定（Q-01，2026-09-25 关闭）：保持回环」。
  **判据是「解析后的文档相同」而不是「逐行相同」**：`tomllib` 解析前后**叶子 12 条全等**，
  阳性对照（改一个值）报 False ⇒ 值、CSP、行为一个字节没动。先红是同一个文件里新加的
  `tests/test_config_shipping.test_the_shipped_configuration_claims_no_open_question`
  逐条点名三条措辞（`README.md:15 states 'still open'`、`agent.toml:18`、`agent.toml:21`）；
  扫描的是**措辞不是问题号**——Q-01 被回答了，「Q-01」这三个字本身不再有害，出货包里不该有的是
  「还没定」这个**断言**。`Ran 12 tests / OK`（`evidence/task-10-config-claims.out`）。
- **归档两遍扫描**（`evidence/task-10-archive-scan.out`）：
  ①**字符串扫描**：旧落点字面量在当前工作树 **0 命中 / 673 个被跟踪文件**，阳性对照打在 `54c87b2^`
  上 **5 个文件命中**（`.ai/CURRENT_CONTEXT.md`、`LEDGER.md`、里程碑、`planned/README.md`、程序总纲）。
  **第一遍曾命中 1 处，是本节自己的草稿**——写「0 命中」的那句话里把旧路径抄了一遍。这条留着：
  扫描抓得住真东西，而我自己就是它抓到的一个。另一条口径：`delivery/active/` 这个**目录约定**
  在 `AGENT-INDEX.md`／skills／MASTER_PLAN 里有 59 处正当引用，不属于要清的东西。
  ②**链接 resolve**：把全部 423 个 md 里的 110 条相对链接逐条解析，对着 `54c87b2^` 的副本做**前后差集**：
  **新弄坏 0 条**、**弄好 4 条**（三条上游 CHG 指针 + CHG-057 点名的那条 `planned/053`；此数由「5」订正为「4」，重测依据见证据 §4.2）；
  另按 CHG-058 立下的先例（`../completed/X` → `../X`）订正 `change.md` §3 里三条**本来就少一层**的上游链接。
  **剩 5 条坏链**：3 条是 CHG-052 证据里少一层 `../` 的（目标文件真的存在，按 **Q-08** 登记不改，
  因为改的是 M3 时期另一个 CHG 的既有证据、不在 §5 清单内）、2 条是 CHG-057／058 归档证据里
  **反引号内引用「这条链接坏掉了」这个历史事实**（叙述，按「路径判修、叙述判留」保留）。
  **扫描自身的局限已写进证据**：正则不区分代码跨度与正文，引号里的历史链接会被算成坏链——这 5 条里 2 条如此。
- **同集合阳性对照**（`evidence/task-10-gate-green.out`）：`git archive HEAD` 的副本放在
  **`wt-media/.t10-control/`**（与 `wt-media-workspace/` 同层，能看见 `../wt-media-*`，避开 T-06 记的陷阱），
  `Ran 73 / failures=4`，四条名字与工作区**逐条同名**；并另做一条**兄弟仓可见性**的对照
  （按用例同样的相对路径读 `../wt-media-agent/src/wt_media_agent/local_api/server.py` 等三个文件，
  全部 `OK`）——不然「同名」也可能只是两边都 skip 了。
- **独立提交**：`54c87b2` 是**纯移动**（66 个文件 100% rename、`0 insertions / 0 deletions`，
  另两个 `--shortstat` 都报 0），写回与记录是它之后的另一个提交；agent 侧的注释与判据一个提交。
- **顺带发现一条既存的间歇红（D-27／Q-07）**：见下节。
- **一条如实登记的观察**：6 个「与本 CHG 无关、不得触碰」的脏文件里，有 5 个的 mtime 停在
  2026-09-24／09-25 00:44，只有 `docs/engineering/specs/2026-09-24-m4-m5-cloud-content-production.md`
  落在本 CHG 的工作窗口内（2026-09-25 09:10），而它的 diff 是**一个纯尾换行**。我没有对它做过有意的写入，
  也拿不出「是谁写的」的证据；因为它是**不得触碰**的文件，既不提交也**不还原**（还原同样是一次写入）。
  它对本次任何一条判据都没有影响。记在这里，免得下一个读 diff 的人怀疑是回写漏了这一处（证据 §8）。

## Blocked

- 无硬阻塞。Q-04 已由 D-17 关闭；AC-09「干净机」那一臂按 D-09 登记为未做（不以文字充当证据）。
- **Q-05 按 D-25 登记为未裁定、不阻塞收尾**：M2 链路的 DMG 构建是否改走发布打包，以及 M2 环境里
  8765 归谁。**在它关闭前，「app 端 Local Agent 在 M2 环境可用」这句话不成立**（AC-08 的例外）。
- **Q-06 按 T-09 登记、不阻塞收尾**：契约声明的两处漂移（map vs 定义文件的版本号、OpenAPI 少列 7 条
  实际被服务的路由）+ 一处文档漏项。三处都在本 CHG 的 Add/Modify 清单之外，
  按「讨论不是需求」只登记不改——**包括那条已过期的 `contract_revision` 一个字都不动**。
- **Q-07 按 D-27 登记、不阻塞收尾**：agent 套件里那条既存的间歇红（见下节）。在它关闭前
  「agent 套件全绿」这句话不成立；它也会随机打红后续任何一次门禁 —— **正因为如此才要登记**，
  免得下一个遇到它的人以为是自己刚改的东西弄红的。
- **Q-08 按 T-10 登记、不阻塞收尾**：CHG-052 证据里三条少一层 `../` 的链接（目标文件真的存在）。

## 既有间歇红（D-27／Q-07，如实登记，不在本 CHG 的修复范围）

- **是什么**：`tests/test_sidecar_entry.py::SigtermTests::test_a_request_in_flight_when_the_signal_arrives_is_waited_for`
  ——T-03 交付的那条「在飞请求要等」的用例。
- **不是本 CHG 造成的**：在**未改动**的原树上量（`git stash push -- config_online tests/test_config_shipping.py`
  之后跑 20 次）⇒ **1/20 失败**；`git stash pop` 还原。T-10 的改动只碰注释与一个新测试文件，
  与它无关（`git stash` 前后两次读数都出现过）。
- **机制只是假设，不是结论**：假设是「信号可能赶在连接被 accept、其处理线程登记之前到达」。
  判别实验用一次性探针（**不是**提交内容，跑完即删）把同一场景加一个 `PROBE_WAIT` 旋钮：
  最终读数（单进程串行、每次迭代 20s 上限的有界驱动）：真实例 **1/20**、探针不等 **6/40**、探针等 0.3s **11/40**。
  **方向与假设相反，但两边都不显著**：A/B 之差 Fisher 双尾 p≈0.55，而同臂两次跑自己就差了 3 倍
  （更早一次不等臂 2/40 ⇒ 同臂 2/40 vs 6/40，p≈0.53）；且三臂是**块状**跑的，块序与机器状态混在一起。
  ⇒ **不宣称机制**。更早那轮 15 次小样本（2/15 vs 0/15）曾读成「方向一致」，**已被推翻、不作数**。
  两次掉队的读数（一次输出没被捕获 0 字节、一次因重复执行只保下一臂）也如实记在证据里。
- **为什么不修**：加一个 `sleep` 正好是「凭一次跑通接受显然的一行修法」——它会把这个窗口从视野里藏起来，
  而不是解决它。按本 CHG 自己的规矩（先红要真红、否定结论要报分母），**登记 + 提 Q-07**，
  把「改测试还是改实现」这个判断留给拿到根因的人。

## Recent verification

- **T-10 之后（关闭门禁，2026-09-25）**：三个校验器**全绿**——`verify_delivery_governance.py`
  （`Delivery governance verification ok. Active CHG: none`，exit=0）、`verify_agent_entry.py`
  （快照 1668 字符 / 预算 8000，`Agent entry verification ok. 0 warning(s)`，exit=0）、
  `verify_skills.py`（10 个 skill 源文件），**同一对命令在回写前是 exit=1**（`task-10-gate-red.out`）——
  这条对照比「绿了」本身更有信息量。`unittest discover -s tests -q` **Ran 73 / failures=4**，
  四条与 `git archive HEAD` 副本（放在 `wt-media/.t10-control/`，兄弟仓可见性另做对照）
  **逐条同名** ⇒ 无新增红、无意外转绿（`task-10-gate-green.out`）。
  agent 侧 `tests/test_config_shipping.py` **Ran 12 tests / OK**（D-08 的判据），
  解析后叶子 12 条全等的阳性对照一并在此（`task-10-config-claims.out`）。
  **一条既存间歇红**（D-27／Q-07）使 agent 全仓套件的单次读数不再稳定，量测与两臂见 `task-10-flake.md`。
- **T-09 之后**（2026-09-25）：agent `bash scripts/test.sh` **Ran 407 tests / OK**（401→407，+6）；
- **T-10 之后**（2026-09-25，关闭时）：agent **Ran 409 tests / OK**（407→409，+2 = D-08 的两条判据；
  见 `evidence/task-10-agent-suite.out`）——**「这一次是 OK」不等于「agent 套件全绿」**，
  那条既存间歇红见下节。**上面这行去重过一次**：原先同一行被写了两遍（同一件事写了两遍不是两件）。
  workspace `unittest discover -s tests -q` **Ran 73 / FAILED (failures=4)**（69→73，+4 = 新文件 4 条），
  四条**逐条同名**于 T-06／T-07／T-08（`test_verify_m0_config` ×2、`test_verify_m2_acceptance` ×1、
  `test_verify_product_master_alignment` ×1）⇒ 无新增红、无意外转绿；**+4 的来源做了对照**：
  新文件移走 `Ran 69 / failures=4`、放回 `Ran 73 / failures=4`（`task-09-gate.out` 段 4）。
  三个校验器绿（`verify_delivery_governance.py` / `verify_agent_entry.py`（快照 2144 字符 / 预算 8000，
  0 warning）/ `verify_skills.py`（10 个 skill 源文件））。skill 侧另有一个**不依赖 `sync_skills.py`
  自述**的复核：剥掉 3 行生成头后 4 份副本与源**逐字节相同**（`task-09-skill-repoint.out` 段 8）。
  本次未重跑 `git archive HEAD` 的同集合阳性对照——T-09 没碰 workspace 的测试与治理脚本，
  四条红的读数与 T-08 那次完全一致（归档位置陷阱见 T-06 那条）。
- **T-08 之后**（2026-09-25）：**未改任何仓的运行时代码 ⇒ 计数不变**（desktop 372 / agent 401 仍是
  T-07 的读数，本次**未重跑**套件）。本任务重跑的是 **M2 链路**：`m2b-local-acceptance.sh all`
  十三阶段全绿（`evidence/task-08-m2-all.out`，0 ERROR、无 Traceback），外加固态矩阵的两条读数
  （`task-08-static-matrix.out` exit=1 的 5 条 ERROR 与 `task-08-static-matrix-repointed.out` exit=0 的
  控制）与真 MySQL 读数（`task-08-mysql.out`）。**发布流程在链路之外真跑了一遍**
  （`task-08-release-build.out`，`build-release-macos.sh` exit=0，产物判定「complete ad-hoc-signed app」），
  由此得到链路 DMG 腿的 before/after 对照（`task-08-dmg-before.out` / `task-08-dmg-after.out`）。
  **workspace 门禁跑了**（本任务的交付就是记录，门禁就是它的测试，`task-08-gate.out`）：
  `verify_delivery_governance.py`（Active CHG: CHG-20260923-059）、`verify_agent_entry.py`
  （快照 2144 字符 / 预算 8000，0 warning）、`verify_skills.py`（10 个 skill 源文件）三者全绿；
  `unittest discover -s tests -q` **Ran 69 / failures=4**，四条**逐条同名**于 T-06／T-07 的读数
  （`test_verify_m0_config` ×2、`test_verify_m2_acceptance` ×1、`test_verify_product_master_alignment` ×1）
  ⇒ 无新增红、无意外转绿；其中 `test_verify_m2_acceptance` 那条就是 §2 的 5 条，成因已逐条落到提交上。
  本次未重跑 `git archive HEAD` 的同集合阳性对照——本任务没碰 workspace 的测试与治理脚本，
  读数与 T-07 那次带对照的读数完全一致（重跑对照的归档位置陷阱见 T-06 那条）。

- **T-07 之后**（2026-09-25）：desktop `cargo test --workspace` **372 passed / 0 failed / 5 ignored**
  （363→372，+9 = 九条臂；编译警告 7→7）；agent `bash scripts/test.sh` **Ran 401 tests / OK**
  （397→401，+4）；变异 desktop **9/9**、agent **6/6**、0 unproven
  （`task-07-desktop-mutations.out` / `task-07-agent-mutations.out`，每轮从 pristine 还原并校验
  sha256：desktop `6ab1fc90…`、agent `248307e7…`；两处过程订正见 `evidence/task-07-upgrade.md` §4）。
  **workspace 门禁**（`task-07-gate.out`）：`verify_delivery_governance.py`（Active CHG:
  CHG-20260923-059）、`verify_agent_entry.py`（快照 2144 字符 / 预算 8000，0 warning）、
  `verify_skills.py`（10 个 skill 源文件）三者全绿；`unittest discover -s tests -q`
  **Ran 69 / failures=4**，四条**逐条同名**于 T-06 的读数（`test_verify_m0_config` ×2、
  `test_verify_m2_acceptance` ×1、`test_verify_product_master_alignment` ×1）⇒ 无新增红、
  无意外转绿。**本次没有重跑 `git archive HEAD` 的同集合阳性对照**——T-07 未改 workspace 的
  测试或治理脚本，读数与 T-06 那次带对照的读数**完全一致**；按 T-06 已登记的陷阱，
  若下次要重跑对照，归档必须放在能看见 `../wt-media-*` 的位置。

- **T-06 之后的 workspace 门禁**（2026-09-25）：`verify_delivery_governance.py`（Active CHG:
  CHG-20260923-059）、`verify_agent_entry.py`（快照 2144 字符 / 预算 8000，0 warning）、`verify_skills.py`
  （10 个 skill 源文件）三者全绿；`unittest discover -s tests -q` **Ran 69 / FAILED (failures=4)**。
  对照：把 `107ffb6`（T-06 记录之前的树）`git archive` 出来跑同一套件，失败的**同集合**四条，
  逐条同名（`test_verify_m0_config` ×2、`test_verify_m2_acceptance` ×1、
  `test_verify_product_master_alignment` ×1，与 `README.md` 既有红项清单逐条同名）。**无新增红、无意外转绿。**
  **对照本身有一处陷阱，登记在此免得后来者踩**：归档若放在 `../wt-media-*` 解析不到的位置，
  其中两条会**skip**而不是失败，于是对照只剩 2 条失败——看上去像「多了 2 条红」。
  归档必须放在与 `wt-media-workspace/` 同层能看见兄弟仓的位置（本次用 `wt-media/.t06main/`，
  读完即删），才是同集合对照。分母：归档 2 条失败 + 2 条 skip，真仓 4 条失败。
- **T-06 之后**（2026-09-25）：desktop `bash scripts/test.sh` **Rust 363 passed / 0 failed / 5 ignored**
  ＋ `tests/release-versions.test.sh` **20 passed / 0 failed** ＋ `tests/package-release-macos.test.sh` 绿
  （`evidence/task-06-desktop-suite.out`；本次未改任何 Rust 文件，读数与 T-05 相同，未重跑全仓）；
  agent `bash scripts/test.sh` **Ran 397 tests / OK**（`task-06-agent-suite.out`，未改）；
  变异 **15/15、0 unproven**（`task-06-mutations.out`，首行是 pristine 摘要 `56f18c18…`，
  每次跑完从 pristine 还原并校验）；真机五类与两条真红见 `task-06-reals.out`；
  **完整发布流程真跑一遍**（`build-release-macos.sh` exit=0，DMG 17,129,049 字节）——
  `--record` 与挂载 DMG 的 `--verify` 复算出**同一摘要**（`task-06-release.out:279,299`）。
- **T-05 之后**（2026-09-25）：agent `bash scripts/test.sh` **Ran 397 tests / OK**（HEAD 的树
  `git archive` 到 `/tmp` 后跑同一套件是 **382 OK**，差 = 本次新增 15 条）；desktop `cargo test`
  **363 passed / 0 failed / 5 ignored**（**本次未改任何 Rust 文件**，读数与 T-04 相同，未重跑全仓）；
  变异 agent **17/17**（跑完工作区复原并比对）。**注**：desktop 的 13 个 rustfmt 变更文件**仍保持
  `工作区 == rustfmt(HEAD)` 的脏状态**（`evidence/task-05-suite.out` 只报 agent 侧增量，就是因为
  desktop 这次没有可报的增量）。
- **T-04 之后**（2026-09-25，churn 还原后重跑）：desktop `cargo test`
  **363 passed / 0 failed / 5 ignored**，汇总行 `generated 7 warnings`（与基线同）；
  `git diff --name-only` = **13** 条，逐个核对为 `工作区 == rustfmt(HEAD)`（13/13）；
  两张变异表在**最终树**上重跑：常规 **13/13**、包内臂 **5/5**（跑完后工作区仍恰好那 13 个文件）。
- **T-03 之后**（2026-09-25，churn 还原后重跑）：desktop `cargo test`
  **353 passed / 0 failed / 4 ignored**，汇总行 `generated 7 warnings`（与基线同）；
  `git diff --name-only | wc -l` = **13**，逐个核对为 `工作区 == rustfmt(HEAD)`；
  agent `bash scripts/test.sh` **Ran 382 tests / OK**。
- **T-02 之后**（2026-09-25，churn 还原后重跑）：desktop `cargo test --workspace`
  **348 passed / 0 failed / 3 ignored**，汇总行 `generated 7 warnings`（与基线同）；
  同一棵树上 `git diff --name-only | wc -l` = **13**，且逐个核对为 `工作区 == rustfmt(HEAD)`（纯重排）。
- **T-01 之后**（2026-09-25，churn 还原后重跑）：desktop `cargo test` **344 passed / 0 failed / 3 ignored**；
  `cargo check --tests` 汇总行 `generated 7 warnings`（与基线同）；agent `tests.test_sidecar_entry`
  **Ran 5 tests / OK**（全仓 378 OK）。真机臂 `cargo test -- --ignored real_agent` 通过，
  阳性对照见 `evidence/task-01-readiness.md` §3.3。
- 激活时基线：agent **377 tests OK**；desktop **336 passed / 0 failed / 2 ignored**；
  workspace 三验证器绿 + `unittest discover` **69 tests / 4 failures**——**4 条红项为既知**
  （`test_verify_m0_config` ×2、`test_verify_m2_acceptance` ×1、`test_verify_product_master_alignment` ×1，
  与 `README.md` 的既有红项清单**逐条同名**），判定要用 `git archive HEAD` 的**同集合阳性对照**，
  不用「看着无关」。
