# T-05 证据：四仓四动词真跑（16 格：13 端到端／3 止于既有前置／0 未覆盖）

- CHG: `CHG-20260926-068`
- Task: T-05（`change.md` §8）
- 日期: 2026-09-26
- **状态：完成。** 用户授权后按 pid 停掉实况（54420／54456），5 格补跑完毕，环境留在运行态。

## 1. 口径

默认端口、默认路径、不用隔离旋钮；每仓顺序 `status(空) → start → status(活) → restart → status(活) → stop → status(空)`；
仓序 cloud → agent → desktop → workspace（workspace 的 `start` 自己起 cloud＋agent，必须排在前两仓停净之后）。
原始读数在 `artifacts/t05-*.out`（逐命令带 `exit=`，并附 pid 文件／监听／健康端点三路旁证）。
`t05-workspace-verbs.out` 约 98 KB，是**原样**留下的：workspace 的 `start`／`restart` 会把整条验收链的
vite 构建与 DMG 打包日志打出来，两个格各一遍；读数只在 `### cell`／`exit=`／`[probe]` 那几行，未做裁剪以免变成「静默省略」。

## 2. 16 格矩阵（AC-03 的计数单位＝仓×动词）

| 仓 | `status` | `start` | `restart` | `stop` |
| --- | --- | --- | --- | --- |
| cloud | **端到端** 空→`exit 1`；活→`pid=64839 alive=yes health=ok` exit 0；重启后 `pid=64919` exit 0；停后 `exit 1` | **端到端**（`go build`＋迁移，pid 64839，18080 监听＋`healthz=200`） | **端到端**（停 64839 起 64919） | **端到端**（真停：pid 文件消失、18080 监听归 0、`healthz=000`） |
| agent | **端到端** 空→`exit 1`；活→`pid=58703 alive=yes health=ok` exit 0；停后 `exit 1` | **端到端**（pid 58703） | **端到端**（停 58703 起 58731） | **端到端**（真停：58731 消失、18765 归 0） |
| desktop | **端到端**（探 5174，`alive=no health=down` exit 1，三次一致） | **止于既有前置**（`beforeDevCommand` 路径差一段） | **止于既有前置**（同因） | **止于既有前置**（无实例可停，只走"未运行"分支） |
| workspace | **端到端** 空→两行 `health=down` `exit 1`；活→两行 `health=ok` `exit 0`；停后 `exit 1` | **端到端**（迁移 `0 applied, 39 total`；真起 cloud 65668＋agent 65686，两路 200；并跑完整条验收链，见 §3） | **端到端**（停旧起新 68061／68079，`exit=0`） | **端到端**（真停：两路监听归 0，`exit=0`） |

**合计 13 端到端／3 止于既有前置／0 未覆盖 = 16。** 没有任何一格是「没跑却写成绿」。

## 3. workspace 的 `start` 跑的是完整端到端链（`t05-workspace-verbs.out`，每次 `exit=0`）

迁移 → 构建 Desktop 前端（vite，3900 modules）→ 起 cloud(18080)／agent(8765) → 验 BitBrowser（`PASS`）→
清产物 → **构建 DMG** → **挂载并启动 DMG** → 复制 dist-desktop → 验环境（Cloud `PASS`／Agent `PASS`）→
验 Desktop 资产（`fresh`／`PASS`）→ 验 DMG（`PASS`）→ 登录冒烟（`Login smoke: PASS user=admin`）。
**这同时证明 `verify_bitbrowser` 依赖的比特浏览器（pid 13947）全程未被触碰**——杀了它这条链就红。

## 4. desktop 的 3 格止于一条**既有缺陷**（`t05-desktop-verbs.out`／`t05-desktop-rootcause.out`）

`start` 真调 `cargo tauri dev`，失败在 `beforeDevCommand`：

```
Running BeforeDevCommand (`cd ../../wt-media-cloud/web && npm run dev:desktop`)
sh: line 0: cd: ../../wt-media-cloud/web: No such file or directory
Error The "beforeDevCommand" terminated with a non-zero status code.
```

**根因是量出来的**：用 `--config` 只把该命令换成打印 `pwd`（未改仓内文件、无残留进程），实测 tauri 的 cwd 是
`wt-media-desktop`（**不是** `src-tauri`）⇒ `../../wt-media-cloud/web` 多了一段，应写 `cd ../wt-media-cloud/web`。
这是 `src-tauri/tauri.conf.json` 里的**既有**缺陷（T-01 只动过 `bin/control.sh` 的模式）。
CHG-067 没看见它，因为它的 start/stop/restart 臂跑在**替身 cargo** 上——替身不理会 `beforeDevCommand`，那条路径从未被执行。
`stop` 印 "not running" exit 0（正确，但**"停"分支未被覆盖**）；无 stray cargo/tauri/vite。

## 5. 实况清场：`bin/control.sh stop` 停不掉，必须按 pid（复证 §14 第 4 项）

清场前：18080＝pid 54420（`.cache/go-build/...`，本仓 `start` 的产物但 pid 文件不在本仓记录内）、
8765＝pid 54456（`.venv/bin/python -m wt_media_agent.local_api`，ppid 1）。
cloud `status` 读作 `alive=no health=ok` exit **1**（探针答话而无 pid 文件认领）；cloud `stop` 印 "not running" exit 0 且
**54420 复查仍活**——两条 `stop` 都碰不到它们。清场由用户授权后 `kill 54420 54456` 完成：2 s 内两个 pid 消失、两端口归 0、无残留监听。
**比特浏览器 pid 13947 自始至终未触碰**（清场前后都验活）。

## 6. 一处自纠：exit 读数取错位置（错误读数未留档）

第一版 `t05-cloud-workspace-blocked.out` 里 cloud `status` 记成 `exit=0`。写法是 `out="$(cmd)"; echo "$out"; echo "exit=$?"`，
**中间那个 `echo` 把 `$?` 重置成了 0**。重测（rc 紧跟命令取值）后订正为 **exit=1**（workspace `status` 同为 1，cloud `stop` 仍 0）。
产物内已写明自纠段，旧的错误读数不留档。

## 7. 收尾读取：环境留在运行态

最后一步是 workspace 的 `restart`，`status` 逐字：

```
== Local M2-B environment status ==
cloud: pid=70220 alive=yes health=ok url=http://127.0.0.1:18080/api/v1/health
agent: pid=70244 alive=yes health=ok url=http://127.0.0.1:8765/healthz
exit=0
```

监听面：18080＝70227（`go run` 的子进程 `server`，父进程 70220 即 pid 文件记的那个）、8765＝70244、
54345＝13947（比特浏览器）；**Desktop 应用已由 DMG 启动**：pid 72068 `/Volumes/WT Media/WT Media.app`。
**怎么停**：`cd wt-media-workspace && ./bin/control.sh stop`（停 cloud＋agent；desktop 应用与 DMG 挂载需自行退出）。

## 8. 副作用如实记

- `run_migrations` 真的跑了：`migration ok: 0 applied, 39 total`（**共享 dev 库上的写**，本轮 0 条新应用）。
- DMG 被构建、挂载并启动；cloud 的 `dist-desktop` 副本被重新生成（`scripts/test.sh` 的既有链，非本 CHG 新增）。
- 实况两个 pid 已换成新值（54420→70227、54456→70244 的父子关系），原 pid 不恢复——计划已登记此项。
- 18765／5174／5173 全程无监听残留；无 stray cargo／tauri／vite。
