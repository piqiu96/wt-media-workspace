# M6-A 验证记录

本页保留 2026-11-18 原实施验证，表中旧路径和删除状态只用于追溯当时结果。当前代码和规则以 [2026-11-19 审查修改验证](review-corrections.md)及正式工程设计为准。
2026-11-19 已修复安装版封面读取策略、发布模块业务时区转换和用户截图反馈（筛选横线、历史可读性、标题默认带入/编辑）；最终前端 1025 项、原型 351 项检查通过，上轮 Rust 540 项通过；已重建安装包并实际确认列表封面及筛选区显示。历史和标题选择的完整页面操作仍交人工接续。见[走查缺陷修复](app-walkthrough-fixes.md)。

2026-11-18—19 当前源码全环境与安装包走查见[安装版与真实浏览器走查](app-walkthrough.md)：构建、签名及启动门禁通过；已完成安装版登录、列表、快速发布空校验和底栏局部核对。发现安装版封面加载失败及两端时间显示差异；资源选择、详情和完整发布流程尚未验收，已保留登录环境供人工接续。以下历史 PASS 不替代本轮完整验收。

页面部分补充：本轮走查发现原有“原型核对”描述不足以证明视觉一致性。公共样式、快速发布及详情的整改范围、差异和最新验证见 [页面整改验证](visual-alignment.md)；下表保留原轮次业务验证事实，不作为本轮页面视觉签收。

验证日期：2026-11-18。Cloud 基线 `9f132dd`，实施提交 `bd099eb63320bd0c5a7d57af3d8c71b15a51ca83`、真实走查修复 `e4780477d2771f641d9e32d9e94f2f85dc1e446c`。本记录只说明实际结果；M6 与本 CHG 均未标记 DONE。

| 检查 | 实际结果 |
| --- | --- |
| Cloud `bash scripts/test.sh` | PASS：全量 Go；共享前端 136 个测试文件、1005 项测试；启动控制脚本 12 项 |
| `WT_MEDIA_CLOUD_HOME="$PWD" WT_MEDIA_TEST_LIVE_DB=1 go test -v -count=1 ./internal/modules/publishing/repository ./internal/modules/files/service` | PASS：8 项实际 MySQL 测试；各自建立并删除隔离库。全新库 105 个原始迁移及重复执行、12 请求争抢同成片、请求键防重、审计回滚、修订冲突、引用/删除竞争、已有生产 JSON 引用及权限分页统计均通过 |
| 接口与 Contract | PASS：4 个正式接口与 OpenAPI 路径对应，均要求登录；严格输入拒绝越权字段、数字形式的大 ID 及尾随 JSON；修订冲突返回当前版本；本单元没有授权或执行接口 |
| 真实页面走查 | PASS：Cloud 与 Desktop 开发入口均由 operator01 实际打开、点击查询与统计卡片、提交空表单、选择账号 9、拒绝类目不符的成片 128、关闭资源选择器和确认离开未保存表单；两端均无页面异常。脚本在 Cloud `web/scripts/test-publication-preparation-browser.mjs`，访问地址使用实际启动输出，经环境变量传入 |
| 原型核对 | 按 change.md 固定的 Cloud 原型基线核对：统计/筛选/任务表、全页快速发布、三段内容与固定页脚、共用资源选择器。没有复制原型代码到正式运行入口 |
| 两端构建 | PASS：`npm run build:cloud` 与 `npm run build:desktop`；存在已有的大包体提示，无构建失败 |
| Workspace | PASS：211 项测试、`verify_m0_config.py`、`verify_product_master_alignment.py`、`git diff --check`；CHG 官方 verify 曾因提交后旧调度服务及 Desktop 构建过期失败；刷新服务并从当前提交重建后，官方 verify 全部通过。未将过期产物视为通过 |
| 素材长链接缺陷 | 先复现规范长链接被错误当成 shorturl 的失败测试，再修复为既有 ID 查询协议；原短链测试保留并通过。真实服务对同一视频 ID 返回成功 |
| 完整真实创建与读回 | PASS：系统内容 1026 经正式入库为素材 186，生产任务 713/714 实际生成成片 129/130；完整下载成片 130，13,683,509 字节与 SHA256 均匹配。Cloud 实际表单使用账号 9、成片 130、封面 12 创建任务 3，读回 pending、无授权、0 次执行；编辑后修订 2。原键重放返回原任务，重复占用、旧修订修改及删除引用封面均拒绝。Desktop 开发页面查询并编辑同一任务，读回修订 3、pending、0 次执行，无页面异常 |
| 走查发现并修复的上传缺陷 | 初次真实创建发现 GORM 把新文件 delete_state 写成空值，列表可见但引用锁拒绝。隔离 MySQL 回归先失败再通过；上传明确初始化 ready，模型默认值保持数据库语义；增量迁移只修复空值并增加状态约束，绝不恢复 deleting。实际新上传封面 12 可正常创建任务。修正资源后清除旧校验提示，实际复测通过 |
| 小文件与压缩处理 | 原视频约 63 MB，被外部 nginx 413 拒绝；按用户授权保留完整 202.95 秒压缩为 6,407,579 字节，正式上传文件 10 成功。原素材的规范源文件已有其他摘要的不可变占位，压缩替换被正确拒绝，未覆盖。随后改用系统真实 37.9 秒素材，通过正常生产流程完成上述成片；保留旧任务 711/712 的失败记录，未修改账号/成片类目或生产任务结果 |
| 真实平台投稿 | 未执行。本单元创建不授权执行；真实作品、平台回执与断网核实仍由 M6-B/C 验证，不能以以上测试代替 |

