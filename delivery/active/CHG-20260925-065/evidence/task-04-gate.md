# T-04 门禁实现与退役

本文件只记事实（改了什么、期望、实际、结论）。原始输出：`artifacts/t04-gate-readings.out`、`artifacts/t04-mutation.out`。

## 1. 改了什么

| 项 | 改前 | 改后 |
|---|---|---|
| 新增检查 | — | `check_repo_entry_files`(E)、`check_pointer_shape`(E)、`check_rule_body_consistency`(E)、`check_layer3_shape`(E)、`check_rule_text_duplication`(W，打印分母)、`check_local_order_scope`(W) |
| 退役 | `check_entry_drift` ＋ `check_layer3_entries`；`FORBIDDEN_RE`／`PATH_TOKEN_RE`／`DRIFT_TOKEN_RE`／`path_tokens()` | 代码中 `check_entry_drift` **0** 条、`check_layer3_entries` **0** 条 |
| `tests/` | 16 条用例；fixture 只有 workspace ＋ cloud，且**默认不满足新形态** | **31 条**；fixture 补齐 agent／desktop 且**默认合规**（新的协作对象由 fixture 建好）；新检查一律断言**完整错误集合逐条相等** |
| 套件 | Ran 79 | **Ran 94**（79 − 16 ＋ 31） |
| `AGENT-INDEX.md` §12 | `# 入口文件、执行快照唯一性与体积预算、各仓入口漂移 WARN` | `# 入口文件形态（指针／正文／目录图）、执行快照唯一性与体积预算、配置一致性`（**按内容定位改**——T-02 加行后该句由 `:193` 漂到 `:198`） |

`check_repo_entry_files` 吸收了旧 `check_layer3_entries` 的意图并升为 ERROR；保留的 WARN 只剩一种：**仓目录本身不在检出里**（可移植性）——这样「目录缺失」与「文件缺失」不会再读成同一件事。

## 2. 真实现状读数（预期见红，分母 = 71 条 ERROR）

```
verify_agent_entry: exit=1   ERROR 71 / WARN 0
cloud 51 · agent 10 · desktop 7 · workspace 3
notes: rule-text duplication: compared 62 rule sentence(s) across 11 file(s) in 4 repositories
```

分判据：`declares no rule body` 8 ／ `restates a rule without naming` 56 ／ `exceeds the pointer budget` 4 ／ `H2 sections, expected 8` 3。**其余五个门禁仍全绿**；`unittest` **Ran 94 / OK**。

⇒ 这 71 条**就是 T-05～T-08 的分母**，逐仓记入 `checkpoint.md`。

**WARN 为 0 的两条要按原因读，不能读成「干净」**：

- `check_local_order_scope` 报 0，是因为三仓的小节**仍叫 `## 上下文加载顺序`**，改名后才是该检查的输入。**T-07 之后必须重测**，届时它才真的在看东西。
- `check_rule_text_duplication` 报 0，**附分母**（62 条规则句／11 文件／4 仓）——非空分母是它这次没有空转的证据。

## 3. 变异对照（分母 6 条新检查；要求「关掉判定后用例失败，且不是 ImportError」）

做法：把 `scripts/` 与 `tests/` 复制进 `mktemp -d`，在模块**末尾**重定义该检查为空实现（`validate_agent_entry` 在调用时查全局名，故末位定义生效），跑套件。

| 被禁用的检查 | 失败用例数 | ImportError | 失败的用例 |
|---|---|---|---|
| `check_repo_entry_files` | 3 | 0 | absent_repository_is_warned、empty_running_repo_entry_file、missing_running_repo_entry_file |
| `check_pointer_shape` | 7 | 0 | empty_running_repo_entry_file、pointer_declaring_itself、pointer_key_pointing_nowhere、pointer_over_heading_budget、pointer_over_line_budget、pointer_restating_a_rule、pointer_without_machine_key |
| `check_rule_body_consistency` | 4 | 0 | pointer_chain_through_the_body、pointer_declaring_itself、pointer_key_pointing_nowhere、pointers_disagreeing_on_the_body |
| `check_layer3_shape` | 2 | 0 | layer3_section_count、layer3_sequence_divergence |
| `check_rule_text_duplication` | 2 | 0 | duplication_denominator_is_reported（`ERROR`，见下）、duplicated_rule_sentence_is_warned |
| `check_local_order_scope` | 1 | 0 | local_order_section_leaking_the_project_order_is_warned |

**六条检查各有至少一条用例在它被关掉时失败，且六次 `ImportError` 计数全为 0。**

**一处如实登记的不足**：`duplication_denominator_is_reported` 在变异下是 `ERROR`（我的辅助方法 `next(...)` 抛 `StopIteration`）而不是 `AssertionError`。它是被禁用的检查导致的真实失败、不是导入错误，但**不是** `AGENT-INDEX.md:206` 要求的「用例失败」的那种最干净形态。已在 `change.md` §14 登记。

