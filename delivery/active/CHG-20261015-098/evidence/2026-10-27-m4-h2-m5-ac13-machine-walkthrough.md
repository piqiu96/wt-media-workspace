# M4-H2 / M5-AC-13 机器走查（Cloud Web，三账号）

日期：2026-10-27（Asia/Shanghai）
状态：机器走查通过；Desktop 与用户签收待补

> 2026-10-27 第二轮修订（T-12～T-17，六项页面修订）后已复跑：97 项断言全部通过，console error / 页面异常 / HTTP ≥500 均为 0，读数见 `2026-10-27-m4-h2-m5-ac13-second-round-checklist.md`。下列第一轮读数保留为当时事实，不再逐条回改；与第二轮冲突处以第二轮为准。

## 环境与方式

- Cloud API pid 93493（当前 `main` 源码，`127.0.0.1:8188`），Vite `127.0.0.1:5173`，`compose-scheduler` pid 94569，`compose-worker` pid 94570。
- headless Chrome + CDP，1440×900；探针脚本 `/private/tmp/chg098-probe.mjs`、结果 `/private/tmp/chg098-probe-result.json`、截图 `/private/tmp/chg098-shots/`，均不提交。
- 三个账号用本机临时会话（token 只在 `/tmp/chg098-session-*`，未打印）：`operator01`（普通运营）、`senior01`（高级运营）、`admin`（管理员）。
- 每个页面读回 `document.body.innerText`；监听 `Runtime.exceptionThrown`、`console.error`、HTTP ≥500，全程 **0 命中**。

## 夹具

| 对象 | 事实 |
| --- | --- |
| 策略 139 | 团队 1 / `sjz` / 负责人 `operator01` / 已停用；真实 run `85631c9a…`，slot `2026-10-27 04:30:34.396418`，candidate 59 / skipped 40（全部 `other_game`）/ created 1 |
| 策略 139 分页夹具 | `chg098-pagination-01..10`，slot 04:19–04:28、candidate 0 / created 0，仅用于翻页；清理时删除 |
| 任务 449 | `scheduled` / operator 3 `pika` / `created_by` 1 / `material_usage_id NULL` / 成功 → 成片 80 |
| 任务 450 | `manual` / operator 3 / `material_usage_id` 8 / 成功 → 成片 81 |
| 任务 448 | `failed` / `input_missing` / attempt 1 / 负责人 `pika` |
| 素材 153 | 团队 1 / `sjz` / ready；成功成片 80、81 均负责人 `pika`；`material_usages` 2 条（`admin`、`operator01`） |

## 读回结果

### 素材库使用情况

| 账号 | 筛选栏 | 素材 153 行 | 详情/弹窗 |
| --- | --- | --- | --- |
| `operator01` | `综合搜索｜游戏｜加入状态｜我的使用｜文件状态`，无「使用情况」 | `已加入` / `已使用`；无使用人数或姓名 | 详情无使用情况段 |
| `senior01` | 增加「使用情况」 | `未加入` / `未使用` / `成片 2 · 使用 1 人`（整格可点） | 弹窗：`成功成片 2`、`pika 成片 2`；无「负责人未记录」「暂无成功成片」 |
| `admin` | 有「团队」筛选 | `已加入` / `未使用` / `成片 2 · 使用 1 人` | 弹窗同高级运营 |

`material_usages` 有 2 条（`admin`、`operator01`），但成功成片都归 `pika`，弹窗按成片负责人去重后只有 `pika` 一人，计数 2。`admin` 虽已加入却显示「未使用」，因为「我的使用」只按本人负责的成功成片判定。三列状态与使用情况是三个不同事实。

### 任务详情与执行记录

任务 449（`/compose?task_id=449`，普通运营读回）：

```text
任务 ID 449 / 触发方式 策略自动 / 创建人 ID 1 / 负责人 pika
当前状态 成功 / 关联素材 素材 153 / 合成策略 策略 139
执行次数 1 / 生成成片 成片 80
执行记录：第 1 次执行 · 成功
  准备源素材 用时 3.2 秒 文件 94.6 MB
  视频合成   用时 2.4 秒 成片时长 4.0 秒
```

