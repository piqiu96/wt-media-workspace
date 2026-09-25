# T-09 证据：吸收项——入口文档同步与 skill 路径 resolve

CHG-20260923-059 T-09（`change.md` §8）。原始转录见本目录 `task-09-*.out`。

判据（T-09 行）：**`sync_skills.py` 后生成副本与源一致；skill 里的路径真的存在（resolve 判据，
不只是字符串）**。吸收来源是 CHG-20260923-053 Task 7。

两条判据都不是字符串比对：一条要求**文件系统真的能解析**，另一条要求**剥掉生成头之后逐字节相同**。
本节把两条的**分母**、**阳性对照**与**证不到的部分**一并写下来。

---

## 1. 这一任务改了什么（与 §5 的 Add 清单逐条对齐）

| 吸收项 | 源文件 | 本次动作 | 判据 |
|---|---|---|---|
| skill 落点过期 | `skills/agent/agent-platform-adapter-change/SKILL.md:12` | 改指 `clients/<platform>` | resolve（§2）＋ `sync_skills.py check` 绿（§3） |
| Agent 入口文档 | `AGENTS.md`、`README.md`、`contracts/README.md` + 4 个领域 README | 同步为现状 | 新增 `tests/test_contract_docs.py` 先红后绿（§4） |
| 生成副本 | `.claude/skills` / `.codex/skills`（agent 仓与 root） | 由 `sync_skills.py` 重生成 | 剥头逐字节相同 4/4（§3） |

**新增的代码只有两个测试文件**（workspace 的 `tests/test_skill_paths_resolve.py`、agent 的
`tests/test_contract_docs.py`），其余全是文档。**这一任务不改任何运行时代码**。

## 2. 判据一：skill 里的路径真的能解析

### 2.1 先红（本任务的真实起点）

把源文件放回 HEAD 那一版——也就是**这条 skill 到今天为止的样子**——跑新写的用例：

```
FAIL: test_every_skill_path_resolves
AssertionError: Lists differ: ['skills/agent/agent-platform-adapter-chan[38 chars]rms'] != []
First extra element 0:
'skills/agent/agent-platform-adapter-change/SKILL.md: src/wt_media_agent/platforms'
Ran 4 tests ... FAILED (failures=1)
unittest exit=1
```

红在**一个真问题上**：`src/wt_media_agent/platforms` 在 agent 仓里**不存在**（`MISSING`，§2.4），
平台差异的落点早在 `clients/` 重构时就搬走了，只有这条 skill 还指着旧位置。
按 `git show HEAD:<源文件>` 量，这个字符串**改了的那一版里有 0 处、HEAD 那一版里有 1 处**——
所以它确实是这次改掉的，不是本来就干净。

### 2.2 分母（防「空转式通过」）

这条检查**今天看了 33 个候选路径，分布在 10 个 skill 源文件里**；逐文件分布见
`task-09-skill-path-test.out` 段 C（0 个的有 2 个 skill，最多的是 `executing-wt-media-change` 的 12 个）。
用例自己钉着两个下界（`skills >= 8`、`candidate >= 20`），使「一个候选都没有还报绿」不可能发生。
它另有一条**独立阳性对照**（`test_the_check_reports_a_path_that_is_not_there`）：先断言 `skills`
确实在已知首段集合里，再拿 `skills/__definitely-not-here__/x` 要求解析步报出它——
即「这条检查失败的能力」本身被证过。

### 2.3 被排除的形态：它们的基底目录**确实存在**（不是把真问题筛掉）

反面论证最容易变成筛掉问题的借口，故逐条给出基底读数：
`delivery/milestones`、`delivery/active`、`docs/product`、`docs/engineering`、`docs/contracts`、
`docs/decisions`、`config`、`scripts` 八个目录 `exists`；`delivery/milestones/M*.md` 是通配形态，
实际匹配到 **5 个文件**。被排除的形态本身举了两个可复核的例子（`<CHG>` 占位与 `M*.md` 通配，
见段 E）。分类的规则是**形态**的（含空格、无 `/`、以 `/` 或 `:` 开头、含 `<`/`>`/`*`），
不是「看着不像路径就跳过」。

### 2.4 修法与复核

