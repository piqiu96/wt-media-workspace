# CHG-20261012-080：M4-C4 云端合成执行器验证

- Status: IMPLEMENTING
- Level: M
- Milestone: `delivery/milestones/M4-content-production.md`
- Closure anchor: §3.1 M4-C4；§5 闭环卡 M4-B
- Product: `docs/product/prd/详细文档/第五章_素材生产.md` §5.5
- Engineering: `docs/engineering/specs/2026-09-24-m4-m5-cloud-content-production.md` §4.3、§5.1、§6
- Decision: `docs/decisions/0017-m4-m5-cloud-owned-content-production.md`、`docs/decisions/0021-compose-four-layer-model.md`
- Affected repositories: `wt-media-cloud`
- Current repository: `wt-media-cloud`
- Activation: CHG-20261012-079 已归档（结构 + 合同就绪，模板 0 行）；用户于 2026-10-12 裁定 M4-C4 验收在本机做（对象存储凭据由用户重新发到本机 git-ignored 路径），`basic_cut` v1 只做切段。

## 1. 独立结果

独立的云端合成程序能检查视频处理工具和存储环境，用固定版本的执行代码把一条真实测试视频切成可播放的 MP4，写入并读回真实对象存储。工具缺失、模板版本未知或存储异常时不得报告成功。

## 2. 范围

- 新增 `cmd/compose-worker` 进程骨架与资源计划：启动即自检 FFmpeg/FFprobe（绝对路径、版本、必需编码器）与对象存储配置，任一不满足则拒绝执行。
- 建立模板版本到执行代码的绑定：代码级注册表 `(code, version) → executor`；`basic_cut` v1 执行器落地，schema 由执行器代码持有（入库发布留到 M4-C2 策略交付）。
- `basic_cut` v1 能力边界（用户裁定）：仅切段，参数只有 `start_seconds` / `end_seconds`，输出重编码为 H.264/AAC MP4；FFmpeg 参数由执行器固定构造。
- 单任务占用保护：跨进程锁保证同一时刻只有一个合成执行；每次执行使用仅以内部 ID 命名的隔离临时目录，清理只删本目录。
- 对象存储读写验证：输出上传临时键 → Stat 尺寸 → 预签名 GET 读回 sha256 比对 → 清理临时键。
- 真实验收：本机 FFmpeg 处理真实测试视频（`三角洲-2` 21MB），读写真实 Garage 对象存储。

## 3. 明确不做

- 不领取正式运营任务；不创建 `compose_task`、`composite_output` 或任何业务表记录（M4-C3/C5）。
- 不发布模板记录或 schema 入库；策略创建与验收属 M4-C2 策略交付。
- 不实现租约、heartbeat、重试、超时取消与重启恢复（M4-C5）；不做 Scheduler 与任何定时触发（M5）。
- 不接受动态节点、用户脚本、任意 FFmpeg 命令或运行时参数拼接。
- 不引入片头/片尾/BGM 资产参数键（ADR-0021 第 5 条，后续模板版本放开）。
- 不触碰 Agent/Desktop；Cloud 侧 HTTP Server 行为不变。

## 4. 有序任务与验收

| Task | 实施结果 | 验证 |
| --- | --- | --- |
| T-01 | FFmpeg 工具环境检查：`config/media/ffmpeg.toml` 配置（绝对路径、期望版本、必需编码器、工作区根目录）；缺失、版本不符或缺编码器时检查失败 | 先红测试；伪二进制阳性对照（假版本/假编码器/路径缺失各自失败） |
| T-02 | 模板版本→执行代码注册表；`basic_cut` v1 固定参数构造；未知 `(code, version)` 具名失败 | 先红测试；未知版本与版本越界不得成功 |
| T-03 | `basic_cut` v1 执行链：隔离临时目录（仅内部 ID 命名、只清理本目录）、FFprobe 输入校验、固定 FFmpeg 切段重编码、FFprobe 输出校验 | 先红测试；损坏输入与非零退出不得产出"成功"输出 |
| T-04 | 单任务占用保护（跨进程锁）与 `cmd/compose-worker` 进程骨架（资源计划、启动自检拒绝） | 先红测试；并发第二执行被锁拒绝；自检失败进程不执行 |
| T-05 | 对象存储读写验证：临时键上传、Stat、预签名 GET 读回 sha256 比对、清理 | 先红测试；存储未配置/上传失败/读回不一致均不得报成功 |
| T-06 | 真实验收：本机 FFmpeg 处理真实测试视频，读写真实 Garage；全量回归与证据 | 输出可播放且读回 sha256 一致；临时键清理干净；工具/版本/存储异常路径均有对照读数 |

每个 Task 按"先验证失败→最小实现→测试→证据→checkpoint→独立提交"推进。

## 5. 验收标准

1. `cmd/compose-worker` 以真实测试视频完成一次验证执行：FFprobe 校验 → FFmpeg 切段 → FFprobe 输出校验 → 对象存储写入 → 读回 sha256 一致 → 清理，全程无业务表记录。
2. 工具异常（路径缺失、版本不符、缺编码器）、未知模板版本、存储异常（未配置、读回不一致）各自具名失败，不出现假成功。
3. 并发第二次执行被单任务占用保护拒绝；临时目录只含本次执行的文件且执行后清理。
4. FFmpeg 命令由执行器固定构造，代码中不存在动态拼接命令或用户脚本入口。
5. Cloud 全量回归通过（Go + web），HTTP Server 现有行为不变。

## 6. Pending Questions

None.
