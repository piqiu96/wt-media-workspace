# CHG116 验证

2026-11-05，基于本 CHG 的 Cloud 源码与固定开发数据库。独立后端审查未发现严重问题；本记录是机器检查，不代替用户人工签收。

- `python3 scripts/wt.py chg verify CHG-20261105-116`：通过，包含 modules 测试、环境、Web/Desktop 构建新鲜度、DMG 与登录检查。DMG 启动后的独立 Agent 端口交接未完成；已用统一开发入口恢复服务后验证通过，原生 Desktop 交接在 CHG118 继续检查。
- `go test ./internal/modules/production/... -count=1` 与 `go test ./internal/modules/...`：通过。
- `WT_MEDIA_CLOUD_HOME="$PWD" WT_MEDIA_TEST_LIVE_DB=1 go test ./internal/modules/production/repository -run '^(TestLiveMergedAttemptReviewIsAtomicSingleUseAndCleanupGuarded|TestLiveAttemptReviewMigrationPreservesFactsAndRejectsOrphans|TestLiveManualBatchExpansionOwnerUsageReplayAndRemake)$' -count=1 -v`：通过。覆盖负责人代办、组／份展开、重放／异内容冲突、再次制作、局部失败冻结、写入失败整体回滚、核实单次恢复、清理守卫、微秒事实保真与孤立核实阻断。测试自清理，不伪造生产历史。
- 提供方 OpenAPI 验证、四份 YAML 唯一键／引用检查、36 个运行时方法路径对齐：通过。核实 GET 与三个旧策略读取已移除，核实 POST 权限保留。
- 前端定向回归与 Cloud/Desktop 构建通过，页面证据见同目录 `ui-verification.md`。
- `git diff --check`：通过。

## 真实操作

浏览器连接实际 Cloud，不拦截响应、不使用模拟数据。跨页和来源切换保留选择；取消选择未发素材关系写入；“使用所选”才写入负责人关系并请求准备。管理员显式确认再次制作后创建批次 30、任务 616；Worker 使用真实 FFmpeg 成功生成成片 82，4 秒、69,142 字节。输入准备、合成、上传及提交都有实际起止时间与结果。成片访问接口核验成功。

脱敏对账见 `task616-result.json`；仅保存业务 ID、步骤和完整性事实，不保存 Cookie、签名 URL 或凭据。截图覆盖任务批次、选择素材、参数编辑及任务信息／执行记录。成片管理后续改动与完整角色／下载验收由 CHG117/118 完成。
