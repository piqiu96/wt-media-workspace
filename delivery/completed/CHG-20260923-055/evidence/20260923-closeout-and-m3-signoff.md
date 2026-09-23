# CHG-20260923-055 关闭记录 与 M3-E3 用户签收

记录时间：2026-09-23
执行：`executing-wt-media-change`（完成闸门）

## 1. 用户裁定（本次关闭的依据）

| 议题 | 用户原话 | 解析 |
| --- | --- | --- |
| 收尾 | 「收尾了，给 M3 优化完成」 | 指示进入收尾 |
| 范围二选一 | 「关 CHG-055 + 记录 M3-E3 签收」 | 归档 CHG-055 为 `DONE`；记录 M3-E3 签收并置 M3 `DONE` |

用户在作出选择前已被明确告知：CHG-054 正文把 **D3 标为「阻塞 = 是（基线 §5）」**，
选此项即表示裁定 D3 不阻塞 M3。故本记录同时是对 D3 的裁定。

签收边界（写明以防被读宽）：**签收的是「M3 验收矩阵结论 + 用户亲眼看到的实机效果」**，
不是「CHG-20260923-054 内全部缺陷已修」。054 的 D1、D2、D3、D6、D7、D8、D9、D10、
D-scheduler-2、S-1 原样保留在 planned。

## 2. 关闭动作与结果

| 动作 | 命令 / 文件 | 预期 | 实际 | 判定 |
| --- | --- | --- | --- | --- |
| 归档 | `git mv delivery/active/CHG-20260923-055 delivery/completed/CHG-20260923-055` | 目录移动，Git 记为 rename | 24 个文件移入新位置；其中 **22 个被 Git 识别为 rename**（5 个因内容同时修改记为 RM），另 2 个见下「未被跟踪的证据文件」。`delivery/active/` 不再含任何 CHG（仅剩 `.gitkeep`） | PASS |

### 未被跟踪的证据文件（既存状态，非本次移动造成）

`evidence/raw/` 下的两个 `proxy-log-*.log`（3 行、4 行）被本仓 `.gitignore` 的 `*.log` 规则忽略
（`git check-ignore -v` 指向 `.gitignore:3`），**从一开始就没有入库**，因此 24 个文件中只有 22 个
以 rename 进入暂存区；它们随目录移动到了新位置，但仍不被跟踪。

- 影响：证据文档引用了这两份日志，而仓库内没有它们的副本，**证据不可持久复现**。
- 敏感值检查（结论为否定，故附阳性对照）：同一正则在已知敏感样本上命中 3 → 检查能失败；
  两个日志的命中数为 0，分母是 3 行与 4 行。即这两个文件只是代理启动输出，不含请求迹与凭据。
- 本轮**不** `git add -f`：是否让证据目录豁免 `*.log` 忽略规则，属仓库级策略，须由独立 CHG 决定；
  本记录只登记事实。
| 状态 | `change.md` 首部 `Status: ACTIVE` → `DONE` | 归档记录不得仍为 ACTIVE | 已改，并补「关闭记录」节 | PASS |
| 台账 | `delivery/LEDGER.md` 移除 055 表行 | 表行数 1 → 0 | 0 行，表下写明「No active M/L CHG」 | PASS |
| 里程碑 | `delivery/milestones/M3-content-discovery-v2.md` | `IN_PROGRESS` → `DONE` | 首部、2.1 表 M3-E3 行、新增 2.2 签收节、第 4 节结论均改 | PASS |
| 主计划 | `delivery/MASTER_IMPLEMENTATION_PLAN.md` | M3 由 `IN_PROGRESS` 改 `DONE` | 总览表行、第 3 节字段块、阶段说明、退出条件标注均已改 | PASS |
| 索引 | `delivery/planned/README.md` | 不再声称 055 为 active | 改为「当前无 active CHG」，055 链接指向 completed | PASS |
| 交叉引用 | `CHG-20260923-054/change.md`、055 的三份 evidence | 不再指向 `active/` | 全仓扫 `active/CHG-20260923-055`：**除本记录自身引用的 2 处外命中 0 处**（分母＝全仓 md/py/sh/json 文件；`node_modules` 已排除） | PASS |

## 3. 顺带补齐的治理工具缺口（本轮的意外发现）

归档 055 后 `delivery/active/` 首次为空。此时发现：

- `scripts/verify_delivery_governance.py` **已经**把「无 active CHG」定义为合法状态
  （`parse_context_change` 把 `none` 归一为 None），`tests/test_verify_delivery_governance.py:94`
  亦有专门用例 `test_no_active_change_is_valid_when_context_and_ledger_are_empty`；
  `scripts/verify_agent_entry.py` 同。
