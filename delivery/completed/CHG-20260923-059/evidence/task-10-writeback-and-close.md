# T-10 证据：回写基线 + 关闭收尾

CHG-20260923-059 T-10（`change.md` §8）。原始转录见本目录 `task-10-*.out`。

判据（T-10 行）：**先失败的检查钉着回写；关闭门禁同集合阳性对照；档案两遍扫描**。

三条都不是我新编的检查：第一条用**治理仓自己的校验器**，第二条用**归档前那棵树**做同集合对照，
第三条是**字符串扫描 + 链接 resolve 两遍**（CHG-058 立下的先例：`active/` → `completed/` 移动会让
写在 `../completed/X` 的链接少一层，这正是两遍都要扫的理由）。

---

## 1. 先红是治理校验器给的，不是我编的

`git mv delivery/active/CHG-20260923-059 delivery/completed/…`（= 提交 `54c87b2`）落地之后、
**回写之前**，同一对治理命令：

```
$ python3 scripts/verify_delivery_governance.py
ERROR current context references missing CHG: CHG-20260923-059
ERROR ledger references missing active CHG: CHG-20260923-059
exit=1

$ python3 scripts/verify_agent_entry.py
ERROR execution snapshot references missing CHG: CHG-20260923-059
ERROR LEDGER references missing active CHG: CHG-20260923-059
exit=1
```

这条红的理由与要证的性质**同源**：校验器说「快照与 LEDGER 指向一个不存在的 CHG」，
而 T-10 要做的正是让它们指向存在的那个。转录：`evidence/task-10-gate-red.out`。
（同一时刻 `verify_skills.py` 是绿的——它不管 CHG 落点，绿是正常的，不是漏报。）

回写完成后**同一对命令** exit=0，附 `verify_skills.py` 与 workspace 套件：

```
$ python3 scripts/verify_delivery_governance.py
Delivery governance verification ok. Active CHG: none          exit=0

$ python3 scripts/verify_agent_entry.py
execution snapshot: 1668 characters (~667 tokens, budget 8000 characters)
Agent entry verification ok. 0 warning(s) need review.          exit=0

$ python3 scripts/verify_skills.py
verified 10 skill source files                                  exit=0

$ python3 -m unittest discover -s tests -q
Ran 73 tests ... FAILED (failures=4)
```

转录：`evidence/task-10-gate-green.out`、`evidence/task-10-workspace-suite.out`。

## 2. 回写清单（与 §5 的 Add/Modify 逐条对齐）

| 落点 | 动作 | 行数 |
|---|---|---|
| `docs/engineering/architecture/社媒运营平台工程架构与分层设计_V1.md` | 五处新增段落：§5.8 出货配置怎么进产物、§2.7 退出协议、§6.5 完整性 + 两段式就绪 + 活性探针、§7.9 五类版本 + pin、§7.10 升级不覆盖的路径判据 | +49 |
| `delivery/milestones/M-launch-engineering.md` | 状态 → **已完成（2026-09-25）**，四个 `../completed/…` 链接，成功事实 #5→B / #6→C / #4,#7,#8→D，**三处例外随达成登记**，Q-05 记未裁定 | +15/−5 |
| `docs/engineering/specs/2026-09-23-launch-engineering-optimization-program.md` | 状态行 → 四阶段全部关闭；承载 CHG 的 D 指针改 `../../../delivery/completed/…`；§3 新增「落定后的口径」块（九条事实的权威落点） | +41 |
| `config/release-matrix.yaml` | **只加** `acceptance_notes`（D-09 的裁定与 status 保持 `verifying`、T-08 的 M2 重跑 13/13 与三处未覆盖、D-22 为何不加 `version_classes:`）；status / manual_acceptance / residual_risks **一字未动** | +4 |
| `delivery/LEDGER.md` | 活动行换为「当前没有 active CHG」；新增 059 关闭段（锚点 #7/#8/#4、交付面、DONE Gate 九项、AC-02/AC-09「一半」+ AC-08 例外、三仓计数、四处实测意外、Q-05/Q-06、D-09 与 onefile SIGTERM、`0.2.5` 保持 `verifying`、间歇红） | +4/−2 |
| `delivery/planned/README.md` | 首行 → 当前没有 active CHG，四个 CHG 全部列出为已归档；阶段表 D → `**DONE（2026-09-25 归档）**` | +4/−4 |
| `delivery/planned/CHG-20260923-053/change.md` | 第 9 行 CHG-059 链接 `CHG-20260923-059/change.md` → `../../completed/CHG-20260923-059/change.md`——**关闭 CHG-057 归档时登记的那条待办**（原文：「等它自己关闭时按本次这套做法处置」） | +1/−1 |
| `.ai/CURRENT_CONTEXT.md` | 由 `scripts/prepare_ai_workspace.py --no-active` 重生成（**不手改**），2144 → 1668 字符 | +17/−17 |
| 本 CHG 自己的记录 | `change.md`（§6 D-26/D-27、§7 Q-07/Q-08、§8 T-10 → DONE、AC-01/AC-11、§9/§10/§11/§12/§13）、`checkpoint.md`、`status/{workspace,agent,desktop}.md` 末尾「关闭时的终态」 | +293 |

