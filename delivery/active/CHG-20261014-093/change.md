# CHG-20261014-093：M5-C2a 引导视频上传与插入/画中画合成

- Status: IMPLEMENTING
- Level: M
- Milestone: `delivery/milestones/M5-automatic-production.md`
- Closure anchor: §4a M5-B1
- Product: `docs/product/prd/详细文档/第五章_素材生产.md` §5.5.3～5.5.5
- Engineering: `docs/engineering/specs/2026-09-24-m4-m5-cloud-content-production.md` §3.3
- Decision: `docs/decisions/0017-m4-m5-cloud-owned-content-production.md`、`docs/decisions/0021-compose-four-layer-model.md`
- Current repository: `wt-media-cloud`
- Affected repositories: `wt-media-cloud`

## 目标

高级运营上传引导视频并在策略中选择插入或画中画模板，配置插入位置、引导片段时长和成片时长。人工与自动合成任务都按创建时快照从 Cloud 对象存储取回两个视频，执行固定 FFmpeg 图，生成可播放的普通成片。

## 当前事实与边界

- `basic_cut` v1 是唯一已发布模板，Runner 只支持单输入切段；不能改变该版本的语义。
- Cloud 已有对象存储、任务快照、Worker、成片与短时预览链接；没有用户上传引导视频的正式资源实体。
- 参考代码在 `wt-media-flow/src/app/cli/composite.py`、`src/infra/media/compositor.py`，为 Python CLI/本地路径实现。本 CHG 迁移已确认的媒体规则，不引入第二套运行时或本地路径依赖。
- 上传资源不可变；配置引用资源 ID，不保存可过期 URL。旧任务仍能按原资源重放。

## 有序任务

| Task | 结果 | 验证 |
| --- | --- | --- |
| T-01 | Cloud 引导视频资源结构与上传/列表/预览 API，含权限、大小、媒体和对象存储读回 | Migration、API、真实对象存储、无效输入 |
| T-02 | `guide_insert`、`guide_pip` 固定模板与 schema；策略和任务按资源 ID 校验范围并保留快照 | Service/Repository 测试、旧 `basic_cut` 回归 |
| T-03 | Worker 按快照取回引导资源、校验摘要、执行两个固定 FFmpeg 图 | 真实 FFmpeg/FFprobe 样本、失败路径测试 |
| T-04 | 策略页面上传/选择/预览引导视频，模板参数就近校验；Cloud/Desktop 构建 | Web 定向测试、双构建、API/UI 对账 |
| T-05 | 本地完整任务产生对象存储成片、合同与交付记录收口 | 真实任务/成片/预览读回及回归 |

## 验收

1. 上传是 Cloud 资源，团队/游戏权限生效；只能选择已验证、不可变的本团队/游戏视频，预览链接短时有效。
2. 插入模式在指定位置拼入引导视频，支持引导时长与总时长；原视频短于插入位置时末尾拼接。画中画模式保留原视频前后段，在指定位置叠加引导画面。
3. 人工与自动任务共用策略、快照、Worker 和 `composite_output`；策略后续编辑不改变已创建任务。
4. 缺失/无效/越权引导资源与媒体失败不出现成功任务或成片。`basic_cut` v1 历史行为不变。
5. 真实 FFmpeg 输出可由 FFprobe 解析，上传后对象存储读回与页面预览成立。用户最终视觉签收按 M5 里程碑统一走查。

## 不做

- 不迁移参考项目的随机去重、贴纸、尾部动画、水印、目录批量或自动发布。
- 不保存任意外部视频 URL、本地机器路径或用户给出的 FFmpeg 命令。
- 不改变 Scheduler 的逐素材任务模型或 Worker Pool 并发策略。

## Pending Questions

None.
