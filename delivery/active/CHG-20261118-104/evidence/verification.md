# 原尝试核实与安全重试验证

2026-11-18。Cloud `af665b255941a32e36d45b0c20edfe4f01776f13`（共用前端未在后续迁移修复中改变，构建标识仍为 `a4ab664`）、Agent `04190410f7248c81f84a71e4a7a23910b9e0e449`、Desktop `577146e797ec7ae3950ed2cf6f14967f0f3bb5bf`。本单元不装配自动发布循环，没有百度上传、最终点击、真实稿件回执或公开作品验收；M6 保持 `IN_PROGRESS`。

| 检查与复现入口 | 实际结果 |
| --- | --- |
| Cloud `bash scripts/test.sh` | PASS：Go 全套、136 个前端文件共 1007 项、控制入口 12 项 |
| Cloud `WT_MEDIA_CLOUD_HOME="$PWD" WT_MEDIA_TEST_LIVE_DB=1 go test ./internal/modules/publishing/repository -run TestLive -count=1 -v` | PASS：19 项隔离 MySQL 用例；107 条迁移首次应用，重复 0。核实错误 UID/未结束现场拒绝、未知禁止重试、并发重试只入队一次、原结果保留、历史尝试隔离、资源变化/停止拒绝和审计回滚均通过；测试库自动移除 |
| Agent `bash scripts/test.sh` | PASS：719 项。实际 SQLite、TCP 监听及已拦截的 HTTP 请求测试，不依赖外部网络；保留既有网络隔离和架构断言 |
| Desktop `bash scripts/test.sh` | PASS：538 项、6 项按既有规则忽略；控制入口 12 项、版本测试 20 项。只修改契约锁，没有改原生业务代码 |
| Workspace `python3 -m unittest discover -s tests` | PASS：211 项；本轮 7 个修改 Markdown 文件的 60 个本地链接均有效，交付、文档治理、产品路线及契约配置检查通过 |
| 官方聚合 `RUST_TEST_THREADS=1 WT_MEDIA_CLOUD_CONFIG_PATH=<私有配置目录> python3 scripts/wt.py chg verify CHG-20261118-104` | PASS，退出 0：各仓标准、本地 Cloud/Agent/Worker/调度服务、开发入口、登录、DMG 新鲜度与配置核对通过；不替代真实平台投稿验收 |
| 构建与包检查 | PASS：Cloud、Desktop 共用前端；重新构建 macOS DMG，以上提交及 2026.11.18.3 提供方版本、摘要、签名与 config_online 镜像核对通过。保留已有大包提示；没有将开发浏览器结果替代原生视觉验收 |

## 实际任务与页面

真实任务 3 / attempt 2 首轮在浏览器入场前因 `preparing` 序号与旧准备前提不匹配而失败。没有下载入场后的平台上传或最终点击，原结果如实保存为 uncertain。本地原结果/hash 已确认补报，未改写或删除检查点来绕开占位。新增“真实 Preparation + 真实 SQLite”测试先复现该衔接错误，再验证修复。

在 Cloud 正式任务页实际打开核实弹窗：取消后完整任务不变，缺少依据不能保存；选择“仍无法判断”，如实记录百家号安全验证阻塞，保存后仍 uncertain、尝试数仍 1，旧版本提交返回 409，原结果及 hash 完整保留。[输入校验](cloud-verification-validation.png)、[原结果与核实记录](cloud-original-result.png)。Desktop 开发入口同一页面的取消和输入校验通过，无页面脚本错误或横向溢出：[Desktop](desktop-verification.png)。原失败测试任务 1 仅打开重试确认并取消，任务与执行历史完全不变，没有发出重试写入。

