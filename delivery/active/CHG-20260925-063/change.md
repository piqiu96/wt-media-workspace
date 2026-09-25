# CHG-20260925-063: 三个校验脚本的僵尸门禁处置——按判据稳定性分层

## 1. Basic Information

- Level: S
- Status: IMPLEMENTING
- Created: 2026-09-25
- Current repository: `wt-media-workspace`
- Affected repositories:
  - `wt-media-workspace`
- 锚点（Level S，按 CHG-20260924-060 §3 与 CHG-20260925-062 §3 先例写散文，不引 Milestone）：本 CHG 处置的是治理仓自身的校验脚本卫生，**不挂任何 Milestone**——`delivery/milestones/` 下 6 篇没有一篇覆盖门禁/校验卫生（已实测 grep 零命中）。`verify_delivery_governance.py` 只对 `Level: M/L` 强制 `- Milestone:`。

三个运行仓（cloud / agent / desktop）**只被读、不被写**：`verify_m2_acceptance.py` 会读它们的文件与契约，本 CHG 不修改它们任何一个。

## 2. Change Goal

把 `scripts/verify_m0_config.py`、`scripts/verify_m2_acceptance.py`、`scripts/verify_product_master_alignment.py` 三个常年红的校验脚本**按判据的稳定性重新分层**，使其**全绿**，且同类红不再长出来：

- 跨仓**源码字面量**断言（别的仓一次合法重构就会使它过期）与**已关闭里程碑的候选关键词**断言，不再作为门禁判据；
- 保留并加固**契约层**判据（contract-map、release-matrix、migrations、契约 yaml、desktop `contracts.lock.json` 的 consumes 映射、禁止持久化密钥标记）；
- 把本轮实测出的**两处静默空转**变成**会失败的检查**，使「检查自己过期」这件事下次自己暴露，而不是安静地留在绿里。

## 3. Baseline References

- 权威源：`AGENT-INDEX.md` §8 交付治理、§12 校验
- 工程规范：`docs/engineering/specs/agent-workspace-conventions.md` §10 校验与已知红项
- 配置：`config/contract-map.yaml`、`config/release-matrix.yaml`
- 产品计划：`delivery/MASTER_IMPLEMENTATION_PLAN.md`
- 诊断来源：本次会话的 `/doctor` 报告 B-7（僵尸门禁）与 G-1/G-10

## 4. Current Facts

全部为 2026-09-25 实测，逐条命令与原始输出见 §11 与 `evidence/`。

### 4.1 三个脚本的红项构成

| 脚本 | exit | 红项 |
|---|---|---|
| `verify_m0_config.py` | 1 | 3 条：`cloud_api` / `local_agent_api` 的 `contract_revision` 期望值过期 ×2；`wt-media-workspace/.github/workflows/m0-workspace.yml` 缺失 ×1 |
| `verify_m2_acceptance.py` | 1 | 5 条：跨仓源码字面量 5 条（见 4.2） |
| `verify_product_master_alignment.py` | 1 | 8 条：M2/M3 状态词 ×2、M2/M3 关键词 ×5、M10 关键词 ×1 |

### 4.2 `verify_m2_acceptance.py` 的 5 条红项逐条根因

| # | 行 | 断言 | 实测现状 | 性质 |
|---|---|---|---|---|
| 1 | `:71` | `cloud/internal/modules/cloudagent/compatibility.go` 存在且含 2 个字面量 | 文件已移到 `.../cloudagent/service/compatibility.go`，两个字面量都在 `:12-13` | 落点搬家 |
| 2 | `:86` | agent `src/wt_media_agent/cloud_agent_contract.py` 含字面量 `REQUIRED_CONTRACT_REVISION = "2026.07.15.1"` | **值没变、常量还在**，但定义搬到 `clients/cloud/contract.py:11`，原文件只剩 import 与 `__all__` 再导出 | 落点搬家 |
| 3 | `:113` | desktop `main.rs` 含 `"wt-media-agent"` | 另两个 needle（`local_agent_start`、`local_agent_status`）各仍有 1 命中；该字符串现在只出现在 `sidecar/integrity.rs:69,75` | 落点搬家 |
| 4 | `:120` | desktop `local_agent/mod.rs` 含 `fn consume_binding_ticket(` | **该符号在全仓不存在**。但**语义没有消失**：票据单次使用现由 Cloud 原子强制，`internal/modules/runtimebinding/repository/store_mysql.go:49` 的 `UPDATE local_agent_binding_tickets SET used_at = ? WHERE id = ? AND used_at IS NULL` | **机制跨仓迁移** |
| 5 | `:121` | desktop `local_agent/mod.rs` 含 `pub fn bind_session<T: BindingTransport>(` | 泛型传输抽象已被 CHG-056 的分层重构取代，现为 `commands/bind.rs:38` 的 `#[tauri::command] pub async fn local_agent_bind_session`（具体 `CloudClient`，无泛型） | 落点搬家 |

