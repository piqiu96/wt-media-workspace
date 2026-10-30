# CHG099 接续点 · 2026-10-30

## 当前状态

- CHG 状态为 `VERIFYING`。Workspace、Cloud、CHG099 Agent 工作树和 Desktop 的候选改动均留给人工审核；未提交、合并或发布。
- Agent 仅使用 `/Users/aqiuye/Develop/workspace/wt-media/wt-media-agent-chg099`，不使用旧 098 Agent 分支。运营库固定为 `wt_media_cloud`；隔离测试库每次用后删除。
- 用户授权的“测试账号”窗口和静态测试代理早前现场验收已完成；最新只读检查发现当前 Cloud 又有“测试代理”ID 1 并正式关联“测试账号”窗口 ID 10，不能沿用早前的“已清理”结论。此次未改变关联；原恢复信息不在当前仓库，保留现状交运营决定。用户明确暂不测试真实动态供应商提取。
- 用户要求 `example/` 和 `evidence/` 仅留最终稿；不保存截图缓存、临时测试数据或凭据。短周期额度低于 5% 时保存并停止。
- 用户于 2026-10-30 明确确认“CHG099 已走查完毕”；人工整体走查已签收。用户随后指定先将前置 CHG107 合入远端 `main`，再合入 CHG099；本轮不发布。CHG107 的 Cloud 与 Workspace PR 已通过 CI，并用保留历史的 merge commit 合入远端 `main`。

## 已完成与最新验证

1. 窗口同步、运行状态读取、代理应用/未知核实、解绑、未分组编辑、缺失窗口核实与运行反馈已落地；真实比特/Cloud/Desktop 现场结果见 [evidence/acceptance.md](evidence/acceptance.md)。
2. 新反馈已落地：非空且可核实主账号的比特快照把未找到的窗口标记 `local_missing`；日常列表默认展示全部未删除窗口，独立“窗口状态”列标明“已找到 / 未找到”，筛选只提供这两个值，清空即显示全部。另有独立“清理已删除窗口”入口用于批量清理；确认删除前保留账号关系和历史，缺失窗口继续占用原代理额度。比特返回零窗口时本机接口无法独立证明登录主账号，拒绝批量标缺失并提示核实。窗口详情按记录的团队 ID 解析真实团队；同步预览显示字段原值/新值；管理员团队输入筛选，其他角色无该筛选。
3. 代理 `proxies.id` 已迁为 MySQL `BIGINT UNSIGNED AUTO_INCREMENT` 主键，Cloud API 返回数字 ID；窗口正式/预留关系与当前操作回执迁为数字引用。旧 ID 留在仅供追溯的 `legacy_id`。正式契约和发布矩阵已更新，旧客户端与新 Cloud 不允许混用。
4. Cloud `go test ./...` PASS；Web 全量 99 文件/872 项 PASS，随后关联窗口列修复的页级 8 项 PASS；Cloud 与 Desktop Web 正式构建 PASS。隔离库空库应用 83 条迁移及四项代理 live 测试 PASS；另在 82 条旧结构上播入字符串代理、正式绑定、预留和回执，应用第 83 条后逐项验证映射与自增，PASS；测试库已清理。
5. 当前运营库已应用 83 条迁移：1 条代理转为整数 ID 1，1 条正式绑定引用保持，42 条窗口及 3 条缺失记录保持；无测试记录写入。隔离四仓布局（指向 CHG099 Agent）M0 配置和 M2 契约验证 PASS；工作区与目标仓 `git diff --check` PASS；原型新增脚本 `node --check` PASS。
6. `WT_MEDIA_AGENT_SOURCE_DIR=/Users/aqiuye/Develop/workspace/wt-media/wt-media-agent-chg099 bin/control.sh restart` 返回 0：Cloud、Agent、两 worker、比特、两个开发服务、Desktop 资源、DMG 和登录烟测全部 PASS。用户登录该版 DMG 后，`control.sh status` 显示 Agent `health=refused owner=desktop`，表示 Desktop 已接管带令牌本机服务。当时运营角色只读实看：代理数字 ID 1；旧版列表曾隐藏 3 条缺失记录，已按本轮决策改为默认显示，最新版本尚待实看；窗口详情团队与数据库 `team_id=1` 的“默认运营组”一致。
7. 新增的供应商精简决策已同步原型和共用 Vue：代理列表仅保留地区，供应商保留在详情与新增/编辑。Web 99 文件/872 项、Cloud/Desktop Web 构建和原型语法均通过；再次使用 CHG099 Agent 完整重启及 DMG 闸口通过。
8. 最终 DMG 登录后的运营角色只读实看：列表仅“地区”不显示供应商，详情独立展示供应商。关联窗口表此前因前端误用 `name` 而显示空白，现改用接口的 `bit_name`；页级 8 项测试、Desktop Web 构建和再次完整 `control.sh restart` 均通过，最新安装包详情里窗口名称显示“测试账号”。最终 `control.sh status` 返回 0，Agent 为 `health=refused owner=desktop`；未触发检测或业务写入。
9. 用户指出三条历史缺失在每次有更新的“同步完成”弹窗中反复列为待处理。后端已排除已确认缺失的再次扫描差异；前端结果页误从全量窗口算异常。此前仅展示本次扫描涉及的异常；按 2026-10-30 最新裁决，历史缺失现于同步结果中单独列为“历史待处理”，不计入本次异常，仍可核实或确认删除。复现测试先失败、修复后相关 24 项 PASS，后端定向测试与 Desktop 前端构建 PASS；CHG099 Agent 完整 `control.sh restart` 再次返回 0。先前 DMG 只读实看：当时列表 37 条，另有缺失记录 3 条（ID 462、38、74）；新列表默认全显尚待实看。本轮未为了制造变化点击同步或修改运营窗口，真实有变化结果页留待自然变化时实看。
10. Q-03 用户最终裁定：不加“当前窗口 / 已缺失”双标签，不保留“窗口记录”筛选；只有扫描后找不到的窗口进入独立清理入口，单项/批量删除前人工确认确已在比特删除。Cloud 清理改为锁行复核、账号解绑与核验状态重置、窗口物理删除、释放托管代理名额及无凭据审计的单条事务；普通窗口和待确认代理操作不能删除。共用 Vue 已改日常列表及清理对话框，原型新增清理/确认/结果三场景；正式 Product、Engineering、OpenAPI 与错误码同步。Cloud profilebinding 定向测试及 Web 页级测试/构建 PASS，原型 `node --check` 和两仓 `git diff --check` PASS。隔离 MySQL 应用 83 条迁移后，带关联账号与托管代理的删除事务测试 PASS，测试库已清理。最新 DMG 完整 `control.sh restart` 闸口 PASS，尚未登录做新清理页现场只读走查；未删除 462、38、74 或其他运营数据。
11. 用户指出原型把“窗口缺失”挂在代理信息下。已按来源拆分：列表代理列只显示代理问题；原型详情把“最近同步未找到”放在窗口信息，缺失时不显示未经核实的代理配置结果；正式页面的代理列及详情同步限制。状态来源与展示位置已写入工程规格及原型 README。Web 页级 16 项、正式构建、原型两份 JS 语法、两仓 diff 检查 PASS；上述最新 DMG 已包含该修正。
12. 本轮用户进一步确认“窗口状态”独立列及筛选、空选显示全部，并要求代理信息可点开详情。正式共用 Vue 与原型均已修改：托管代理为只读侧栏，比特自管代理为只读居中弹窗，直连不提供详情入口；缺失窗口的地址均标作上次同步。Product、Engineering、CHG 定义已同步。Cloud Web 页级 24 项、正式构建、原型语法及两仓 diff 检查 PASS。CHG099 Agent 源完整 `control.sh restart` 返回 0；登录最新 DMG 后只读实看默认 40 条、状态筛选分别 37/3 条、两种代理详情弹层；`control.sh status` 返回 0，Agent 为 `health=refused owner=desktop`。未操作现有窗口或代理，详见验收文件。