```
resolves  src/wt_media_agent/clients
resolves  src/wt_media_agent/clients/platform_identity.py
resolves  src/wt_media_agent/clients/bilibili/identity.py
MISSING   src/wt_media_agent/platforms        ← 改之前那个落点（对照）
```

修好后同一条用例 `OK`，`unittest exit=0`。**33 个候选里只有这 1 个是真的坏的**——
这个数字也是这条判据的诚实边界：它不代表 skill 其余部分都正确，只代表**能被它看见的形态**里
没有别的坏落点。

### 2.5 这条判据证不到什么（如实登记）

- **首段拼错 = 静默丢弃**：只有**首段命中已知顶层条目**的候选才会被解析。所以
  `delvery/milestones` 这种拼错会被当成「不是路径」跳过，而不是报红。这条检查抓的是**在已知顶层目录
  之下的搬迁**，不是任何错字。（想抓这一类，判据得反过来：先要求首段像路径形态就一律解析。）
- **不检查符号**：`src/wt_media_agent/clients/cookie.py` 这种「文件在、函数搬走了」的写法看不出来。
- **根目录外的兄弟仓按目标分别解析**：`agent`/`cloud`/`desktop` 组的候选在各自仓根下解析，
  故一个 skill 若写错**仓**（把 agent 的路径写进 desktop 组），只要该仓里恰好同名也不会红。

## 3. 判据二：生成副本与源一致

`sync_skills.py` 的三步读数（`task-09-skill-repoint.out` 段 4→5→6）：

| 步 | 读数 |
|---|---|
| 源已改、副本未同步 → `check` | **4 份逐份点名**（root/codex、root/claude、agent/codex、agent/claude），`exit=1` |
| `sync` | `synced` 10 条（5 个目标的 ×2 工具），`exit=0` |
| 再 `check` | `skill outputs are up to date`，`exit=0` |

**独立复核（不依赖 `sync_skills.py` 自己的判断）**：把生成副本的前 7 行（frontmatter + 3 行
`GENERATED` 头）与源的前 5 行剥掉，其余逐字节比对——

```
IDENTICAL body  ../.claude/skills/agent-platform-adapter-change/SKILL.md
IDENTICAL body  ../.codex/skills/…                     （4/4 全 IDENTICAL）
```

旧路径 `src/wt_media_agent/platforms` 的命中数在同步后重测：源 0、4 份副本 0/0/0/0、
agent 仓 tracked 树 0 个文件。

**同步只动了预期的两份**：root 的两个目标 `commit_generated: false`，故不进仓；
agent 仓的 `git status` 只有 `.claude/skills/...` 与 `.codex/skills/...` 两个 ` M`。

**一处过程订正（转录内如实保留）**：第一次跑这条转录时**先执行了 `sync` 再取「同步前」的读数**，
于是「同步前」那张表显示的是 `up to date / exit=0`——**那一次的表什么都不证明**。把 4 份副本还原
成本任务开始前的状态（`git checkout -- .claude .codex` + 备份文件）后按正确顺序重跑，才有上表的
`out of date ×4 / exit=1`。另外 `git grep` 旧路径返回的是 **2 而不是 0**，因为 agent 树里那两份
**还没跟上的副本**也含它——**那 2 个命中正是「源改了、副本没跟上」这件事本身**，不是判据坏了。

## 4. agent 侧文档：三条 dangling revision 与三处漏列端点

### 4.1 先红

7 个文档全部放回 HEAD 那一版（本任务的真实起点），跑新增的 `tests/test_contract_docs.py`：
`Ran 6 tests / FAILED (failures=2)`，两条失败各自点名到底：

```
local-agent-api/README.md omits /api/v1/account-check, which paths: has
local-agent-api/README.md omits /api/v1/bit-browser/profile-groups, which paths: has
local-agent-api/README.md omits /api/v1/health, which paths: has
local-agent-api/README.md: revision 2026.09.06.1 is on no local-agent-api/v1/*.yaml (has ['2026.09.24.1'])
local-event-schemas/README.md: revision 2026.07.14.6 is on no …
local-status-enums/README.md: revision 2026.07.14.6 is on no …
```

### 4.2 逐条成因：README 写的 vs 同一目录 `v1/*.yaml` 真正带的

