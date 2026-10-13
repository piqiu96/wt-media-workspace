# CHG-20261014-090 验证记录

## 页面渲染检查

- 方法：Chrome 155 headless，1440×900，运行当前 Cloud Vite 页面；仅拦截 `/api/v1/*` 返回固定样本。截图在 `visual-fixture/`。样本不是生产数据，不用于证明真实任务、下载或发布链路。
- 期望：策略、任务、成片列表的 ID、状态、关联信息与操作可辨；任务进度不重复；操作列不被遮挡；详情按维度定位；创建任务先呈现已选素材，未选策略的错误就近显示。
- 实际：初次截图发现任务进度百分比重复，以及策略和成片操作列横向溢出；修正后再次截图，三页列表和详情符合上述布局检查。创建弹窗及字段错误见 `wt-media-chg090-create-detail.png` 和 `wt-media-chg090-create-validation.png`。
- 结果：PASS（布局与反馈样本检查）。真实数据和 Desktop WebView 操作仍属 M4-H2。

## 定向测试与构建

- `npm test -- --run src/modules/compose src/modules/materials/pages/MyMaterialsPage.test.js`：6 个文件、48 个测试通过。测试检查筛选参数、任务重试和成片接线、列表列宽约束与多素材入口。
- `npm run build:cloud`：PASS。
- `npm run build:desktop`：PASS。
- `git diff --check`：PASS。

## 差异与边界

- 仅改 Cloud 所有的共用 Vue 页面、相关样式和列数测试；无 API、数据结构、权限或任务执行变更。
- 参考图中的任务名称、批次归并、视频封面和发布记录当前没有对应业务事实，未在页面伪造。
- 创建任务仍为每条素材生成独立任务；批量部分失败改用现有 `feedback.toast.error`，避免调用不存在的 `toast.warning`。
