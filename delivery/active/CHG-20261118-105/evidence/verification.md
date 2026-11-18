# Playwright 发布器与执行接入验证

2026-11-18，CHG-105 相对 `codex/CHG-20261118-104` 的增量。实现 Python Playwright `BrowserSession`、`Publisher` 协议、`BaiduPublisher` 和 Local/Sidecar 串行执行；没有修改 Cloud、Desktop 业务源码、Contract 或数据库。真实投稿验收尚未通过，CHG 为 `VERIFYING`，M6 为 `IN_PROGRESS`。

验证的 Agent 代码提交：`bf8735f7ee4a36d84df5f4dd018945bd54944563`；Cloud `55fa6fc8753d26b7554793b7275da5ffaa78d48e`、Desktop `577146e797ec7ae3950ed2cf6f14967f0f3bb5bf` 均保持 CHG-104。安装包在上述 Agent 源码修改完成后重建，未将旧包作为本轮产物。

## 自动检查

| 检查与复现入口 | 预期及实际结果 |
| --- | --- |
| Workspace `python3 scripts/wt.py chg verify CHG-20261118-105` | PASS，退出 0；Workspace 211 项、Agent 739 项，本地服务、开发入口、登录、DMG 新鲜度及配置检查通过。不是全仓 Cloud/桌面 Rust 重测或真实投稿验收 |
| Agent `bash scripts/test.sh`（聚合入口调用） | PASS 739 项，包含 33 项架构约束；保留网络隔离、SQLite、防重及子进程恢复检查 |
| Agent `PYTHONPATH=src .venv/bin/python -m unittest discover -s tests/browser -p 'test_*.py'` | PASS 7 项，实际独立 Chrome 页面；正文、声明、两个封面、停止/被改写内容拒绝、上传未完成拒绝、图片解码失败、一次最终请求及精确回执解析。全部外网请求被拦截，回执为测试夹具，不能证明百家号投稿成功 |
| Agent `bash scripts/build.sh` | PASS，wheel 和 sdist 构建完成；Local extra 固定 Playwright 1.58.0，不安装另一套 Chromium |
| Workspace `python3 scripts/dev/local_env.py up --force-restart` | PASS，重建并启动当前本地 Cloud、Agent、Worker、调度及共用开发前端；测试未使无 Token 的 Agent 领取任务 |
| Workspace `python3 scripts/dev/local_env.py build-dmg` | PASS，重建 macOS arm64 DMG，内含当前 Sidecar；Windows、Intel Mac 和安装后完整发布流程未验证 |
| Agent `.venv/bin/python scripts/verify/smoke_frozen_sidecar.py --binary <实际 app 内 Sidecar>` | PASS，冻结进程启动及带鉴权 healthz 通过 |
| Agent `PYTHONPATH=src .venv/bin/python scripts/verify/smoke_frozen_browser.py --binary <实际 app 内 Sidecar>` | PASS，从安装产物提取的 368 个驱动文件可直接启动，版本为 Playwright 1.58.0；不依赖开发机 Node |

首次包含包内驱动的检查失败：Node 在 hardened runtime 下不能分配 JIT 代码内存。复现后，仅增加 `com.apple.security.cs.allow-jit` 签名权限，保留 hardened runtime；精确签名参数及权限测试先失败、修复后通过，重新构建的同一探针通过。没有增加调试、跳过库校验等权限。

一次标准测试与 PyInstaller 重签名构建同时运行时，7 项子进程检查遭 SIGKILL；没有降低断言。构建结束后串行运行上述正式聚合，739 项全部通过。最终结果不使用那次失败日志冒充通过。

## 大文件与包内驱动

实际 BitBrowser 130.0.6723.70，使用启动返回的本机 CDP 地址及 `is_local=True`。测试生成有效 H.264 MP4，再追加合法 MP4 `free` box 至 67,108,864 字节；`ffprobe` 读回 1 秒视频。只在独立、全网络拦截的文件输入页选择文件，浏览器读取的完整文件 SHA-256 与本机一致。没有把文件上传百家号，也没有压缩至 50 MiB 以下替代此项检查。

随后使用实际 app 内提取的 Playwright 驱动，连接同一 BitBrowser，在独立隔离页读取相同大小文件，通过：`bundled_browser_connection=true`、`file_bytes=67108864`、`platform_submit=false`。复现命令为 Agent `PYTHONPATH=src .venv/bin/python scripts/verify/smoke_frozen_browser.py --binary <实际 app 内 Sidecar> --endpoint <本次启动返回地址> --file <有效大于 50 MiB 的测试视频>`。该检查只证明包内驱动、连接和路径传文件，不等于冻结 Python 发布循环、平台转码或最终投稿验收通过。

## 实际页面和原任务

用户完成百家号安全验证后，实读账号 UID 与任务快照一致；逐页核对全部 103 篇稿件，没有对应标题，草稿 0 篇。平台列表实际响应为 `errno=0`，未使用首屏加载中的空列表作依据。但是重新打开视频编辑器后，仍恢复上次上传的视频及部分文字；页面未提供已经核实可安全放弃的操作。因此不能将原任务判为失败、释放占用或重新入队，也未删除浏览器缓存来绕过核实。

Cloud 任务 3 当前 attempt 4、status `uncertain`、revision 15、attempt_count 3。本轮未执行核实结论写入、安全重试、再次上传或最终提交；不以无同名作品、空草稿或测试回执证明未发布。

Cloud 和 Desktop 开发入口分别运行现有 `web/scripts/test-publication-recovery-browser.mjs`：实际打开任务详情、核实弹窗，取消后任务不变，缺少依据不能保存，原结果保留；页面错误 0、无横向溢出。[脱敏读回](readback.json)。沿用 Cloud `web/example/proto/publishing-design/PublishingTaskPage.vue`、`TaskDetail.vue`、`TaskActionDialog.vue` 和公共组件，没有另行设计页面。该项是浏览器开发入口走查，不是原生安装包视觉验收。

复现页面检查时，使用当前启动输出提供 `WT_MEDIA_BROWSER_BASE_URL`、本机授权会话 `WT_MEDIA_BROWSER_STATE`、输出目录 `WT_MEDIA_BROWSER_EVIDENCE` 及 `WT_MEDIA_BROWSER_TASK_ID=3`；不设置 resolve/retry 写入选项。账号主页、Cookie、Token、CDP 地址、完整响应和原始运营截图只留本机，不进证据库。

## 未通过的验收与 Review 顺序

- 未验证真实空白编辑器完整填写、平台实际视频处理完成、最终自动提交和本次可信稿件回执。旧编辑现场未安全处置前不执行新尝试；人工继续、公开作品核实与补录属于后续 M6-C。
- 未验证超过 50 MiB 文件在百家号完成上传和处理，也未验证安装包内完整发布流程；上述本机文件与驱动检查不能替代它们。
- CHG-101～104 前置 PR 链先合并；随后 [Agent #12](https://github.com/piqiu96/wt-media-agent/pull/12) → Workspace CHG-105。各自以 `codex/CHG-20261118-104` 为 base，保留独立差异，不自动合并。
- 当前堆叠 base 不触发既有 main-only workflow；以上为实际本地验证，不宣称远端 CI 通过。