13. 2026-10-30 最新已确认方案：窗口状态列与筛选均移至运行状态前；单项危险按钮统一“删除”，悬停红字浅红底、最终确认红色实心，规则写入统一前端规范及 common 示例。同步原型新增历史待处理示例，Cloud 共用 Vue 在本次异常与历史缺失之间分开计数；没有新增变化时仍可从同步窗口核实或删除历史项。Product、Engineering、CHG、原型 README 同步。Cloud 定向 3 文件 40 项 PASS、Cloud/Desktop Web 构建 PASS；原型脚本语法与两仓 diff 检查 PASS。浏览器策略拒绝 file:// 原型预览，本轮没有绕过；最新 DMG 已由 CHG099 Agent 源完整重建并启动，`control.sh restart` 构建及启动前闸口 PASS；应用停在登录页。随后 `control.sh status` 显示 Cloud/worker/前端正常，但 Agent 端口暂未监听，需登录后检查 Desktop 接管结果；新交互仍待只读实看。未删除运营窗口。

14. 2026-10-30 现场代理绑定故障：Cloud 对窗口 17 与 37 的开始操作均返回 201，正式占用 1、待确认预留 2，故选择器剩余 0；PyInstaller 归档实测当时 DMG 内 Agent 仅有旧 `/api/v1/proxy-mutation`，没有 Desktop 调用的 `/api/v1/proxy-write` 与 `/api/v1/proxy-verification`，404 发生在本机代理写入入口。已将 Agent 冻结构建强制指向选定源码、校验冻结路由，并在 Desktop 打包前检查 Agent 构建清单的必需路由；Cloud 页面显式显示待确认占用。真实旧包校验失败、新包校验通过；Cloud 3 文件 37 项、Agent 22 项定向测试 PASS，完整 `control.sh restart` 及 DMG 闸口 PASS。窗口 17“一数儿”从新包读取核对为不一致，按正式流程释放预留；窗口 37“路-华为”原核对因比特直连详情省略认证字段而不可核实，已修复为先用代理类型/地址/端口判定明确不一致，最终 DMG 中正式核对结算失败并释放预留。运营库再次只读核对为正式占用 1、预留 0；代理页实看“1 / 3、剩余 2”，AOS账户选择框实看剩余 2、可用。未重新绑定或人工改写数据库。

