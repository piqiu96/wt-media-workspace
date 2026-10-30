# CHG-108 实施计划

## 任务理解

按 M2-D1 完成账号维护及人工登录后检查同步；按 V7 重构页面，清理对应无用代码，不提前实现 Cookie 写入/批次对象。整个重构的数据表/接口目录由 Engineering social-accounts.md 唯一维护，109/110 引用，不复制到各计划。

## 当前事实与约束

Cloud、Agent、Desktop 起始工作区干净；Workspace 的发布/互动原型及两份旧报告为既有未提交工作，不覆盖。当前模块未投入使用，允许破坏性重构，但不得操作真实外部 Cookie 来完成清理。共享类目/窗口/代理能力保持归属，既有顺序迁移保留。

## 计划修改

### Task 1：正式基线与原型

- 当前 PRD 第三章 §3.3 重写，§3.6 改为指针；总 PRD、第二章、ADR-0030、运营资源规格同步。
- 固定 example/proto/social-accounts/index.html 为已批准原型；不把评审目录、演示身份切换或故障注入加入运行时。
- M2-D1～D3、108 active/109–110 planned、LEDGER 对齐。
- 验证：python3 scripts/docs/check.py；python3 scripts/verify/verify_delivery_governance.py；python3 scripts/verify/verify_product_master_alignment.py。Expected: 全部退出 0。
- 清理过期 Master 复制流程与锁死旧 M2 文案的验证，保留真实闭环链接验证。测试：tests/test_verify_product_master_alignment.py，10 项 PASS。
- 提交边界：Workspace 独立 planning/baseline 提交，只包含本任务文件。

### Task 2：检查与资料的 Cloud 闭环

文件：Cloud contracts/cloud-api/v1/media-accounts.openapi.yaml、business-schemas/v1/media-account.yaml、business-enums/v1/media-account.yaml、cloud-error-codes/v1/media-account.yaml；internal/modules/mediaaccount/{model,dto,service,repository} 及 handler/router；migrations/20261030_082_account_check_results.sql。

接口：保留 POST /media-accounts/:id/check 与 /check/result；result 新增 execution_status=completed/failed。Account 新增 last_check_status/message/identity、check_operation_id/started_at/profile_id；Store 新增 BeginCheck(id, profileID, operationID, at) error 与 FinishCheck(record, operationID, profileID) error，专用 SQL 条件更新只写检查/身份字段。重复当前已结算编号返回现有结果，旧编号或目标已变化返回 stale_check，不写任何字段。

- RED：TestCheckRefreshesKnownIdentity、TestCheckPreservesIdentityOnMismatch、TestCheckFailureRetainsPreviousConclusion、TestCheckRejectsStaleOrChangedProfile、TestCheckResultIsIdempotent、TestCheckWithoutCategoryOrStoredCookie；Repository SQL 测试验证匹配编号/窗口及零行拒绝。Expected: 针对缺失行为失败。
- GREEN：实现上述行为、迁移与相应 DTO；失败回报由前端调用同 result 接口。成功只表示取得平台结论，不把未登录当执行失败。
- 资料 PATCH 收敛 category_ids/tags/remark/enabled，标签原子替换；移除手填身份/状态写入口与无消费者账号组全栈。新增用于用户/团队/一级类目收窄的过滤投影，复用现有归属校验。
- 验证：go test ./internal/modules/mediaaccount/...；受影响身份/窗口调用方定向测试；提供方契约校验和新迁移语法/测试库执行。Expected: PASS，若测试库不可用则明确未验收，不声称迁移已执行。
- 提交边界：Cloud 检查/维护 API 及其测试、迁移、契约；Workspace 契约映射独立提交。

### Task 3：Agent 只读识别与 Desktop 消费

文件：Agent local_api/server.py、services/browser/cookies.py、clients/bilibili/identity.py、clients/baidu/identity.py、提供方契约和现有账号检查测试；Desktop src-tauri/src/dto/account.rs、commands/account.rs、contracts.lock.json；Vue apps/desktop/features/local-agent/service.js。

- RED：实时读取失败不能伪装成功；本次识别失败与未登录分开；不同 UID 保留真实观测昵称/UID；检查不调用写 Cookie/清理方法。
- GREEN：以实时观测及平台响应形成结果，明确读取来源/错误；Desktop 只解析和桥接，不重写业务结论。提供方先改契约，再同步 DTO/锁。
- 验证：Agent 账号检查与 Cookie/browser 相关定向 pytest；Desktop account DTO/命令定向 cargo test；跨仓契约检查。Expected: PASS。不启动真实浏览器来跑自动单测。
- 提交边界：Agent 与 Desktop 各自独立提交。

### Task 4：最终账号维护页面与清理

文件：Cloud web/src/modules/accounts/ 拆分 AccountsPage.vue、components/*、accountMaintenance.js 及行为测试；shared/api/mediaAccounts.js；shared/layout/nav.js（以实际引用定位）；两端 router.ts；utils.js 和旧开户判断的真实消费者。

- RED：独立行为测试覆盖一级切换清空二级、回车标签去重、本人/团队/管理员范围、本机门槛不依赖分类/已存 Cookie、检查失败回报/保留结论、身份对照、批量检查七计数、首次加载与刷新失败差异。使用真实纯逻辑与调用边界，不再靠源代码字符串测试替代行为。
- GREEN：按 V7 和公共组件实现列表、800px 只读详情、560/640px 编辑、新增与凭证查看、960px 绑定/批量检查；窗口详情只读。资料、启停、绑定与检查分开。保留列表上下文，更多门槛及分页规则正确。
- 删除 AccountOpeningPage.vue、两端 account-opening 路由/菜单、无调用客户端方法与旧冻结源码断言；批量 Cookie 最终入口在 110 随真实流程交付，不保留旧假成功实现。
- 验证：npm test -- src/modules/accounts src/shared/api/mediaAccounts.test.js 及受影响路由/导航测试；npm run build:cloud；npm run build:desktop。Expected: PASS。1440/1920 走查与 V7 对照；浏览器人工登录后真实 B站/百度识别另留事实结论。
- 提交边界：Cloud 页面与清理独立提交。

### Task 5：整体 review 与验收

运行修改对应检查，记录最终提交基线；独立 review 检查 Cloud 结算、数据库并发、平台读写隔离及页面。自动验证通过不能替代授权账号真实验收。未经真实验证的条目保持未验收，108 不标 DONE、不激活依赖 109/110。合并后清理工作分支及无独立价值中间材料。

## 明确不修改

不新增审批/审计、接码、周期全量检查、通用任务/许可中心；不重新建设公共窗口和代理，不触及真实外部会话；不提交既有无关工作。

## 冲突与未确认项

已确认的 V7 和用户对“未上线直接重构”的裁定优先，相关旧规则在本次回写。真实账号、目标测试库及打包 Desktop 验收需要实际可用环境；先完成不依赖这些条件的实现及自动验证，不能将环境未知写作 PASS。

## Review Focus

- 同一账号两个并发检查的旧响应和窗口换绑后迟到响应。
- 平台返回正常但 UID 与台账不同，不能更新原 UID/昵称。
- 检查链路错误与明确未登录不能混作同一状态。
- 新增/编辑没有类目或 Cookie 仍可登录维护。
- 清理没有误删共享数据/平台适配，也没有残留旧开户入口。
