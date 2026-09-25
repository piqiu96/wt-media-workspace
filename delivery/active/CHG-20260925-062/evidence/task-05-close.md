# Evidence: T-05 收尾——验收矩阵、门禁读数与归档后指针扫描

- CHG: `CHG-20260925-062`
- Task: `T-05`
- Date: 2026-09-25
- Type: command
- Status: PASS

## Purpose

为 §10 的 12 条验收判据逐条给出可复核读数，并证明归档后旧指针真的失效、新指针真的可达。
本文件同时登记 T-05 复核出的**两处我自己写错的计数**及其更正。

## Method

```bash
python3 -B -X pycache_prefix=/tmp/pyc-none scripts/verify_delivery_governance.py
python3 -B -X pycache_prefix=/tmp/pyc-none scripts/verify_agent_entry.py
python3 -B -X pycache_prefix=/tmp/pyc-none scripts/verify_skills.py
python3 -B -X pycache_prefix=/tmp/pyc-none scripts/sync_skills.py check
python3 -B -X pycache_prefix=/tmp/pyc-none -m unittest discover -s tests -q

# 基线：必须在「兄弟位」建 worktree，不能建在 /tmp —— 见下「测量的一个坑」
git worktree add --detach ../wt-baseline840ba38-tmp 840ba38
# 漂移扫描（两遍，判据不同）
grep -rn "第 13 节" docs/                     # 旧串扫描，分母 = docs/ 下 66 个 .md
grep -rni 'root `AGENT-INDEX.md`' skills/ .claude/skills .codex/skills ../.claude/skills ../.codex/skills
# 正向 resolve：读链接目标是否真存在
```

原始输出：`artifacts/t05-verify_*.out`、`t05-sync-check.out`、`t05-unittest.out`、
`t05-unittest-baseline-diff.out`、`t05-unittest-baseline-placement.out`、`t05-sweep-*.out`。

## AC 逐条判据

| AC | 判据（命令/读数） | 判定 |
|---|---|---|
| AC-01 | `AGENT-INDEX.md` 178 行 12 节；`AGENTS.md` **30 行 2 节**（权威源 + 最小硬约束）、`CLAUDE.md` 91 行 8 节。**判别性判据**：`AGENT-INDEX.md` 的 12 个 `##` 标题（本仓库定位 / 红线 / 知识地图 / 读取顺序与上下文加载 / 关联仓库与职责边界 / 需求路由 / 端到端工作流 / 交付治理 / 变更规则 / Agent 入口与执行快照 / 多 Agent 并行 / 校验）**无一**出现在两个入口文件里。 | **PASS（判据收窄，见下）** |
| AC-02 | 正向 resolve：`AGENTS.md` → `AGENT-INDEX.md` ✓；`CLAUDE.md` → `AGENT-INDEX.md` ✓、`README.md` ✓、`docs/engineering/specs/agent-workspace-conventions.md` ✓。**4/4 全部存在**，无 MISS。 | PASS |
| AC-03 | 修前 `grep -rn "第 13 节" docs/` 命中 **2**（见 t03 证据）；现在 **0**（分母 66 个 .md）。正向：`AGENT-INDEX.md:143 ## 10. Agent 入口与执行快照` 与规范文字逐字吻合。 | PASS |
| AC-04 | 实跑 `verify_agent_entry.py` → `0 warning(s) need review`；§10 第 133 行现写「绿，**0 WARN**（快照 1923 字符）」。读数与表一致。 | PASS |
| AC-05 | `grep -rni 'root \`AGENTS.md\`'`（**大小写不敏感**，分母 5 个目录）→ **0**；`sync_skills.py check` → `skill outputs are up to date`；`verify_skills.py` → `verified 10 skill source files`。 | PASS |
| AC-06 | 变异式对照（T-04 已做）：改源未同步时 `check` **红 8 行**（exit 1），同步后绿；并逐文件读副本确认第 1 步文本已变。阳性对照 `root \`AGENT-INDEX.md\`` 现在 **10** 处命中（2 skill × 5 目录）。 | PASS |
| AC-07 | 基线以 **840ba38 的兄弟位 worktree** 实测：`Ran 73 tests / FAILED (failures=4)`；当前同为 `Ran 73 tests / FAILED (failures=4)`；红项名字 **diff 为空**（逐条同名）。 | PASS |
| AC-08 | `verify_delivery_governance.py` → `ok. Active CHG: CHG-20260925-062`；`verify_agent_entry.py` → `ok. 0 warning(s)`；`verify_skills.py` → `verified 10`。三者 exit 0。 | PASS |
| AC-09 | 快照 `Active CHG: CHG-20260925-062` / `Status: IMPLEMENTING`；LEDGER 表行 `\| CHG-20260925-062 \| … \| IMPLEMENTING \| wt-media-workspace \|`（裸 id）；`delivery/active/` 仅 `CHG-20260925-062`。三者互指一致。 | PASS |
| AC-10 | `git status --porcelain -uall` 仅 7 个未跟踪的 `t05-*` 产物（本任务产物），无越界文件；`2026-09-24-m4-m5-cloud-content-production.md` 与 HEAD 的 `git diff` **0 行**（逐字一致）。 | PASS |
| AC-11 | `scripts/verify_agent_entry.py` 在 `840ba38..HEAD` 全程 **diff 0 行**（未动）；`check_entry_drift` 仍在 `:240`，`:241` 的 docstring 仍写 "forbidden by AGENTS.md"；`AGENT-INDEX.md` §12 仍**不含** `verify_delivery_governance.py`（命中 0）。 | PASS |
| AC-12 | 三仓 `.claude/skills` / `.codex/skills` 在本仓 status 中 **0 条**；desktop 13 个 `.rs`、cloud `dump.rdb` 逐个 `stat`，mtime 全部早于本会话首个证据文件（`checkpoint.md` = 2026-09-25 14:05:43）。 | PASS |

