# CHG-20260723-024: M2-A3 用户管理、运营分组、游戏字典与Desktop角色入口回修

## 1. Basic Information

- Level: M
- Status: CLOSED
- Created: 2026-07-23
- Affected repositories: `wt-media-cloud`, `wt-media-workspace`
- Current repository: `wt-media-workspace`
- Milestone: `delivery/milestones/M2-account-runtime.md#m2-a-用户权限会话与运行环境可信闭环`
- Inherited evidence:
  - `delivery/completed/CHG-20260722-021/evidence/task-5-m2-a1-acceptance.md`
  - `delivery/completed/CHG-20260723-022/evidence/task-5-m2-a2-acceptance.md`

## 2. Change Goal

补齐 M2-A 用户管理真实可用性：Cloud 用户管理、运营分组和游戏范围作为基础管理能力独立呈现；所有管理列表默认具备搜索、筛选、列表和分页；创建用户失败必须展示运营可理解的原因；Desktop 只允许普通运营登录并发起本机执行，管理员和高级运营只能使用 Cloud Web 管理能力。

## 3. Current Proven Facts

- 用户自增 UID、角色、分组、游戏范围、会话替换和主账号可信已经具备基础实现；
- Cloud Web `/users` 有用户管理页面，但当前页面同时混放运营分组，列表未分页；
- 当前游戏范围仍为手工输入，容易产生错别字和权限范围错误；
- Desktop 与 Cloud 共用登录页，当前没有在 Desktop 入口阻止管理员或高级运营；
- 用户反馈创建用户失败，需要明确错误原因和可修复路径。

## 4. Ordered Tasks

### Task 1：Milestone 与治理同步

- 更新 M2-A milestone，明确 Desktop 只允许普通运营登录；
- 明确 Cloud 系统管理包含用户管理、运营分组、游戏管理；
- 明确所有管理类列表默认包含搜索、筛选、列表和分页。

### Task 2：游戏管理基础字典

- 增加游戏字典表、Cloud API 和服务校验；
- 支持游戏列表、新建、编辑、停用/启用；
- 创建/编辑用户时只能选择已启用游戏。

### Task 3：用户管理页面回修

- 页面标题改为“用户管理”；
- 用户列表支持分页；
- 创建用户失败展示明确原因；
- 创建/编辑用户时使用游戏字典选择，不再手工输入游戏 ID；
- 保留 UID、用户名、角色、分组、游戏、状态、编辑、重置密码、停用/启用、删除。

### Task 4：运营分组独立页面

- 从用户管理页拆出运营分组页面；
- 分组列表支持搜索、分页、用户数量展示；
- 支持新建、重命名、删除空分组；被引用时提示不能删除。

### Task 5：Desktop 角色入口限制

- Desktop 登录后只允许普通运营进入业务页面；
- 管理员和高级运营在 Desktop 登录后应被拒绝并提示使用 Cloud Web；
- Desktop 本地无认证页面，如 Agent 状态和本地日志，保持可访问。

### Task 6：验收

- 自动测试覆盖用户 API、页面关键文案、Desktop 角色限制；
- Cloud API 验证用户、分组、游戏基础流程；
- Evidence 记录用户可见入口、失败提示和分页/筛选行为。

## 5. Acceptance

- Cloud 菜单展示“用户管理”“运营分组”“游戏管理”；
- 用户管理列表具备搜索、筛选、分页；
- 运营分组列表具备搜索、分页和用户数量；
- 游戏管理列表具备搜索、筛选、分页，创建用户只能从游戏字典选择游戏；
- 创建用户失败时显示可理解原因；
- 管理员和高级运营不能进入 Desktop 业务页面；
- 普通运营可以继续进入 Desktop 业务页面；
- 不改变 M2-B Profile、M2-C 代理、M2-D Cookie 和 M2-E 本机执行抽屉范围。

## 6. Explicitly Not Doing

- 不实现 M2-B Profile正式同步、Diff应用或账号绑定；
- 不实现 M2-C 代理写入BitBrowser；
- 不实现 M2-D Cookie上号或账号检查；
- 不实现复杂组织树、自定义角色或审批；
- 不实现游戏业务全量配置，只做 M2-A 权限范围所需的基础游戏字典。

## 7. Checkpoint

- Completed: Task 1～6 completed, including latest manual feedback fixes. Desktop menu now removes empty groups after filtering, so the empty “系统” group no longer appears; Cloud hides and route-guards user/team/game management for non-admin users; backend also forbids non-admin `GET /api/v1/users`; user management maps game IDs to Chinese game names; game ID is constrained to 32-character alphanumeric values and duplicate IDs are rejected; create/reset password minimum is 6 characters; games referenced by users cannot be disabled or deleted; operation teams referenced by users cannot be deleted and the UI disables the unsafe action. M2-A milestone updated; game dictionary migration/API/service added; user management page renamed and paginated; operation teams and games split into independent Cloud pages with list/search/pagination; Desktop route guard and login page reject admin/senior_operator roles; automated and real Cloud API verification recorded.
- Current: Closed after user manual acceptance.
- Next: Continue with M2-B from `delivery/milestones/M2-account-runtime.md`.
- Blockers: 无。
- Recent verification: `go test ./internal/modules/... ./internal/app` PASS; Cloud Web `npm run test` PASS; Cloud Web `npm run build` PASS; Cloud config `npm run build:cloud` PASS; Desktop Web `npm run build:desktop` PASS; real MySQL + Cloud API invalid game ID rejection `[400,10004,游戏ID仅支持32位以内字母或数字]`, 6-character password operator creation `[201,0]`, and ordinary operator user-management API rejection `[403,11003]` PASS. Cloud API restarted with current code on `18080` and `8080` using `WT_MEDIA_SESSION_COOKIE_SECURE=false` for local HTTP validation. Follow-up fix for user-management blank/loading state: admin `game_ids=null` is now guarded in `UsersPage.vue`; focused tests `npm run test -- --run UsersPage.test.js TeamsAndGamesPage.test.js` PASS; `npm run build:cloud` PASS; browser verification confirms `/users`, `/operation-teams`, and `/games` tables render. Reference protection follow-up: `env GOCACHE=/Users/aqiuye/Develop/workspace/wt-media/wt-media-cloud/.cache/go-build go test ./internal/modules/... ./internal/app` PASS; Cloud Web `npm run test` PASS; `npm run build:cloud` PASS; browser verification confirms referenced teams cannot be deleted and referenced enabled games cannot be disabled/deleted. User manual acceptance confirmed: `确定已验收`. Evidence: `evidence/m2-a3-management-review.md`.
