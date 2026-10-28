# 最新规范落地 · 人工评审与验收证据

2026-10-28 18:24（Asia/Shanghai）。CHG-20261028-099仍为VERIFYING。本轮Task14–16已完成到可审核状态，不合并、推送或发布。

[打开30场景评审](review.html) · [完整可操作原型](../../../../../example/proto/browser-proxy/index.html) · [公共参考](../../../../../example/common/index.html) · [frontend正式规范](../../../../../docs/standards/frontend/README.md)

## 最终改动

- Workspace原型提交 `10d2e6e`：迁入75个有效场景，引用common公共资源，按实际视口渲染；短表单居中、详情自适应、行操作清晰且打开无图标。原完整HTML保留入口并转向新proto，同目录保留迁移前完整备份。未复制旧截图大包。
- Cloud行操作提交 `358d8a6`：32px热区、主要轻按钮置前、清晰蓝色次动作、加载宽度预留，回调与权限不变。实际两页最多5项，全部平铺；没有为展示规范添加虚假的第六项操作。
- Cloud公共视觉提交 `4f73ba9`：ResourceDescriptions、ResourceChoiceCards；统一Overlay/Header/Footer、表单/详情分节、轻提示/关联展开、批量结果；新Token映射TDesign并保留旧别名；导入预览复用语义状态标签。
- frontend新增已审批能力的实际实现引用；完整业务原型入口与公共参考相互引用。Cloud/Desktop复用同一Vue源码，没有Workspace运行时依赖。

## 公共变更的原因、影响和兼容

| 变更 | 原因 | 范围与兼容 | 回归证据 |
| --- | --- | --- | --- |
| Token与TDesign映射 | 代码仍沿用旧色值、重圆角和默认黑色遮罩，与已审批规范不一致 | 全站主题颜色/圆角/边框/遮罩；旧变量保留别名，官网/登录brand变量独立保留，不批量重排其他模块页面 | consumer-and-behavior-inventory.json列25个直接旧变量消费者（含定义）；生产/挖掘/用户3页截图与检查 |
| RowActions与列宽 | 原动作12px/28px太淡，主动作缺少识别 | 仅两个显式消费者；outline测量不变，text模式按真实13px/热区/间距/加载预留，打开纯文字 | 4项列宽测试；approved专项，22项既有回归 |
| Descriptions | 固定vertical双列使少字段空洞、长字段拥挤 | 两页显式接入；TDesign字段/slot保留，实际内容≥640且短字段密度足够才双列，长字段满行，full简写与布尔绑定均支持 | 4项布局测试；752/窄容器DOM、长值、复制入口与截图 |
| ChoiceCards | 普通单选与旁挂解释割裂 | 两页少量互斥选择显式接入；沿用真实model、TDesign Radio键盘/禁用 | 点击、Space与方向键改变真实表单值；短/长表单截图 |
| Overlay/Section/Notice/Progress | 空旷侧栏、重复大提示、无视觉中心结果 | 两页共用容器；默认短Dialog560、标准Drawer800、选择/结果960，空选择器560；提交busy与进度处理中阻止关闭，进度仍禁Esc，风险与结果语义保留 | 21弹层、22既有交互、新专项；390/768/1366及480低高度 |
| 筛选布局 | 多字段标签与控件拥挤，间距不统一 | 只有窗口/代理通过resource-visual-approved接入上置标签/24横距/20行距；保留真实控件根可收缩规则，其他模块原布局兼容 | DOM间距及范围检查；内容生产/挖掘旧布局回归 |

## 验证事实

| 检查 | 实际结果 | 证据 |
| --- | --- | --- |
| Vitest全量 | 89文件、811用例通过 | vitest-output.txt |
| Cloud构建 | 通过 | build-cloud-output.txt |
| Desktop共用前端构建 | 通过 | build-desktop-output.txt |
| 全部原型有效场景 | 75场景非空、无缩放、无console/pageerror | proto-results.json |
| 原型交互/旧入口 | 7项通过 | proto-interactions.json |
| 实际Vue弹层专项 | 21项通过 | overlay-verification-after.json |
| 实际Vue既有交互 | 22项通过；含导入选中项请求、互斥计数、重试、权限、窄视口，以及导入标签实际前景/背景对比度≥4.5:1 | ui-verification.json |
| 新规范实际Vue专项 | 15项通过 | approved-verification.json |
| 人工评审工具 | 30场景图片均加载；批注切换保持、JSON导出通过，无页面错误 | review-verification.json |
| 文档/差异 | 15索引校验、diff空白检查通过 | Workspace检查记录 |

构建保留既有大体积chunk提示，不属于构建失败。本轮没有修改依赖锁、Backend、数据库、跨仓Contract、Agent或Desktop Runtime。

两页script与Cloud `601238b`对比：只新增展示组件import与操作列主要动作的尺寸选项，业务函数完全一致，见consumer-and-behavior-inventory.json。运行时代码没有引入原型数据、计时器或固定成功结果。测试fixture仅用于隔离浏览器验证，不打包进入业务应用。

## 独立代码检查

独立只读review覆盖 `601238b` 至Task15及Task16工作差异，未发现Critical/Important回归。两项Minor均已处理：full空字符串标记补失败测试后修复；导入预览由实底t-tag换公共ResourceStatusBadge，保留分类/勾选逻辑并核验对比度。检查者未修改工作区，也未将实现者提供的测试结果冒充自己重跑。

## 仍需人工与真实验收

- 本轮视觉与公共组件请在review.html逐项审查；可导出JSON，不自动扩大其他模块的布局改造。
- 真实比特开关窗、修改字段后的逐项读回、代理应用与目标网络，以及完整Cloud/Agent/Desktop组合验收仍待现场完成。当前的fixture检查不能替代这些验收。
- 整体CHG保持VERIFYING；Task14–16完成不表示整单可关闭。保留两份无关未跟踪社媒报告，不纳入提交。

## 复跑

从Workspace根目录运行；需要当前Cloud web依赖、Node、Playwright与已安装Chrome。若Playwright在系统工作运行时中，用NODE_PATH指向其node_modules。serve-review.mjs只在5190启动独立当前源码服务，不更换用户5173/5174进程；fixture只注入测试浏览器页面。

```sh
node delivery/active/CHG-20261028-099/evidence/modern-ui/serve-review.mjs
node delivery/active/CHG-20261028-099/evidence/modern-ui/verify-prototype.cjs
node delivery/active/CHG-20261028-099/evidence/modern-ui/verify-proto-interactions.cjs
node delivery/active/CHG-20261028-099/evidence/modern-ui/verify-overlays.cjs
node delivery/active/CHG-20261028-099/evidence/modern-ui/verify-regression.cjs
node delivery/active/CHG-20261028-099/evidence/modern-ui/verify-approved.cjs
node delivery/active/CHG-20261028-099/evidence/modern-ui/verify-review.cjs
```

2026-10-28 17:40续接时额度恢复；一次自动化17-40已删除。低于5%保存停止条件仍适用于后续工作，本次未触及。
