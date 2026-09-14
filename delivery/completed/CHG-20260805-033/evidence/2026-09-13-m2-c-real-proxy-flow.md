# M2-C 本机真实写回链路验证（2026-09-13）

## 范围

仅使用两条明确标记的本机验收 Browser Profile 与一条测试结束后删除的临时代理记录；不读取或记录代理密码、Cookie、节点凭证或 BitBrowser 身份细节。

## 操作与结果

1. 用 Cloud 绑定票据注册 Local Agent 节点，并上报当前 Agent、BitBrowser 与 Profile 运行事实：通过。
2. 创建指向 `127.0.0.1:19086` 的临时 TCP 连通性夹具并执行 Cloud 代理检测：Agent 返回 `reachable`，Cloud 边界归一化为可分配状态 `ok`：通过。
3. 请求两条验收窗口的推荐：临时代理因状态正常、未过期且剩余配额为 2 而被返回：通过。
4. 调用批量绑定：两条窗口均成功；Cloud 正式关系与 BitBrowser 读回一致：通过。
5. 调用逐条解绑：Agent 显式写入 `noproxy` 并清空地址与凭据字段，BitBrowser 读回后 Cloud 清除正式关系：通过。
6. 删除临时代理并再次读取两条验收窗口：均为无代理：通过。

## 验证命令

- Cloud：`go test ./internal/modules/mediaaccount ./internal/modules/profilebinding ./internal/modules/proxy -count=1`
- Agent：`.venv/bin/python -m unittest discover -s tests`
- Web：`npm test -- --run src/proxy.test.js src/proxyOperationBoundary.test.js src/profileBindings.test.js src/mediaAccounts.test.js`

## 限制

该夹具只证明本轮合同定义的 TCP 可达性和跨端写回/读回，不等同于真实供应商代理的出口 IP、鉴权或区域能力。真实供应商代理在 M2 综合人工验收时验证。
