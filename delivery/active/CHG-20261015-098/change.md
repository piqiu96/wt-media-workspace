# CHG-20261015-098：M5-C7 真实计划时间全链与 M4/M5 统一验收

- Status: IMPLEMENTING
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

## 验收

1. 真实 Scheduler 按计划时间创建任务，跨进程/重启不重复；批次和任务状态、数量上限及策略启停与数据库和页面一致。
2. 真实 Worker、FFmpeg、对象存储产生可播放自动成片；失败/恢复事实可追溯，无无限重试、重复执行或孤儿进程。
3. Cloud Web 与打包 Desktop 显示同一正式状态，自动与人工成片走同一 `composite_output` 和下载链路，Local Agent 实际落盘可播放文件。
4. M5-AC-01～13、M4 相关回归、旧路径扫描和用户最终走查均有证据；未通过项保持未完成，不以模拟或手动触发冒充真实调度。
5. T-10 新策略模型从数据库到 OpenAPI、服务端、共用 Vue 页面一致；手动/定时共用选材引擎，规则、额度、权限与逐项失败边界均有真实证据；M4 人工选材任务与历史快照不回归。M5-AC-01/01a 在新模型复验前保持 TODO。

## 不做

- 不新增生产规则表、第二套批次或成片对象、Agent 视频合成服务。
- 不将 C7 验证中发现的跨仓 Contract、Architecture 或 Ownership 变化直接混入修复；先回 Workspace 更新定义。

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