第 4 条与前四条**不同类**：前四条是「位置搬了、值没变」，第 4 条是「**强制点换了个仓**」。因此它的处置不是改指针，而是**把断言改指真正的强制点**（见 D-02）。

### 4.3 `verify_product_master_alignment.py` 的根因：候选块在关闭时被移除，而检查假设它永远在

逐里程碑实测（状态词取自 MASTER 各段 `| 状态 |` 行，候选块取自 `candidate_block()`）：

| 里程碑 | 状态 | 候选 CHG 块 |
|---|---|---|
| M0 | `DONE` | 267 字符 |
| M1 | `DONE` | 320 字符 |
| **M2** | `DONE` | **0（无块）** |
| **M3** | `DONE` | **0（无块）** |
| M4–M10 | `NOT_STARTED` | 120–400 字符，全部有块 |

即：**M2、M3 在转为 `DONE` 时其候选 CHG 块被移除**（由阶段表/闭环叙述取代），而 M0、M1 是更早关闭的，块还留着——移除候选块是**较新且应用得并不一致**的做法。校验脚本写于 M2/M3 仍然开着的时候，它默认「候选块永远在」。

由此产生**两处静默空转**（这是本 CHG 要根治的部分，不只把值改新）：

1. **`candidate_block()` 返回空串时不报错**。`require_all("", needles, …)` 于是变成**恒假**（needle 永远缺失），而 `forbidden in ""` 变成**恒真**（永远不触发）。同一个空串，两类断言一个永远红、一个永远绿，脚本却对「块没了」这件事一言不发。
2. **M3 的禁用对象检查今天恒真**。M3 是唯一**既无候选块、也无 `or sections[3]` 兜底**的段（M2 无块但有兜底）。实测 `crawl_result` 确实出现在 M3 段正文中，因此若照 M2 的样子补上兜底，该检查会从**恒真翻成恒假**——红项从 4 变 5。**任何「顺手把兜底补上」的改法都会踩这个坑。**

### 4.4 测试套件里的一处假通过（本轮实测发现）

`tests/test_verify_product_master_alignment.py::test_rejects_stale_operational_object_in_candidate_chg` 是一个**假通过**：

- 它把 `M3-C6 source_content 全局去重、状态和最新原始 JSON` 替换成 `M3-C6 crawl_result 和 content_lead 入库`，然后断言出现 `"M3 candidate"` 错误。
- 实测该**被替换的字符串在 MASTER 里根本不存在**（`False`），`str.replace` 是**空操作**，所谓「变异后的文本」与原文逐字相同。
- 于是它断言的 `"M3 candidate"` 错误来自**另外 4 条**（候选块为空导致的 needle 缺失），**与它想测的禁用对象机制毫无关系**。
- 结论：**这条测试从未验证过禁用对象检查**，该检查即便被整个删掉它也照样绿。

同类问题：`test_rejects_missing_m2_product_capability` 的变异字符串**存在**、机制**真的被跑到**，该测试有效；但它的有效性依赖 M2 的 `or sections[2]` 兜底，而这个兜底正是为 M2 无块打的补丁（见 4.3 第 2 条）。

### 4.5 门禁与治理权威直接矛盾（1 处）

`verify_m0_config.py:267-273` 要求存在 `wt-media-workspace/.github/workflows/m0-workspace.yml`。实测该仓**没有 `.github/` 目录**，而三个运行仓都有 CI（`m0-cloud.yml` / `m0-agent.yml` / `m0-desktop.yml`）。

治理权威两处写明这是**有意为之**：`AGENT-INDEX.md` §12「本地手工执行，本仓库当前不设 CI」；`agent-workspace-conventions.md` §10「本仓库当前**不设 CI**（`.github/workflows/` 已移除）」。**门禁与权威源矛盾，权威源为准。**

由此暴露一个结构成因、本 CHG 只登记不改（见 §14）：**该仓不设 CI ⇒ 这些门禁只在有人手工跑时才会被发现已经红**，这正是它们长成僵尸的机制。

### 4.6 同类问题在本仓有先例，且红项被文档化后就固定不动

`delivery/completed/CHG-20260721-020/evidence/start-gate.md:12-13` 记录同一类失败：`verify_m2_acceptance.py`「Script crashed reading removed `wt-media-desktop/src/services/local-agent.js`」、「Script reported obsolete M1/M2 status and candidate assertions」——**2026-07-21 就已经因「检查读到已删除的文件」「报过时的状态」红过一次**。

