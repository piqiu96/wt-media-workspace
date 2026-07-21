# CHG-20260721-020 治理范围审计

## 审计原则

- `PASS`：现有 Evidence、提交和本次复验可以证明该阶段性技术结果。
- `PARTIAL`：实现或自动化存在，但 Milestone 要求的用户操作、真实外部副作用、读回或人工验收未闭环。
- `NOT PROVEN`：缺少足以重现该声明的证据。
- 代码、路由、任务类型或页面存在，不能单独证明业务闭环完成。

## 事实表

| 声明 | Evidence | Commit / 本次复验 | 闭环卡 | 结果 |
|---|---|---|---|---|
| Web API client 测试注入恢复，8 项通过 | `task-2-web.md`、`web-builds.md` | Cloud `daf423d`；2026-07-22 Web 8/8、Cloud/Desktop build PASS | M2-A | PASS |
| M2 与产品计划校验脚本恢复 | `task-3-governance.md` | Workspace `9773ea7`；2026-07-22 两个治理脚本 PASS | M2-A | PASS |
| 媒体账号越权读取被拒绝 | `task-4-authorization.md` | Cloud `b419244`；2026-07-22 Cloud 全量 Go 测试 PASS | M2-A | PASS |
| 失效会话停止领取并进入安全排空 | `task-5-session-invalidation.md` | Cloud `985644f`、Agent `1e3e96f`；2026-07-22 Cloud PASS、Agent 48/48 PASS | M2-A | PASS |
| BitBrowser 首次绑定与重绑审计事件 | `task-6-binding-audit.md` | Cloud `c009523`；2026-07-22 Cloud 全量 Go 测试 PASS | M2-A | PASS |
| 三角色 UI/API、401/403 与真实绑定人工验收完成 | `m2-a-automated-verification.md` | Evidence 明确记录 manual acceptance pending | M2-A | NOT PROVEN |
| Profile 创建、开关、更新已任务化并由 Agent 执行读回 | `m2-b-foundation.md`、`profile-id-boundary.md`、`task-result-readback.md` | 2026-07-22 Cloud/Agent 自动化 PASS | M2-B | PARTIAL |
| Profile 绑定向导、完整 Diff、恢复系统配置、单个/批量账号检查形成用户闭环 | `m2-b-foundation.md` | Evidence 明确列为 remaining；无真实 Profile 变更验收 | M2-B | NOT PROVEN |
| 代理任务、授权分配、写入与主机端口读回基础存在 | `m2-c-foundation.md`、`proxy-assignment.md`、`sync-fast-path.md` | 2026-07-22 Cloud/Agent/Web 自动化 PASS | M2-C | PARTIAL |
| 导入预览无副作用、配额与占用校验、真实代理写入后 Profile 可打开 | `m2-c-foundation.md`、`proxy-assignment.md` | 无完整真实代理/Profile 用户验收 | M2-C | NOT PROVEN |
| Cookie 读写任务边界、脱敏结果和 Cloud 状态投影存在 | `cookie-read-boundary.md`、`cookie-result-projection.md`、`task-redaction.md` | 2026-07-22 Cloud/Agent 自动化 PASS | M2-D | PARTIAL |
| Cookie 实际写入/读回、身份回填、三种开户、部分成功与精确重试闭环 | `cookie-result-projection.md`、`retry-controls.md`、`web-sensitive-redaction.md` | Evidence 明确不声明真实外部 Cookie refresh；输入尚未接最终 permit 链路 | M2-D | NOT PROVEN |
| Desktop 持有和停止 Agent 子进程基础 | `desktop-agent-lifecycle.md` | 2026-07-22 Cargo 2/2 PASS | M2-E | PARTIAL |
| 打包 Sidecar、真实 Desktop 操作、恢复矩阵和最终人工验收完成 | `desktop-agent-lifecycle.md`、`integrated-gates.md` | Evidence 明确记录 packaged-app smoke 与真实依赖验收仍待完成 | M2-E | NOT PROVEN |
| 普通任务详情对敏感字段脱敏 | `task-redaction.md`、`web-sensitive-redaction.md` | 2026-07-22 Cloud/Web 自动化 PASS | 横切 | PASS |
| 失败或取消任务可创建新尝试并保留历史 | `retry-controls.md` | 2026-07-22 Cloud/Web 自动化 PASS | 横切 | PASS |

## 本次复验

| 命令 | 实际结果 | 状态 |
|---|---|---|
| Cloud `go test ./...` | 所有包通过 | PASS |
| Agent `PYTHONPATH=src python3 -m unittest discover -s tests -q` | 48 项通过 | PASS |
| Web `npm test -- --run` | 8 项通过 | PASS |
| Web `npm run build:cloud` | 构建通过，只有既有 chunk 提示 | PASS |
| Web `npm run build:desktop` | 构建通过，只有既有 chunk 提示 | PASS |
| Desktop `cargo test --workspace` | 2 项通过，只有既有 unused 警告 | PASS |
| Workspace `verify_m2_acceptance.py` | 静态矩阵通过，并提示真实依赖需单独 Evidence | PASS |
| Workspace `verify_product_master_alignment.py` | 对齐校验通过 | PASS |

## 结论

CHG-020 可以作为“跨 M2 的阶段性技术基础工作”归档，但不能声明 M2-A～E 任一业务闭环已经完成：M2-A 仍缺人工角色与真实绑定验收；M2-B～E 均缺 Milestone 要求的用户纵向链路或真实依赖验收。

下一项必须是 M2-A 验收收口 CHG。只有 M2-A 的全部成功事实通过后，才能进入 M2-B。
