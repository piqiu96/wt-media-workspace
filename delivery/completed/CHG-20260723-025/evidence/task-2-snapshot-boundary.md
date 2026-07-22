# Task 2 evidence：扫描输入与 Diff 数据边界

> 日期：2026-07-23  
> 范围：扫描快照字段、敏感字段边界、Diff 字段识别

## 1. 本次事实变更

### Cloud

- `ProfileInput` 接收代理摘要与备注字段：
  - `proxy_type`
  - `proxy_host`
  - `proxy_port`
  - `remark`
- `SubmitScan` 将上述字段写入候选快照。
- `changedFields` 增加代理摘要与备注变化识别。
- `profile_sync_candidates` 持久化代理摘要与备注，保证扫描结果可复查。
- 新增迁移：
  - `20260723_014_profile_sync_candidate_runtime_fields.sql`

### Web

- `profileBindings.safeProfile` 继续使用 allow-list，只提交允许字段。
- 若 Agent 返回 `status`，提交 Cloud 前映射为 `bit_status`。
- 不提交 `cookie`、`proxyPassword` 等敏感字段。

### Agent

- `test_local_profile_scan.py` 明确断言扫描响应包含运行状态与代理摘要字段。
- 继续断言响应不包含 Cookie / password。

## 2. 验证命令与结果

### Cloud profilebinding

命令：

```text
env GOROOT=/Users/aqiuye/Develop/workspace/devenv/go26/go GOPATH=/Users/aqiuye/Develop/workspace/devenv/go19/gopath GOCACHE=/Users/aqiuye/Develop/workspace/wt-media/wt-media-cloud/.cache/go-build /Users/aqiuye/Develop/workspace/devenv/go26/go/bin/go test ./internal/modules/profilebinding/...
```

结果：PASS。

覆盖：

- 扫描提交不修改正式 `browser_profiles` / binding；
- Diff 可识别名称、运行状态、代理摘要和备注变化；
- MySQL staged scan 会保存候选代理摘要与备注。

### Cloud Web

命令：

```text
npm test -- profileBindings
```

结果：PASS，3 tests。

覆盖：

- 前端提交 Cloud 的扫描快照只包含 allow-list 字段；
- Agent `status` 会规范映射为 Cloud `bit_status`；
- Cookie 和代理密码不会进入提交 payload。

### Agent

命令：

```text
python3 -m unittest tests/test_local_profile_scan.py
```

结果：PASS，3 tests。

覆盖：

- Local Agent 扫描响应包含 BitBrowser 主账号、Profile账号、运行状态、代理摘要；
- 响应不包含 Cookie 和 password。

## 3. 明确未做

- 未新增 Desktop Rust 扫描命令；
- 未修改 Desktop 页面扫描入口；
- 未应用 Diff 到 Cloud 正式 Profile 镜像；
- 未创建、编辑、打开或关闭 Browser Profile；
- 未处理媒体账号绑定影响摘要。

这些属于 Task 3～Task 5 或后续 M2-B 独立 CHG。

## 4. 结论

Task 2 的扫描输入与 Diff 数据边界已完成：Cloud 能接收并保存安全的 Profile 扫描候选字段，Diff 能表达代理/运行状态/备注变化，前端与 Agent 测试均证明敏感字段不会进入扫描快照。
