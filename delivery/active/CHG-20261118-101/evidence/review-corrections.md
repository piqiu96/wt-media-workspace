# PR #44 审查修改验证

日期：2026-11-19。Cloud 从原提交 `e4780477d2771f641d9e32d9e94f2f85dc1e446c` 追加修复 `3a7067c61ce8b1b98df3e15944f54a1a267dd070`，继续使用 [Cloud #44](https://github.com/piqiu96/wt-media-cloud/pull/44) 原分支 `chg/CHG-20261118-101`；配套文档更新在 [Workspace #52](https://github.com/piqiu96/wt-media-workspace/pull/52)。未合并 PR。

## 修改结果

- 后端模块改为 `internal/modules/publish`，接口统一 `/api/v1/publication`，前端使用 `createPublicationClient`。契约改为 `publication.openapi.yaml` 与 `publish.yaml`，提供方 API 和错误码版本为 `2026.11.19.1`；数据库业务表名保留。
- 文件接口返回结构体命名为 `FileView`，与数据库 `File` 区分；新增 `DeletedAt` 放在原有字段末尾。
- 发布状态由模块 `model.Status` 及常量维护；业务错误码在 `internal/shared/errcode/publish.go` 集中维护，数字不变，HTTP 状态使用框架常量。
- 删除只检查明确的文件 ID 引用；当前为正式任务的 `cover_file_id`。移除生产 JSON 的 URL 扫描及对应写入锁。本站与外部链接采用相同规则，资源读取不到时由生产明确报错。
- `deleted_at` 替换 `delete_state`。物理删除失败可重试，保留首次删除时间；记录仍可在恢复列表查看，但不能预览、下载或新增引用。
- 去掉百度准备配置、响应字段及页面隐藏逻辑。创建任务仍是 pending、无授权、零次执行。

## 本轮实际验证

| 范围 | 结果 |
| --- | --- |
| Go 相关包 | publish、files、production、bootstrap、config、shared/errcode 全部通过 |
| 修改前后回归 | 接口命名、默认百度创建、删除时间三项先失败后通过；图片选择器删除记录渲染先因旧字段判断失败，修正后通过 |
| 隔离 MySQL | 8 项通过；完整 106 个迁移的空库及重放、旧删除标记升级、文件 ID 引用/删除竞争、重试时间保持、URL 资源不阻止删除、权限分页、修订与审计回滚、新上传文件引用均通过 |
| 共用前端 | 5 个测试文件、14 项通过，包括删除记录的图片选择器渲染 |
| Cloud / Desktop 构建 | 两端通过；保留已有包体积提示 |
| Workspace 文档同步 | 文档治理、交付治理、产品与主计划一致性、单仓配置校验通过；API/错误码映射与本轮 Cloud 提供方实际版本逐项一致 |
| 最终代码复查 | 修复选择器遗漏的旧字段判断；未发现其他重要问题；差异空白检查通过 |

本轮未重复浏览器或原生安装包页面走查，没有修改生产数据库或正式任务，没有平台投稿。前一轮实际页面证据仅说明当时版本，不冒充本轮验证。

## 迁移与回退

新增 `20261119_106_operations_file_deleted_at.sql`，不改历史迁移：先加可空 DATETIME(6)，将旧 deleting 行的 updated_at 迁入 deleted_at，再删除旧约束和列。旧结构未记录单独删除开始时间，因此迁移值只承接删除事实。

应先执行迁移，再启动匹配的新服务和前端。旧服务依赖 delete_state，不能与迁移后的结构混跑。若回退代码，需先按 deleted_at 是否为空恢复旧列及约束，不能将已开始删除的文件恢复为可用；在回退核验完成前保留删除时间。

## 后续分支依赖

尚未合并的执行分支需要同步 publish 包、错误码契约路径及文件删除时间；任务 API 按用户要求统一为单数 `/publication`，对应调用方在其集成时同步。Desktop 消费锁也需在对应集成中推进。这里只同步 #44 和 #52，不把后续执行代码并入 M6-A。提供方契约位于 Cloud，不在 Workspace 复制第二套定义。

CHG 保持 VERIFYING；M6 尚未完成。

## 命名补充复核（2026-11-19）

Cloud 提交 `b62d706` 将新增字段移到原有字段末尾，`788ab6b` 将文件响应类型改为 `FileView`，并按用户要求将任务接口统一为单数 `/api/v1/publication`。后端模块仍使用 `publish`；前端客户端为 `createPublicationClient`，API 契约为 `publication.openapi.yaml`。

补充验证：files、publish、bootstrap、shared/errcode 相关 Go 包通过；共用前端 4 个测试文件、11 项通过；Cloud 和 Desktop 构建通过。文档治理、交付治理、产品与主计划一致性、差异空白检查通过。保留此前 8 项隔离数据库与 14 项前端验证记录；本次命名调整没有重复数据库和浏览器走查。
