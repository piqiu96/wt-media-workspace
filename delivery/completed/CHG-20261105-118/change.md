---
id: CHG-20261105-118
parent: delivery/milestones/M4-content-production.md#m4-n-production-acceptance
status: DONE
depends_on: ["CHG-20261105-117"]
affected_repos: ["wt-media-cloud", "wt-media-agent", "wt-media-desktop", "wt-media-workspace"]
risk: H
merge_commits: {"wt-media-cloud": "7bf8e2a4a47012ad5b443b9ec3d88b2c35c542d7", "wt-media-agent": "b8c2b259ec06e68eaac304bad753acf131fce598", "wt-media-desktop": "e3ee88afcda134d097a9f9770a3282c3d2db4046"}
---

# CHG-20261105-118：内容生产全链调试与视觉验收准备

## Change

从最新源代码启动 Cloud、Worker、Scheduler、Web、Agent 与 Desktop，完成三角色、真实输入／输出、失败恢复及全页面视觉检查，修复验收范围内问题，保留供次日人工走查的入口。

用户于 2026-11-05 授权自行拆分并连续推进内容生产全量落地、调试与视觉走查；无需每个 CHG 结束再请求启动下一项。各依赖仍须验证、独立提交与合并后再启动，不能用离线原型证据代替运行结果。

## Done When

- 使用固定开发数据库和最新构建通过环境新鲜度验证；未通过项如实阻塞而不冒充完成。
- 真实视频经多组／多份、策略立即／定时与人工任务形成成片，按存储／数据库／API／页面对账。
- 重放、并发、额度、越权、取消／失败／核实恢复及下载文件完整性通过实际检查。
- 策略读取改为真实服务端分页及总数，策略页面／任务筛选／新建选择器均同步，超过 200 条仍能找到受权旧策略；同一接口查询参数、DTO 与合同同步。
- 已迁移的 087 为旧任务补造了 legacy 批次；通过新的保留数据迁移只撤销可精确识别的人造批次，原任务／尝试／成片不变，历史无真实批次保持空关联。
- 未核实的 `execution_uncertain` 继续占用并发名额，人工核实旧执行已停止后才释放；不新增表或 Redis 空实现。
- 本机下载沿用 Local Agent 仅运营／高级运营的权限；管理员不能新建永远无法执行的本机队列，仍可取消本人已有传输，不允许操作他人任务；普通／高级运营团队变更后的门禁不放宽。
- 素材库、我的素材、策略、任务批次／列表、成片批次／列表在典型及窄屏走查，公共规范一致。
- 显式下载请求在上次下载已结束后创建新一代传输，只合并仍在排队／进行中的请求；本机文件缺失时重新下载不返回旧成功记录，保留旧历史与完整性校验。
- Local Agent 按已发布合同优先读取 `category_name`，仅旧 Cloud 未提供字段时接受 `game_name`；真实下载文件保留类目与 UTF-8 长度限制。
- Workspace 统一环境入口启用 Agent 正式下载循环，并管理合成 Scheduler 的启动、停止与新鲜度；不以仅有健康接口的进程充当完整执行器。
- 自审、差异、构建与相关回归完成，记录准确入口及未验证边界；用户次日人工签收保持待验收。

## References

- 产品：`docs/product/prd/详细文档/第五章_素材生产.md`
- 工程：`docs/engineering/specs/2026-09-24-m4-m5-cloud-content-production.md`
- 决策：`docs/decisions/0031-content-production-batches-and-manual-reproduction.md`
- 原型：`example/proto/content-operations/index.html`
- 公共规范：`docs/standards/frontend/README.md`

## Constraints

不实现发布领域的执行器／多日编排、不引入 Redis／MQ／工作流、不改变 Agent 与 Desktop 本机授权。正式业务规则已确认，缺失后端能力按本 CHG 实现；真正未确认的业务分叉保留明确阻塞，不通过虚构数据绕过。

## 验证

见 [最终核对](evidence/verification.md)与[界面走查](evidence/ui/ui-verification.md)。运行仓已合并并进入各自本地main，最终回归、真实全链、共享界面走查及环境新鲜度均通过；最新DMG已构建并完成启动探测。原生UI连接不可达，页面与登录交接保留人工待验收，不冒充用户签收。
