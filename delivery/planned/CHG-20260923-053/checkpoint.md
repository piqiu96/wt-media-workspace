# Checkpoint

- 状态：PLANNED（未激活）。用户已于 2026-09-23 确认方案，并按 decision 排在 M3 收尾之后实施。
- Completed（登记阶段已完成的治理动作）：
  - ADR-0016 已提交（workspace `9ef8039`），并按 ADR-0016 改写工程架构基线 §2.2（移除 Cloud Agent 的抖音关键词和作者监控，与 ADR-0015 对齐）、§1.3 原则四（平台差异改指 `clients/<platform>`）、§5.2（推荐目录按新结构重写）、§5.4（分层关系重写并写明依赖禁向）、§5.5（平台目录改 `clients/<platform>`）、§5.6（`/healthz` 冻结 + 新增 `/api/v1/health`）、§5.8（数据目录内部分类、配置不在数据目录内）与附录 A.4。
  - 重构前基线已实测记录，见 `evidence/20260923-baseline.md`。
  - `wt-media-agent` 工作区既有脏文件（`uv.lock` 的 pyinstaller 构建组闭包、`packaging/` 与 `patches/` 空占位目录的删除）已在登记阶段单独提交。
- Current：未开始实施，不占用 active 名额。
- Next：待 M3（`CHG-20260916-052`）收尾、`delivery/active` 名额释放后激活本 CHG，再按 Task 1～7 顺序推进，每步以 `bash scripts/test.sh` 验证后单独提交。
- Blockers：`delivery/active` 只允许一个 CHG（`scripts/prepare_ai_workspace.py` 硬校验），本 CHG 与 M3 不能同时 active。
- 注意：ADR-0016 与工程基线描述的是**已确认的目标设计**，而 `wt-media-agent` 代码在激活实施前仍停留在旧结构。二者在此期间不一致属预期，激活实施后收敛。工程基线的定位本就是「当前系统应该如何设计」，不表示现状。
