# T-09 证据：回写、关闭门禁、端到端验收与归档

只记事实，不重复需求。每条给：命令或手工动作 / 期望 / 实际 / 通过或失败 / commit 或 diff 引用。

前置脚本：`/tmp/chg058/t09/precheck.sh`（`before` / `after` 两态，逐条报**命中数与文件数**即分母）。
产物：`precheck-before.out`、`precheck-after-final.out`、`desktop-tests-final.out`、
`agent-tests-final.out`、`web-tests-final.out`、`ctrl-head-final.txt`、`worktree-archived-final.txt`。

## 1. 先失败检查：回写前基线里应当**没有**这些事实

**为什么用这个形状**：T-09 是回写任务，它的失败态不是「测试红了」，而是「基线里本就写着答案」。
所以先逐条列出**本任务要写进去的事实**，问「基线里现在有没有」；每条都配一个**阳性对照**——
同一个 `git grep` 机制在一个必然命中的模式上必须报非零，否则「0 命中」只是空转。

范围（分母）：工作区 `docs/` + `delivery/milestones`；两个运行仓的入口文档
（`AGENT-INDEX.md` / `DIRECTORY_MAP.md` / `AGENTS.md` / `CLAUDE.md` / `README.md`）。
**CHG 记录自身不算基线**，不在分母内。

| # | 事实 | before | after |
|---|---|---|---|
| A1 | 装机态 cache 根 `~/Library/Caches/WTMedia/Desktop`（工作区基线） | **0 / 0** | **3 / 2** ✓ |
| A2 | `app_paths.rs`（工作区基线） | **0 / 0** | **1 / 1** ✓ |
| A3 | `local_settings_get`（工作区基线） | **0 / 0** | **1 / 1** ✓ |
| A4 | `local_log_tail`（工作区基线） | **0 / 0** | **1 / 1** ✓ |
| A5 | `data/versions,logs,cache` 目录树（架构 §5.8） | **0 / 0** | **1 / 1** ✓ |
| A6 | `app_paths.rs`（desktop 入口文档） | **0 / 0** | **3 / 2** ✓ |
| A7 | `settings.rs`（desktop 入口文档） | **0 / 0** | **6 / 2** ✓ |
| A8 | `local_settings_get`（desktop 入口文档） | **0 / 0** | **1 / 1** ✓ |

**8/8 事实在回写前确实缺失、回写后确实进入基线**。

### 1.1 已经变假、本任务要清掉的旧口径

| # | 旧口径 | before | after |
|---|---|---|---|
| B1 | desktop「18 个命令」 | **2 / 2** | **0 / 0** ✓ |
| B2 | desktop「按日期与 20MB 分档」 | **1 / 1** | **0 / 0** ✓ |
| B3 | agent「按天保留与总量上限」 | **1 / 1** | **0 / 0** ✓ |
| B4 | 程序总纲「出现真实需求时再入基线」 | **1 / 1** | **0 / 0** ✓ |

### 1.2 阳性对照（同一套 grep，必然命中的模式）

| # | 模式 | before | after |
|---|---|---|---|
| C1 | `desktop\.log\.<YYYY-MM-DD-HH>`（工作区基线） | 1 / 1 | 1 / 1 |
| C2 | `data/.*logs/.*versions`（架构） | 1 / 1 | 1 / 1 |
| C3 | 「轮转」在 desktop 入口文档 | 6 / 3 | 9 / 3 |
| C4 | 「轮转」在 agent 入口文档 | 3 / 2 | 1 / 1 |
| C5 | 「保留」在 agent 入口文档 | 8 / 3 | 8 / 3 |

**5/5 对照活着**，故上表的 0 是「真的没有」，不是 grep 打不中。
C3 上升、C4 下降都是改写本身的结果（desktop 侧把「轮转与限额」拆成轮转 + 保留两句；agent 侧
旧句里的「轮转」被按小时切割的具体说法吸收），两者都非零，未变成空转。

### 1.3 这个先失败检查**自己**暴露出的两个模式缺陷（如实记录）

1. **A5 第一次写成了不存在的东西**：初稿模式是 `\.local/{data,logs,versions,cache}`，报 0。
   但那不是我真正写下的字串——实际写的是 `<repo>/.local/{data,data/versions,logs,cache}`。
   即**模式编码的是我对措辞的猜测，不是措辞本身**。改正后仍报 0，第二个原因更硬：
   **BRE 里 `{`/`}` 是区间语法**，含花括号的模式匹配不到字面花括号。最终去掉花括号，
   用 `data/versions,logs,cache`，命中。
