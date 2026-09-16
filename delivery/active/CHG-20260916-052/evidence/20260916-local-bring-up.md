# M3 本地自测环境启动证据（2026-09-16）

## 启动命令

```text
WT_MEDIA_BITBROWSER_API_URL=http://127.0.0.1:8899 scripts/m2b-local-acceptance.sh stop
WT_MEDIA_BITBROWSER_API_URL=http://127.0.0.1:8899 scripts/m2b-local-acceptance.sh all
```

## 门禁结果

- Cloud migration：PASS；固定数据库 `wt_media_cloud`，20260916_028/029/030 已应用。
- Cloud：PASS，`http://127.0.0.1:18080/api/v1/health`。
- Local Agent：PASS，`http://127.0.0.1:8765/healthz`。
- BitBrowser：PASS，Agent status 返回 `bitbrowser_status=normal`、2 个脱敏测试窗口。
- Desktop 前端：PASS，38 个资源文件，资源包含 `127.0.0.1:18080/api/v1`，构建新鲜。
- Desktop DMG：PASS，已构建并挂载 `/Volumes/WT Media/WT Media.app`。
- 登录 smoke：PASS，`admin` 登录成功。
- 走查账号 smoke：PASS，`operator01/operator01` 登录成功（team_id=1）；内容池与挖掘策略列表 API 均返回 `errcode=0`。

## 环境边界

本机未安装真实 BitBrowser，因此本轮使用仓库既有脱敏 mock（`127.0.0.1:8899`）；不代表真实 BitBrowser/M3 外部渠道验收。Douyin 真实请求仍需在 Agent 配置 `WT_MEDIA_DOUYIN_API_BASE`、`WT_MEDIA_DOUYIN_API_KEY`（可选 Cookie）后单独走查。