| 领域 | README 写的 | 定义文件带的 |
|---|---|---|
| `local-agent-api` | `2026.09.06.1` | `2026.09.24.1` |
| `local-event-schemas` | `2026.07.14.6` | `2026.07.14.9`, `2026.07.14.8`, `2026.07.14.8` |
| `local-status-enums` | `2026.07.14.6` | `2026.07.14.8` |
| `local-error-codes` | `2026.07.14.6` | `2026.07.14.6` ← **本来就对** |

两个数字的分布要分开说，免得读者以为「这些号全是脏的」：
`2026.09.06.1` 在 agent 仓全仓（分母 = tracked 文件）只出现 **1 次**，就是那份 README 自己——
**没有任何定义文件带它**；`2026.07.14.6` 出现在 **4 个文件**里，其中 `local-error-codes` 的
README 与它的定义文件是**正确的一对**，另外两份是过期 README（它们的定义已到 `.9` / `.8`）。

**判据的选择**：`revision` 从定义文件里读（schema／错误码文件的 `revision:`、OpenAPI 的
`info.version`），于是 YAML 仍是唯一源，改版是**一个文件**的事，而 README 只是被检查的一方。
读取**刻意不依赖任何库**——这个包声明 `dependencies = []`，PyYAML 不是其中之一。

### 4.3 修法与复核

端点列表与 `paths:` 做成**双向相等**（多一个、少一个都红），这是它不会退化成
「`paths:` 的第二份没人校验的副本」的原因；下界用 `assertGreater(checked, 0)` 而不是条数下限，
因为**条数下限会把有用的报文吃掉**（首版写 `checked >= 10` 时只报 `AssertionError: 7 not greater
than or equal to 10`，改成相等 + 非空后才报出上面那条「omits `/api/v1/health`」）。
改完 7 个文档，同一条用例 `Ran 6 tests / OK`。
**每一个断言都有一条阳性对照**：`test_the_revision_check_reports_a_stale_readme`（临时 YAML 上
「配对通过、过期报出」）与 `test_openapi_information_version_is_read_as_a_revision`。

### 4.4 两处 false claim 与新增的 `## Configuration` 段

文档里另有两句**自相矛盾**的话，不是版本号问题：`contracts/README.md` 写「M0 keeps directories
only as ownership placeholders; no formal OpenAPI, schema, DTO, SSE event, or error-code definitions
are active yet.」，`local-event-schemas/README.md` 写「M0 status: placeholder only」——
而同一目录下 `v1/*.yaml` **全是活的**，四份 README 自己也都在引用它们。

`AGENTS.md` 新增的 `## Configuration` 段写的是吸收项真正要留的知识：`config/` 是运行期唯一读的目录、
`config_online/` 经 `--config-dir` 整目录覆盖它、冻结侧由**可执行文件的位置**推导配置目录并先 WARNING、
凭证不从这两个目录来。同时补齐了三处漏列（`clients/platform_urls.py`、`local_api` 的
`health.py`/`reporting.py`、`utils`）。**复核口径**：把 `src/wt_media_agent` 的顶层模块与四个入口
逐条对回 `AGENTS.md`，现在**逐条都被点名**。

## 5. 吸收项的不变量：`config_online/` 在运行期零引用

`grep -rn config_online src/` → **0 命中**（分母 = `src/` 全部文件）；**阳性对照**：同一模式打在
`src/` 之外（tracked 文件里）→ **9 个文件命中**。这条不变量有测试钉着：
`tests/test_dependency_boundaries.py:542`（运行期文件里出现该值即失败）与
`tests/test_config_shipping.py`（整目录替换与它携带什么）。**这是 T-05 交付的性质，本节只做复核**。

## 6. 顺手发现、但**不在本 CHG 的 Add/Modify 清单内**，故登记不修改

三条都落在**别的文件**上，CHG-059 §5 没有授权改它们。按「讨论不是需求」的规矩，只登记（Q-06）。

### 6.1 7 条被服务、却没写进 OpenAPI 的路由

被服务的路径 **17** 条（`local_api/server.py` 的 16 条 `/api/v1/*` 加冻结的 `/healthz`），
`v1/local-agent.openapi.yaml` 的 `paths:` 声明了 **10** 条。差集是 **7 条**：
`/api/v1/bind`、`/api/v1/cookie-read`、`/api/v1/bit-browser/profile-create`、`profile-open`、
`profile-close`、`profile-update`、`profile-delete`。
这是 T-09 那两条用例**故意不覆盖**的方向：它们检查「README 说的 = 定义的」，不检查
「定义说的 = 服务端真的提供的」。

