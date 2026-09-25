# Evidence: T-04 修 skill 第 1 步指针并分发生成副本

- CHG: `CHG-20260925-062`
- Task: `T-04`
- Date: 2026-09-25
- Type: command
- Status: PASS

## Purpose

证明两个 workspace skill 的第 1 步确实指向了已失效的「Root `AGENTS.md`」（先红），
改源后生成副本**真的随之改变**（正向 resolve），并且这次同步**没有脏化**三个运行时仓库。

## Method

```bash
grep -rn 'Root `AGENTS.md`' skills/ .claude/skills .codex/skills ../.claude/skills ../.codex/skills
# 改两个源文件的第 1 步
python3 -B -X pycache_prefix=/tmp/pyc-none scripts/sync_skills.py check   # 阳性对照：应当红
python3 -B -X pycache_prefix=/tmp/pyc-none scripts/sync_skills.py sync
python3 -B -X pycache_prefix=/tmp/pyc-none scripts/sync_skills.py check
python3 -B -X pycache_prefix=/tmp/pyc-none scripts/verify_skills.py
git -C ../wt-media-{cloud,agent,desktop} status --porcelain -uall
```

原始输出：`artifacts/t04-red-agents-pointer.out`、`artifacts/t04-check-red-after-source-edit.out`、
`artifacts/t04-sync.out`。

## Expected / Actual

**① 第 1 步的失效指针。**

- 期望（先红）：源文件与四个副本目录都命中「root `AGENTS.md`」。
- 实际：命中，共 **10** 处 = 本仓 **6**（2 个源 + `.claude` 2 + `.codex` 2）+ 执行根 **4**
  （`../.claude` 2 + `../.codex` 2）。

  > **我自己的一次假阴性（登记）**：首次 grep 用的是 `'Root \`AGENTS.md\`'`（**大写 R**），
  > 只命中 `executing-wt-media-change`，得 **5** 处（`artifacts/t04-red-agents-pointer.out` 逐行可见）。
  > `planning-wt-media-delivery` 写的是小写 `root`，被整个漏掉。改用 `grep -i` 后 **10** 处齐现。
  > **若不做这一步，我会漏修一半。**

  > **同一份记录里我把这个数写错，已改正（登记）**：本节初稿写「命中 **8** 处」，并附
  > 「2 个 skill × {源, `.claude`, `.codex`, 执行根 `.claude`, 执行根 `.codex`}」——该算式得 10，
  > 与 8 自相矛盾。复核查出 8 是**另一个分母**：`sync_skills.py check` 的 out-of-date 行数
  > （4 个落点 × 2 个 skill），被我与 grep 命中数混为一谈。
  > **精确值改以「从 git 重建」为准**（不靠记忆也不靠旧输出）：
  > `git show HEAD~1:<file> | grep -ci 'root \`AGENTS.md\`'` 对本仓 6 个文件逐个得 1、合计 **6**，
  > 加执行根 4 处 = **10**。本节与 T-04 的 commit message 均已按 10 改正。

- 修后复扫（大小写不敏感，分母 = 5 个目录）：**0 条命中**。

**② 阳性对照：这个检查能不能红。** 改完源、尚未同步时跑 `sync_skills.py check`：

```text
root/codex: out of date …/executing-wt-media-change/SKILL.md
root/codex: out of date …/planning-wt-media-delivery/SKILL.md
root/claude: …  workspace/codex: …  workspace/claude: …
exit=1
```

**恰好 8 行**（= 4 个落点 × 2 个 skill；**注意这是 `check` 的分母，与 ① 的 grep 命中数 10 不是同一个数**——
`check` 只数副本，不数 `skills/` 下的源），且**只有 root 与 workspace 两个落点**——与
`config/skills-distribution.yaml` 里 `workspace` 分组的投递面逐一对上
（cloud/agent/desktop 只收 `common` 分组，不含这两个 skill）。
即：`check` 确实能红，且红出来的范围正是我判定的范围。

**③ 同步后副本真的变了（正向 resolve，不能只信 check 绿）。**

| 副本 | 第 1 步现在的内容 |
| --- | --- |
| `.claude/skills/executing-wt-media-change/SKILL.md:17` | ``1. Root `AGENT-INDEX.md` — the governance text and routing authority. `AGENTS.md` and `CLAUDE.md` are thin parallel pointers to it, not the text itself.`` |
| `.codex/skills/executing-wt-media-change/SKILL.md:17` | 同上 |
| `.claude/skills/planning-wt-media-delivery/SKILL.md:17` | ``1. root `AGENT-INDEX.md` (the governance text; `AGENTS.md`/`CLAUDE.md` are thin pointers to it) and `wt-media-workspace/.ai/CURRENT_CONTEXT.md`;`` |
| `../.claude/skills/planning-wt-media-delivery/SKILL.md:17` | 同上 |

`sync_skills.py check` → `skill outputs are up to date`；`verify_skills.py` → `verified 10 skill source files`。

**④ 三仓是否被脏化。** `sync` 的控制台输出列了 10 个 target（含 cloud/agent/desktop），
但内容只有 root 与 workspace 变——因为三仓只收 `common` 分组。实测三仓的
`.claude/skills` / `.codex/skills` **均未出现在 `git status` 里**。

## 三仓的既有脏文件（**不是本 CHG 造成的，如实登记**）

`git status` 显示 desktop 与 cloud 并非全空，但 **mtime 归属明确**，全部早于本会话：

| 仓库 | 内容 | mtime | 判定 |
| --- | --- | --- | --- |
| `wt-media-desktop` | `src-tauri/src/` 下 **13** 个 `.rs` | 11 个为 **2026-09-24 22:32:20**，另 3 个为 **2026-09-25 09:57 / 10:34 / 10:38** | **先于本会话**（本会话约 13:5x 起，本 CHG 的写入为 14:08–14:09） |
| `wt-media-cloud` | 未跟踪的 `dump.rdb` | **2026-09-24 17:19:16** | 先于本会话；Redis 运行时转储 |
| `wt-media-agent` | 无 | — | 干净 |

本 CHG 对三仓**零读写**（`sync` 的写入面不含三仓，见上）。**但因此不能写「三仓工作区全空」**——
见 `change.md` §10 AC-12 按实测改写后的措辞。

## Follow-Up

- desktop 那 13 个 `.rs` 与 cloud 的 `dump.rdb` 属**他人/他任务的在途改动**，本 CHG 不碰、不提交、
  不清理。若后续 CHG 要以它们为基线，需先确认归属。
- `executing-wt-media-change/SKILL.md` 的 Authority Order 第 6 项仍写「Affected repository
  `AGENTS.md` files」。按新模型仓内权威是各仓自己的 `AGENT-INDEX.md`。**本次只改第 1 项、未改第 6 项**
  （用户裁定的范围是「第 1 步读取指针」），**登记在此**：第 6 项不算错（层三本来就读该仓的
  `AGENT-INDEX.md`、`AGENTS.md`、`CLAUDE.md`），但措辞可更精确。
