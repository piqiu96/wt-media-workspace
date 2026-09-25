# T-05 证据：纯过程产物删除（按三形态复检后的清单）

- CHG: `CHG-20260925-066`
- Task: T-05（`change.md` §8）
- 日期: 2026-09-26
- 锚: HEAD = `f07142d`（T-04 的提交）

## 1. 结论

**T-02 的「42 files / 140,556 B ＝ 1.3%」是高估，实删 2 files / 54,810 B。**
原因不是清单挑错了文件，是 T-02 的**入站引用仪器只认三种写法中的一种**。

| 口径 | 判定为「被引用」 | 判定为「无引用」 |
| --- | --- | --- |
| T-02（形态 1：精确文件名／CHG 限定路径） | 158 files / 630,808 B | **42 files / 140,556 B** |
| 形态 1＋2（加带星 glob） | 21 / 42 | 21 / 42 |
| 形态 1＋2＋3（加裸前缀） | **37 / 42** | **5 / 42** |
| 实际删除 | — | **2 files / 54,810 B** |

读数：`artifacts/t05-reference-forms.out`（三形态逐条命中）、
`artifacts/t05-deletion-list.out`（删前删后）。

## 2. T-02 漏掉的两种写法（都是同 CHG 记录里的真引用）

1. **形态 2 — 带星 glob。** `CHG-20260925-062/change.md:221`：
   「`evidence/artifacts/`：原始输出（`t01-*`、`t03-*`、`t04-*`、`t05-*`）。」；
   `CHG-20260925-062/evidence/task-03-drift-sweep.md:27`：
   「`artifacts/t03-verify_product_master_alignment*.out`」。
2. **形态 3 — 裸前缀（不带任何 `*`）。** `CHG-20260925-064/change.md:395` 的产物清单写作
   「原始输出（`t01-`、`t03-`、`t04-`、`t05-`、`t06-gate-readings.out`、…）」——
   **前缀就是引用**，而任何基于 `*` 的扫描都看不见它。`CHG-20260925-063/evidence/task-01-m0-config.md:33-35`
   与 `:89` 同形。

⇒ 这两个 CHG 的 `t05-*`／`t01-baseline-*`／`t03-postfix-*` 等产物，在他们的记录里是**被点名的证据**；
删掉就是把归档记录的指针变成死链——`MASTER:132`「归档记录保持原样、不回改」的同一类缺陷。

**连 T-02 自己判为「同名碰撞、不是引用」的那 1 条（1,801 B）在三形态下也被引用**：
`CHG-20260925-064/evidence/artifacts/t05-gate-readings.out` 落在该 CHG 自己 `change.md:395` 的 `t05-` 清单里。

## 3. 五个「三形态皆无引用」的逐条裁定

**不删的 3 个（`CHG-20260923-055/evidence/raw/probe-*.json`，32,146 B）——它们是测量，不是派生。**
它们是 2026-09-23 那一刻由 `tools/csp-probe-proxy.py` 打出的 HTTP 探针原始结果，
**不是任何已跟踪源的确定性函数**：源码还在，但那一刻的响应不会重现。且
`delivery/milestones/M3-content-discovery-v2.md:59` 有一条**活指针**指向那个 evidence 目录做「实机复核」。
「只删可再生的纯过程产物」不含它们。

**删掉的 2 个（`__pycache__/*.pyc`，54,810 B）**：由已跟踪源码确定性派生、被 `.gitignore` 覆盖、
全仓（含归档）无一处点名；分母是**归档区全部 `.pyc` ＝ 2 个**，删后 0 个。

## 4. 执行与读数

- **仪器对照**（先证明这套读数能失败）：两个目标删前都报「存在」；一条不存在的同目录路径报「不存在」；
  `.pyc` 分母实测 2。
- 删前 **699 文件 / 10,740,897 B** → 删后 **697 文件 / 10,686,087 B**，差 **54,810 B**（与逐条读数相等）。
- **git 侧零痕迹**：两个 `.pyc` 本就被 `.gitignore` 覆盖，`git status --porcelain` 无删除项。
  **唯一记录就是本文件与 `artifacts/t05-deletion-list.out`**——这正是 §4 F-08 预判的形态。
- 删后六门禁全 `exit=0`、`unittest` `Ran 100 / OK`：`artifacts/t05-gate-readings.out`。

## 5. 判据的自限（不宣称覆盖更多）

- 只扫**同 CHG 的已跟踪文本**。被 `.gitignore` 覆盖的文件（`.pyc`／`.log`）不在分母内——它们的**内容**不参与匹配。
- 形态 3 的前缀规则是**收紧过的**：只认本仓的 Task 产物形状（`t\d\d-`、`task-\d\d-`）。
  松一档（任意 `-` 边界 ≥4 字符）会把 `probe-` 匹配到 `csp-probe-proxy.py`——**阴性对照实测失败过**，
  见 §4 的「对照」段与 `artifacts/t05-reference-forms.out`。
- 「目录级指针」不在此判据内（如 M3 里程碑指向 `CHG-20260923-055/evidence/`）：本 Task 按人工读数处理（§3），
  不是机检。

## 6. 本 Task 改动的文件

| 文件 | 改动 |
| --- | --- |
| `delivery/completed/CHG-20260923-056/evidence/tools/__pycache__/ac05_desktop_launch.cpython-314.pyc` | 删除（46,581 B） |
| `delivery/completed/CHG-20260924-060/evidence/tools/__pycache__/t02_csp_shipped_value_launch.cpython-314.pyc` | 删除（8,229 B） |
