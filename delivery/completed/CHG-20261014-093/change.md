# CHG-20261014-093：M5-C2a 引导视频地址与插入/画中画合成

- Status: DONE
- Level: M
- Milestone: `delivery/milestones/M5-automatic-production.md`
- Closure anchor: §4a M5-B1
- Product: `docs/product/prd/详细文档/第五章_素材生产.md` §5.5.3～5.5.5
- Engineering: `docs/engineering/specs/2026-09-24-m4-m5-cloud-content-production.md` §3.3
- Decision: `docs/decisions/0017-m4-m5-cloud-owned-content-production.md`、`docs/decisions/0021-compose-four-layer-model.md`
- Current repository: `wt-media-cloud`
- Affected repositories: `wt-media-cloud`

## 目标

高级运营在策略中填写可下载的引导视频地址并选择插入或画中画模板，配置插入位置、引导片段时长和成片时长。人工与自动合成任务都按创建时快照下载引导视频，执行固定 FFmpeg 图，生成可播放的普通成片。

## 当前事实与边界

- `basic_cut` v1 是唯一已发布模板，Runner 只支持单输入切段；不能改变该版本的语义。
- Cloud 已有任务快照、Worker、成片与短时预览链接；引导视频由运营提供可下载地址，转链接在独立运营工具实现。
- 参考代码在 `wt-media-flow/src/app/cli/composite.py`、`src/infra/media/compositor.py`，为 Python CLI/本地路径实现。本 CHG 迁移已确认的媒体规则，不引入第二套运行时或本地路径依赖。
- 任务快照固定地址和参数。外部链接可能失效或内容变化，失败时明确报告，不静默换源。

## 有序任务

| Task | 结果 | 验证 |
| --- | --- | --- |
| T-01 | 定义可下载 HTTPS 地址与安全下载边界 | URL、跳转、私网、大小、无效媒体测试 |
| T-02 | `guide_insert`、`guide_pip` 固定模板与 schema；策略和任务保存地址快照 | Service 测试、旧 `basic_cut` 回归 |
| T-03 | Worker 按快照下载并执行两个固定 FFmpeg 图 | 真实 FFmpeg/FFprobe 样本、失败路径测试 |
| T-04 | 策略页面填写引导视频地址，参数就近校验；Cloud/Desktop 构建 | Web 定向测试、双构建、API/UI 对账 |
| T-05 | 本地完整任务产生对象存储成片、合同与交付记录收口 | 真实任务/成片/预览读回及回归 |

## 验收

1. 策略仅接收可公开下载的 HTTPS 地址；下载不访问内网目标，限制跳转和大小，实际媒体无效时任务失败。
2. 插入模式在指定位置拼入引导视频，支持引导时长与总时长；原视频短于插入位置时末尾拼接。画中画模式保留原视频前后段，在指定位置叠加引导画面。
3. 人工与自动任务共用策略、快照、Worker 和 `composite_output`；策略后续编辑不改变已创建任务的地址。
4. 缺失/失效地址与媒体失败不出现成功任务或成片。`basic_cut` v1 历史行为不变。
5. 真实 FFmpeg 输出可由 FFprobe 解析，成片上传后对象存储读回与页面预览成立。用户最终视觉签收按 M5 里程碑统一走查。

## 不做

- 不迁移参考项目的随机去重、贴纸、尾部动画、水印、目录批量或自动发布。
- 不实现视频上传或转链接工具，不接收本地机器路径或用户给出的 FFmpeg 命令。
- 不改变 Scheduler 的逐素材任务模型或 Worker Pool 并发策略。

## Pending Questions

None.

## 验收结论

T-01～T-05 机器验收通过：下载边界、两个固定 FFmpeg 模板、策略与任务快照、Cloud/Desktop 页面回归、本地真实任务到成片及预览读回均有证据。Cloud 提交 `7beb3dd`、`93e6e94`；M4/M5 用户视觉签收仍按里程碑统一进行。
