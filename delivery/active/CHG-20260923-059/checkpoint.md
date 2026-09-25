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

- **T-04 运行期完整性校验未开工**（T-01、T-02、T-03 均已收尾，见下三节）。
- 记录链：激活记录见 `0449604`；T-01 的代码、证据与回写见 `evidence/task-01-readiness.md`
  与对应的两个仓提交；T-02 见 `evidence/task-02-identity.md` 与 desktop 的 `15951a4`、`c54025a`；
  T-03 见 `evidence/task-03-exit.md` 与 agent 的 `70a1647`、desktop 的 `242f61e`。

## Next

- T-04 运行期完整性校验（启动前读 `sidecar-manifest.json` 验 sha256，失败拒绝启动；
  **`sha2 = "0.10"` 已是直接依赖**，不新增依赖；先造一个篡改一字节的必拒读数，再加完好的阳性对照），
  按 `先失败的验证/测试 → 最小实现 → 测试 → diff 检查 → evidence → checkpoint → 独立提交` 推进。

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

## Blocked

- 无硬阻塞。**T-06 内有一条待关闭的 Q-04**（「组件与资源版本」的**口径**——M-launch-engineering
  成功事实 #7 要求「发布可追溯五类版本」，而前端构建版本与组件/资源版本至今**没有任何表示**，
  是新建而非校验）。T-06 要么关闭它，要么如实退回给用户。

## Recent verification

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
