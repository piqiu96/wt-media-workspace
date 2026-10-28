# frontend 公共视觉规范优化审核稿 V1

日期：2026-10-28。版本：审批前提案快照。对象：`docs/standards/frontend/` 下现有四份规范及入口 README。

**后续结论**：用户已审批14项，正式规范已回写；V07采用短表单Dialog，V08按批注改为字段密度自适应单/双列。详见[审批落地记录](frontend-visual-standard-apply.md)及其正式规范链接。下文“待审 / 建议 / 本轮不修改”为提交审批时的历史表述，不代表当前状态。

本稿用于审批规范修订，不是新一套并行规范。本轮不修改正式 frontend 规范、不再改运行时代码、不合并发布。批准的条款将分别回写原文档，保留各文档的职责分工。

## 任务理解

以用户认可的原视觉稿为质量目标，提炼可复用设计原则，改善公共规范及其组件约束。不能只让窗口/代理两个页面好看，也不能把原稿的优点压回原有库默认样式。本次先交审核稿，审核后再回写规范和形成实施边界。

## 当前事实与约束

视觉基线：`browser-proxy-design/screens/` 当前实际为75张PNG（文件沿用原88项编号，并非88张连续截图）。已查看5张总览、10张代表性高清图及相应原型CSS，覆盖列表、详情、创建、选择、导入、进度、按钮和状态；本稿是公共规范评审，不冒称已逐屏完成75项业务验收。全部截图文件清单见附录。

原稿的主要优点是：冷灰白与克制的品牌蓝；标题/辅助信息的比例；筛选、表格与分页的统一边界；横向键值详情；相关字段的双列组合；卡片式语义选择；浅色提示与状态的轻重；批量结果的视觉中心。

当前实现/规范的主要偏差：旧规范把所有整改锁定为PATCH；反馈和主体有两套颜色；32/40px控件缺少与原稿相近的常规档；详情被统一改为标签在上的双列；语义选择退回裸单选；分区和提示要么过重、要么过度压平；验证只证明运行正确，未强制验证视觉目标。

本稿中精确数值均为建议的CSS逻辑像素或候选Token，不是已经批准的取值。原稿有些字段如比特标签尚未接入合同，视觉审美批准不代表功能自动纳入范围。权限、资源关系、真实执行结果与异常恢复语义继续保留。

## 计划修改与审批总表

建议14项均按下文推荐方案审阅；V07特意保留“短表单Dialog”与“恢复原稿Drawer”的明确选择，避免覆盖你上一轮对空洞侧栏的反馈。

| 编号 | 审核主题 | 影响 | 建议 | 你的决定 |
|---|---|---|---|---|
| V01 | 让已审批视觉目标成为实施依据 | 高 · 执行规则 | 采用下文推荐 | 待审 |
| V02 | 统一冷灰层次与语义配色 | 高 · 公共 Token | 采用下文推荐 | 待审 |
| V03 | 重建清楚而紧凑的字号与控件节奏 | 高 · 基础密度 | 采用下文推荐 | 待审 |
| V04 | 保留原稿的页面骨架与轻面板 | 中 · 页面模板 | 采用下文推荐 | 待审 |
| V05 | 表单按字段关系组织，避免全单列或全双列 | 中 · 表单组件 | 采用下文推荐 | 待审 |
| V06 | 将语义选择恢复成带说明的卡片 | 中 · 新公共模式 | 采用下文推荐 | 待审 |
| V07 | 保留原稿浮层气质，同时延续短表单居中 | 高 · 容器与遮罩 | 采用下文推荐 | 待审 |
| V08 | 详情以横向键值对为默认，双列按内容选择 | 高 · 详情组件 | 采用下文推荐 | 待审 |
| V09 | 分区标题减少重线条和重复层级 | 中 · ResourceSection | 采用下文推荐 | 待审 |
| V10 | 采用原稿的轻提示层级，减少说明而非删除引导 | 高 · 提示视觉 | 采用下文推荐 | 待审 |
| V11 | 列表、按钮和状态保留原稿的轻重关系 | 中 · 保留加补齐 | 采用下文推荐 | 待审 |
| V12 | 批量结果恢复原稿的视觉中心 | 中 · OperationProgressDialog | 采用下文推荐 | 待审 |
| V13 | 公共能力优先做完整，再推广 | 高 · 组件与迁移 | 采用下文推荐 | 待审 |
| V14 | 把视觉还原纳入验收，而不是只看测试通过 | 高 · 验收 | 采用下文推荐 | 待审 |