`README.md:77-81` 把三个脚本的既知红项写成「Known open failures」段落。即：**红项一旦被文档化，就被就地固定了下来**——这正是本次要拆掉的东西。

## 5. Scope

### Add

- `scripts/verify_m2_acceptance.py`：新增一条**契约层**断言，校验 binding ticket 单次使用的真实强制点（Cloud 侧原子 `UPDATE … WHERE used_at IS NULL`）。
- `scripts/verify_product_master_alignment.py`：新增一条**结构断言**——未关闭（非 `DONE`）的里程碑**必须**有候选 CHG 块，否则报错。
- `tests/test_verify_product_master_alignment.py`：新增用例覆盖上述结构断言；并修正 4.4 的假通过用例。

### Modify

- `scripts/verify_m0_config.py`：两条 revision 期望值对齐 `config/contract-map.yaml`；移除 workspace CI 断言。
- `scripts/verify_m2_acceptance.py`：移除跨仓源码字面量断言，保留全部契约层断言。
- `scripts/verify_product_master_alignment.py`：`expected_statuses` 对齐现状；候选块断言改为**按里程碑状态分层**；消除 4.3 的两处空转。
- `README.md` §Verification：删掉「Known open failures」段落。
- `docs/engineering/specs/agent-workspace-conventions.md` §10：按实测重写校验表（三个脚本转绿）。
- `AGENT-INDEX.md` §12：补列该节漏掉的校验脚本。

### Delete

- `scripts/verify_m2_acceptance.py` 中 3 处跨仓源码字面量断言（`:69-73`、`:83-87`、`:110-123`）。
- `scripts/verify_product_master_alignment.py` 中 M3 的候选块断言（needles ×4 与禁用对象检查）——M3 已 `DONE` 且无候选块，这些断言无处可指。

### Explicitly Not Doing

- **不修改三个运行仓的任何文件**。第 4 条红项指向的 Cloud 原子 SQL 是被**读取**的对象，不是被修改的对象。
- **不新建 workspace CI**（`AGENT-INDEX.md` §12 已裁定不设）。
- **不修改 `config/release-matrix.yaml`**。该文件的 `verification:` 块是**历史发布记录**（文件头 `planning_note` 自述「Verified releases are historical scope evidence」），改动它等于改写历史。
- **不处理 G-9 的权威冲突**（ADR-0015/0017 的 FFmpeg 归属、读取顺序两版、`milestones/README.md` 的 M3 状态等 8 条）——需独立 CHG。
- **不修 `verify_agent_entry.py` 的 workspace 臂空转**（G-10）——需独立 CHG；本 CHG 只处理与本三个脚本相关的空转。

## 6. Confirmed Decisions

| ID | Decision | Status |
|---|---|---|
| D-01 | 判据按**稳定性分层**：跨仓源码字面量与已关闭里程碑的候选关键词不再作为门禁；契约层判据保留并加固。用户 2026-09-25 裁定。 | CONFIRMED |
| D-02 | `verify_m2_acceptance.py` 第 4 条红项**不是改指针**：binding ticket 单次使用的强制点已迁到 Cloud，断言改指该处真实强制点，把死断言换成活断言。 | CONFIRMED |
| D-03 | `verify_m0_config.py` 的 workspace CI 断言**删除**，与 `AGENT-INDEX.md` §12 一致；三个运行仓的 CI 断言保留。用户 2026-09-25 裁定。 | CONFIRMED |
| D-04 | 已 `DONE` 里程碑在 `verify_product_master_alignment.py` 中**只校验状态词**；其既有的「闭环记录」级断言（M0/M1 门禁措辞、M2 能力清单）**保留**——它们记录的是「当时凭什么算关闭」，属稳定历史，不是候选清单。 | CONFIRMED |
| D-05 | 删掉的是**常年红的覆盖**而非有效覆盖：第 4.2 节 5 条今天全部为红，其覆盖早已为零。此点须在证据中逐条留痕，不得含糊。 | CONFIRMED |
| D-06 | 本 CHG 取 **Level S、不引 Milestone、不立 ADR**。层级理由同 `CHG-20260924-060` D-05 与 `CHG-20260925-062` D-03：纯治理仓改动、不挂 Milestone。**必须开 CHG 而非直接小改**的理由：`AGENT-INDEX.md` §8 的「小修改」明确限于「文档修正、小 Bug、**不影响行为**的重构」，而本 CHG **改变三个门禁的判据集合**（既有删除也有新增），影响行为，故不在小修改之列。另：删除类改动即使分级为 S，其**逐条删除清单**仍须在证据中落痕（由 AC-04 强制）。 | CONFIRMED |

