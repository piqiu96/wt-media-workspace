# M6 发布页面公共原型落地与视觉整改

日期：2026-11-18。CHG-101 保持 `VERIFYING`，M6 保持 `IN_PROGRESS`。本记录补充原有业务验证，不代表公开作品闭环、安装版走查或用户视觉签收。

## 依据与当前差距

原型基线仍为 Cloud `9f132dd375477c116809b48507f6fd7a8b28d567` 的 publishing-design 与 common；本轮基于 Cloud `55fa6fc8753d26b7554793b7275da5ffaa78d48e` 的现有真实发布页面整改，不回退后续任务执行和核实能力。原型基线固定，公共适配改为消费同一份真实组件，不新增第二套原型规则。

走查确认：正式双入口未加载公共列表/表格/操作样式，任务列表缺少显式适配；快速发布使用原生日期、普通文字星号和局部字段样式；详情绕过 ResourceSection/Descriptions；操作栏可能同时出现两个主操作。旧记录只说明结构和业务操作，不能证明视觉一致。

## 修改与覆盖范围

| 部分 | 已修改 | 覆盖与边界 |
| --- | --- | --- |
| 公共样式 | 双入口加载 resource-surfaces；列表与表格显式接入；表单操作增加 resource-form-actions-scope；弹层使用 form-actions | 原型入口显式接入原有展示范围；正式页面先覆盖发布工作区，不因打开该页面改版其他页面 |
| 公共组件 | 新增 ResourceRequiredLabel，原型 RequiredLabel 改为适配；ResourceOverlay/MediaPreview 增加默认关闭的操作样式接入；ResourceDescriptions 过窄时纵向标签和值 | 已有公共实现复用，不复制离线脚本；不改变业务状态、保存或权限 |
| 任务列表 | 同一白卡承载筛选/表格/分页；公共表头、字体、边距与行操作；默认10条；统一平台文案 | `/publish`，Cloud/Desktop 共用源码；不增加演示统计或任务动作 |
| 快速发布/编辑 | 13px/500标签、红色必填标识、24px内容字段节奏、公共时间选择与字段帮助、封面预览；锁定字段保持可读 | 保留内容确认、资源锁定、未保存保护、请求键与修订号逻辑 |
| 任务详情 | 公共分区、容器自适应字段与封面预览；详情只读，底部仅返回 | 执行、编辑、核实、安全重试已移至列表；审核中仍不代表公开成功 |
| 资源选择/核实 | 标准960px资源弹窗、公共内嵌表格与行操作、核实表单必填及按钮层级 | 输入、资格校验和关闭恢复保持原业务语义 |
| 页面切换 | 打开编辑/详情回到正文顶部，返回列表恢复原滚动位置 | 保留筛选和列表上下文 |

公共规范只补充接入、冲突裁定及覆盖核验要求，没有改写原有颜色、字号、间距或组件库基线。已知背景 Token 引用缺口已在发布页改用现有 `--wt-color-bg-subtle`。

明确差异与后续范围：

- 用户已确认：真实成片接口没有缩略图字段，本轮保留真实摘要并调用现有 video-url 预览，缩略图数据后续补齐；未伪造缩略图或扩大 Contract。
- M6 已明确后置 AI 文案、封面模板与通用图片库维护；不照搬这些演示功能，不添加无真实能力的控件。
- 生产策略/任务/成片、内容挖掘/素材、账号和文件等既有页面未作整页迁移，不能据本次声明全产品覆盖；迁移时继续使用相同公共组件与样式并列出覆盖清单。批次/计划/图片库/模板的正式业务仍由后续 Milestone 交付。本轮以文件页验证未接入页面的按钮隔离性，以全量前端测试及原型回归检查共享组件影响。
- 正式导航外壳沿用既有产品；未混入当前另一个任务的导航修改。

## 前轮验证

以下保留首轮验证；当前追加修正的结果见文末。

全部浏览器回归使用本次独立启动的 Vite 服务、独立 Chrome 上下文和固定 API 数据，服务地址来自本次启动。接口全部拦截，没有调用真实任务写入、授权执行或平台投稿。浏览器证据只证明 UI 与输入/返回行为，不证明生产数据或真实视频播放。

| 检查 | 实际结果 |
| --- | --- |
| `npm test`（Cloud web） | PASS：136文件、1007项；[日志](visual/publication-tests.log) |
| `npm run build:cloud` / `npm run build:desktop` | PASS；保留已有包体提示；[Cloud](visual/publication-cloud-build.log)、[Desktop](visual/publication-desktop-build.log) |
| `CHROMIUM_EXECUTABLE=<本机Chrome> node scripts/test-publication-visual-browser.mjs` | PASS：1440px与390px共43项；0页面异常、0写入请求。检查列表默认条数、公共字体、辅助实底/表格文字操作隔离、快速发布空表单、详情操作检查（后续追加纠正为只保留返回）、图片弹窗返回、视频地址接口503及实际媒体404均可重试、输入及列表筛选保留、窄容器可读、页脚不遮最后字段；[断言](visual/checks.json)、[日志](visual/publication-final-ui.log) |
| 同一脚本加 `WT_MEDIA_CHECK_PROTOTYPE=1` | PASS：既有 commonVisual 与 taskPages 共18项；覆盖任务/批次/计划/图片库/模板列表与整页模式、窄屏及返回保护；[日志](visual/publication-visual.log) |
| `python3 -m unittest discover -s tests`（Workspace） | PASS：211项；[日志](visual/publication-workspace-tests.log) |
| `verify_product_master_alignment.py`、两仓 `git diff --check` | PASS |

