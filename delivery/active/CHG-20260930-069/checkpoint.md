# CHG-20260930-069 Checkpoint

- Status: `ACTIVE`
- Current task: 等待用户真实桌面走查与 M4-A 签收（实现任务 1-5 已全部完成，本地环境已启动并通过全部验收门）。
- Completed:
  - Task 1 完成：`model.Material` 新增 `cover_url`/`author_home_url`（JSON 可选键），投影 SQL JOIN source_contents 带出，无数据库迁移；Business Schema Material 增两属性、revision `2026.09.30.1`；wire/repository/service 测试先行后全绿（证据 `evidence/task1-source-links.md`）。
  - Task 2 完成：`infra/storage.PublicURL` 组合稳定公开地址（endpoint/bucket/prefix，无凭据可用，键校验，生命周期随 Initialize/Close）；service `ObjectLinker` 注入 + `VideoURL`（范围→就绪→事实完整→组合）；路由 `GET /api/v1/materials/:id/video-url`；OpenAPI + Business Schema `MaterialVideoLink`，Material 禁携 `video_url`；测试先行后全绿，全仓 Go 测试 0 失败（证据 `evidence/task2-video-url.md`）。
  - Task 3 完成：两列表改为封面（MaterialCover，缺图/裂图显示占位）+ 素材 ID + 标题 + 平台 + 游戏 + 状态 + 时间 + 操作；作者/链接/体积移入共用详情抽屉（含云端视频 URL，就绪时经详情接口取）；client 新增 `getVideoUrl`；定向 36 用例全绿（证据 `evidence/task3-lists-and-drawer.md`）。
  - Task 4 完成：`splitTransferRows` 纯函数按 `isTerminal` 分两栏（组内保序、计数一致）；抽屉 `t-tabs` 两标签带实时计数、按标签渲染单一列表、各有空态；取消/重试/重新下载/打开文件/轮询/文件扫描未动；定向 55 用例全绿（证据 `evidence/task4-download-tabs.md`）。
  - 执行前修复了过期的 `.ai/CURRENT_CONTEXT.md`（09-29 无活跃 CHG），已用 `prepare_ai_workspace.py --change CHG-20260930-069` 重新生成。
- In progress: Task 5 全部完成：定向测试与双构建（Go 定向全 ok、Web 定向 91 用例通过、`build:cloud`/`build:desktop` 成功）；`m2b-local-acceptance.sh all` exit 0（Cloud/Agent 健康、BitBrowser normal、Desktop assets 与 DMG fresh 且含 `127.0.0.1:18080/api/v1`、CORS 预检通过、admin 登录冒烟通过、WT Media.app 已启动 pid 73943）。剩余：用户真实走查与 M4-A 签收。
- Blocked: 真实对象 URL 可访问性取决于现有对象存储桶读权限；本 CHG 不改变桶 ACL（用户走查时验证）。
- 范围外备注：全量 Web 测试有一条既有失败 `localSettingsWiring.test.js`（桌面路由数量），由本 CHG 之前已存在的工作区脏改动（TasksPage 删除/路由调整）造成，不属于本 CHG，保持原样。
- Next: 用户在已启动的 WT Media.app 中走查验收（封面/ID 列与占位图、详情四项、越权/不存在/未就绪不返回地址、下载中心两栏计数与终态行为、云端视频 URL 实际可访问性）；签收后走 Completion Gate。签收前不关闭本 CHG，不启动 M4-C2。
- Recent verification: 定向 Go 五包 ok；定向 vitest 91 用例通过；`build:cloud`/`build:desktop` 成功；`m2b-local-acceptance.sh all` exit 0（全部环境门 PASS）。
- 提交边界备注：工作区 13 个文件的既有改动按 change.md §6 保持原样；与本 CHG 重叠的 3 个 Vue 文件其既有样式改动随 CHG 提交一并保留（内容不回退），无关文件不提交。
- Acceptance: 等定向验证、桌面人工走查和 M4-A 用户签收；保持 M4-C2 未激活。
