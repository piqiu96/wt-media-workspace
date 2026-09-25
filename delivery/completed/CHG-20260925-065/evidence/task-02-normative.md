# T-02 规范与落点成文

本文件只记事实（改了什么、期望、实际、结论），不重复需求。原始输出：`artifacts/t02-normative-strings.out`。

## 1. 改了什么（四文件）

| 文件 | 改动 | 期望 | 实际 |
|---|---|---|---|
| `docs/engineering/specs/agent-workspace-conventions.md` | 文件头「更新」行；§1 #2／#3；**§3 整节改写**为「入口文件形态」；§9 耦合表两行 → 五行；§10 已知限制重写；§11 两条禁令 | §3 成为形态的**唯一落点**，且不新增节号（`verify_m0_config.py:249` 引 §10） | §3 现含：角色与边界表（5 文件 × 装什么／不装什么）／`AGENT-INDEX.md` **同名两角色**＋运行仓八节模板／**指针文件的机检定义**（三条 ERROR，含机读键 `` - 正文：`AGENT-INDEX.md` ``、**规则词判据**、H2≤1 白名单 `权威源`＋≤30 行＋≤2000 B）／「重复只在生成物与它唯一具名的生成器之间存在」／「为什么是两个指针」（含显式否决 `@` 导入的四条理由）。节号未变 |
| `AGENT-INDEX.md` | §4 `:62` 作用域句；§10 入口文件表（加 `DIRECTORY_MAP.md` 行、三仓列「四仓都必须存在」、`AGENT-INDEX.md` 角色改「该仓**全部正式内容**的唯一落点」）＋「两者都不得承载规则正文」段 | 治理仓**不复述**形态规定正文，只列强制项并指向 `conventions §3` | 表加 3 行；新增段落点名由 `scripts/verify_agent_entry.py` 强制。`§4` 明确「两个层级」而非「两个落点」 |
| `docs/engineering/architecture/社媒运营平台工程架构与分层设计_V1.md` | `:769` 补自洽句；`:1801` 验收话就地扩写 | 消解 `:769`（禁止整体覆盖）与四仓形态统一之间的表面矛盾；`:1801` 补进另四个文件 | `:769` 加「**Workspace 提供的是形态，不是内容**」；`:1801` 由「存在 `AGENTS.md` 和 `CLAUDE.md`」改为五文件 ＋ 角色规定 ＋ 点名门禁。`:478` 按 D-04 **不动** |
| 本 CHG 记录 | `evidence/artifacts/t02-normative-strings.out` | 判据串新写；读数带前后对照 | 见 §2 |

## 2. 判据串读数（锚 `bd5df2c`，分母 = 15 个判据串）

判据串**先写**进规范（本 Task），实现留 T-04。锚取**开工 commit `bd5df2c`** 而非 `HEAD`——修复一进 `HEAD`，对照退化成镜子。

| 判据串 | `bd5df2c` | 工作树 |
|---|---|---|
| `正文：`（机读键） | 0 | 1 |
| `check_pointer_shape` | 0 | 2 |
| `check_rule_body_consistency` | 0 | 1 |
| `check_layer3_shape` | 0 | 1 |
| `check_local_order_scope` | 0 | 1 |
| `check_rule_text_duplication` | 0 | 1 |
| `check_repo_entry_files` | 0 | 1 |
| `## 本仓规则` | 0 | 2 |
| `本仓内加载顺序` | 0 | 2 |
| `check_entry_drift` | 1 | 2 |

**阳性对照**：把全部 10 个判据串注入一份 fixture，`10/10 判据串模式全部命中 ✓`。⇒ 上表的 0 是「确实没有」，不是「grep 模式写错了」。

## 3. 「先写后实现」的证明

`scripts/verify_agent_entry.py` 中：

| 检查名 | 代码命中 |
|---|---|
| `check_pointer_shape`／`check_rule_body_consistency`／`check_layer3_shape`／`check_local_order_scope`／`check_rule_text_duplication`／`check_repo_entry_files` | **6/6 为 0** |
| `check_entry_drift`（阳性对照） | 2 |

⇒ 规范已点名并规定判据，代码里**一条都还没有**。T-04 落地时这些检查**必然对现状报红**（三仓八节序列未达 8、四件文件未齐、机读键未写、指针预算未测），由 T-05～T-07 逐个收口——这是 `checkpoint.md`「预期中间态见红」一节的实测依据。

## 4. 门禁读数（改后立刻取）

```
verify_m0_config / verify_delivery_governance / verify_agent_entry /
verify_skills / verify_product_master_alignment / verify_m2_acceptance : exit=0
python3 -m unittest discover -s tests -q : Ran 79 tests / OK
python3 scripts/sync_skills.py check : exit=0
```

六门禁全绿是**预期**：本 Task 只写规范与文档，未改任何脚本，而新判据尚未实现（§3）。

## 5. 未覆盖 / 遗留

- **`AGENT-INDEX.md` 里那句旧描述仍在**：计划写在 `:193`，计 T-04 与该脚本同 commit 改。T-02 的 §10 表新增 3 行后该句**移到 `:198`**——行号随本次改动漂移，故以内容定位（`# 入口文件、执行快照唯一性与体积预算、各仓入口**漂移 WARN**`）而非行号定位，T-04 按内容改。
- 本 Task **未**改 `scripts/init-agent-entry.sh`（T-03）与 `scripts/verify_agent_entry.py`（T-04）。
- 本 Task **未**触碰三仓任何文件。
- `conventions` §3 里「规则词判据」的词表本身尚未定死成一份字面清单——T-04 实现时以该节为准；若实现中发现判据不可机检，回来改本节而不是放松门禁（记 `change.md` §14）。
