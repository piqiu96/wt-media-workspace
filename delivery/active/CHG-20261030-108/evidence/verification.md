# CHG-108 验证记录

## 提交组合

- Cloud: 52e9c17（含前续681f341、55d5fec）
- Agent: ec766de
- Desktop: 56f0600
- Workspace: 当前 CHG 与正式文档提交

## 自动验证

| 动作 | 预期 | 实际 |
| --- | --- | --- |
| Cloud `go test ./internal/modules/mediaaccount/... -count=1`，注入本机测试DSN | 检查结算和原子资料更新正确 | PASS；实际MySQL使用同连接临时表，不改现有账号；验证并行备注/凭证保留、旧编号/重复/窗口变化拒绝、事务回滚、筛选分页与计数 |
| `go test ./cmd/server ./internal/bootstrap/...` | 启动装配可编译 | PASS |
| Vue 账号、窗口、角色、路由、错误反馈定向测试 | 消费方通过 | PASS，14文件111项 |
| `npm run build:cloud` / `build:desktop` | 两端可构建 | PASS；存在既有大chunk提示 |
| Agent `test_local_account_check.py` / `test_dependency_boundaries.py` | 实时事实与分层通过 | PASS，9项/33项；另cookie读取3项通过 |
| Desktop `cargo test --manifest-path src-tauri/Cargo.toml commands::` | 命令层回归 | PASS，125通过、5个既有忽略 |
| Workspace docs/config/delivery/master/M2静态校验 | 正式事实与组合一致 | PASS |

## 真实环境与平台

- 本机固定数据库 wt_media_cloud；迁移082、083各执行一次成功。执行前账号7条，废弃账号组0条且无外部表引用；不修改历史迁移链，不操作外部窗口/Cookie。
- `bin/control.sh start` 初次强制重建通过Cloud、Agent、BitBrowser、开发入口、CORS、资源、DMG、登录冒烟并挂载启动新包。最后一次源提交后的组合重建和页面验收继续执行中。
- 用户授权测试窗口：“测试账号”序号51、“路-华为”序号46。分别经真实Agent处理函数与BitBrowser读取取得正常身份及昵称/UID/头像；全程不调用Cookie写入能力。此处为平台读取证据，完整业务闭环需下面单独确认。
- 本机验收账号operator01原凭据不符合环境技能约定，按技能通过管理员重置接口恢复约定测试密码；不更改平台密码或Cookie。

## 业务闭环

待最新组合的桌面页面、Cloud落库与三角色走查结束后填写，不以当前平台读取或单测代替完成结论。
