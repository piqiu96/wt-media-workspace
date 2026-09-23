# Checkpoint

- Completed：按 ADR-0015 将 M3 discovery 执行边界纠偏为 Cloud-owned Crawler；Cloud 不再创建/分配 discovery Agent task，Agent 中的 M3 遗留 adapter/executor 已清理；搜索结果仍采用“任务结果→人工选择→内容池”两步语义。修复抖音 `/dyRank` 搜索必须传 `ck` 表单字段的问题（Cloud `0548b22`），并提供管理员受控调度入口（Cloud `e18a2b1`；会话替换可配置，Workspace `fdd9e66`）。2026-09-23 按用户确认与实施事实回写自动转素材（产品基线 §4、ADR-0013 第 3 条）与 `partial_success`（产品基线 §5、ADR-0013 第 7 条），并将 M3 产品基线落回 `docs/product/`。
- Current：ACTIVE；Cloud Crawler、Cloud Scheduler、Web 入口和治理记录已同步，自动化验证通过。2026-09-23 已按 Cloud 仓库实施结果同步 M3 阶段状态（`delivery/milestones/M3-content-discovery-v2.md` 第 2.1 节）：A～E1 有真实证据，C2/E2 已暂停，E3 未开始。
- Next：进入 E3（CHG-20260915-051）综合验收与用户签收；C2/E2 已暂停，不再作为 E3 前置。关键词链路的真实外部读回需先具备 Cloud Douyin 凭据/接口环境；凭据以 `config/credentials/douyin.toml` 形式提供给 Cloud（2026-09-23 更正：Cloud 运行时只读 `config/` 下的 TOML，架构边界测试禁止 `os.Getenv`；`WT_MEDIA_DOUYIN_*` 环境变量与 `wt-media-cloud/.env.local` 对其无效）。定时调度入口为 Cloud `cmd/discovery-scheduler`，Worker 为 `cmd/discovery-worker`（原 `scripts/run-discovery-scheduler.sh`、`scripts/run-discovery-worker.sh` 已在 Cloud `36a7cfe` 删除，云仓 `scripts/README.md` 已于 Cloud `aaf66c5` 更正）。
- Blockers：真实 Douyin 凭据/接口可用性不在仓库内，需以 `config/credentials/douyin.toml` 形式提供给 Cloud（2026-09-23 更正：Cloud 运行时只读 `config/` 下的 TOML，环境变量对其无效）后才能做真实外部读回。不以 BitBrowser/Agent mock 替代。
- Verification：Cloud `go test ./...` PASS（含团队权限、选择入池、批量链接、时区调度、Crawler 映射、`ck` 搜索字段、受控调度入口和 discovery task 禁用测试）；Agent `./scripts/test.sh` PASS（85 tests，M2 回归）；Web Vitest PASS（20 files/76 tests），Cloud/Desktop builds PASS（仅既有 chunk size/dynamic import warnings）；最新 `scripts/m2b-local-acceptance.sh up --force-restart` + `verify` PASS，Cloud `18080`、Agent `8765`、脱敏 BitBrowser mock、Desktop assets/DMG、admin 登录 smoke 均通过。配置真实凭据后，运营账号关键词搜索任务已返回 `status=success`、`errcode=0`；本地调度脚本返回 `triggered=0`，运营账号调用被拒绝 `HTTP 403`，禁用会话替换时已有管理员会话返回 `HTTP 409`（本地门禁不作为 M3 真实 Douyin 外部验收）。

## 2026-09-23 M3 全量验收结论

- 验收在 Cloud `aaf66c5` 上完成：`run-manifest.json` 共 106 步，87 PASS / 7 FAIL / 1 NOT VERIFIED / 1 ADJUDICATED。
- 唯一硬阻断是 D-scheduler：独立 `cmd/discovery-scheduler` 首次 tick 即 panic 退出，**无人值守的真实周期触发本期未交付**（管理员 `run-due` 受控端点与周期 tick 共用实现，但不等于无人值守触发）。
- 其他缺陷：D1 策略重名返回 500、D2 `schedule` 无服务端校验、D3 `/run` 可重复排队、D9 上游空返回透传为成功；`material_failed` 记 NOT VERIFIED（未构造公开 API 触发路径）。
- 独立的只读业务流转视图按用户 2026-09-23 裁定移出验收范围（ADJUDICATED），不作为缺口；ADR-0013 第 8 条的禁止性约束不变。
- 结论：**未标记 M3 DONE**，M3 保持 `IN_PROGRESS`。详细证据见 `evidence/m3-e3-acceptance-20260923/`（判定见 `14-verdict.md`，缺陷与安全问题见 `12-defects-and-security.md`）。
