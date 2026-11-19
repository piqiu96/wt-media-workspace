# CHG102 / CHG103 存储整改实施计划

> 执行方式：沿用本会话串行实施，按 `superpowers:executing-plans` 逐项落实；不另建 CHG、任务状态或第二份实施计划。

**目标：** 完成已确认的 ORM、任务标识、结果关联和初始化整改，并在后续领取及发布流程中接入，保留原有安全行为。

**架构：** Agent 在 bootstrap 统一创建 SQLAlchemy Engine 和 Session 工厂；Storage 通过注入使用，每次操作独立事务。Cloud 仍负责正式业务事实，Desktop 负责把所连接 Cloud 的环境配置传给 Agent。

**技术：** Python >=3.12、SQLAlchemy ORM、现有 SQLite 文件和版本化迁移；不新增通用 Repository、Unit of Work 或工作流框架。

**依据：** [CHG102](change.md)、[发布工程设计](../../../docs/engineering/specs/publishing-management.md) §3.7、§4.5，以及本轮用户确认的 ORM 与 `cloud_env` 设计。

## 范围与 PR 归属

| 顺序 | 单元 | 本轮承载 | 现有 PR |
| --- | --- | --- | --- |
| 1 | CHG102 | ORM、表结构与迁移、任务身份、防重及补报存储、既有下载和配置存储迁移 | Agent #9、Workspace #53 |
| 2 | CHG103 | 领取请求键、执行前检查适配；Desktop 传递 `cloud_env`；核对 Cloud 领取与补报协议 | Agent #10、Desktop #11、Workspace #54；Cloud #45 核对协议 |
| 3 | 后续兼容 | 基础改动传递到 CHG104，适配实际投稿、恢复及结果补报消费者 | Agent #11、Desktop #12、Workspace #55，按实际受影响文件更新 |

CHG103 原有 Cloud 授权、领取、检查和报告业务范围保留；本轮 ORM 整改不要求新增 Cloud API 或业务状态。发现提供方确需变化时，先更新共同定义再实施。

不把 CHG104/105 的平台实现倒灌进 CHG102，也不另开一套替代现有 PR。继续使用用户已允许的串行堆叠方式：102 → 103 → 104。更新分支使用保留历史的方式，不强推；本轮不合并 PR。

## 全局约束

- 业务状态、执行阶段和三个操作入口的业务含义保持不变。重启不能依靠 checkpoint 自动重放可能产生投稿副作用的动作；只补报已经保存的原结果。
- `task_id` 保存 Cloud 原始任务 ID；`task_type`、`cloud_env`、`user_id`、`attempt_id` 独立存列，不再用 `publication:摘要` 充当业务 ID。
- `cloud_env` 取 `dev/test/pre/prod`，表示连接的 Cloud 环境。与应用的 debug/release、运行期 development/production 分开；URL 只用于连接，不推算环境。
- 沿用现有 SQLite 文件路径，不按 `cloud_env` 拆文件。实际 Profile 的未结束现场在同一数据库内跨用户、跨 Cloud 环境互斥。
- 所有新连接统一启用 `synchronous=FULL`、`foreign_keys=ON`，集中处理 WAL 与连接超时；业务方法不再设置 PRAGMA 或执行 `BEGIN IMMEDIATE`。
- 采用 ORM 正常事务，依靠唯一约束、条件更新和受影响行数处理竞争；移除提前写锁后必须用真实 SQLite 并发测试证明防重仍成立。
- Engine/Session 工厂按进程装配，Session 按操作创建；不在线程间共享 Session，不跨网络、浏览器或文件读取持有数据库事务。
- 所有 SQLite 业务读写迁移到 ORM，删除旧业务连接入口。历史升级 DDL 可通过统一 Engine 执行，不保留双写、兼容视图或第二套业务实现。
- 旧库升级不得猜测历史记录所属环境或用户，不得重置结果、报告摘要、序号、待补报标记或提交防重记录。
- 公共默认值、任务类型、阶段和配置枚举进入公共常量文件，调用方导入使用；不顺便改变协议值。

## 初始化和目录

以下路径均以对应仓库为根。

