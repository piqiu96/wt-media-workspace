---
id: CHG-20261118-105
parent: delivery/milestones/M6-single-publishing.md#单任务从内容准备到真实作品
status: VERIFYING
depends_on: ["CHG-20261118-104"]
affected_repos: ["wt-media-workspace", "wt-media-agent"]
risk: H
---

# CHG-20261118-105：M6-B 百度真实自动投稿

## Change

将已授权的单任务从所属用户领取，推进到百家号真实上传、填写、自动最终提交和可信稿件回执。沿用已有 Cloud 契约、确认内容、持久化提交屏障及原尝试补报；不以平台接收冒充公开成功。

Agent 实现实际浏览器表单适配与 Local/Sidecar 串行领取循环；Cloud 模式不操作浏览器。仅使用当前内存 Agent Token 路由所属用户，正式权限仍由 Cloud 校验；会话变化停止新的动作，旧结果只按原用户补报。Desktop 验证重新打包后的 Sidecar，不复制 Vue 或平台逻辑，不为形成 PR 制造壳代码变更。

本单元不实现批次、计划、其他平台、公开作品核实/补录、人工继续或新建续编。页面沿用已有任务状态及详情，无新 UI 设计。真实提交只使用已授权账号和系统成片；平台要求人工安全验证时如实记录，不绕过、不自动重复投稿。

按用户本轮临时授权，串行堆叠于 CHG-104，前置 PR 尚待 Review；不修改永久治理规则、不自动合并。原任务 3 当前 attempt 4 仍为 uncertain。用户本轮明确确认旧视频未发布，并授权从成片另选视频、按素材填写并投稿。46 号窗口已使用不同的标准成片完成一次真实平台适配验证，取得稿件号 `1882173445914373676`，提交结果页显示“提交成功，正在审核中”，随后作品管理页显示“已发布”并提示“作品仅主页可见”。此次未领取或重试原任务，也未将新回执绑定到旧任务；Cloud 所属用户领取、提交屏障及结果回写的完整真实闭环仍未验收。

## Done When

- 实际表单上传原快照对应视频及封面，读回确认文案、话题和声明；不自动替换内容或伪造平台能力。
- 最终提交前已持久化阶段并取得新鲜 Cloud 允许；只点击一次。取得与当前编辑稿件匹配的真实回执才回报 reviewing，无回执或现场未确认结束仍 uncertain，不宣称公开成功。
- Local/Sidecar 只在 runner 开启且所属用户凭据有效时领取；Cloud 模式无发布循环。启动、重复领取、断网和重启不得重入旧尝试或重放最终点击；补报保留原 packet/hash。
- 自动测试覆盖表单不完整、账号/凭据变化、停止、提交边界丢包和回执不可信；真实浏览器走查记录实际字段、上传与结果，不以模拟结果替代投稿验收。
- 运行适用的 Agent、契约、构建、Desktop Sidecar 与 Workspace 检查，记录可复现证据并提交独立堆叠 PR；未通过的外部验收明确保留，M6 不标记 DONE。

## 实施与检查顺序

| 当前情况 | 计划修改 | 验证 |
| --- | --- | --- |
| 协调器已有，平台实现需按已确认设计调整 | Agent `BrowserSession` 以 Playwright 连接现有 BitBrowser，`Publisher` 协议及 `BaiduPublisher` 分离平台表单与任务授权；本机大文件使用路径及 `is_local=True` | 隔离真实浏览器验证填写、停止、提交回执及超过 50 MiB 文件；安全核实原尝试后才可真实投稿 |
| Local/Sidecar 仅运行下载循环 | Agent `runner/publication_loop.py`、`runtime/agent_token.py` 及 bootstrap 显式装配 | 无 Token 零领取、旧会话停止新动作、只补报原用户、Cloud 不启动 |
| 打包仍为上一单元 | 现有打包入口重建 Sidecar/DMG，Workspace 记录已验证版本及证据 | 标准测试、真实开发页面与安装产物检查；各变更仓独立提交 |

## 本轮真实页面适配

使用 46 号窗口核对现有表单。串行修正封面上传判定：将本地图片解码校验限定到选中文件的上传控件，避免把视频抽帧缩略图误认为上传成功；支持新视频的空封面控件；最终提交前再次检查视频上传状态，并精确处理未匹配话题确认框，保留原文且不再次点击发布。先在隔离浏览器复现失败，再修改 `clients/baidu/publisher.py`，运行发布器浏览器检查和 Agent 标准检查。原恢复现场继续保留，不重新执行旧任务或修改 Cloud 契约。

## 当前验收

发布器、串行领取与打包接入已实现。既有 Workspace 211 项检查通过；本轮 Agent 739 项及隔离浏览器 14 项通过，46 号真实视频上传、文案/双封面填写、一次最终投稿和匹配回执验证通过；实际 BitBrowser 和包内驱动均验证了 64 MiB 本地文件。本次是用户直接授权的独立平台适配验证，未通过 Cloud 正式任务领取/提交前许可/原尝试补报链路，也未验证更新后的安装包；原任务状态未改。因此本单元保留 `VERIFYING`、M6 保留 `IN_PROGRESS`。[实际证据与限制](evidence/verification.md)。

## References

- [M6](../../milestones/M6-single-publishing.md#单任务从内容准备到真实作品) M6-B。
- [PRD](../../../docs/product/prd/详细文档/第六章_发布管理.md) 6.4、6.5、6.8；[Engineering Spec](../../../docs/engineering/specs/publishing-management.md) §2.2、§4、§5.3、§6。
- [前置核实与安全重试证据](../CHG-20261118-104/evidence/verification.md)。Cloud 提供方契约仍为 2026.11.18.3，不新增接口。
- 页面验收引用 Cloud `web/example/proto/publishing-design/PublishingTaskPage.vue`、`TaskDetail.vue`；[公共交互规范](../../../docs/standards/frontend/前端交互规范.md)。服务地址从当前启动输出获取。
