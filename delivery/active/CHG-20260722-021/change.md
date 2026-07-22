# CHG-20260722-021: M2-A1 用户领域模型迁移

## 1. Basic Information

- Level: M
- Status: IN_PROGRESS
- Created: 2026-07-22
- Affected repositories: `wt-media-cloud`, `wt-media-workspace`
- Current repository: `wt-media-workspace`
- Milestone: `delivery/milestones/M2-account-runtime.md#m2-a-用户权限会话与运行环境可信闭环`
- Inherited evidence: `delivery/completed/CHG-20260721-020/evidence/governance-scope-audit.md`

## 2. Change Goal

将Cloud用户领域从旧的字符串ID、`technician`角色和仅游戏范围模型，迁移为人工确认的自增UID、管理员/高级运营/普通运营、单层运营分组与游戏交集权限模型，并在真实MySQL、API和Web用户管理中形成可独立验收的A1闭环。

本 CHG 的用户可见纵向结果是：管理员可以管理分组和用户；高级运营只访问同组与授权游戏交集；普通运营只访问本人和授权游戏交集；管理员不受分组限制。

## 3. Current Proven Facts

- Cloud已有用户、密码、游戏范围、会话、审计和部分跨游戏403基础；
- Web已有用户列表和基础用户管理入口；
- 当前迁移、服务、测试和页面仍以字符串ID与`technician`为事实；
- 运营分组及“同组/本人∩授权游戏”尚不存在。

## 4. Remaining Gap

- `users.id`及关联外键不是自增数值ID；
- 角色仍为`operator/senior_operator/technician`；
- 没有运营分组表、用户分组关系、转组历史归属规则；
- 现有模块授权没有统一表达管理员全部、高级运营同组、普通运营本人，再与游戏范围求交集；
- Web用户管理缺少分组和新角色语义；
- 会话确认和BitBrowser身份可信属于A2，不在本CHG实现。

## 5. Ordered Tasks

### Task 1：迁移与领域类型

- 先为自增UID、三角色和分组约束编写失败测试；
- 设计并实现不丢失现有用户与关联数据的MySQL迁移；
- 更新Cloud身份领域类型、角色校验和契约；
- 验证管理员无分组，普通/高级运营必须且仅属于一个分组。

### Task 2：运营分组生命周期

- 实现分组创建、列表、重命名和受约束删除；
- 已有用户或历史业务引用时禁止物理删除；
- 用户转组后只影响新业务归属，历史记录保留旧分组事实；
- 记录脱敏审计。

### Task 3：权限交集

- 建立统一授权判定：管理员全部、高级运营同组、普通运营本人；
- 将上述范围与授权游戏求交集；
- 接入M2现有账号和Profile Cloud查询/修改入口，并保存创建时分组快照；
- 代理不设置个人或分组归属，代理权限在M2-C基于真实Profile/账号关系接入，本CHG不虚构归属字段；
- 用正向、跨组、跨用户和跨游戏测试证明零数据泄漏和零副作用。

### Task 4：用户管理API与Web

- 更新用户创建、列表、筛选、修改角色/分组/游戏、密码重置和禁用；
- 新密码只在创建或重置响应中显示一次；
- 页面统一显示UID、用户名、角色、分组和授权游戏；
- 移除`technician`与`retired`无关的旧角色文案。

### Task 5：A1真实验收与迁移证据

- 使用真实MySQL执行迁移和回滚前检查；
- 运行Cloud与Web自动测试及治理校验；
- 人工验证管理员、高级运营和普通运营的用户/分组/游戏权限矩阵；
- 仅判定A1完成，不宣称整个M2-A完成。

## 6. Acceptance

### 用户验收

- 管理员可以管理分组和三类用户且不需要分组；
- 高级运营只看到同组且在授权游戏内的数据；
- 普通运营只看到本人且在授权游戏内的数据；
- 用户列表、筛选、修改、重置密码、禁用和审计符合新模型。

### 系统验收

- 自增UID和关联外键迁移不丢失已有数据；
- API与UI使用一致角色、分组和游戏交集权限；
- 跨组、跨用户和跨游戏访问无数据泄漏、无外部副作用；
- 用户、分组、权限变更和密码操作正确持久化并审计。

### 真实依赖验收

- 使用真实MySQL和运行中的Cloud/Web；
- Evidence 只记录脱敏标识、命令、期望、实际结果、PASS/FAIL 和提交引用；
- 自动测试不能代替三角色与真实MySQL/Web人工验收。

## 7. Explicitly Not Doing

- 不实现M2-A2确认式会话替换、Desktop环境、BitBrowser首次绑定或重绑；
- 不实现 M2-B Profile 生命周期、Diff 双向处理或账号检查；
- 不实现 M2-C 代理导入、配额、分配和真实写入；
- 不实现 M2-D Cookie 写入、读取或开户；
- 不实现 M2-E 打包 Sidecar 和综合恢复；
- 不修改非测试 BitBrowser Profile；
- 不在 Evidence、日志、测试或仓库保存真实密码、Cookie、代理凭据、token 或验证码；
- 不因自动测试通过而跳过人工验收。

## 8. Checkpoint

- Completed: Cloud提交`d623bcb`、`089936c`、`98a35d1`、`cbd60a0`、`d16e37d`和`9fc4c8a`已完成A1迁移、三角色/分组、权限交集、API/Web用户管理及审查纠偏；真实MySQL新库13/13、无Ledger的001～011旧库2/13接管并最终13条、危险遗留数据前置阻断均通过；运行中隔离Cloud的三角色API矩阵通过；Cloud全量Go、Web 14项、Cloud构建及Workspace 26项治理测试通过。
- Current: A1代码、自动验证、真实MySQL、运行中Cloud API和Evidence已完成；用户管理Web页面人工走查尚未执行。
- Next: 在真实Web中由管理员完成创建、筛选、修改、重置密码和禁用走查；通过后关闭本CHG，再规划M2-A2。
- Blockers: 无代码或产品阻塞；仅剩用户可见Web页面的人工验收。
- Recent verification: `go test ./... -count=1` PASS；`npm test --prefix web` 14/14 PASS；`npm run build:cloud --prefix web` PASS（仅既有chunk提示）；Workspace治理测试26/26 PASS；真实MySQL三类迁移场景PASS；隔离Cloud三角色API矩阵PASS。

## 9. Evidence Requirements

- `evidence/governance-start-gate.md`；
- `evidence/task-1-identity-migration.md`；
- `evidence/task-2-team-lifecycle.md`；
- `evidence/task-3-scope-matrix.md`；
- `evidence/task-4-user-management.md`；
- `evidence/task-5-m2-a1-acceptance.md`。

## 10. Pending Questions

None.
