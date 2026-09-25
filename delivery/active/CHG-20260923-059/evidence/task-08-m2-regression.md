# T-08 证据：M2 业务回归

CHG-20260923-059 T-08（`change.md` §8）／AC-08。原始转录见本目录 `task-08-*.out`。

判据（T-08 行）：**`m2b_local_acceptance.py` 读数；实网/实凭据部分按 §7 如实标注覆盖与否**。
AC-08 另要求「M2 业务回归对 A/B/C/D 之后的树**通过**」。

---

## 1. 跑的是什么

| 项 | 值 |
|---|---|
| 命令 | `wt-media-workspace/scripts/m2b-local-acceptance.sh all`（→ `scripts/m2b_local_acceptance.py all`） |
| 时间 | 2026-09-25 11:53–11:57 |
| 树 | workspace `4f05cc1`、desktop `293806f`、agent `feb532d`（三者都是 T-07 的收尾提交）、cloud `f21bbcb` |
| 转录 | `task-08-m2-all.out`（453 行） |

转录里共 **13 个 `== … ==` 段**（行号即引用行；其中 Cloud／Agent／BitBrowser 在收尾的 `verify` 里各再算一段）：

| 阶段 | 行 | 读数 |
|---|---|---|
| Cloud 迁移 | `:1` | `migration ok: 0 applied, 39 total` |
| 启动 Cloud | `:410-412` | `cloud: started pid 54410` → `Cloud: PASS` |
| 启动 Agent | `:414-416` | `agent: started pid 54456` → `Agent: PASS` |
| BitBrowser 经 Agent | `:418-419` | `BitBrowser via Agent: PASS` |
| 清理旧产物 | `:421-425` | `rm -rf .generated/frontend` 与两个 bundle 目录 |
| 构建 Desktop 产物 | `:426-429` | `build-desktop.sh` + `cargo tauri build --bundles dmg --no-sign` |
| 挂载并启动 DMG | `:430-432` | `hdiutil attach` + `open /Volumes/WT Media/WT Media.app` |
| 重出 Cloud dist | `:434-435` | `npm run build:desktop` |
| `verify`：Cloud / Agent / BitBrowser | `:437-442` | 三条再次 `PASS` |
| `verify`：资产 / DMG 新鲜度 | `:444-450` | `Desktop assets: fresh`、`DMG: fresh` → `PASS` |
| `verify`：登录 smoke | `:452-453` | `Login smoke: PASS user=admin` |

**链路的每一条判据都绿**，无 ERROR、无 Traceback。下面三节是链路**没有**覆盖、由本任务另加读数的那部分——一条指针过期的静态检查腿（§2）、一条只证「文件在」的 DMG 腿（§3），以及覆盖情况（§4）。

---

## 2. 静态跨仓矩阵：5 条 ERROR 全部是**指针过期**，不是东西没了

`scripts/verify_m2_acceptance.py`（与链路是两条独立命令）：

```
ERROR: missing file: wt-media-cloud/internal/modules/cloudagent/compatibility.go
ERROR: .../agent/src/wt_media_agent/cloud_agent_contract.py: missing 'REQUIRED_CONTRACT_REVISION = "2026.07.15.1"'
ERROR: .../desktop/src-tauri/src/main.rs: missing '"wt-media-agent"'
ERROR: .../desktop/src-tauri/src/local_agent/mod.rs: missing 'fn consume_binding_ticket('
ERROR: .../desktop/src-tauri/src/local_agent/mod.rs: missing 'pub fn bind_session<T: BindingTransport>('
EXIT=1
```

（`task-08-static-matrix.out`）。逐条根因——每一条都是**今天另跑一次取证**得到的，不是「看着无关」：

