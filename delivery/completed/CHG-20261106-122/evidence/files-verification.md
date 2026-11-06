# 文件管理验证事实

- Cloud 提交：18b05fc（API）、3f2861b（后端）、75f84dd（共用页面）。独立只读 Review 检查权限、资源令牌、上传失败、删除和前端 multipart；发现错误容器可冒充视频扩展名，已校验 ffprobe format 并加表格测试，定向 PASS。
- `go test ./...`：PASS（完整最终结果 `/tmp/wt-media-chg122-go-final.txt`）。
- 前端全套：996 tests / 133 files PASS；`build:cloud`、`build:desktop` PASS。路由新增使旧计数断言变化，已按实际路由更新。
- `python3 scripts/dev/local_env.py up --force-restart`：Cloud、Worker、Compose Worker、Scheduler、Agent 和两套开发前端 readiness PASS。DB migration 098 实际应用，累计100项。
- 真实 API 验证：生成 PNG/MP4 上传 wt-media，稳定资源地址匿名读回与本地 SHA256 一致，附件下载读回一致；运营本人/同团队他人、高级运营团队范围和跨团队、管理员范围均按规则；越权改名/删除404；团队内改名保持资源令牌；类型筛选、缺失/非法名称拒绝；删除后资源URL404。临时用户、团队及其会话/审计依赖定向清理完成，未留测试数据。
- 准备好的三角洲开头引导实际上传为文件ID3，3,214,374 bytes，SHA256与原视频一致；页面显示名称、视频类型、大小及预览/下载/复制/改名/删除操作。该文件保留供后续合成闭环使用。
- 浏览器：上传空表单显示“请选择文件并填写文件名”。自动选择本地文件需要浏览器扩展的 file URL 权限，本次未扩大权限；上传由真实 API 验证，浏览器确认正式结果。
- 边界：此 CHG 不声称完成打包 Desktop 原生业务验收；文件链接按已有新窗口机制交系统浏览器，素材/成片仍使用原下载中心；完整组合验收归 CHG125。

- `wt.py chg verify CHG-20261106-122`：190项Workspace测试及Cloud模块测试PASS；环境门禁首次调度器构建早于最终提交，已重建，复核Cloud/Agent/Worker/Compose Worker/Scheduler/BitBrowser全PASS。该通用门禁继续报打包Desktop assets早于新增前端提交；本CHG两套前端源码构建已PASS，打包DMG重建与原生完整验收统一在CHG125执行，未以旧包宣称通过。
- docs、Delivery、Product/Master、config、AI workspace校验PASS；状态改为VERIFYING后同步Ledger，消除首次状态不一致。

- Cloud PR34 CI verify PASS（2m58s），已merge并fast-forward本地main：2043fe1933061938dd857d210ec44f24f60af9be。Workspace独立Review指出里程碑残留旧迁移目标，已同步改为最新删除决定。
