# Task 2：Cloud 公开首页与下载按钮

- 命令：`npm test -- src/modules/public/downloadManifest.test.js src/apps/cloud/publicRoutes.test.js`。
- 预期：`/home` 公开，业务页仍受保护，三平台清单校验拒绝缺失和异源 URL。
- 实际：先因模块不存在失败；实现后 2 个测试文件、3 项测试通过。
- 命令：`go test ./internal/bootstrap -run TestCloudWeb -count=1`。
- 预期：Cloud 静态服务为 `/home` 返回入口、为清单路径返回 JSON。
- 实际：通过。
- 命令：`npm run build:cloud`。
- 实际：构建成功；Vite 报现有主 chunk 超过 500 kB 的体积提示。
- 人工浏览器布局与点击下载仍待集成验收。