| # | 脚本要求的 | 今天在哪 | 提交 | 性质 |
|---|---|---|---|---|
| 1 | `cloudagent/compatibility.go` 文件存在 | `cloudagent/**service**/compatibility.go`（`find` 唯一命中） | `bf499d9 refactor: migrate identity and cloudagent modules` | **移动**（同名文件全仓仅此一处） |
| 2 | `cloud_agent_contract.py` 里有 `REQUIRED_CONTRACT_REVISION = "2026.07.15.1"` | 字面量在 `clients/cloud/contract.py:11`（**值一字不变**）；旧路径只剩 21 行 re-export shim，首行即 `"""Deprecated import path. Use wt_media_agent.clients.cloud.contract."""` | `51f2ee4 refactor(agent): Cloud 客户端迁入 clients/cloud/，旧路径留 re-export shim` | **移动 + 留 shim**：脚本要的是`名 = "值"`这个**赋值形态**，shim 里只有名字（`from ... import`） |
| 3 | `desktop/src-tauri/src/main.rs` 里有 `"wt-media-agent"` | `sidecar/integrity.rs:69`（`SIDECAR_NAME`）与 `:75`（`COMPONENT`） | `3bcf2c7 refactor(desktop): 17 个 Tauri 命令迁出 main.rs（含 state.rs）` | **移动**；同一条 needle 里的 `local_agent_start` / `local_agent_status` **仍在** `main.rs:179/181` |
| 4-5 | `local_agent/mod.rs` 里有 `fn consume_binding_ticket(` 与 `pub fn bind_session<T: BindingTransport>(` | 全仓 **0 命中**（`grep -rc` 过滤后无输出）；活着的绑定路是 `commands/bind.rs:38,44`（`pub async fn local_agent_bind_session` 与 `let binding_ticket = args.binding_ticket…`） | `30b9ebf refactor(desktop): 删除 local_agent/mod.rs 的死代码，只留 BoundNodeFacts`（提交信息：删的是「有契约、无实现者」的一层） | **被有意删除，不是移动** |

**分母与阳性对照**（否定结论不能只报 0）：今天工作树里两条模式 `0 命中`；同两条模式对 `30b9ebf^:src-tauri/src/local_agent/mod.rs` 分别命中 **3** 与 **1** ⇒ 那个 0 是「真的不在」，不是模式写错（`task-08-static-pointers.out` 段 F／G）。

**控制**：把 5 处指针改到今天的落点后，同一条检查 **exit=0**（`M2 static cross-repository acceptance matrix ok`，`task-08-static-matrix-repointed.out`）。它回答的是「东西还在不在」，**不是**「脚本该这么改」：副本里我给 desktop 换的 needle（`commands/bind.rs` 的 `binding_ticket` / `local_agent_bind_session`）是我选的，原脚本要的那两个**函数形态**今天确实不存在——#4/#5 是「被删」而不是「搬家」，控制里那一处是**替代**，不是**复原**。

**它是既知红项，本任务补的是成因。** `tests/test_verify_m2_acceptance.py` 断言 `validate_static_matrix() == []`，它就是 workspace 那 4 条既知红之一（`unittest discover -s tests -q` 的读数里 `test_verify_m2_acceptance` ×1，与 T-06 的读数逐条同名）。README 的既有红项说明把它写成「`verify_m2_acceptance.py`（**a Cloud file that no longer exists**）」——**这句话只覆盖 5 条里的 1 条**：#1 才是云侧那一次移动，#2／#3 是 agent 与 desktop 的移动，**#4／#5 是 desktop 的有意删除（不是移动）**。`README.md` 与 `docs/engineering/specs/agent-workspace-conventions.md` 都在本 CHG **不得触碰**的脏文件之列（那 6 个与本 CHG 无关的改动仍未提交）⇒ **只登记、不改**；逐条成因与落点从本文件起可查。

**处置**：`verify_m2_acceptance.py` **原样未改**。§5 Add 只列「M2 回归的重跑记录（工具已有）」，Explicitly Not Doing 明写「不重写现有稳定脚本」；这份读数是**登记**（§6 D-25），不是修改授权。

---

## 3. 链路的 DMG 腿：它绿，但它证的是「文件存在且新鲜」

