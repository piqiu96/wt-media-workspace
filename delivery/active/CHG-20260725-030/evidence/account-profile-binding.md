# 媒体账号绑定/换绑窗口验证

日期：2026-07-25

## 修改事实

- 绑定窗口选择项和列表展示使用统一标签：
  - `系统ID <cloud_profile_id> / <窗口名称> / BitBrowser <bit_profile_id>`。
- 账号可先作为台账存在，不绑定游戏、不绑定窗口。
- 创建时如果填写游戏，Cloud 仍按角色与游戏授权校验；空游戏不绕过后续可执行判断。
- 可执行结论明确阻断：
  - 未绑定游戏；
  - 未绑定窗口；
  - 绑定窗口已停用；
  - 未完成真实检查。
- 继承已有 Cloud 服务规则：
  - 只能绑定本人授权 active 窗口；
  - 同一 Profile 同平台最多一个媒体账号；
  - 绑定/解绑/换绑后登录状态重置为 `unknown`，最近检查时间清空。

## 验证

- `env GOCACHE=/Users/aqiuye/Develop/workspace/wt-media/wt-media-cloud/.cache/go-build go test ./internal/modules/mediaaccount ./internal/modules/profilebinding ./internal/modules/profileguard`：PASS。
- `npm test`：PASS，源码测试确认绑定窗口标签包含系统ID、窗口名称和 BitBrowser Profile ID。

## 结论

媒体账号绑定/换绑窗口选择已满足运营可识别性；Cloud 服务继续负责授权、归档和同平台唯一性校验。