2. **B3 的替换文本让旧模式失去区分力**：修完 B3 仍报 1，原因是我的新句子合法地含有
   「**没有总量上限**也没有单文件上限」。模式得收紧到**那个主张**（`按天保留与总量上限`）才归 0。
   这与既有教训 `negative-check-must-prove-it-can-fail` 是同一条纪律：
   「0 命中」必须先证明这个模式**能失败**。

## 2. 落地的回写清单

**工作区基线**

- 程序总纲 `docs/engineering/specs/2026-09-23-launch-engineering-optimization-program.md`
  §2 末行：`cache` 由「出现真实需求时再入基线」改为**已入基线**并给出两头真实路径
  （装机态 `~/Library/Caches/WTMedia/Desktop`、开发态 `<repo>/.local/cache`），
  并写明「**只有 Desktop 有 `cache`，Agent 侧没有**」「装机态不在数据根之内」。
  §3 `### CHG-C` 增补「落定后的口径」块（页面位置与路由、三处一致、**不经回环访问**、
  恰 9 个新命令及其名字、`settings.toml` 原子替换与 `save_dir` 无消费方、列表即白名单 +
  不在⇒0 / 读不到⇒`Err`、「该级别及以上」、清理规则含 `Other` 与一次只清一棵树与按独立 walk 对账、
  诊断包形状 + 归档外兄弟 `.sha256` + 双重 `mask` + 由**布局**而非名字过滤），末行链接到
  `../../../delivery/completed/CHG-20260923-058/change.md`。
  头部状态行改为「A、B 已归档；**C 已于 2026-09-25 归档 `DONE`**；D 待激活」。
- 架构基线 `docs/engineering/architecture/社媒运营平台工程架构与分层设计_V1.md`
  §5.8 增补 Desktop **四个根**（数据根 / `versions` / 日志根 / 缓存根）与装机态、开发态两套路径树，
  并写明「**缓存不在数据根之内**……清理命令要保护的『数据根』与它要清的『缓存根』是两个不同的根」；
  §6.8 的缓存条目改指 §5.8，并把「分布与限额」改为「分布与保留（**没有容量限额**——被限定的是历史留多久）」。
- 里程碑 `delivery/milestones/M-launch-engineering.md`：状态行记 C 于 2026-09-25 归档、
  **成功事实 #5 由 CHG-B 达成、#6 由 CHG-C 达成**；用户目标句「日志独立落盘受容量限制」→「按天保留」
  （T-02 修了 #5 却漏下这一行与之矛盾的表述）。

**运行仓入口文档**

- `wt-media-desktop`：`AGENT-INDEX.md`（`main.rs` 行 115 → **254 行 / 27 个命令 / 新命令追加在末尾**、
  本地安全桥、两条新的「本仓库拥有」、日志行改「轮转与保留……**没有容量限额**」、
  六条新需求路由、两条新禁止）、`DIRECTORY_MAP.md`（五个新模块行 + 五个新命令文件行、
  命令数 18 → 27、`logging/` 行按小时切割重写、`production.toml` 的 logging 键去掉上限键）、
  `AGENTS.md`（18 → 27 + 单实例守卫）。
- `wt-media-agent`：`AGENT-INDEX.md`（小时切割 / 稳定名 / 归档名 / 本机时区 / 整点 / 只按天保留 /
  默认 14 / 不控总量 + 「**两侧机制有意不对称**」）、`DIRECTORY_MAP.md`（`runtime/logging.py` 行重写）。
- `wt-media-cloud`：`AGENT-INDEX.md`（「本机设置」页与日志查看器的路由行 + 两条新禁止：
  页面里不得出现 `127.0.0.1`/`localhost`/`fetch(` 且**新模块要显式进 `localAgentBoundary.test.js`
  那份硬编码清单**、`.vue` 里不放可测逻辑）、`DIRECTORY_MAP.md`（两个新 features 目录、
  四个新测试文件、`localAgentBoundary.test.js` 行由「两个文件三条规则」改正）。

## 3. 关闭门禁读数