## 逐项审核条款

### V01｜让已审批视觉目标成为实施依据

**回写位置**：README；AdminUI §0；架构与视觉 §8.1。**影响**：高 · 执行规则。

**现状与问题**：当前有“视觉稿只作参考”“现有整改一律 PATCH”“符合旧规范就不为追图修改”。这些规则会让开发保留明显低于目标的实现。

**推荐决定**：推荐修订为 PATCH 与 REDESIGN 两种明确模式。本次后续视觉重构按经审核的目标实施，允许调整公共组件和对应规范。

**建议写入规范的条款**：

> 普通修补按 PATCH 冻结无关范围。用户明确要求视觉重构时，登记视觉基线、需调整的规范条款、公共影响与验收场景后按 REDESIGN 实施；已批准的目标视觉及本次审定条款共同构成验收依据。不得以组件默认样式或旧规范阻止已批准目标落地；未经审核的图稿不自动覆盖业务、权限与外部执行规则。

**兼容与边界**：只建立受控的视觉重构方式，保留需求方最终决定和变更可追溯性；不授予开发无限制全站重构权。

**原稿依据**：[01-w-list.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/01-w-list.png)。

- 审核结论：□ 同意推荐　□ 修改后同意　□ 暂不采纳
- 你的批注：

### V02｜统一冷灰层次与语义配色

**回写位置**：架构与视觉 §3.6.1；用户反馈“组件与视觉”。**影响**：高 · 公共 Token。

**现状与问题**：主体规范和反馈规范分别写了两组绿、橙、红硬编码色；现有规范与原稿的背景、正文和边框色也不完全一致。

**推荐决定**：推荐采用原稿冷灰白基调，保留品牌蓝，反馈与状态共用同一语义色源。

**建议写入规范的条款**：

> 品牌色保持 #0052D9；候选基础色为页面 #F4F6F9、容器 #FFFFFF、浅层 #F6F8FB、边框 #E7EBEF、主文字 #263449、次级文字 #657184。辅助灰 #8C97A5 仅用于非关键辅助内容，关键值与错误原因不得灰到难读。语义色通过一套 Token 同时映射 TDesign、状态和反馈；反馈规范不再另定义一套十六进制色表。所有浅底标签和提示在实际字号下验证文字可读性后定稿。

**兼容与边界**：本项影响主题与全站消费者，需单独批准后集中映射和分批回归；不在页面散落新色值，不把某个业务状态颜色改成新业务含义。

**原稿依据**：[64-s-status.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/64-s-status.png)。

- 审核结论：□ 同意推荐　□ 修改后同意　□ 暂不采纳
- 你的批注：

### V03｜重建清楚而紧凑的字号与控件节奏

**回写位置**：架构与视觉 §3.6.2、§3.6.3、§3.6.5。**影响**：高 · 基础密度。

**现状与问题**：现规范只有 20px 页面标题、16px 模块标题、32/40px 控件，缺少列表、详情行、弹层之间的比例；容易把所有区域做得一样大。

**推荐决定**：推荐页面标题更明确、分区标题更克制，采用 36px 常规控件和专门的列表密度。

**建议写入规范的条款**：

