# T-06 evidence — 脚本／模板与 `checkpoint.md` 落点对齐

日期：2026-09-25
Task：T-06（依赖 T-05）
原始读数：`evidence/artifacts/t06-gate-readings.out`

## 1. 改前的缺口（逐项实测）

| 缺口 | 改前事实 |
|---|---|
| 「active 目录必须有 `checkpoint.md`」这条**规则已存在但无人执行** | `AGENT-INDEX.md` §8 写「该目录**至少包含** `change.md` 与 `checkpoint.md`」，而 `git grep -i checkpoint -- scripts tests` 命中 **0** 个文件（阳性对照：同一扫描对 `change.md` 命中 9 个文件）⇒ 没有任何门禁读它。一个只有 `change.md` 的 active CHG 能通过全部六个门禁 |
| `templates/delivery/` 缺 `checkpoint.md` | 目录下只有 `change.md`、`evidence-record.md` |
| 模板把 checkpoint **内联**在 `change.md` §12 | `templates/delivery/change.md:121-136` 是 Completed／Current／Next／Blocked 的实体块，与「独立 `checkpoint.md`」的用法相反 |
| skill 教的是错落点 | `skills/workspace/executing-wt-media-change/SKILL.md:95`：「Update the active **`change.md`** checkpoint」 |
| 脚本接受集与 §3 的词汇**交集为零** | `:290` 只收 `{IN_PROGRESS, IMPLEMENTING, VERIFYING, ACTIVE}`——`IN_PROGRESS` 与 `ACTIVE` 均由 T-05 判为退役／幻影词 |
| 脚本把带注的状态行**读成 `None`** | `:288` 的 `(\S+)\s*$` 要求整行只有那个词；带注形式一个都匹配不上（见 §4） |

## 2. `checkpoint.md` 结构检查（红 → 绿 → 变异对照）

改 `tests/test_verify_delivery_governance.py`：夹具 `write_active_change` 改为写**成对**文件，新增 `test_active_change_without_checkpoint_is_reported`（删掉夹具刚写的 `checkpoint.md`，断言错误集恰为一条）。实现加在 `scripts/verify_delivery_governance.py` 的 active 循环里。

| 步 | 操作 | 实测 |
|---|---|---|
| 红 | 只加测试、未加检查 | `FAILED (failures=1)`，报文 `Lists differ: [] != ['active CHG is missing checkpoint.md: CHG-20260722-021']`——**是判据缺失的红**，不是 `ImportError`／夹具坏了 |
| 绿 | 加检查 | `Ran 5 tests … OK`；`verify_delivery_governance.py exit=0` |
| **变异对照** | `if not (…)` 改为 `if False and not (…)`（命中 1 处，断言过） | 新测试**再次变红**（`Ran 5 tests … FAILED (failures=1)`），其余 4 条仍绿 ⇒ 该用例确实绑在这段代码上，不是被夹具的整洁满足的 |
| 还原 | 由备份拷回 | `cmp` 逐字节相同；再跑 `OK` |
| **活树阳性对照** | 把 `delivery/active/CHG-20260925-064/checkpoint.md` 临时改名 | 真门禁报 `ERROR active CHG is missing checkpoint.md: CHG-20260925-064`、`exit=1`；还原后 `sha256` 与原文件相同（`bd5e5fa8…`）、`exit=0` |

夹具的两处附带更正：`write_ledger` 与 `write_active_change` 由 `IN_PROGRESS` 改为 `IMPLEMENTING`（T-05 定下的活态词）。

## 3. 接受集收口（红 → 绿）

`:290` 由 `{IN_PROGRESS, IMPLEMENTING, VERIFYING, ACTIVE}` 收为 **`{IMPLEMENTING, VERIFYING}`**，`:292` 文案同步；`:282-283` 的注释仍以 `> 状态：ACTIVE` 举例，改为不再点名退休词。

**为什么只收这两个词**：记录落在 `delivery/active/` 就意味着正在执行。`DISCUSSION`（不激活）与 `PLANNED`（可激活）是**激活前**的状态、家在 `delivery/planned/`；`DONE`／`SUPERSEDED` 是终态。收任何一个都等于把 §3 明令禁止的状态放行。

