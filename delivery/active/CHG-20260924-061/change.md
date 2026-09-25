# CHG-20260924-061：M4-A 素材库、我的素材与原素材懒加载下载

- Status: IMPLEMENTING
- Level: M
- Milestone: `delivery/milestones/M4-content-production.md`
- Closure anchor: §4「闭环卡 M4-A：素材库与我的素材」
- 日期：2026-09-24
- 决策：`docs/decisions/0017-m4-m5-cloud-owned-content-production.md`
- 产品基线：`docs/product/prd/详细文档/第五章_素材生产.md`
- 工程基线：`docs/engineering/specs/2026-09-24-m4-m5-cloud-content-production.md`
- Current repository: `wt-media-cloud`
- 当前仓库：`wt-media-cloud` 为业务事实、API、Cloud 文件准备和 Web 主仓；`wt-media-agent` 为本地下载执行；`wt-media-desktop` 为本机目录/打开文件能力；`wt-media-workspace` 为治理与 Evidence
- 激活前置：M3 `DONE`；当前 active CHG 与其已批准后继顺序完成或由用户重新排期；任一时刻仍只允许一个 active CHG。2026-09-26 已逐项核验并激活本 CHG。

> 本记录是 M4-A 的唯一 active 执行合同；进度和验证读数只记录在同目录 `checkpoint.md` 与 `evidence/`。

## 1. 独立目标

交付 M4 的第一个可独立验收用户闭环：运营在素材库看到正式 `material` 及真实源视频状态，把素材加入唯一的“我的素材”关系 `material_usage`，按需准备原素材并通过全局下载中心把完整文件落到运营电脑。

```text
source_content
→ material（默认不下载原视频）
→ material_usage
→ file_transfer_task(asset_type=material)
   ├── purpose=compose_input_prepare, execution_scope=cloud
   └── purpose=user_download, execution_scope=local_agent
→ Cloud 对象存储 / 运营电脑本地文件
```

该闭环验证“懒加载而非入库即下载”、Cloud 与本地执行边界、真实传输进度及完整性；不以静态页面、模拟进度或仅有任务记录代替真实文件结果。

## 2. 当前差距

截至本 CHG 建立时：

- Cloud 只有 `materials` 基础表和内容池转素材入口；没有冻结后的源视频状态/对象引用、`material_usage` 或 `file_transfer_task`；
- `/material-library` 仍复用内容池投影，“我的素材”仍是占位页；
- Cloud 尚无对象存储与原素材准备基础能力；
- Local Agent 尚无原素材下载领取、进度回报、原子落盘和 Hash 校验合同；
- 顶部下载中心 Drawer 尚未接入真实任务。

因此本 CHG 必须先补齐正式事实、合同和真实执行，再实现页面；不得反向以参考图字段驱动临时表或前端假状态。

## 3. 范围

### 3.1 Cloud 数据与领域

- 增量扩展 `material`，保存源视频准备投影：`not_downloaded | downloading | ready | failed`、对象存储引用、文件大小、Hash、媒体摘要及最后错误；
- 新增且只新增“我的素材”对象 `material_usage`，按用户和素材保证最多一个有效关系，支持移出与恢复；
- 新增横向任务对象 `file_transfer_task`，至少包含 `asset_type`、`asset_id`、`purpose`、`execution_scope`、五态、进度、速度、预计剩余时间、重试、错误和完整性结果；
- `material`、`material_usage`、`file_transfer_task` 都遵守团队/业务范围隔离、审计字段和明确外键；
- 迁移使用下一个实际可用编号，提供 migration runner 测试；Repository 保留显式 SQL。

### 3.2 Cloud API 与执行

- 素材库列表/详情：来源、游戏、平台、作者、发布时间、视频状态和权限范围；
- “加入我的素材”使用幂等命令，重复/并发提交不产生第二个有效关系；
- “我的素材”列表、移出和恢复；移出不物理删除历史关系；
- 创建、查询、取消、重试原素材传输任务；所有响应继续使用 `errcode / message / data / logid`；
- Cloud 文件准备执行器只处理 `purpose=compose_input_prepare, execution_scope=cloud`：受控获取源文件、隔离临时目录、校验媒体、写对象存储并更新投影；
- 给 Local Agent 的任务领取/续租/进度/结果合同只包含本地传输所需最小信息，并使用短时最小权限下载信息；
- HTTP 请求只创建或查询任务，不同步等待文件传输；HTTP Server 不启动文件 Worker。

### 3.3 Local Agent 与 Desktop

- Local Agent 原子领取分配给当前节点的 `user_download` 任务，写临时文件，校验大小/Hash 后原子改名；
- 支持取消、超时、有限重试、进程重启恢复和失败临时文件清理；
- 本地绝对路径只留在 Desktop / Agent 本机可信存储，不写入 Cloud 正式业务表；
- Desktop 提供目录选择、打开文件/目录和 Sidecar 调用，不保存第二套业务任务状态；
- Agent 合同和实现不得出现 FFmpeg、合成策略、模板或成片生成。

### 3.4 Cloud Web / Desktop WebView

