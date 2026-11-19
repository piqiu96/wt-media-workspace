# M6-B 本地执行安全验证

日期：2026-11-18。Agent 实施提交 `6046a789fe53530f75673c4706ebdfea6decc1ed`，地址别名修复 `eb49901`、CI 争锁修复 `f663af1`。此单元只是首次自动投稿的前置安全能力，不代表平台投稿或 M6 完成。

| 检查 | 实际结果 |
| --- | --- |
| 定向故障测试 | PASS：16 项执行边界及 3 项连接初始化测试；先出现缺失实现的失败，再实现并通过。地址别名回归先失败，再统一大小写与默认端口；最终定向复验通过 |
| SQLite 并发与隔离 | PASS：8 个线程争抢同一 attempt 只有一个首次登记；同号下载、不同环境/用户不覆盖；输入与结果不可改写；实际 Profile 的未知现场跨用户/环境互斥 |
| 突然退出与恢复 | PASS：3 个实际子进程分别在 submitting、click_started、result_saved 后直接退出；重开 SQLite 可读到此前阶段，重复调度没有再次准备或点击。结果保存后退出仍保留原 outbox |
| 事务回滚与补报 | PASS：SQLite 触发器注入 outbox 写失败，checkpoint 更新一并回滚；断网、错误确认及跨用户/环境发送均不结算；确认只标记原结果投递，不自动释放未知现场；明确安全结算后仍保留防重记录 |
| Agent 标准回归 | PASS：`bash scripts/test.sh`，695 项；既有架构边界、下载、迁移、身份与本地接口验证保留，未降低断言、未向 checkout .local 写测试数据 |
| 装配 | PASS：14 项；安全组件与既有 checkpoint 使用同一数据库，构造本身不启动发布循环 |
| Workspace | PASS：211 项；交付索引、Milestone/MASTER 归属、配置与差异检查通过 |
| 实际环境预检 | 账号 9、Profile 37 的本机百度 UID 实读匹配，登录正常；浏览器实际打开百家号后台并点击「发布视频」，空上传表单可见。未上传或点击发布，不作为本单元端到端投稿证据 |
| 页面与正式平台验收 | 本单元不改变页面。M6-A 两端实际表单证据见前置 CHG；首次真实自动投稿尚未接入，不声称通过 |

复现：Agent `PYTHONPATH=src .venv/bin/python -m unittest discover -s tests -p test_publication_execution.py`；`bash scripts/test.sh`。均使用临时 SQLite，不连接 Cloud MySQL、不以测试回调充当真实平台成功。

