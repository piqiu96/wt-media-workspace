# 人工验收环境启动记录

日期：2026-07-25

## 启动事实

- Cloud MySQL migration：
  - `scripts/migrate.sh`
  - 结果：PASS，`migration ok: 0 applied, 16 total`
- Cloud API：
  - 地址：`http://127.0.0.1:18080`
  - 健康检查：`GET /healthz` 返回 `ok`
  - 运行方式：前台长会话，避免后台进程被执行环境回收
- Desktop Web：
  - 地址：`http://127.0.0.1:5174/`
  - 模式：`vite.config.desktop.js`
  - 健康检查：首页 HTML 可访问
- Local Agent：
  - 地址：`http://127.0.0.1:8765`
  - 健康检查：`GET /healthz` PASS
  - 状态检查：`GET /api/v1/status` PASS
- BitBrowser：
  - `bitbrowser_status`：`normal`
  - `main_user_id`：`2c9bc06191effa4e0191f9589996619f`
  - 读回窗口数量：37

## 人工验收入口

```text
http://127.0.0.1:5174/
```

建议验收链路：

```text
扫描窗口 → 处理 Diff → 新建窗口 → 打开/关闭窗口
→ 新增账号 → 绑定窗口 → 单项检查/同步
→ 多选账号批量检查/同步 → 失败项重试
```

## 备注

- 本次未使用 mock BitBrowser；Local Agent 已连接真实 BitBrowser Local API。
- FFmpeg 状态为 `not_installed`，不影响 M2-B 浏览器窗口和媒体账号验收。
