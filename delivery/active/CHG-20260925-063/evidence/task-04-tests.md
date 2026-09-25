# Evidence: T-04 修正测试套件的假通过与失效用例

- CHG: `CHG-20260925-063`
- Task: `T-04`
- Date: 2026-09-25
- Type: command
- Status: PASS

## Purpose

`tests/test_verify_product_master_alignment.py` 5 条用例里有 1 条**从未验证过它命名的机制**（`change.md` §4.4），
另有 3 条用**「存在某标签」**判定，可被同族的任何错误满足。本任务把 5 条改成 7 条，
并把断言判定方式从「有某标签」改为「**错误集合逐条相等**」。

改前（T-03 之后，`artifacts/t04-postfix-full-test-suite.out` 的前身读数）：整套 **Ran 73 / 1 FAIL**。
改后：该文件 **Ran 7 / OK**，整套 unittest **Ran 75 / OK**（连跑两次，读数一致）。

## 关键一步：先证明「旧用例绿的原因也是空转」，再改

T-03 只查明「变异字符串在 MASTER 中不存在 ⇒ `str.replace` 是空操作」。**这不足以说明用例是空的**——
也可能它本来就靠别的途径失败。于是先做阳性对照，用 `1ce97d9~1` 版脚本对**未变异**文本求值：

```
M3 candidate missing 'source_content' / 'Scheduler' / '正式任务 Schema' / '真实抖音接口'
-> 'M3 candidate' errors present BEFORE any mutation: 4
```

而该用例的断言是 `any("M3 candidate" in error for error in errors)` ⇒ **它在变异之前就成立**。
**两个错互相掩盖**：空操作让用例看起来在测禁用对象机制，恒定噪音让断言看起来被变异触发。

**终极对照（`artifacts/t04-mutation-control.py` 第 3 臂）**：把**旧脚本**的 M3 禁用检查
`if forbidden in m3_candidates:` 改成 `if False:`（判定被整条关掉），再跑旧用例的逻辑 ——
**它依然通过**。即：这条用例**无法检测它所命名的那条检查被删除**。

## 改动清单

| 用例 | 改法 |
|---|---|
| `test_current_product_master_and_governance_are_aligned` | 不变（本来就是全量断言） |
| `test_done_milestones_need_no_candidate_block` | **新增**：钉住 D-04 分层——M2/M3 无候选块**且**整体干净，防止日后有人把「必须有候选块」加回到已关闭里程碑上 |
| `test_rejects_reopened_milestone_status_regression` | 断言改为**恰好 1 条**（M0 有块，故缺块检查不插话） |
| `test_rejects_forbidden_operational_object_in_candidate_chg` | **重定目标**：M3（块已撤）→ **M8 与 M9**（均 `NOT_STARTED` 且**有非空块**）；断言改为恰好 1 条；**两条禁用臂都测** |
| `test_rejects_unfinished_milestone_without_candidate_block` | **新增**：清空 M9 块，断言**全部 4 条**——结构检查 1 条 + `require_all` 3 条噪音，**并明确禁用循环贡献 0 条** |
| `test_rejects_missing_m2_product_capability` | 断言改为**恰好 2 条**（实测 `M2-C：` 在全仓**只出现 1 次**，剥掉它同时打掉段标签与能力 needle） |
| `test_contract_governance_requires_mixed_state_and_active_task_schema` | 断言改为**恰好 1 条** |

### 两处判据所需的库级配套（写在测试文件里）

- **`mutate()`**：先 `assertIn(old, master)` 再替换，并 `assertNotEqual(changed, master)`。
  前者正是本条假通过的病根——**目标不存在时 `replace` 是静默空操作**；后者覆盖 `old` 为空串的退化情形
  （空串 `in` 任何字符串，`replace("", "", 1)` 等于原文）。
- **`assert_errors()`**：比较**排序后的完整错误集合**，而不是「有没有某标签」。
  标签式断言的问题是**同族任何一条错误都能满足它**，于是用例在它命名的那条判据坏掉时仍然绿。

## Method

```bash
python3 -B -X pycache_prefix=/tmp/pyc-none -m unittest tests.test_verify_product_master_alignment -v
python3 -B -X pycache_prefix=/tmp/pyc-none -m unittest discover -s tests -q
python3 -B -X pycache_prefix=/tmp/pyc-none delivery/active/CHG-20260925-063/evidence/artifacts/t04-mutation-control.py .
```

原始输出：`artifacts/t04-postfix-test_verify_product_master_alignment.out`（7 条逐条 ok）、
`artifacts/t04-postfix-full-test-suite.out`、`artifacts/t04-mutation-control.{py,out}`、
`artifacts/t04-gate-readings.out`、`artifacts/t04-baseline-verify_product_master_alignment.py`
（`1ce97d9~1` 版脚本，11466 字节，供第 3 臂复跑）。

## Mutation control（AC-09、AC-10）

新写的代码必须先能**红**——但**红的形态必须是「判定被关掉后用例失败」，不能是 ImportError**
（导入错误什么都证明不了）。故每一臂都是「**关掉一条判定，重放对应用例的谓词**」：

```
ok  control: forbidden-object predicate holds on the real script      (expected PASS)
ok  control: missing-block predicate holds on the real script         (expected PASS)
ok  forbid_all() neutralised -> forbidden-object test goes red         (expected FAIL)
ok  structural check disabled -> missing-block test goes red           (expected FAIL)
ok  no-op mutation + silent M3 forbidden check -> old test STILL passed (expected PASS)
```

前两臂是**阳性对照**：未变异的真实脚本上两个谓词成立。后三臂是判别力本身。
**第 3 臂是决定性的**：它证明的不是「新用例有效」，而是「**旧用例无效**」——
旧用例对关掉它命名的判定毫无反应。

## 覆盖范围（如实枚举）

| 情形 | 是否覆盖 |
|---|---|
| 禁用对象检查在**非空块**上会报 | ✅ M8 `interaction_batch`、M9 `production_signal` 各 1 臂 |
| 未关闭里程碑**缺块**会报 | ✅ M9 清空 |
| 已关闭里程碑**无块**被接受 | ✅ 新增用例 + 全量断言 |
| 已关闭里程碑被**改回未关闭** | ✅ 状态变异（且实测会**同时**触发缺块检查，已记） |
| 状态词、M2 能力清单、M0 门禁措辞、契约层判定 | ✅ 各有臂，且均为全集合比较 |
| 禁用对象检查在**空块**上不报（静默） | ✅ 由清空 M9 那臂的期望集合显式记下「贡献 0 条」——**这是已知且有意保留的行为**，因为空块本身已由结构检查单独报出 |

**未覆盖、如实登记**：本文件不覆盖 `validate_active_change()` 与 `validate_product_identity()` 两条路径的
负向用例（该二者本 CHG 未改动，且 `test_current_product_master_and_governance_are_aligned`
只做全量正向断言）。此点属既有覆盖缺口，**不在本任务范围内**，不冒充已覆盖。

## 与 §14 遗留的关系

- 本任务关闭 `change.md` §4.4 登记的假通过。
- **未引入** `verify_product_master_alignment.py` 要求 active CHG 的 §7 为字面 `None.` 那条形状限制（遗留 7）的任何对策。
