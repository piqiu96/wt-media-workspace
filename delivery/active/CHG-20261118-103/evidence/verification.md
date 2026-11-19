# 所属用户领取与实际准备验证

2026-11-18。Cloud `966cd3a4de2d72b3dac7dda94a0d7daa75560537`，Agent `47e4d907cf7d17889f910090d9fa54abad6a0595`，Desktop `5cd5461243f1be90b4ea84e8ccacba188674eaed`。本单元没有百度上传、最终点击或自动投稿循环，不代表 M6 完成。

| 检查与复现入口 | 实际结果 |
| --- | --- |
| Cloud `bash scripts/test.sh` | PASS：完整 Go 回归、136 个前端测试文件共 1006 项、12 项控制入口检查。后续资源防护及原结果保存修正再次定向回归通过 |
| Cloud `WT_MEDIA_CLOUD_HOME="$PWD" WT_MEDIA_TEST_LIVE_DB=1 go test ./internal/modules/publishing/... -count=1` | PASS：15 项隔离 MySQL 用例（7 项执行与 8 项任务/文件基础回归），包括所属用户、并发上限、未知现场、UID/Profile 互斥、原请求键、提交许可丢失、原结果重复与冲突、晚到报告；不连接业务数据库伪造结果 |
| 空库迁移和重复启动 | PASS：106 项首次应用，重复 0 项；新增 104 的约束与索引生效 |
| 契约与哈希 | PASS：6 个用户接口、4 个 Agent 接口的认证及输入检查；Python 生成的 3 组原结果哈希向量与 Go 一致，含中文、特殊字符及大序号 |
| Agent `bash scripts/test.sh` | PASS：705 项。实际 SQLite 请求键并发、丢失响应重放、重启拒绝再次入场、实读 UID/文件不匹配、结果与敏感地址拒绝测试；既有架构边界断言保留 |
| Desktop `bash scripts/test.sh` | PASS：538 项，6 项按既有规则忽略；控制入口 12 项、版本记录 20 项通过 |
| 两端构建与安装包 | PASS：Cloud/共用 Desktop 前端构建；按以上三个提交重建 macOS DMG，组件版本与摘要核对通过。保留既有较大前端包提示；未据此声称原生页面走查通过 |
| Workspace / 官方聚合 | PASS：211 项；`WT_MEDIA_CLOUD_CONFIG_PATH=<私有测试配置目录> python3 scripts/wt.py chg verify CHG-20261118-103` 退出 0，包含各仓标准检查、本地服务、Worker、登录、DMG 新鲜度及配置核验 |

## 实际页面与本机验证

通过共用正式任务页操作真实任务 1（账号 9，所属用户 3）：取消执行确认后任务完整读回不变；再次明确确认后授权并排队，尝试仍为 0；重复旧版本授权返回 409。截图 [确认](cloud-confirmation.png)。正式页面沿用已验收 Cloud `web/example/proto/publishing-design/TaskDetail.vue`、`PublishingTaskPage.vue` 与公共前端规范，没有另行设计流程。

所属用户的有效 Desktop 会话换取 Agent Token 后领取任务 1 / attempt 1，先持久化本机记录，再实际下载 13,603,237 字节成片与 85,779 字节封面并核对摘要，打开指定 BitBrowser Profile，实读百度 UID 与冻结输入一致，Cloud 读回 ready。没有上传文件或点击平台提交。

首次关闭调用返回后浏览器调试入口仍存活，验证如实失败；没有据此报告现场已关闭。再次关闭并核对端口列表及原调试入口拒绝连接后，按本机原记录补报安全未提交失败。期间失联曾进入 uncertain，恢复未重新打开或准备浏览器；最终任务 failed，错误 `PREPARATION_ONLY_NOT_SUBMITTED`，原结果与摘要保留，现场明确结算。原结果重复补报被确认而不产生新尝试。替换会话后旧 Token 领取返回 401 / `AUTH_DESKTOP_REPLACED`，原 attempt 的结果仍可补报。安全读回见 [JSON](preparation-readback.json)，不含凭据、Cookie 或临时下载地址。

