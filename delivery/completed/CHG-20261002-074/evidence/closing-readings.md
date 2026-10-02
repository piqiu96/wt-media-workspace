# CHG-20261002-074 关闭读数（2026-10-02）

阶段 1+2+3 代码全部落地后的自动化验证与验收 grep 读数。实机走查（迁移上真库、Desktop 重启、双会话共存实测）由用户驱动，未包含在此文件；走查完成前 CHG 不置 DONE。

## 提交对照

| 阶段 | 仓 | 提交 |
| --- | --- | --- |
| 阶段 1（client_type 解耦） | wt-media-cloud | `11ce766` |
| 阶段 2（凭据独立 + 落盘） | wt-media-cloud | `91c58e5` |
| 阶段 2（Desktop 落盘） | wt-media-desktop | `75860f7` |
| 阶段 3（dedupe 改维 + 重分配 + 重取 + 自助 + 23002/23003） | wt-media-cloud | `00028ac`（含迁移 `20261002_048_file_transfer_tasks_assigned_device.sql`，40 文件） |

## 自动化读数（最后一次代码改动之后；阶段 3 树 = 阶段 3 提交树）

| # | 命令（cwd） | 期望 | 实际 | 判定 |
| --- | --- | --- | --- | --- |
| 1 | `go build ./...`（wt-media-cloud） | 通过 | 通过 | PASS |
| 2 | `go vet ./internal/...`（wt-media-cloud） | 无告警 | 无告警 | PASS |
| 3 | `go test -count=1 ./internal/...`（wt-media-cloud） | 全绿 | 62 包 ok，0 失败（exit 0） | PASS |
| 4 | `npx vitest run`（wt-media-cloud/web） | 全绿 | 49 文件 / 457 用例通过 | PASS |
| 5 | `npm run build:cloud`（wt-media-cloud/web） | 构建成功 | 成功（仅既有 chunk 体积提示） | PASS |
| 6 | `npm run build:desktop`（wt-media-cloud/web） | 构建成功 | 成功，8.02s（仅既有 chunk 体积提示） | PASS |
| 7 | `cargo test`（wt-media-desktop，阶段 2 树 `75860f7`） | 全绿 | 505 通过（含凭据落盘回读 + 0600 权限、缺失/损坏文件视为无绑定 2 条新测） | PASS |

读数 1–4、7 在阶段 3 期间已跑过一轮（62 包 / 457 用例 / 505 条）；本文件记录的是收尾会话对同一棵树（= `00028ac` 提交树）的重跑。读数 6（`build:desktop`）为收尾会话首次补跑，补齐任务 5 的「双构建」。

## 验收 grep（change.md §4，收尾会话当场重跑，均带阳性对照）

| # | 模式（`git grep`，wt-media-cloud，排除 `web/node_modules`） | 期望 | 实际 | 阳性对照（同模式对旧提交） |
| --- | --- | --- | --- | --- |
| G1 | `ClearMainIdentity\|clearBitBrowserBinding`（代码） | 0 | 代码 0 命中；仅 `docs/superpowers/handoffs/2026-09-18-cloud-foundation-convergence-handoff.md` 1 处历史叙述（按「叙述判留」保留） | `91c58e5` 命中 `profilebinding/handler.go`×2、`store_mysql.go`×1——模式有效 |
| G2 | `invalidated_at IS NULL` | 仅会话层 + 注册闸门 | `identity/store_mysql.go` 4 处（全量失效、同类型计数/失效、Logout 自身）+ `runtimebinding/store_mysql.go:75`（binding_tickets 注册闸门），无其他 | ——（存在性检查，见 G1/G3 对照方法） |
| G3 | `n\.session_id\|JOIN user_sessions`（执行层） | 0 | 0 命中（exit 1） | `11ce766` 命中 cloudagent×1、profileguard×1、runtimebinding×4——模式有效，且命中的正是阶段 2 清理的文件 |
| G4 | `userDownloadDedupeKey` 维度 | device 维 | 键为 `user_download\|assetID\|userID\|deviceID\|generation`（store_mysql.go:237 实测，generation 计数、键哈希进 CHAR(64)）；宽模式 `dedupe.*node` 在同文件仅 1 命中＝:416 INSERT 列清单中 `assigned_node_id` 与 `dedupe_key` 相邻（任务仍如实记录执行节点属性），非 node 维去重键 | —— |

## 实机走查（待用户执行，完成前置 DONE）

- 迁移 `20261002_046`（client_type）/ `20261002_047`（node 去 session_id）/ `20261002_048`（assigned_device_id）经 `scripts/migrate.sh` 应用到真实 MySQL。
- desktop 与 web 双会话共存不互挤；同类型登录才 20010。
- 会话失效后凭据仍可 authenticate；Desktop 重启凭据仍在。
- 设备 A 领任务 → 解绑 → 设备 B 绑定后可重取；比特主账号切换后自助「以当前环境为准」；23002/23003 实发。
