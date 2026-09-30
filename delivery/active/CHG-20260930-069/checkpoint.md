# CHG-20260930-069 Checkpoint

- Status: `ACTIVE`
- Current task: 等待用户真实桌面走查与 M4-A 签收（实现任务 1-6 已全部完成；环境已用任务 6 前端重建重启并通过全部验收门）。
- Completed:
  - Task 1 完成：`model.Material` 新增 `cover_url`/`author_home_url`（JSON 可选键），投影 SQL JOIN source_contents 带出，无数据库迁移；Business Schema Material 增两属性、revision `2026.09.30.1`；wire/repository/service 测试先行后全绿（证据 `evidence/task1-source-links.md`）。
  - Task 2 完成：`infra/storage.PublicURL` 组合稳定公开地址（endpoint/bucket/prefix，无凭据可用，键校验，生命周期随 Initialize/Close）；service `ObjectLinker` 注入 + `VideoURL`（范围→就绪→事实完整→组合）；路由 `GET /api/v1/materials/:id/video-url`；OpenAPI + Business Schema `MaterialVideoLink`，Material 禁携 `video_url`；测试先行后全绿，全仓 Go 测试 0 失败（证据 `evidence/task2-video-url.md`）。
  - Task 3 完成：两列表改为封面（MaterialCover，缺图/裂图显示占位）+ 素材 ID + 标题 + 平台 + 游戏 + 状态 + 时间 + 操作；作者/链接/体积移入共用详情抽屉（含云端视频 URL，就绪时经详情接口取）；client 新增 `getVideoUrl`；定向 36 用例全绿（证据 `evidence/task3-lists-and-drawer.md`）。
  - Task 4 完成：`splitTransferRows` 纯函数按 `isTerminal` 分两栏（组内保序、计数一致）；抽屉 `t-tabs` 两标签带实时计数、按标签渲染单一列表、各有空态；取消/重试/重新下载/打开文件/轮询/文件扫描未动；定向 55 用例全绿（证据 `evidence/task4-download-tabs.md`）。
  - 执行前修复了过期的 `.ai/CURRENT_CONTEXT.md`（09-29 无活跃 CHG），已用 `prepare_ai_workspace.py --change CHG-20260930-069` 重新生成。
  - Task 6 一轮完成（走查反馈修正，证据 `evidence/task6-walkthrough-fixes.md`，提交 `6ffdd15`）：素材投影 JOIN 带出内容池统计（Business Schema `2026.09.30.2`）；两列表素材 ID 列第一、标题蓝色外链跳来源平台落地页；「下载到本机」改「下载」并删除提示小字（`downloadHint` 删除）；详情抽屉新增「来源内容池统计」独立区块（千分位）。前端测试先行红（6 失败）后绿；定向 Go 五包 ok；后端部分系上一会话开工留在工作区的未提交改动，验证后一并提交。封面链路核对：`source_contents.cover_url` 已由投影带出，占位图问题属来源 CDN 签名过期，不在本 CHG 内修。
  - Task 6 二轮完成（走查反馈「统计全 0」「ID 带 #」，提交 `be89265`）：「统计全 0」根因是运行中的 Cloud 为旧编译产物（m2b 对已健康服务不重启），`up --force-restart` 后 API 验证返回真实统计；抖音对 518 行来源 `play_count` 恒为 0，经用户裁定统计区块不展示「播放」；素材 ID 在两列表与详情抽屉均去 `#` 前缀。定向 vitest 93 用例通过、双构建成功、m2b all exit 0（Cloud 新代码 + DMG/assets 以二轮前端重建）。
  - Task 8 完成（走查三轮，交互对齐 `docs/standards/前端交互规范.md`，证据 `evidence/task8-interaction-alignment.md`，提交 `84def36`）：「查看」统一「详情」；素材库行与抽屉移除下载（下载归我的素材，用户裁定），主操作「加入我的素材」；我的素材行 详情 | 下载（failed→「重试」）| 更多：移出；共用抽屉按 mode 提供上下文动作。测试先行红（7 失败）后绿；定向 96 用例、全量 331/332（唯一失败为既有 localSettingsWiring，范围外已登记）、双构建、m2b all exit 0。范围仅交互层；标题跳来源页登记为与 §5.3 的已裁定偏差；内容池对齐另立 CHG-20260930-070（planned，待本 CHG 关闭后激活）。
- In progress: 无实现中任务。剩余：用户真实走查（含任务 6 两轮与任务 8 修正项）与 M4-A 签收；签收后关闭本 CHG 并激活 CHG-20260930-070（内容池交互对齐）。
- Blocked: 真实对象 URL 可访问性取决于现有对象存储桶读权限；本 CHG 不改变桶 ACL（用户走查时验证）。
- 范围外备注：全量 Web 测试有一条既有失败 `localSettingsWiring.test.js`（桌面路由数量），由本 CHG 之前已存在的工作区脏改动（TasksPage 删除/路由调整）造成，不属于本 CHG，保持原样。
- Next: 用户在已重启的 WT Media.app 中走查验收（封面/ID 列与占位图、ID 第一列、标题蓝色跳转来源页、详情四项与内容池统计四项、越权/不存在/未就绪不返回地址、下载中心两栏计数与终态行为、云端视频 URL 实际可访问性、任务 8 交互形态：素材库无下载/我的素材重试与更多移出/两页「详情」）；签收后走 Completion Gate，关闭本 CHG 并激活 CHG-20260930-070。签收前不启动 M4-C2。
- Recent verification: 定向 Go 五包 ok（-count=1）；定向 vitest 96 用例通过、全量 331/332（唯一失败为既有 localSettingsWiring）；`build:cloud`/`build:desktop` 成功；Cloud `--force-restart` 后 API 实测返回真实统计；`m2b-local-acceptance.sh all` 复跑 exit 0（任务 8 前端已进 DMG 与 assets）。
- 提交边界备注：工作区 13 个文件的既有改动按 change.md §6 保持原样；与本 CHG 重叠的 3 个 Vue 文件其既有样式改动随 CHG 提交一并保留（内容不回退），无关文件不提交。
- Acceptance: 等定向验证、桌面人工走查和 M4-A 用户签收；保持 M4-C2 未激活。
