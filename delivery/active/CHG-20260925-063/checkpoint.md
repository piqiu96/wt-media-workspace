# Checkpoint — CHG-20260925-063

- 状态：IMPLEMENTING（2026-09-25 激活）。
- 性质：处置三个常年红的校验脚本（僵尸门禁），按判据稳定性分层——跨仓源码字面量与
  已关闭里程碑的候选关键词不再作门禁，契约层判据保留并加固。Level S，仅 `wt-media-workspace` 一仓。
- 来源：本次会话 `/doctor` 诊断的 B-7（僵尸门禁）与 G-1，经用户 2026-09-25 裁定
  「按稳定性分层」+「删掉 CI 断言」后立此 CHG。

## Completed

- 2026-09-25 Start Gate 勘查（只读，无任何写入）：三个脚本实跑读数 exit 1，
  红项 **3 / 5 / 8** 条；16 条逐条追到具体行与具体文件（`change.md` §4）。
  工作区开工时只有 2 个已知脏文件（`CLAUDE.md`、`docs/engineering/specs/agent-workspace-conventions.md`，
  均为上一任务的工作区编辑，非本 CHG 产物，开工前已核实归属）。
- 2026-09-25 两项实测发现（均为本轮新查、非推断）：
  1. **M3 的禁用对象检查今天恒真**——`candidate_block(sections[3])` 返回空串，
     而 `crawl_result` 实际出现在 M3 段正文里；照 M2 补兜底会把它从恒真翻成恒假。
  2. **测试套件里有一处假通过**——`test_rejects_stale_operational_object_in_candidate_chg`
     的变异字符串 `M3-C6 source_content 全局去重、状态和最新原始 JSON` 在 MASTER 中
     **不存在**，`str.replace` 是空操作，该用例从未验证过禁用对象机制。
- 2026-09-25 T-01：建 `delivery/active/CHG-20260925-063/`（`change.md` 十四节、本 `checkpoint.md`、
  `evidence/artifacts/`）。单仓实施，**不建** `status/`。

## Completed

- 2026-09-25 Start Gate 收尾：LEDGER 加表行、快照经 `prepare_ai_workspace.py --change` 再生成
  （`active_milestone=null`，Level S 预期）。`verify_delivery_governance.py` / `verify_agent_entry.py` /
  `verify_skills.py` 三者 exit 0。**形状限制导致一处记录改动**：`verify_product_master_alignment.py`
  要求 active CHG 的 §7 为字面 `None.`（不接受「非阻塞」档位），故原拟的 Q-01 移入 §14 遗留第 1 项。
- 2026-09-25 T-01 完成：`verify_m0_config.py` 由 `exit=1`／3 红 转为 `exit=0`，
  `tests.test_verify_m0_config` **Ran 4 tests / OK**。两次**变异对照**（改坏 contract-map 的
  `cloud_api` revision → 报错；空 `OUTER_ROOT` → 三个运行仓工作流 3/3 报缺）证明未改成恒真、
  亦未使 CI 检查器整体失去判别力。**纠正一处自我错误**：首轮基线用 `PY="…"` 变量拼接，
  zsh 不做词分割致三个产物只含 `exit=127`，已用 shell 函数重跑替换（靠 `exit=` 码与体量交叉核对发现）。
  证据：`evidence/task-01-m0-config.md`。
- 2026-09-25 T-02 完成：`verify_m2_acceptance.py` 由 `exit=1`／5 红 转为 `exit=0`，
  `tests.test_verify_m2_acceptance` **Ran 1 test / OK**。**D-01/D-02 的张力经测量解开**——
  真正的强制点在 Cloud，且行为覆盖已在 Cloud 自己的
  `TestRegisterConsumesTicketOnceAndIssuesHashedCredential`；本仓改断**已应用 migration 的 schema**
  （append-only ⇒ 文本冻结，故满足稳定性分层）。**三条自我纠正**（同源：判据自己写错时输出照样「像量过的」）：
  ①首版变异对照**没有重定向 `m.CLOUD`**，三条变异全报 0 error，是空转；
  ②AC-04 用 `grep -c` 不具判别力（被删字符串出现在我写的删除说明注释里），改 **AST 枚举**
  证明 **9 个被删 needle 中 0 个仍在断言集合内**；③AC-05 首版判据把路径当 needle 找，误报 3 个 MISSING，
  修正后六类契约层目标全部 present。证据：`evidence/task-02-m2-acceptance.md`。
- 2026-09-25 T-03 完成：`verify_product_master_alignment.py` 由 `exit=1`／8 红 转为 `exit=0`，
  六个门禁全部 `exit=0`。按 D-04 分层：M2/M3 状态词对齐，**M3 的两组候选块断言整组删除**
  （4 条 needle 恒缺 ⇒ 每次必报红；禁用循环 `forbidden in ""` 恒假 ⇒ 静默通过——**两组覆盖都是零**），
  新增「非 `DONE` 里程碑必须带候选块」的**结构错误**把第二种沉默变响。**三条 needle 的根因各自落到决策**：
  M2 的「五条」编码的是 **M2-D 暂缓（2026-09-12 已记录）之前**的计划；M10 的「分发」编码的是
  **ADR-0015** 时代口径，而已被 **ADR-0017 第 1、10 条**取代（FFmpeg 属 Cloud 部署组件）。
  **变异对照 7 臂**（两条对照先行：空文本证明函数读的是传入文本、未变异文本 0 错证明基线干净），
  每臂产出恰好其预期错误集；**6 个被删 needle 经 AST 证明 0 个仍在断言集合内**。
  **一处预期写错并纠正**：M2 状态变异实得 2 条错而非 1 条——重开已关闭里程碑**同时**触发新增的
  缺块检查，这是该检查的意图，是预期写窄了。证据：`evidence/task-03-product-master-alignment.md`。