> 页面标题 24px/600；弹层标题 18px/600；分区标题 14px/600；正文与表单值 14px；列表正文 13px，确需高密度时可用 12px；辅助文字 12px；关键动作不得缩成 10–11px。常规输入与按钮 36px，密集工具栏 32px，40px 仅用于明确的大尺寸场景。保持 4px 间距网格：字段间 16–20px、分区间 24–28px、同组操作 8px、文字操作 12px。

**兼容与边界**：这些是候选 CSS 逻辑像素，不是从 2400px 位图直接抄数。原稿 CSS 使用 23px 标题、34/36px 控件等，建议归并为项目档位；批准后在 100% 缩放下用同尺寸截图确认整体比例。

**原稿依据**：[01-w-list.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/01-w-list.png)。

- 审核结论：□ 同意推荐　□ 修改后同意　□ 暂不采纳
- 你的批注：

### V04｜保留原稿的页面骨架与轻面板

**回写位置**：AdminUI §2–§3；架构与视觉 §3.6.4、§4.1。**影响**：中 · 页面模板。

**现状与问题**：原稿的筛选区、表头、正文和分页共用一个干净面板；实现容易叠卡片、重复内边距，或为填空添加说明。

**推荐决定**：推荐将原稿的对齐和面板关系写成公共资源页模板，而非只记几个圆角数。

**建议写入规范的条款**：

> 页面常规内边距 24px，宽屏可用 28px；区块间距 16–20px。筛选与列表、分页共享一个容器边界，内部以轻分隔线组织，不再嵌套第二个同义白卡。筛选标签置于控件上方，查询与重置与控件基线对齐。统计仅在能帮助判断或快捷筛选时出现，不因页面空而补卡片。

**兼容与边界**：保留现有指标准入规则；不把原稿两张统计卡推广成所有模块必选。应用外壳导航关系仍由产品定义，原稿只作为比例和选中态参考。

**原稿依据**：[01-w-list.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/01-w-list.png)。

- 审核结论：□ 同意推荐　□ 修改后同意　□ 暂不采纳
- 你的批注：

### V05｜表单按字段关系组织，避免全单列或全双列

**回写位置**：AdminUI §6.2；架构与视觉 §4.4.1。**影响**：中 · 表单组件。

**现状与问题**：原稿长文本满行、协议/端口与认证成组，短表单无重复标题；当前仅用“所有表单两列”或一串单列控件都不够。

**推荐决定**：推荐顶部标签，相关短字段成对，长字段和需要连续阅读的信息满行。

**建议写入规范的条款**：

> 表单标签在控件上方，标签与控件间 8px；帮助和校验在该控件下方，绝不挤到输入右边。名称、地址、提取链接、备注等长内容满行；协议/端口、用户名/密码、地区/供应商可成对。只按实际字段分区，单组短表单不再重复“基础信息”。窄容器自动退为单列，错误后保留内容和相关动作。

**兼容与边界**：不因为原稿有字段就恢复未支持的比特标签，不更改现有必填、默认值、认证保留或权限规则。

**原稿依据**：[40-p-create.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/40-p-create.png)。

- 审核结论：□ 同意推荐　□ 修改后同意　□ 暂不采纳
- 你的批注：

### V06｜将语义选择恢复成带说明的卡片

**回写位置**：AdminUI §6.3；架构与视觉 §4.4.1。**影响**：中 · 新公共模式。

**现状与问题**：原稿“比特自管 / 系统托管”“静态 / 动态”有选项标题、简短说明和整卡选中态；现实现退化为裸单选，视觉与决策提示都减弱。

**推荐决定**：推荐沉淀通用 ChoiceCard，不继续用长段说明补裸单选。

**建议写入规范的条款**：

> 涉及操作方式、资源来源或执行策略的少量互斥选择，用 2–3 张等高选项卡：标题、单行差异说明、真实单选控件；整卡可选，选中用浅品牌底和细边框。普通二值开关与没有解释成本的选项仍用原生控件。必须支持键盘、焦点、禁用与错误，不只实现鼠标点击外观。

