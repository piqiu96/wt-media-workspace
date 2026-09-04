# Task 3 前置：真实资源与 CDP 关键发现

日期：2026-08-05
CHG：CHG-20260805-032（M2-B 社媒账号收口）
状态：发现记录（Task 3 平台识别的依据）

## 用户提供的真实资源

1. **百家号账号**（已登录 BitBrowser 窗口）：比特序号 46，profile `dadb60405c354150a42811540654814f`（名称"路-华为"，分组"夹心海苔"，备注"百家号-牛逼"），已打开百家号后台 `https://baijiahao.baidu.com/builder/rc/content`
2. **B站 接码链接（香港号）**：手机号 `4208560`，接码 API `http://217api.com:9900/api/sms/getcode?token=685126570fdb729af167fba037f1a485`——登录 B站/获取验证码用（Task 3 端到端 / M2-D 接码上号）

## 关键发现 1：本版 BitBrowser（云手机）无 `/browser/cookie` API

- Agent `bitbrowser.read_cookies()` 调用 `POST /browser/cookie`，本版本返回 **404 Not Found**
- 探测 `browser/cookie`、`browser/getCookies`、`browser/list-cookie` 均不存在
- 正确读取 Cookie 需走 **CDP**（DevTools 端口，`Network.getAllCookies`），已用原生 WebSocket 验证可行
- 影响：Agent 现有 account_check 的 Cookie 读取路径在本环境是坏的（B4-1 从未端到端验证过）；B3-1 同步读 Cookie 同样依赖该坏路径

## 关键发现 2：百家号 UID 在页面 JS（window.user_id），BDUSS 为加密二进制

- 百家号窗口 DevTools 页面 `https://baijiahao.baidu.com/builder/rc/content` 上：
  - `window.user_id = eccf03edc1a5bafad166bfe355df7bc7`（32 位 hex，百家号账号 UID）
- BDUSS（192 位，`.baidu.com`）解码后为二进制加密格式，无法直接提取 UID/昵称
- 识别 Cookie 键：BDUSS/STOKEN/PSTM/BAIDUID（`.baidu.com`）、PHPSESSID/bjhStoken/devStoken（`baijiahao.baidu.com`）
- 影响：百家号账号识别的 UID 需从**页面**（CDP `Runtime.evaluate` `window.user_id`）读取，而非 Cookie 解析；昵称/头像需平台 API 或页面读取

## Task 3 结论：Agent 需新增 CDP 能力

为实现平台身份真实识别（Bilibili/百家号/抖音的 UID/昵称/头像），Agent 需要：
1. **CDP 读 Cookie**：替代坏的 `/browser/cookie` API（`Network.getAllCookies`）
2. **CDP 页面求值**：`Runtime.evaluate` 读取 `window.user_id` 等页面状态（百家号）
3. **平台 API 回填昵称/头像**：服务端调用（Bilibili card API 等），避开浏览器 CORS

这同时修复 B3-1 同步读 Cookie 的底层缺陷（其 `read_cookies` 在本版本会失败）。