- 按六图中的素材库、我的素材和下载 Drawer 信息架构实现正式数据页面；演示数字不是需求；
- 素材库支持查询、筛选、来源详情、加入我的素材和下载原视频；
- 我的素材支持列表、移出、恢复、下载原视频；“创建合成任务”在本 CHG 内明确显示后续能力，不创建假任务；
- 顶部下载入口展示真实进行中/最近完成任务、进度、速度、剩余时间、取消、重试和打开文件；
- Cloud Web 与 Desktop WebView 复用页面和 Cloud API；仅本机能力走 Desktop / Local Agent。

## 4. 明确不做

- 不实现 `compose_strategy`、`compose_task`、Compose Worker、FFmpeg 或 `composite_output`；
- 不实现 M5 Scheduler、自动生产、批量合成或 Worker Pool 资源控制；
- 不新增 `material_user_relation`、`user_material`、`favorite_material` 或任何 `material_usage` 替代表；
- 不新增 `production_rule`、`compose_pool_item`、通用 Agent 合成任务或第二张下载任务表；
- 不在素材进入素材库时批量下载全部原视频；
- 不把本机路径、长期对象存储凭据或完整签名 URL写入 Cloud 日志/业务表；
- 不让 Desktop / Local Agent 执行视频合成；
- 不用 Mock 文件、前端定时器或硬编码百分比作为真实下载验收证据。

## 5. 实施顺序

### Task 0：激活检查与合同冻结

- 确认无其他 active CHG，并按治理命令完成 061 激活；
- 盘点 Cloud 当前 migration 最大编号、对象存储部署参数、各平台源链接有效期及 Local Agent 节点身份；
- 先在 Cloud 正式 OpenAPI/contract 中冻结素材、`material_usage`、`file_transfer_task` 的 DTO、枚举、错误码和兼容规则；
- 明确 Cloud 准备与本地下载是否串联复用同一已准备对象，禁止同一业务命令创建无界重复任务。

验收：合同与数据对象只有本 ADR 批准的命名；待决外部下载授权已关闭；无凭据写入文档。

### Task 1：迁移、模型与 Repository（测试先行）

- 先写 migration runner、Repository 并发/权限/状态转换失败测试；
- 增量扩展 `material`，创建 `material_usage` 和 `file_transfer_task` 所需表、索引、唯一约束、检查约束及外键；
- 实现列表、详情、幂等加入/恢复、移出、传输任务创建、原子领取、续租、进度和终态写入的显式 SQL；
- 校验重复点击、并发请求、跨团队读取、非法状态回退和已取消任务回报成功均失败。

验收：迁移可从现有库前滚；同一用户/素材最多一个有效关系；同一传输任务同时最多一个执行者；Repository 测试使用 `go-sqlmock` 包装 `*gorm.DB`。

### Task 2：Cloud Service、Handler 与正式 API

- 在业务模块中实现权限、筛选、幂等、状态机、重试/取消规则和审计；
- Handler 只解码/校验并调用包级 Service，Router 只绑定 method/path/function；
- API 列表与详情读回来源、视频状态和传输投影；错误码区分无权限、源不可用、任务冲突、已取消和完整性失败；
- 更新 Cloud contract、客户端封装和 route tests，不改变既有内容池转素材路由。

验收：API 200 后可从独立 GET 与数据库读回事实；越权、重复和非法状态转换有自动测试；内容池现有测试不回归。

### Task 3：Cloud 原素材准备与对象存储

- 在 `internal/infra/client` 实现类型化源文件获取，在 `internal/infra/storage` 实现对象存储；业务模块不得直接创建 `http.Client`；
- 独立 Worker 原子领取 Cloud 范围任务，使用隔离临时目录，校验大小、Hash 和媒体可读性后提交正式对象；
- 准备成功才把 `material.video_status` 投影为 `ready`；下载、校验、上传任一步失败均进入 `failed` 且不保留假对象引用；
- 配置只放 `config` / `config_online` 的规范目录，凭据与连接配置分离；HTTP Server 不启动 Worker。

验收：真实来源文件写入真实测试对象存储；重启、取消、超时、源 404、字节不足、Hash 不符和对象存储失败均有受控证据；入库未触发时无文件下载。

### Task 4：Local Agent 下载执行与 Desktop 本机桥接

- 先更新 Local Agent contract 与合同测试，再实现领取、心跳、断点策略、进度回报、校验、原子落盘和恢复；
- Desktop 只实现目录选择、任务发起所需本机参数、打开文件/目录及 Sidecar 连接；
- 下载目标做路径规范化、磁盘空间检查、同名文件策略和目标目录边界校验；
- 任务取消或失败时不得把 `.part` 文件当作完成文件。

验收：真实文件落到用户选择目录且大小/Hash 一致；Agent 重启和 Desktop 退出场景结果可判定；Cloud 不出现本机绝对路径；Agent 边界扫描无 FFmpeg/compose 执行。

### Task 5：素材库、我的素材与下载中心 UI

