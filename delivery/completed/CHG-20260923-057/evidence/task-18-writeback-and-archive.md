# Evidence: T-18 基线回写、入口文档、验收补量与归档收尾

- CHG: `CHG-20260923-057`
- Task: `T-18`
- Date: 2026-09-24
- Type: diff | command | manual
- Status: PASS

## Purpose

把 T-02…T-21 已落地的实现事实**回写进稳定基线与两个运行仓的入口文档**，把 §10 里几行**已经变陈旧的
验收状态**按实测归位（含把一条原本登记为「未测」的 AC 真去量掉），把 §7 的 Q-07 关掉并新增 Q-08，
然后走 DONE Gate、归档、冷启动重生成快照，最后**主动扫**一遍失效指针。

本文件同时是 T-18 唯一的证据文件；AC-10 的两臂原始读数在本节 §3。

## Method

### 1. 基线回写（`wt-media-workspace`）

| 文件 | 改动 | 为什么必须改 |
|---|---|---|
| `docs/engineering/specs/2026-09-23-launch-engineering-optimization-program.md` §3 CHG-B | 新增 8 条「落定后的数字与口径」（20MB / 14 天 / 总量 400MB·100MB / `truncate=true original_size=<n>` / 三文件纯文本且不做 JSONL / Desktop 文件名单文件形态 / `operation_id` 只在进程内）+ 指向归档记录的链接 | 本节是这些数字的**权威落点**；此前它们只出现在 CHG-053 草案里，而那处自称「来自程序总纲」并不成立 |
| 同上 §文件头 | 状态行补「A、B 两阶段已于 2026-09-24 归档 `DONE`；C/D 仍待激活」；`承载 CHG` 行给 057 补链接与归档状态 | 原状态行只提 A，归档后为假 |
| `docs/engineering/architecture/…_V1.md` §5.8 | 在 `data/logs/versions` 目录树后补两段：三文件**开发态也落盘**（`<repo>/.local/logs/`，此前只走 stderr、一个文件也不写）、纯文本与限额与路由、以及 Desktop 的**另一棵树**与 100MB | 基线原文只画了装态的树；不补的话「dev 不落盘」仍是读得出来的结论 |
| 同上 §6.8 | 新增一段「**日志分属两棵树，且开发态也落盘**」 | 让「开发态不落盘不再是允许的省事做法」成为基线语句，而不是 CHG 里的临时约定 |

### 2. 入口文档回写（两个运行仓）

`wt-media-agent`（+5/−4，3 文件）：`DIRECTORY_MAP.md` 的 `runtime/paths.py` 行（dev/override 现在解析到日志文件）
与 `runtime/logging.py` 行（三文件路由 / 轮转保留 / 截断 / 脱敏 / `operation_id` 字段通道）；
`AGENT-INDEX.md` 新增「Agent 自己的日志」条目与一条路由行（并写明 Logger **只允许在 `bootstrap/app.py` 装配一次**）；
`AGENTS.md` 的 `runtime` 行。

`wt-media-desktop`（+11/−6，3 文件）：`DIRECTORY_MAP.md` 新增 `src-tauri/src/logging/` 行、`resources` 行补 `logging.*`、
命令行 `logging.rs` → `webview.rs`（命令名 `log_js_error` 不变）、**重写 drain 行**（缓冲仍是 200 行内存态、
存活期间普通输出**不产生记录**、`report_exit` 恰一条带末 20 行尾、读失败另一条、脱敏在 `logging/redact.rs`）；
`AGENT-INDEX.md` 新增「Desktop 自己的日志」条目、两条路由行与一条禁止（在 `logging/setup.rs` 之外装配日志、
或把 Agent stdout 全量转存进 `desktop.log`）；`AGENTS.md` 的 sidecar 行、新增 `logging/` 行与命令行。

**为什么必须改**：改前的 `drain` 行写的是「不落盘 / 不轮转 / 不脱敏」，T-15/T-16/T-17 落地后这句**已经变假**。

### 3. AC-10 补量：把「未测」真去测掉

原先 §10 的 AC-10 只登记了 T-06 的一处真泄漏与 T-08 的 health 响应面，`status` 响应体一路写着未测。
本次按两臂真机量掉。

```
bash /tmp/t18/ac10_arm.sh          # scratch 端口 18773 + 两个死端口 18794/18795
python3 /tmp/t18/assert_ac10.py
```

两臂的差别只有一处：**臂「修前」** 用 `b66d7f5^` 的 `bootstrap/cloud.py`（`git show` 取出、不碰工作树），
**臂「当前」** 用工作树。两臂的凭据都种在**该进程自己的** `WT_MEDIA_CLOUD_BASE_URL` 里
（`http://alice:$PASSWORD@127.0.0.1:$DEAD_CLOUD/api`，`PASSWORD=pw123456`），故「凭据进没进输出」
问的是这条链路本身，不是外部喂进去的串。

