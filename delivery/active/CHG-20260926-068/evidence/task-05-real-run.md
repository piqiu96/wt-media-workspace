# T-05 证据：四仓四动词真跑（16 格，8 格端到端／3 格止于既有前置／5 格未覆盖）

- CHG: `CHG-20260926-068`
- Task: T-05（`change.md` §8）
- 日期: 2026-09-26
- **状态：未完成。** 6 格被实况实例占用阻塞，等用户授权按 pid 停掉它们后才能跑（见 §5）。

## 1. 口径

按计划：默认端口、默认路径、不用隔离旋钮；顺序 `status(空) → start → status(活) → restart → status(活) → stop → status(空)`；
仓序 cloud → agent → desktop → workspace。原始读数在 `artifacts/t05-*.out`（4 个文件，逐命令带 `exit=`）。

## 2. 16 格矩阵（AC-03 的计数单位＝仓×动词）

| 仓 | `status` | `start` | `restart` | `stop` |
| --- | --- | --- | --- | --- |
| cloud | **端到端**（探针打到活实例，`alive=no health=ok` exit **1**） | 未覆盖 | 未覆盖 | **端到端**（真跑，但对象为空：印 "not running" exit 0，pid 54420 未被停到） |
| agent | **端到端**（空→`exit 1`；活→`pid=58703 alive=yes health=ok` exit 0；停后→`exit 1`） | **端到端**（pid 58703，exit 0） | **端到端**（停 58703 起 58731，exit 0） | **端到端**（真停：58731 消失、18765 监听归 0，exit 0） |
| desktop | **端到端**（探针打 5174，`alive=no health=down` exit 1，三次一致） | **止于既有前置** | **止于既有前置** | **止于既有前置**（无实例可停，只走到"未运行"分支） |
| workspace | **端到端**（探 18080＋8765 两个活实例，两行 `health=ok`，exit **1**） | 未覆盖 | 未覆盖 | 未覆盖 |

**合计 8 端到端／3 止于既有前置／5 未覆盖 = 16。** 没有任何一格是「没跑却写成绿」。

## 3. agent：4/4 端到端（`artifacts/t05-agent-verbs.out`）

`status`(空, exit 1) → `start`(58703, exit 0) → `status`(`alive=yes health=ok`, exit 0) → `restart`(停 58703／起 58731, exit 0) →
`status`(exit 0) → `stop`(exit 0) → `status`(空, exit 1)。日志尾见 `local API listening on 127.0.0.1:18765` 与 SIGTERM 收尾。
**实况 8765 上的 pid 54456 在这 7 步前后都验活**：agent 的本仓端口是 18765，不碰它。
副作用：陈旧 pid 文件 `75067` 被 `stop` 清掉（计划 §7 第 4 项已登记）；18765 归零，无残留。

## 4. desktop：`start`／`restart` 止于一条**既有缺陷**（`t05-desktop-verbs.out`／`t05-desktop-rootcause.out`）

`start` 真调 `cargo tauri dev`（用 `HTTPS_PROXY` 仅本次调用），失败在 `beforeDevCommand`：

```
Running BeforeDevCommand (`cd ../../wt-media-cloud/web && npm run dev:desktop`)
sh: line 0: cd: ../../wt-media-cloud/web: No such file or directory
Error The "beforeDevCommand" terminated with a non-zero status code.
```

**根因是量出来的，不是猜的**：用 `--config` 只把 `beforeDevCommand` 换成打印 `pwd`（未改任何仓内文件、无残留进程），
实测 tauri 的 cwd 是 `wt-media-desktop`（**不是** `src-tauri`）⇒ `../../wt-media-cloud/web` 多了一段，
应写 `cd ../wt-media-cloud/web`。这是 `src-tauri/tauri.conf.json` 里的**既有**缺陷（T-01 只动过 `bin/control.sh` 的模式）。
CHG-067 没看见它，因为它的 start/stop/restart 臂跑在**替身 cargo** 上——替身不理会 `beforeDevCommand`，那条路径从未被执行。

`stop` 印 "not running" exit 0（正确，但**"停"分支未被覆盖**）；三次 `status` 一致；无 stray cargo/tauri/vite，5174／5173 均无监听。

## 5. 未覆盖的 5 格（＋cloud `stop` 的空转）：实况占用，等授权

`artifacts/t05-cloud-workspace-blocked.out`。18080＝pid **54420**、8765＝pid **54456** 是 09-25 起、**不在本仓 pid 文件记录内**的实例
（§14 第 4 项）。因此：

- cloud `status` 走通并**正确暴露了那条不对称**：`alive=no health=ok` exit **1**——探针答话，但没有 pid 文件认领它；
- cloud `stop` 印 "not running" exit 0，**pid 54420 复查仍活**（该格因此不是"端到端停"）；
- cloud `start`／`restart` **未跑**：`do_start` 会往被占的 18080 再绑一次，必然起不来，读数是阻塞的产物而非入口的读数；
- workspace `start`／`restart`／`stop` **未跑**：harness 的 `start_cloud`／`start_agent` **先探活再复用**，
  在 18080／8765 被占时会读成 "reuse"、什么都不起——那个读数会**冒充**计划里的实验。

**要跑这 6 格必须先按 pid 停掉 54420／54456**（`bin/control.sh stop` 停不掉，见 §14 第 4 项）。
按 pid 杀被本会话的自动权限分类器拒绝：那两个进程不是本会话创建的，而"杀掉它们"的指令只存在于压缩摘要里，
不构成用户同意。**已停下等用户明示点名这两个 pid。** 比特浏览器（pid 13947，54345）自始至终未触碰。

## 6. 一处自纠：exit 读数取错位置（错误读数未保留）

第一版 `t05-cloud-workspace-blocked.out` 里 cloud `status` 记成 `exit=0`。写法是 `out="$(cmd)"; echo "$out"; echo "exit=$?"`，
**中间那个 `echo` 把 `$?` 重置成了 0**。重测（rc 紧跟命令取值）后订正：cloud `status` **exit=1**、workspace `status` **exit=1**，
cloud `stop` 仍 0。产物内已写明自纠段，旧的错误读数不留档。

## 7. 副作用如实记

- agent 的 `start`／`restart` 会起真实进程，已全部停净（18765 归零）。
- cloud 的 `run_migrations` 本应写共享 dev 库——**本轮 6 格未跑，因此这次没有发生**（若授权后跑，会写）。
- desktop 的 `start` 未走到 vite(5174) 与开窗那一步（止于 `beforeDevCommand`）。
- 实况 54420／54456 未被触碰，pid 值未变。
- **环境当前不在"计划要求的运行态"**：计划要求收尾由 workspace 的 `restart` 把环境拉起来。这一步没做，
  但实况 cloud(18080)＋agent(8765) 仍在答话，与外部观感一致。
