# CHG115 验证

对应 Cloud 提交 `409062b`；固定本地 MySQL `wt_media_cloud`，087～090 迁移已实际应用。下列真实数据库测试用事务回滚隔离验收数据。

| 检查 | 预期 | 实际 | 结果 |
|---|---|---|---|
| 规则与设置 | 排除优先；缺失数据不按 0；每组独立且执行器校验 | Model／service／repository 回归通过；原始 Douyin statistics 区分已观测 0 与默认 0 | PASS |
| 真实批次 | 平台不乘份数，预览无写入 | `TestLiveMultiSettingPreviewAndConfirmation`：选 2 素材 × (2+3) 份=10 任务；预览前后任务、批次、运行记录行数不变 | PASS |
| 命令一致性 | 过期拒绝，同请求相同内容复用；不同内容拒绝 | 真实 MySQL 验证显示名不影响指纹、变更 token 拒绝、重放同 batch_id、已有未完成批次拒绝 | PASS |
| 定时行为 | 复扫幂等，立即执行不移动下次执行 | `TestLiveComposeScheduleDueAndRepeatScan` 通过；测试先结束旧批次再立即执行，符合新重叠保护 | PASS |
| Worker 保护 | 租约／并发／取消／提交旧保护不回退 | `go test ./internal/modules/...` 与 production 全包通过 | PASS |
| 共享前端 | 表单、预览、排序、客户端与模板参数行为 | compose 及 API 回归通过；Cloud／Desktop 构建通过 | PASS |
| 浏览器 | 底部操作可见，新增组保留配置，预览有依据 | 本机 Chrome 1440×1000：保存按钮 y931 高36；新增后2组；无 pageerror；真实预览显示素材指标值与跳过原因 | PASS |
| 环境与规范 | 最新服务、配置与文档通过 | `bin/control.sh start` 全流程完成；桌面接管后 Agent 未监听，首次 verify 失败；随后 `local_env.py up --force-restart` 恢复并重建，`wt.py chg verify` 全部通过 | PASS |

浏览器连接工具连续两次超时，未获得原生窗口截图；改用本机 Chrome 实际页面检查。浏览器截图临时位置 `/tmp/wt-content-qa/strategy-final.png`、`strategy-preview.png`。最终安装包全量功能与视觉由 CHG118 收口，本 CHG 不将安装包启动等同于内容生产验收。

独立审查修复：指纹展示字段误判、同请求不同内容、旧无效配置空批次、模板标记、源指标存在性、批次快照敏感地址脱敏、immediate 筛选及共同排序组件。人工任务新批次路径尚属 CHG116，成片 UI 属 CHG117；这些未用原型完成情况冒充已实现。