**兼容与边界**：仅封装选择表达，不自行推导业务权限、代理状态或后续执行；短表单使用 Dialog 时也完整保留此模式。

**原稿依据**：[06-w-create.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/06-w-create.png)。

- 审核结论：□ 同意推荐　□ 修改后同意　□ 暂不采纳
- 你的批注：

### V07｜保留原稿浮层气质，同时延续短表单居中

**回写位置**：AdminUI §6.1、§7.5；交互 §9；架构与视觉 §4.4。**影响**：高 · 容器与遮罩。

**现状与问题**：原稿短新建/编辑用 Drawer，用户上轮明确指出空洞并要求评估 Dialog；不能因这次认可原稿就无说明地反转。原稿的浅遮罩和浮层比例也优于单纯库默认值。

**推荐决定**：推荐短表单继续居中，完整保留原稿字段分组、卡片选择、留白和对齐；长配置与关联详情保留 Drawer。

**建议写入规范的条款**：

> 短表单 Dialog 560px，较宽表单 640px；资源选择/批量结果 960px；空选择场景收至 560px。Drawer 标准 800px、复杂内容 960px，按实际内容选用，字段数量只作参考。Header 高 64px、左右 24px，正文 24px、Footer 16px×24px；内容受视口约束、正文滚动、关键动作可达。候选遮罩 rgba(35,51,78,.28)，弹层圆角 8px、统一轻阴影；多层不叠加成黑屏。

**兼容与边界**：本项请优先审核：推荐“短表单 Dialog + 原稿视觉”；也可批注选择“短表单恢复原稿 Drawer”。本轮仅提案，不再次改容器。只读详情无空 Footer，危险操作仍确认，处理中关闭保护保持。

**原稿依据**：[06-w-create.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/06-w-create.png)。

- 审核结论：□ 同意推荐　□ 修改后同意　□ 暂不采纳
- 你的批注：

### V08｜详情以横向键值对为默认，双列按内容选择

**回写位置**：AdminUI §7.2；架构与视觉 §4.4.2。**影响**：高 · 详情组件。

**现状与问题**：原稿 03–05、38–39 的标签与值横向成行，眼睛沿同一条值轴扫描。上轮一律标签在上、值在下再分双列，改变了原稿的阅读节奏。

**推荐决定**：推荐恢复横向键值行；比较卡和关系表保持原稿完整表达，避免详情表单化。

**建议写入规范的条款**：

> 对象属性默认使用无框键值列表，标签列约 112–128px，标签与值间 16px，短值行高约 32px，长值自然换行且不裁掉关键信息。只有相互独立的短字段才使用双列；单个对象名称、地址、备注不强行并排。配置差异使用托管/实际并排比较，关联对象使用真实关系表；不为减少行数隐藏字段或复制摘要。

**兼容与边界**：建议由描述列表公共适配器提供布局选项，不全局覆盖所有 TDesign Descriptions；窄屏自然堆叠，读数与复制能力仍归业务页。

**原稿依据**：[38-p-detail.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/38-p-detail.png)。

- 审核结论：□ 同意推荐　□ 修改后同意　□ 暂不采纳
- 你的批注：

### V09｜分区标题减少重线条和重复层级

**回写位置**：AdminUI §6.2、§7.2；架构与视觉 SharedUI。**影响**：中 · ResourceSection。

**现状与问题**：原稿详情用轻竖标识、表单用标题旁细线。当前所有分区都加一整条下边框与较大标题间距，容易显得层级过重。

**推荐决定**：推荐一个公共分区组件提供表单与详情两种外观，语义统一、表达按内容。

**建议写入规范的条款**：