`docs/` 根下那份**遗留副本区**未动（root `docs/` 不是新实现决策的来源）；
`.ai/CURRENT_CONTEXT.md` 在**执行根父层没有副本**（治理硬约束）。

## 3. D-08 的落点：只改注释，判据是「解析后相同」

`wt-media-agent/config_online/agent.toml:17-21` 与 `config_online/README.md` 里那段
「still open … Resolve before release」是 Q-01 关闭（2026-09-25）之后的**过期陈述**。改写为
「已裁定：保持回环」。

**先红**：新写的 `tests/test_config_shipping.py::test_the_shipped_configuration_claims_no_open_question`
在改注释之前逐条点名——把 `config_online` 侧改动 `git stash` 掉，同一过滤器下红得正是这四条：

```
README.md:15 states 'still open'
README.md:15 states 'undecided'
agent.toml:18 states 'still open'
agent.toml:21 states 'resolve before release'
```

**判据不是「逐行相同」而是「解析后的文档相同」**：`tomllib` 解析前后**叶子 12 条全等**；
阳性对照（把 `base_url` 改一个字符再比）同一条比对报 **False**，证明这个等式抓得住值的变化。
改动后同一过滤器 `Ran 12 tests … OK`、exit=0。

**扫描的是措辞不是问题号**——Q-01 被回答了，「Q-01」这三个字本身不再有害；
出货包里不该有的是**「还没定」这个断言**。所以标记集合是
`("still open", "undecided", "unresolved", "resolve before release")`，不是问题号清单。
转录：`evidence/task-10-config-claims.out`（含 §3b 一条订正：首轮 `tail -3` 抓到的是测试自己的
stdout 而不是摘要行，补记了真实的 `Ran 12 tests / OK / exit=0`，没有回头改写）。

## 4. 档案两遍扫描

完整输出：`evidence/task-10-archive-scan.out`。移动提交 `54c87b2`（66 文件 100% rename，
**0 insertions / 0 deletions**）。

### 4.1 第一遍：字符串扫描

分母 = 工作区被跟踪文件 **673** 个。两条模式：

| 模式 | 命中文件数 |
|---|---|
| `delivery/active/CHG-20260923-059` | **0** |
| `active/CHG-20260923-059` | **0** |

**阳性对照**（同两条模式打在移动之前的提交 `54c87b2^` 上）：分别命中 **2** 与 **5** 个文件
（`.ai/CURRENT_CONTEXT.md`、`delivery/LEDGER.md`、里程碑、`planned/README.md`、程序总纲）。
⇒ 这条扫描是有分母、有阳性对照的「0 命中」，不是空转。

**一次诚实的过程记录**：第一遍曾命中 **1 处**，是**本节自己的草稿**——写「0 命中」的那句话里
把旧路径抄了一遍。这正好说明这条扫描抓得住真东西；改掉草稿后重测才是上面的 0。

**回测（提交之后再跑一次同一对模式，如实登记）**：分母变成 **683** 个被跟踪文件
（+10 = 本次新增的 10 份 T-10 证据），命中 **2 个文件**——
`evidence/task-10-archive-scan.out` 与**本文件**。两处都是同一件事：**这份扫描自己的转录与说明里
必须把旧路径的字面量引出来**（转录是脚本回显的模式串，本文件是 §4.1 的那张表）。
⇒ 命中全部落在「记录这次扫描的东西」内部，**没有一处是活的指针**；
「旧落点还在被当路径用」这个判据由第二遍（链接 resolve，新弄坏 0 条）承担，
字符串这一遍的证据是「**除自身记录之外 0 命中**」。
这正是先例里那条自我指涉的老问题：**别让扫描证据自己变成扫描对象**——所以口径写明，不是把数字改成 0。

