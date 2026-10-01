# Task 21 证据：下载文件名改 日期/游戏名-ID-发布时间-标题名 + 修复任务 19 的 complete 400 缺陷

- 日期：2026-10-01
- CHG：CHG-20260930-069（走查反馈折入，用户裁定命名规则再改）
- 仓库：`wt-media-cloud`（Contract+Cloud）、`wt-media-agent`、本 Workspace
- 提交：Cloud `bc9f700`、Agent `c9915a3`（见文末）

## 背景

走查反馈（用户中途追加）：「下载的文件名修改 日期/游戏名-ID-发布时间-标题名」。逐条裁定：日期目录保持**下载日期**（Agent 本机时钟，如 `20261001/`，不变）；发布时间段格式 `YYYYMMDD`、分隔符统一 `-`、取不到整段省略；标题段消毒 + 截断（总名 ≤255 字节不丢后缀）；无游戏兜底 `未分类` 保持。

同链路还带着任务 19 留下的**卡死缺陷**：任务 19 把契约 `Completion.file_name` 放宽到一层子目录，但 Cloud 服务端 `service.go` 的运行时校验仍拒任何 `/` → Agent 本地下载成功、上报带 `/` 的名字 → 400「文件传输请求格式错误」→ 任务永远 `running`。新形状带日期子目录，同被卡死，必须先修。

## 三处修订号一致（契约核对）

- `contracts/cloud-agent-api/v1/file-transfer.openapi.yaml` `info.version: 2026.10.01.1`（`LocalLease` 增可选 `published_at`）
- `internal/modules/cloudagent/service/compatibility.go` `ContractRevision = "2026.10.01.1"`（`MinimumAgentContractRevision` 仍 `2026.07.14.7`）
- `wt-media-workspace/config/contract-map.yaml` `cloud_agent_api.contract_revision: "2026.10.01.1"`
- 状态：PASS（三处一致，最小兼容版本未动）

## Cloud 侧测试

- 命令：`gofmt -l internal/modules/`、`go build ./...`、`go test -count=1 ./...`
- 预期：0 FAIL；尤其 `TestCompleteTaskEnforcesTheFrozenOneSubdirectoryNamePattern`（`20261001/三角洲-31.mp4`、`a/b.mp4` 放行；`a\b.mp4`、`a/b/c.mp4`、`/abs.mp4`、`a/b.mp4/`、`a//b.mp4`、256 字节拒绝）、`TestClaimTaskCarriesTheFactsTheExecutorNeeds`（租约带 `game_name` 与 `published_at`）、`TestGetTaskScansThePublishedAtColumn`（阳性对照：有值→读出、NULL→nil）、dto 键集测试含 `published_at`。
- 实际：66 包 ok / 0 FAIL；`go build` 干净。`gofmt -l` 只报 `internal/modules/production/model/model.go`——该文件是任务 20 提交 `e940ecd` 带进来的既有未格式化（`MaterialUsage` 结构体 tag 对齐），本轮未触碰、未改，不属本任务范围。
- 状态：PASS

## Agent 侧测试（先红后绿）

- 命令（先红基线）：`PYTHONPATH=src python3 -B -X pycache_prefix=/tmp/wtmedia-pycache -m unittest tests.test_material_download_executor tests.test_download_sink tests.test_cloud_transfer_client`
- 预期（先红）：executor 默认租约带 `title="春日"`，命名形状变化后 9 个 ERROR + 4 个 FAIL（文件落点 `saved()` 找旧名、`未分类` 兜底、碰撞 `(2)`、resume 记录名全按旧平铺形状断言）。
- 实际（红）：先红如上；**且红先撞出实现 bug**——`download_sink.py` 拆分后缀时丢了扩展名圆点（`'20260930/春日-42mp4' != '20260930/春日-42.mp4'`），修平后才进入测试改写。
- 定向：`test_download_sink` 44 条 OK（新增发布段命中/省略、标题段、`#` 与全角标点保留、标题超长截断、有标题时游戏名封顶一半）、`test_material_download_executor` 55 条 OK（新增发布段端到端、无标题省略、`#` 保留端到端）、`test_cloud_transfer_client` 28 条 OK（`published_at` 可选→date、不可解析→None）。
- 全量回归：`PYTHONPATH=src python3 -B -X pycache_prefix=/tmp/wtmedia-pycache -m unittest discover -s tests -p 'test_*.py'` → `Ran 641 tests in 26.0s OK`（比任务 19 的 630 多 11，正是本轮新增）。
- 状态：PASS