- 但生成器 `scripts/prepare_ai_workspace.py` 只能 `--change <CHG>`，**渲染不出这个状态**；
  而 `AGENT-INDEX.md` 明令快照「Do not edit it by hand」。
- 即：**校验侧承认的状态，生成侧造不出来**。不补就只能手工编辑生成物，属于被禁止的做法。

补法（最小改动）：

- `prepare_ai_workspace.py` 增加 `--no-active`：渲染 `- Active CHG: \`none\``、`- Status: \`NONE\``、
  受影响仓库为 `- None`，不写里程碑与 Change file 行；阅读顺序退化为固定五项。
- 安全阀：`--no-active` 与 `--change` 同时给出 → `ValueError`；
  `--no-active` 而 `delivery/active/` 非空 → `ValueError` 并列出残留 CHG（防止「忘了传 id」被当成「关闭了」）。
- 测试：`tests/test_prepare_ai_workspace.py` 增 3 条，其中
  `test_no_active_change_renders_none_snapshot` 生成后**再调 `verify_delivery_governance` 断言 errors == []**，
  即交叉验证「生成出来的快照确实被校验侧接受」，而不是只断言字符串长相。

### 为什么没有选另一条路

- **不激活下一个 CHG**：`MASTER_IMPLEMENTATION_PLAN.md` 的下一个候选（CHG-20260923-053 Agent 运行时、
  CHG-20260923-054 验收遗留）都需用户先定优先级；054 的 D9/S-1/D-scheduler-2 处置范围本就待用户裁定。
  `.ai/CURRENT_CONTEXT.md` 亦写明「Do not start the next CHG」。故 active 名额留空并回报建议，不自行激活。
- **不手工编辑快照**：那是明令禁止的，且下一次生成即被覆盖，制造隐性漂移。

### M3 验收证据指针失效（关闭时发现并修）

`delivery/active/CHG-20260916-052/...` 自 052 归档（`ceecc20`）起已不存在，但仍有 7 处活引用指向它，
其中**一处是代码**：

| 位置 | 性质 | 处理 |
| --- | --- | --- |
| `scripts/verify_m3_acceptance.py:44`(`EVIDENCE`)、`:403`(`own_artifacts`) | **脚本**，既读旧运行产物（`raw/*.log`）也写新产物 | 改指 `completed/`；附注释说明为何必须改 |
| `docs/product/M3-content-mining-v2.md:13,259` | 产品基线的证据指针 | 改指 `completed/` |
| `docs/decisions/0015-m3-cloud-owned-discovery-execution.md:55` | 决策记录的证据指针 | 改指 `completed/` |
| `delivery/planned/CHG-20260923-054/change.md:5`、`checkpoint.md:5` | 存活 planned 记录的证据指针 | 改指 `completed/` |
| `.../m3-e3-acceptance-20260923/00-run-header.md:5`、`01-freeze-and-preconditions.md:28` | **历史运行记录**，记的是当次运行时的落点 | **不改**——改了就是篡改历史 |

为什么不改不行：`EVIDENCE` 被 `mkdir(parents=True, exist_ok=True)`（`:301`/`:307`）使用，
路径失效后重跑会有两个后果——(a) 在 `delivery/active/` 下**重新造出一个孤儿证据目录**（污染 active 名额），
(b) 读不到旧日志而在 P10 阶段崩掉。修完逐条核对脚本读的 6 个路径（`raw/p10-cloud-test.log`、
`p10-m2-regression.log`、`p10-flowview-grep.txt` 等）**全部存在**，脚本 AST 解析通过。

**登记一处未处理**：同一处 `own_artifacts` 里还列着 `scripts/m3-acceptance.sh`，该文件**不存在**
（对过滤逻辑无害，仅是个空悬标记）；不删，以免把「路径修正」扩大成「验收脚本逻辑重写」。

### 证据工件被 `.gitignore` 的 `*.log` 排除（同一类问题，两处）

第一节登记的 055 `raw/proxy-log-*.log` 并非孤例。同一次核查发现
`delivery/completed/CHG-20260916-052/evidence/m3-e3-acceptance-20260923/raw/` 下**6 个 `.log`**
同样未被跟踪（该目录 `p10-flowview-grep.txt` 等非 `.log` 文件已跟踪）。而
`verify_m3_acceptance.py` 与多份证据文档都要读这些 `.log`。

