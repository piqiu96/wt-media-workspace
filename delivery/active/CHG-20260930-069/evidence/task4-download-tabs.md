# Task 4 证据：下载中心「正在下载 / 最近完成」两标签

- 日期：2026-09-30
- 范围：`wt-media-cloud` web transfer 模块（DownloadCentreDrawer、transferRows 分组纯函数）。

## 测试先行（红）

- 命令：`npx vitest run src/modules/transfer`
- 预期：`splitTransferRows` 未定义导致 transferRows.test 编译失败；抽屉两标签断言失败。
- 实际：5 条用例失败（2 文件红），失败点均为未实现的目标形态。
- 状态：PASS（失败形态正确）

## 实现后（绿）

- 命令：`npx vitest run src/modules/transfer`
- 实际：5 个测试文件 55 条用例全部通过。
- 状态：PASS

## 实现要点（对照 change.md §2/§4）

- `transferRows.js` 新增 `splitTransferRows(rows)`：按 `isTerminal(task)` 分成 `active`（pending/running）与 `recent`（success/failed/cancelled），组内保序，一行恰属一栏；纯函数，测试钉住五状态归属与两栏计数之和等于行数。
- 抽屉：`t-tabs` 两标签带实时计数（`正在下载 (N)` / `最近完成 (M)`），单一列表按当前标签渲染；打开面板时若无在跑任务但有历史，直接落在「最近完成」。
- 保留：真实任务状态、取消、重试、重新下载、打开文件、轮询与文件扫描逻辑全部未动（分组只发生在展示层，`hasLiveTask`/`ensurePolling` 仍看全量任务）。
- 每栏各自的空态文案（「暂无正在下载的任务」/「最近没有完成的任务」）。

## 相关提交

- `feat(chg-069): 下载中心分「正在下载」与「最近完成」两个标签`
