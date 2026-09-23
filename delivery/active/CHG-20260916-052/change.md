# CHG-20260916-052：M3-B～E 内容挖掘自动化入口

- Status: ACTIVE
- Level: M
- Milestone: `delivery/milestones/M3-content-discovery-v2.md`
- 日期：2026-09-16
- 基线：`docs/product/M3-content-mining-v2.md`；ADR-0013、ADR-0015；团队隔离决策见 ADR-0014。
> 当前仓库：`wt-media-cloud`
> 预计影响仓库：`wt-media-agent`、`wt-media-workspace`
> 仓库说明：Agent 仅做 M3 遗留 discovery task/adapter 清理，M2 本地执行能力保持不变。

## 独立目标与范围

在 M3-A 内容池基础上交付人工入口与自动挖掘入口：分享链接导入、关键词搜索、关键词策略、挖掘任务记录及 Cloud-owned Douyin Crawler。搜索结果先保存在任务结果中，由运营选择后入池；链接导入与策略任务成功结果自动入池。策略不承担调度；Cloud Scheduler 只创建 `pending crawl_task`，Cloud Discovery Worker 原子领取并执行，不创建 Agent task。

博主搜索（C2）与作者策略（E2）已于 2026-09-23 暂停：本期不交付、不计入 M3 验收，入口、`author` 取值与字段保留，后续版本再评估（见 ADR-0013 增补记录）。

策略可配置自动转素材（`auto_material` / `material_rule` / 阈值）；任务状态含 `partial_success`（部分成功），可仅重试失败项。两项均由 2026-09-23 用户确认/实施事实回写产品基线，见 ADR-0013 第 3、7 条。

不建设通用工作流引擎、视频下载/存储、AI 评分、剪辑、发布互动和数据分析；B站/快手等仅保留渠道字段，不宣称已接入。

## 权限与数据边界

普通运营按业务团队隔离；同团队可见全部内容，管理员跨团队可见。Cloud 持有 `discovery_strategies`、`crawl_tasks` 与搜索结果投影；Cloud 运行时只读取 `config/` 下的 TOML 凭据（抖音为 `config/credentials/douyin.toml`），架构边界测试禁止 `os.Getenv`，`WT_MEDIA_DOUYIN_*` 环境变量与 `.env.local` 对 Cloud 运行时无效（2026-09-23 更正）；Agent/BitBrowser/Desktop 不参与 M3 执行。

## 实施任务

- B：分享链接单条导入并在任务成功后幂等进入内容池。
- C：关键词搜索，任务详情展示结果，确认选中结果后入池。（博主搜索已暂停，不在本次范围。）
- D：统一 `discovery_strategy`，本期支持 keyword、启停和手动执行；`author` 取值保留但暂停。（2026-09-23 调整，原为 keyword/author 同时交付。）
- E：统一 `crawl_task` 状态、统计、错误和每分钟到期策略触发；Scheduler 只入队，Worker 统一领取后由 Cloud Crawler 执行并直接入池。2026-09-23 更正：`cmd/server` 只启动 HTTP 引擎，Discovery Scheduler 与 Discovery Worker 是独立 CMD（`cmd/discovery-scheduler`、`cmd/discovery-worker`），无 flag，循环间隔取自 `config/scheduler/scheduler.toml`；不存在「启动服务即同时拉起三者」的行为。

## 验收口径

自动化单元/集成测试必须通过：团队权限、重复去重、搜索结果选择入池、任务状态、Crawler 映射和调度。真实 Douyin 端到端需由 `config/credentials/douyin.toml` 提供凭据后执行（2026-09-23 更正：Cloud 运行时只读 `config/` 下的 TOML，不读环境变量，`WT_MEDIA_DOUYIN_API_BASE`、`WT_MEDIA_DOUYIN_API_KEY` 与 `.env.local` 对其无效），不以 mock 或 HTTP 200 替代真实业务读回。

## 提交边界

Cloud、Agent、Workspace 分仓提交；Desktop 不因本次 M3 纠偏修改，只复用 Cloud Web 构建，不复制业务逻辑。完成前必须更新 checkpoint 与 evidence。

## Checkpoint

- Completed：用户已确认 Scheduler/Worker 职责边界；ADR-0015 已更新为“Scheduler 只入队、Worker 统一执行”，手动立即执行同样入队。2026-09-23：用户确认自动转素材为 M3 正式能力，已回写产品基线 §4 与 ADR-0013 第 3 条；`partial_success` 按实施事实回写产品基线 §5 与 ADR-0013 第 7 条；M3 产品基线落回 `docs/product/M3-content-mining-v2.md`。
- Current：M3 阶段状态已同步至 `delivery/milestones/M3-content-discovery-v2.md` 第 2.1 节——A～E1 有真实证据，C2/E2 已暂停，E3 未开始。CHG 继续保留，用于 M3 其余真实外部验收与完整闭环。
- Next：进入 E3（CHG-20260915-051）综合验收与用户签收；C2/E2 已暂停，不再作为 E3 前置。关键词链路的真实外部读回需先具备 Cloud 凭据环境。
- Blockers：关键词链路的真实外部读回依赖 `config/credentials/douyin.toml` 形式的凭据（2026-09-23 更正：Cloud 运行时只读 `config/` 下的 TOML，`WT_MEDIA_DOUYIN_*` 环境变量与 `.env.local` 对其无效），凭据不在仓库内。不以 mock 或 HTTP 200 替代真实业务读回。
- Recent verification：`scripts/test.sh` 的 Go 全包与 Web 20/76 Vitest 通过；迁移 `20260916_031` 已应用；独立 Scheduler/Worker 入口（后收敛为 `cmd/discovery-scheduler`、`cmd/discovery-worker`）在空队列返回成功；本机 `/api/v1/health` 通过。详见 `evidence/20260916-scheduler-worker-boundary.md`。
- Open follow-ups（非阻塞）：本轮全量验收产生的 4 项后续待决，归属待用户裁定，均不阻塞本 CHG。
  - D9：上游空返回是否应区分为「查无结果」与「上游异常」（现为如实透传为「成功且 0 条发现」）。
  - D6 / D2：来源方式标签失真与 `schedule` 无服务端校验的修复归属（本 CHG 修复，还是另立 CHG）。
  - D-scheduler：修复独立调度进程 panic 后，无人值守的真实周期触发是否在本 CHG 内复验，并据此重开 M3-E1 的通过判定。
  - `material_failed`：NOT VERIFIED 的状态可达性是否以受控故障注入补验，由本 CHG 还是后续 CHG 承担。

## 6. Pending Questions

None.

本轮全量验收产生 4 项后续待决，均**不阻塞本 CHG 的剩余范围**，故不列为本 CHG 的待决问题，
登记在下方 Checkpoint 的「Open follow-ups（非阻塞）」与 `evidence/m3-e3-acceptance-20260923/`
（`12-defects-and-security.md`、`14-verdict.md`），归属待用户裁定。
