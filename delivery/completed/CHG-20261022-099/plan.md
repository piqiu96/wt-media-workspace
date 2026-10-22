# CHG-20261022-099 实施计划

1. 收口 CHG 模板、Active 规则和治理校验；保留旧 CHG 兼容，验证单/多 Active 与依赖失败路径。
2. 增强 `prepare_ai_workspace.py`：按指定 CHG 生成可再生导航，移除 Git 跟踪；验证旧入口和多 CHG 选择。
3. 实现薄 `wt` CLI：只读取仓库映射与 CHG 元数据，启动/恢复/验证输出；环境和测试场景调用既有入口。
4. 保守清理默认加载规则冲突，更新 Skill 源和索引，不批量迁移旧脚本或历史归档。
5. 跑治理、上下文、Skill 与 CLI 测试；用现有 CHG 演练 start/resume、低风险 fast 和中风险 integration 的安全路径；核对四仓分支/工作区状态。

每阶段按测试红绿、diff 检查、Evidence、Checkpoint 和独立提交推进。`wt chg start` 对旧归档依赖缺少可机器核对的各仓提交时必须阻止启动，并指出需要人工补齐的证据，不自行视为已合并。