> 表单分区为 14px 标题与同一基线的浅分隔线；详情分区为克制的左侧标识与标题，正文不嵌套描边盒。只有需要比较或独立交互的内容才用卡片。一个弹层内按固定节奏分组，不连续堆多个仅含一项的分区，不为对称增加 Tab 或重复当前对象摘要。

**兼容与边界**：只新增显式 variant，不把不同业务章节拆成一套业务私有组件，也不默认替换所有既有标题。

**原稿依据**：[05-w-detail-mismatch.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/05-w-detail-mismatch.png)。

- 审核结论：□ 同意推荐　□ 修改后同意　□ 暂不采纳
- 你的批注：

### V10｜采用原稿的轻提示层级，减少说明而非删除引导

**回写位置**：用户反馈“选型/视觉”；架构与视觉 §4.5。**影响**：高 · 提示视觉。

**现状与问题**：用户不喜欢的是大面积、高饱和、多条重复提示。原稿仍有合理的浅色提示；上轮把信息过度压成一行或全改纯文字，同样丢失层次。

**推荐决定**：推荐普通帮助纯文字、真实影响用紧凑浅底摘要、真正异常保持明确状态。

**建议写入规范的条款**：

> 普通格式说明为 12px 中性文字或按需帮助；影响摘要可用浅中性底、1px 轻边框与16px图标；明确风险可用克制的语义浅底，内边距 12–16px，不用大图标或高饱和整块背景。同一事实只反馈一次，通常一个任务区域保留一个主要摘要。关键后果默认可见，补充名单与格式可展开；零账号不显示“影响0个”。空资源与筛选无结果使用一处可恢复空态；加载失败和无权限仍单独表达。

**兼容与边界**：不设“所有提示一律禁色”的规则；不为视觉删掉代理替换、直连、检测失效等后果，也不把持续阻断藏到 Tooltip。

**原稿依据**：[14-w-bind.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/14-w-bind.png)。

- 审核结论：□ 同意推荐　□ 修改后同意　□ 暂不采纳
- 你的批注：

### V11｜列表、按钮和状态保留原稿的轻重关系

**回写位置**：AdminUI §4；架构与视觉 §3.7–§3.9。**影响**：中 · 保留加补齐。

**现状与问题**：原稿 ID 独立、名称突出、地址/备注次级、行操作文字化、状态有浅底而非满屏蓝链接。这些与本地多数现行规则一致，无需推翻。

**推荐决定**：推荐保留现规则，补充可执行的密度与不同控件状态样式。

**建议写入规范的条款**：

> 表头约44px，单行数据行约48px，多行资源摘要64–80px随内容；不靠压字号强塞列。行操作文字化且保留真实 Loading：不超过5项全平铺，超过5项才收纳。每个操作区域至多一个实心主按钮；次按钮白底细框，文字按钮无底框；禁用文字按钮仍无底框。危险动作平时低权重、最终确认红色。配置开关、运行事实、健康标签分开；处理中蓝色、待确认橙色、失败红色，标签文字同时表达含义。

**兼容与边界**：不推翻 ID 独立列、5项阈值、角色显隐、平台账号关系与配置/事实分离；原稿 76 的橙色旋转示意不覆盖已确认的处理中蓝色语义。

**原稿依据**：[63-s-buttons.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/63-s-buttons.png)。

- 审核结论：□ 同意推荐　□ 修改后同意　□ 暂不采纳
- 你的批注：

### V12｜批量结果恢复原稿的视觉中心

**回写位置**：交互 §10/反馈；架构与视觉 §4.5。**影响**：中 · OperationProgressDialog。

**现状与问题**：原稿进度与结果采用居中状态图标、标题、短说明，然后是整体计数和逐项表。当前改成左对齐摘要，更像普通说明条，缺少完成或异常的视觉中心。

**推荐决定**：推荐批量现场处理使用统一居中结果摘要；普通保存仍用轻反馈。

**建议写入规范的条款**：