| 项 | 命令 | 实际 | 判定 |
|---|---|---|---|
| 交付治理 | `python3 scripts/verify_delivery_governance.py` | `ok. Active CHG: CHG-20260923-058`（归档前） | 绿 |
| 入口 | `python3 scripts/verify_agent_entry.py` | `ok. 0 warning(s)`；快照 2159 字符 / 预算 8000 | 绿 |
| Skills | `python3 scripts/verify_skills.py` | `verified 10 skill source files` | 绿 |
| 治理单测 | `python3 -m unittest discover -s tests -q` | `Ran 69 tests ... FAILED (failures=4)` | **4 条既知红项** |
| agent | `bash scripts/test.sh` | `Ran 377 tests ... OK` | 绿（起点 379，例外见下） |
| desktop | `cargo test --workspace` | `336 passed; 0 failed; 2 ignored` | 绿（起点 175） |
| cloud/web | `npx vitest run` | `Test Files 25 passed (25)` / `Tests 166 passed (166)` | 绿（起点 21 文件 101 tests） |

### 3.1 4 条红项的判据：同集合阳性对照（不是「看着无关」）

对照树是 `git archive HEAD` 抽出的树，**落点必须在真实 `wt-media/` 之内**
（`/Users/aqiuye/Develop/workspace/wt-media/wt-media-workspace-t09head/`）。
原因是一条实测教训：`tests/test_verify_m2_acceptance.py:25-28` 在
`required_repository_paths()` 不存在时 **`skipTest`**——把对照树放在 `/tmp` 会让路径敏感的
兄弟仓用例**静默跳过**，于是「4 条红」会被读成「2 条红」。**这正是 CHG-057 当初把 4 读成 2 的原因**。
外层 `wt-media/` 不是 git 仓，故把树放在那里不产生未跟踪噪声。

```
diff <(HEAD 对照树的失败项名) <(工作树的失败项名)   →   IDENTICAL
```

两棵树各 `Ran 69`、各 `failures=4`，四个名字逐名相同：
`test_contract_map_matches_m1_cloud_agent_compatibility`、
`test_contract_map_provider_paths_exist_in_full_workspace`、
`test_current_product_master_and_governance_are_aligned`、
`test_static_cross_repo_contract_and_security_matrix`。

**归档使其中 3 条错误消失、但失败名字集合不变**：`scripts/verify_product_master_alignment.py:230-231`
的 `validate_active_change` 在「没有 active CHG」时**直接 return**，故
「active CHG status must be …」「current repository is missing」「must have no pending questions」
三条随之不再产生；该测试仍因 M2/M3/M10 的既有不一致而失败。**名字集合不变**才是判据。

### 3.2 agent 379 → 377 这条例外

少的 2 条断言的是 `max_bytes` 与 `total_bytes` 的**互相约束**（交叉校验），
而这两个键已被用户裁定删除、**没有比较对象**。逐条列在 `task-02-log-rotation.md`。
同时用 `git grep` 复核 `BoundedFileHandler`：**8 命中 → 0**，阳性对照
`TimedRotatingFileHandler` 3 命中 / 2 文件、阴性对照 0——即「全仓 8 处引用都随实现改完」这句话
带分母且可失败。

## 4. 端到端验收（出货包，2026-09-25）

**包**：`bash scripts/package-release-macos.sh --output-dir /tmp/chg058/t09/output`
（`HTTPS_PROXY=http://127.0.0.1:7897` **只给该次调用**）→ 成功，产出
`WT-Media_0.1.0_macos-aarch64/{WT Media.app, WT Media_0.1.0_aarch64.dmg, sidecar-manifest.json,
agent-build-manifest.json, SHA256SUMS}` 与 `WT-Media_0.1.0_macos-aarch64.zip{.sha256}`；
`.app` 通过 `codesign --verify`（`valid on disk` / `satisfies its Designated Requirement`）。

**起跑前场况**：`8765` / `18080` / `54345` / `5174` 均无监听者，无 wt-media 进程
（开发者自己的端口未被动过；测试全程不占 `54345`）。

