# CHG117 验证

2026-11-05，真实 Cloud、Worker、MySQL 和对象存储；本记录是机器检查，不代替用户人工签收。

- 全部 `internal/modules/...` 与 `internal/jobs/...` Go 测试通过，包含真实 FFmpeg 输出探测。独立后端／合同审查后修复 source 请求必须明确 `remake_confirmed:true` 的遗漏，并补省略／false 回归；已知文件名在分页保持事实。
- `WT_MEDIA_CLOUD_HOME="$PWD" WT_MEDIA_TEST_LIVE_DB=1 go test ./internal/modules/production/repository -run 'TestLive(ManualSource|OutputPagination)' -count=1` 通过：原组单份、原版本／参数、幂等重放优先、固定参数／归属拒绝、跨历史类目同素材聚合、分页总数／授权对象集合。
- `WT_MEDIA_CLOUD_HOME="$PWD" WT_MEDIA_TEST_LIVE_DB=1 go test ./internal/modules/filetransfer/repository -run Category -count=1` 通过：原 043／044 列结构到 093 改名保持 NULL、空值、已存名称、微秒发布时间及所有行；迁移后可写入新传输记录。
- 提供方 OpenAPI 3.1 校验、四份 YAML 唯一键／引用检查通过，共 36 个方法路径。退役 archive POST；新增素材聚合 GET。输出及创建请求 wire 测试与提供方 Schema 对齐。
- 开发库已执行 092／093，当前共 95 个迁移；无历史成片名称／文件名的猜补。统一开发入口从最新源码重启所有服务，健康检查通过。
- 页面真实再次制作：源成片 82 → 批次 41／任务 671 → 成片 104，原组一份，参数 start=1/end=4；当前策略仍为 start=1/end=5。打开或取消无写入，确认先加入素材关系，再创建任务。实际成片 3 秒、640×360、53707 字节，视频访问核验成功。
- 对象丢失禁止访问／下载但不改原成功任务；存储故障返回 503，不伪装为空或不可用。原素材仍可获取时，成片对象丢失不阻止再次制作。
- `git diff --check` 通过。共享页面回归、Cloud／Desktop 构建及截图见 `ui-verification.md`。

本轮真实页面和对象已验证；本机完整下载及原生 Desktop 交接、三角色与全量容量／失败恢复走查在后续 CHG118 收口，不把浏览器演示或排队受理记为已下载。