```text
wt-media-agent/
  config/agent.toml                  # 运行期读取的配置
  config_online/agent.toml           # 发布替换源
  src/wt_media_agent/
    runtime/config.py               # 唯一配置读取、校验入口
    runtime/constants.py            # 公共默认值和枚举
    runtime/paths.py                # 保留现有数据目录规则
    storage/database.py             # Engine、Session 工厂、模块内选型、关闭
    storage/dialect.py              # SQLite 连接、冲突写入、条件索引与历史升级
    storage/models.py               # 新增：ORM 表、索引与约束
    storage/migration.py            # 同一 Engine 上的版本化升级
    storage/checkpoint_store.py     # ORM 检查点访问
    storage/publication.py          # 发布防重、原结果及投递记录；CHG103 领取独立类
    storage/save_directory.py       # ORM 读写 agent_metadata
    runner/publication.py           # 既有执行边界和原结果发送协调
    bootstrap/app.py                # 按顺序显式装配，不选择数据库
```

配置沿用“环境变量 > 文件 > 默认值”，凭据仍只来自环境变量。

```toml
[cloud]
cloud_env = "dev"
base_url = "http://127.0.0.1:8188"

[database]
synchronous = "FULL"
timeout_seconds = 5.0
```

开发与发布配置分别明确填写对应 `cloud_env`，环境变量入口为 `WT_MEDIA_CLOUD_ENV`。Desktop 配对传递 Cloud 地址和 `cloud_env`，不能只覆盖其中一个，也不能通过构建模式判断连接目标。

初始化次序：读取配置 → 解析现有数据路径 → 创建数据库资源 → 运行迁移 → 注入各 Storage → 装配业务组件 → 启动循环。退出时先停止循环，再释放数据库资源。模块 import 不连接数据库；迁移命令行入口也复用相同初始化规则。

## 表职责与关联

| 表 | 职责 | 关联和保留规则 |
| --- | --- | --- |
| `task_checkpoint` | 记录某任务已执行到哪一步、固定输入及是否存在未结束现场 | 本地自增主键 `id`；业务 ID 独立存列；发布按 attempt 区分，下载保留跨租约重领续传能力 |
| `task_result` | 原始最终结果及发给 Cloud 的投递记录 | 自增 `id`；`checkpoint_id` 外键且唯一；每个发布 checkpoint 对应 0 或 1 条结果 |
| `agent_metadata` | 下载目录等小配置、尚未确认的领取请求键 | 配置按原职责保存；领取键按 `cloud_env/user_id` 隔离，不另建任务表 |
| `schema_migrations` | 已应用数据库版本 | 保留现有名称与迁移历史 |

一个 Cloud task 可有多个 attempt，因此可有多条 checkpoint 和多条结果；每条结果只能属于一个明确的 checkpoint。所有读取、更新和删除都带完整业务作用域，不能仅凭 `task_id` 跨任务类型查询。

发布输入写入后不可被重复领取覆盖；相同结果保存幂等，不同结果拒绝覆盖。检查点终态更新和结果保存同一事务完成。下载不强行套用发布的结果补报流程。

下载成功确认后删除续传检查点。未核实现场、未完成投递和冲突证据保留。发布结果已确认且现场已结算后可清理冗余载荷，但必须保留阻止重复执行所需的最小标识、输入摘要和原报告依据；不按固定天数直接删除防重记录，不新增清理守护进程。

## 重点核查条件

1. 相同 task_id 来自不同类型、用户或 Cloud 环境时，各自查询、删除和投递均不串数据。
2. 两个线程或进程同时领取同一 attempt 或占用同一实际 Profile，只能有一个获得执行资格。
3. 提交边界或结果落盘后进程突然退出，重开保留原阶段、原报告及防重效果。
4. 现场已人工结算但结果尚未送达，不能因为 checkpoint 结算而从补报扫描中消失。
5. 历史下载或领取记录缺少可靠环境映射时，不能被静默归给当前登录用户，也不能丢弃。

## 任务 1：CHG102 配置与 ORM 装配

文件：Agent `pyproject.toml`、`config/agent.toml`、`config_online/agent.toml`、两份配置 README、`runtime/config.py`、`runtime/constants.py`、`storage/database.py`、`bootstrap/app.py`；按实际依赖补充生命周期关闭调用方。依赖按现有工程方式声明和安装，不手工编辑生成的锁文件。

接口：配置解析产出 `cloud_env` 与数据库策略；`Database` 持有 Engine、Session 工厂及 `close()`；各 Storage 接收同一 `Database`，不各自读取配置或新建 Engine。保留既有数据路径解析入口。

