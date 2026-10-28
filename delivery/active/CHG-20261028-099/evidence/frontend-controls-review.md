# 公共参考评审：详情层级、动作、选择器与间距

时间：2026-10-28 13:42（Asia/Shanghai）。对应Task 12，依据用户四张截图反馈。修改范围为公共HTML与正式规范，未修改运行仓。

## 四项处理

| 问题 | 结论 | 已做修改 |
|---|---|---|
| 查看详情是否应再开弹窗 | 按信息量分层 | 少量关联账号在原摘要内展开；代理供应商/认证方式/到期/检测等补充信息在当前选择框内展示；完整属性和关系表才进入800px只读Drawer，返回保留筛选与选择 |
| 按钮颜色与“更多” | 降低同排动作竞争 | 详情导航保持蓝色，次要执行动作次级文字色，悬停增强，危险动作悬停/确认表达；超过5项的阈值不变；更多为独立浮动菜单，视口不足可向上展开，支持键盘与关闭恢复 |
| 下拉效果 | 统一触发器与选项层 | 共用controls.js演示：36px控件、箭头、选中浅底/勾选、活动/禁用态、单一焦点表现；Popover面板受视口约束，不被Dialog正文裁切；原始select保留数据/事件/重置语义，真实产品仍用TDesign |
| 多个搜索/筛选间距 | 修复布局并统一节奏 | 横距24px、换行纵距20px、标签间8px；宽容器同排，窄屏完整字段组换行；display:contents仅作用于local-form，不再覆盖筛选form |

正式回写：AdminUI§3.2/§6.3；架构视觉§3.7.3/§3.7.7/§4.1.4；交互§4/§5.6；用户反馈“说明、影响和风险的视觉层级”。共用脚本与起始页的引用、复用说明已同步。

## 根因与失败核验

修前浏览器实际计算：`[data-picker-search]`的display为contents；两个字段Y分别294.19和358.98，搜索被撑满、地区接在下面。仅在浏览器临时恢复该表单的flex布局并设置间距，两项Y同为316.58，验证了公共form规则覆盖局部布局的根因；随后只缩小该规则作用域。

修改前5项检查均失败：同排筛选、少量详情原位、浮动更多菜单、统一选择面板、次要动作中性色。见[失败记录](frontend-controls/red-results.json)。修后[同一组回归](frontend-controls/regression-smoke.cjs)通过，另外补充更完整的交互检查。

## 验证

| 操作 | 实际结果 |
|---|---|
| `node delivery/active/CHG-20261028-099/evidence/frontend-controls/verify.cjs` | PASS，28项；选择键盘/外点/Esc/禁用、源值同步、菜单焦点/危险确认、账号原位展开、详情层级、筛选对齐/间距、选项视口边界；0脚本错误 |
| `node delivery/active/CHG-20261028-099/evidence/frontend-examples/browser-verify.cjs` | PASS，101项；原有列表、Dialog/Drawer、内容自适应、选择保留、过程/结果、窄屏与起始页仍可用；0错误/外部请求 |
| `python3 delivery/active/CHG-20261028-099/evidence/frontend-examples/static-verify.py` | PASS，8组；37个Token一致，本地资源/ID/label与新增控件脚本无网络/自动成功计时器 |
| `python3 scripts/docs/check.py` | PASS，15 indexes |
| `git diff --check` | PASS |

Node脚本使用Playwright与本机Chrome，从Workspace根目录执行；本次使用桌面应用提供的依赖，通过NODE_PATH指定模块目录，不增加仓库构建依赖。详情原有native select数据源核验改为force读取/选择隐藏源；新的28项检查通过可见触发器与键盘/鼠标验证真实交互，未将隐藏源写值冒充选择器操作。完整结果见[专项JSON](frontend-controls/results.json)与[全场景JSON](frontend-examples/browser-results.json)。

视口为1600×1000、1366×900、390×844，DPR1、100%缩放。人工查看以下4张针对截图反馈的证据：

- [下拉与行操作](frontend-controls/select-list-1600.png)
- [更多浮动菜单](frontend-controls/more-menu-1600.png)
- [同排筛选与原位详情/账号](frontend-controls/picker-inline-1600.png)
- [窄屏筛选换行](frontend-controls/picker-390.png)

旧Task 11记录保留当时验收结论；其共用核验脚本和对应结果/截图现已更新到本轮，之前版本可由Git查看。以本轮记录判断当前参考稿。

本轮没有真实业务写入，不把HTML演示当业务验收。没有推送、合并或发布；CHG继续VERIFYING，运行时新视觉迁移与真实比特/网络验收仍待继续。