| 词 | 旧接受集 | 新接受集 |
|---|---|---|
| `IMPLEMENTING`／`VERIFYING` | 收 | 收 |
| `DISCUSSION`／`PLANNED`／`DONE`／`SUPERSEDED` | 拒（但报文写「IN_PROGRESS, IMPLEMENTING or VERIFYING」） | 拒（报文与新集一致） |
| `IN_PROGRESS`／`ACTIVE` | **收**（T-05 已判为退役／幻影） | 拒 |

新增 `test_active_change_accepts_only_the_two_execution_words`（两个合法词各跑一遍，6 个非法词各跑一遍，断言**完整错误集**）。**红**：把脚本换回 `HEAD` 版 → 6 个非法词 subTest **全部失败**（`subTests failed: 6`），其中 `IN_PROGRESS` 与 `ACTIVE` 是**被旧集收下**（`[] != [ … got 'IN_PROGRESS' ]`），另 4 个是报文不一致。**绿**：新脚本 `Ran 10 tests … OK`。还原经 `cmp` 逐字节确认。

**必须在本 CHG 仍 active 时复测**（计划要求）：以上绿读数都是在 `CHG-20260925-064` 仍在 `delivery/active/`、接受集正好打在**它自己的 LEDGER 表行**上时取得的。

## 4. 带注状态行被读成 `None`（实测发现的既有缺陷，就地修）

`:288` 的 `(\S+)\s*$` 要求状态行**恰好**是那个词。实测：58 篇 `change.md` 里 **9 篇**的状态行带注（分母 58），形式有全角括号 `（…）`、半角 `(…)`、以及 `**WORD（…）**` 加粗包裹。这些行**一个都匹配不上** ⇒ `status` 为 `None`。

这不是假想：`delivery/completed/CHG-20260923-059` 在 active 期间的状态行就是
`- Status: IMPLEMENTING（2026-09-25 由 \`delivery/planned/\` 激活并改写为十三节执行记录）`，
而它自己的门禁输出里留着这条错（`evidence/task-08-gate.out`）：

```text
'active CHG status must be IN_PROGRESS, IMPLEMENTING or VERIFYING, got None',
```

**这条报文点的是一个该记录从未有过的状态**——记录是合法 active，脚本报 `got None`。与 T-03 那类「模式对不上就是空转」同源：判据没咬住它就报了一个别的东西。

处置：抽出 `status_word()`——先剥 `**`、再剥 `（…）`／`(…)`，再交给接受集判。

新增两个用例，`HEAD` 版脚本上的红**是行为性的**：`test_annotated_status_line_is_read_as_its_word` 对 `CHG-059` 的原句得到
`AssertionError: Lists differ: ['active CHG status must be IN_PROGRESS, IMPLEMENTING or VERIFYING, got None'] != []`
——**在测试里复现了 059 门禁输出里的那条报文**，而新脚本下为 `OK`。

> 一次自我更正：该用例初稿同时断言 `status_word()` 与 `validate_active_change()`，于是 `HEAD` 上的红是
> `AttributeError: module … has no attribute 'status_word'`——**这种红什么都证明不了**。改为把取词断言拆到
> 另一个用例（`test_status_word_strips_bold_and_annotation`），行为用例只调 `validate_active_change`，
> 红才是行为性的。同一次里还修了夹具自身的 bug：初次把带注串当 LEDGER 值写进去，多出一条
> `Ledger is not aligned …`。

**口径变严的一处**：剥注后 `status` 不再为 `None`，`ledger` 表行比对（`:308` 的
`if title and status and current_repository`）由**被跳过**变为**真的执行**。这是收紧，不是放松。

`MASTER` §3 的两处连带改写（T-06 的落点之外，但本 Task 造成了它们的失效）：