前端脚本需要 `WT_MEDIA_BROWSER_BASE_URL`、现有登录态路径 `WT_MEDIA_BROWSER_STATE`、输出目录 `WT_MEDIA_BROWSER_EVIDENCE`、已授权账号 ID `WT_MEDIA_BROWSER_ACCOUNT_ID`；可指定已知不匹配成片 `WT_MEDIA_BROWSER_INCOMPATIBLE_OUTPUT_ID`。登录态与凭据只留在本机，不进入 Git。

文件删除的对象故障恢复另由 files Service 实际调用路径测试：物理删除失败后保留 deleting，可重试；访问与选用均拒绝，恢复列表不返回资源地址。隔离库数据和单位测试替身不作为真实发布证据。

Cloud 独立 PR：[wt-media-cloud#44](https://github.com/piqiu96/wt-media-cloud/pull/44)。提交通过 GitHub 官方对象 API 上传，逐文件 SHA、tree 及 commit SHA 与本地完全一致；常规 Git HTTPS 推送超时。

Desktop 安装包曾从 Cloud `bd099eb` 构建、签名并启动；随后从最新 `e478047` 重建并通过签名与组件版本检查，包内前端版本 `0.1.0+e478047`。原生 UI 自动化连续两次读取超时，尚不能宣称此安装包的页面点击走查通过；两端开发入口的浏览器走查结果见上表。

页面证据：[Cloud 创建](cloud-created-task.png)、[Desktop 共用任务](desktop-shared-task.png)、[不匹配资源拒绝](resource-eligibility.png)。成片完整下载核对值见 [output-readback.json](output-readback.json)。

复现完整创建走查时，在既有环境参数外传入 `WT_MEDIA_BROWSER_OUTPUT_ID` 与 `WT_MEDIA_BROWSER_COVER_ID`，必须使用真实、可用且未被当前平台占用的成片。`WT_MEDIA_BROWSER_EXISTING_TASK_ID` 模式用于另一端查询、编辑同一正式任务；不会授权执行。测试后保留任务供 Review，不清空真实业务数据来重跑。

追加菜单遮挡与按钮职责修正已完成自动化检查：69项宽窄屏UI断言、18项既有原型回归、1007项前端测试及双入口构建通过；证据与M6-C未完成能力见[页面走查追加记录](visual-alignment.md#追加走查菜单遮挡与按钮职责)。真实任务及安装版验收不由本轮固定数据走查代替。

执行历史的最新设计及实施验收见[执行详情抽屉整改](execution-history-drawer.md)。此前折叠展示与查看原始反馈的接续说明已被该设计替代；原始审计数据仍保留。
