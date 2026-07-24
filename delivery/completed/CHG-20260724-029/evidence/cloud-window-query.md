# Cloud 浏览器窗口查询与只读边界验证

日期：2026-07-24

## 修改事实

- `ProfilesPage.vue` 已补充浏览器窗口列表字段：
  - 系统ID；
  - BitBrowser ID；
  - 比特序号；
  - 名称；
  - 分组；
  - 代理摘要；
  - 备注；
  - 授权用户；
  - Cloud镜像状态；
  - 最近同步时间。
- 页面新增搜索、状态筛选和分页。
- Cloud Web 仍只展示 Cloud 已保存镜像；扫描、新建、打开、关闭入口仅 Desktop 可见。
- Cloud 路由中的旧本机操作入口已改为拒绝：
  - `POST /api/v1/browser-profiles`
  - `POST /api/v1/browser-profiles/:id/open`
  - `POST /api/v1/browser-profiles/:id/close`
  - `PATCH /api/v1/browser-profiles/:id`
- 以上入口不再创建 Cloud Agent 异步任务。

## 验证

- `env GOCACHE=/Users/aqiuye/Develop/workspace/wt-media/wt-media-cloud/.cache/go-build go test ./internal/modules/profilebinding`：PASS
- `npm test`：PASS
- `npm run build`：PASS

## 结论

Cloud Web 与 Desktop 的功能边界已收紧：Cloud Web 只读，Desktop 才能执行本机 BitBrowser 操作。
