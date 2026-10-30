# CHG-108 验证记录

## 提交组合

- Cloud: b586848（含检查结算、窗口分离、单行选择、即时回车标签与V7详情修正）
- Agent: 0156c50（实时识别ec766de，契约索引同步）
- Desktop: 56f0600
- Workspace: PR #19 / merge887ddfb；各仓合并号见change.md

## 自动验证

| 动作 | 预期 | 实际 |
| --- | --- | --- |
| Cloud `go test ./internal/modules/mediaaccount/... -count=1`，注入本机测试DSN | 检查结算和原子资料更新正确 | PASS；实际MySQL使用同连接临时表，不改现有账号；验证并行备注/凭证保留、旧编号/重复/窗口变化拒绝、事务回滚、筛选分页与计数 |
| `go test ./cmd/server ./internal/bootstrap/...` | 启动装配可编译 | PASS |
| Vue 账号、窗口、角色、路由、错误反馈定向测试 | 消费方通过 | PASS，先定向14文件111项，最终Vue全量100文件879项 |
| `npm run build:cloud` / `build:desktop` | 两端可构建 | PASS；存在既有大chunk提示 |
| Agent `test_local_account_check.py` / `test_dependency_boundaries.py` | 实时事实与分层通过 | PASS，9项/33项；另cookie读取3项通过 |
| Desktop `cargo test --manifest-path src-tauri/Cargo.toml commands::` | 命令层回归 | PASS，125通过、5个既有忽略 |
| Workspace docs/config/delivery/master/M2静态校验 | 正式事实与组合一致 | PASS |

## 真实环境与平台

- 本机固定数据库 wt_media_cloud；迁移082、083各执行一次成功。执行前账号7条，废弃账号组0条且无外部表引用；不修改历史迁移链，不操作外部窗口/Cookie。
- `bin/control.sh start` 初次强制重建通过Cloud、Agent、BitBrowser、开发入口、CORS、资源、DMG、登录冒烟并挂载启动新包。最终源码组合b586848/0156c50/56f0600重建PASS，Desktop assets与DMG均fresh，登录冒烟与挂载启动PASS。
- 用户授权测试窗口：“测试账号”序号51、“路-华为”序号46。分别经真实Agent处理函数与BitBrowser读取取得正常身份及昵称/UID/头像；全程不调用Cookie写入能力。此处为平台读取证据，完整业务闭环需下面单独确认。
- 本机验收账号operator01原凭据不符合环境技能约定，按技能通过管理员重置接口恢复约定测试密码；不更改平台密码或Cookie。

## 业务闭环

| 动作 | 预期 | 实际 |
| --- | --- | --- |
| 真实Cloud登录 → 发起检查 → Agent处理函数 → 指定BitBrowser窗口 → 平台响应 → Cloud回报/GET | B站与百度正式身份一致，检查不写Cookie | PASS；B站账号1/窗口10，百度账号9/窗口37；均有真实UID/昵称/头像及normal结论，凭证前后摘要一致 |
| 百度无分类、无已存Cookie建台账后绑定检查 | 可正常识别 | PASS；账号9分类为空，凭证仍为空 |
| 重复/旧编号、失败、并行资料更新、异UID回报 | 幂等、结构化拒绝、历史保留、正式身份不接管 | PASS；旧编号23002；失败保留有效检查时间/登录结论；标签/备注不被检查覆盖；异UID单独保存观测 |
| 异UID后再真实检查原UID | 回到正常 | PASS；发现旧mismatch状态残留后修复27f04a4，并添加恢复回归；两个账号最终以真实成功检查恢复 |
| 手填身份/混合启停、服务端分页与本人范围 | 拒绝越界字段，分页准确 | PASS；非法PATCH10001，page2/size1正常，本人台账5条 |

## 页面与桌面桥接

- PASS：打包Desktop以运营账号登录，指定百度账号9单项勾选后批量检查，页面结果“共1项，成功1，失败0，跳过0，等待0；检查完成：登录正常”，最近检查为刚刚。
- PASS：取消百度勾选，仅勾选B站账号1，再次通过真实Tauri → Sidecar → BitBrowser → Cloud结算，页面结果同为1成功/0失败。未操作其他平台窗口。
- PASS：共享Vue真实页面走查发现并修复表格row-key错误（单项勾选误关联）和立即回车早于搜索防抖（新标签未加入）；修正后仅目标行checked，回车出现新标签且输入清空。
- PASS：切换一级游戏后出现对应二级多选，无“暂不分类”；编辑只保留业务资料；“更多 → 更换窗口”进入独立960px候选表，搜索“路-华为”准确显示当前绑定、序号46，无自动选择。
- PASS：详情按V7显示头像/昵称/UID、业务分类/标签/备注、窗口名/分组和检查结论，800px只读、无footer；移除旧技术ID和八项实现检查清单。以上Vue页面通过本地dev入口交互验证，最终b586848包重建、资源fresh与DMG门禁PASS。
- 角色范围：普通/高级/管理员归属、资料与本机权限在Service/Handler及前端定向用例验证；真实运营页面仅显示本人5条。管理员Cloud真实页面复核PASS：8条全局账号、团队/使用人筛选；无新增、批量检查或本机按钮，保留资料查看/编辑。

## Review

按CHG边界复查提供方和直接消费者：资料PATCH不写身份；检查只更新检查字段，失败与迟到不破坏历史；旧组/identify/开户路由无消费者；保留共享窗口/代理/类目与真实Cookie。Cookie更新旧链路由109替换，不提前创建批次对象。

PR：Cloud #17、Agent #5、Desktop #7、Workspace #19。CI发现Agent契约README版本索引过期，0156c50修复后定向8项通过，重跑CI已PASS（658项，1项既有skip）；Cloud CI发现路由删除后的固定分母、旧技术ID断言及筛选占位不一致，b586848对齐，定向23项与全部Vue100文件879项PASS。

## 最终门禁

四仓PR CI均SUCCESS；最终组合强制重建及启动PASS。真实运营两平台检查、管理员Cloud视角、共享Vue表单/独立选窗/只读详情已通过；人工最终走查留在用户验收阶段，不以开发验证代替用户确认。
