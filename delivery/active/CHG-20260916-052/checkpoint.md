# Checkpoint

- Completed：M3-B～E 运行时代码、Web 入口和 Douyin Agent 适配已实现；搜索结果采用“任务结果→人工选择→内容池”两步语义。
- Current：ACTIVE；代码验证及最新本地自测环境启动门禁已通过。
- Next：由产品侧按走查清单验收；真实接口环境具备后补做外部读回。
- Blockers：真实 Douyin 凭据/接口可用性不在仓库内，需按环境变量提供后才能做真实外部读回。
- Verification：Cloud `go test ./...` PASS（含团队权限、选择入池、批量链接、时区调度测试）；Agent `./scripts/test.sh` PASS（90 tests）；Web Vitest PASS（20 files/76 tests），Cloud/Desktop builds PASS（仅既有 chunk size/dynamic import warnings）；`m2b-local-acceptance.sh all` PASS（Cloud/Agent/BitBrowser mock/Desktop DMG/login smoke）。
