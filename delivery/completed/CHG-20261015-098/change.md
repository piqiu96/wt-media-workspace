# CHG-20261015-098：M5-C7 真实计划时间全链与 M4/M5 统一验收

- Status: DONE
- Level: M
- Milestone: `delivery/milestones/M5-automatic-production.md`
- Closure anchor: §4 M5-A 策略调度纠偏、§6 M5-C 自动生产综合验收、§7 M5-AC-01/10～13、§8 DONE Gate
- Product: `docs/product/prd/详细文档/第五章_素材生产.md` §5.7～5.10
- Engineering: `docs/engineering/specs/2026-09-24-m4-m5-cloud-content-production.md` §5～7
- Decision: `docs/decisions/0017-m4-m5-cloud-owned-content-production.md`
- Current repository: `wt-media-workspace`
- Affected repositories: `wt-media-cloud`, `wt-media-agent`, `wt-media-desktop`（验收目标，运行时代码修改以复现缺陷为前提）
- Verification repositories: `wt-media-cloud`, `wt-media-agent`, `wt-media-desktop`
- Runtime implementation: Cloud owns the M4/M5 compose-task acceptance corrections confirmed on 2026-10-16; Agent and Desktop remain verification targets
- Round 3 (T-19～T-26, 2026-10-27): 用户确认八项页面修订并裁定平台标识与角色能力口径，运行时修改扩展到 Agent（平台标识重命名）与 Desktop（系统管理导航、sidecar 角色、共用前端）

## 目标

高级运营在真实计划时间启用策略后，独立 Cloud Scheduler 创建批量任务，独立 Worker 按容量限制用真实 FFmpeg 和对象存储生成可播放成片；运营在 Cloud Web 与打包 Desktop 中看到相同状态，使用既有 Local Agent 下载成片。复跑 M4 人工生产与下载、故障恢复和旧路径扫描，完成 M4-H2 与 M5 的统一用户走查。

## 当前事实与差距

- M5-C1～C6（含 C2a）已机器验证并归档；C7 是当前唯一 Active CHG。
- M5-AC-01～12 在旧计划模型下曾 PASS；T-10 策略模型纠偏后 01/01a/02/03/04/09/10/11 退回 TODO，2026-10-17 已按新模型重新验回 PASS；M5-AC-13 与 M4-H2 的页面走查及签收仍未完成。
- C7 需固定运行环境、明确真实对象和跨进程读回；不能只以 HTTP 200、任务行或模拟依赖判定通过。

## 有序任务

