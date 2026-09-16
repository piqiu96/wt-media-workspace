# Checkpoint

- Completed：按 ADR-0015 将 M3 discovery 执行边界纠偏为 Cloud-owned Crawler；Cloud 不再创建/分配 discovery Agent task，Agent 中的 M3 遗留 adapter/executor 已清理；搜索结果仍采用“任务结果→人工选择→内容池”两步语义。
- Current：ACTIVE；Cloud Crawler、Cloud Scheduler、Web 入口和治理记录已同步，自动化验证通过。
- Next：由产品侧按走查清单验收；真实 Cloud Douyin 凭据/接口环境具备后补做外部读回。
- Blockers：真实 Douyin 凭据/接口可用性不在仓库内，需按 Cloud 服务端环境变量提供后才能做真实外部读回；不以 BitBrowser/Agent mock 替代。
- Verification：Cloud `go test ./...` PASS（含团队权限、选择入池、批量链接、时区调度、Crawler 映射和 discovery task 禁用测试）；Agent `./scripts/test.sh` PASS（85 tests，M2 回归）；Web Vitest PASS（20 files/76 tests），Cloud/Desktop builds PASS（仅既有 chunk size/dynamic import warnings）；最新 `scripts/m2b-local-acceptance.sh up --force-restart` + `verify` PASS，Cloud `18080`、Agent `8765`、脱敏 BitBrowser mock、Desktop assets/DMG、admin 登录 smoke 均通过（本地门禁不作为 M3 真实 Douyin 外部验收）。
