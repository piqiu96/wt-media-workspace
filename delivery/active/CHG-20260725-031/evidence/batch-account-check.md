# 批量账号检查逐项执行验证

日期：2026-07-25

## 修改事实

- `AccountsPage.vue` 在 Desktop 多选账号后展示“批量检查/同步”入口。
- Cloud Web 不展示批量检查入口。
- 批量检查采用页面内串行逐项执行，不创建 Cloud 通用 task，不创建假批次成功状态。
- 每个可执行账号复用单项检查链路：
  - Cloud `POST /api/v1/media-accounts/:id/check` 创建本地敏感操作授权；
  - Desktop Tauri/Rust 执行 preflight；
  - Local Agent 检查 BitBrowser Profile 内的平台身份；
  - Cloud `POST /api/v1/media-accounts/:id/check/result` 回填结果。
- 不可执行账号在执行前被跳过并展示 `executableText` 原因。

## 验证

- `npm test`：PASS，9 files / 32 tests。
- `npm run build`：PASS，存在既有 chunk size warning。
- `env GOCACHE=/Users/aqiuye/Develop/workspace/wt-media/wt-media-cloud/.cache/go-build go test ./internal/modules/mediaaccount ./internal/modules/profilebinding ./internal/modules/profileguard`：PASS。

## 结论

批量账号检查入口和逐项串行执行路径已接入；每个账号仍以真实单项检查结果为准，不以批量请求成功代替业务成功。