| Task | 可独立验证结果 | 验证 |
| --- | --- | --- |
| T-01 | 从当前源码确定性启动 Cloud、Agent、BitBrowser、Web 与打包 Desktop；健康、版本、登录、CORS 和配置均可读回 | `environment-bring-up` 全部 gate 与证据 |
| T-02 | 真实时间触发一批自动任务；核对计划时区、素材范围、上限、幂等、停用、混合结果和 Worker 容量/恢复 | 独立进程、MySQL、对象存储、FFprobe、API 对账 |
| T-03 | 自动成片在 Cloud Web 和打包 Desktop 可预览并经 Local Agent 下载；复跑 M4 人工生产/下载 | 页面与文件读回、Cloud/Agent 状态对账、M4-H2 走查记录 |
| T-04 | 代码/Migration/Contract 排除旧对象和 Agent 合成路径，按 M5 验收矩阵逐项收口并完成用户签收 | 扫描结果、差异复审、用户走查结论 |
| T-05 | 收口合成任务列表与详情走查结论：创建时稳定名称、实体追溯、状态/阶段、执行记录与配置快照 | Cloud schema/API/Web 测试及 Cloud Web/Desktop 共用页面走查 |
| T-06 | 收口合成任务页面走查第二轮：创建入口迁到合成任务页、我的素材净删除、关联实体编号去 `#`、已下载行的本地文件分支 | Cloud 测试与双端构建、开发库读数、真实页面走查 |
| T-07 | 收口合成任务创建与详情走查第三轮：参数顺序/预填/提交前拦截、素材按游戏与名称筛选、详情生成结果收口与失败原因、执行过程步骤记录（Cloud 侧 JSON）、创建时任务名称与批量序号 | Cloud schema/API/Web 测试与双端构建、migration 064 开发库应用与读回、真实页面走查（含 Worker 真跑两条任务） |
| T-08 | 收口合成任务创建与列表走查第四轮：素材按 (策略,素材) 分「未使用过/已使用过」并用一个使用情况下拉筛选、同对在途创建由服务端权威拒绝、筛选栏按 合成策略-触发方式-状态-创建时间 排序、失败详情补「为什么没有重试」一句 | Cloud schema/API/Web 测试与双端构建、migration 065 开发库应用与读回、真实库并发创建实测、真实页面走查 |
| T-09 | 收口合成任务创建与重试走查第五轮：一条 (策略,素材) 只跑一次（抽屉只读 / 服务端有记录即拒 / 调度有记录即跳过）、候选默认发布时间倒序并可切点赞倒序、候选行与「我的素材」补点赞与收藏、已取消任务可重试且人工重试重定基自动容错配额、手工启动 compose-worker 跑通积压 | Cloud schema/API/Web 测试与双端构建、真实库重试三连（含重试→取消→再重试的 1062 路径）与创建守卫三态实测、真实页面走查、worker 真跑前后分布对账 |
| T-10 | 收口合成策略页走查：状态与执行方式、优先级条件、统一候选选择、单项失败隔离及同一策略表单；保留 M4 人工选材路径 | 新 schema/API 与规则测试、真实 Scheduler/人工触发读回、Web/双端构建、策略页走查；本机开发库旧策略及关联数据按用户授权定向清理 |
| T-11 | 收口 2026-10-21 走查的「素材已就绪但文件丢失」：合成消费前确认对象、每 claim 一次重新准备、素材受控回退、用户下载/预览预检、准备地址失败重试一次、成功挂接对账、Content-MD5 上传校验与清理边界 | Cloud/Web 测试与双端构建、真实环境重试 319/320/321 与对象/清理读回、Garage Content-MD5 双向对照；用户下载端到端与真实并发登记为未覆盖 |
| T-12 | 合成任务列表展示完成时间；详情「结束时间」改为「完成时间」 | Vitest 列序/列数与详情标签；真实页面读回 |
| T-13 | 合成策略运行记录、合成任务、成片管理的触发 / 生成方式统一为「策略自动 / 人工创建」，由前端公共常量提供 | 新 `compose/labels.test.js` 与受影响页面/组件测试；真实页面读回三处文案 |
| T-14 | 所有页面的游戏筛选与表单只列启用游戏；新建策略服务端拒绝停用游戏 | 新 `shared/utils/games.test.js`、受影响页面测试、Go 停用游戏回归；真实页面逐页确认 |
| T-15 | 普通运营可见素材使用情况，只显示计数、不显示姓名；详情抽屉同样按 `mode` 判断 | Vitest 列/筛选/弹窗/详情与 `usageOperatorCount`；真实页面按 operator01 读回 |
| T-16 | 素材库列表移除文件状态列与筛选；详情仍可查看文件状态 | Vitest 反向断言 + 详情抽屉正向对照；真实页面读回 |
| T-17 | 内容池「来源策略」「来源任务」合并为「来源」列，策略可点开只读关联弹窗，人工来源固定文案且不可点 | Vitest 列/组件/footer 渲染；真实页面用策略来源与人工来源各读回一次 |
| T-18 | 六项修订复走查与签收：三账号机器走查、用户复走查、M4-H2 / M5-AC-13 签收与归档 | 探针 0 异常、复走查清单、用户签收、`wt chg verify` 与文档 PR |
| T-19 | 平台展示统一：页面一律显示 抖音/B站/小红书/百度，代码统一为 `douyin/bilibili/xhs/baidu`，展示文案由前端公共常量持有 | `shared/utils/platforms.test.js`、受影响页面测试、Go mediaaccount 测试、migration 076 开发库应用与读回、Agent unittest、合同与 `verify_m0_config` |
| T-20 | 挖掘策略/挖掘任务搜索标签改「综合搜索」；内容池「发现时间」改「入库时间」；内容池行操作「素材详情」改「详情」 | Vitest 标签/列/行操作断言与反向断言；真实页面读回 |
| T-21 | 素材库列表与详情显示操作人（素材创建人，姓名由服务端解析） | Go production 用例、合同、Vitest 列序与详情断言；真实页面读回 |
| T-22 | 管理员转素材后弹窗告知目标团队与素材；输出全量角色能力矩阵 | Vitest 单条/批量/失败分支；角色矩阵证据；真实页面读回 |
| T-23 | 系统管理按角色可见：用户管理仅管理员，运营团队/游戏管理高级运营+管理员（高级运营只读），桌面环境运营+高级运营；团队人数服务端化 | Go identity 用例、identity 合同、Vitest 导航/页面角色断言、Desktop 路由与构建 |
| T-24 | 社媒账号增加使用人列与筛选（默认本人）；高级运营仅对本人在本地可操作，他人与管理员只读；sidecar 改由 `canRunLocalAgent` 启停 | Go 三角色本人/他人用例、合同、Vitest 行级门禁、Desktop/Login/PersonalInfo 断言 |
| T-25 | 11 个列表页去掉刷新按钮，改 10 秒自动刷新，抽屉/弹窗/表单打开时暂停 | 新 `useAutoRefresh` 测试与 11 页断言；真实页面等待读数 |
| T-26 | 第三轮八项与第二轮六项统一复走查、签收与归档 | 探针 0 异常、复走查清单、用户签收、`wt chg verify` 与 PR |