## 4. 实现期实测推翻的三处写法（代码是对的，是我原来的期望窄了）

1. **`pointer_body` 不能在校验失败时返回 `None` 就完事**：`AGENTS.md` 声明自己是正文时，「正文不同一」本应同时报出，而短路让后者消失——**一条破损被另一条破损掩盖**。改为返回**声明的原值**（即使它无效），两个判据各自独立判断。
2. **正文声明正文要单独抓**：只用「声明的正文不能是指针文件」抓不住 `AGENT-INDEX.md` 里写 `- 正文：\`CLAUDE.md\``（`A -> B, B -> A` 的那种环）。补「正文必须终结」判据。
3. **同一缺陷被报两遍**：两个指针都声明同一个破损正文时，逐指针循环会输出两条完全相同的 ERROR。改为按**声明值**去重——一个缺陷一条。
4. 另有两处是我的**期望写错**（不是代码错）：指针模板里「唯一落点」那句**不含任何规则词**，故我原以为会同时命中的「规则词越界」并不发生——`规则`／`落点` 都不是规则词。据此把该用例改成显式注入一行规则句。

## 5. 未覆盖 / 已知边界

- **`规则词` 词表未穷尽**（`conventions §3` 只举例）。实测影响：`规则`／`落点`／`红线` 等名词不入表，故「`## 模块规则` 段被贴进指针」这类变异是靠**段内规则句**抓的，不是靠标题名——这正是 §3 改成「标题行不计入」的同一理由。
- **`check_rule_text_duplication` 的比较集偏粗**：`DIRECTORY_MAP.md` 的说明句「目录事实与禁止扫描区的唯一落点」因含 `禁止` 而进比较集（fixture 里计入 3 条规则句中的 1 条）。它是**每仓一行、内容唯一**，不会触发重复；但「规则句」这个词比实际含义宽。
- **门禁对真实现状是红的**（§2），故本 Task 的收尾读数**不**包含 `verify_agent_entry` 的绿。T-09 必须在 T-07 之后重测。
- 本 Task **未**触碰三仓任何文件；`workspace` 那 3 条按 T-08 处置。

## 6. 用门禁自己的函数复测生成器产出（兑付 T-03／AC-13 的欠账）

T-03 的 12 项形态对账用的是**我写的临时脚本**，当时已声明「不是门禁，T-04 后须调门禁自己的函数复测」。本节兑现：把 `scripts/` 复制进临时树、让 `ROOT` 落在临时树上，用生成器写一个仓，然后**调 `verify_agent_entry.py` 的六个函数**（不是另写正则）。脚本与原始输出：`artifacts/t04-remeasure.sh`、`artifacts/t04-generator-vs-gate.out`。

| 门禁函数 | 生成器产出上的读数 |
|---|---|
| `check_repo_entry_files` | ERROR 0 ／ WARN 0 |
| `check_pointer_shape` | 0 |
| `check_rule_body_consistency` | 0 |
| `check_layer3_shape` | 0 |
| `check_rule_text_duplication` | WARN 0；**分母** `compared 1 rule sentence(s) across 2 file(s) in 1 repository` |
| `check_local_order_scope` | 0 |

**阳性对照（同一批函数、故意破坏的树）3/3 命中**：删 `DIRECTORY_MAP.md` → `check_repo_entry_files` 报 `cloud: missing agent entry file: DIRECTORY_MAP.md`；往 `CLAUDE.md` 追加一行规则句 → `check_pointer_shape` 报 `CLAUDE.md:11 restates a rule without naming AGENT-INDEX.md`；往 `## 本仓内加载顺序` 插 `.ai/CURRENT_CONTEXT.md` → `check_local_order_scope` 报出。⇒ 六个 0 **不是路径写错造成的空转**。

**两处按分母读、不读成「全绿」**：
- `check_layer3_shape` 的 0 里，**跨仓序列比较的分母是 1**（只生成一个仓，`zip` 无配对），真正跑到的是长度＝8 那条。跨仓相等那部分在本树上是**未覆盖**的，得由真树（T-05～T-07）覆盖。
- `check_rule_text_duplication` 的**分母只有 1 条规则句**——生成器产出的骨架是占位符（`（本仓依赖的…）`／`待补`），不含规则句。分母非空故非空转，但**薄**；它是「骨架没有规则句」的读数，不是「重复判据在真实文件上无重复」的读数。

**一处我自己的工具缺陷（发现并改正，登记）**：第一版复测脚本把 `check_rule_text_duplication` 的返回值当成 `(warnings, warnings)` 打印——它是 `(warnings, note)`，于是把 note **字符串按字符逐个印成 83 条 WARN**。真读数是 `WARN 0`。若不复看输出，「83 条 WARN」就会被当成结论写进证据——**辅助脚本的打印形状也要被核**，与「计数必须当场量」同源。

