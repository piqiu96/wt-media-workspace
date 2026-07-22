# Task 5：M2-A1 综合验收结论

> 日期：2026-07-22

## 已完成

- M2-A1 详细实施计划已建立并按任务执行；
- 规格复审通过；
- 代码质量审查发现的迁移、权限、事务、列表范围和错误吞噬问题已修复；
- Cloud 全量 Go 测试、Web 14 项测试、Cloud 生产构建通过；
- Workspace 交付治理、产品计划、Skill 校验和 26 项测试通过；
- 真实 MySQL 新库、无 Ledger 的 001～011 旧库和危险数据阻断三类场景通过。
- 运行中隔离 Cloud 的管理员、高级运营、普通运营 API 权限矩阵通过。
- 用户管理页面真实浏览器操作验收通过。

## 真实 Web 页面验收

> 日期：2026-07-23

### 验收环境

- MySQL：本机 MySQL 8.4，隔离库 `wt_media_m2_a1_web_acceptance`；
- Cloud：隔离实例，`WT_MEDIA_CLOUD_HTTP_ADDR=127.0.0.1:18080`；
- Web：Cloud Web Vite，本地 `http://127.0.0.1:5173/users`；
- 初始管理员：脱敏验收账号 `m2a1_admin`。

### 页面操作

| 操作 | 期望 | 实际 | 状态 |
|---|---|---|---|
| 管理员登录 | 进入工作台并显示当前管理员 | 工作台显示当前用户 `m2a1_admin`、角色 `admin` | PASS |
| 打开用户与权限 | 展示 UID、用户名、角色、运营分组、游戏范围、状态、操作 | 页面展示上述列和管理员行 | PASS |
| 新建运营分组 | 分组创建后出现在运营分组列表 | 创建 `火影运营组`，列表显示 `#1 火影运营组` | PASS |
| 新建普通运营用户 | 用户落库并在列表显示 UID、角色、分组、游戏、状态 | 创建 `m2a1_operator`，页面显示 UID `2`、普通运营、火影运营组、`game-a`、启用 | PASS |
| 一次性密码展示 | 创建后只在本次弹窗显示 | 弹窗显示一次性密码说明和当前密码值 | PASS |
| 用户筛选 | 按用户名筛选只显示目标用户 | `m2a1_operator` 筛选后仅显示目标用户 | PASS |
| 编辑用户角色 | 修改后页面刷新显示新角色 | 角色从普通运营改为高级运营，页面显示高级运营 | PASS |
| 重置密码 | 重置后仅弹窗显示一次性密码 | 弹窗显示重置后的一次性密码说明和值 | PASS |
| 停用用户 | 页面状态改为停用，操作变为启用 | 用户状态显示停用，按钮切换为启用 | PASS |
| 重新启用用户 | 页面状态恢复启用 | 用户状态显示启用，按钮切换为停用 | PASS |

### 数据库核对

最终只读核对结果：

```text
users:
1  m2a1_admin     admin            enabled  NULL  NULL
2  m2a1_operator  senior_operator  enabled  1     火影运营组

user_game_scopes:
2  game-a

audit_logs latest:
user.update
user.update
user.password.reset
user.update
user.create
operation_team.create
user.login
user.bootstrap
```

### 判定

真实 Web 页面、Cloud API、MySQL 持久化和审计均已证明 M2-A1 用户领域模型迁移闭环成立。

## 判定

| 范围 | 状态 |
|---|---|
| 代码实现 | PASS |
| 自动测试 | PASS |
| 真实 MySQL | PASS |
| 治理校验 | PASS |
| 运行中 Cloud API 权限矩阵 | PASS |
| Web 页面人工验收 | PASS |
| CHG-20260722-021 | READY_TO_CLOSE |

本证据只宣称 M2-A1 完成，不宣称整个 M2-A 或 M2 完成。下一步应关闭本 CHG，并按 M2 Milestone 规划 M2-A2。