> 批量处理弹窗依次为：居中40–48px状态图标、18px标题、一行必要说明、同一浅底区域内的七类计数、进度（处理中）、逐项结果和恢复动作。计数不拆成七张独立卡片；总数与互斥分类一致，原因可完整读取。处理中不允许普通关闭，完成/失败/中断/待确认分别表达；失败只重试失败范围，待确认先核实。普通单字段保存不强制生成结果弹窗。

**兼容与边界**：只调整视觉和公共呈现，不加入任务中心、历史编号或固定成功数据；普通确认与批量结果共用视觉基础但不强求同一内容结构。

**原稿依据**：[76-flow-progress.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/76-flow-progress.png)。

- 审核结论：□ 同意推荐　□ 修改后同意　□ 暂不采纳
- 你的批注：

### V13｜公共能力优先做完整，再推广

**回写位置**：架构与视觉 §3.3.2、§6、§7.2；README。**影响**：高 · 组件与迁移。

**现状与问题**：只写规范或局部 CSS 无法稳定达到原稿；直接复制原型 CSS 又会建立第二套页面系统。

**推荐决定**：推荐在 TDesign 与现有 shared/ui 上完成视觉适配，公共能力验证后再接入业务页。

**建议写入规范的条款**：

> 优先扩展现有 ResourceOverlay、ResourceForm、ResourceSection、ResourceNotice、ResourceEmptyState、ResourceRowActions 和 OperationProgressDialog；必要时新增通用 ChoiceCards 与 DescriptionList。组件至少覆盖默认、焦点、选中、禁用、加载、错误、长内容、窄视口。Token 集中映射，不让每页自行覆盖库内部样式。公共变更列出所有消费者与兼容策略；涉及全站主题先审核，不自动扫描后全站替换。

**兼容与边界**：规范可面向全站；本次实施页仍先限定窗口/代理。主题与共享默认值一旦改变，需覆盖代表性既有消费者；保持业务 API、权限和运行仓边界。

**原稿依据**：[40-p-create.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/40-p-create.png)。

- 审核结论：□ 同意推荐　□ 修改后同意　□ 暂不采纳
- 你的批注：

### V14｜把视觉还原纳入验收，而不是只看测试通过

**回写位置**：架构与视觉 §8.2；AdminUI §0；README。**影响**：高 · 验收。

**现状与问题**：构建与交互测试通过只能证明代码可运行，不能证明接近原稿。少量数据、缩放整页或只截正常态也会掩盖比例问题。

**推荐决定**：推荐增加有基线、同视口、同密度、全状态的视觉验收门槛。

**建议写入规范的条款**：

> 至少在1600×1000与1366×900的CSS视口、100%缩放、相同DPR、相同角色和样例内容下对照原稿。检查列表、只读详情、短新建/编辑、长配置、卡片选择、空/失败/部分/待确认、导入和批量结果；列表同时覆盖8行、多平台账号、长名称/地址/备注。先核对比例、对齐、密度、主次与遮罩，再核对颜色和像素细节。不得以编译或单测通过替代视觉审核，不以整页缩放“压得像原稿”，也不以只测假数据证明真实业务验收。

**兼容与边界**：原截图通常为2400px宽，是导出制品；必须先识别CSS视口和DPR，不直接把位图尺寸当控件尺寸。所有偏离目标的保留项逐项列出并由人审核，不使用笼统“已适配规范”结案。

**原稿依据**：[01-w-list.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/01-w-list.png)。

- 审核结论：□ 同意推荐　□ 修改后同意　□ 暂不采纳
- 你的批注：

## 正式回写分工

