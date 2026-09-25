# T-01 证据：workspace 脚本层分层

- CHG: `CHG-20260926-067`
- Task: T-01（`change.md` §8）
- 日期: 2026-09-26
- 锚: 开工前 workspace HEAD `30891c8`（T-00 的提交）

## 1. 本 Task 的改动文件

| 文件 | 改动 |
|---|---|
| `bin/control.sh` | `scripts/local-control.sh` **移动**而来；加 `restart`／`status`，保留 `start`／`stop`／`verify`／`help` |
| `scripts/test-control.sh` | `scripts/test-local-control.sh` **移动**而来；断言串同步，判据从 1 条扩到 4 条 |
| `scripts/dev/.gitkeep`、`scripts/verify/.gitkeep` | 新建（两个空目录的占位） |
| `scripts/README.md` | **首建**（本仓此前没有 `scripts/README.md`） |
| `AGENT-INDEX.md` | §3 知识地图加 `bin/` 行，`scripts/` 行加分类指针 |
| `scripts/m2b_local_acceptance.py` | 新增 `status` 动词：`cmd_status()` ＋ `choices` ＋ `main()` 分派 |
| `scripts/verify_delivery_governance.py` | `:140` `glob("*.py")` → `rglob("*.py")`（归 §5 Modify） |
| `tests/test_verify_delivery_governance.py` | `write_script` 支持子目录 ＋ 新增子目录用例 |

## 2. 归档只读门禁的扫描面：两臂活体对照

`scripts/verify/` 是新设落点，判据若用非递归 glob，落在其中的脚本会**静默滑出**扫描面。
同一个写归档的探针（`scripts/verify/probe-archive-write.py`）在两臂下的读数：

| 臂 | 门禁 | 分母 | 归档写 | 探针 | 文件 |
|---|---|---|---|---|---|
| A（改前，`glob`） | `exit=0` | `scanned 12 script(s)` | `0 write(s)` | **未点名** | `artifacts/t01-scan-surface-arm-a.out` |
| B（改后，`rglob`） | `exit=1` | `scanned 13 script(s)` | `1 write(s)` | `ERROR archive readonly: scripts/verify/probe-archive-write.py:8 writes under delivery/completed/ (ARCHIVE / 'probe.txt')` | `artifacts/t01-scan-surface-arm-b.out` |

分母 12 → 13 的**差 1 就是那个探针本身**；探针删除后分母回到 **12**（§6 的收尾读数），
与 F-03 记录的改前数一致——**扫描面变了，被扫对象没变**。

同一形态另有一条**持久用例**：`test_archive_write_from_subdirectory_script_is_reported`。
它的变异对照是把 `rglob` 换回 `glob`，实得 `AssertionError: Lists differ: [] != [...]`——
是**断言失败**而非 `ImportError`；还原后绿。

## 3. `test-control.sh` 的四条判据与五处变异

判据：usage 逐字、未知名词退出码 2 且 usage 落 stderr、`status` 端到端跑通、`bin/control.sh`
不含端口字面量。五处变异（`artifacts/t01-test-control-mutations.out`，先跑阴性臂证明基线是绿的）：

| 变异 | 结果 |
|---|---|
| usage 里删掉 `status` 行 | `FAIL: usage line missing:   status …` |
| `status` 分派被短路（不再指向 harness） | `FAIL: no cloud status line` |
| 未知名词退出码 `2 → 0` | `FAIL: unknown verb exit=0, want 2` |
| `control.sh` 里写进端口字面量 | `FAIL: bin/control.sh carries a port literal; …` |
| `HARNESS` 路径写错 | `FAIL: status exit=127, want 0 or 1` |

首轮跑时第一处变异**只给一个静默的 `exit=1`**（裸 `grep` 在 `set -e` 下不打印）。
已把逐行断言收进 `assert_line()`，让每条失败自报是哪一条；上表是改后的读数。

## 4. 一处早先写错的记录：`status` 的读数不是「环境没跑」

首稿的 artifact 标题写「此刻本地环境未运行」，而实测 `health=ok`。追下去发现**环境确实在跑**
（`lsof` 报 54420／8765 的 54456 各在 LISTEN，`curl` 两个端点各答 `{"status":"ok"}`），
而 `<root>/.local/m2b/pids` **不存在**——即它**不是经 harness 起的**。标题已改正，
并把独立探针一并落进 `artifacts/t01-control-status.out`。

这条读数的价值在于它**分开报**了两个互相独立的信号：

```text
cloud: pid=- alive=no health=ok url=…/api/v1/health
agent: pid=- alive=no health=ok url=…/healthz
exit=1
```

⇒ **`exit=1` 的含义是「本环境不是由 harness 起的」，不是「服务挂了」**（`change.md` §14 第 10 项）。
该运行实例**先于本 CHG 存在**，本 Task 未启停、未触碰。

## 5. 失效指针扫描

分母 **902** 个已跟踪文件（`git ls-files | wc -l`）。三种写法逐一枚举，不用一种推断其余：

| 形态 | 命中 | 处置 |
|---|---|---|
| `scripts/local-control\.sh` | 1（`docs/superpowers/plans/…:75`） | 判留，登记 §14 第 9 项 |
| 裸名 `local-control` | 2（上述 ＋ `docs/superpowers/specs/…:58`） | 同上 |
| `test-local-control` | **0** | — |
| **阳性对照**：`bin/control\.sh` | 7（`AGENT-INDEX.md`、`bin/control.sh`、本 CHG 记录） | 对照有命中 ⇒ 上面三个读数不是空转 |

`delivery/completed/` 下的命中是过去时叙述，按判留保留、不计入上表（已从扫描里排除）。

## 6. 六门禁与套件

读数落 `artifacts/t01-gate-after.out`（T-01 全部改动后）与 `artifacts/t01-gate-final.out`
（记录写完之后复跑）。要点：六个门禁 `exit=0`；`sync_skills.py check` `exit=0`；
`unittest discover -s tests -q` → `Ran 101 tests` / `OK`（激活前为 100，**+1 是本 Task 新增的子目录用例**）；
`bash scripts/test-control.sh` → `PASS`。

本 Task 的记录体量读数落 `artifacts/t01-record-size.out`——**不在此内联**：本文件的字节数会随写入而变，
内联就等于把「量出来的数」变成「写下来的数」。
