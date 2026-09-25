# T-06 收尾（workspace）：归档、LEDGER、快照、扫描、对账、门禁

只记事实与可重跑的命令。读数原始输出进同目录 `artifacts/`。

## 1. 归档

```
git mv delivery/active/CHG-20260926-068 delivery/completed/CHG-20260926-068
```

`git status --porcelain` 得 **41 条 rename**（40 条纯 `R` ＋ 1 条 `RM`＝`change.md` 移动后又改写状态词）。
`delivery/active/` 移后只剩 `.gitkeep`。**归档与记录改动在同一次 commit 内落地**，git 历史里不存在
「先归档、再回改」的中间态（沿用 CHG-067 收尾 `5622622` 的做法）。

## 2. 记录内的三处订正

| 位置 | 订正 | 依据 |
| --- | --- | --- |
| §8 T-06 行 | `git mv` **49 条 rename → 41 条** | 计划期写的是 49（照抄 CHG-067 收尾的读数），实测 41 |
| §8 T-01／T-02／T-03 行 | 各补上运行仓提交号 `ffe089d`／`339cc15`／`095196e` | 逐仓 `git log` 实测 |
| §13 最后一条 | desktop 的 T-01 提交 `9aca4f2` → **`ffe089d`** | `9aca4f2` 是 workspace 的记录提交，不是 desktop 的 |

三处同源：**计划期/前一个 CHG 的数字不能当下一个 CHG 的读数用**（`计数必须当场量`）。

## 3. `MASTER` §3 读数列

量法：直接 `import` 门禁自己的 `status_word()`（`scripts/verify_product_master_alignment.py:275`），
不重新推导。读数与分母、以及首测/终测差一处的原因，原始输出落 `artifacts/t06-status-words.out`。

终测：活列 **19**（`SUPERSEDED` 9／`PLANNED` 3／`DISCUSSION` 7，`IMPLEMENTING` 归 0）；
归档记录 **43**（`DONE` **33**／`IMPLEMENTING` 1／`VERIFYING` 1／`CLOSED` 2／`HANDOFF` 2／`IN_PROGRESS` 4）；
归档列 **35**；闭合式 35＋2＋2＋4＝**43** ✓；总分母 62。

**首测曾自相矛盾**（归档 `DONE` 32／归档 `IMPLEMENTING` 2／归档列 35）：因为刚移动的 `change.md`
自己还写着 `- Status: IMPLEMENTING`，被读成归档列里的 `IMPLEMENTING`。⇒ **归档动作与状态词改写必须都落定后再测**。

## 4. 快照

```
python3 -B -X pycache_prefix=/tmp/pyc-none scripts/prepare_ai_workspace.py --no-active
```

`exit=0`；`.ai/CURRENT_CONTEXT.md` 变为 `Active CHG: none`／`Status: NONE`、无 Change-file 行、无 Affected Repositories。

## 5. LEDGER

表行 `| CHG-20260926-068 | … | IMPLEMENTING | wt-media-workspace |` **移出**（表保留表头），
在其位置写入关闭段（`DONE` + Level S + 四仓 + 四条最值得单记的实测 + 如实登记的四处 + 计数 + 扫描读数）。
段落**不内联**扫描的分母（本段自身新增一条链接，写进正文就会改掉它自己的分母——沿用 CHG-065 的口径）。

**一处中间态实测**：快照先改成 `--no-active`、而 LEDGER 表行仍在时，
`verify_delivery_governance.py` 与 `verify_agent_entry.py` **各报 2 条 ERROR**
（`current context and ledger disagree: none != CHG-20260926-068`／`ledger references missing active CHG`），
两条都在表行移出后**同时归零**。⇒ 归档动作、快照重生成、表行移出三者必须在**同一次提交**内落地。

## 6. 两遍失效指针扫描

原始输出落 `artifacts/t06-sweep.out`（含分母、逐条命中、两处阳性对照与两处反向对照）。

- **第一遍（字符串面，模式＝归档前的完整旧路径）**：分母 **999** 已跟踪 ＋ **0** 未跟踪
  （取在 `git add -A` 之后。**读数必须取在 `git add -A` 之后**：`git ls-files`／`git grep` 只看得见
  已跟踪与已暂存文件，未暂存的新文件不在被扫集合里，分母会小一号）。
  **归档目录之外 0 行**；三个运行仓 `git -C <repo> grep` 亦 **0** 行；归档目录内 **32 行**
  （原始捕获 25 ＋ 记录正文 5 ＋ 本 Task 自写产物 2）全是过去时叙述或对当次 `porcelain` 的原样引用 ⇒ **判留**
  （先例：CHG-067 自己的归档记录同样留着它的旧 active 路径）。
  阳性对照锚**不可变基线** `d8d7ba4`（归档前那棵树）命中 **32** 行，与工作树**同数**——两侧分母一致时，
  这个 32 才是可比的：基线 32 ＝ 生成物快照 3 ＋ 归档内 29，工作树 32 ＝ **同一批 29 行只换了路径前缀**
  （`delivery/active/…` → `delivery/completed/…`，逐文件命中数一一对应：**这是改名不是新增**）
  ＋ 本 Task 自写 3 行（`t06-repo-reconcile.out` 2 ＋ `task-06-closeout.md` 1）。
  **自指单列**：本产物复述了被扫的模式，单列计数、不入上述结论。