链路的这条判据是 `verify_dmg()`（`scripts/m2b_local_acceptance.py:258-263`）：`DMG_PATH.is_file()` + 大小非 0 + `check_fresh(...)`。它够不到「这个包能不能用」——而 D 恰好把「能用」定义成了判据（T-04 的运行期校验）。

### 3.1 before：按 D 的契约量，链路自己造的那个包是**不完整的**

（`task-08-dmg-before.out`）

| 读数 | 值 |
|---|---|
| `Contents/Resources/` | **只有 `resources/` 一个目录**（无 `sidecar-manifest.json`、无 `versions.json`、无 `config/`） |
| `Contents/MacOS/` | `wt-media-agent`（10,784,448）与 `wt-media-desktop-shell`（21,699,792） |
| sidecar 签名 | `flags=0x10002(adhoc,runtime)`——T-05／D-16 量过的「**起不来**」的那个形态 |
| app 日志 | `[WARN] agent.supervisor: 随应用的 Local Agent 校验失败：包内缺少记录文件 /Volumes/WT Media/WT Media.app/Contents/Resources/sidecar-manifest.json。这个安装包不完整，请重新安装完整的 WT Media 安装包。` 后跟 `[ERROR] webview: … Local Agent startup failed` |
| DMG | 16,373,051 字节 |

两个成因都在**链路的构建路径**里：`build_dmg()`（`:279-283`）只跑 `build-desktop.sh` + `cargo tauri build --bundles dmg --no-sign`，而写记录/暂存配置的那两步只在 `wt-media-desktop/scripts/build-release-macos.sh:36-37`（`stage-release-config.sh`、`repair-macos-signing.sh`）里。链路一路 `DMG: PASS`，而 app 自己在日志里说这个包不完整——**两条读数同时为真**，因为量的是两件事。

### 3.2 after：同一个位置换成发布包（只变这一项）

在链路之外跑 `bash wt-media-desktop/scripts/build-release-macos.sh`（**exit=0**，`task-08-release-build.out`；末尾自带 `verify-release-macos.sh` 的「complete ad-hoc-signed app」判定），再挂载、启动、读日志（`task-08-dmg-after.out`）：

| 读数 | before（链路自造） | after（发布流程） |
|---|---|---|
| `Contents/Resources` | 只有 `resources/` | `config/` + `resources/` + `sidecar-manifest.json` + `versions.json` |
| sidecar 签名 | `flags=0x10002(adhoc,runtime)` | `flags=0x2(adhoc)` |
| DMG 字节 | 16,373,051 | **17,125,121**（+752,070） |
| app 的第一条 agent 记录 | 校验**失败**（缺记录） | 校验**通过**：`sha256=355dc0da31e32ef0efe8731d5bdf7916f38290d892031dbe57bed2cd9fca9496 version=0.2.2 native_target=aarch64-apple-darwin` |
| 随后 | 没有 sidecar 可起 | sidecar **真的被拉起**（`sidecar_started`），然后 `OSError: [Errno 48] Address already in use`，退出码 1 |
| 就绪闸门 | 未走到 | 按出货的 `start_timeout_ms = 15000`（`resources/desktop.production.toml:46`）**真的超时**，报「没有报告就绪；它没有打印监听行」并附**末 10 行输出** |
| 收尾 | — | `Local Agent 已停止`（T-03 的退出路在真包上走完） |

包内记录的 `sha256` 与日志里校验通过时报的 `sha256` **是同一个值**，`version/target` 与 pin 一致（`agent-compat.json`）。

**这是 T-01 与 T-04 的第一条真包读数。** T-04 此前只有**手工搭的**包布局（AC-04 登记的例外是「没有双击启动真包的读数」）；今天补的是**阳性那一半**在真包上的读数——记录由签名脚本亲手写进真 DMG，app 启动时比对上真包里的二进制并通过。阴性那一半（篡改必拒）仍只在包内臂里量过，不因这条转述为已做。

### 3.3 sidecar 为什么起不来，以及为什么「只修 §3.1」不够