1. 历史词汇句里的 `ACTIVE`（0 处，**只在 `verify_product_master_alignment.py` 的接受集里**）——接受集改了，这个括号就地作废，改为「`ACTIVE`（0 处）」，并补一句「落到 `delivery/active/` 的记录只有 `IMPLEMENTING`／`VERIFYING` 合法」。
2. 同一句把 `TODO` 与 `IMPLEMENTED`、状态值 `VERIFIED` 并列说成「零处使用」——**`TODO` 在任务表的状态列仍合法在用**（本 CHG 自己的 §8 有 18 行，模板 `:76` 也用它）。已限定为「作为 **CHG 状态值**的 `TODO`…」。

## 5. 模板与 skill

- **新增 `templates/delivery/checkpoint.md`**：标题 ＋ CHG／Level／Updated ＋ 状态 ＋ Completed／Current／Next／Blocked／Recent verification。内容取自真实 checkpoint 的形状，并写明两条纪律：状态词来自 `MASTER` §3；**读数必须在最后一次内容改动之后取**（早取的不是关闭值）。
- `templates/delivery/change.md` §12 由内联块改为**指针**，并写明「active CHG 缺 `checkpoint.md` 会被 `verify_delivery_governance.py` 拒绝」。
  - 计划里点了 `templates/delivery/change.md:6`（`- Status: DISCUSSION`）作为落点，**实测它已经是 T-05 定的词，无需改动**——如实登记，未为「有计划」而改。
- `skills/workspace/executing-wt-media-change/SKILL.md:95`：「Update the active **`change.md`** checkpoint」→「Update the active **`checkpoint.md`** …… it is a **required** file …… Keep `change.md` for the plan and the acceptance record」。
- `AGENT-INDEX.md:141`：「必须更新 checkpoint」→「必须更新 **`checkpoint.md`（不是 `change.md`）**」（§8 早已写死这条规则，此处只是把文件点名）。
- 重生成：`sync_skills.py sync`（`exit=0`）→ `sync_skills.py check`：`skill outputs are up to date`（`exit=0`）。
- `README.md:40` 的 `templates/delivery` 说明补 `checkpoint`。
- `conventions` §9 加两行耦合：**active 记录成对**（规则＝`AGENT-INDEX.md` §8；实现＝新检查 ＋ 模板 ＋ skill）与 **CHG 状态词**（规则＝`MASTER` §3；实现＝接受集）。

## 6. 门禁读数（在 T-06 最后一次内容改动之后取）

| 判据 | 读数 |
|---|---|
| 六个静态门禁 | 全部 `exit=0` |
| `python3 -m unittest discover -s tests -q` | **`Ran 79 tests` / `OK`**（T-05 收盘为 75；T-06 新增 4：`test_verify_delivery_governance` ＋1、`test_verify_product_master_alignment` ＋3） |
| `sync_skills.py check` | `skill outputs are up to date`，`exit=0` |
| 三仓工作区 | `cloud` `?? dump.rdb`；`agent`、`desktop` 空——与 T-01 基线逐条一致 |

三仓零写**在 `sync_skills.py sync` 之后复测**：该命令会写到四个 target（含三仓的 `.claude`／`.codex`），故必须量。
实测同步前后三仓 `git status --porcelain` 逐字相同；`desktop` 的 `.claude` 由 `.gitignore:10` 忽略，其余仓该 skill 未分发（`sync_skills.py diff` 只报 `root/codex`、`root/claude`、`workspace/codex`、`workspace/claude` 四处过期）。

## 7. 未覆盖 / 未决

- **`status_word()` 只剥一层括号**：`- Status: DONE（见 A（B））` 会得到 `DONE（见 A` 再被剥成 `DONE`（正则 `[（(].*$` 贪婪到行尾），行为正确但属实现巧合；嵌套括号未单独立例。
- **`> 状态：` 与 `- Status:` 混写**未处理（取**第一处**匹配）；实测 58 篇无一篇同时写两种形式。
- 任务表状态词（`TODO`／`DONE`）**无门禁**，本 Task 只把 §3 的措辞限定到 CHG 轴，未新增判据（属「补落点」，见 §14）。
- `delivery/completed/CHG-20260925-063/evidence/artifacts/t04-baseline-verify_product_master_alignment.py` 是**当时脚本的留证副本**，其中仍是旧接受集与旧正则——**故意不改**：它是基线快照，改了就是伪造证据。
