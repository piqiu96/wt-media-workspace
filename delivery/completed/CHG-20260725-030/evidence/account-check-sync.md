# 检查/同步账号信息验证

日期：2026-07-25

## 修改事实

- 账号详情按钮从“检查账号”收口为“检查/同步账号信息”。
- Desktop 账号详情新增提示：
  - 用户可在 BitBrowser 窗口中人工登录；
  - 返回系统点击“检查/同步账号信息”；
  - 系统读取真实平台身份并回填 Cloud。
- 单项检查/同步继续复用既有 B4-1 链路：
  - Cloud 创建 sensitive account check 授权；
  - Desktop Tauri/Rust 做 preflight；
  - Local Agent 打开 BitBrowser Profile 并读取平台身份；
  - Cloud 保存平台 UID、昵称、头像、登录状态和最近检查时间。
- 本 CHG 不实现批量检查；页面源码测试确认未出现“批量检查”入口。批量账号检查如需完整业务体验，应作为后续独立 CHG 或 M2-B 补充收口处理。

## 验证

- `npm test`：PASS，9 files / 32 tests。
- `npm run build`：PASS。
- `env GOCACHE=/Users/aqiuye/Develop/workspace/wt-media/wt-media-cloud/.cache/go-build go test ./internal/modules/mediaaccount ./internal/modules/profilebinding ./internal/modules/profileguard`：PASS。

## 结论

单项“检查/同步账号信息”已覆盖自动检查和人工登录后回填入口；批量检查边界明确，不在本轮冒进实现。
