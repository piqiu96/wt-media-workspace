# Evidence: T-02 提交入口重构本体

- CHG: `CHG-20260925-062`
- Task: `T-02`
- Date: 2026-09-25
- Type: diff
- Status: PASS

## Purpose

把已在工作区停了一天多的入口重构提交入账，并证明提交内容与 §4 记录的实测差量一致、无夹带。

本次是**提交既有工作**，不是新写：内容一字未改，`git diff` 在提交前后完全相同。

## Method

```bash
git diff --check AGENT-INDEX.md AGENTS.md CLAUDE.md README.md     # 空白/冲突检查
git diff --numstat AGENT-INDEX.md AGENTS.md CLAUDE.md README.md   # 逐文件 +/−
git diff --name-only  AGENT-INDEX.md AGENTS.md CLAUDE.md README.md
```

## Expected

- `--check` 无输出（无行尾空白、无冲突标记）。
- `--numstat` 与 `change.md` §4 的实测表逐格一致：`AGENT-INDEX.md` +128/−59、
  `AGENTS.md` +21/−378、`CLAUDE.md` +80/−13、`README.md` +2/−1。
- 只有这 4 个 markdown 文件，无二进制、无脚本、无配置文件。

## Actual

- `git diff --check` → **无输出**（干净）。
- `git diff --numstat` → `128 59 AGENT-INDEX.md` / `21 378 AGENTS.md` / `80 13 CLAUDE.md` / `2 1 README.md`，
  与 §4 表逐格一致。
- `--name-only` → 恰好上述 4 个文件。
- 读 `AGENTS.md` 全文（30 行）：确认它是纯指针——只有权威源表、读取顺序、平级声明与最小硬约束，
  **不含**职责边界表、需求路由表或上下文加载规则正文。符合 §10 AC-01。

## 提交前做的两遍指针扫描（含阳性对照）

第一遍与第二遍用的是不同的判据，因为只做字符串扫描会给出假绿。

**第一遍：markdown 链接 resolve。** 5 个文件共 5 条相对链接，**0 条悬空**。
但这一遍太薄——这些文档的路径几乎都写在反引号里，不是链接，所以 5 条不足以说明问题。

**第二遍：反引号内的仓内路径 resolve。** 分母与结果：

| 文件 | MISS |
| --- | --- |
| `AGENT-INDEX.md` | 0 |
| `AGENTS.md` | 0 |
| `CLAUDE.md` | 0 |
| `README.md` | 1 |
| `agent-workspace-conventions.md` | 2 |

**阳性对照（证明这个扫描能命中）**：`AGENT-INDEX.md` → OK、`wt-media-cloud/README.md`（跨仓）→ OK、
`docs/engineering/specs/__nope__.md`（故意编的）→ MISS。三例双向往返正确。

**三处 MISS 逐条甄别，全部不是缺陷、且全部与本 CHG 无关**：

1. `README.md:50` 的 `changes/active`——出现在**否定句**里：
   「Do not create \`changes/active\`; use \`delivery/active/<change-id>/change.md\`」。
   **不存在正是这句话的意思。** 且该行不在本次 diff 的改动范围内。
2. `agent-workspace-conventions.md:134` 的 `wt-media-cloud/internal/modules/cloudagent/compatibility.go`
   ——出现在 §10「校验与已知红项」表里，原话是「**红 1 项**：… 在云仓已不存在」。
   实测该文件已移到 `../wt-media-cloud/internal/modules/cloudagent/service/compatibility.go`。
   表里那句作为**历史陈述**是真的（那个路径下确实没有了），改它属 CHG-053→059 遗留的红项处理，
   不在本 CHG 范围。**只登记。**
3. `agent-workspace-conventions.md` 的 `internal/runtime`——见 §10 中对
   `verify_agent_entry.py::check_entry_drift` 的解释，它是**举例的假想路径**，
   用来说明「标题里的路径也是主张」。不是路径主张。

## Follow-Up

- `agent-workspace-conventions.md` 整体作为 T-03 的对象（它同时含这次重构的文档化改动
  与 T-03 要修的三处陈旧引用，拆到两个提交反而更乱），故**不在本 T-02 提交内**。
  这一点与建 CHG 时 §8 的写法一致：T-02 就是「四文件一个 commit」。