页面沿用 Cloud `web/example/proto/publishing-design/TaskActionDialog.vue` 的结论/原因/依据结构、`TaskDetail.vue` 和 `PublishingTaskPage.vue`，使用既有 ResourceOverlay、FeedbackAlert 与公共样式。仅实现本单元的两种核实结论，不复制原型源码或新增视觉体系。可复现入口 Cloud `web/scripts/test-publication-recovery-browser.mjs`：通过 `WT_MEDIA_BROWSER_BASE_URL`、`WT_MEDIA_BROWSER_STATE`、`WT_MEDIA_BROWSER_EVIDENCE`、`WT_MEDIA_BROWSER_TASK_ID` 提供当前地址和授权任务；默认只取消与校验，显式 `WT_MEDIA_BROWSER_RESOLVE` 与实际 `WT_MEDIA_BROWSER_BASIS` 才写结论。不得以此脚本虚构“确认未发布”的依据。

[脱敏读回](original-attempt-readback.json) 仅保留任务、尝试、原 hash 与实际页面状态，不含 Token、Cookie、Profile 身份或临时下载地址。

## 故障与恢复检查

- 准备序号衔接：真实失败后修复；没有重新进入旧 attempt。新鲜尝试协调器在准备前报告后可继续准备，重启/重放仍拒绝入场。
- 许可响应丢失零次最终点击；点击响应丢失只点一次，结果未知，不自动重放；Cloud 停止时不进入上传。
- 真实 TCP 测试证明“关闭响应成功且端口镜像空”仍可能有存活浏览器。仅镜像和原调试端口共同确认关闭才结束现场；无法确认仍 uncertain，可信回执也不能掩盖未结束现场。
- 零值稿件 ID 曾被协调器误认成 reviewing；失败测试复现后加上正数及规范格式校验，回归通过。
- 断网只补报同一份结果；当前任务已推进仍按原 attempt/hash 查询处置；补报确认后、结算前崩溃可恢复，不使用新任务状态释放旧现场。
- 最大允许核实依据与原因的完整 JSON 超出旧 VARCHAR(2000)，隔离 MySQL 先复现 Data too long；新增迁移 105 仅扩为 TEXT，不截断、不降低输入标准，200 字原因和 2000 字多字节依据完整读回。
- 只读 GET 初次测试发现携带 `null` 请求体；改为无请求体，准确 ID/bearer 和网络隔离检查通过。

## 未完成与后续顺序

已改用系统内约 13.7 MB 的真实成片和 85.8 KB 封面，文件已通过正式存储与前置资源校验，未修改 nginx 或业务文件上限。首次被百家号安全验证阻塞，任务 3 保持待核实。用户随后完成验证；在原页面逐页核对全部 103 篇稿件无对应标题、草稿 0 篇，实读原 UID 匹配；原执行进程已结束，BitBrowser 镜像和原调试端口共同证实关闭。通过正式页面确认未发布，revision 7→8，原 hash 不变；Agent 按原 attempt/hash 读回处置后，本地检查点为 settled，保留重放屏障。再通过正式页面先取消、后明确确认重试：同一任务 3 入队，revision 9，current_attempt_id 为空，attempt_count 仍 1，内容、资源及原历史完整保留；未领取新尝试、未上传或投稿。实际账号列表与平台截图仅保留本机，未复制账号主页和无关运营数据进仓库。

后续 M6-B 继续实际观察百度上传表单、实现适配和独立执行循环、通过持久化许可后自动最终提交并读取真实回执；M6-C 再完成公开作品核实、补录、人工继续、安全终止/放弃及关联作品。尚未验证的范围不计入本单元通过。

## 聚合检查与 Review 顺序

首次聚合中的既有磁盘空闲量测试，两次实时读数相差 4096 字节；单独保留原断言复测通过。使用 `RUST_TEST_THREADS=1` 减少测试间并发写盘后全部 Rust 检查通过，未修改或降低断言。另一次聚合拒绝早于最终源码提交的合成调度构建；服务实际存活，按既有环境入口重建、应用迁移 105 并重启全部本地服务后，最终正式聚合退出 0。