## 7. Pending Questions

None.

（原拟在此登记的 Q-01「是否引入非 CI 的强制点」已移入 §14 遗留第 1 项：它不是本 CHG 的待决问题，
而是本 CHG 明确不处置的后续事项。`verify_product_master_alignment.py` 要求 active CHG 的
本节为字面 `None.`——该检查不接受「非阻塞」这个档位，只要本节存在表格即报错。此形状限制见 §14 第 7 项。）

## 8. Implementation Tasks

| Task | Goal | Status | Verification |
|---|---|---|---|
| T-01 | `verify_m0_config.py` 转绿：两条 revision 期望值对齐 contract-map；移除 workspace CI 断言（D-03） | DONE | 脚本 exit 0；`tests/test_verify_m0_config.py` 4 条全绿；**两次变异对照**（改坏 contract-map 的 revision 必须报错；空 `OUTER_ROOT` 下三个运行仓工作流必须逐条报缺）见 `evidence/task-01-m0-config.md` |
| T-02 | `verify_m2_acceptance.py` 转绿：移除 3 处源码字面量断言，新增 Cloud 原子单次使用断言（D-01/D-02） | TODO | 脚本 exit 0；新增断言做**变异对照**（改坏 SQL 必须报错） |
| T-03 | `verify_product_master_alignment.py` 转绿：状态词对齐、候选块断言按状态分层、消除两处空转、新增未关闭里程碑缺块断言 | TODO | 脚本 exit 0；新断言做**变异对照**（抽掉一个非 DONE 里程碑的候选块必须报错） |
| T-04 | 修正测试套件的假通过与失效用例（4.4） | TODO | 新用例先红后绿；证明变异字符串真实存在 |
| T-05 | 文档同步：README §Verification、conventions §10、`AGENT-INDEX.md` §12 | TODO | 三处读数与实测一致；`verify_agent_entry.py`、`verify_delivery_governance.py` 仍绿 |
| T-06 | 收尾：全套门禁 + unittest 读数、归档指针扫描 | TODO | 见 §10 验收矩阵 |

每个 Task 按 `executing-wt-media-change` 的协议执行：失败验证 → 最小实现 → 测试 → diff 检查 → 证据 → checkpoint → 独立提交。

## 9. Repository Checklist

### wt-media-workspace

- [ ] 三个校验脚本转绿，且新增断言有变异对照留证
- [ ] 测试套件由 73 项 4 红 → 全绿
- [ ] README / conventions §10 / AGENT-INDEX §12 与实测一致

### wt-media-cloud

- [ ] Not affected（只读：`service/compatibility.go`、`runtimebinding/repository/store_mysql.go` 被断言读取，不修改）

### wt-media-agent

- [ ] Not affected（只读：`clients/cloud/contract.py` 被断言读取，不修改）

### wt-media-desktop

- [ ] Not affected（只读：`contracts.lock.json` 被断言读取，不修改）

## 10. Acceptance Matrix

| AC | Requirement | Verification | Status |
|---|---|---|---|
| AC-01 | `verify_m0_config.py` exit 0 | 实跑，原始输出入 evidence | TODO |
| AC-02 | `verify_m2_acceptance.py` exit 0 | 实跑，原始输出入 evidence | TODO |
| AC-03 | `verify_product_master_alignment.py` exit 0 | 实跑，原始输出入 evidence | TODO |
| AC-04 | 跨仓源码字面量断言已移除，且**删除清单逐条留痕** | `git diff` 逐条对照 §4.2 的 5 条 | TODO |
| AC-05 | 契约层判据**未被削弱**：contract-map、release-matrix、migrations、契约 yaml、desktop `contracts.lock.json` consumes、禁止持久化标记六类断言仍在 | 逐类在脚本中定位并在 evidence 中列出行号 | TODO |
| AC-06 | 新增的 Cloud 原子单次使用断言**能失败**（变异对照） | 改坏被测 SQL 字符串 → 必须报错；改回 → 必须 exit 0 | TODO |
| AC-07 | 新增的「未关闭里程碑必须有候选块」断言**能失败**（变异对照） | 抽掉一个非 DONE 里程碑的候选块 → 必须报错 | TODO |
| AC-08 | M3 的禁令检查空转已消除，且**不因补兜底而翻成恒假** | 证明新逻辑下 M3 不跑候选块断言；`crawl_result` 在 M3 段正文中存在这一事实被记录 | TODO |
| AC-09 | 4.4 的假通过用例已修正，且修正后**证明变异字符串真实存在** | 断言替换前后文本不同 | TODO |
| AC-10 | `python3 -m unittest discover -s tests -q` 全绿 | 登记进程数与失败数 | TODO |
| AC-11 | `verify_delivery_governance.py`、`verify_agent_entry.py`、`verify_skills.py` 仍绿 | 实跑三者 | TODO |
| AC-12 | 三个运行仓工作区**零改动** | `git -C ../wt-media-{cloud,agent,desktop} status --porcelain` 与开工前一致 | TODO |
| AC-13 | 文档三处读数与实测一致 | 逐处比对 | TODO |
| AC-14 | `config/release-matrix.yaml` 零改动 | `git diff --stat` 该文件 0 行 | TODO |