口径说明：`delivery/active/` 作为**目录约定**仍在 59 个文件里出现（`AGENT-INDEX.md`、skills、
`MASTER_PLAN` 等）。那不是要清的东西——要清的是 CHG-059 这个**具体落点**，不是「active 这个词」。

### 4.2 第二遍：链接 resolve（前后差集）

对着 `54c87b2^` 的副本做**逐链接 resolve**，再与工作区做差集：

```
工作区：    423 个 md / 110 条相对链接，坏链 5
归档前副本：423 个 md / 103 条相对链接，坏链 9

移动【新弄坏】的链接： 0          ← 这是这条扫描要的判据
移动【弄好】的链接：   4
  FIXED  delivery/active/CHG-20260923-059/change.md -> ../completed/CHG-20260923-056/change.md
  FIXED  delivery/active/CHG-20260923-059/change.md -> ../completed/CHG-20260923-057/change.md
  FIXED  delivery/active/CHG-20260923-059/change.md -> ../completed/CHG-20260923-058/change.md
  FIXED  delivery/planned/CHG-20260923-053/change.md -> CHG-20260923-059/change.md
两次都坏（既存）：     5
```

四条 FIXED 里前三条是**同一件事的两面**：`change.md` 里写给上游 CHG 的 `../completed/X` 在
`active/` 下是对的（`active/` 与 `completed/` 是兄弟），搬到 `completed/` 之后就该是 `../X`
——按 CHG-058 归档时立下的先例订正。第四条正是 CHG-057 归档时**点名登记、特意留给这一刻**的链接。

**这个数订正过一次，如实记下来**：先前在本节的草稿与 CHG 记录里写的是「弄好 5 条」。
重测（`54c87b2^` 副本坏链 **9** → 工作区坏链 **5**，且**新弄坏 0**）⇒ 差集只能是 **4**
（9 = 4 修好 + 5 既存）。差 1 的来源是早先一次口径不同的比对（对照落在 `HEAD` 而不是 `54c87b2^`，
那次比的是「回写前 vs 回写后」而不是「移动前 vs 移动后」，两次比的东西不是同一件）。
`change.md` 的 T-10 行与 §12、`checkpoint.md`、`status/workspace.md` 已一并改为 **4**；
本文件 §4.2 与 `evidence/task-10-archive-scan.out` 的转录是这条数的**唯一依据**。

剩下 5 条坏链**两次都坏**（既存，不是本次造成），按 **Q-08** 登记不改：

- CHG-052 证据里 3 条指向 `../wt-media-cloud/…` 的链接**少一层 `../`**（目标文件真实存在）；
- CHG-057 / CHG-058 归档证据里各 1 条——它们**写在反引号内的历史叙述里**，
  是「当时用过的路径」这件数据，不是活指针（路径判修、叙述判留）。

**扫描局限（要连同数字一起读）**：正则不区分代码跨度与正文，所以**引号内引用的历史坏链会被算成坏链**
——上面 5 条里 2 条如此。这条局限只影响那 5 条的**分类**，不影响「新弄坏 0 条」这个判据。

## 5. 关闭门禁的同集合阳性对照

判据不是「这 4 条红看着与我们无关」，而是**它们在归档之前的树上就已经是这 4 条**。

对照副本 = `git archive 54c87b2 | tar -x -C ../.t10-control`（**落点在 `wt-media/` 之内**）。
落点这一条是承重的：放在 `/tmp` 里，站在 `../wt-media-cloud` 上的用例会因兄弟仓不存在而
**静默 skipTest**，把「4 条红」读成「2 条红」——而缩水本身不报错（CHG-057 就是这么读错的）。

```
控制树独有 = ∅
工作区独有 = ∅
同集合 = True （两边各 4 条）
```

四条逐条同名：`test_contract_map_matches_m1_cloud_agent_compatibility`、
`test_contract_map_provider_paths_exist_in_full_workspace`（两条 `test_verify_m0_config`）、
`test_static_cross_repo_contract_and_security_matrix`（`test_verify_m2_acceptance`）、
`test_current_product_master_and_governance_are_aligned`（`test_verify_product_master_alignment`）。

**兄弟仓可见性对照**：控制树里那两条站在 `../wt-media-cloud` 上的用例**确实红了**——
这证明控制树的兄弟仓是解析得到的，对照不空转。转录：`evidence/task-10-gate-green.out` 末尾。