- 2026-09-25 T-03 副产物：查明 §4.4 那条假通过用例**绿的原因也是空转**，并实测证明——
  用 `HEAD` 版脚本对**未变异**文本求值已产出 4 条 `M3 candidate missing …`，而该用例断言的正是
  「存在该标签」，故**在变异之前就成立**。两个错互相掩盖。因此 T-04 **不能只换变异字符串**。
  证据：`evidence/artifacts/t03-false-pass-proof.out`。
- 2026-09-25 T-04 完成：`tests/test_verify_product_master_alignment.py` 5 条 → **7 条全绿**，
  整套 unittest **Ran 75 / OK**（连跑两次一致）。断言判定由「**有某标签**」改为
  「**完整错误集合逐条相等**」——标签式断言可被同族任何错误满足，故会在它命名的判据坏掉时仍绿。
  新增 `mutate()`：先 `assertIn` 再 `assertNotEqual`，正对病根（目标不存在时 `replace` 是静默空操作）。
  **变异对照 5 臂**，其中**决定性一臂**：把**旧脚本**的 M3 禁用判定整条关掉后，
  **旧用例依然通过** ⇒ 它**无法检测它所命名的那条检查被删除**。禁用对象用例重定目标到
  **M8/M9**（均 `NOT_STARTED` 且有非空块），并新增「清空 M9 块」用例把三族检查的不对称钉死。
  证据：`evidence/task-04-tests.md`。

- 2026-09-25 T-05 完成（提交 `3204f91`）：三处文档与实测对齐——`README.md` §Verification 由 4 项补为
  **6 个静态门禁 + unittest** 并**删掉「Known open failures」整段**（附显式禁令；该段的红项与清单本身互相矛盾：
  清单只列 4 个脚本却在下一段讨论另外两个）；`conventions §10` 由「校验与已知红项」改写为
  **实测绿表 + 四条硬约束**（判据稳定性分层、候选块属于未关闭里程碑、"报通过/0 命中前先证明检查能失败"、
  已知 WARN 含一条结构性空转的如实登记）；`AGENT-INDEX.md` §12 由只列一个脚本改为**列全校验命令**、
  并声明 `conventions §10` 为**校验状态的唯一落点**——**关闭 CHG-062 遗留第 2 项**（原先真正约束 CHG 的
  `verify_delivery_governance.py` 根本没被列出）。
  **两遍引用扫描**：字符串扫描 0 条现行断言（阳性对照：同模式在该文件另有 4 处命中）；相对引用 resolve
  46 条 link 形态**全通、0 条指不到**（阳性对照：喂一个不存在的路径，解析器报 `False`）；另 264 条散名 /
  兄弟仓路径 / 命令按形态排除。**一处自我纠正**（同类错第五次）：首版分类器把 27 个散文用名误判为链接并
  全报 MISS，改为按「首段是否为仓内顶层目录」判定。**并纠正一处既有诊断**：先前说该臂恒空的成因是
  「红线路径全带扩展名」——实测 `AGENT-INDEX.md` 17 个 path token 里 10 个**可以**通过点号规则，结论不变
  而机制不同（真正原因是 `check_entry_drift` **只读 `AGENTS.md`**，不读 `AGENT-INDEX.md`）；`change.md` §14
  第 2 项已按新机制改写并附更正说明。
  **不提交他人工作区改动**：该文件开工前已有一处 `/doctor` 编辑（第 33 行），处置为「临时还原为 HEAD 文本 →
  确认 diff 只剩本任务改动 → 提交 → 改回」，核对读数：提交前 `git diff --stat` = `2 +-`；`git show HEAD:<file>`
  该模式计数 = 2（原有行 `:11`、`:32`），恢复后工作区 = 3 ⇒ 未进入任何提交。证据：`evidence/task-05-docs.md`。

## Current

- T-06 收尾：AC-12 复测、AC-01…AC-14 终态、DONE Gate 签字、归档与两遍失效指针扫描。

## Next

- T-06 收尾（`evidence/task-06-close.md`）：
  1. 在**本 CHG 最后一次改动之后**重跑六个门禁 + 整套 unittest，取关闭值（不能沿用 T-05 读数）；
  2. `git -C ../wt-media-{cloud,agent,desktop} status --porcelain` 复测 AC-12；`config/release-matrix.yaml`
     复测 AC-14 零改动；逐条给 AC-01…AC-14 终态；
  3. §13 DONE Gate 逐条签字、§9 Repository Checklist 勾选；
  4. `delivery/active/` → `completed/` 归档，同步 `LEDGER.md`；
  5. 归档后**两遍**失效指针扫描（字符串扫描 + 相对链接从**引用者自身目录** resolve），并做阳性对照。

## Blockers

- None。（Q-01 已标 NON-blocking。）

## Recent verification

- 见 `change.md` §4 与 `evidence/artifacts/`：三个脚本的原始红项输出、逐里程碑状态与候选块实测表、
  三处测试变异字符串的存在性探针。
