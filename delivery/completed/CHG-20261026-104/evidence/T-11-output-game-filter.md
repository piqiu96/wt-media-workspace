# T-11 成片游戏筛选与游戏列

日期：2026-10-27

## 用户反馈

用户走查第 7 项：成片管理需要新增游戏筛选，并在列表展示游戏。

## 修订

| 层 | 文件 | 修订 |
| --- | --- | --- |
| 服务入参 | `internal/modules/production/service/output.go` | `ListComposeOutputsInput` 新增 `GameID`；service 校验 trim 后不超过 32 字符（超长返回 `ErrComposeOutputInvalid` → 400）；普通运营指定非本人负责游戏返回 `ErrComposeOutputForbidden` → 403，不静默放宽；合法时 `filter.GameIDs = []string{GameID}`；未指定时保留原角色范围（普通运营仍取本人负责游戏） |
| Handler | `internal/modules/production/output_handler.go` | 解析 `game_id` 并传入 input |
| API 客户端 | `web/src/shared/api/compose.js` | `listGames(filters = {})` 转发 `keyword/status/scope`；成片页用 `{scope:'all'}` 取名称字典、`{scope:'all',status:'enabled'}` 取筛选项 |
| 页面 | `web/src/modules/compose/pages/MyOutputsPage.vue` | 筛选新增 `game_id`；`gameFilterOptions` 取启用游戏，普通运营再与本人 `game_ids` 取交集；列表新增“游戏”列（来源素材列后）；请求带 `game_id`；`reset()` 清空；游戏名回退 ID |
| 合同 | `contracts/cloud-api/v1/content-production.openapi.yaml` | `version: 2026.10.27.1`；`/api/v1/compose-outputs` 增加 `game_id`（maxLength 32、只收窄）与 403 说明；修正“高级运营默认本人负责”的过期描述 |
| Workspace 合同映射 | `config/contract-map.yaml` | `cloud_api.contract_revision: "2026.10.27.1"`，注释登记本次变更 |

Business Schema、错误码文件未改。

## 自动验证

### Cloud Go

命令（Cloud 仓根）：

```text
go test ./internal/modules/production/service -run 'Uncertain|OutputsNarrows' -v -count=1
go test ./...
```

读数：

```text
--- PASS: TestListComposeOutputsNarrowsByGameWithoutWideningTheScope
ok  	.../internal/modules/production/service
go test ./...  ok=72 fail=0 no_test_files=11
```

`TestListComposeOutputsNarrowsByGameWithoutWideningTheScope` 覆盖：

- 普通运营选本人负责游戏：收窄为 `GameIDs=[该游戏]`；
- 普通运营选非本人负责游戏：403，且未调用存储；
- 普通运营不选游戏：保留本人负责游戏；
- 高级运营/管理员选任意游戏：按所选游戏收窄；
- 33 字符 `game_id`：400，且未调用存储。

### Vitest（`web/` 下）

```text
npm test -- --run
```

实际：80 文件 / 736 用例通过。`MyOutputsPage.test.js` 断言游戏筛选、`game_id` 请求参数、重置、游戏列位置、`gameFilterOptions` 交集、两次 `listGames` 调用；`ListPageConventions.test.js` 成片列数 10→11；`compose.test.js` 断言 `listGames` 无参调用与 `?status=enabled&scope=all`。

### 合同

```text
python3 scripts/verify/verify_m0_config.py
```

实际：`Workspace config verification ok`（Workspace 仓根）。

### 真实 HTTP 读数（2026-10-27 02:29，operator01，团队 1，负责 `hy,sjz`）

旧 API 进程仍是改动前的二进制，首次探测 `game_id=other` 返回 200 且条数不变；停止该进程后用当前代码重启（`bin/control.sh start`，pid 66952），复测：

```text
GET /api/v1/compose-outputs?game_id=hy     -> 200，1 条，game_id 全部为 hy
GET /api/v1/compose-outputs?game_id=other  -> 403，errcode 15215（compose_output_forbidden）
```

`other` 已停用且不在 operator01 的负责游戏里；服务端拒绝而非静默放宽。这同时证明运行中的 API 已是本次构建，而不是旧二进制。

## 覆盖边界

- 已验证：服务端参数校验、角色收窄、超长 400、越界 403；页面参数/列/选项源码。
- 待用户走查：A8、B4、C5 的真实页面筛选、清空与游戏列显示（停用游戏 `other` 的成片名称回退 ID）。
- 未覆盖：跨团队 `game_id` 组合的服务端口径由既有团队授权用例覆盖，本次未新增真实 HTTP 读数；走查以团队 1 数据为准。

## 用户复走查结果（2026-10-27，通过）

- 成片管理页出现游戏筛选，选项为启用游戏；列表新增游戏列（来源素材列后）。
- 清空负责人再筛选不报错；普通运营只看到本人负责游戏的成片。
- 结论：用户确认 T-11 的筛选、列和清空守卫在真实页面成立。