### AC-01 判据为什么收窄（如实登记）

原措辞「两个入口文件不含正文副本」**过强**，收尾复核发现一处局部重复：

- `CLAUDE.md` 的 `## 高频红线`（9 行）是 `AGENT-INDEX.md` §2 红线（**8** 条，11 行）里**取 4 条**的
  改写复述。该小节自带「以下四条最容易出错，**完整规则与例外见 `AGENT-INDEX.md`**」，是
  有意的「常见错误速查」，**不是**正文副本；但客观上是正文一部分的第二份文本，
  存在与本次重构同源的漂移风险。
- 按 §5「不还原、不改写那次重构的任何内容」与用户裁定的「修两处该修的」范围，**本次不改**，
  §14 遗留小节登记。

故 AC-01 的判定改以**可判别的判据**为准：正文的 12 个**小节标题**无一进入入口文件，
两文件不含职责边界表 / 需求路由表 / 上下文加载规则正文。**局部复述一项单列登记，不计入 PASS 的掩盖。**

### AC-12 的判据改成逐文件 `stat`（因两处计数写错）

收尾复核出我自己在 T-04 记录里写错的**两个数**，都已更正：

1. **grep 命中数写成 8，实为 10。** 8 是**另一个分母**——`sync_skills.py check` 的 out-of-date
   行数（4 个落点 × 2 个 skill），被我与 grep 命中数混为一谈。并由 `git show HEAD~1:<file> |
   grep -ci` 逐文件重建证实：本仓 6 + 执行根 4 = **10**。（该错误同时出现在 T-04 的 commit
   message 里，已 `--amend` 改正；工作区文件里的同处已在本次更正。）
2. **desktop 的 mtime 分组写成「11 + 3」，实为「10 + 3」。** 11+3=14 与本行自己的总数 13 自相矛盾。
   逐文件 `stat` 重测：22:32:20 ×**10**，另 3 个为 09:57:13 / 10:34:48 / 10:38:13。

**两次错误同源：凭印象写数、没逐个量**，且两次都与同一行里另一个已量准的数字冲突
（10 与算式冲突；11+3 与总数 13 冲突）。**所以 AC-12 的判据从「数一下几个文件」改成
「逐文件 `stat` 归属」**——数个数正是出错的那一步。

## 测量的一个坑（会让人误判回归）

基线**不能**建在 `/tmp`：同名 commit 在 `/tmp` 位跑出 `Ran 69 tests / FAILED (failures=2, skipped=3)`，
看着像「本 CHG 把红项从 2 变成 4」。**成因**：`tests/test_skill_paths_resolve.py:31`
`EXECUTION_ROOT = ROOT.parent`，而其 `setUpClass` 在 `GROUP_ROOTS` 里任一仓目录不存在时抛
`SkipTest`——`/tmp` 下没有三个运行仓兄弟目录，于是 `SkillPathsResolveTests` 4 条用例整体不执行、
收敛成 1 条 `setUpClass` 跳过项。**基线必须建在与主仓同层的兄弟位**（`EXECUTION_ROOT` 下四个仓
齐备），才是可比读数：**73 测试 / 4 红**。两处读数都留在
`artifacts/t05-unittest-baseline-placement.out`。

## Follow-Up

- `CLAUDE.md` 的 `## 高频红线` 与 `AGENT-INDEX.md` §2 的局部重复（4/8 条）需独立 CHG 处置；
  本 CHG 只登记。
- 两处临时 worktree（`../wt-baseline840ba38-tmp`、`/tmp/wt-base-840ba38`）已 `worktree remove` +
  `prune` 清理，`git worktree list` 只剩主仓，外层 `wt-media/` 无残留。
