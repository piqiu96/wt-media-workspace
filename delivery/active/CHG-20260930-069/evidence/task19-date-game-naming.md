# Task 19 证据：下载文件名按 日期/游戏-素材ID 命名

- 日期：2026-10-01
- CHG：CHG-20260930-069（并进任务 18/19，用户裁定）
- 仓库：`wt-media-cloud`（Contract+Cloud）、`wt-media-agent`、`wt-media-desktop`、本 Workspace
- 提交：见文末

## 背景

走查反馈④（用户中途追加）：下载文件名要按 日期/游戏-素材ID，而不是 `<标题>-<素材ID>.<ext>`。这是 Contract 变化（`LocalLease` 增可选 `game_name`、`Completion.file_name` 放行一层相对子目录、撞 `contract_revision`）。用户裁定的形状：`20260930/三角洲行动-30.mp4`（日期目录不带横杠，文件名保留横杠）；无游戏兜底 `未分类-30.mp4`（实测 149 素材中 2 个无 `game_id`）；日期取下载日期（Agent 本机时钟，租约不带日期字段）。

## 三处修订号一致（契约核对）

- `contracts/cloud-agent-api/v1/file-transfer.openapi.yaml` `info.version: 2026.09.30.1`
- `internal/modules/cloudagent/service/compatibility.go` `ContractRevision = "2026.09.30.1"`（`MinimumAgentContractRevision` 仍 `2026.07.14.7`）
- `wt-media-workspace/config/contract-map.yaml` `cloud_agent_api.contract_revision: "2026.09.30.1"`（顺带消掉 map 与代码既有的漂移，`minimum_agent_contract_revision` 不变）
- 状态：PASS（三处一致）

## Cloud 侧测试

- 命令：`gofmt -l internal/modules/`（空）、`go test ./...`
- 预期：66 包 ok / 0 FAIL，尤其 `TestLeaseAndTerminalMatchTheFrozenExecutorContract`（LocalLease 增 game_name 后键集仍与契约一致）、production `CreateDownload` 带游戏名解析、repository INSERT/列/参数全对齐。
- 实际：`gofmt -l` 空；66 包 ok / 0 FAIL。中途 11 条 sqlmock 失配（INSERT 列/参数/`taskDefaults`）逐条修平。
- 状态：PASS

## Agent 侧测试（先红后绿）

- 命令：`PYTHONPATH=src python3 -B -X pycache_prefix=/tmp/wtmedia-pycache -m unittest tests.test_download_sink tests.test_material_download_executor tests.test_transfer_source tests.test_transfer_runner tests.test_cloud_transfer_client`
- 预期：`file_name` 旧签名（title 单参、无日期）与旧平铺形状全红——新断言按 `20260930/三角洲行动-42.mp4` 形状书写；executor 命名断言、`未分类` 兜底、记录形状（恰好一段 `/`）、`parse_lease` 的 game_name 缺省都先红。
- 实际：先红（`file_name` 签名变更是整组红、executor 命名/记录断言红、`test_a_collision_suffix...` 因子目录未建红），实现后定向 129 条 OK。
- 全量回归：`PYTHONPATH=src python3 -B -X pycache_prefix=/tmp/wtmedia-pycache -m unittest discover -s tests -p 'test_*.py'` → `Ran 630 tests in 26.0s OK`（比任务 18 的 625 多 5，正是本轮新增：日期子目录命中、未分类兜底、带子目录碰撞、带子目录提交、parse_lease game_name）。
- 状态：PASS

## Desktop 侧测试

- 命令：`cargo test`（cwd = `src-tauri/`）
- 预期：`file_name_of` 放行一层子目录后，`a_path_is_not_a_name` 的组边界更新（`sub/secret.mp4`、`~/secret.mp4` 移到「被查」组，`a/b/secret.mp4`、`20260930/../secret.mp4` 进「拒绝」组）；新增日期子目录命中、链接子目录拒绝、文件形子目录、带子目录搬移四用例。
- 实际：`test result: ok. 497 passed; 0 failed; 6 ignored`（saved_files 定向 70 条全绿）。
- 状态：PASS

## 改动

### 契约 + Cloud（`wt-media-cloud` 提交 `6928291`）

- `contracts/cloud-agent-api/v1/file-transfer.openapi.yaml`：`LocalLease` 增**可选** `game_name`（string，说明用途与回落）；`Completion.file_name` `pattern: '^[^/\\]+$'` → `'^[^/\\]+(?:/[^/\\]+)?$'`；`info.version` `2026.09.30.1`。
- `migrations/20260930_043_file_transfer_game_name.sql`：`ALTER TABLE file_transfer_tasks ADD COLUMN game_name VARCHAR(64) NULL AFTER asset_title;`（仿 042 风格）。
- `internal/modules/production/service/service.go`：`Service` 增 `resolveGame` 字段（默认接 `identityservice.ResolveGame`，测试可 stub）；`CreateDownload` 把 `material.GameID` 解析出的游戏名经 `GameName` 传入 filetransfer；查不到/为空 → `""`（Agent 兜底 `未分类`），命名失败不阻塞下载。
- `internal/modules/filetransfer/{service,repository,model,dto}`：`CreateUserDownloadInput.GameName` → `createTask` INSERT 增列 → `model.Task`/`dto.Task` 可选 `GameName` → `leaseBody` 写入 `LocalLease.GameName`；`taskColumnList` 增 `game_name`。
- `internal/modules/cloudagent/service/compatibility.go` + `compatibility_test.go`：`ContractRevision` → `2026.09.30.1`。

### Agent（提交 `8eb30b0`）

- `storage/download_sink.py`：`file_name(game_name, material_id, extension, today)` → `<YYYYMMDD>/<消毒后游戏名>-<素材ID>.<ext>`，日期前缀 9 字节计入 `MAX_NAME_BYTES` 预算；`commit` 对 `final.parent` 自建目录（并在 fsync 集合中带上它）。`allocate` 的碰撞后缀在子目录内生效（`20260930/三角洲行动-30 (2).mp4`）。
- `executors/material_download.py`：`_prepare` 用 `lease.game_name or UNCLASSIFIED_GAME("未分类")`、`lease.asset_id`、`self._today()`（新注入 `today: Callable[[], date] = date.today`，可测）命名；resume 沿用旧名。
- `clients/cloud/transfer.py`：`TransferLease` 增可选 `game_name`（缺省 `""`），`parse_lease` 透传。

### Desktop（提交 `909d582`）

- `saved_files.rs`：`file_name_of` 从「恰一个路径组件」放宽为「至多一个子目录 + 一个组件」，逐段按 `Path::components` 校验（拒绝 `.`/`..`/根/驱动前缀/两层以上，`\` 按平台语义）；`entry_in` 对 `subdir/name` 下钻一层，子目录必须是真目录（`symlink_metadata` 拒绝链接子目录，防逃逸）；`move_one` 在目标自建日期子目录。`Located.directory` 保持保存根目录（`current` 语义不变），打开/定位用含子目录的完整路径 → `containing_dir` 即打开 `…/20260930/`。

## 相关提交

- `wt-media-cloud` `6928291`（`feat(chg-069): 任务 19 下载按 日期/游戏-素材ID 命名（契约+Cloud 侧）`）
- `wt-media-agent` `8eb30b0`（`feat(chg-069): 任务 19 下载落盘按 日期/游戏-素材ID 命名（Agent 侧）`）
- `wt-media-desktop` `909d582`（`feat(chg-069): 任务 19 保存目录扫描支持一层日期子目录（Desktop 侧）`）
- 本 Workspace（证据 + checkpoint + contract-map 修订，随本记录提交）
