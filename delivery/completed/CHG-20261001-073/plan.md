# CHG-20261001-073 实施计划

依据 [change.md](change.md) 和 [M2-G](../../milestones/M2-account-runtime.md)；当前草稿与未完成项见 [checkpoint.md](checkpoint.md)。

1. 以 `web/public/brand-mark.svg` 为唯一 Web Logo 源；登录页、顶部品牌和 favicon 使用同一资源。检查图形、品牌名“起飞”和副标题“内容运营平台”在 Cloud Web/Desktop 一致。
2. 登录页按用户参考图完成布局与响应式处理；真实登录、失败提示、替换旧会话确认、Desktop 角色限制沿用现有逻辑，不因视觉修改回退。
3. `src-tauri/icons/brand-mark.svg` 与 Web Logo 保持图形一致，由 Tauri 图标工具生成 PNG、ICNS、ICO；应用名称和窗口标题统一。版本号读取包或 Tauri 实际版本，不能复制示意图 `v1.0.0`。
4. 安装 Web 锁定依赖后完成 Cloud/Desktop 双构建、定向登录测试与小屏人工检查；准备 Sidecar 后构建原生应用，在实际 macOS Dock/窗口和可用的其他平台包中核对图标、名称、版本与登录流程。
5. 保存验证证据并由用户走查签收；与 CHG-072 共用工作树的提交要按 CHG 分开记录，不能因另一项通过就关闭本项。
