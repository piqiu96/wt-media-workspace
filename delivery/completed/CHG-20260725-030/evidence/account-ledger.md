# 媒体账号台账字段与状态规则验证

日期：2026-07-25

## 修改事实

- `AccountsPage.vue` 新增/收口媒体账号列表字段：
  - 系统ID；
  - 平台；
  - 平台UID；
  - 头像；
  - 游戏；
  - 绑定窗口；
  - 登录状态；
  - 业务状态；
  - 最近检查；
  - 可执行结论；
  - 标签和备注摘要。
- 新增账号入口从“新建账号台账”改为“新增账号”。
- 绑定窗口展示改为包含：
  - Cloud窗口系统ID；
  - 窗口名称；
  - BitBrowser Profile ID。
- 新增账号表单允许先不绑定游戏；页面明确提示启用执行前必须绑定游戏。
- 可执行结论新增“未绑定游戏”与“绑定窗口已停用”原因。
- `mediaaccount.Service.CreateAccount` 允许创建无游戏账号；如果提供游戏，仍按角色和游戏授权校验。
- 当前 CHG 未实现批量检查；源码测试明确锁定页面不出现“批量检查”入口。

## 验证

- `npm test`：PASS，9 files / 32 tests。
- `npm run build`：PASS，存在既有 chunk size warning。
- `env GOCACHE=/Users/aqiuye/Develop/workspace/wt-media/wt-media-cloud/.cache/go-build go test ./internal/modules/mediaaccount ./internal/modules/profilebinding ./internal/modules/profileguard`：PASS。

## 结论

媒体账号台账已向 M2-B 目标字段和状态语义收口；“新增账号可先不绑定游戏，但不可执行前必须绑定游戏”规则已在 Cloud 和页面同步。