实际读数（`assert_ac10.py`，8 条，**ALL ASSERTIONS PASS**）：

| # | 断言 | 读数 |
|---|---|---|
| 1 | 对照：**修前**诊断包**确实**打出凭据（针打得中） | 分母 335 字符 facts，命中 `https://alice:pw123456@cloud.example.invalid/api` |
| 2 | 当前诊断包不再带凭据 | 330 字符 facts，实测 `https://alice:***@cloud.example.invalid/api` |
| 3 | 但 URL 仍可读 | 保留 `https://alice:***@cloud.example.invalid/api` |
| 4 | 掩码**落在密码原来的位置**，其余一字未变 | 把修前那条的密码换成 `***` 后**逐字等于**修后那条 |
| 5 | `status` 体的键集合就是本记录枚举的那 13 个 | 377 字节 / 13 键，多余 0、缺失 0 |
| 6 | **该体里根本没有**配置值可掩 | 两臂都不含 `cloud_base_url` 这个键 |
| 7 | 两臂的 `status` 体都不含凭据 | 分母 377 / 377 字节；该体出自一个**自己配置里就有凭据**的进程 |
| 8 | 两臂的 `status` 体形状相同 | — |

第 6 条是本次**推翻自己上一版口径**的一处：环境那半边是**白名单**（`RuntimeEnvironmentReport.to_dict()`
的固定字段），不是「掩住了」——修前修后都不在。原先含糊的一句「已掩」在此改成分明的「本来就进不去」。

臂 4 的对照曾经**报过一次假失败**：两臂的 facts 里各带自己的 scratch 路径（`/tmp/t18/pre_out` 与
`/tmp/t18/cur_out`），逐字比对自然不等。处置是加一个**可见的** `normalised()` 把臂名换成 `<arm>`，
而不是放松断言——被比的是「掩码这一处之外有没有别的变化」，路径本来就不该参与。

### 4. CHG 记录自身

- §7 **Q-07 改写为已修状态**（原文按旧行为行文，把两处列为「实测输出」）；**新增 Q-08**（Desktop 的
  「环境」取**构建期** `bootstrap::build_environment()`，不取生效配置，理由与代价都写在行内）。
- **一处 ID 撞车当场修掉**：Q-08 这个 ID 早先被 §8 的 T-19 行与 §10 的 AC-11b 当作 **Q-05** 内容的别名用过。
  两处已**改指 Q-05**，Q-08 现只对应一个内容。
- §10：AC-06 点名 T-21 并把「形状错」归位到 AC-06（它坏的是「这一行还读不读得回来」，不是「泄漏了没有」）；
  AC-07 按 T-20 的四处实测缺陷改写；AC-10 由「部分」改写成实测 PASS（`PASS（T-06/T-08/T-18）`）。
- §9 清单：基线回写、两仓入口文档、归档收尾三行勾掉。
- §12：Current 改为「本 CHG 已关闭」；Next 只留**范围外**的三条；Blockers 补 Q-08。
- §13 DONE Gate 九项逐项签字 + 关闭记录（见 `change.md`）。
- §1 `Status: IMPLEMENTING` → `DONE`。

### 5. 归档与冷启动重生成

```bash
git mv delivery/active/CHG-20260923-057 delivery/completed/CHG-20260923-057
ls -a delivery/active/            # 只剩 .gitkeep
python3 scripts/prepare_ai_workspace.py --no-active
```

`delivery/LEDGER.md` 的活动表行**移除**并把原说明段改写为归档叙述；
`delivery/planned/README.md` 的头段与 B 行、`delivery/milestones/M-launch-engineering.md` 的状态行、
`delivery/planned/CHG-20260923-053/change.md` 的并入去向行，四处指向 `active/` 的**活链接**全部改指 `completed/`。

### 6. 失效指针扫描（**报分母 + 阳性对照**）

```bash
git grep -n "active/CHG-20260923-057"                                  # 模式 P
git grep -o "active/CHG-20260923-057" | wc -l                          # 分母
git grep -o "completed/CHG-20260923-056" | wc -l                       # 阳性对照：模式非空转
for r in ../wt-media-agent ../wt-media-desktop ../wt-media-cloud; do
  git -C $r grep -n "active/CHG-20260923-057"; done
```

| 量 | 读数 |
|---|---|
| P 命中**总数（分母）** | **10 处** |
| 涉及文件 | **2 个**，且**两个都在归档记录内部** |
| 记录**外部**的残留 | **0** |
| 三个兄弟仓 | **各 0**（`wt-media-agent` 只有两行 OpenAPI **出处注**（`CHG-20260923-057 T-08`），不含路径；desktop/cloud 0） |
| 外层执行根（`AGENTS.md`/`CLAUDE.md`/`.agents/`） | 0 |
| **阳性对照**：`completed/CHG-20260923-056` | **13 处 / 9 文件** ⇒ 同一个 grep 机制在别处有命中，故「0」不是空转 |
| **阳性对照**：`active/CHG-`（更宽的模式） | **80 处** ⇒ 模式本身能命中 `active/` 形态 |