页面把创建触发（`任务信息 → 触发方式`）与 Worker 尝试（`执行记录` 的逐次尝试、步骤与耗时）分开展示；任务页列序为 `任务 ID｜任务名称｜触发方式｜关联素材｜合成策略｜负责人｜生成成片｜状态｜创建时间｜操作`。

任务 448（失败恢复样本）：

```text
当前状态 失败 / 失败原因 源文件缺失
operator01：提示「可重试，但当前账号无此权限（需高级运营或管理员）」，抽屉内重试按钮数 0
senior01：抽屉内重试按钮数 1，无权限提示
```

### 成片与空使用关系

- `/finished-media?output_id=80`（管理视图）：`成片 ID 80 / 生成方式 定时 / 负责人 pika / 来源素材 素材 153 / 策略 139 / 任务 449 / 下载状态 未下载`。**管理视图不渲染「素材使用」行**，这是当前页面布局的事实。
- 任务上下文：任务 449 →「生成成片」→ 成片详情「来源追踪」：`素材 ID 153 / 素材使用 — / 合成策略 139 CHG-098 定时验收`。
- 任务 450 → 成片 81「来源追踪」：`素材使用 8 · 使用中`。

因此 `material_usage_id=NULL` 的读回入口是任务关联成片的来源追踪；成片管理抽屉只给生成来源三元组，不重复个人关系字段。

### 策略运行记录与批次任务

`senior01` / `admin` 打开策略 139：

```text
运行记录（共 11 条，含 10 条分页夹具）
2026/10/27 04:30  定时执行  候选 59  跳过 40  创建 1  失败 0  查看本次任务
2026/10/27 04:28 … 04:20  定时执行  0  0  0  0  —
第 2 页：2026/10/27 04:19  定时执行  0  0  0  0  —

查看本次任务：
排队中 0 · 处理中 0 · 成功 1 · 失败 0 · 已取消 0
任务 449 · 素材 153
成功 · 成片 80
```

翻页前后请求与内容对应：第 1 页 10 行（真实 run 04:30 + 夹具 04:28…04:20），第 2 页 1 行（04:19），总数 11。

### 权限与筛选边界

- `operator01` 打开已停用策略 139：不出现详情抽屉，服务端按不可见处理（`canReadStrategy` 对普通运营要求策略启用）。
- `senior01` 负责人下拉只有 `pika`、`senior01` 两个团队成员，无「我的」「团队全部」伪选项。
- `operator01` 任务页无「负责人」筛选；`admin` 有「团队」「负责人」筛选；两页清空负责人后继续筛选未复现 `undefined` 报错。
- `senior01`/`admin` 成片页有「游戏」筛选与游戏列；`operator01` 成片页只有其负责游戏的选项。

## 截图

`/private/tmp/chg098-shots/`：`operator01-material-library.png`、`operator01-compose-list.png`、`operator01-task-449.png`、`operator01-task-448.png`、`operator01-output-80.png`、`senior01-material-usage-dialog.png`、`senior01-task-448-retry.png`、`senior01-strategy-139-run.png`、`admin-material-library.png`。

其中 `senior01-material-usage-dialog.png` 可见弹窗 `使用情况 / 成功成片 2 / pika 成片 2`；`senior01-strategy-139-run.png` 可见 04:30 真实 run 与 10 条分页夹具。

## 覆盖边界

- 本记录只覆盖 Cloud Web（Chromium）。Desktop（WebKit）共用页面、预览与下载由用户用当前打包 `起飞.app` 走查，见同日清单。
- T-11 stale-ready 用户下载未执行；按清单 C6，默认记为未验证，除非用户当场授权删除云端对象。
- 分页夹具只证明翻页与总数渲染；真实的定时边界、并发与额度以 CHG-105 证据为准，不在本轮重测。
- 任务 448 的重试是待用户在页面上执行的真实动作；机器走查只读按钮与权限，不代替点击后的 Worker 执行。
