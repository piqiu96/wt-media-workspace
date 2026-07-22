# Task 4：用户管理 API 与 Web 证据

> 日期：2026-07-22

## 已验证事实

- 用户列表和表单统一使用数值 UID、三角色、分组、游戏和状态；
- 完整 PATCH 在全部字段校验后一次提交，角色/分组/游戏已修改但状态失败的部分提交已消除；
- 修改权限、状态和密码会失效旧会话，并与审计处于同一事务；
- 新建和重置密码只在响应与当前弹窗中显示一次，关闭后清空前端内存引用；
- Bootstrap 使用 `WT_MEDIA_INITIAL_ADMIN_*`，旧 `WT_MEDIA_INITIAL_TECHNICIAN_*` 仅作兼容别名。

## 验证

| 命令或用例 | 实际结果 | 状态 |
|---|---|---|
| `go test ./... -count=1` | Cloud 全包通过 | PASS |
| `npm test --prefix web` | 5 个测试文件、14 项测试通过 | PASS |
| `npm run build:cloud --prefix web` | 生产构建通过；仅既有 chunk 大小提示 | PASS |
| `TestUpdateUserRejectsInvalidStatusWithoutChangingAccess` | 非法状态不会修改已持久化权限 | PASS |
| `TestUpdateUserCommitsAccessAndStatusTogetherAndInvalidatesSession` | 完整修改原子提交且旧会话失效 | PASS |

## 运行中 API 验证

隔离 Cloud 实例已完成管理员登录、创建分组、创建高级运营/普通运营用户和角色会话验证；响应返回的用户均使用数值 UID、角色、分组与授权游戏。测试数据仅存在于临时验收数据库，未写入项目业务库。

## 尚需人工验证

管理员在真实 Web 中完成创建、筛选、修改、重置密码和禁用的页面走查尚未执行，不能以构建成功或 API 验证替代。