前置 CHG-101/102/103 PR 链先合并；本单元 [Cloud#46](https://github.com/piqiu96/wt-media-cloud/pull/46) → [Agent#11](https://github.com/piqiu96/wt-media-agent/pull/11) → [Desktop#12](https://github.com/piqiu96/wt-media-desktop/pull/12) → 本 Workspace PR。Cloud 含迁移 105；各 PR 以对应 CHG-103 实际远端分支 `chg/CHG-20261118-103` 为 base，当前 head 为 `codex/CHG-20261118-104`。保持独立差异，未合并。

当前堆叠目标不匹配既有 main-only workflow，尚无本单元远端 CI；以上为实际本地标准及正式聚合结果，不把无检查称为 CI 通过。原生视觉走查与真实平台投稿仍未验证，不标记 CHG 或 Milestone DONE。

补验入口：Cloud 真实页面脚本仅显式 `WT_MEDIA_BROWSER_RETRY=1` 才确认重试，不能与 resolve 同轮执行。确认失败、旧版本 409、取消重试、实际重试与原结果读回全部通过，页面错误 0、无横向溢出；脚本语法与差异检查通过，未改运行时代码。补验未重新运行此前已通过的完整测试。

补验脚本提交 Cloud `55fa6fc8753d26b7554793b7275da5ffaa78d48e`；[实际重试页面](same-task-retry.png)、[脱敏结果](same-task-retry-readback.json)。Workspace 文档治理、Delivery 和产品路线对齐检查均通过。


## 2026-11-19 ORM 下游兼容与补报回归

本轮基于 Agent CHG103 `e08e3bf`，兼容修改 `a0f6b7c` 与争锁修正合入 `35c14a7`；保留此前 CHG105 的平台 Publisher 分层、浏览器公共动作和一期 browser 协议。原 CHG104/105 的历史验证不能代替本轮证据。

| 检查 | 本轮实际结果 |
| --- | --- |
| Agent 标准回归 | PASS：775 项（`/private/tmp/chg104-final-full.log`），完整保留实际准备、执行屏障、平台适配、重启、许可丢失及结果不可变断言 |
| 人工结算与未投递结果 | 新增真实 SQLite 回归先失败再通过：结果保存后断网、Cloud 人工结算现场、重开日志、网络恢复。原 packet 仍被发现；模拟 Cloud 既有冲突回应时继续未投递，最终浏览器点击仍一次 |
| 默认事务争锁 | CHG102 的 BUSY_SNAPSHOT 回归传递通过；仅重试本地短事务，reserve_report/settle_resolved 同样适配，HTTP 与浏览器均不重放 |
| Desktop 标准回归 | PASS：Rust 540 项、6 项依既有规则忽略；控制入口 12 项、版本记录 20 项（`/private/tmp/chg104-desktop-test.log`）；Cloud 地址与 cloud_env 成对注入 |
| 实际冻结 Agent | PASS：PyInstaller 构建 macOS arm64 Sidecar，含 SQLAlchemy；严格按工具生成锁文件安装成功。实际二进制分别用临时空库和历史四版本发布库启动，认证 healthz 可用；五个版本及单数新表落地，旧表退出，原结果摘要保留（`/private/tmp/chg104-frozen-orm-smoke.log`） |

恢复扫描合并“未结算现场”和“未投递结果”；结算不会伪造投递回执。核对当前 Cloud 规则：人工结算且云端没有原结果摘要时，迟到报告可能被拒绝，因此不能声称恢复网络后一定投递成功。拒绝记录及原结果保留供核查，不更改 Cloud 状态机。

独立审查唯一阻塞项为 SQLite 快照写入争锁，已在前置 CHG102 修正并通过三层完整回归。所有验证使用临时数据，任务轮询关闭；本轮未执行真实平台投稿、未重建完整 DMG、未做原生界面验收，不沿用历史截图声称通过。文档与代码同步在原 PR 链中，未自动合并。

最终 Agent 提交 `545c890` 补齐工具生成的 Publisher 锁定依赖；`uv sync --all-extras --locked --offline` 通过后，用该分支独立环境复验完整 775 项通过（`/private/tmp/chg104-own-env-full.log`）。当前 Workspace 回归 207 项、18 项按既有条件跳过（`/private/tmp/chg104-workspace-full.log`）；文档、Delivery、产品路线和差异检查通过。所有原 PR 描述已按当前范围重写，原堆叠 base 保持。

最终 Agent 分支 `e43ea50` 仅继续承接前置 Linux 测试目录兼容修正，3 项连接故障断言复验通过；运行时代码与 `545c890` 的包内依赖相同，775 项和实际冻结包验证的范围不变。历史 CI 及本轮首次失败均保留在对应前置 CHG 证据，最新状态以各 PR 当前提交检查为准。


## 2026-11-19 存储清理集成验证

Agent `711fd45` 顺序继承 CHG102 `509304a`、CHG103 `dd29f29`。恢复已核对同一 attempt/hash 后，直接调用 Journal 确认原 packet；删除全量 pending 扫描和伪发送回调。未知现场不重入、未确认原结果继续可见；未改变 Cloud 状态及本地执行阶段。

- 完整 Agent 标准回归 **778 项通过**（`/private/tmp/storage-cleanup-104-full.log`）。三项旧恢复测试仅将删除的冗余路径属性替换为共享 Database 路径，原重启、手工结算和迟到报告断言保留。
- 新建 macOS arm64 PyInstaller Sidecar 成功（`/private/tmp/storage-cleanup-build.log`）；实际新二进制分别用临时空库及历史四版本发布库启动，认证健康接口、五个升级版本、单数表、旧表退出及原报告摘要保留均通过（`/private/tmp/storage-cleanup-frozen-smoke.log`）。任务轮询关闭，未连接真实账号投稿。
- 独立只读最终审查未发现 Critical/Important，另行执行 81 项存储/发布相关测试通过。唯一 Minor 为前置 dialect 文件末尾空行，按原清单留待后续，运行行为不受影响。范围差异检查会报告该格式项，不宣称其通过。

本轮不修改 Cloud/Desktop，不重建完整 DMG、不执行真实投稿或原生页面验收；其他数据库尚未接入，未来须新增适配和迁移验证。原防重设计保留，本轮仅验证重构未破坏其行为。PR 保持未合并。

本轮 Workspace 文档、Delivery、产品路线、AI/Skills 和配置校验通过；完整回归 **207 项、18 项按既有条件跳过**（`/private/tmp/storage-cleanup-chg104-docs-docs.log`）。Agent #11 与 Workspace #55 已更新原描述，不创建新 PR、不合并；前置 Agent #9 最新 CI 通过，后续堆叠目标未触发的工作流不视为远端通过。


## 2026-11-19 environment 命名同步

顺序继承前置环境命名：Agent `a9a49c0` 完整 **780 项通过**（`/private/tmp/environment-names-104-full.log`）；Desktop `05a7c16` 完整 **543 项通过、6 项既有忽略**，控制入口 **12 项**、版本资源检查 **20 项**通过（`/private/tmp/environment-desktop-104-full.log`）。两字段独立，Desktop 传入明确 `WT_MEDIA_ENV` 与 `WT_MEDIA_CLOUD_ENV`；发布构建的 prod floor 与安装目录策略保留，不变更本单元的发布/恢复状态。

以新 Agent 代码和 prod 发布配置实际构建 macOS arm64 Sidecar（`/private/tmp/environment-names-build.log`），以临时空库和历史四版本发布库实际启动；认证健康接口、五版本升级、单数表、原结果摘要保留通过（`/private/tmp/environment-names-frozen-smoke.log`）。轮询关闭，未连接真实账号投稿。新旧环境配置替换方式见 Agent/Desktop README；未重建完整 DMG，不沿用此前原生页面验收。

命名变更后的 Workspace 标准回归 **207 项、18 项按既有条件跳过**，各治理校验通过（`/private/tmp/storage-cleanup-environment-chg104-docs-docs.log`）。本轮独立跨仓核对无阻塞项；新旧库冻结启动验证来自本轮实际二进制，其他未验证边界沿用本轮 CHG102/103 明示范围。所有原 PR 保持未合并。


## 2026-11-20 Cloud104 同类问题 review

Cloud104 `b0ea139`、`11ea457`、`0f8724c` 同步103修订并保留本单元 resolve/retry/原尝试只读能力。原有 heartbeat/progress 与复数 attempt 接口移除，切换 singular `/api/v1/cloud-agent/publication-task/{id}/attempt/{attempt_id}`，与 Agent 对齐；无需执行开关。recovery task/attempt 更新改用 revision CAS，移除其 FOR UPDATE 与基础 LockPublicationScene，状态和核实结论使用同一组常量。原 packet/hash、核实记录、审计和冻结输入保留，uncertain 不能直接 retry；并发核实/重试各只允许一次成功。提供方兼容元数据版本2026.11.20.2。

验证：完整 Go 通过（/private/tmp/cloud104-final-go.log）；全部发布模块隔离 MySQL 通过（/private/tmp/cloud104-final-live.log），覆盖原尝试读回、安全重试、双核实并发、原结果不覆盖、迁移与重放，并继承103的输入变化/乐观更新/Profile引用竞争回归。前端137文件、1008项通过，生产构建通过（/private/tmp/cloud104-web.log、/private/tmp/cloud104-web-build.log）。独立最终审查未发现104额外阻塞；跨仓Cookie与Profile引用竞争四项发现已在103/Agent修复并合入本分支。

Agent本轮修订独立分支 `codex/chg103-104-review`，提交 `7b32e57`，原 #10/#11/#12 已合并，未向已关闭PR声称追加交付。完整官方离线790项通过；Cookie真实stage参数、cookie-read互斥、首次READY停止原因回归先失败后通过，保留原报文补报和单次点击屏障。基于远端main保留“现场已结算仍补报未送达原结果”的既有修复。

本轮不操作真实浏览器、不真实投稿、不重建Desktop/DMG、不合并PR。迁移108若发现既有无效Profile引用会失败，需核实数据，不能静默重写历史。操作互斥保留单Agent进程假设，持久checkpoint负责重启后占位，不承诺多实例同时操作同一数据库。CHG/M6维持现有验证状态。


本轮已推送：[Cloud104 #46](https://github.com/piqiu96/wt-media-cloud/pull/46) / [Cloud103 #45](https://github.com/piqiu96/wt-media-cloud/pull/45)，[Agent草稿 #13](https://github.com/piqiu96/wt-media-agent/pull/13)。Workspace #54/#55同步正式设计和各自证据，文档、Delivery、产品路线校验通过。各PR保持未合并，保留工作树供逐个review。


## 2026-11-20 第二轮基础查询与恢复审查

Cloud104 顺序同步103 `42d9771`（基础九个 publication.go 删除、普通读取去锁、迁移109活动 Profile/用户槽唯一约束、通用 JSON 序列化且摘要不变），并提交 `e6f4847` 将 recovery 的输入复查改为普通事实读取，核实/重试事务采用 READ COMMITTED。恢复仍使用 task/attempt revision CAS，原报文/hash及核实审计保留；未决现场继续占用 Profile 和用户名额，只有完成或核实结束才释放；retry 后新领取在约束下取得新 attempt。

本轮完整Go通过（`/private/tmp/chg104-go-final.log`），全部发布模块隔离MySQL通过（`/private/tmp/chg104-live-final.log`），涵盖核实与重试并发、原尝试读回及不覆盖、新尝试原子准入、输入变化停止、迁移回填/重放/错误历史拒绝和基础查询不阻塞修改。独立最终review审查103完整差异及104恢复改动，无可行动问题，独立publish/model测试通过。Workspace已同步103正式设计；迁移部署前停写、预检和DDL部分失败/回退要求见103本轮evidence。

前端、Agent协议与报文摘要未变，本轮不重复构建；不真实投稿、不重建Desktop/DMG、不合并PR，CHG/M6继续验证中。Cloud45/46、Workspace54/55使用原PR更新。
