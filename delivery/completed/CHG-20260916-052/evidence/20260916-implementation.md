# M3-B～E 实现证据（2026-09-16）

## 自动化验证

- Cloud：`go test ./...` PASS（contentpool、cloudagent、app 及全仓包）
- Agent：`./scripts/test.sh` PASS（85 tests；M3 discovery adapter/executor 已移除，M2 能力回归通过）
- Web：`npm test` PASS（20 files/76 tests）；`npm run build:cloud` PASS；`npm run build:desktop` PASS
- 关键语义：分享链接支持单条/批量；关键词和博主搜索结果在 `crawl_tasks.result_json` 中保留，确认选中后才创建 `source_content`；策略定时按配置时区计算。
- 分仓提交：Cloud `4720fc5`；Agent `1e137e4`；Workspace 本记录所在提交。

## 真实性边界

本记录只记录代码和自动化验证；未配置真实 Douyin 凭据时，不将 mock/fixture 结果写作真实外部采集验收。M3 discovery 现由 Cloud Crawler 执行，真实端到端需在 Cloud 服务端环境变量具备后补充脱敏请求、任务 ID、内容池数据库读回和页面证据。
