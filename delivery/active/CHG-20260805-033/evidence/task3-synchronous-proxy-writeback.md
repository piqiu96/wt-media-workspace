# Task 3：同步代理写入与读回

## 变更事实

- Agent-owned Local Agent API `2026.09.04.1` 新增 `POST /api/v1/proxy-mutation`：写入 BitBrowser Profile 后扫描读回；响应只含协议、地址、端口和 `readback=true`，凭据仅写入请求体。
- Cloud 的 `POST /api/v1/proxies/{proxy_id}/assign` 改为同步调用 Agent。只有 Agent 读回的 Profile、协议、地址和端口均与目标代理一致，Cloud 才写入 `browser_profiles.proxy_id` 和镜像代理字段。
- 统一容量按正式 `proxy_id` 关系统计，代理列表展示已用/剩余；已绑定其他代理的 Profile 被拒绝，留待 Task 4 的更换流程处理。
- Cloud 与 Agent 形式化 OpenAPI 均已补齐为兼容性新增；无生成消费者。

## 验证

- Agent 失败测试：新增端点前 `test_proxy_mutation` 因方法不存在失败；实现后 `python3 -m unittest discover -s tests -v` 76 项通过。
- Cloud 失败测试：新增类型和正式关系前 `TestAssignWritesThroughAgentThenBindsReadbackProfile` 编译失败；实现后 `go test ./internal/modules/proxy ./internal/modules/profilebinding -count=1` 通过。
- Web：`npm test -- --run` 41 项通过；`npm run build:cloud`、`npm run build:desktop` 通过。

## 未替代的验收

真实代理分配、读回、更换和解绑仍需要可写且可验证的真实代理资源；本记录不将 mock/单元测试替代为外部真实效果。
