# M2-B～M2-E 完整实施计划

> 用户已确认：先完成完整 M2，再进行一次统一人工验收。

## 执行规则

- 继续沿用 `CHG-20260721-020` 的可信验收基础，不关闭 M2-A 的人工门禁，不虚报完成。
- M2-B、M2-C、M2-D、M2-E 各自独立提交、测试和证据；最终统一验收。
- 真实 Cookie、短信 Token、代理密码只通过临时进程环境或交互输入传递，不写入仓库、日志或证据。
- 任何外部写入都必须先做 Cloud 授权、任务化执行、BitBrowser 读回和审计。

## 阶段一：M2-B 媒体账号与 Profile

1. 梳理当前 Profile 路由和 Cloud 任务模型，移除 create/open/close/update 的占位成功响应。
2. 增加 Profile mutation typed tasks、Agent executor、读回验证和不确定结果状态。
3. 完善扫描 Diff、保护 Cloud-owned operational fields、确认/恢复分支。
4. 补齐账号检查、身份状态更新、批量项目状态与重试历史。
5. 完成 Cloud/Agent/Web 自动化验证。

## 阶段二：M2-C 代理与 Profile

1. 代理文本/CSV/TXT/XLSX 导入与逐行校验、脱敏预览。
2. Agent 真实连通性与协议检查、Cloud 结果回写。
3. 平台默认配额、代理配额、分配预览和容量校验。
4. Profile 代理写入、BitBrowser 读回、部分成功与不确定结果。

## 阶段三：M2-D Cookie 与开户

1. Cookie 结构化解析、写入/读回、脱敏展示和授权导出审计。
2. 批量开户的逐项状态、成功项保留、失败项精确重试。
3. SMS 轮询适配器与人工验证码交接，不持久化一次性验证码。
4. 账号身份检查、媒体账号正式状态更新和容量预检。

## 阶段四：M2-E Desktop 与综合安全

1. Sidecar 启停、健康、状态事件、日志和清理闭环。
2. Web/Desktop 真实任务进度、错误、恢复状态。
3. Cloud/Agent/Desktop/BitBrowser 重启与中断恢复。
4. 全量 M2 矩阵、治理验证、跨仓契约和最终人工验收证据。

## 完成门槛

- 所有自动化测试和构建通过。
- 真实 MySQL、BitBrowser、代理、Cookie/SMS（适用路径）和 Sidecar 证据齐全。
- 64 项 M2 矩阵全部 PASS 后，才将 M2 标记为 VERIFYING 并通知用户统一验收。
