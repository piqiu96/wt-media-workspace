# CHG-20261013-086：M4-C8 综合验收（真实视频、对象存储、故障恢复与 UI 对账）

- Status: IMPLEMENTING
- Level: M
- Milestone: `delivery/milestones/M4-content-production.md`
- Closure anchor: §3.1 M4-C8「真实视频、对象存储、故障恢复和 UI 综合验收」；§7 M4-AC-01～12 十二项逐项对账；§8 M4 DONE Gate
- Product: `docs/product/prd/详细文档/第五章_素材生产.md` 第五章全章（M4 范围）
- Engineering: `docs/engineering/specs/2026-09-24-m4-m5-cloud-content-production.md`
- Decision: `docs/decisions/0017-m4-m5-cloud-owned-content-production.md`、`docs/decisions/0021-compose-four-layer-model.md`
- Affected repositories: `wt-media-cloud`、`wt-media-agent`、`wt-media-desktop`（只读证据；预期无运行时代码改动）
- Current repositories: `wt-media-cloud`、`wt-media-agent`、`wt-media-desktop`
- Activation: CHG-20261013-085（M4-C7 下载中心）已归档；用户指示 M4 剩余 CHG 连续执行、2026-10-14 晨统一验收。按里程碑顺序进入 M4-C8。

## 1. 独立结果

M4 十二项验收要求（M4-AC-01～12）逐项拿到真实链路读数：机器可证项在真实环境（真实 FFmpeg、真实对象存储、真实 Local Agent、真实 MySQL/API）重新实测或引用带日期的真实环境证据；需要人眼与签收的 UI 腿（Desktop/Cloud Web 页面走查）逐项登记为待用户签收，不以截图、任务记录或 API 200 充数。汇总表落在本 CHG 验收记录，M4 DONE Gate 的「用户签收」由用户晨间统一验收完成。

## 2. 范围

- 逐项对账：对 M4-AC-01～12 每项给出「本轮真实读数」或「带日期的真实环境证据引用（对应归档 CHG evidence 文件）+ 本轮复核该面未被后续改动触碰」；两者都不具备的项如实标 `UNVERIFIED`，不得标 PASS。
- 本轮真实链路复测（最小集）：真实合成→成片→预览→下载落盘→sha 校验（覆盖 AC-05/06/08/09 的机器腿），与取消/失败无双执行抽测（AC-07）。
- 权限与边界：三角色权限矩阵与越权探针（AC-11）、Desktop/Agent 无合成执行路径的边界扫描（AC-10）、三仓测试与独立提交核对（AC-12）。
- 证据登记：每项读数写入 `evidence/`，格式与既有 CHG 一致（命令/预期/实际/判定）。
- 用户签收清单：列出留待 2026-10-14 晨验收的 UI 腿与签收点，交用户逐条走查。

## 3. 明确不做

- 不改任何运行时代码：验收发现缺陷时回到对应 CHG 范围登记修复，不在本 CHG 顺手修。
- 不做 GUI 自动化走查：本机无法程序化驱动/截取 GUI（既有环境约束），页面走查是用户签收项。
- 不写 `published` 发布事实、不建 `publication`（M6 范围）。
- 不以 Mock 视频、页面截图、任务记录或构建成功替代真实成片与真实读数（M4-C8 关键约束）。
- 不重复归档 CHG 已完整留证的读数——引用并核对「该面后续未被改动」，不伪造新鲜感。

## 4. 有序任务与验收

| Task | 内容 | 验收方法 |
| --- | --- | --- |
| T-01 | 环境基线与素材盘点：bring-up、素材/策略/模板/成片现状、改动面核对（AC-01/03/04 前置） | 健康门 + 库/API 对照 |
| T-02 | 素材库与 my-materials 机器读数：四态视频状态、usage 创建/去重/移出/恢复、懒加载对照、任务快照不变（AC-01/02/03/04） | MySQL + API + 前后对照 |
| T-03 | 合成链真实复测：真实 FFmpeg 合成、落盘后创建成片、取消/失败/Worker 重启无双执行抽测（AC-05/06/07） | 真实探针 + 故障注入 |
| T-04 | 我的成片与下载中心真实复测：预览、来源追踪、归档、下载落盘、sha、进度终态（AC-08/09 机器腿） | 真实探针 + 前后对照 |
| T-05 | 权限矩阵与边界扫描、三仓测试与提交核对（AC-10/11/12） | 越权探针 + 边界扫描 + 套件读数 |
| T-06 | 十二项汇总对账与用户签收清单（UI 腿逐项列出），收口提交 | 汇总表 + governance |

## 5. 验收标准

1. M4-AC-01～12 每项在验收记录里有明确判定：PASS（带读数或带日期证据引用）、UNVERIFIED（如实登记）——不存在无判定的项。
2. 本轮真实链路复测全部真实依赖（真实 FFmpeg/对象存储/Agent/MySQL），清零带披露。
3. UI 走查与签收项完整移交用户，无静默省略。
4. governance verify exit 0；工作区与各仓提交边界干净。

## 6. Pending Questions

None.

## 7. 范围裁定（规划期）

- **证据引用 vs 新鲜读数**：M4-C8 是对账不是重做——在 061/082/083/084/085 已留真实读数、且对应代码面在其后未再被改动的项，引用原读数并核对改动面；链路核心（合成→成片→下载）在本轮用最新代码再跑一遍最小集，防止「证据是真的、代码已经变了」。
- **UI 腿**：AC-01/02/08 的 UI 部分与 M4 DONE Gate 的用户签收留待 2026-10-14 晨；本 CHG 把每条签收点写明（页面、路径、要点），不占用「PASS」。
- **无新决策**： twelve AC 均有既有裁定与契约，无需新增决策记录。