390px截图使用产品已有侧栏折叠操作，正文按真实可用宽度验证；同时增加容器级重排和共享详情的过窄适配，不能仅用没有整页横向溢出认定可读。图片是测试数据，视频失败路径经实际点击验证；完整真实视频播放及安装版视觉仍须后续真实环境复核。

## 页面与原型证据

| 入口 | 正式页面 | 公共原型参考 |
| --- | --- | --- |
| 列表 | [1440px](visual/1440-list.png)、[390px](visual/390-list.png) | [列表](visual/prototype-tasks-list.png) |
| 快速发布 | [1440px](visual/1440-quick-publish.png)、[390px](visual/390-quick-publish.png) | 完整新增/编辑按同一公共外壳核验 |
| 编辑 | [1440px](visual/1440-editor.png)、[390px](visual/390-editor.png) | [编辑](visual/prototype-03-edit-viewport.png) |
| 详情 | [1440px](visual/1440-detail.png)、[390px](visual/390-detail.png) | [详情](visual/prototype-11-detail-review-viewport.png) |
| 资源选择 / 核实 | [资源](visual/1440-picker.png)、[核实](visual/1440-verification.png)、[窄屏核实](visual/390-verification.png) | 复用公共弹层、内嵌表格和表单操作模式 |

本轮先在独立 Cloud 工作目录验证，避免当前导航任务的未提交改动。未自动合并、发布或标记 CHG DONE；真实安装版与用户视觉签收仍待完成。

独立只读复核发现的视频媒体加载失败无提示/重试（P2）已修复；定向浏览器复核同一404场景，错误提示与重试入口均出现，未发现新的P1/P2。

已将验证修改应用回配置映射的实际 Cloud 工程，16个目标文件与独立验证目录逐字节一致；原导航任务3个文件的摘要完全保留。前一轮未提交补丁 SHA256：`fcd5b365bea6eac2a1204136a46237715526a46f9c375827af6331a6c58ea4bb`，仅追溯前一轮应用，不含下列追加修正，不是发布版本。

实际 Cloud 工程应用后再执行 `npm test`：136文件、1007项全部通过，见[应用后回归](visual/publication-original-tests.log)。


## 追加走查：菜单遮挡与按钮职责

用户截图指出的两项问题均有效；前一轮“刷新移到底部、保留详情业务动作”的处理不符合 PRD §6.4，本段纠正该结论。

- 根因：正式外壳没有传入原型侧栏宽度变量，固定 Footer 回退为 `left: 0`。修复前浏览器断言已实际复现“page footer never covers sidebar”失败。
- 修复：ResourceDetailPage 以最近可滚动正文容器的实际边界定位底栏，通过 ResizeObserver 跟随菜单展开/收起、窗口变化；没有该容器时保留原型的变量接入。正文继续按真实 Footer 高度留空，未修改当前独立导航任务。
- 按钮：按 PRD 6.4.1/6.4.3/6.4.4，把执行、编辑、核实结果、安全重试放回列表；列表名称为“执行”，确认弹窗才用“确认执行”。详情仅返回，删除“刷新进展”；行操作复用32px公共文字/轻按钮，页脚和确认弹窗沿用公共实底层级。
- 并发：执行/重试 fresh GET 同时比较列表修订号，内容或状态变化时更新列表并拒绝直接授权未阅览版本；取消确认不写入任务。编辑也复核取消标记。
- 能力缺口：终止、去处理、完整核实/补录、放弃、作品关联和条件复制不能视为已完成；真实提供方缺少完整能力，沿用 M6-C 范围，实施顺序与覆盖要求回写 Milestone。PRD 不改为迁就当前实现。

本轮追加直接在实际 Cloud 工作区完成，不复用此前独立目录。最新验证与截图在 `visual-footer/`，替代上表中对应旧页面截图；原型18项回归仍通过，未修改业务原型按钮规则。


| 最新检查 | 实际结果 |
| --- | --- |
| 正式页面浏览器 | PASS：1440/390px，69项，0页面异常、0写入；包含展开/收起菜单边界、详情只返回、列表执行/重试取消、旧修订阻止授权与重试、32px行操作、输入保留、原有文件页隔离。[断言](visual-footer/checks.json)、[日志](visual-footer/final-ui.log) |
| 公共与业务原型 | PASS：18项，包含只读详情页脚与窄屏避让。[日志](visual-footer/prototype-regression.log) |
| 前端回归 | PASS：136文件、1007项。[日志](visual-footer/tests.log) |
| Cloud / Desktop 构建 | PASS；已有包体提示仍保留。[Cloud](visual-footer/cloud-build.log)、[Desktop](visual-footer/desktop-build.log) |
| Workspace | PASS：211项；产品/交付对齐和两仓 diff 检查通过。[日志](visual-footer/workspace-tests.log) |
| 既有真实业务走查脚本 | preparation / execution / recovery 已同步列表入口并通过语法检查；本次未执行真实任务写入或平台投稿 |

最新截图：[列表操作](visual-footer/1440-list.png)、[快速发布底栏](visual-footer/1440-quick-publish.png)、[只读详情](visual-footer/1440-detail.png)、[编辑](visual-footer/1440-editor.png)、[窄屏编辑](visual-footer/390-editor.png)。独立只读复审指出的旧列表修订可能授权未阅览内容问题已修复并加入浏览器断言，复审未发现其余新增 P1/P2。

安装版真实点击走查、真实成片完整播放和用户视觉签收仍未完成；本轮没有提交、合并或发布，也未改变 M6 的完成状态。