Agent PR：[wt-media-agent#9](https://github.com/piqiu96/wt-media-agent/pull/9)。依赖 M6-A [Cloud#44](https://github.com/piqiu96/wt-media-cloud/pull/44) 与 [Workspace#52](https://github.com/piqiu96/wt-media-workspace/pull/52)；本 Workspace PR 以 #52 的分支为基线，只显示本单元差异。用户本次已允许堆叠，未修改长期规则；标准 start 因前置未合并拒绝，本次仅按明确授权继续，未绕过或削弱校验脚本。

CI 在 Linux/Python 3.12 首次 WAL 初始化并发测试失败，保留原并发断言；新增实际 SQLite 读锁测试确定性复现，只修复连接初始化的争锁重试与错误关闭；3 项定向测试及 695 项完整回归通过。不是重跑 CI 碰运气，也没有给平台操作增加自动重试。最终 GitHub CI PASS（run 44188903102）；`wt chg verify CHG-20261118-102` PASS，包含 Workspace 211 项与 Agent 695 项及配置/运行环境检查。当前安装包重建、签名与组件版本校验通过，包内 Agent 来自 `f663af1`；不据此宣称原生页面走查或平台投稿通过。实际平台领取、适配和最终提交继续留在后续 M6-B 范围。


## 2026-11-19 异常退出后的人工处置衔接

本轮用户确认以最小人工处理流程补齐缺口，不实现自动平台核实、断点续跑或自动重新投稿。修复位于已包含 CHG-104/105 的当前 Agent 分支，提交 `38961c5160f67a94b219955f52fafdb7ae76134d`；PR #9 自身仍是上述基础安全单元，不能把本轮后续协调器修复算作其原始独立交付。

修改前已通过本机既有网络代理同步远端 main（不修改永久代理配置）：Agent main 为 `b8c2b259ec06e68eaac304bad753acf131fce598`，已包含于工作分支；Workspace main 为 `afc76c498e3caa1715b4935febc27b7c0e776f31`，合入提交 `8de5104`。契约版本冲突采用主线 Cloud API `2026.11.19.1`，保留后续 Cloud-Agent `2026.11.18.3`；原有未提交走查文档已备份、恢复，未纳入本轮提交。

### 缺口与修复

- 原恢复查询只遍历已保存结果的记录；实际硬退出发生在结果落盘前时，Cloud 心跳超时及人工核实虽能完成，本地 Profile 占位仍无法解除。恢复查询现包含无结果的旧尝试，仅只读查询原尝试处置，不重新打开浏览器或生成完成结果。
- 原恢复将现场处置与结果 hash 确认绑定；人工核实先于结果送达时，Cloud 合法返回 `result_hash=null,scene_resolved=true,resolved_status=failed`，本地仍会卡住。现将明确现场处置与投递回执分开，只按原用户、环境、task/attempt 查询确认对应占位。
- 人工明确处置后使用既有本地 `settled/publication_settled` 结束现场。缺失最终结果继续为空；未送达的原 packet、outbox 行及 `report_pending=1/delivered=0` 保留，不伪装已经投递。已结束现场不再进入自动恢复轮询；没有收到的原结果仍是未投递历史记录。
- 同一 attempt 的输入、结果及重放屏障保留；安全重试仍经 Cloud 原任务重试入口授权新的 attempt，从头执行。错误 attempt、跨用户/环境、未明确处置、结果摘要冲突，以及本地可信审核回执与无回执的人工失败冲突，均不释放现场。
- 业务任务状态、Cloud API、数据库结构、页面和 Desktop 原生代码均不改变。既有 `uncertain → failed → queued/pending` 处理条件保持；不释放成片等正式业务资源，不宣称已实现公开结果核实或完整 M6-C。

### 本轮实际验证

| 检查 | 结果 |
| --- | --- |
| 回归复现 | 新增 7 项测试；修复前相关套件出现 3 个断言失败及 2 个缺失方法错误，准确复现两个恢复缺口；其余新增检查约束隔离与冲突边界 |
| 相关执行与存储测试 | PASS：38 项；实际临时 SQLite 覆盖无结果重启、人工处置早于补报、原记录不变、未投递标记真实、旧尝试不可重放及新尝试可登记 |
| Agent 标准回归 | PASS：`PYTHONDONTWRITEBYTECODE=1 bash scripts/test.sh`，750 项；需要本机临时端口的测试在授权执行环境通过，未新增 checkout `.local` 路径；未连接真实账号或投稿 |
| 独立审查 | 无待修问题；独立复验 20 项 PublicationJob 测试通过 |
| 文档与交付治理 | PASS：`scripts/docs/check.py`、`scripts/verify/verify_delivery_governance.py`；本轮差异检查通过 |
| Workspace 整体测试 | 本轮执行 211 项，出现 26 项失败报告：已有未提交 Milestone 文档在测试临时副本中引用未复制的 `app-walkthrough-fixes.md`，以及 Cloud 提供方最新 `2026.11.19.2` 与合入主线映射 `2026.11.19.1` 不一致。非本轮 Agent/CHG-102 修改引入，未删除走查记录或降低断言 |
| 配置与运行环境检查 | `verify_m0_config.py` 被上述提供方版本不一致阻断；`bin/control.sh verify` 的 Cloud、Agent、Cloud worker、Compose worker 检查通过，Compose scheduler 因现有二进制早于最新源码而失败。本轮未重启、重建运行环境，不将其记为通过 |

复现相关测试：`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:tests .venv/bin/python -m unittest test_publication_job test_publication_execution`。本轮只验证 Agent 控制边界，未进行安装包重建、真实发布或公开作品验收。CHG 保持 VERIFYING，待既有跨仓基线问题处理及相应 Review/合并后再收口，不将本次修复测试替代整体交付验收。


### 公共常量整改与 Review 范围

Agent 提交 `3f9033a550f51d745fe188e396f54b032a749061` 将本轮发布执行与恢复涉及的重复常量集中到既有 `src/wt_media_agent/runtime/constants.py`，包括 Cloud 发布任务状态、Cloud 执行阶段、本机执行阶段、检查点状态、上报操作、错误码与默认心跳/轮询间隔。Cloud 阶段与本机阶段分别命名，防止混用；Cloud 仍裁决业务状态，Agent 只消费已有值。SQLite 使用参数传入公共常量，持久化值及 JSON/HTTP 字符串保持不变，没有数据库迁移。

最终复验 `PYTHONDONTWRITEBYTECODE=1 bash scripts/test.sh`：750 项通过；列表、字典、空值及未知状态/上报类型的 8 项补充边界检查仍按原行为拒绝。独立审查未发现待修问题；差异检查通过。本轮没有真实平台操作，原有 Workspace 整体验证限制仍适用。

Review 按原有堆叠关系进行：[Agent CHG-104 PR #11](https://github.com/piqiu96/wt-media-agent/pull/11) 先审核核实与安全重试衔接，[Agent CHG-105 PR #12](https://github.com/piqiu96/wt-media-agent/pull/12) 再审核实际投稿与本轮后续修复；分别确认，不合并为一个新 CHG。首次记录时，后续修复与常量整改尚在既有 `codex/CHG-20261118-105` 本地分支，未推送。后续结构重整与本轮统一交付见 [CHG-105 最新验证](../../CHG-20261118-105/evidence/verification.md#2026-11-19-review-后的平台能力职责重整)；远端最终 Review 以现有 PR 的最新提交为准，包含本节修复与公共常量整改。CHG-104 的独立 PR 不包含本轮后续修复。保持 VERIFYING，不自动合并。

## 2026-11-19 ORM Review 整改

本轮保留此前验证的历史，不用其测试数量证明新版本。Agent `4de3d1c` 将全部 SQLite 业务读写统一为 SQLAlchemy，旧连接模块移除，任务表改为 `task_checkpoint/task_result`。`cloud_env` 显式配置，原始任务 ID 分列隔离，Profile 互斥由数据库唯一索引保证。

- 修改前标准回归：695 项通过。
- 最终完整回归：703 项通过（`/private/tmp/chg102-final-full.log`），对应 Agent `787ae55`；此前存储/发布定向复验 25 项通过。
- 真实 SQLite 验证：8 线程同 Profile 跨环境竞争仅一次登记、同类型/跨类型同号隔离、外键拒绝孤立结果、事务失败回滚、实际子进程强制退出保留提交屏障、原结果幂等且不可覆盖。
- 升级验证：未知旧下载身份阻止升级并保留原行及四个历史版本；明确映射后转换。历史发布原报文摘要与待补报状态保留。未确认旧领取键未完成映射时不旋转，核实映射后保留同一请求值。
- 连接验证：每个新连接启用 FULL/FK/WAL，真实首次 WAL 争锁测试保留，非争锁失败不重试且关闭连接。
- Python 发布包：`uv build` 通过，源码分发与 wheel 均构建成功。依赖锁由 `uv sync --all-extras` 生成，未手工编辑。

以上使用临时 SQLite，不进行真实平台投稿。最终安装包内依赖及后续消费者由 CHG104 集成验证；本记录不替代该证据。PR 尚未合并。


最终独立审查发现默认事务下的快照写入竞争：读取检查点后其他连接提交，保存结果可能遇到 SQLITE_BUSY_SNAPSHOT。真实 SQLite 回归先复现，再在纯数据库方法外增加有界事务重试；沿用原结果和序号，HTTP 与浏览器均不重放。修正后 703 项完整测试通过。未引入 BEGIN IMMEDIATE。

当前隔离 Workspace 完整回归：207 项，18 项因未提供运行仓同级目录或专项条件而按现有规则跳过（`/private/tmp/chg102-workspace-full.log`）；不把此前 211 项结果当作本轮执行结果。Delivery、产品路线及文档治理另行复验。最终 Agent Sidecar 在 CHG104 打包，并实际启动验证空库和历史四版本发布库升级，原报告摘要保留；详见 CHG104 的本轮证据。本轮未重建完整 DMG、未进行真实平台投稿，也未将历史验收结果冒充新版本验收。
