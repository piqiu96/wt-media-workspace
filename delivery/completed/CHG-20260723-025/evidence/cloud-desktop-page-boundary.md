# Task 5 evidence：Cloud Web / Desktop 页面展示边界

> 日期：2026-07-23  
> 范围：浏览器窗口页面按 Cloud Web 与 Desktop 能力边界收口

## 1. 本次事实变更

### Cloud Web

浏览器窗口页面在非 Desktop 环境下：

- 只展示 Cloud 已保存的浏览器窗口列表、详情和刷新；
- 显示提示：当前为 Cloud Web，只展示 Cloud 已保存信息；
- 不展示新建窗口；
- 不展示扫描本机窗口；
- 不展示打开/关闭/删除等本机操作入口；
- 不展示依赖 Local Agent / BitBrowser 的 Diff 处理入口。

### Desktop

浏览器窗口页面在 Desktop 环境下：

- 展示新建窗口、扫描本机窗口、打开、关闭、删除等本机操作入口；
- 扫描流程沿用 Task 4 的 Tauri/Rust/Local Agent 路径；
- 扫描结果抽屉明确提示：本次扫描只展示 Diff，不会同步或覆盖 Cloud 浏览器窗口。

### Diff 抽屉

- 移除了可点击的“仅确认主账号”和“确认同步窗口”动作。
- 将后续动作展示为禁用按钮：
  - 接受本地变化（后续）
  - 恢复Cloud配置（后续）
- 保留“取消变更”用于关闭当前只读结果。

## 2. 验证命令与结果

### Web 单元测试

命令：

```text
npm test -- profileBindings localAgentService
```

结果：PASS，4 tests。

### Cloud Web 构建

命令：

```text
npm run build:cloud
```

结果：PASS。

### Desktop Web 构建

命令：

```text
npm run build:desktop
```

结果：PASS。

### 关键词检查

命令：

```text
rg -n "触发扫描|扫描本机窗口|确认同步窗口|仅确认主账号|接受本地变化|恢复Cloud配置|127\\.0\\.0\\.1:8765" wt-media-cloud/web/src/modules/profiles/pages/ProfilesPage.vue wt-media-cloud/web/src/apps/desktop/features/local-agent
```

结果：

- 浏览器窗口页仅保留 Desktop 专用“扫描本机窗口”；
- 不再出现“确认同步窗口”；
- 不再出现“仅确认主账号”；
- 扫描抽屉只显示禁用的后续动作提示；
- 业务页未直连 `127.0.0.1:8765`。

## 3. 明确未做

- 未实现接受本地变化；
- 未实现恢复 Cloud 配置；
- 未应用 Diff；
- 未补完整页面人工截图验收；
- 未处理 B2 窗口生命周期与授权闭环。

## 4. 结论

Task 5 已完成 Cloud Web / Desktop 浏览器窗口页面展示边界收口：Cloud Web 不再暴露本机执行入口，Desktop 才承载本机扫描和只读 Diff 展示，且本 CHG 不包含的 Diff 应用动作不会误导用户点击完成。