**其中 6 条在 Desktop 的 Rust 里有真实调用点**（分母 = `src-tauri/src`，命中数：
`v1/bind` 4、`cookie-read` 3、`profile-create` 2、`profile-open` 1、`profile-close` 1、
`profile-update` 1；**阳性对照**是 yaml 里本来就有的 `profile-scans` 1 与 `account-check` 3——
没有这两条读数，「上面那些 0 不是空转」这句话就无从谈起）。
**剩下那条 `profile-delete` 是 0**：`git grep` 在 desktop 仓**一个命中都没有**，
在 agent 仓里也只出现在它自己那一行 `local_api/server.py:486`（连同名测试也没有）——
即**被提供、却没有任何消费方**。这一条比「7 条都被消费」更值得记：
它既是文档缺口，也是**没人用过的代码路径**。

### 6.2 同一个契约有两份版本声明，而**没有任何东西在对账**

`config/contract-map.yaml:72` 的 `local_agent_api.contract_revision: "2026.09.06.1"` 与
`contracts/local-agent-api/v1/local-agent.openapi.yaml` 的 `info.version: 2026.09.24.1`
**互相矛盾**。git 时间线把成因钉死：

- `87b1264`（agent 仓，CHG-057 的 T-08「聚合健康检查 `/api/v1/health`」）把 `info.version`
  推到 `2026.09.24.1`，**没有同步改 workspace 的 map**；
- workspace 的 map 那一行最后一次变动是 M2-C 的 `988a010`（`2026.09.05.1` → `2026.09.06.1`）。

两份声明都活着，而且 T-06 明确把 **map 当作契约版本的权威**
（`release-versions.sh:17` 的注释与 `contract_versions()` 都只读 map），于是发布记录里
`local_agent_api=2026.09.06.1` 是**如实引用了一份自己已经过期的声明**。
**这与已知红项 #1 不是同一件事**：那条红是 `verify_m0_config.py` 把 M0 时代的号
（`local_agent_api` 期望 `2026.07.14.7`）硬编码在验证器里，比的是「验证器 vs map」；
本节讲的是「map vs 定义文件」——**这一对今天没有任何守卫**。

### 6.3 `wt-media-agent/scripts/README.md` 漏列 `build_desktop_sidecar.py`

`grep` 该文件对 `build_desktop_sidecar` **0 命中**。它在 CHG-20260923-053 Task 7 的吸收来源里
被点名，但**不在 CHG-059 的 Add 清单**里，故只登记。

## 7. 计数、门禁与仓库状态

| 树 | T-08 读数 | T-09 读数 | 增量 |
|---|---|---|---|
| workspace `unittest discover -s tests -q` | `Ran 69 / failures=4` | `Ran 73 / failures=4` | **+4**（新文件 4 条），**失败数与名字都不变** |
| agent `unittest` | `Ran 401 / OK` | `Ran 407 / OK` | **+6**（新文件 6 条） |

增量来源做了对照，不是推断：把新文件移走重跑得 `Ran 69 / failures=4`，放回得 `Ran 73 / failures=4`
（`task-09-gate.out` 段 4）。四条红的**逐条名字与 T-06／T-07／T-08 同名**（段 3）。
三个校验脚本全绿：`verify_delivery_governance.py`（`Active CHG: CHG-20260923-059`）、
`verify_agent_entry.py`（`0 warning(s) need review.`）、`verify_skills.py`（`verified 10 skill source files`）。

## 8. 边界

- **这一任务证的是「文档与它自称的源一致」与「skill 里的路径真的能解析」**，
  不是「文档内容全对」。§2.5 与 §6 列出的三类东西它看不见，不要读成「文档已经没问题了」。
- **`config/contract-map.yaml` 与 `docs/contracts/contract-map.md` 一个字都没动**（§6.2 只登记）。
- **workspace 的 4 条已知红项照旧**，本任务没有把任何一条变成绿，也没有新增红。
- 本次**没有跑真机**：这一任务的产物全是文档与静态判据，没有需要真进程的部分。