对照副本用完即删（`.t10-control`、`.t10-control-pre` 两个目录都不在了）。

## 6. 一条既存间歇红：如实登记，不粉饰（D-27／Q-07）

关闭门禁跑 agent 套件时暴露出 `tests/test_sidecar_entry.py::SigtermTests::
test_a_request_in_flight_when_the_signal_arrives_is_waited_for` 会间歇失败。
**先在未改动的原树上量**（`git stash` 掉本 CHG 的 agent 侧改动）：20 次里失败 **1** 次
⇒ 与 T-10 的改动无关，是既存间歇红。

**机制是假设，不是结论**：候选解释是「信号可能赶在连接被 accept、其处理线程登记之前到达」。
判别实验用一次性的探针（`tests/zz_t10_race_probe.py`，**不提交、用完即删**）扫 `PROBE_WAIT`
这个旋钮：不等 → 2/15，等 0.3s → 0/15，40 次重跑 A 臂 2/40。方向与假设一致，但
**两臂的差别不足以判显著**，故**不写「已定位」**。

按本 CHG 自己的规矩**不修**：加一个 `sleep` 正好是「凭一次跑通接受显然的一行修法」，
会把这个窗口从视野里藏起来。处置方向记为 **Q-07（未裁定）**：修测试还是修实现。
完整量测见 `evidence/task-10-flake.md` 与 `evidence/task-10-flake.out`。

**这条影响一个措辞**：agent 计数写「**407 tests OK**」，但「agent 套件每次全绿」这句话
在 Q-07 关闭之前**不成立**——LEDGER 与 AC-11 都照这个口径写。

## 7. 提交边界

| 提交 | 内容 | 形态 |
|---|---|---|
| `54c87b2` | `git mv delivery/active/CHG-20260923-059 delivery/completed/…` | **纯移动**：66 文件、100% rename、**0 insertions / 0 deletions** |
| 待提交（workspace） | 本文件、其余 `task-10-*.out`、§2 表里除本 CHG 记录之外的全部落点 + 本 CHG 自己的记录 + 重生成的快照 | 回写与记录 |
| 待提交（agent） | `config_online/agent.toml`、`config_online/README.md`、`tests/test_config_shipping.py` | D-08 的落点 |

「移动文件」与「改逻辑」**不在同一个 commit** 里；一仓一 commit。

## 8. 一条如实登记的观察：受保护脏文件里的一个尾换行

工作区里有 6 个**与本 CHG 无关、且本 CHG 不得触碰**的脏文件（`AGENT-INDEX.md`、`AGENTS.md`、
`CLAUDE.md`、`README.md`、`docs/engineering/specs/2026-09-24-m4-m5-cloud-content-production.md`、
`docs/engineering/specs/agent-workspace-conventions.md`）。逐条核过 mtime：其中 5 个停在 2026-09-24／
09-25 00:44，**只有** `2026-09-24-m4-m5-cloud-content-production.md` 的 mtime 落在本 CHG 的工作窗口里
（2026-09-25 09:10），而它的 diff 是**一个纯尾换行**（`+` 一行空白，292 行文件的末尾）。

**如实登记，不擅自处置**：①我没有对它做过有意的写入，也拿不出「就是它被谁写的」的证据；
②它是**本 CHG 不得触碰**的文件，所以既不提交、也不还原——还原同样是一次写入动作；
③它对本次回写与关闭判据**没有任何影响**（不在任何判据的输入里）。
记在这里是为了让下一个读 diff 的人不必怀疑是不是回写漏了这一处。

## 9. 边界：这份证据证不到什么

- 字符串扫描证的是**字面量**，证不到「语义上仍在把读者指向 `active/`」这种**没写全路径**的说法
  （那类只能靠第二遍 resolve 与人工阅读）。
- 链接 resolve 用的是正则，**会把代码跨度内的历史叙述算成坏链**（§4.2 已逐条标注）。
- 同集合对照证的是**失败名单相同**，证不到这 4 条红的**成因**在归档前后也相同——
  成因分析在 CHG-056/057/058 各自的记录里，本 CHG 未重做。
- **干净机安装**（D-09）与**随包 onefile sidecar 的引导器是否转发 SIGTERM**（T-03）**未做**，
  因此「发布验证通过」这句话在 D-09 关掉之前**不宣布**。
