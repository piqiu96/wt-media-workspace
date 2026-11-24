# 快速发布收尾验证

2026-11-23；CHG106；Cloud提交`02067b0`。范围为管理员执行边界与正常／常见异常流转收尾，供PR审核。本轮不新增真实投稿、不修改原审核中稿件结论；多账号联合验收待批量发布完成后统一进行，生产远端代理出口尚未实测。

## 修改与失败先行

Cloud共用Vue隐藏管理员在发布页、成片列表及素材成片抽屉中的发布入口；管理员成片发布直达链接不初始化表单或读取草稿。流程入口在访问草稿、复制内容及原现场桥接前检查当前角色，管理员仍可查看、编辑云端记录，执行停止、放弃与结果核实等既有管理操作。

服务端复用既有身份与错误规则，拒绝管理员创建、启动、重试和复制发布任务；执行输入复查不接受管理员作为执行所属用户。未新增权限框架、数据表、接口或契约字段。原执行测试改用有团队／类目授权的运营用户。

新增前端2项用例先复现“管理员进入新建表单、弹出执行授权”，后端4个子场景先复现“管理员创建、启动、重试、复制均放行”；最小修改后通过。自行走查同时修正旧页面回归脚本与当前草稿返回、AI选择框、双封面及图片库接口不一致的测试数据／定位。

## 本轮实际验证

| 操作 | 预期与实际结果 | 结论 |
| --- | --- | --- |
| Cloud `web/`：`npm test -- src/modules/publication src/modules/compose/pages/MyOutputsPage.test.js src/shared/api/publicationDraft.test.js src/apps/desktop/desktopRoleGuard.test.js --no-file-parallelism --maxWorkers=2` | 17文件112项通过；管理员进入创建／复制／执行／重试／原现场继续前被阻止，详情仍可访问；原内容、封面、草稿与结果处置回归通过 | PASS |
| Cloud：`go test ./internal/modules/publish/... ./internal/modules/localagent/... -count=1` | 发布业务及Agent准入通过；管理员四类命令不触达业务写入，云端列表／详情／编辑保留，运营执行通过 | PASS |
| Cloud：`WT_MEDIA_CLOUD_HOME=<Cloud根目录> WT_MEDIA_TEST_LIVE_DB=1 go test ./internal/modules/publish/... -count=1` | 实际创建并清理隔离MySQL测试库；停止／提交、未知结果、核实／补录、重试／放弃、占用、补报和核验截止等现有流转通过；不修改正式业务库 | PASS |
| Agent：`PYTHONPATH=src .venv/bin/python -m unittest discover -s tests -p 'test_publication*.py'` | 113项通过；覆盖SQLite草稿、原现场继续、提交边界、未知结果不重投、本地持久化补报和只读核验；模拟平台响应，不操作真实平台 | PASS |
| Cloud `web/`：`node scripts/test-publication-role-browser.mjs` | 实际加载Cloud与Desktop各自入口，分别走查管理员／运营／高级运营共6组；管理员保留管理入口、关闭发布及直达链接，跨页面无草稿／发布／启动Agent调用；运营与高级运营可进入准备，Desktop读取本机草稿桥，Web使用内存；无页面JS错误和业务写入 | PASS |
| Cloud `web/`：`WT_MEDIA_BROWSER_WIDTH=1440 CHROMIUM_EXECUTABLE=<本机Chrome可执行文件> node scripts/test-publication-visual-browser.mjs` | 1440px桌面宽度62项通过；资源读取失败／占用、输入保留、保存草稿返回、执行与重试取消、核实缺少依据、预览失败恢复、封面选择、详情／筛选及浮层布局均通过；无页面JS错误或业务写入 | PASS |
| Cloud `web/`：`npm run build:cloud -- --outDir <临时目录>`、`npm run build:desktop -- --outDir <临时目录>` | 两端生产构建均通过；只有既有包体大小提示 | PASS |
| Workspace文档治理、Delivery治理、产品计划对齐，以及两仓`git diff --check` | 均通过 | PASS |

角色浏览器验证使用受控HTTP与原生桥响应，直接观察正式Vue的真实DOM和截图；不等于安装版原生执行、真实SQLite桥或真实平台验收。截图、原始日志和临时构建产物不入Git。旧页面脚本额外的390px窄屏分支在既有侧栏折叠／固定操作列处等待失败，未计为通过；本轮完成1440px桌面宽度验收，未扩展窄屏布局整改。

## 业务验收对照

| 验收项 | 可核对的证据 |
| --- | --- |
| 图片／模板、真实AI与双封面 | 沿用[既有真实验收](verification.md)的不同素材全自动闭环及最终安装包复验；本轮未修改这些提供方能力 |
| 续编不创建任务、不占用成片；Desktop重启恢复 | 本轮草稿及创建异常回归；既有安装版SQLite跨重启证据继续有效 |
| 停止、原现场继续、未知核实、补录、重试和放弃 | 本轮真实隔离MySQL及Agent113项模拟流转，原输入／尝试／占用边界保留 |
| 公开作品与统计 | 既有任务11／attempt34自动核实作品4（12052878563859428344）；不把审核中回执计为成功。原记录中的“累计4／今日2”为2026-11-22验证时数值，不作为今天的重新读取结果 |
| 管理员基础Cloud管理与非执行边界 | 本轮前后端用例及6组实际前端走查 |
| 四仓Review、合入与签收 | 2026-11-23本轮只提交审核；2026-11-24已按用户后续授权完成审查修复与四仓main合入，见[合并核对](main-merge-and-verification.md)；整体验收签收仍待完成 |

## 自查结论

已核对角色限制覆盖列表、抽屉、直达链接和服务端命令，同时保留云端管理。复用现有状态、账号归属、提交授权与结果补报规则，未加入新的安全兜底或抽象。当前收尾范围没有新增阻塞项；受控模拟和既有真实业务证据分别列明。其他会话的原型、文件管理及文档未提交改动原样保留，不纳入本轮提交。