| 动作 | 期望 | 实际 | 判定 |
|---|---|---|---|
| 启动出货包 | 落盘**稳定名** | 新增 `desktop.log`；**旧的 `desktop-20260924-1.log` 原样留着**（不认的名字既不轮转也不删） | ✓ |
| 同上 | sidecar 起来 | `wt-media-agent` 监听 `127.0.0.1:8765`；`desktop.log` 记 `agent.supervisor: Local Agent 已启动（sidecar_started）` | ✓ |
| 同上 | 数据根 / 缓存根 | **两者都不建**——`AppPaths::prepare` 只在写路径调用，读方只用 `directory`（设计如此） | ✓ |
| 把活文件 mtime 推回 1 小时（`touch -t $(date -v-1H …)`）再启动 | 轮转出归档 + 重建活文件 | `desktop.log`（948 B，mtime 09-24 23:36）→ **`desktop.log.2026-09-24-23`**（内容即旧活文件**全部 5 条**），并**重建** `desktop.log`（334 B = 本次 2 条） | ✓ |
| 预置 15 天前的 `desktop.log.2026-09-10-00` + 1 天前的 `desktop.log.2026-09-24-20`，再启动 | 老删新留 | 15 天前**已删**、1 天前**留下**（`FileLimit::Age` 按归档名时间戳判，与进程是否连续运行无关） | ✓ |
| 九个新命令是否在出货二进制里 | 全在 | 逐名计数（原始字节，绕开 `strings` 的分行）`local_settings_get` 1、`local_settings_set` 2、其余各 2；阳性对照 `get_public_config` 1 / `log_js_error` 4，**阴性对照 0** | ✓ |
| 九个命令是否在**内嵌前端产物**里 | 全在 | 构建树 `.generated/frontend/assets/` 逐名 **9/9 命中**，阴性对照 0；且 `LocalLogsPage-d7LcNePf.js` / `LocalSettingsPage-gYyVkDYr.js` 两个**文件名本身**作为内嵌资源键出现在出货二进制里（各 1）⇒ 该包内嵌的正是这次构建 | ✓ |

**单实例守卫（AC-04）——用同一调用路径的配对观测，不用 `open -a`**

先说一个**被否证的观测方式**：`open -a` 一个已在运行的应用在 LaunchServices 层就是 no-op，
**根本不会产生第二个进程**，所以「第二次 `open -a` 后进程数没变」**什么都证明不了**。
改成直接 exec 二进制：

| 臂 | 动作 | 实际 | 判定 |
|---|---|---|---|
| 对照（无同伴） | `"…/MacOS/wt-media-desktop-shell"` 直接 exec，等待 15 s | **存活**；`desktop.log` **+3 行**（含 startup 摘要与 supervisor 那条） | 证明这条调用路径确实会走到日志装配并常驻 |
| 受试（有同伴） | 在对照存活时再直接 exec 第二个副本 | **退出码 0**、**+0 行**、shell 进程数仍 1、agent 进程数不变、无输出 | **守卫生效** |

`+3` 对 `+0` 是同一条路径上的可失败对照，不是「进程数看起来没变」。
与源码相符：`main.rs:120-135` 的注释写明链被切开、**守卫在一切碰日志目录的动作之前**，
故第二个实例在建日志文件之前就退出了——这也是它**零写入**的原因。

### 4.1 本轮**未做**的一步（如实登记，不静默吸收）

计划要求的「按页面点击走一遍：查看/修改保存位置 → 看日志（级别筛选）→ 打开日志文件夹 →
清缓存 → 清旧日志 → 导出脱敏诊断包」**以及打开诊断包逐个核对**，**未执行**。原因两条，都是环境事实：

1. 执行时会话处于**锁定态**：`ioreg` 实测 `"CGSSessionScreenIsLocked"=Yes`、`IOConsoleLocked = Yes`
   （`CGSSessionScreenLockedTime=1790267178`）。锁屏下 `screencapture` 只能拿到壁纸
   （两次实拍均如此），窗口既不可见也不可聚焦。
2. 本机**未授予 System Events 自动化权限**：`osascript … tell process "WT Media" to set frontmost`
   返回 `-1743 未获得授权将 Apple 事件发送给 System Events`，故没有可用的点击通路。
   （macOS 上 `tauri-driver` 无 WebKit WebDriver 支持，也不存在别的驱动通路。）

**已用不依赖点击的等价取证替代**（上表六条 + 命令名在二进制/内嵌前端产物里的双证据），
但「有人真的点过这六个动作」这件事**没有发生**。该臂并入 CHG-D 的干净机 `manual_acceptance`
一并做；本 CHG **不**据此宣称该 AC 的人工臂已验（§10 的 AC-08/AC-09 与 §13 第 5 项均已就地标注）。

## 5. 归档与失效指针扫描

**归档动作**：`git mv delivery/active/CHG-20260923-058 delivery/completed/CHG-20260923-058`；
`LEDGER.md` 活动表行移除（表内留下「当前无 active CHG」占位行）并新增 C 的归档段；
`planned/README.md` 头部与 C 行改 `DONE（2026-09-25 归档）`、D 行改「前置已满足，待激活」；
快照 `python3 scripts/prepare_ai_workspace.py --no-active` 冷启动重生成 → `Active CHG: none` / `Status: NONE`。

