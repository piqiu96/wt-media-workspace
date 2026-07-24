# Diff 与窗口停用语义验证

日期：2026-07-24

## 修改事实

- 无 Diff 时，扫描结果抽屉只显示“本机窗口与Cloud记录一致，无需处理”，不显示接受/恢复/取消按钮。
- 有 Diff 时才显示：
  - 接受本地变化；
  - 恢复Cloud配置并读回验证；
  - 取消变更。
- 浏览器窗口操作栏中的“删除”已改为“停用”。
- Cloud `DeleteProfile` 实现已改为更新 `browser_profiles.local_status = archived`，不删除 Cloud 记录。
- 停用不会调用 BitBrowser 删除接口，不删除本地窗口，不删除账号历史。

## 验证

- `go test ./internal/modules/profilebinding`：PASS
- 新增/更新测试确认 `DeleteProfile` 只归档 Cloud 镜像，不删除记录。

## 结论

窗口删除语义已收口为 Cloud 镜像停用/归档；本机 BitBrowser Profile 不会被删除。
