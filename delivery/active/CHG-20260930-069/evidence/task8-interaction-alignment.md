# Task 8 证据：走查三轮——素材库/我的素材交互对齐前端交互规范

- 日期：2026-09-30
- 范围：`wt-media-cloud` materials web 模块（两列表、共用详情抽屉、labels）。仅交互层，不动后端与契约。
- 依据基线：`docs/standards/前端交互规范.md`（§2.3/§5.3/§5.5/§5.6/§7.4）。
- 用户裁定（2026-09-30）：素材库不再有下载（含详情抽屉），下载保留在我的素材；仅交互层；内容池另立 CHG-20260930-070（见 delivery/planned）。

## 测试先行（红）

- 命令：`npx vitest run src/modules/materials`
- 实际：7 条用例失败（4 文件红），失败点均为未实现的目标形态（详情文案、无下载断言、mode 抽屉、downloadActionLabel、更多下拉）。
- 状态：PASS（失败形态正确）

## 实现后（绿）

- 命令：`npx vitest run src/modules/materials src/modules/transfer src/shared/api/materials.test.js`
- 实际：12 文件 96 用例全部通过。
- 全量：`npx vitest run` → 331/332 通过，唯一失败为既有 `localSettingsWiring.test.js`（工作区既有脏改动所致，与本 CHG 无关，checkpoint 已登记）。
- 状态：PASS

## 双 Web 构建

- 命令：`npm run build:cloud` → `✓ built in 7.29s`；`npm run build:desktop` → `✓ built in 6.82s`。
- 状态：PASS

## 本地环境重建

- 命令：`m2b-local-acceptance.sh all` exit 0：Cloud/Agent 健康、BitBrowser normal、Desktop assets 与 DMG fresh（含任务 8 前端）、登录冒烟 PASS。
- 状态：PASS

## 实现要点（对照 change.md §5 任务 8）

- 「查看」→「详情」：两页行操作与断言统一；`>查看</t-button>` 被测试钉住不再出现。
- 素材库行：`详情 | 加入我的素材`（primary）；`download`/`createDownload`/`createDownloadFailureMessage`/`downloadCentre` 全部从页面移除（测试钉住缺席）；页面描述改为「加入我的素材后即可下载到本机」。
- 我的素材行：`详情 | {{ downloadActionLabel(video_status) }} | 更多：移出`；failed 显示「重试」（§7.4），其余「下载」；移出收进 `t-dropdown`（与挖掘策略页同形状），不再平铺危险按钮。
- 共用详情抽屉：新增 `mode` prop（library/mine）；library 上下文只有「加入我的素材」，mine 上下文只有「下载/重试」；我的素材页随之移除 `addBack`（在「我的素材」给自己一个加入按钮是同义反复，恢复路径仍是回素材库再点一次，测试注释已更新）。
- `labels.js` 新增 `downloadActionLabel(videoStatus)`，行内与抽屉共用同一文案源。

## 范围外登记

- 标题点击跳来源平台落地页（CHG-069 走查裁定）保留，登记为与规范 §5.3「标题可点击进详情」的已裁定偏差——规范该条为「可以」而非「必须」，详情入口由常驻「详情」按钮承担。
- 需要新后端能力的状态矩阵（已领取/已放弃/素材生命周期/加入合成）不在本轮。

## 真实桌面包走查（待用户执行）

- 环境已用任务 8 前端重建重启；核对点：素材库行与抽屉无下载、我的素材 failed 行显示「重试」、「更多」里的移出、两页「详情」文案。
- 状态：PENDING（用户签收前本 CHG 保持 ACTIVE）

## 相关提交（wt-media-cloud）

- `84def36` Task 8