- 先写页面/交互测试，再把占位路由替换为真实页面；
- 将当前 `/material-library` 从内容池复用投影调整为正式素材 API，保留“查看来源”跳转；
- 实现“加入我的素材”、我的素材移出/恢复和两端下载入口；
- 实现顶部下载 Drawer 的真实状态、取消/重试和本机完成动作；
- 对等待本机、无 Agent、空间不足、取消中、失败和完整性错误提供明确状态，不展示假完成。

验收：Cloud Web 与 Desktop WebView 使用同一业务组件；三种角色、两个团队和至少两个游戏范围走查正确；参考图六页面导航结构不被破坏。

### Task 6：跨仓验收、提交与交接

- 以一个真实来源执行“转素材后无下载 → 加入我的素材 → 按需准备 → 下载到运营电脑 → Hash 校验”；
- 执行取消、重复点击、跨团队、源失败、对象存储失败、Agent 离线/重启、本地磁盘不足和文件损坏；
- 回归 M2、M3 内容池与转素材；确认未来合成只需复用 `compose_input_prepare`，不重造下载表；
- Cloud、Agent、Desktop、Workspace 分仓独立提交，Evidence 记录版本、提交、输入、期望、实际和 PASS/FAIL；
- 用户签收后只关闭 M4-A，不提前把 M4 或 M5 标为 `DONE`。

验收：本 CHG 验收矩阵全部 PASS、无开放阻断缺陷、各仓工作区只保留进入任务前的无关改动。

## 6. 验收矩阵

| AC | 要求 | 最低证据 |
| --- | --- | --- |
| 061-AC-01 | 新素材默认 `not_downloaded`，转素材不触发文件下载 | 数据库、对象存储空值与网络/Worker 对照 |
| 061-AC-02 | 素材库来源、权限和四态视频状态真实 | API、MySQL、UI 三方对账 |
| 061-AC-03 | `material_usage` 幂等加入、并发去重、移出和恢复正确 | 并发测试、数据库唯一约束、UI 走查 |
| 061-AC-04 | Cloud 原素材准备真实落对象存储并通过完整性校验 | 真实对象、大小/Hash、媒体探针 |
| 061-AC-05 | 原素材用户下载真实落运营电脑 | Local Agent 日志、本地文件、大小/Hash |
| 061-AC-06 | 下载中心进度、速度、剩余时间和终态来自真实任务 | `file_transfer_task`、Agent 回报、UI 对账 |
| 061-AC-07 | 重复命令和进程重启不产生双执行或无界重复任务 | 并发/重启故障注入 |
| 061-AC-08 | 取消、源失败、上传失败、磁盘不足和 Hash 不符无假成功 | 故障注入与临时文件/对象检查 |
| 061-AC-09 | 三角色、团队和游戏范围隔离正确 | 权限矩阵与越权测试 |
| 061-AC-10 | HTTP Server 不启动 Worker、不同步等待传输 | 进程测试与路由时延证据 |
| 061-AC-11 | Cloud 无本机路径/长期签名，Agent 无合成能力 | 数据/日志/合同/代码边界扫描 |
| 061-AC-12 | M2/M3 回归、Cloud Web/Desktop WebView 和真实用户流程通过 | 自动测试摘要、截图、用户签收 |

## 7. 验证命令基线

实际激活时按仓库实时 `AGENTS.md` 补充命令；最低集合：

```bash
# wt-media-cloud
go test ./internal/modules/production/... ./internal/infra/storage/... ./internal/infra/database/migration/...
go test ./...
go vet ./...
(cd web && npm test && npm run build:cloud && npm run build:desktop)

# wt-media-agent
python -m pytest

# wt-media-desktop
cargo test --manifest-path src-tauri/Cargo.toml

# wt-media-workspace
python3 scripts/verify_agent_entry.py
```

还必须执行真实对象存储、真实来源文件、真实 Local Agent 与本地文件系统验收；单元测试、Mock、构建成功或截图不能替代真实传输证据。

## 8. Evidence 与提交边界

激活后在该 CHG 的 `evidence/` 记录：

- 各仓基线和最终 commit、配置模板版本、迁移编号与 Contract 版本；
- 每个 AC 的输入、角色/团队/游戏、期望、实际、PASS/FAIL 与脱敏截图；
- 数据库行、对象存储键/元数据、本地文件大小/Hash 的可关联 ID；
- 正常流程与每类故障注入的 Worker/Agent 日志摘要；
- 独立验证者结论和用户签收。

凭据、Cookie、完整签名 URL、本机用户名和绝对路径不得进入 Evidence。Cloud 提供正式合同后，Agent 与 Desktop 才实现消费者；提供方与消费者分别提交，不跨仓混交。

## 9. Initial planning record

- Completed：M4-A 的独立目标、仓库边界、任务顺序和 12 项验收条件已规划。
- Current：`IMPLEMENTING`；激活后的实时进度见同目录 `checkpoint.md`。
- Next：执行 Task 0，冻结正式合同并验证外部下载授权、对象存储测试环境与跨平台保存目录策略。
- Blockers：上述运行前提必须在其需要真实外部副作用的 Task 前验证；尚无阻止 Task 0 的待决业务选择。
- Verification：本轮只验证治理文档完整性与交叉引用，不代表 M4-A 运行链路已交付。

## 10. Pending Questions

None.