## 验收

1. 真实 Scheduler 按计划时间创建任务，跨进程/重启不重复；批次和任务状态、数量上限及策略启停与数据库和页面一致。
2. 真实 Worker、FFmpeg、对象存储产生可播放自动成片；失败/恢复事实可追溯，无无限重试、重复执行或孤儿进程。
3. Cloud Web 与打包 Desktop 显示同一正式状态，自动与人工成片走同一 `composite_output` 和下载链路，Local Agent 实际落盘可播放文件。
4. M5-AC-01～13、M4 相关回归、旧路径扫描和用户最终走查均有证据；未通过项保持未完成，不以模拟或手动触发冒充真实调度。
5. T-10 新策略模型从数据库到 OpenAPI、服务端、共用 Vue 页面一致；手动/定时共用选材引擎，规则、额度、权限与逐项失败边界均有真实证据；M4 人工选材任务与历史快照不回归。M5-AC-01/01a 在新模型复验前保持 TODO。

## 不做

- 不新增生产规则表、第二套批次或成片对象、Agent 视频合成服务。
- 不将 C7 验证中发现的跨仓 Contract、Architecture 或 Ownership 变化直接混入修复；先回 Workspace 更新定义。
- **第三轮显式豁免**：T-19 经用户 2026-10-27 裁定的平台标识重命名（`baijiahao` → `baidu`）是已定义的跨仓 Contract 变更，按 ADR-0024 与 release matrix 同批发布，不走「先回 Workspace 再修」的旧限制；定义与合同在 Workspace 侧同步更新。

## Pending Questions

None.

## 验收记录

