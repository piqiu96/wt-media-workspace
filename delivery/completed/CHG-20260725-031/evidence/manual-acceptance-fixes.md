# 人工验收问题修复记录

日期：2026-07-25

## 用户反馈

1. BitBrowser 分组没有获取成功。
2. 创建窗口时不需要填写比特序号。
3. 点击创建没有反应，也没有提示。
4. 点击打开或关闭窗口不可用。

## 修复事实

- `wt-media-agent`：
  - BitBrowser `/group/list` 调用补充 `page` 和 `pageSize` 参数；
  - 分组接口已能返回真实分组：`测试组`；
  - BitBrowser 返回“浏览器正在打开中/已打开”时不再当作不可理解失败；
  - 底层 BitBrowser 请求失败会保留具体错误原因。
- `wt-media-cloud/web`：
  - 新建窗口弹窗移除“比特序号”输入；
  - 创建 payload 不再发送 `seq`；
  - 创建前校验窗口名称和真实 BitBrowser 分组；
  - 分组加载失败、分组为空、创建失败都在弹窗内显示明确错误。
- `wt-media-desktop`：
  - 已重新 `cargo build`，确保 Tauri 壳包含 B5 的分组、创建、打开、关闭命令。

## 验证

- `curl -X POST http://127.0.0.1:8765/api/v1/bit-browser/profile-groups`：PASS，返回真实分组。
- `curl -X POST http://127.0.0.1:8765/api/v1/bit-browser/profile-open`：PASS，返回 `opened`。
- `python3 -m unittest tests/test_local_profile_operations.py tests/test_local_account_check.py`：PASS，8 tests。
- `npm test`：PASS，9 files / 33 tests。
- `npm run build`：PASS，存在既有 chunk size warning。
- `cargo test`：PASS，8 tests，存在既有 dead_code warning。

## 当前验收环境

- Cloud：`http://127.0.0.1:18080` 健康；
- Desktop Web：`http://127.0.0.1:5174/` 可访问；
- Local Agent：`http://127.0.0.1:8765` 已重启并连接真实 BitBrowser；
- Tauri Desktop 壳已重启。