- **第二遍（链接面）**：分母 **507** 篇 `*.md`／**128** 条站内相对链接（跳过代码跨越**与行内代码**，
  行内代码区分度双向对照：同一处死链写在散文里报出、写进行内代码不报）。**未解析 6 条**，
  与 CHG-065 T-09／CHG-066 T-06／CHG-067 T-07 三次读数**逐条相同**（同一批、同一成因：跨仓链接少一级 `..`），
  **全部在已归档记录里**，按 `MASTER:132`「归档记录保持原样、不回改」只登记。
   **指向本 CHG 的链接 1 条、已解析、未解析 0**。归因对照：同一解析器对 `CHG-20260926-067` 读到 1 条且已解析
  ⇒ 证明「本 CHG 0 条」不是因为扫描器认不出本 CHG 的链接形状。

  **分母两处坑（本 Task 新踩）**：①`git ls-files` 默认把非 ASCII 路径**八进制转义**成
  `"\347\244…"`（本仓已跟踪路径里这样的有 **18** 条）——**行数不变**（`wc -l` 两种口径都读 507），
  但**按名字打不开**：实测默认口径下 507 篇 `*.md` 只有 **496** 篇 `os.path.exists` 为真，
  扫描器会把那 **11** 篇连其链接一起静默丢掉（不修口径时本扫描只读到 496 篇），
  改用 `-c core.quotePath=false` ＋ `-z` 后 **507／507** 全可开。教训：**分母错了不会有报错**，
  只有与另一条独立路径（这里 `wc -l`）对不上才会露头，且要先分清是「行数」还是「可打开数」。
  ②扫描产物落在被扫目录里会喂自己的分母（沿用 CHG-067 §14 第 28 项）。

## 7. 四仓对账

原始输出落 `artifacts/t06-repo-reconcile.out`。锚 T-00 记录的基线：
workspace `5622622`／cloud `e2ba4d8`／agent `aa95332`／desktop `9ba5486`。

- 改动路径逐条归属 §5：**越界 0**。
- 口径教训：**不能只跑 `git status --porcelain`**——desktop 工作树现在是干净的，可它相对基线有 4 条改动
  （早已进提交）。必须跑 `git diff --name-status <基线>`，否则「零脏项」会被读成「零改动」。
- 两条脏项（cloud ` D internal/architecture/boundary_test.go`、agent ` M AGENT-INDEX.md`）
  **先于本 CHG 存在、全程未触碰**（T-00 基线已记）。
- 端口值：裸命中 **99 行**，按文件归类后**全部**落在本 CHG 自己的归档记录内
  （`t05-workspace-verbs.out` 32／`t03-agent-test-sh.out` 14／…，记的是运行实例的 `url=` 与健康端点），
  **归档目录之外 0 行** ⇒ 性质是「对端口值的引用」，不是「端口值的改动」；四仓运行代码／配置／脚本端口值改动 **0**。
  过滤器有阳性对照（CHG-067 的 desktop 提交 `9ba5486` 命中 2 行）。
- 业务代码：本 CHG 自己的改动里 `.go`／`.py`／`.rs`／`.vue`／`.ts` **0** 条；唯一 `.go` 路径是上面那条先于本 CHG 的既有删除（D-03 归用户）。

## 8. 门禁与套件

原始输出落 `artifacts/t06-gate-final.out`（含分母、逐条退出码、以及本产物写完前的**复跑确认**）。
`Ran 106 / OK`（基线 101，+5 为 T-04 新增用例）。读数**取在最后一次改动之后**。

## 9. 记录体量

原始输出落 `artifacts/t06-record-size.out`（v5 每 Task 增量；锚＝上一 Task 提交 `d8d7ba4` 的 blob）。
本 Task：`change.md` **+4944**、`checkpoint.md` **+3968**、本文件 **+8804**（界 5120／4096／9216，均**界内**）。
全 CHG 唯一的越界在 **T-00 激活当期**（+176.3%）——那一期一次性写完整份记录，属结构性越界
（同 CHG-067 T-00 先例，读数比先例小一档）；**T-01 起每期均在界内**（实测 +971／+1341／+1274／+924／+3146／+1684）。
⇒ 勘误：本文件先前写的「`change.md` 从 T-00 起就在界外」**不成立**——判据卡的是**每 Task 增量**、不是总量，
T-00 的总量一次成型与 AC-07 的 PASS 不矛盾；此处按实测改写（`counts must be measured`）。

## 10. 边界（本 Task 未做）

- 不动三个运行仓的任何文件（本 Task 对三仓**零读写**，逐仓对账见第 7 节）。
- 不杀比特浏览器（pid 13947，第三方）。
- 不新增门禁、不改 `AGENT-INDEX.md` §12 的口径。
- 不自动开始下一个 CHG。