## 改动

### Cloud + Contract（提交 `bc9f700`）

- 修复任务 19 缺陷：`service.go` complete 校验 `strings.ContainsAny(fileName, "/\\")` → `validCompletedFileName`（与契约 `Completion.file_name` pattern `^[^/\\]+(?:/[^/\\]+)?$` 一致：至多一层相对子目录、两段都非空、不含 `\`、拒绝对路径/两层/`.`/`..`；空名=可选键放行）。
- `migrations/20261001_044_file_transfer_publish_time.sql`：`ALTER TABLE file_transfer_tasks ADD COLUMN published_at DATETIME(6) NULL AFTER game_name;`（仿 043 风格）。
- `filetransfer` 全链路（仿任务 19 game_name）：`model.Task.PublishedAt` → `taskColumnList`/INSERT/`scanTask` 读回 → `CreateUserDownloadInput.PublishedAt` → `dto.LocalLease.PublishedAt`（可选）→ `leaseBody` 写入。
- `production/service.go` `CreateDownload`：`PublishedAt: material.PublishedAt` 带入。
- 契约：`LocalLease` 增**可选** `published_at`（format date-time，description 说明用于命名 `YYYYMMDD/<game>-<id>[-<YYYYMMDD>][-<title>].<ext>`）；`info.version` → `2026.10.01.1`；`compatibility.go` 同步。

### Agent（提交 `c9915a3`）

- `clients/cloud/transfer.py`：`TransferLease` 增 `published_at: date | None`；`parse_lease` 经 `_parse_publish_date` 宽容解析（不可解析 → None → 省略段，命名是装饰性的，不为一个日期拒绝整张租约）。
- `storage/download_sink.py`：`file_name(game_name, material_id, extension, today, publish_date=None, title=None)` → `日期/游戏名-ID[-YYYYMMDD][-标题].ext`。发布段非空才拼 `-YYYYMMDD`；标题 `_sanitize` 消毒（`<>:"/\\|?*`/控制符 → `_`，`#`/`@`/全角标点保留）+ 字节预算内 UTF-8 边界截尾；有标题时游戏名封顶 `budget//2`（标题不饿死），标题截空则整段连同 `-` 一起省略；无游戏兜底 `未分类`、碰撞 `(2)`、日期目录逻辑不变。
- `executors/material_download.py` `_prepare`：命名调用透传 `lease.published_at, lease.title`；resume 沿用旧名。

## 相关提交

- `wt-media-cloud` `bc9f700`（`feat(chg-069): 任务 21 发布时间进租约 + 修复任务 19 的 complete 400 校验`）
- `wt-media-agent` `c9915a3`（`feat(chg-069): 任务 21 下载命名加 发布时间/标题段（Agent 侧）`）
- 本 Workspace（证据 + checkpoint + change.md §5 任务 21，随本记录提交）

## 剩余（不属本任务）

- 端到端重建走查：重建 Cloud（含 044 迁移 + complete 校验放宽），**Agent 保留不重启**（避免丢节点绑定）；真实下载落 `20261001/三角洲行动-30-20260922-标题.mp4` 形状、complete 不再 400、下载中心一条「已完成」、素材页「已下载」；无发布时间的素材省略该段；标题超长截断。卡死残留两行属历史数据，验证靠新行。
