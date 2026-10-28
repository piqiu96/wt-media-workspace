# 行操作层级原型修改验收

时间：2026-10-28 14:15（Asia/Shanghai）。Task 13，依据用户明确确认“按照推荐规范进行修改原型”。本次决定覆盖Task 12的灰色次操作建议。

## 已落地

- 窗口列表8行与基础示例2组：打开置前，浅蓝底/品牌蓝/播放标识，32px热区；通过显式 `ex-row-primary` 标记主要任务，不按文案猜测业务优先级。
- 详情、编辑、设置代理使用清晰品牌蓝，悬停浅蓝底；文字按钮补足点击区域，行间距8px；更多品牌蓝、32px热区，浮动菜单保持可操作。
- 停用默认主文字色，悬停语义红色浅底，最终确认仍危险按钮；禁用独立浅灰与真实不可点击。5项门槛不变。
- 架构视觉§3.7.3/§3.7.7、公共复用说明同步；现有灰色断言更新为最新审批规则。页面级实心主按钮、业务事件、权限与本地演示边界未改变。

参考上轮已核对的[Ant Design按钮层级](https://ant.design/components/button/)与[Carbon表格操作](https://carbondesignsystem.com/components/data-table/usage/)原则，具体颜色、尺寸和5项门槛取本地已确认规范，不复制外部阈值。

## 核验事实

修改前5项失败，见[RED结果](row-action-priority/red-results.json)：首位主动作、浅底/热区、蓝色次动作、悬停底、危险默认色。修改后[专项结果](row-action-priority/results.json)13项PASS，含1366与390视口无页面溢出、5项平铺、菜单执行与焦点恢复、禁用和0脚本错误。

执行：从Workspace根目录运行 `node delivery/active/CHG-20261028-099/evidence/row-action-priority/verify.cjs`（Playwright与本机Chrome，依赖经NODE_PATH指定）。原型全场景脚本101项PASS，控件专项28项PASS，0错误/外部网络请求；静态核验8组（37个Token一致）、文档校验15索引、diff空白检查PASS。既有核验截图与JSON同步到本轮，历史由Git保留。

人工核对：[列表1600](row-action-priority/list-1600.png)、[两组操作1600](row-action-priority/actions-1600.png)。DPR1、100%缩放；检查主要动作、蓝色可用动作、危险/禁用对比、完整热区与操作列未遮挡。图片为必要核验，不批量导出原型全部页面。

未修改运行仓，未推送/合并/发布。CHG仍VERIFYING；本轮交付公共原型与规范，实际业务页面新视觉迁移与真实比特/网络验收尚待继续。
