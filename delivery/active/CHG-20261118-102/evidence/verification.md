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

本轮最终差异完成独立审查及修正回归；Agent #9/#10/#11、Desktop #11/#12 和 Workspace #53/#54/#55 均沿用原 PR，描述按当前范围重写。代码按 102 → 103 → 104 传递，未自动合并。远端检查须以各 PR 最新提交为准，历史 CI 不作为新提交通过的依据。


本轮首次 Linux/Python 3.12 CI（run 44436600277）失败于测试夹具写死 `/private/tmp`，在连接数据库前触发 PermissionError；其余运行断言未失败。修正提交 `e92b691` 仅将该路径改为系统 TemporaryDirectory，保留“连接非争锁错误只尝试一次”的原断言。3 项故障定向与 703 项完整回归再次通过（`/private/tmp/chg102-portable-full.log`），并顺序传递至 CHG103/104，各复验同一 3 项通过；运行时代码和包内依赖未变。最新远端结果以 PR 当前提交检查为准。


## 2026-11-19 存储清理与数据库差异集中

Agent `509304a`：数据库类型只在 `storage/database.py` 内声明，默认 SQLite，不新增 URL/类型配置或环境变量。SQLite 连接、PRAGMA、冲突写入、条件唯一索引及历史升级移入 `storage/dialect.py`；Store 使用共享 Session 和模型规则。正常事务、现有唯一性、数据路径和业务状态保持不变。

删除 `records.py/OfflineResult`、未使用的检查点查询及路径属性；`TaskCheckpoint` 移至 `checkpoint_store.py`。待投递数量直接统计，发布发送协调移至既有 Runner，Journal 只读取原结果和记录确认。历史 DDL 原值保留，生产模型的时间默认值改用通用 UTC 函数。

新增接口定向测试先失败后通过：默认目录初始化、未知适配拒绝且不建目录、跨环境/用户待投递统计及确认。完整 Agent 回归 **706 项通过**（`/private/tmp/storage-cleanup-102-full.log`）。迁移测试改为在实际适配上注入历史/新增版本，保留旧数据和增量升级断言。后续分支、冻结包和最终独立审查仍待本轮验证，不引用此前结果作为完成依据。
