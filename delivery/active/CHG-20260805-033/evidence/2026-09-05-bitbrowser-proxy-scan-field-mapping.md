# BitBrowser 窗口代理扫描字段映射修复

日期：2026-09-05  
CHG：CHG-20260805-033 / Task 6

## 根因

BitBrowser `POST /browser/list` 对窗口代理使用 `host`、`port` 字段。Agent 的安全快照错误读取了 `proxyHost`、`proxyPort`，导致已配置代理的窗口以空地址、端口 0 传递给 Cloud Diff；Diff 因此没有可比较的本机代理记录。

## 修复

- Agent 的列表快照改为读取官方 `host`、`port`。
- 创建窗口及同步代理写入改为提交官方 `host`、`port`。
- 保留既有写后扫描读回验证；未改变 Cloud 台账、窗口关系或代理凭据处理。

## 验证

| 操作 | 预期 | 实际 | 结果 |
| --- | --- | --- | --- |
| 新增适配器失败测试 | 旧映射不能读出官方 `host`/`port` | 测试在修复前断言失败 | PASS（Red） |
| 针对性自动测试 | 扫描、创建、同步 mutation 均使用官方字段 | 3 项通过 | PASS |
| Agent 全量测试 | 无回归 | 78 项通过 | PASS |
| 强制重建环境 | 最新 Cloud、Agent、Desktop DMG 与 BitBrowser 均可用 | 迁移 0/27、健康/资源/DMG/登录门禁全部通过 | PASS |
| 真实 BitBrowser 扫描 | 配置了代理的窗口应带非空地址和端口 | 读取到 11 个 SOCKS5 窗口，全部具有非空地址和有效端口 | PASS |

实机扫描只记录计数和字段存在性；未在本证据中保存账号、Cookie 或代理凭据。
