# 发布计划 V1 原型验收记录

日期：2026-11-13。仅本地交互原型验收，待用户视觉 Review；不代表生产执行、平台作品发布或停止能力验收。

## 结果与入口

- Cloud 当前稿：`web/example/proto/publishing-design/plan/`。旧 `/example/?view=publishing#plans` 和发布导航已转入 V1。
- [交互原型](http://127.0.0.1:8768/example/proto/publishing-design/plan/)；[40 张逐项截图图册](http://127.0.0.1:8768/example/proto/publishing-design/plan/evidence/)。
- 截图及逐项浏览器结果在 Cloud `plan/evidence/`；`browser-results.json` 有 18 项 PASS、40 张截图及空页面异常列表。
- 离线截图 ZIP 已生成并校验，包含索引、common 样式和全部原图；不携带本地业务存档。

## 实施与边界

用户提供的 ZIP 是本轮已选定设计，保留其单页新建、矩阵及批次编辑、详情与处理流程。复用 common Token、选择器、36px 控件、筛选查询/重置/已生效计数、独立 ID 表格和默认 8 条分页；使用原生 Dialog、逐层焦点返回、背景滚动锁和键盘多选。沿用现有品牌与三个发布平台。

本轮修复：复制清除执行统计；锁定行完整不可变；取消不自动放弃未知结果；重试仍阻止结束；缺口约束覆盖新增和编辑补量；拆分保持补量类型且禁止与原始批次合并；推荐大数输入先校验；已锁定种子目标与容量一致；输入失焦不会吞掉保存首击；Tab 保留下一字段，数量自动汇总；损坏存档不静默覆盖，保存失败不报成功。

独立存储 `wt-publishing-plan-v1`，未修改旧任务、批次原型存档。计划内的批次数据仍是 V1 自包含演示，通过实际入口可打开原有批次模块；不把两个模块的虚构记录称为已接通的数据关系。资源、AI、配置完成及执行反馈明确为演示。停止中保留为条件原型状态，真实执行器同步停止能力未验证。

## 验证事实

| 操作 | 实际结果 |
| --- | --- |
| `npm run test:publishing-plan` | 18 / 18，通过矩阵、锁定、拆并、复制、串行、未决结果、补量、唯一 ID、持久化及大数阻断测试 |
| `npm run test:publishing-prototype` | 13 个文件，239 / 239 通过 |
| `npm run test:example` | 22 / 22 通过 |
| Workspace `python3 -m unittest discover -s tests` | 191 / 191 通过 |
| `npm run build:example` | 通过；仍有已有公共入口大包提示 |
| 构建产物浏览器检查 | 旧入口转入 V1、新增表单、图册及 40 张图片全部返回正常，无页面异常；产物 app.js 与源码 SHA-256 一致 |
| 浏览器实际操作 | 18 项 PASS：筛选、Tab、刷新、数字汇总、多选、推荐、拆合排、校验修复、遮罩滚动锁、锁定编辑、嵌套返回焦点、链接必填、重试核实、补量边界、分页、窄屏、旧入口、存储失败 |
| 截图视觉检查 | 1600×1000、1366×900、390×844；已查看列表、目标矩阵、锁定编辑、补量抽屉与窄屏表单；表格内横向滚动，窄屏无整页横向溢出 |
| 独立只读复核 | 首轮发现的补量、推荐与弹层问题修复后复核通过，未扩大范围 |
| `git diff --check` / ZIP 完整性 | 通过 |

本轮未运行 Go Backend、Agent/Desktop、真实平台联调或 `bin/control.sh verify`；它们未改变，也不作为本原型验收依据。`chg verify --plan` 已核对默认检查建议，不将 plan 模式记录为全套运行时通过。

## Git 与交付状态

`chg start --plan` 因 Workspace 既有未提交修改拒绝切换分支。为保护用户工作，保留 Workspace `codex/publishing-design-boundaries`、Cloud `codex/publishing-interaction-closure`，通过 `chg resume` 选择本 CHG。未覆盖旧 CHG review.md、设计文档及旧截图；不切换、重置或夹带用户文件。

本地成果为 VERIFYING，待用户 Review，未推送或合并。

Cloud 本地提交：`276e245`（Add common-aligned publishing plan V1 prototype）。只包含本轮原型、导航、测试与图册，未夹带旧轮次未跟踪截图。
