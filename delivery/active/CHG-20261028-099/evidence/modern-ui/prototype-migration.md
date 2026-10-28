# Task14 原型迁移验证

2026-10-28。范围：Workspace静态业务原型，不连接业务服务。来源与SHA见 `example/proto/browser-proxy/source-manifest.json`；只复制有效场景引擎/必需资源。

- 运行verify-prototype.cjs：75有效场景逐一渲染，全部非空、transform:none，console/pageerror为0，见proto-results.json。
- 运行verify-proto-interactions.cjs：原HTML入口场景参数、短表单560、排除未接入比特标签、选择卡、公共选择器源值、本地创建结果、详情导航、1366/768视口，7项通过，见proto-interactions.json。
- 图像：proto-create.png、proto-window-list.png，已人工查看比例/密度；实际视口渲染，表格内部可滚动。
- 原外部完整HTML已变成保留query/hash的最新入口；原制品备份在同目录“完整视觉方案-迁移前备份.html”。旧源文件不动。
- 原型保持明确演示，不构成真实窗口/代理写入、权限或比特执行验收。Task15–16与真实业务验收另外记录。