| 文件 | 建议修改 | 不应承担 |
|---|---|---|
| frontend/README.md | 明确视觉基线、职责分工、PATCH/REDESIGN与验收入口 | 不复制所有尺寸和交互规则 |
| 前端架构与视觉规范.md | Token、字号、尺寸、组件模式、样式边界、视觉验收 | 不定义代理权限/任务业务事实 |
| AdminUI页面规范.md | 资源页面板、表单组织、容器选择、详情布局 | 不另写第二套配色/反馈生命周期 |
| 前端交互规范.md | 关闭、提交、键盘、选项卡、恢复、上下文保持 | 不重复控件尺寸表 |
| 用户反馈规范.md | 说明/影响/风险/阻断、紧凑反馈模式与生命周期 | 不再维护独立颜色表 |

## 公共组件落点（审核通过后实施）

| 能力 | 处理建议 | 需验证的范围 |
|---|---|---|
| ResourceOverlay | 扩展视觉预设、遮罩、标题/正文/Footer、宽度档位 | Dialog/Drawer及多层、忙碌关闭、滚动边界 |
| ResourceForm + ResourceSection | 增加字段网格和表单/详情分区外观 | 短表单、长表单、校验与权限隐藏 |
| ChoiceCards | 必要新增，封装现有Radio语义与卡片呈现 | 焦点、键盘、整卡选择、禁用和长文案 |
| DescriptionList | 必要新增，优先适配现有Descriptions | 横向键值、多列选择、长值、复制和窄屏 |
| ResourceNotice + EmptyState | 扩展轻说明、影响摘要、紧凑风险和空态 | 不重复信息，真正错误保留，恢复入口正确 |
| ResourceRowActions / StatusBadge | 复用并统一密度、禁用与语义映射 | 5项/超过5项、Loading、权限与文本可读性 |
| OperationProgressDialog | 调整视觉中心、计数与逐项结果结构 | 成功/失败/部分/中断/待确认及真实重试范围 |
| PageHeader / FilterPanel / ResourceCard | 复用模板与Token，合并重复容器边界 | 不改业务导航或自动补统计 |

## 明确不修改

本轮只交审核文档；不改正式frontend文件、不回退已提交代码、不再次改原型和评审入口、不扩展未交付业务功能。本稿批准后，规范可以面向全站，具体运行时代码与推广页面仍应另行明确；不将两页样式无条件铺到所有模块。

保留：ID独立列、5项收纳阈值、一套组件库、Cloud/Desktop共用源码、权限边界、配置与事实分离、真实结果与异常恢复。原型中的模拟数据、成功计时器不进入实际服务。

## 冲突与未确认项

需要你重点决定：V01视觉重构执行方式、V02全站Token、V03密度、V07容器折中、V08详情阅读方式、V10提示样式、V12结果视觉中心。其余项已有明确推荐，可逐项批改。不需要你重新设计技术方案。

本次“让你Review”的原因是你明确要求先审规范；草案不会自动生效。收到审批后只回写批准项，并将有争议项单独保留，不把部分同意理解成全部批准。

## 附录：视觉基线与检查范围

原HTML：`browser-proxy-design/完整视觉方案.html`。高清PNG与原型CSS用于提取视觉语言，业务有效范围继续引用既有产品与交付定义。直接查看的代表图为01、05、06、14、38、40、48、63、64、76；5张overview用于覆盖其余场景的整体一致性。

本轮只校验审核文档完整性、资源链接、可读页面和批注导出，不重跑业务构建测试；前序807项测试不是本稿规范已经实施的证据。

### 75张原图文件清单