## 11. Evidence

证据落在 `evidence/`，记录事实（命令、期望、实际、判定、提交引用），不重复需求。

- `evidence/task-01-m0-config.md`
- `evidence/task-02-m2-acceptance.md`
- `evidence/task-03-master-alignment.md`
- `evidence/task-04-tests.md`
- `evidence/task-05-docs.md`
- `evidence/task-06-close.md`
- `evidence/artifacts/`：各次实跑的原始输出

## 12. Current Checkpoint

Completed:
- 只读勘查与逐条根因定位：三个脚本的 16 条红项全部追到具体行与具体文件（§4）。
- 两处静默空转（`candidate_block` 空串、M3 禁令检查恒真）与一处测试假通过（4.4）经实测确认。
- 两个方向问题由用户裁定（D-01 判据分层、D-03 删 CI 断言）。

Current:
- 记录建立，准备激活并进入 T-01。

Next:
- 激活本 CHG 并写 checkpoint：`python3 scripts/prepare_ai_workspace.py --change CHG-20260925-063`。
- 按 T-01 → T-06 逐个实施。

Blocked:
- None.

Recent verification:
- 三个脚本实跑读数见 §4.1（exit 1 / 3 条、5 条、8 条）；逐里程碑状态与候选块实测见 §4.3。

## 13. DONE Gate

- [ ] Scope completed.
- [ ] No blocking `Q-xx`.
- [ ] Acceptance matrix all PASS.
- [ ] Automated tests passed or justified.
- [ ] Manual verification evidence recorded where required.
- [ ] Diff checked for out-of-scope changes.
- [ ] Runtime repositories touched only if listed in scope.
- [ ] Required baselines updated.
- [ ] Affected repositories committed independently.

## 14. 遗留（只登记，不在本 CHG 处置）

1. **该仓不设 CI ⇒ 门禁只在手工执行时才会被发现已经红**（§4.5，原 Q-01）——僵尸门禁的结构成因。本 CHG 把三个脚本转绿，但**没有**引入任何自动强制点。待决：是否为此引入一个非 CI 的强制点（如 CHG 完成闸门必跑全套、或 pre-commit）。
2. **`verify_agent_entry.py` 的 workspace 臂空转**（G-10，CHG-062 遗留第 1 项）：其正则要求末段不含点号，而该仓红线路径全带扩展名，该臂在唯一需要它的仓里永远为真。**独立 CHG。**
3. **G-9 的 8 条权威冲突**（ADR-0015/0017 的 FFmpeg 归属、读取顺序两版、`milestones/README.md:7` 的 M3 状态与事实相反、`MASTER:54` 的 `delivery/verifying/` 不存在等）。**独立 CHG。**
4. **M0/M1 已 `DONE` 却仍保留候选 CHG 块**（§4.3）：与 M2/M3 的做法不一致。本 CHG 只让校验脚本不再依赖该块的存在，**不改 MASTER 内容**。
5. **CHG-062 遗留第 4 项**（`CLAUDE.md` `## 高频红线` 与 `AGENT-INDEX.md` §2 的局部重复）与**第 8 项**（`LEDGER.md:21` 的「见上表」已不可达）仍未处置。
6. **`README.md:78` 把 `verify_m0_config.py` 的红项描述为「the removed `m0-workspace.yml` workflow」**——本 CHG 会删掉该断言，故该句一并消失；但「红项被文档化后就地固化」这一机制本身（§4.6）没有对策。
7. **`verify_product_master_alignment.py::validate_active_change` 不接受「非阻塞」这个档位**：它要求 active CHG 的 §7 为字面 `None.`，只要该节存在待决问题表格即报错，无论是否阻塞。这使「登记一个非阻塞问题以便日后追溯」在 active 期间做不到，只能放进遗留节（本 CHG 即如此处理）。**本 CHG 不改此检查**——它属记录形状而非本 CHG 的判据分层范围；登记以免后人重提。
