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

已改用系统内约 13.7 MB 的真实成片和 85.8 KB 封面，文件已通过正式存储与前置资源校验，未修改 nginx 或业务文件上限。百家号原账号页面出现安全验证，用户完成前无法继续核对稿件；任务 3 保持待核实，不确认未发布、不重试、不公开投稿。平台安全验证截图仅保留本机，未复制账号主页和无关运营数据进仓库。

后续 M6-B 继续实际观察百度上传表单、实现适配和独立执行循环、通过持久化许可后自动最终提交并读取真实回执；M6-C 再完成公开作品核实、补录、人工继续、安全终止/放弃及关联作品。尚未验证的范围不计入本单元通过。

## 聚合检查与 Review 顺序

首次聚合中的既有磁盘空闲量测试，两次实时读数相差 4096 字节；单独保留原断言复测通过。使用 `RUST_TEST_THREADS=1` 减少测试间并发写盘后全部 Rust 检查通过，未修改或降低断言。另一次聚合拒绝早于最终源码提交的合成调度构建；服务实际存活，按既有环境入口重建、应用迁移 105 并重启全部本地服务后，最终正式聚合退出 0。

前置 CHG-101/102/103 PR 链先合并；本单元 [Cloud#46](https://github.com/piqiu96/wt-media-cloud/pull/46) → [Agent#11](https://github.com/piqiu96/wt-media-agent/pull/11) → [Desktop#12](https://github.com/piqiu96/wt-media-desktop/pull/12) → 本 Workspace PR。Cloud 含迁移 105；各 PR 以对应 CHG-103 实际远端分支 `chg/CHG-20261118-103` 为 base，当前 head 为 `codex/CHG-20261118-104`。保持独立差异，未合并。

当前堆叠目标不匹配既有 main-only workflow，尚无本单元远端 CI；以上为实际本地标准及正式聚合结果，不把无检查称为 CI 通过。原生视觉走查与真实平台投稿仍未验证，不标记 CHG 或 Milestone DONE。