那 10 处**判为叙述、保留**：`change.md:270` 是 §9 的 T-01 行（记录 T-01 当时把草案移进 `active/`），
`evidence/task-01-governance.md` 的 9 处是 T-01 的**原始记录**（`:21`/`:22` 两条当时真跑过的命令、
`:46-51` 当时的 `find` 输出、`:111` 当时对 README 的改写说明）。
**改了它们就不是 T-01 的证据了**，故一字未改；在该文件顶部加了一段**归档后追加**的注记，
说明这些路径是 T-01 那一刻的事实、记录现位于 `completed/`。这与 CHG-056 归档时的处置同形
（其归档记录自己的 `change.md` 与 `evidence/artifacts/ac05-run5.log` 也保留了 `delivery/active/CHG-20260923-056/`）。

**第二个扫描：把改过的链接真去解析一遍**（字符串扫描证明「没有旧路径」，解析证明「新路径真的通」——
两者不是一回事）。对本次改过的 5 个文件里**全部 50 条相对链接**逐条 `resolve()`：

```
relative links checked: 50   broken: 1
BROKEN  delivery/planned/CHG-20260923-053/change.md  ->  CHG-20260923-059/change.md
```

唯一那条坏的正是上面 Follow-Up 登记的那条（059 的同形链接，非本 CHG 引入）。
它同时是**这个扫描器的阳性对照**：扫描器**能**报错，所以「057 的四处改指 `completed/` 全部解析成功」
是真结果而不是空转。

### 7. 关闭时的验证快照

```
cd wt-media-agent      && bash scripts/test.sh              → Ran 379 tests … OK
cd wt-media-desktop    && cargo test --workspace            → 175 passed; 0 failed
cd wt-media-workspace  && python3 scripts/verify_delivery_governance.py → ok, Active CHG: none
                       && python3 scripts/verify_agent_entry.py         → ok, 0 warning(s)，快照 1668 字符
                       && python3 scripts/verify_skills.py              → verified 10 skill source files
                       && python3 -m unittest discover -s tests -q      → Ran 69 tests, FAILED (failures=4)
```

那 4 条红**不是本 Task 造成的**，判据是**同集合的阳性对照**（不是「看着无关」）：

```bash
rm -rf /tmp/t18/head && mkdir -p /tmp/t18/head
git archive HEAD | tar -x -C /tmp/t18/head           # HEAD 状态，不碰工作树
ln -s …/wt-media-{agent,desktop,cloud} /tmp/t18/       # 兄弟仓就地链接（跨仓路径检查要用）
cd /tmp/t18/head && python3 -m unittest discover -s tests -q
```

| 树 | 读数 | 失败的 4 条 |
|---|---|---|
| `HEAD`（`git archive`，**含** `delivery/active/CHG-20260923-057`） | **Ran 69，FAILED (failures=4)** | `test_verify_m0_config` ×2、`test_verify_m2_acceptance` ×1、`test_verify_product_master_alignment` ×1 |
| 工作树（归档后） | **Ran 69，FAILED (failures=4)** | **逐名相同** |

两棵树的失败**集合与条数完全一致**，且三条模块的失败文案与 `README.md` 已登记的已知红项逐条对上
（`contract_revision` 陈旧 / 一个已被删掉的 Cloud 文件 / M2-M3 状态措辞漂移）。
另有一处结构性旁证：`verify_product_master_alignment.validate_active_change()` 在
`delivery/active/` 下没有 `*/change.md` 时**直接返回 `[]`**（`scripts/verify_product_master_alignment.py:229-230`），
即「没有 active CHG」在这条检查里是**通过**条件而不是失败条件 ⇒ 归档不可能由它转红。

## Expected

基线里读得出已落定的数字与「dev 也落盘」；两个运行仓的入口文档不再把已经变假的旧行为当现状；
AC-10 不再是「未测」；`active/` 下无记录、快照为 `none`、档外无失效链接。

## Actual

全部达成：§1 表的每一处都有实际 diff；AC-10 两臂 8/8 PASS（臂 1 是会失败的那种对照）；
归档后 `Active CHG: none`；失效指针扫描外部残留 **0**、并附两个非空转的阳性对照。
**未做**的只有一件事，如实登记：`git grep` 只覆盖**已入库**的文件，
`.local/`、`target/`、`node_modules/` 这类忽略区不在分母内（本次也不该进——它们不是文档）。

## Follow-Up

- 范围外、不阻塞本次关闭：`delivery/planned/CHG-20260923-053/change.md` 里**同形式的** CHG-059 链接
  （`[CHG-20260923-059](CHG-20260923-059/change.md)`，相对路径不成立）仍是坏的。它**不是**本 CHG 引入的，
  也**不该由归档 057 顺手改**——059 还没归档，等它自己关闭时按本次这套做法处置。