15. 2026-10-30 后续只读复查：当前“起飞”已登录 `operator01`，未重新输入或保存用户提供的凭据；代理列表仍显示测试代理 ID 1“1 / 3、剩余 2”。`bin/control.sh status` 返回 0，Cloud 与前端健康，Agent 为 `owner=desktop`。当前窗口页无筛选时展示 37 条、待处理 0，未出现此前三条缺失记录和清理入口；原因尚未核实，不将旧 40 条现场结论套用于当前数据，也不操作运营数据制造缺失样例。

16. 用户反馈批量设置后列表仍显示代理差异，打开同步窗口又提示同一字段变化。现场只读预览确认窗口 22 与 17 的比特代理地址/端口已是目标配置，Cloud 旧镜像未跟上；按已授权的同步确认处理这两项后，结果为更新 2、无新异常，列表恢复正常。根因是明确成功回执结算只更新 `proxy_id`，未更新 `bit_proxy_*`，不是批量页面缺少 `reloadAll()`。Cloud 已在操作开始时保存非秘密连接快照，成功结算时同事务投影正式关系和最近确认的连接；失败/待确认不投影。新增回执单测与隔离 MySQL 实测通过（83 条迁移、结算后字段一致，测试库已删除），Cloud `go test ./... -count=1` PASS；CHG099 Agent 源完整 `control.sh restart` 与 DMG 构建/登录烟测 PASS，Workspace/Cloud `git diff --check` PASS。没有为了验收再次对运营窗口发起代理写入；重启后现场窗口状态已被其他操作改变，保留当前状态，不代用户回滚。

## 后续交付工作

1. 用户于 2026-10-30 确认 CHG099 整体人工走查完成；此前逐项未留实屏证据的场景不冒称为各自独立现场 PASS，统一签收见 [evidence/acceptance.md](evidence/acceptance.md)。批量设置后的列表与同步差异已单独确认验收；最新成功回执投影通过独立 MySQL 结算验证，未为了验收重复写入运营窗口。
2. CHG107 Cloud [#15](https://github.com/piqiu96/wt-media-cloud/pull/15) 与 Workspace [#16](https://github.com/piqiu96/wt-media-workspace/pull/16) 已先行合入远端 `main`。CHG099 的 Cloud/Workspace PR 已切回 `main` 基线；差异清单不含 CHG107 迁移及过期计划副本。Agent/Desktop 原本即基于 `main`。
3. 整理四仓 CHG099 改动，排除其他任务文件和构建缓存；Cloud 根 `node_modules/`、Desktop `__pycache__/` 已加入各自 `.gitignore`，最终提交前复核暂存清单。执行最终适用验证，按仓提交并交由人工审核；不自行合并或发布。
4. 真实动态供应商提取的现场网络验证按 Q-02 延期；A37 同页会话“查看上次导入结果”作为用户整体走查后保留的行为，不擅自改成历史中心。

## 人工审核入口 · 2026-10-30

- 前置 CHG107 Cloud [#15](https://github.com/piqiu96/wt-media-cloud/pull/15) 与 Workspace [#16](https://github.com/piqiu96/wt-media-workspace/pull/16) 首次 CI 均 PASS，已依用户指定顺序用 merge commit 合入远端 `main`；远端 `main` 分别包含其原分支提交。CHG099 PR 已切回 `main` 基线。
- CHG099 四仓分别提交并推送：Cloud [#16](https://github.com/piqiu96/wt-media-cloud/pull/16)（`e73050a`）、Agent [#4](https://github.com/piqiu96/wt-media-agent/pull/4)（`ae14d18`）、Desktop [#6](https://github.com/piqiu96/wt-media-desktop/pull/6)（`bcb6105`）、Workspace [#17](https://github.com/piqiu96/wt-media-workspace/pull/17)（`fa80e1e` 起，后续有文档修正）。Agent/Desktop GitHub 校验 PASS；Cloud/Workspace 切回 `main` 后需触发并核对常规 CI。
- 最终本机回归：Agent `bash scripts/test.sh` 656 项 PASS；Desktop `bash scripts/test.sh`（Rust 541 项及脚本闸口）PASS；Workspace `python3 scripts/docs/check.py` 15 个索引 PASS、Delivery 治理检查 PASS；Cloud Go 全量与隔离 MySQL 回执投影验证见验收记录。Cloud 根 `node_modules/` 和 Desktop `__pycache__/` 已忽略，未进入提交；Workspace 的发布互动原型及早期社媒分析稿属于其他工作，未纳入 CHG099 PR。
- CHG099 在四仓 CI 与差异复核完成前保持 `VERIFYING`；按用户指定顺序合入后再同步发布矩阵与归档为 `DONE`。本轮不发布。

## 接续边界

保护他人改动；不重新全仓扫描，不操作其他运营窗口/代理，不自行合并发布。进一步记录验收时只写最终可复核事实到 `evidence/acceptance.md`。
