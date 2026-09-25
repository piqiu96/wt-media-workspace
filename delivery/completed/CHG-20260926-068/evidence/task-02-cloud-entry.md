# T-02 证据：cloud `scripts/verify/test-control.sh` ＋ `scripts/test.sh` 接线

- CHG: `CHG-20260926-068`
- Task: T-02（`change.md` §8）
- 日期: 2026-09-26

## 1. 新建 `scripts/verify/test-control.sh`（模式 755）

**cloud `scripts/verify/` 的第一个真实文件**（原只有 `.gitkeep`）。判据与 desktop 的 `tests/control.test.sh` **同类同数**：
12 条／六类（存在＋被跟踪、index `100755`、磁盘执行位、**直接调用** `help` 退 0、四个动词逐行锚定、未知动词退 2 且 stdout 空／usage 在 stderr）。
只跑 `help` 与未知动词，**不建不启不连**（不需要 go、数据库或端口）。

cloud 的 `help` 读数：`exit=0`、stdout 331 B、stderr 0 B；四个动词在描述行上，逐行锚定四条全中。

## 2. 接线：`scripts/test.sh` 末尾一行

```
"$ROOT_DIR/scripts/verify/test-control.sh"
```

**直接调用**（不写 `bash`）——这正是本 CHG 的主题，写成 `bash` 就等于把判据又和缺陷错开一格。

**输出前缀是硬约束**：`scripts/verify_m3_acceptance.py:1621-1632` 用 `^ok\s`、`^FAIL.*$`、
`Test Files\s+(\d+) passed \((\d+)\)`、`Tests\s+(\d+) passed \((\d+)\)` 解析 `scripts/test.sh` 的日志。
本脚本**每一行**都以 `[control] ` 开头。

## 3. 前缀到底承不承重（`artifacts/t02-cloud-prefix-control.out`）

量法：把门禁**自己的两条正则**套在两段文本上——(a) 真实日志、(b) 同一日志**剥掉行首 `[control] `**。

| 输入 | 写法 | `^ok\s` | `^FAIL` | 10.1 判 |
| --- | --- | --- | --- | --- |
| 合成两行（比较器的阳性对照） | `ok  \t…` / `FAIL\t…` | 1 | 1 | 比较器**能**触发 ✓ |
| green 日志 | 原样 | 56 | 0 | PASS |
| green 日志 | 剥前缀 | 56 | 0 | PASS（**delta 0**） |
| **red 日志**（变异 ①） | 原样 | 0 | 0 | FAIL |
| **red 日志** | 剥前缀 | 0 | **9** | FAIL（**delta +9**） |

**如实记一次自踩**：第一次只拿 green 日志做对照，读到 `delta +0`，于是脚本自己打印「前缀是承重的」——
那是**空转**：绿跑根本不写 `FAIL` 行，两边都为 0 说明不了任何事。改用 red 日志（变异 ① 的输出）后，
剥掉前缀会往 10.1 会解析的日志里注入 **9 行**伪 `FAIL`，判据才有分母。两段读数都留在产物里。

## 4. 两处变异（`artifacts/t02-cloud-mutations.out`，各还原并复跑取绿）

| 变异 | 手法 | 读数 |
| --- | --- | --- |
| ① 磁盘执行位 | `chmod -x bin/control.sh` | **4 passed／8 failed**（判据 3／4／5×4／6 的第二条） |
| ② 只关 index | `git update-index --chmod=-x`（磁盘仍 `-rwxr-xr-x`） | **11 passed／恰 1 failed = 判据 2** |

与 desktop 的两处变异**同数同分布**（8／1）⇒ 同一组判据在两仓的判别力一致。
**如实记**：cloud 的入口**本来就带执行位**，此处没有「真实缺陷先红」可报——判别力的证据只有这两处变异，
不冒充先红。还原后 `git ls-files -s` 复读 `100755`、检查复跑 `12 passed, 0 failed`。

## 5. `scripts/test.sh` 全跑（取在最后一次改动之后，`artifacts/t02-cloud-test-sh.out`）

`exit=0`：`go test ./...` **`^ok\s` 56 行、`^FAIL` 0 行**；vitest `Test Files 25 passed (25)`／`Tests 166 passed (166)`；
`[control]` 13 行、**12 passed／0 failed**。

**门禁解析面的回归复证**：把上面四条正则套回这份新日志，四类读数与接线前**同形**
（`^ok\s` 56、`^FAIL` 0、两条 vitest 匹配都在），且 `[control]` 的 13 行**对 `^ok\s`／`^FAIL` 各贡献 0 行**（实测，非推断）。

## 6. `scripts/README.md`

- Verification 行补 `verify/test-control.sh`；
- 「两个子目录各只有一个 `.gitkeep`」这句**已不成立**，改写为「`scripts/verify/` 有第一个真实文件，
  `scripts/dev/` 仍只有 `.gitkeep`」，并写明前缀的理由与「不启停任何东西」。

## 7. 如实记

- 本检查断言的是**入口属性**，不覆盖 `start/stop/restart/status` 的**行为**——那是 T-05 的 16 格真跑。
- cloud `internal/architecture/boundary_test.go` 的删除（D-03，用户操作）**全程未触碰**，
  它在 `git status` 里仍显示为 ` D`。