- 影响：**证据不可持久复现**——`git clone` 出来的仓库缺这些文件，脚本与证据文档会指向不存在的输入。
- 根因：仓库根 `.gitignore:3` 的 `*.log` 覆盖了 `delivery/**` 下的证据目录。
- 本轮不改：是否给 `delivery/**/evidence/**/raw/*.log` 开豁免属仓库级策略，须独立 CHG 裁定并据此重扫历史。

### 多仓状态文件的说明

`.ai/CURRENT_CONTEXT.md` 的执行边界要求「多仓 CHG 在 `delivery/active/<CHG>/status/<repo>.md`
记录逐仓状态」。经查本仓历史（`git log --all --diff-filter=A -- 'delivery/*/CHG-*/status/*'` 无输出），
该约定**从未被实际使用过**——包括同为多仓的 CHG-052（归档时同样只有 `change.md` 与 `checkpoint.md`）。

本轮**不新造该结构**：CHG 已关闭，逐仓状态应属于归档记录。事实上它已在 `change.md` 的
「仓库」列与 `checkpoint.md` 的逐仓提交号（cloud `65b67d3`/`a3b8bea`、desktop `5141e36`/`69246be`、
workspace 本记录）中逐条落地，无需另立空壳文件。登记此差异，供后续把该约定写清或删掉。

## 4. 验证读数

| 项目 | 命令 | 结果 |
| --- | --- | --- |
| 快照生成 | `python3 scripts/prepare_ai_workspace.py --no-active` | 写出 `Active CHG: \`none\``（见 `.ai/CURRENT_CONTEXT.md`） |
| 交付治理 | `python3 scripts/verify_delivery_governance.py` | `Delivery governance verification ok. Active CHG: none`，0 ERROR |
| 生成器测试 | `python3 -m unittest discover -s tests -p 'test_prepare_ai_workspace.py'` | 6 tests OK（原 3 + 新增 3） |
| 全量测试 | `python3 -m unittest discover -s tests -q` | 见下「已知红项」，与本次改动无关 |

三仓代码仓（cloud / agent / desktop）本轮**未改动**，工作树保持干净——关闭动作只落在治理仓。

## 5. 已知红项（已存案，非本次引入）

**这不是本次发现**：`docs/engineering/specs/agent-workspace-conventions.md` 第 10 节
「校验与已知红项」早已逐条登记，并写明「上述红项不在 Agent 入口工作范围内，需各自独立开 CHG 处理」。

全量测试在本次改动前后各有 4 条 FAIL，**完全同集**（基线对照：改动前 `git stash` 后重跑，同样 4 条）：

```
FAIL test_verify_m0_config.VerifyM0ConfigTests.test_contract_map_matches_m1_cloud_agent_compatibility
FAIL test_verify_m0_config.VerifyM0ConfigTests.test_contract_map_provider_paths_exist_in_full_workspace
FAIL test_verify_m2_acceptance.VerifyM2AcceptanceTests.test_static_cross_repo_contract_and_security_matrix
FAIL test_verify_product_master_alignment.ProductMasterAlignmentTests.test_current_product_master_and_governance_are_aligned
```

分母与性质：全量 69 条（改动后）/ 66 条（改动前，含我新增的 3 条），红 4 条；四条均来自
§10 已登记的三个校验脚本。
**本次不修**：它们不属于 CHG-055 范围，修它们等于改写 M0/M2 的历史验收口径，须由独立 CHG 处置。

一处与本轮相关的读数变化：`verify_product_master_alignment.py` 的失败信息中，
M3 一项由改动前的 `M3 status expected 'NOT_STARTED', got 'IN_PROGRESS'` 变为
`M3 status expected 'NOT_STARTED', got 'DONE'`（已实测确认）。该脚本内嵌的 M3 期望值本就落后于真实基线
（§10 已记为「校验脚本内嵌的期望值漂移」），**红/绿性质不变**，漂移项数仍为 2。

顺手把 §10 那一行的总数订正为「69 项中 4 项失败」并注明总数只因新增测试而变、红项集未变。

## 6. 提交边界

治理仓单独提交：`scripts/prepare_ai_workspace.py`、`scripts/verify_m3_acceptance.py`、
`tests/test_prepare_ai_workspace.py`、`delivery/`（归档移动 + 台账 + 里程碑 + 主计划 + planned 索引 + 本证据）、
`.ai/CURRENT_CONTEXT.md`、`AGENT-INDEX.md`、`docs/engineering/specs/agent-workspace-conventions.md`
（登记 `--no-active` 与订正测试总数）、`docs/product/M3-content-mining-v2.md` 与 `docs/decisions/0015-*.md`
（M3 证据指针改指归档位置）。
运行时代码仓本轮无改动，不产生提交（`git status --porcelain` 在 cloud/agent/desktop 三仓均为 0 项）。
