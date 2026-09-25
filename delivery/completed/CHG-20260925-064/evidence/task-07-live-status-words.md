# T-07 evidence — 活记录状态词就地改写

日期：2026-09-25
Task：T-07（依赖 T-06）

## 1. 两遍量测（同一脚本、同一分母）

| | 活记录（20 篇） | 归档记录（38 篇） |
|---|---|---|
| 改前 | `{IN_PROGRESS:1, PLANNED:3, SUPERSEDED:8, DISCUSSION:7, IMPLEMENTING:1}` | `{DONE:28, IN_PROGRESS:4, CLOSED:2, HANDOFF:2, VERIFYING:1, IMPLEMENTING:1}` |
| 改后 | `{SUPERSEDED:9, PLANNED:3, DISCUSSION:7, IMPLEMENTING:1}` | **不变** |

分母与取法：`delivery/planned/CHG-*/change.md` 19 ＋ `delivery/active/CHG-*/change.md` 1 ＝ 20；
`delivery/completed/CHG-*/change.md` 38。词由 `verify_product_master_alignment.py::status_word()` 逐文件提取
（同一函数即门禁用的那个，故「量出来的」与「门禁认的」不会分叉）。

**改前活记录里不在 §3 表中的词恰有 1 个**：`IN_PROGRESS`（`CHG-20260723-023`）。
**改后活记录 20 篇全部落在 §3 的六个词内**，一个不剩。归档记录仍有 8 处不在表中
（`IN_PROGRESS` 4、`CLOSED` 2、`HANDOFF` 2）——`MASTER` §3 的历史词汇行已声明归档记录保持原样。

## 2. `CHG-20260723-023`：为什么是 `SUPERSEDED` 而不是 `DONE`／`PLANNED`

这是一次**内容判断**（T-05 明确把它留给 T-07），依据是两个互相独立的已归档记录：

1. `delivery/completed/CHG-20260723-025/change.md:1` 的标题就是
   **「CHG-20260723-025：M2-B1 浏览器窗口扫描与 Diff 只读闭环」**——与 023 的
   「M2-B1 浏览器窗口扫描与Diff基线」是同一个 M2-B1 标签；
2. `delivery/completed/CHG-20260725-031/evidence/m2-b-closure.md:8` 在 M2-B 收口矩阵里把
   **B1 归给 025**（`B1：delivery/completed/CHG-20260723-025`）。

023 的三项 Task 都被别的 CHG 交付：Task 1／2 → 025（只读闭环），Task 3「确认同步窗口到 Cloud 镜像」
→ `CHG-20260723-026`（收口矩阵 B2「窗口同步应用、恢复与授权闭环」），主账号确认部分 →
`CHG-20260723-022`（其 `evidence/task-3-bitbrowser-main-identity.md` 是 023 自己写的 inherited evidence）。

023 自身：从未进过 `delivery/active/`、目录下**只有 `change.md`、无 `evidence/`**、mtime 停在 2026-07-23
（创建当天）。**不是** `DONE`（本记录从未收口、无验收矩阵），**不是** `PLANNED`（无可激活的剩余方向）——
`SUPERSEDED` 的定义句正是「已被后续工作取代，不再独立激活」。

`git diff` 该文件只有一行：

```text
-- Status: IN_PROGRESS
+- Status: SUPERSEDED
```

## 3. `planned/README.md` 两处

1. **`023` 那一条**由「正文保留 IN_PROGRESS 标记；状态整理不属于本次 M3 拆分范围，保留原文件」改写为：
   草案、从未激活、无 evidence，范围已由 022／025／026 交付，故 `SUPERSEDED`；并保留原句真正想守住的结论——
   **M2 的完成与否以 `M2-account-runtime.md` 与 031 的收口矩阵为准，与本记录无关**。
   原句的理由（「状态整理不属于本次 M3 拆分范围」）已过期，就地覆盖。
2. **M3 表的「状态」列加一段列说明**：该列写**程序进度**（做没做、由谁承载），不是记录自身的状态词；
   记录的状态词在各自 `change.md` 的 `Status:` 字段。这解开了表格与记录之间那处**看着像冲突、其实不同轴**
   的写法——例如 `045` 的表格行写「已实施，真实证据，由 CHG-052 承载」，而 `045/change.md` 写
   `- Status: DISCUSSION` 且正文自述「未开始运行时代码实施」。两者都真：前者说工作已由别处交付，
   后者说这份草案从未被激活。**本 Task 只让两个轴可分辨，不改判任何一份草案**——记录层要不要为这些
   草案补终态词是独立的治理裁定（§14 第 8 项）。

## 4. `MASTER` §3 读数的连带更新（本 Task 造成的失效）

T-05 把 §3 的读数列写成**实测值**，所以 T-07 改了活记录就必须跟着改，否则 §3 立刻变成过期读数：

| 位置 | 改前 | 改后 |
|---|---|---|
| `SUPERSEDED` 活记录列 | 8 | **9** |
| 历史词汇行的 `IN_PROGRESS` | 活记录 1 处、归档 4 处 | 活记录 **0** 处、归档 4 处 |
| 分母对账句 | 活列 19 ＋ 退役 `IN_PROGRESS` 1 ＝ 20 | 活列 **20**（退役词在活记录里已归零） |
| 历史词汇行的范围 | 「归档记录**与 `planned` 记录**保持原样，不回改」 | 「**归档记录**保持原样、不回改，**活记录一律改用上表的词**」 |

最后一条是本 Task 直接证伪的原句：T-07 就是改了 `planned` 记录。

## 5. 判据

| 判据 | 读数 |
|---|---|
| 活记录用词全部落在 §3 表内 | 20/20，改前 19/20（阳性对照：同一脚本对归档记录仍报出 8 处不在表内的词 ⇒ 扫描能咬住） |
| `git diff` 只改状态词一行 | 023 的 diff 为 `1 insertion, 1 deletion`，即 `- Status:` 那一行 |
| 六个静态门禁 | 全 `exit=0` |
| `unittest` | `Ran 79 tests` / `OK` |

## 6. 未覆盖

- **归档记录的 8 处退役词不动**（T-05 声明，§14 第 12 项登记 `HANDOFF` 的再分类待裁定）。
- **README 的「程序进度」列未改成词表**：它承载的是「由谁承载」这类词表装不下的信息，改成单词会丢信息。
  本 Task 只声明它的轴，未重写内容。
- **这些草案记录是否该补终态词**（`045`／`046`／`047`／`048`／`049`／`050`／`051` 七份）：属 §14 第 8 项，
  需用户裁定，T-07 不碰。
