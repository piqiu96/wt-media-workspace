# 窗口与代理实际 UI 整改：验证与人工评审

日期：2026-10-28。状态：本轮 UI 整改已验证、待人工评审；整体 CHG 保持 VERIFYING，未推送、未合并、未发布。

## 本轮范围

接续 Cloud 基线 `b86e65f` 的 DeepSeek 实现，按用户追加授权优化实际 Vue 页面。交互参考 V3，视觉采用本地 Token、TDesign 和内容生产 / 内容挖掘页面结构。两个参考页面没有修改；没有改 Go、数据库、迁移、Contract、Agent 或 Desktop Runtime，没有执行真实比特写入或迁移。

Cloud / Desktop 继续共用 `wt-media-cloud/web`。ID 独立列、五项以内平铺、只读详情无底部业务操作等本地规范保留。服务调用、权限、调度、失败重试和待确认核实仍使用已有实现；隔离数据只用于检查，未复制进生产代码。

## 公共候选：四项分别人工决定

| 候选与原因 | 本次实现和影响 | 兼容与审核重点 |
|---|---|---|
| 文字行操作：描边按钮占用过多列宽 | 新增 `resource/ResourceRowActions.vue`；两页显式接入，Loading / 禁用 / 权限保留 | `opColumnWidth` 增加可选 text 模式，默认 outline 数值不变；是否推广另行评审 |
| 批量工具栏：原窗口工具栏受行操作 max-content 样式挤压 | 新增 `resource/ResourceSelectionToolbar.vue`；全宽计数、动作、取消与原因提示 | 两页复用；选中状态和执行规则由页面持有；审核动作顺序和原因可读性 |
| 信息分区：详情和长表单缺少层级 | 新增 `resource/ResourceSection.vue`；800px 只读详情双列，代理表单分组双列、窄屏单列 | 仅显式容器生效，不改基础按钮 / 字号 / 品牌色；审核字段密度与分区 |
| 现场进度：结果扫描困难 | 升级既有 `feedback/OperationProgressDialog.vue`；960px 内摘要、七类计数、完整逐项状态与原因 | props / events 保持；仅窗口 / 代理现有消费者受影响；处理中不可普通关闭，结果可关闭，失败重试与核实分开 |

公共规范仅补充可选实现落点，不强制全站迁移。规范及公共候选与本轮页面改动一并提交人工审核。

页面改动还包括：代理低频筛选折叠且已设条件可发现；长名称 / 地址完整提示；导入长预览改抽屉；普通运营编辑只展示授权资料；空端口初始不显示人为的 0 值错误；动态提取缺少本机能力时明确禁用。未增加任务历史，比特标签仍按原 CHG 排除。

## 最终验证

| 范围与命令 | 实际结果 |
|---|---|
| Cloud web `npm test` | 88 文件 / 807 用例通过，0 失败；2026-10-28 09:52 重跑 |
| Cloud web `npm run build:cloud` | 通过；11.55s |
| Cloud web `npm run build:desktop` | 通过；7.54s |
| Cloud、Workspace `git diff --check` | 通过 |
| Workspace `python3 scripts/docs/check.py` | 通过：15 个索引 |
| 隔离 Chromium `node qa.cjs` | 22 项检查通过，pageerror 0；2026-10-28 09:52 后重跑 |
| 评审 HTML 检查 | 21 个场景、28 张内嵌截图；前后切换、无旧图场景、原图缩放、逐页意见、四项结论与 JSON 导出通过，pageerror 0 |

构建保留既有大 chunk 提醒；未扩大范围拆包。宽度函数新增用例先观察失败再实现；旧描边模式用例继续通过。两页既有源代码约束测试同步新布局选项，业务与权限断言保留。没有改后端，不重复运行与本轮无关的 Go / Rust / 数据迁移验证，前序证据见 `implementation-and-gates.md`。

22 项 UI 检查覆盖：五项文字行操作及禁用、混选批量限制 / 全宽 / 清除、详情返回保留搜索、托管与实际配置差异、窗口创建、筛选展开与重置、分组表单与提示位置、配额、处理中 Esc 阻断、七类计数和逐项表、自动部分结果与仅失败项重试、导入实际勾选计数、待确认 / 中断、1366 / 768 / 390 视口、高级运营网页版 / 普通运营网页版 / 管理员桌面端的呈现边界、普通运营资料编辑。

## 评审与复现

评审根目录：

`/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/resource-ui-review`

- `视觉整改评审.html`：自包含离线文件，可切换前后、逐页批注、四项采纳决定并导出 JSON。
- `评审说明.md`：阅读与决定说明；`ui-verification.json`：22 项实际读数。
- `before/`、`after/`：实际 Vue 页面截图，旧版 7 张、新版 21 张；同一明确测试数据。
- `serve-review.mjs` 固定旧版 `b86e65f`，隔离端口 5186 / 5187；`capture.cjs` 和 `qa.cjs` 复现截图及交互检查。使用本工作机已有依赖，不替换用户原有开发服务。
- 最终日志：`/tmp/wt-resource-full-tests.log`、`/tmp/wt-resource-cloud-final.log`、`/tmp/wt-resource-desktop-final.log`、`/tmp/wt-resource-ui-qa.log`。日志可清理，关键读数已记录在本文。

## 本地提交

Cloud：`dc07f59`（`chg/CHG-20261028-099`），10 个前端文件。Workspace 本记录与规范落点独立提交；两份无关社媒报告未纳入。未推送、未合并、未发布。

## 待人工验收与限制

隔离浏览器加载真实 Vue 源码，但拦截 API 并提供测试用 Tauri 桥；可以证明界面状态、前端请求范围与布局，不能证明真实服务和比特操作成功。真实比特开关窗 / 编辑读回、实际网络检测、完整集成和最终视觉选择仍需人工。原 CHG 的基线集成脚本缺失 `wt_media_agent.cloud_agent_client` 问题没有在本轮处理。

本轮可交用户评审，不将整体 CHG 标记 DONE。用户评审四项公共候选后，再按具体意见修订；推广到其他模块必须单独决定。
