# CHG093 引导视频合成验证（2026-10-14）

| 动作 | 预期 | 实际 | 结果 |
| --- | --- | --- | --- |
| `go test ./internal/modules/production/service ./internal/modules/production/compose ./internal/modules/production/executor` | 策略快照、下载边界、真实 FFmpeg 插入与画中画回归通过 | 三个包通过 | PASS |
| `WT_MEDIA_LIVE_GUIDE=1 go test ./internal/modules/production/service -run TestLiveGuideDownloadComposeAndStorageReadback -count=1 -v` | HTTPS 地址下载、合成、对象存储上传与哈希读回 | 真实对象存储和 FFmpeg 测试通过 | PASS |
| 本地 API、Worker 升级后执行 `cmd/compose-template-publish` | 执行器先就绪，模板后发布 | `basic_cut` v1 id 6、`guide_insert` v1 id 8、`guide_pip` v1 id 9 均处于 active | PASS |
| 环境变量启用真实任务验证，运行 `TestLiveGuideDownloadComposeAndStorageReadback` | 任务成功、成片可查询、预览可读 | 素材 161 → 任务 36 `success` → 成片 13，68074 字节；“我的成片”查询包含该成片；预览 Range GET 返回 206 | PASS |
| 同一验证先使用素材 175 | 源对象缺失时不得产生成功成片 | 任务 35 `failed/storage_error`，无成片；检查发现素材库旧记录对应对象已不存在 | PASS |
| Cloud/Desktop Web 构建、29 个合成 Web 测试、`go test ./...`、Contract YAML 解析 | 旧模板和页面回归通过 | 均通过；构建仅有已有的 Vite 分块体积提示 | PASS |

Cloud 实施提交：`7beb3dd`；T-05 验证代码提交见后续提交记录。最终 M4/M5 视觉与人工签收按里程碑统一进行。
