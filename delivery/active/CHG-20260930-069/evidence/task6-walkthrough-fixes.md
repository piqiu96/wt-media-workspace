# Task 6 证据：走查反馈修正（ID 列第一、标题外链、下载按钮、详情统计区块）

- 日期：2026-09-30
- 范围：`wt-media-cloud` production 模块投影/契约 + materials web 模块（两列表、详情抽屉、labels）。

## 后端（投影与契约）

- 事实：本次会话开始时，任务 6 的后端改动已在 `wt-media-cloud` 工作区存在但未提交（model.Material 五个统计字段、投影 JOIN、Business Schema `2026.09.30.2`、repository/wire 测试更新）；来源为上一会话开工的任务 6。本次会话验证后随前端一并提交。
- 命令：`go test -count=1 ./internal/modules/production/... ./internal/infra/storage/... ./internal/bootstrap/...`
- 实际：production、production/repository、production/service、infra/storage、bootstrap 全部 `ok`（缓存清除后复跑）。
- `TestFindMaterialScopesTheSourceAndVideoProjectionByTeam` 断言五项统计值逐字段读出；`TestMaterialProjectionJoinsTheSourceRowLinksIntoEveryRead` 把五个列名钉进列清单；`TestMaterialBodyMarshalsExactlyTheFrozenPropertySet` 测得 Material 24 属性，与 schema 一致。
- OpenAPI 不列 Material body 属性（只写描述），无需改动。
- 状态：PASS

## 前端测试先行（红）

- 命令：`npx vitest run src/modules/materials`
- 预期：两页「ID 列第一/标题外链/无提示小字」、抽屉统计区块与「下载」文案、labels 的 `downloadHint` 缺席断言失败。
- 实际：6 条用例失败（4 文件红），失败点均为未实现的目标形态。
- 状态：PASS（失败形态正确）

## 前端实现后（绿）

- 命令：`npx vitest run src/modules/materials`
- 实际：6 个测试文件 32 条用例全部通过。
- 定向复跑：`npx vitest run src/modules/materials src/modules/transfer src/shared/api/materials.test.js` → 12 文件 92 用例全部通过。
- 状态：PASS

## 双 Web 构建

- 命令：`npm run build:cloud` → `✓ built in 6.80s`
- 命令：`npm run build:desktop` → `✓ built in 6.67s`
- 仅有既有 chunk 体积提示，无错误。
- 状态：PASS

## 实现要点（对照 change.md §4/§5 任务 6）

- 两列表：素材 ID 列移至第一列（封面随后）；标题有 `source_url` 时渲染为 `wt-primary-link` 外链（新窗口打开，与内容池页同一形状），无落地页退回普通文本；颜色只写在 span 分支避免覆盖主题色。
- 下载按钮统一为「下载」，按钮下提示小字与 `downloadHint` 函数一并删除（状态徽章已说明）；labels 测试钉住 `downloadHint` 不再导出。
- 详情抽屉新增「来源内容池统计」独立区块（播放/点赞/收藏/评论/分享，千分位，与内容池页同量法）；顺手补上抽屉内 `wt-primary-link` 样式定义（此前借类名无样式）。
- 封面数据链路（change.md §5 任务 6 备注）：`source_contents.cover_url` 已由既有投影 JOIN 带出，无需同步；走查所见占位图属来源 CDN 签名地址过期，不在本 CHG 内修。

## 本地环境重建（m2b-local-acceptance.sh all）

- 命令：`wt-media-workspace/scripts/m2b-local-acceptance.sh all`（exit 0，2026-09-30 复跑）。
- 各门：Cloud/Agent 健康 PASS、BitBrowser normal、Desktop 前端与 DMG 全新构建（含任务 6 前端）并挂载启动、Desktop assets fresh、登录冒烟 PASS user=admin。
- 状态：PASS

## 走查二轮修正（2026-09-30，用户反馈两条）

### 反馈 1：统计数据全部为 0

- 根因定位：`m2b_local_acceptance.py` 的 `start_cloud` 对「已健康」的服务直接返回不重启，运行中的 Cloud 为任务 5 时的旧编译产物，API 不含五个统计键，前端缺键显示 0。
- 修正动作：`m2b_local_acceptance.py up --force-restart` 强制重启。
- 验证（阳性对照）：登录 admin 后 `GET /api/v1/materials`，149 条素材中抽到的行返回真实统计（如 id 153：like 72,313 / favorite 15,676 / comment 4,028 / share 8,323），`view_count` 全部为 0。
- 「播放」恒 0 的数据事实：直查 MySQL `source_contents` 518 行带 `raw.statistics` 的来源行 `play_count` 全部为 0（抖音该接口不提供播放数）；归一化映射 `statistics.play_count → view_count` 本身正确（discovery_crawler_test 有 340,000 阳性样例）。
- 用户裁定（2026-09-30）：统计区块不展示「播放」项；`view_count` 字段保留在契约中不渲染。
- 状态：PASS

### 反馈 2：素材 ID 不能用 # 号

- 修正：两列表 ID 列与详情抽屉的素材 ID 均显示纯数字，去掉 `#` 前缀；页面测试钉住 `#{{ row.id }}` / `#{{ material.id }}` 不再出现。
- 状态：PASS

### 二轮验证

- 命令：`npx vitest run src/modules/materials src/modules/transfer src/shared/api/materials.test.js` → 12 文件 93 用例全部通过。
- 命令：`npm run build:cloud` → `✓ built in 7.04s`；`npm run build:desktop` → `✓ built in 7.32s`。
- 命令：`m2b-local-acceptance.sh all` exit 0：Cloud/Agent 健康（Cloud 为强制重启后的新代码）、BitBrowser normal、DMG 与 assets 以二轮前端重建 fresh、登录冒烟 PASS。
- 状态：PASS

## 真实桌面包走查（待用户执行）

- 环境已用二轮前端重建重启；用户可在 WT Media.app 中核对：ID 第一列纯数字、标题蓝色跳转、下载按钮与无小字、详情统计四项与既有素材数据一致。
- 状态：PENDING（用户签收前本 CHG 保持 ACTIVE）

## 相关提交（wt-media-cloud）

- `6ffdd15` Task 6（后端投影与前端走查修正一并提交）
- `be89265` Task 6 二轮（ID 去 # 前缀；统计区块不展示「播放」）