- [01-w-list.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/01-w-list.png)
- [02-w-web.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/02-w-web.png)
- [03-w-detail-self.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/03-w-detail-self.png)
- [04-w-detail-managed.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/04-w-detail-managed.png)
- [05-w-detail-mismatch.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/05-w-detail-mismatch.png)
- [06-w-create.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/06-w-create.png)
- [07-w-create-error.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/07-w-create-error.png)
- [08-w-create-success.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/08-w-create-success.png)
- [09-w-edit.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/09-w-edit.png)
- [10-w-note.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/10-w-note.png)
- [11-w-edit-failed.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/11-w-edit-failed.png)
- [12-w-edit-partial.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/12-w-edit-partial.png)
- [13-w-mode.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/13-w-mode.png)
- [14-w-bind.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/14-w-bind.png)
- [15-w-replace.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/15-w-replace.png)
- [16-w-replace-confirm.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/16-w-replace-confirm.png)
- [17-w-mismatch.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/17-w-mismatch.png)
- [18-w-resync.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/18-w-resync.png)
- [19-w-self.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/19-w-self.png)
- [20-w-self-success.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/20-w-self-success.png)
- [21-w-unbind.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/21-w-unbind.png)
- [22-w-bind-empty.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/22-w-bind-empty.png)
- [23-w-sync.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/23-w-sync.png)
- [24-w-sync-issues.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/24-w-sync-issues.png)
- [25-w-identity.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/25-w-identity.png)
- [26-w-missing.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/26-w-missing.png)
- [27-w-uncertain.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/27-w-uncertain.png)
- [28-w-offline.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/28-w-offline.png)
- [29-w-batch.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/29-w-batch.png)
- [30-w-batch-bind.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/30-w-batch-bind.png)
- [31-w-batch-result.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/31-w-batch-result.png)
- [34-w-disable.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/34-w-disable.png)
- [36-p-list.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/36-p-list.png)
- [37-p-web.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/37-p-web.png)
- [38-p-detail.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/38-p-detail.png)
- [39-p-detail-api.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/39-p-detail-api.png)
- [40-p-create.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/40-p-create.png)
- [41-p-create-api.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/41-p-create-api.png)
- [42-p-extract.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/42-p-extract.png)
- [43-p-edit.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/43-p-edit.png)
- [44-p-edit-bound.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/44-p-edit-bound.png)
- [45-p-quota.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/45-p-quota.png)
- [46-p-quota-error.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/46-p-quota-error.png)
- [47-p-import.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/47-p-import.png)
- [48-p-import-preview.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/48-p-import-preview.png)
- [49-p-import-result.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/49-p-import-result.png)
- [50-p-checking.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/50-p-checking.png)
- [51-p-check-result.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/51-p-check-result.png)
- [52-p-batch-check.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/52-p-batch-check.png)
- [53-p-delete.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/53-p-delete.png)
- [54-p-delete-blocked.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/54-p-delete-blocked.png)
- [55-p-paused.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/55-p-paused.png)
- [56-p-expired.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/56-p-expired.png)
- [59-s-loading.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/59-s-loading.png)
- [60-s-error.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/60-s-error.png)
- [61-s-permission.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/61-s-permission.png)
- [63-s-buttons.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/63-s-buttons.png)
- [64-s-status.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/64-s-status.png)
- [65-w-senior.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/65-w-senior.png)
- [66-w-admin.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/66-w-admin.png)
- [67-w-detail-senior.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/67-w-detail-senior.png)
- [68-w-detail-admin.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/68-w-detail-admin.png)
- [69-w-accounts.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/69-w-accounts.png)
- [70-p-senior.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/70-p-senior.png)
- [71-p-admin.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/71-p-admin.png)
- [72-p-detail-senior.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/72-p-detail-senior.png)
- [73-s-roles.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/73-s-roles.png)
- [76-flow-progress.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/76-flow-progress.png)
- [77-flow-partial.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/77-flow-partial.png)
- [78-flow-interrupted.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/78-flow-interrupted.png)
- [79-flow-uncertain.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/79-flow-uncertain.png)
- [80-flow-retry.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/80-flow-retry.png)
- [85-flow-import-progress.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/85-flow-import-progress.png)
- [87-flow-failed.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/87-flow-failed.png)
- [88-flow-retry-result.png](/Users/aqiuye/.codex/visualizations/2026/10/26/01a1799f-9a86-7302-9201-4df31f7e9c3d/browser-proxy-design/screens/88-flow-retry-result.png)
