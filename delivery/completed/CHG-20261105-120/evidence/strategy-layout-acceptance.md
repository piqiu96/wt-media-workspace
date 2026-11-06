# 合成策略布局复查（2026-11-05）

Cloud 提交 `c36a9b4`。仅修改实际 Vue 策略页及共用策略详情，未修改 example/ 原有变更，不新增 API、数据库表或权限。

## 核对结果

| 用户问题 / 检查 | 实际结果 |
| --- | --- |
| 基础筛选顺序 | 综合搜索 → 类目 → 合成模板 → 状态；查询／重置保留公共布局。三角色实际页面检查通过。 |
| 详情基本信息 | 公共 ResourceSection / ResourceDescriptions / ResourceStatusBadge；名称整行，ID／状态、团队／类目、模板／负责人、创建／修改时间配对。抽屉标题固定“合成策略详情”，不重复放列表主操作。 |
| 执行条件 | 执行方式、数量上限与定时计划使用公共只读信息布局；选材规则表展示优先级、命中动作、条件关系和具体条件。手动不显示每日上限，定时显示每次／每日上限及计划。已配置参数按模板顺序排列；引导地址不泄露签名 URL。 |
| 执行记录 | 实际批次 ID 首列，执行时间紧邻操作；真实批次 49 的记录可见。不补造缺失批次，回归检查缺失值显示“—”、仍只对实际批次提供详情入口。 |
| 新增／编辑基本信息 | 名称整行，团队／类目、模板／负责人同序。编辑团队／类目／模板为禁用输入框；高级运营新建团队自动带入且禁用；管理员新建可选。负责人仍可调整，候选依赖团队与类目，未选类目前禁用。 |
| 添加成片设置 | 内容宽度、左对齐描边按钮“添加成片设置”；实测宽度小于 250px。添加后组数增加，抽屉滚动偏移小于 5px。 |
| 草稿与执行字段 | 修改草稿后添加规则，草稿保留、滚动偏移小于 5px；手动与定时切换正确，下次执行为禁用计算字段。测试仅操作草稿，取消时使用“不保存”，未创建或更新业务策略，未触发合成。 |
| 权限与布局 | admin／senior01 可管理，operator01 仅详情。1440／1024／768 页面未横向溢出；600px 编辑与详情单列，宽规则表只在表内横滚。全部无 JS pageerror。 |

## 验证

- Cloud/web `npm test -- --reporter=dot`：127 个文件、970 项 PASS。
- `python3 scripts/wt.py chg verify CHG-20261105-120`：Workspace 190 项、Cloud 全模块 Go 测试及其运行环境检查 PASS。
- `python3 scripts/docs/check.py`：15 个索引 PASS；`git diff --check` PASS。
- `bin/control.sh start`：由干净的 `c36a9b4` 构建共用 Desktop 前端及 macOS DMG，清单 `source_commit=c36a9b4`、`source_dirty=false`；重启后重新完成三角色页面及宽窄、手动／定时走查。
- 原生桌面启动后仍复现既有 Agent 端口交接不监听；使用标准 `local_env.py up` 恢复独立 Agent。首次复核 BitBrowser 状态请求超时，重试 `bin/control.sh verify` 全部 PASS（Cloud、Agent、Worker、合成调度、BitBrowser、双前端、DMG 新鲜度、登录烟测）。不把共用 Vue 浏览器检查冒充原生窗口逐控件签收。

## 截图

- [筛选顺序](120-strategy-filter-order.png)
- [详情基本信息](120-strategy-detail-layout.png)／[定时与选材规则](120-strategy-scheduled-detail.png)
- [编辑禁用项](120-strategy-edit-layout.png)／[高级运营新建](120-strategy-create-layout.png)
- [执行记录列顺序](120-strategy-run-order.png)
- [窄屏表单](120-strategy-editor-narrow.png)／[窄屏规则](120-strategy-rules-narrow.png)

本次为机器走查，当前 CHG 仍为 VERIFYING，等待既有 PR 审阅及用户人工视觉签收。

## 字段顺序补充（用户确认）

基本信息改为“策略名称整行 → 类目／模板 → 团队／负责人”。新增、编辑和详情同步；本次只调整现有节点顺序。策略页定向 9 项测试、文档索引及 diff 检查 PASS；实际浏览器检查新增／编辑两行坐标与详情字段顺序，无 pageerror，未保存业务数据。上文完整构建和三角色结果仍对应 `c36a9b4`，不作为这次增量的重新构建声明。

最新截图：[新建](120-strategy-fields-create.png)／[编辑](120-strategy-fields-edit.png)／[详情](120-strategy-fields-detail.png)。此前截图保留为前次验收证据，以本段顺序为准。
