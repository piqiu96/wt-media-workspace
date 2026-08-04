# A2 恢复 Cloud 配置 502 修复记录

日期：2026-08-05
CHG：CHG-20260725-031（M2-B 浏览器窗口收口）
所属验收项：A2 恢复 Cloud 配置（Diff 反向：恢复 Cloud 配置→写回 BitBrowser→读回验证）

## 现象

打包 Desktop GUI 验收时，「恢复Cloud配置并读回验证」报错：

```text
写回BitBrowser失败: 502 Bad Gateway
{"error":{"code":"bitbrowser_response_error","message":"BitBrowser request failed: 请传入 browserFingerPrint"}}
```

## 根因

- BitBrowser `/browser/update` 端点**强制要求 `browserFingerPrint` 字段**（create 与 update 共用该端点）。
- 新建窗口（A3）能成功，是因为 `_create_profile_payload` 有 `payload.setdefault("browserFingerPrint", {})`；
- 恢复流程（Agent `update_profile`）直接透传调用方 payload，**没有传 browserFingerPrint** → BitBrowser 拒绝 → 502。
- 既有测试只断言了 create 的 fingerprint，`update_profile` 无 payload 断言，导致漏网。

## 修复决策（正确性优先）

**不传空对象**：`browserFingerPrint` 含代理/UA/硬件等浏览器身份信息，update 传 `{}` 会让 BitBrowser 重置指纹、改变浏览器身份，对已登录账号有风险。

正确做法（`wt-media-agent`）：
- `update_profile` 若调用方未提供 `browserFingerPrint`，**先从 BitBrowser 本地读回当前指纹并原样传回**，指纹不离开本地运行时（符合 `BitProfile` 白名单 + `secret_policy`）；
- 读不到当前指纹时**报错拒绝执行**，不静默降级为 `{}`；
- 调用方显式传入指纹时直接使用，不做额外扫描。

涉及文件：
- `wt-media-agent/src/wt_media_agent/runtimes/bitbrowser.py`：新增 `_read_profile_fingerprint`；`update_profile` 保留当前指纹。

## 测试

- `tests/test_bitbrowser_runtime.py` 新增：
  - `test_update_profile_preserves_current_fingerprint`：update 扫描读回当前指纹并传回；
  - `test_update_profile_keeps_caller_fingerprint_without_scan`：显式指纹不扫描；
  - `test_update_profile_raises_when_fingerprint_unreadable`：读不到时拒绝且不发 update 请求。
- 适配 `test_profile_mutations_use_long_timeout`（update 现在先本地扫指纹）。
- `python -m unittest discover -s tests`：66 tests PASS。

## 验证状态

- 代码修复 + 单测 PASS。
- **待用户 GUI 重验 A2**：重建打包 Desktop（内嵌新 Agent）后，对产生 Diff 的窗口执行「恢复Cloud配置并读回验证」，确认不再 502、BitBrowser 被写回 Cloud 配置、重扫读回一致、且窗口指纹未被重置（重新打开窗口确认浏览器身份未变）。
- 若重验发现代理配置（proxyMethod 等）相关问题，另行处理。
