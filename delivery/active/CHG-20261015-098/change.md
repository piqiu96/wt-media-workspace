# CHG-20261015-098：M5-C7 真实计划时间全链与 M4/M5 统一验收

- Status: IMPLEMENTING
- Level: M
- Milestone: `delivery/milestones/M5-automatic-production.md`
- Closure anchor: §6 M5-C 自动生产综合验收、§7 M5-AC-01/10～13、§8 DONE Gate
- Product: `docs/product/prd/详细文档/第五章_素材生产.md` §5.7～5.10
- Engineering: `docs/engineering/specs/2026-09-24-m4-m5-cloud-content-production.md` §5～7
- Decision: `docs/decisions/0017-m4-m5-cloud-owned-content-production.md`
- Current repository: `wt-media-workspace`
- Affected repositories: `wt-media-cloud`, `wt-media-agent`, `wt-media-desktop`（验收目标，运行时代码修改以复现缺陷为前提）
- Verification repositories: `wt-media-cloud`, `wt-media-agent`, `wt-media-desktop`
- Runtime implementation: none planned; any discovered defect is localized to its owner and recorded before repair

## 目标

高级运营在真实计划时间启用策略后，独立 Cloud Scheduler 创建批量任务，独立 Worker 按容量限制用真实 FFmpeg 和对象存储生成可播放成片；运营在 Cloud Web 与打包 Desktop 中看到相同状态，使用既有 Local Agent 下载成片。复跑 M4 人工生产与下载、故障恢复和旧路径扫描，完成 M4-H2 与 M5 的统一用户走查。

## 当前事实与差距

- M5-C1～C6（含 C2a）已机器验证并归档，当前没有 Active CHG，四个仓库工作区干净。
- M5-AC-01、10～13 仍为 `TODO`；此前单项测试和人工触发均不替代真实计划时间的全链证据。
- C7 需固定运行环境、明确真实对象和跨进程读回；不能只以 HTTP 200、任务行或模拟依赖判定通过。

## 有序任务

| Task | 可独立验证结果 | 验证 |
| --- | --- | --- |
| T-01 | 从当前源码确定性启动 Cloud、Agent、BitBrowser、Web 与打包 Desktop；健康、版本、登录、CORS 和配置均可读回 | `environment-bring-up` 全部 gate 与证据 |
| T-02 | 真实时间触发一批自动任务；核对计划时区、素材范围、上限、幂等、停用、混合结果和 Worker 容量/恢复 | 独立进程、MySQL、对象存储、FFprobe、API 对账 |
| T-03 | 自动成片在 Cloud Web 和打包 Desktop 可预览并经 Local Agent 下载；复跑 M4 人工生产/下载 | 页面与文件读回、Cloud/Agent 状态对账、M4-H2 走查记录 |
| T-04 | 代码/Migration/Contract 排除旧对象和 Agent 合成路径，按 M5 验收矩阵逐项收口并完成用户签收 | 扫描结果、差异复审、用户走查结论 |

## 验收

1. 真实 Scheduler 按计划时间创建任务，跨进程/重启不重复；批次和任务状态、数量上限及策略启停与数据库和页面一致。
2. 真实 Worker、FFmpeg、对象存储产生可播放自动成片；失败/恢复事实可追溯，无无限重试、重复执行或孤儿进程。
3. Cloud Web 与打包 Desktop 显示同一正式状态，自动与人工成片走同一 `composite_output` 和下载链路，Local Agent 实际落盘可播放文件。
4. M5-AC-01～13、M4 相关回归、旧路径扫描和用户最终走查均有证据；未通过项保持未完成，不以模拟或手动触发冒充真实调度。

## 不做

- 不新增生产规则表、第二套批次或成片对象、Agent 视频合成服务。
- 不将 C7 验证中发现的跨仓 Contract、Architecture 或 Ownership 变化直接混入修复；先回 Workspace 更新定义。

## Pending Questions

None.

## 验收记录

实施中；逐任务事实在 `evidence/`，进度在 `checkpoint.md`。
