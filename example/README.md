# 视觉参考与业务原型

本目录保存可直接在浏览器打开的 HTML 制品。正式规则仍由 [frontend 规范](../docs/standards/frontend/README.md)维护，本目录展示规则，不建立第二套规范，也不参与业务运行。

| 目录 | 用途 | 入口 |
|---|---|---|
| `common/` | 跨业务公共视觉与交互：布局、容器、字段、控件、反馈、过程结果 | [打开公共参考](common/index.html) · [复用说明](common/README.md) |
| `proto/` | 具体需求的业务原型：组合公共模式，表达流程与信息关系 | [原型约定](proto/README.md) · [起始页](proto/starter.html) |

直接打开HTML即可，无需安装、构建、联网或启动业务服务。建议在1600×1000与1366×900的CSS视口、100%缩放下查看；另检查窄容器与键盘操作。

`common` 供 `proto` 引用；`common` 不依赖任何业务原型。新原型使用 `proto/<业务主题>/index.html`，从当前公共参考复制所需结构，并用相对路径引用公共资源，避免每份原型维护一套颜色和尺寸。完整约定见各目录说明。

## 当前稿保留

本目录只保存最终可操作稿及必要资源；中间截图、测试脚本、日志、缓存和多版本副本不进入example或CHG evidence。具体边界统一遵循[最终制品保留原则](../docs/standards/文档与知识事实治理规范.md#21-最终制品保留原则)。当前业务原型见[浏览器窗口与代理](proto/browser-proxy/index.html)、[内容运营完整工作台](proto/content-operations/index.html)。

当前社媒账号业务稿见[社媒账号](proto/social-accounts/index.html)。

内容生产、发布管理、作品管理和互动管理已合并到 [content-operations](proto/content-operations/README.md)。[逐页评审稿](proto/content-operations/review.html#page-review)按页面与 Tab 列出功能问题及建议，支持人工补充、逐页结论和导出交接；综合依据与历史意见保留在同一入口。
