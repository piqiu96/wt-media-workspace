# T-04 证据：归档边界两条 ERROR 门禁

- CHG: `CHG-20260925-066`
- Task: T-04（`change.md` §8）
- 日期: 2026-09-26
- 判据: `scripts/verify_delivery_governance.py::check_archive_readonly` /
  `check_completed_has_boundary`

## 1. 两条判据与各自的分母

| 判据 | 级别 | 判什么 | 现树分母与读数 |
| --- | --- | --- | --- |
| `check_archive_readonly` | ERROR | `scripts/*.py` 中流向写操作、且写入目标可达 `delivery/completed/` 的**每一处** | `scanned 12 script(s)`，`0 write(s)` |
| `check_completed_has_boundary` | ERROR | 归档区存在 ＋ `README.md` 存在 ＋ 含机读键 `- 归档边界：\`READ-ONLY\`` | `1 boundary marker(s)` |

两条分母由 `main()` 无条件打印——「0 命中」与「什么都没扫」必须能分开。
原始读数：`artifacts/t04-gate-readings.out`。

## 2. 判据层的阳性对照（锚：不变的基线提交 `05c2045`）

同一个 `check_archive_readonly` 跑在**改前**的 `verify_m3_acceptance.py` 上：
**11 处**归档写全部报出（`:285` `:288` `:304` `:306` `:310` `:311` `:385` `:524`
`:1061` `:1739` `:1740`），跑在现树上 **0 处**。原始输出
`artifacts/t04-readonly-oracle.out`。

锚取 `05c2045` 而**不取 `HEAD`**：T-03 一进 `HEAD`，对照就退化成镜子，
读数会恰好也是 0。

这 11 处中有 4 处（`:288` 的 `path`、`:385` 的 `log`、`:524` 的 `target`、
`:1061` 的 `log_path`）是**函数内的局部名**——它们必须先被「一跳传播」追上，
判据才有判别力；这正是 T-03 §14 第 11 项记下的那条：判据锚在**字符串字面量**
上，再从字面量追一跳，而不是锚在接收者变量名上。

**判据自身修掉的一处错**：`write_target` 初版对方法形式的 `x.open(mode)` 用了
内建形式的 mode 下标（第 1 个实参），于是 `path.open("rb")`（**读**）被读成写，
报出 14 处（多出 `:88` `:97` `:438` 三处假阳性）。是这条 oracle 抓出来的；
修好后恰好 11 处。

## 3. 用例层的阳性对照（变异：关掉判定 → 用例必须真红）

四条变异，每条都先断言「要替换的原文确实在脚本里」——替换没生效时会得到一条
**假的绿**。原始输出：`artifacts/t04-gate-mutation.out`。

| 变异 | 红掉的用例 | ERROR | ImportError |
| --- | --- | --- | --- |
| M1 关掉 `check_archive_readonly` 的判定 | `test_archive_write_from_script_is_reported`、`test_archive_checks_report_their_denominators`（2 条） | 0 | **0** |
| M2 关掉 `check_completed_has_boundary` 的判定 | `test_archive_boundary_marker_is_required`、`test_archive_boundary_readme_is_required`、`test_missing_archive_is_reported`、`test_archive_checks_report_their_denominators`（4 条） | 0 | **0** |
| M3 方法形式 `open` 的 mode 位置改回错的那一处 | `test_archive_reads_and_filter_literals_are_not_reported`（1 条） | 0 | **0** |
| M4 两条判据从 `validate_delivery_governance` 的接线里摘掉 | 写入／标记／README／归档缺失（4 条） | 0 | **0** |

M3 是**负例的变异**：它证明「只读面不被报」这条负例不是空的——把 mode 下标改错
之后，它立刻红。M4 证明判据不只是两个可被用例直接调用的函数，而是**真的接进了
门禁**（用例走的是 `validate_delivery_governance`）。

结论：四条变异全部红成 `FAIL`，`ImportError` 计数 **0**，`ERROR` 计数 **0**。

## 4. 负例：三种「提到归档区但不是写」的形态不得被报

同一条用例里三种形态各一条，都是 T-03 实测踩过的：

1. `(ARCHIVE / "README.md").read_text(...)` —— 读；
2. `(ARCHIVE / "README.md").open("rb")` —— 读，且是方法形式；
3. `NEVER_UPLOAD = ("delivery/completed",)` ＋ `path not in NEVER_UPLOAD` ——
   `own_artifacts` 那种**只用来过滤**的路径串（T-03 §14 第 11 项的负例）。

## 5. 落地时暴露的第三处（记入 §14）

`tests/test_prepare_ai_workspace.py::test_no_active_change_renders_none_snapshot`
也调用 `validate_delivery_governance`，其 fixture 建的临时树没有归档区，于是新判据
报出 `archive boundary: delivery/completed/ is missing`。**这是 fixture 不合规，
不是判据错**：该用例要验的是「关掉最后一个 CHG 时快照渲染为 `none`」，与归档无关。
按与其他 fixture 相同的规则就地补上合规归档区（不是放宽判据）。
全量套件 **94 → 100** 用例，`OK`（`artifacts/t03-gate-readings.out` 的 94 对
`artifacts/t04-gate-readings.out` 的 100）。

## 6. 范围与残余（不宣称覆盖更多）

- 判据只扫 `scripts/*.py` 顶层。`scripts/` 下另有 **6 个 shell 脚本**
  （`build-desktop.sh`／`init-agent-entry.sh`／`local-control.sh`／
  `m2b-local-acceptance.sh`／`test-local-control.sh`／`verify_m0_local.sh`）
  **不在判据内**。人工读数：这 6 个文件提到 `delivery/completed` 的行数 **0**
  （`grep -n "delivery/completed" scripts/*.sh`）——是读数，不是判据。
- `is_archive_literal` 接受单独一段 `completed`（路径逐段拼出时只能这样认）。
  代价是对无关的 `"completed"` 字面量会误报。现树该字面量只出现 **1 次**
  （门禁自己的 `ARCHIVE_SEGMENT`），且没有任何写入指向它。
- 污染集是「模块级传递闭包 ＋ 函数内一跳」。函数内**不做**闭包是刻意的：
  做了会因名字空间跨函数共用而爆炸（T-03 §14 第 11 项实测约 180 个名字）。
  代价是同名不同义会误报——现树 0 命中。
- `ARCHIVE_WRITE_ALLOWLIST` 当前为空。留它是为了让「唯一的例外」有地方写、
  且必须写明理由。

## 7. 本 Task 改动的文件

| 文件 | 改动 |
| --- | --- |
| `scripts/verify_delivery_governance.py` | 新增 `import ast` 与 §「归档边界」一节（两条判据 ＋ 三个辅助函数）；`validate_delivery_governance` 接线；`main()` 打印两条分母 |
| `tests/test_verify_delivery_governance.py` | fixture 改为默认合规（归档区 ＋ 标记串 ＋ `scripts/` 空目录）；新增 6 条用例 |
| `tests/test_prepare_ai_workspace.py` | fixture 补合规归档区（§5） |
