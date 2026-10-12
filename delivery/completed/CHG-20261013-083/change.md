# CHG-20261013-083：M4-C5 成片执行（任务领取、FFmpeg 执行与 composite_output）

- Status: DONE
- Level: L
- Milestone: `delivery/milestones/M4-content-production.md`
- Closure anchor: §3.1 M4-C5「成片执行」；验收矩阵 M4-AC-05/06/07 的执行侧
- Product: `docs/product/prd/详细文档/第五章_素材生产.md` §5.4.4、§5.4.5、§5.6
- Engineering: `docs/engineering/specs/2026-09-24-m4-m5-cloud-content-production.md` §3.5、§4.3、§4.4、§5、§6、§10
- Decision: `docs/decisions/0021-compose-four-layer-model.md`
- Affected repositories: `wt-media-cloud`
- Current repository: `wt-media-cloud`
- Activation: CHG-20261013-082（M4-C3 任务创建与排队）已归档；用户指示 M4 剩余 CHG 连续执行、不等待单项验收，2026-10-14 晨统一验收。按里程碑顺序进入 M4-C5。

## 1. 独立结果

云端 Worker 领取 pending 的 `compose_task`，确认源视频就绪（未就绪时经 `file_transfer_task` 的 `compose_input_prepare` 边界准备并等待），按任务不可变快照所绑定的模板版本执行真实 FFmpeg，输出经探针校验、对象存储临时键→校验→正式键提交后，才在数据库事务内创建 `composite_output` 并把任务置 `success`。取消（含 running 的受控终止）、超时、失败重试与 Worker 重启恢复均不产生假成片、不重复执行。

## 2. 范围

- 迁移新建 `composite_output`（工程规格 §3.5：来源素材/usage/任务/快照引用、对象键、大小、媒体信息、Hash、生成时间、发布投影 `pending_publish`）。
- 领取与租约：单条条件 UPDATE 原子领取 `pending → running`（worker_id、lease_expires_at、heartbeat_at）；heartbeat 周期续租；`attempt_count`/`max_attempts` 记账。
- 输入就绪门：`material.video_status != ready` 时创建/等待 `compose_input_prepare`（cloud scope）传输任务，观测到成功与 ready 投影后才进入 FFmpeg；不在领取栈内直接下载。
- 执行：复用 M4-C4 的 `compose.Runner`/`Workspace`/`Lock`/执行器注册表；执行时只读任务快照（`template_code`/`template_version`/`config_snapshot`），不读最新策略；FFprobe 输入/输出校验；独立临时目录。
- 提交：上传临时键 → 校验大小/SHA256 → 正式键 + `composite_output` + 任务 `success` 同一数据库事务；进度 stage/progress 按阶段边界推进。
- 取消：pending 直接 cancelled（已有）；running 先写取消请求，Worker 受控终止 FFmpeg、处置临时文件后才确认 cancelled；超时走同一终止流程。
- 重试与恢复：临时性错误（网络/对象存储抖动、Worker 崩溃、租约过期）在上限内退避重排；业务失败（输入缺失、参数非法、编码器不支持）不自动重试；恢复扫描只处理租约过期的 running，外部状态不明时停止自动重试并记录人工处置原因。
- 错误合同：`compose_task_not_cancellable`（15217）语义收窄为 success/failed/cancelled；running 取消返回成功并带 `cancel_requested` 投影；新增合成执行失败具名错误（编号落在 handler，冻结名入 `content-production.yaml`）。

## 3. 明确不做

- 不实现 Scheduler/定时触发、批量资源上限、策略上限（M5）。
- 不实现「我的成片」页面与 composite_output 查询 API（M4-C6）。
- 不实现下载中心成片支持（M4-C7）。
- 不修改 Agent / Desktop 原生代码；Agent 合同不出现 FFmpeg、快照或合成步骤。
- 不建通用 `template` 表、不开放动态工作流或上传脚本。

## 4. 有序任务与验收