实际 Cloud 1440 与 Desktop 开发页 1280 打开相同任务并刷新尝试记录，显示失败及原因，无横向溢出或页面脚本错误：[Cloud](cloud-attempt-history.png)、[Desktop](desktop-attempt-history.png)。浏览器脚本位于 Cloud `web/scripts/test-publication-execution-browser.mjs`，从环境变量读取当前服务地址和登录态；`AUTHORIZE_TASK=1` 只对尚未授权、已明确允许测试的任务使用，普通回归不重复授权已执行任务。任务 3 仅取消确认，保持 pending / revision 3 / attempt 0，供下一单元真实投稿。

## CI 整改

Desktop 首次 GitHub 检查（run 44198492339）失败：干净 macOS 的测试程序位于 cargo deps，Tauri 无法找到包资源目录。定位到 `Location::of` 强制读取资源目录；仅对未打包调试程序使用实际 Sidecar 所在目录，正式包缺目录仍拒绝。新增「开发路径可用／正式包缺目录拒绝」两项测试，完整 538 项及脚本套件通过，原断言未降低。修复后 GitHub CI PASS（run 44199617144），最新安装包的官方聚合验证再次退出 0。

Cloud/Agent 当前堆叠 PR 的目标是功能分支，现有 workflow 只对 main 运行，暂未触发远端检查；以上本地标准与专项测试保留，不将“无检查”描述为远端通过。

## PR 与边界

前置 [Cloud#44](https://github.com/piqiu96/wt-media-cloud/pull/44) → [Workspace#52](https://github.com/piqiu96/wt-media-workspace/pull/52) → [Agent#9](https://github.com/piqiu96/wt-media-agent/pull/9) → [Workspace#53](https://github.com/piqiu96/wt-media-workspace/pull/53)。本单元按 [Cloud#45](https://github.com/piqiu96/wt-media-cloud/pull/45) → [Agent#10](https://github.com/piqiu96/wt-media-agent/pull/10) → [Desktop#11](https://github.com/piqiu96/wt-media-desktop/pull/11) → 本 Workspace PR 审查及合并，不自动合并。

仅按用户本轮授权临时串行堆叠；没有改写 start 的前置合并限制或项目治理规则。代码库与线上配置默认关闭执行开关，真实准备使用私有本地覆盖配置。真实百度上传、最终提交、公开作品核实及安全重试尚待后续 M6 单元；原生安装包页面走查未验证，不将开发浏览器走查替代原生验收。


## 2026-11-19 ORM 与环境参数整改

本轮 Agent 基于 CHG102 `787ae55`，最终适配提交 `e08e3bf`；Desktop 配置提交 `b4a649b`。领取键只存 `publication.claim.<cloud_env>.<user_id>`，原请求值在响应未知时保留；并发领取使用 ORM 唯一键，不重新生成请求绕过未知结果。Preparation 和补报使用同一显式环境标签，Cloud 地址仅供通信；输入、序号与报告哈希算法不变。

- Agent 最终完整回归 713 项通过（`/private/tmp/chg103-final-full.log`）；包含真实 SQLite 并发请求键、旧领取键映射保留、跨环境隔离、准备失败及快照写入竞争回归。
- Desktop 标准回归通过：Rust 540 项通过、6 项依既有规则忽略；控制入口 12 项、版本记录 20 项通过（`/private/tmp/chg103-desktop-green2.log`）。新增 debug 连接 prod、非法标签拒绝及 Cloud 地址/环境成对注入检查。
- 核对 Cloud #45 的领取幂等、原报告摘要与 report-safe 边界；本轮不修改 Cloud，也不改变线上状态或重放平台动作。
- Agent 后续实际 Sidecar 打包与旧库升级证据归 CHG104。本轮不复用此前 DMG/原生页面/真实准备证据证明新版本通过，未进行真实投稿。PR 保持未合并。

当前隔离 Workspace 标准回归 207 项、18 项按既有条件跳过（`/private/tmp/chg103-workspace-full.log`）；文档治理、Delivery 与产品路线校验通过。跳过项依赖缺席的运行仓同级目录或专项条件，不将历史 211 项视作本轮数量。