- [x] 实施前获取各相关仓库最新 `origin/main`，在隔离工作树将 main 更新合入现有 CHG 基线；保留用户原工作区改动。先处理前置依赖，再按 102 → 103 → 104 传递，不能把后续分支全量合入前置 PR。
- [x] 先补充配置和数据库测试：非法环境拒绝、debug 连接 prod 保持 prod、两个新连接都应用 FULL/FK、事务失败回滚、不同线程不共用 Session。
- [x] 运行定向测试确认新断言暴露缺口，再实现最小装配；按 Python >=3.12 驱动行为配置正常事务及连接 PRAGMA，不用自定义提前写锁代替。
- [x] 复验 `test_runtime_config.py`、`test_config_shipping.py`、`test_storage_sqlite.py` 和 `test_bootstrap.py`，通过后提交此单元。

## 任务 2：CHG102 表升级与既有消费者切换

文件：Agent `storage/models.py`、`storage/migration.py`、`storage/checkpoint_store.py`、`storage/save_directory.py`、`storage/publication.py`、`storage/sqlite.py`，以及 `runner/transfer.py`、`runner/config.py`、本地状态/健康接口的直接消费者。

接口：所有业务查询使用明确的任务作用域和 ORM Session；结果由 `checkpoint_id` 关联。约束区分发布 attempt 与下载任务，不使用含 NULL 的普通唯一键冒充完整隔离，也不使用覆盖式写入替换不可变输入。

- [x] 先补充旧库夹具、跨类型同号查询、结果外键、升级重复执行与中途失败回滚测试；保留原输入、报告摘要及防重断言。
- [x] 实现追加版本迁移，覆盖空库和现有各版本；能核实的历史发布身份从原快照还原，不能反推的历史下载/领取身份明确报告并保留原数据，在获得可靠映射前不完成破坏性转换。
- [x] 将下载续传、下载目录、检查点、发布日志和本地状态访问整体切换到 ORM，移除旧业务 SQL/连接入口。历史 DDL 保留在迁移层。
- [x] 用真实 SQLite 并发测试证明同 attempt 和跨环境同 Profile 互斥；用触发器或等效数据库故障证明结果写失败时检查点一并回滚。
- [x] 运行 `test_storage_migration.py`、`test_storage_migration_paths.py`、`test_transfer_resume.py`、`test_transfer_runner.py`、`test_publication_execution.py` 及对应目录/状态测试；通过后提交。

## 任务 3：CHG103 领取、准备与 Desktop 环境传递

文件：Agent `storage/publication_claim.py`、`runner/publication_preparation.py`、`clients/publication.py`、`bootstrap/app.py` 及身份构造调用方；Desktop `src-tauri/src/config.rs`、`src-tauri/src/sidecar/mod.rs`、`src-tauri/resources/desktop.production.toml` 和既有开发配置/测试夹具。

接口：领取键按显式 `cloud_env/user_id` 持久化；只有无任务或 attempt 已可靠落盘后才确认领取键。Preparation 使用任务原始 ID 和同一 ORM 日志；Desktop 启动 Sidecar 时成对传递 Cloud 地址和 `WT_MEDIA_CLOUD_ENV`。

- [x] 先补充同一领取请求响应丢失后的重放测试、不同环境同号隔离测试、未确认旧领取键保留测试，以及 Desktop 开发包连接 prod 的环境传递测试。
- [x] 合入已验证的 CHG102 基础提交，再切换领取键 ORM 访问和身份构造；不在 HTTP 前后跨越一个数据库事务，不重新生成结果未知的领取键。
- [x] 核对 Cloud #45 的领取幂等、序号、报告摘要及 report-safe 边界。移除 URL 身份键只改变本地存储身份，不改线上报文摘要算法。
- [x] 复验 Agent `test_publication_preparation.py`、领取/报告客户端与装配测试，以及 Desktop 配置和 Sidecar 测试；通过后提交。

## 任务 4：后续分支适配与补报遗漏回归

文件：在 CHG104 的 Agent `runner/publication_job.py`、`storage/publication.py` 及其身份、恢复调用方；对应 `tests/test_publication_job.py`。实际平台 Publisher 的能力边界沿用已确认设计，不重新组织一套执行框架。

接口：未结束现场扫描负责现场恢复；未确认结果扫描直接由 `task_result` 投递状态驱动，两者不互相充当过滤条件。