| Task | 实施结果 | 验证 |
| --- | --- | --- |
| T-01 | `composite_output` 迁移 + 合同修订（15217 语义、cancel_requested、执行失败冻结名） | 迁移测试红先绿后；合同 YAML 解析与修订记录 |
| T-02 | Repository：原子领取/续租/进度/重试记账/取消请求/`composite_output` 事务提交/过期租约扫描查询 | sqlmock 定向测试（领取条件更新、只有成功事务产出成片） |
| T-03 | Service：领取→输入就绪门→执行→校验→临时键→正式提交的错误分类与状态机；业务失败 vs 临时失败 | 定向测试：快照只读、失败零成片、重试分类、恢复分支 |
| T-04 | Worker 运行时：主循环、并发/超时/租约配置、取消终止 FFmpeg、恢复扫描、临时目录清理；`cmd/compose-worker` 从验证壳升级为领取循环 | 循环单测 + 配置缺失拒绝启动 |
| T-05 | API：running 取消语义、cancel_requested/进度投影、执行失败错误映射；合同与 handler 比对 | handler 探针测试（冻结名读 yaml） |
| T-06 | 真实 MySQL/API/FFmpeg 验收：领取→准备→执行→成片全链路、快照遵循、取消 running、失败无假成片、租约恢复；验收数据清零 | 真实视频媒体探针 + 数据库前后对照 |
| T-07 | 全量回归与证据收口 | Go 全量、vitest 全量、双构建、diff check、治理 PASS |

每项按失败验证 → 最小实现 → 测试 → 证据 → checkpoint → 独立提交推进。

## 5. 验收标准

1. Worker 按任务快照使用对应模板版本执行；模板升级后绑定旧版本的任务仍按旧配置完成（对照任务快照、真实输出媒体信息）。
2. `composite_output` 只在对象存储落盘且大小/Hash 校验通过后创建；上传失败/校验失败/数据库失败均无成片行。
3. 取消（pending/running）、超时、FFmpeg 失败、Worker 崩溃与租约过期恢复均无假成片、无双执行；重试保留尝试记账。
4. 输入未就绪任务保持 pending 并经 `compose_input_prepare` 准备，ready 投影后才执行；源视频缺失为业务失败不重试。
5. 执行期不读取最新策略配置；修改策略不影响已领取任务的执行。

## 6. Pending Questions

None.

## 7. 范围裁定（规划期，依据工程规格与里程碑直接裁定）

- **Worker 进程形态**：`cmd/compose-worker` 从 M4-C4 验证壳升级为领取循环，保留既有 `compose.Lock` 单实例占用与工具校验（版本不兼容不领取）；M4 不做分布式多 Worker 编排，并发上限来自配置、默认小值。
- **输入准备边界**：Worker 通过 `file_transfer_task`（purpose `compose_input_prepare`、scope cloud）协作，复用既有 material_prepare job 的投影（`material.video_status=ready`）；Worker 自身不直接下载源文件。
- **输出提交顺序**：临时键上传 → 对象大小/SHA256 校验 → 「正式键 rename + composite_output 插入 + 任务 success」同一事务；事务失败由恢复任务清理临时对象；库成功而正式对象缺失按异常暴露。
- **取消语义**：`POST /compose-tasks/:id/cancel` 对 running 返回 200 并置 cancel_requested，Worker 确认后任务才 cancelled；15217 仅对 success/failed/cancelled。取消请求状态由任务行上的取消标记承载，不建第二张表。
- **进度模型**：stage 为有限枚举（`validating_input`/`cutting`/`probing_output`/`uploading`/`committing`），progress 在阶段边界推进，不做 FFmpeg 逐帧百分比。
- **错误分类**：具名业务失败（输入缺失、快照模板不可用、编码器不支持、参数被执行器拒绝）不重试；其余按临时失败退避重试至上限，超限置 failed 并保留最后错误。

## 8. 验收记录（2026-10-13）

- T-01～T-05：逐任务红先实现、独立提交（cloud `151baed`→`eb3ad0a`→`be295ad`→`cb09319`→`30bb4ff`）。
- T-06：真实 MySQL/API/FFmpeg 七探针（全链路成片、快照遵循、取消 running、失败无假成片、租约恢复、双实例拒启、数据清零）全 PASS；发现并修复「取消旗标骑进领取」真 bug（红先用例 + 实机确认，cloud `3ea646d`）。披露与残留（审计行保留、崩溃孤儿目录人工处置、素材 161 源对象重播）见 `evidence/T-06.md`。
- T-07：全量回归抓出两处 T-04 模块级盲区——`config_online/scheduler/compose.toml` 缺必填旋钮（deploy 模板补齐）、`prepare` 用例断言已上移的拒绝（环境门抽为 `verifyWorkerEnvironment`）——修复后 Go 71 包全绿、web vitest 524 例全绿、governance verify exit 0（cloud `61880e9`）。
- 验收标准逐条对照：①快照执行=探针 B（策略改后输出仍 1000ms）；②成片只在校验后创建=探针 A2/D（失败与 exhaustion 零成片行）；③取消/超时/崩溃恢复无假成片、无双执行=探针 C/E/F（含修复）；④输入未就绪等待=状态机用例 + T-03；⑤执行期不读最新策略=探针 B + execution.go 只读快照。
- 用户单项验收按既定指示并入 2026-10-14 M4 统一验收。
