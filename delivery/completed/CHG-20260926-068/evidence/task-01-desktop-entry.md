# T-01 证据：desktop 入口执行位修复 ＋ `tests/control.test.sh`（含两处变异）

- CHG: `CHG-20260926-068`
- Task: T-01（`change.md` §8）
- 日期: 2026-09-26

## 1. 修复

`chmod +x bin/control.sh` ＋ `git add`。**字节内容零改动**（`git diff --cached --numstat` = `0/0`），
只有模式从 `100644` / `-rw-r--r--` 变成 `100755` / `-rwxr-xr-x`（5233 B 不变）。
`./bin/control.sh help`：**`exit=126` → `exit=0`**。读数落 `artifacts/t01-entry-fix-and-mutations.out`。

## 2. 机检 `tests/control.test.sh`（新建，模式 755）

被 `scripts/test.sh:57-60` 的 `for suite in tests/*.test.sh` 自动拾取，**不需要 cargo／不需要窗口**
（只跑 `help` 与未知动词，不触发任何启停）。12 条判据，六类：

| # | 判据 | 为什么这样写 |
| --- | --- | --- |
| 1 | 文件存在且**被 git 跟踪** | 没有 index 记录的文件在新克隆里不存在 |
| 2 | `git ls-files -s` 首字段 = **`100755`** | **判别力在变异 ② 里证明**（见下） |
| 3 | 磁盘有执行位 | 本机能不能跑 |
| 4 | **直接调用** `"$CONTROL" help` → `exit=0` | CHG-067 的臂全部经 `bash`，这正是它看不见缺陷的原因 |
| 5 | 四个动词各**逐行锚定**出现（`^  <verb>\b`） | 裸 `grep -F start` 会被 `restart` 那一行喂饱（假绿） |
| 6 | 未知动词 → `exit=2`、stdout 空、usage 在 stderr | 四仓同形的既有语义 |

**判据 4 不断言字面退出码**（原因见 §3）。

## 3. 实测到的一处新事实：同一缺陷在两个上下文里退出码不同

`./bin/control.sh help` 在未修时：**shell 外 126、`set -e` 脚本内 1**。矩阵实测（`artifacts/t01-entry-red.out` 末段）：

| shell 选项 | 捕获到的退出码 |
| --- | --- |
| 无 | `126` |
| `set -u` | `126` |
| `set -o pipefail` | `126` |
| **`set -e`** | **`1`** |
| **`set -eu`** | **`1`** |

只有 `set -e` 改读数，且它同时改脚本自身退出码（`set -e` 直跑 `exit=1`、无 `set -e` 直跑 `exit=126`）。
⇒ **任何在 `set -e` 套件里报「126」的地方都会与实际输出不符**；本 Task 的套件因此断言**属性**（`exit=0`）而非字面码。
bash 内部机制未进一步定位，此处只记可复现的矩阵。登记 §14 第 1 项。

## 4. 先红（真实缺陷，非合成变异）

修前跑新套件：**3 passed / 9 failed**，失败的正是这个缺陷的类别（判据 2、3、4、5×4、6 的两条；
判据 1 与「stdout 空」在 126 下仍为真故通过）。读数落 `artifacts/t01-entry-red.out`。

## 5. 两处变异（关掉判定后必须红，且要红在对的地方）

| 变异 | 手法 | 读数 | 证明了什么 |
| --- | --- | --- | --- |
| ① 磁盘执行位 | `chmod -x` | **8 failed**（判据 3／4／5×4／6 的第二条） | 磁盘那一侧承重 |
| ② 只关 index | `git update-index --chmod=-x`（磁盘仍 `-rwxr-xr-x`） | **恰 1 failed = 判据 2** | **判据 2 不是判据 3 的复述**：它单独抓「本地能跑、新克隆与 CI 跑不了」这一类；若只看磁盘，本仓本地恒绿 |

两次都还原并复跑取绿（`12 passed, 0 failed`）。

## 6. `scripts/test.sh` 全跑（取在最后一次改动之后）

落 `artifacts/t01-desktop-test-sh.out`：`cargo test` **372 passed; 0 failed; 5 ignored**、
`control.test.sh` **12 passed, 0 failed**、`release-versions.test.sh` **20 passed, 0 failed**，`exit=0`。
与 CHG-067 T-03 的 `372 passed; 0 failed; 5 ignored` **逐字相同**（新套件不改变 Rust 侧读数）。

## 7. 如实记

- **GitHub Actions 本身仍未在此运行**（沿用 CHG-067 T-03 的同一条登记）；本 Task 证明的是**本机**读数为绿。
- `tests/package-release-macos.test.sh` 仍是 **644**——它由 `scripts/test.sh` 以 `bash "$suite"` 调用、
  **没有被文档承诺直接调用**，故不在本判据内（`change.md` §7 第 1 项）。
