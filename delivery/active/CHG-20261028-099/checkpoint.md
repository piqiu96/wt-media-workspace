# CHG099 · 当前接续点

## 状态

- CHG099：`VERIFYING`。
- CHG107 已完成并合入本地主线。
- 代码、迁移、契约、Cloud/Agent/Desktop 自动化和 Web 页面读回已完成。
- 真实 BitBrowser 写入与目标网络尚待用户在早上 review 后指定测试资源。

## 已完成

- Cloud 收敛为 7 张运营资源领域表：`media_accounts`、`media_account_categories`、`media_account_tags`、`media_account_groups`、`browser_profiles`、`proxies`、`browser_profile_syncs`。
- 删除 `profile_sync_candidates`、`profile_sync_scans`、`proxy_configs`、`account_groups`、通用 `tasks` 与 sensitive 表。
- 启停统一 `enabled`；比特字段统一 `bit_`；平台字段统一 `platform_`；检查字段统一 `last_check_`。
- Cookie 只保留同步读取并回报链路；旧异步 `/cookies/read`、`/cloud-agent/tasks/*` 已退役。
- 代理写链路改为 Cloud 预留 + Desktop/Agent 执行 + Cloud 结算；失败清预留，可直接重试。
- 三块页面完成 Web 真实读回；Web 适配层已移除旧字段回译，统一使用 `enabled/local_state/protocol/max_profiles/platform_*`。
- 最终自动化通过：Cloud `go test ./...`、Web 90 files / 813 tests、Agent 717 tests、Desktop 540 passed / 6 ignored，Cloud/Desktop 双 build 通过。
- 最新提交：Cloud `eefc61d`、Agent `46775c7`、Desktop `815468d`；测试与构建结果见 [acceptance.md](evidence/acceptance.md)。

## 下一步

1. 用户指定不影响现有运营数据的测试窗口与可达代理目标。
2. 完成真实 BitBrowser 开/关、字段编辑、代理 apply/unbind/release 与目标网络读回。
3. 将真实结果补入 acceptance；满足后再决定完成、推送和发布。

## 阻塞

- 真实 BitBrowser 写入没有安全的测试窗口授权。
- 代理目标网络没有可用测试代理。