`lsof -tiTCP:8765 -sTCP:LISTEN` → **54456**，正是链路 11:54 起的那个 dev Agent。app 启动时受管槽位是空的，而 D-02 定的是「槽位为空时一次请求都不发」（那个端口上可能是别人的 Agent）⇒ app 不知道端口上有人，于是拉起自己的 sidecar，撞端口。

⇒ 这条腿有**两条独立成因**：

1. 链路的 DMG 构建路径落后于 D 的打包契约（§3.1）——补上就得到 §3.2 那份完整的包；
2. M2 环境里「链路起的 Agent」与「app 自带的 sidecar」是**同一个 8765 的两个提供者**（§3.3）。

**把①修好，app 的 Local Agent 在这个环境里仍然起不来**——§3.2 那条 `Errno 48` 就是原话。反过来，只消掉②（让链路不占 8765）而包不完整，仍然会红在 §3.1。

**这不是 D 造成的回归，是 D 让一件旧事可见**：②在 D 之前就成立；①在 D 之前不是「缺记录」而是「签名不对」——T-05 量过那份未重签的产物 `flags=0x10002(adhoc,runtime)` **且起不来**（`evidence/task-05-frozen-reading.out` 的 `raw-build` 段），而链路的包今天仍是那个形态。所以 D 之前这条腿的红是「spawn 之后立刻死」，D 之后是「启动之前就被拦下并说清原因」。**如实标注**：§3.2 的 before/after 是今天**跑出来的**；②的「D 之前也红」是**读证**（T-05 的 flags 读数 + 今天链路包的同一形态），我没有跑 D 之前的树。

### 3.4 处置：登记，不改脚本

- 本 CHG 的授权里没有改链路构建路径这一项（§5 Add 只列重跑记录，Explicitly Not Doing 明写不重写稳定脚本）⇒ 登记为 **D-25**、AC-08 的例外，并把待裁定的部分开成 **Q-05**（§6）。
- 我这次换 DMG 是**在链路之外**做的受控对照，不是链路的行为：**重跑一次 `m2b-local-acceptance.sh all` 会把那个位置换回链路自己造的包**。

---

## 4. 覆盖情况（判据的另一半：逐条标注，不静默省略）

| 项 | 覆盖 | 读数／依据 |
|---|---|---|
| 真实 MySQL（本机 3306，`wt_media_cloud`） | **是** | 链路 `:1` `migration ok: 0 applied, 39 total`；独立查库（`task-08-mysql.out`）：`tables=26`、`schema_migrations=39`、`latest=20260922_038_audit_fields`、`source_contents=570`、`crawl_tasks=73`。`migrations/` 目录最新一条正是 `20260922_038` ⇒ 今天这一步是**幂等空跑**，不是「有新迁移没应用」。凭据经 600 权限的 defaults 文件传入，不回显、不落盘，用完即删 |
| 真实 BitBrowser（本机 54345） | **是** | `BitBrowser via Agent: PASS`（`:419`、`:442`）；agent 日志 `bitbrowser_status=normal main_user_id=2c9bc061… profile_count=40` |
| 真实 Douyin **网络** | **否** | Cloud 记外部调用的 `logs/external.log` **今天零写入**（mtime 停在 2026-09-23 16:50，那是 CHG-052 的 M3 E3 验收留下的）；今天的 `logs/access.log` 37 行**全是本机 API 路径**（`/api/v1/auth/me`、`/browser-profiles`、`/proxies`…）。链路没有任何一步会向抖音发请求 |
| **实凭据** | **否** | `wt-media-cloud/.env.local` **不存在** ⇒ `local_douyin_env()`（`scripts/m2b_local_acceptance.py:69-102`）返回空，链路不注入 `WT_MEDIA_DOUYIN_*`。`wt-media-cloud/config/credentials/douyin.toml` **存在**（7,078 字节，`api_key`／`cookie`／`[headers]` 三键）且 Cloud 启动时读它（`internal/config/config.go:203`）——但**没有任何一步用它发请求**；其值我未读取。⇒「实凭据链路已验证」今天不成立 |
| GUI 交互 | **否** | 链路只 `open` DMG 里的 app：没有点击、没有走 C 的「本机设置」六步（那属于 C 的关闭门禁） |
| app 的 Local Agent 可用 | **否** | §3：包不完整（before）／端口被链路自己占着（after） |
| 静态跨仓矩阵 | **否** | §2：5 条指针过期，脚本未改 |
| 干净机安装 | **否** | D-09 已裁定登记为未做，本任务不重开 |