**扫两遍，因为这是两个不同的判断**：

### 5.1 字符串扫描（分母 + 阳性对照）

| 范围 | `active/CHG-20260923-058` |
|---|---|
| **档外**（排除归档记录自身） | 修前 **2 处 / 2 文件** → 修后 **0 / 0** ✓ |
| 档内（归档记录自身） | 3 处 / 2 文件，**判为叙述/过去时，一字未改** |

修掉的 2 处都在**活文件**里、都是**指针**（按「路径判修、叙述判留」）：
`delivery/completed/CHG-20260923-057/change.md:9`（该链接由 CHG-058 的 T-02 写入，
指 `../../active/…`）与程序总纲 §3 的 `../../../delivery/active/…`，**两者都改指 `completed/`**。

档内 3 处保留的理由：`change.md` 那处是本 CHG 自己的说明句；`evidence/task-01-activation.md`
的 `git mv …/active/…` 与 `mkdir …/active/…` 是 **T-01 那一刻的真实命令**，是对已发生动作的叙述
（今天重放没有意义），照 CHG-057 T-18 的先例保留。

**阳性对照**：同一模式族 `active/CHG-` 修后仍 **97 命中**（更宽的模式能命中 `active/` 形态）；
`completed/CHG-20260923-057` **14 命中 / 10 文件**。**阴性对照** `active/CHG-99999999-999` **0**。
故上面的「0」不是空转。

### 5.2 链接 resolve（与字符串扫描**不是**同一个 claim）

字符串扫描证明「没有旧路径的字符串」，它**证明不了**「新路径真能打开」。所以另跑一遍 resolve。

- 我改过的 19 个文件（归档记录全树 + `LEDGER.md` + `planned/README.md` + 里程碑 + 程序总纲 +
  架构基线）：**分母 62 条相对链接，坏 0** ✓
- 全仓：**分母 105 条链接 / 420 个跟踪的 `.md`，坏 9**，其中**与本次归档相关的 1 条**——
  实为 `completed/CHG-20260924-060/evidence/task-01-governance.md` 里的
  `| [CHG-20260924-060](active/…) | … |`，其中 `active/…` 是**省略号占位**、本就不是路径，
  且与本次改动无关。**本次归档造成的坏链：0**。
  （该正则对嵌套方括号/带空格的链接是近似的，分母 105 是它的下界；但「与本次归档相关」这一类
  已被前一条独立确认到 0，两条判据互不依赖。）

### 5.3 resolve 抓到一条字符串扫描**结构上**不可能发现的坏链

归档移动把 `change.md` 里一条链接弄坏了：它原写 `[CHG-20260923-057](../completed/CHG-20260923-057/change.md)`，
在 `active/CHG-20260923-058/` 下 `../completed/` 是对的；搬到 `completed/CHG-20260923-058/` 之后
就变成 `completed/completed/`，**字符串里没有任何 `active/` 痕迹**，故 5.1 永远看不见它。
已改为 `../CHG-20260923-057/change.md`（同级兄弟）。**这正是两遍都要扫的理由**。

## 6. 未动的范围外事项

- 用户既有的脏文件（workspace 根的 `AGENT-INDEX.md`/`AGENTS.md`/`CLAUDE.md`/`README.md`/
  `docs/engineering/specs/agent-workspace-conventions.md` 与三份 PRD、desktop 的 13 个既有乱格式
  文件、cloud 的未跟踪 `dump.rdb`）**一律未碰、未提交**。
- `.generated/frontend/index.html` 与 `index.desktop.html` 因本次打包重新生成（入口 chunk 哈希
  `index.desktop-Cgz6Qdso.js` → `-BDgQLqf2.js`，2 文件 2 行），是构建产物指纹，
  **单列一个 `chore(build)` commit**，不与记录或逻辑混提（照 `4ebf7d6` 先例）。
- 全仓既有的旧 `active/CHG-*` 失效指针（`057` 20 处、`021` 19 处、`032` 11 处等，多数在更早的
  归档记录与 `docs/superpowers/plans/` 内）**不是本 CHG 引入的，也不该由归档 058 顺手改**，
  只在 §5.1 报出分母，不动。
- 本机日志目录里由本轮验收造出的两个合成归档只用于触发规则，测完即删：
  被删的那个已由应用自己的年龄规则删除，留下的 `desktop.log.2026-09-24-20` 已 `rm`。
  用户既有的 `desktop-20260924-1.log` 与两条真实记录未删改。