- T-01～T-04 机器腿全部 PASS，逐项事实见 `evidence/T-01.md`～`evidence/T-04.md`；进度与残留见 `checkpoint.md`。
- M5-AC-01～12 已在 `delivery/milestones/M5-automatic-production.md` 收口为 PASS（含证据出处）；T-10 模型纠偏后 01/01a/02/03/04/09/10/11 曾退回 TODO，2026-10-17 按新模型重新验回，见 `evidence/T-10.md`。04a/05/06/07/08/12 未受本轮影响，保持 PASS。
- M5-AC-13 与 M4-H2 用户走查签收为唯一未决项；已探明的归属事实（本机设备绑定仅 operator01，自动成片 created_by 为策略创建者）在 `evidence/T-03.md` 如实登记，交用户走查时裁定。
- 2026-10-16 用户给出合成任务页面走查整改结论；T-05 进入实施，改动只归 Cloud 业务事实与共用 Vue 页面，完成后重新走查 M4-H2/M5-AC-13。
- 2026-10-16 用户给出第二轮裁定（创建入口集中到合成任务页、关联实体编号全站去 `#`、已下载行按本地文件分支、历史空名称只清开发库）；T-06 机器腿与真实页面走查 PASS，见 `evidence/T-06.md`；本机 Desktop 的“实测缺文件 → 重新下载”一格无法程序化验证，登记为未验事实。
- 2026-10-16 用户按第二轮交付的真实页面给出第三轮 7 条整改；T-07 机器腿（Web 70 文件/638 测试、production 6 包、双端构建）、migration 064 开发库应用与读回、真实页面走查（含 Worker 真跑 257/258 两条任务与 256 失败样本的步骤记录）全部 PASS，见 `evidence/T-07.md`；“多步成功后中途失败”的真实 run 与本机 Desktop 差异面登记为未验事实；`tokens.css` 从未接入入口的存量问题登记为待裁定，本轮未顺手接线。
- 2026-10-16 用户按第三轮交付的真实页面给出第四轮 4 条（去重策略与素材分区、搜索区与已选区重合、筛选顺序、失败为何无重试），形态经三轮追问拍定为「使用情况一个下拉 + 内联候选」；T-08 机器腿（Web 72 文件/668 测试、production 6 包、双端构建）、migration 065 开发库应用与读回、**真实库并发创建实测**（6 个并发键恰好 1 条落地、重放不算冲突、无死锁）与真实页面走查（含两窗同抢一条素材的中文冲突提示）全部 PASS，见 `evidence/T-08.md`；在途行「排队中」重复显示一格与仅单测覆盖的三项（已使用过排序、50 行上限、状态读失败降级）如实登记。
- 2026-10-16 用户按第四轮交付的真实页面给出第五轮 5 条（已使用过只读、候选默认发布时间倒序、点赞与收藏同步、排队中不执行是否后台没起、已取消能否重跑），逐条追问后拍定为「一条 (策略,素材) 只跑一次、重跑一律走重试」；T-09 机器腿（Web 72 文件/678 测试、production 6 包 + migration 包、双端构建）PASS，**真实库重试三连**（失败重试重定基 `ac+3`、取消后可重试、再重试不再撞 1062 且占位行重开）与创建守卫三态（失败/成功/排队中各被 15219 拒、无新行）实测通过，真实页面走查覆盖抽屉排序切换/已使用过行无按钮/跨策略保留已选的中文拒绝、任务页取消行的重试确认框与回到排队中、我的素材两列与详情抽屉千分位一致；**手工启动 compose-worker 把 25 条积压跑成 0 排队**（success 12→16、failed 5→27）。compose-worker 不在任何发布/部署清单这一缺口按裁定登记待裁定、本轮未修；详见 `evidence/T-09.md`。
- 2026-10-17 用户裁定本轮做到 M5-AC 复验收口（不代签收、不归档），并修掉 compose-worker 发布清单缺口。T-10 机器腿（Web 72 文件/679 测试、Go 85 包行 0 FAIL、双端构建、DMG 03:23:18 且内嵌修复后页面）、真实独立 Scheduler/Worker 全链（策略 36 到点 02:32:05 → 任务 299/300 → 成片 49；单项失败隔离 run d338c176 → 任务 312/314；双进程+重启防重用例）、M4 抽屉路径与 Local Agent 真实下载（任务 315 → 成片 59 → 本地文件 SHA-256 与对象/库三方一致）、Cloud Web 38 项页面走查全部 PASS；走查发现并修复两个真实缺陷（列表行 Vue 代理上的 `structuredClone` 使「编辑」无反应；TDesign `t-select` 的 `<t-option>` 插槽缓存使第一个条件的运算符不随字段变化），均先红后绿。M5-AC-01/01a/02/03/04/09/10/11 按新模型翻回 PASS，M5-AC-13 与 M4-H2 保持未签收。compose-worker 已补进构建/打包/部署/运行检查四处清单，并有双向覆盖用例（变异验证可红）。Linux 发布链路未在本机执行、Desktop 视觉逐屏待用户确认，如实登记；详见 `evidence/T-10.md`。
- 2026-10-21 走查发现合成任务 319/320/321 因「源文件不见了」失败（素材 154/160/159 的 ready 与 key 在库，对象已不存在）。用户裁定：清理只删云端临时文件/临时对象；ready 但对象丢失时按「对象在则用、不在则重新抓取补回」；failed 自动重试准备一次；上传完整性改用 Content-MD5。T-11 机器腿（Go 85 包行 0 FAIL、Web 77 文件/721 测试、双端构建）与真实自愈（319/320/321 重试全部 success，成片 63/65/64；三次各只新增 1 条准备任务，暂存对象 0 残留；Garage 错 MD5 → 400 `InvalidDigest`、正确 MD5 → 200）PASS。用户下载端到端（本机无新鲜受信 Local Agent 节点）与真实并发（第五轮「一条 (策略,素材) 只跑一次」使合法组合不足）未复现，如实登记；M5-AC-13 与 M4-H2 仍未签收。详见 `evidence/T-11-source-self-heal.md`。
- 2026-10-27 用户按第一轮交付页面提出六项修订（完成时间、触发文案统一、游戏选择器只列启用、普通运营可见使用情况计数、素材库列表去文件状态、内容池来源合并），实施为 T-12～T-17，Cloud 侧提交在 `chg/CHG-20261015-098-round2`（PR #13）。机器腿：Web 84 文件/757 测试、production Go 包全绿；三账号机器走查 97 项断言 FAILED 0，console error / 页面异常 / HTTP ≥500 均为 0。复走查中发现并修复来源弹窗「执行周期」直接渲染原始值 `manual` 的缺陷（`contentpool/labels.js` 共用映射，提交 `8b6f818`，修复后 Web 全量与探针复跑均通过）。用户复走查与 M4-H2/M5-AC-13 签收仍待办，清单见 `evidence/2026-10-27-m4-h2-m5-ac13-second-round-checklist.md`。
- 2026-10-27 用户按第二轮交付页面提出第三轮八项修订（自动刷新、综合搜索、平台文案统一、素材操作人、管理员转素材去向、Desktop 系统管理、素材详情改名、入库时间），并逐轮拍定平台标识与角色能力口径；实施为 T-19～T-26。T-19～T-24 机器腿 PASS，逐项事实见 `evidence/T-19-platform-identifiers.md`、`T-20-labels-and-ingest-time.md`、`T-21-material-creator.md`、`2026-10-27-round3-role-capability-matrix.md`（T-22）、`T-23-system-management-roles.md`、`T-24-account-owner-and-local-operations.md`；Cloud 提交在 `chg/CHG-20261015-098-round3`，最新 `f3e34d7`。收尾读数：Web 86 文件/780 测试全绿、Go mediaaccount + localagent 6 包全绿、Cloud/Desktop 双端构建成功、`verify_m0_config` ok。角色矩阵登记 5 项待裁定（Cloud Web 本地页对高级运营/管理员可见、管理员读任意账号 Cookie、账号云端编辑范围、内容池团队公共池、高级运营无法取得可绑定窗口）。T-25 随后完成（见下条）；T-26 三账号复走查/签收仍待办。
- 2026-10-27 T-25 完成（第三轮第 1 项）：内容挖掘、内容生产、系统设置三个分区共 11 个列表页移除「刷新」按钮，改由公共 `useAutoRefresh` 每 10 秒静默重读；抽屉/弹窗/表单打开、有选中行、批量/提交进行中、页面不可见时跳过。合成任务的列表从「有活任务才 5 秒轮询」并入同一实现，详情抽屉 5 秒轮询保留。Cloud 提交 `940716b`；读数：Web 88 文件/799 测试全绿、Cloud/Desktop 双端构建成功、11 页 `>刷新<` 扫描 0 命中且账号/窗口/代理三页阳性对照 3 命中。前端交互规范新增 §5.7，PRD 第四/五章同步。真实 10 秒等待读数并入 T-26，见 `evidence/T-25-list-auto-refresh.md`。
- 2026-10-28 T-26 机器腿完成（第三轮八项 + 第二轮只读回归 + T-23/T-24 角色可见性）：Cloud Web 探针 75 项、Desktop 布局（127.0.0.1:5174）探针 28 项，FAILED 均 0，console error / 页面异常 / HTTP ≥500 全程 0。读数：11 页渲染按钮无「刷新」；内容池 / 素材库 / 用户管理在 11.2 秒窗口内各自动重读列表 1 次，内容池详情抽屉打开期间 0 次；内容池表头与详情为「入库时间」、行操作「详情」、平台显示「抖音」且平台筛选只有抖音；挖掘策略与挖掘任务搜索标签为「综合搜索」；素材库有「操作人」列；管理员转素材内容 972 → 素材 181（team 1「默认运营组」，created_by 1 admin），弹窗给出素材与目标团队；社媒账号使用人高级运营默认本人（本人暂无账号 → 0 行）、切「全部成员」后 4 行且不含 admin，管理员默认「全部成员」7 行；Cloud Web 与 Desktop 布局的系统管理菜单/路由、桌面环境、工作环境胶囊与账号行「检查」禁用提示均与 T-23/T-24 口径一致；Web 会话取 Agent Token 返回 11001「请先在 Desktop 登录」。2026-10-28 00:40 Web 全量 88 文件/799 测试全绿。未覆盖：打包 Desktop 视觉与 sidecar 实际启停、高级运营本人账号的本地执行正面链路（本人暂无账号，且受待裁定 §三-5 阻塞）、开户页平台文案、后台标签节流。清单见 `evidence/2026-10-27-m4-h2-m5-ac13-third-round-checklist.md`；用户复走查与 M4-H2/M5-AC-13 签收仍待办。
- 2026-10-28 用户对角色矩阵五项待裁定给出结论：Cloud Web 开户 / 浏览器窗口 / 代理保持现状；管理员保留 Cookie 只读；账号云端字段与窗口绑定暂不动（用户将重构社媒账号）；普通运营维持内容池团队公共池；高级运营窗口来源随重构再定。复核更正：开户页与代理页走 Cloud API，Cloud Web 可用，只有浏览器窗口页依赖 Desktop 且已有提示——原「三页都是本机执行面」的说法不准确。本轮无运行时代码改动，只更新矩阵 §三、复走查清单 §五、PRD 第三章 §3.2.8；第 3/5 项留待 CHG-098 归档后的社媒账号重构 CHG。T-26 用户复走查与 M4-H2/M5-AC-13 签收仍待办。
- 2026-10-28 用户确认验收完成：M4-H2 与 M5-AC-13 按 `evidence/2026-10-27-m4-h2-m5-ac13-third-round-checklist.md` 的统一复走查结果签收。清单 §五 的未覆盖项——打包 Desktop 视觉与 sidecar 实际启停、高级运营本人账号的本地执行正面链路、开户页平台文案、后台标签节流——按登记保持未覆盖，不因签收改写；第 3/5 项裁定留待后续社媒账号重构。
- 2026-10-28 `python3 scripts/wt.py chg verify CHG-20261015-098`（risk M；fast + integration）：Cloud `go test ./internal/modules/...` 0 FAIL、Agent unittest 728 项 OK、Desktop cargo 540 passed / 6 ignored / 0 failed，release-versions 20 passed；integration（`scripts/verify/verify_m1_integration.py`）红于 `ModuleNotFoundError: No module named 'wt_media_agent.cloud_agent_client'`。该模块由 `e034910`（2026-10-23，已在 `origin/main`）删除，脚本本身早于该改造且不在 `AGENT-INDEX.md` §12 门禁表内，属既有失效，不是本 CHG 改动；`wt chg verify` 因此退出 1，表内各腿均绿。原始日志 `/private/tmp/chg098-wt-verify.log`，不提交。
- 2026-10-28 合并：Cloud round 2 PR #13 `624e04e`、round 3 PR #14 `7dd49e8`；Agent PR #3 `1b6f196`；Desktop PR #5 `8dff82c`。四仓 CI 均通过后合入 `main`，本地 `main` 已同步。