「否」都给了分母或原始读数，没有一条靠「看着无关」放过。

---

## 5. 仓库状态、计数与本次造成的状态变化

- **本任务未改任何仓的运行时代码** ⇒ desktop `372 passed / 0 failed / 5 ignored`、agent `401 OK` 不变（**未重跑**，读数是 T-07 的；本次不含 Rust／Python 改动）。
- **本仓门禁跑了**（记录型任务的交付就是记录，门禁就是它的测试，`task-08-gate.out`）：
  `verify_delivery_governance.py`（Active CHG: CHG-20260923-059）、`verify_agent_entry.py`（快照 2144 字符 / 预算 8000，0 warning）、`verify_skills.py`（10 个 skill 源文件）**三者全绿**；`unittest discover -s tests -q` **Ran 69 / failures=4**，四条**逐条同名**于 T-06／T-07（`test_verify_m0_config` ×2、`test_verify_m2_acceptance` ×1、`test_verify_product_master_alignment` ×1）⇒ **无新增红、无意外转绿**。其中 `test_verify_m2_acceptance` 那条正是 §2 的 5 条（它的断言是 `validate_static_matrix() == []`）。本次未重跑 `git archive HEAD` 的同集合阳性对照：本任务未碰 workspace 的测试与治理脚本，读数与 T-07 那次带对照的读数一致。
- `scripts/m2b_local_acceptance.py` 与 `scripts/verify_m2_acceptance.py` **原样未改**；`/tmp/chg059/` 下的两支配对脚本（`repoint_m2_matrix.py`、`run_repointed.py`）**不进仓**。
- **一处我造成的状态变化，如实登记**：链路 DMG 路径（`wt-media-desktop/target/release/bundle/dmg/WT Media_0.1.0_aarch64.dmg`）上的产物现在是**发布流程**那份（17,125,121 字节）；挂载点 `/Volumes/WT Media`，app pid **66413**。重跑链路会把它换回链路自己那份。
- 环境照旧在跑：Cloud pid **54410**（`127.0.0.1:18080`）、Agent pid **54456**（`127.0.0.1:8765`）。
- workspace 工作树里 6 个与本 CHG 无关的脏文件（`AGENT-INDEX.md`、`AGENTS.md`、`CLAUDE.md`、`README.md`、两份 `docs/engineering/specs/*.md`）本次**未动、未提交**；链路跑到的是它们所在的这棵树，读数不依赖它们的内容。
- 本节新增的 8 份转录落盘前扫过凭据形态（`password|passwd|api_key|cookie` 后接 `:`／`=`，以及 `Bearer `）：**0 命中**；同一条模式打在 `config/database/primary.toml` 与 `config/credentials/douyin.toml` 上分别 **1 / 2** 命中 ⇒ 这个 0 有分母、有阳性对照，不是空转。查库那次用的 defaults 文件（600 权限）用完即删。

---

## 6. 边界

- 未跑 D 之前的树做对照（§3.3 已标注为读证）。
- 未做干净机安装（D-09）、未做 Windows/x86_64（Q-03）、未验证实网与实凭据（§4）。
- 本任务不宣布「M2 业务回归通过」：链路自己的判据全绿，但 §4 那张表里 8 项有 **6 项为「否」**（实网／实凭据／GUI／app 的 Local Agent／静态矩阵／干净机），它们与 §3 的两条成因是这份读数的一部分。AC-08 按例外登记，不以文字充当证据。
