# M3 本地自测环境启动证据（2026-09-16）

## 启动命令

```text
WT_MEDIA_BITBROWSER_API_URL=http://127.0.0.1:8899 scripts/m2b-local-acceptance.sh stop
WT_MEDIA_BITBROWSER_API_URL=http://127.0.0.1:8899 scripts/m2b-local-acceptance.sh all
```

## 门禁结果

本次最新源码重启（`up --force-restart`）及复核（`verify`）均已通过；Cloud 与 Local Agent 进程以脱离终端方式持续运行，供走查使用。

- Cloud migration：PASS；固定数据库 `wt_media_cloud`，20260916_028/029/030 已应用。
- Cloud：PASS，`http://127.0.0.1:18080/api/v1/health`。
- Local Agent：PASS，`http://127.0.0.1:8765/healthz`。
- BitBrowser：PASS，Agent status 返回 `bitbrowser_status=normal`、2 个脱敏测试窗口。
- Desktop 前端：PASS，38 个资源文件，资源包含 `127.0.0.1:18080/api/v1`，构建新鲜。
- Desktop DMG：PASS，已构建并挂载 `/Volumes/WT Media/WT Media.app`。
- 登录 smoke：PASS，`admin` 登录成功。
- 走查账号 smoke：PASS，`operator01/operator01` 登录成功（team_id=1）；内容池与挖掘策略列表 API 均返回 `errcode=0`。

## 环境边界

本机未安装真实 BitBrowser，因此本轮使用仓库既有脱敏 mock（`127.0.0.1:8899`）；不代表真实 BitBrowser 验收。按 ADR-0015，M3 discovery 不使用 Agent/BitBrowser；Douyin 真实请求仍需在 Cloud 服务端配置 `WT_MEDIA_DOUYIN_API_BASE`、`WT_MEDIA_DOUYIN_API_KEY`（可选 Cookie）后单独走查。

## 本机凭据配置

为满足本机代码库内可控配置，Cloud 提供 `.env.local.example` 模板。复制为 `wt-media-cloud/.env.local` 并填入真实值即可；该文件已被 `.gitignore` 排除，启动脚本只接受 owner-only（`0600`）权限文件，命令行环境变量优先级更高。真实凭据不写入源码常量，也不进入提交历史。

## 搜索失败修复回归

- 首次失败根因：Cloud 进程早于 `.env.local` 创建，旧进程没有加载 API Key，任务错误为 `content crawler is not configured`。
- 重启后第二个根因：参考客户端要求 `/dyRank` 将 Cookie 作为 `ck` 表单字段传入，旧实现只设置了 HTTP `Cookie` Header。
- 修复提交：Cloud `0548b22`；新增回归测试断言 `ck` 字段。
- 重启 Cloud 后使用 `operator01` 执行关键词搜索，接口返回 `errcode=0`，任务 `status=success`；本次关键词上游返回 0 条结果，但已不再直接失败。