- [x] 增加回归：结果保存后断网 → Cloud 人工结算现场 → Agent 重启 → 网络恢复，原结果仍被发现并按 Cloud 既有规则处理，浏览器提交次数保持一次。
- [x] 根据实际 Cloud 回应区分确认、重试和冲突；明确拒绝不能标记成功投递，人工结算也不能伪造上报确认。
- [x] 将 CHG103 基础提交传递到 CHG104，适配消费者并运行发布故障/恢复测试；不把后续代码反向带入 #9 或 #10。

## 任务 5：文档、验证与再次 Review

文件：Workspace `docs/engineering/specs/publishing-management.md`、CHG102/103 各自 `change.md` 和 `evidence/verification.md`，后续兼容修改的证据归对应 CHG。此计划是共用实施清单，状态仍只在各自 `change.md`。

- [x] 在 CHG102 正式设计中回写表职责、关系、身份、初始化和生命周期；在 CHG103 分支更新环境传递与领取边界，不复制一份设计全文。
- [x] 每个运行仓先执行相应定向测试，再执行既有标准回归；检查残留业务 `sqlite3`、散落 PRAGMA、`BEGIN IMMEDIATE` 和只按 task_id 查询的入口。
- [x] 对含 ORM 的最终 Agent 验证打包导入和旧库升级，不以源码测试代替包内依赖验证；使用临时数据，不连接真实账号执行投稿。
- [x] 更新原 PR 描述、验证证据和依赖基线，独立 Review 最终差异；各 PR 分别提供修改内容、实际测试结果及遗留项，不自动合并。

此前的测试数量和 CI 结果均属于整改前提交。本轮实施清单已完成，CHG 保持 VERIFYING，等待用户 Review，未运行的平台或安装包验收不声明完成。


## 2026-11-19 后续确认：存储清理与数据库差异集中

用户已确认执行。本段承接原清单，不建立第二套任务状态。数据库类型常量只在 `storage/database.py` 内声明，默认 SQLite；不新增 URL、类型配置或环境变量。`app.py` 仅装配并注入 Database，不判断数据库类型。

### 任务 6：CHG102 数据库适配与旧代码清理

- [x] 新增小型 `storage/dialect.py`，集中 SQLite 连接、冲突写入、条件唯一索引及争锁识别；普通约束由模型声明，建表时创建，写入仅引用已有约束规则。
- [x] Store 使用普通 ORM 与统一冲突写入方法，不直接导入 SQLite 方言，不重复声明冲突列/条件；适配调用复用 Session，不自行提交。
- [x] 保留迁移历史、旧库映射与失败回滚；迁移入口按 Database 的适配调用对应升级；普通时间默认值使用统一时间函数。
- [x] 删除 OfflineResult 和 records.py，TaskCheckpoint 移入 checkpoint_store.py；待投递数量直接统计；删除无调用方法、未用属性、旧导出和过期注释，收口跨模块常量。
- [x] 发布补报发送协调放入既有 runner/publication.py；Journal 只查询原 packet 和记录确认；校验原 hash 与作用域，重试不包含 HTTP 或浏览器。
- [x] 先验证新接口缺失，再以真实 SQLite 复验约束、隔离、事务、重启与原结果；完成 Agent 标准回归并提交。

### 任务 7：CHG103 领取组件合并

- [x] 合入 CHG102；PublicationClaimStore 并入 storage/publication.py，保留独立类；删除 publication_claim.py，更新装配、准备和测试。
- [x] 领取键创建引用统一插入方法，保留原请求值；准备补报使用现有 Runner 协调；定向及标准回归通过。

### 任务 8：CHG104 恢复消费者衔接

- [x] 合入 CHG103，恢复逻辑直接确认原结果，不遍历全量 pending 来伪造发送回调；保持未投递结果可见、未知现场不重入。
- [x] 保留同一 attempt/hash 校验、一次点击、人工结算与未投递分离；运行完整回归及冻结 Sidecar 新旧库启动。

### 任务 9：文档、最终 Review 与原 PR 更新

- [ ] 正式设计及各 CHG evidence 同步；文档治理及适用 Workspace 回归通过。
- [ ] 对本轮差异完成独立最终 Review，修正阻塞项并回归；更新 Agent #9/#10/#11 与 Workspace #53/#54/#55，不合并。

范围确认：本轮不改变业务状态、表职责、原结果内容或数据路径，不新增运行时对 Workspace 的依赖。Cloud/Desktop 无本轮新增修改。未来数据库接入须新增适配和迁移、验证相同约束，不声称只改类型即可搬迁历史数据。
