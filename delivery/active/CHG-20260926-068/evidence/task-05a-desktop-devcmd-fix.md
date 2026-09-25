# T-05A 证据：修 desktop `beforeDevCommand` 少写的一段路径（T-05 查出、用户裁定「修了」）

- CHG: `CHG-20260926-068`
- Task: T-05A（`change.md` §8；**T-05 之后新增**，§5 Modify 末条为本次扩范围）
- 日期: 2026-09-26
- 运行仓提交：**desktop `b0ae3c3`**

## 1. 缺陷与改动

```diff
  "build": {
    "frontendDist": "../.generated/frontend",
    "devUrl": "http://127.0.0.1:5174",
-   "beforeDevCommand": "cd ../../wt-media-cloud/web && npm run dev:desktop",
+   "beforeDevCommand": "cd ../wt-media-cloud/web && npm run dev:desktop",
    "beforeBuildCommand": "bash scripts/prepare-release-sidecar.sh && bash ../wt-media-workspace/scripts/build-desktop.sh"
  },
```

**一行、一段路径。** 原值让 dev 模式一启动就死在
`Error The "beforeDevCommand" terminated with a non-zero status code.`——dev 模式**从来没有起来过**。

## 2. 根因：两条独立证据，都不是推断

1. **实测 cwd**（`artifacts/t05-desktop-rootcause.out`）：用 `--config` 只把该命令换成 `pwd > …`（**未改仓内文件、无残留进程**），
   日志落定 `tauri beforeDevCommand cwd = /Users/aqiuye/Develop/workspace/wt-media/wt-media-desktop` ——**不是** `src-tauri`。
   ⇒ `../../wt-media-cloud/web` 解析成 `<wt-media>/wt-media-cloud/web`（不存在）；从实测 cwd 起，`../wt-media-cloud/web` 正确。
2. **同文件内的第二个证人**：`beforeBuildCommand` 用的是**一段** `../wt-media-workspace/scripts/build-desktop.sh`，
   且 `scripts/prepare-release-sidecar.sh` 是**无前缀**的。这两条路径只有 cwd＝`wt-media-desktop` 时才同时存在
   （实测：两者都 `EXISTS`）⇒ 该文件的 cwd 形状本就如此，`../../` 是这一行**孤立**的笔误，不是某种约定。

**目标端也验过**：`../wt-media-cloud/web` 存在，其 `dev:desktop` = `vite --config vite.config.desktop.js`，
`vite.config.desktop.js:31-34` 是 `host 127.0.0.1 / port 5174 / strictPort`——与 `devUrl` 的 `127.0.0.1:5174` 一致。

**CHG-067 为什么没看见**：它的 start/stop/restart 臂跑在**替身 cargo** 上（`PATH=/private/tmp/desktop-sim/bin`），
替身只实现 `tauri --version` 与 `tauri dev`（自己起一个 http.server），**根本不执行 `beforeDevCommand`**——
那条命令一次都没被跑到。与本 CHG 起因同形：判据与缺陷错开一格。

## 3. 修复后复跑（`artifacts/t05-desktop-verbs-fixed.out`，真跑 `cargo tauri dev`）

| 格 | 命令 | 读数 |
| --- | --- | --- |
| 1 | `status`（空） | `pid=- alive=no health=down` **exit 1** |
| 2 | `start` | `cargo tauri dev started: pid=81359` ／ `dev server answering: http://127.0.0.1:5174` **exit 0** |
| 3 | `status` | `pid=81359 alive=yes health=ok` **exit 0** |
| 4 | `restart` | `stopped` ／ `started: pid=81755` ／ dev server 答话 **exit 0** |
| 5 | `status` | `pid=81755 alive=yes health=ok` **exit 0** |
| 6 | `stop` | `cargo tauri dev stopped` **exit 0** |
| 7 | `status`（空） | `pid=- alive=no health=down` **exit 1** |

三路旁证（每格取）：pid 文件 `81359 / 81755 / (absent)`；5174 监听 `81400 / 81800 / (空)`；`http://127.0.0.1:5174/` → `200 / 200 / 000`。
日志尾落在**改后的命令**上：`Running BeforeDevCommand (`cd ../wt-media-cloud/web && npm run dev:desktop`)` → `VITE v7.3.6 ready in 225 ms` → `Local: http://127.0.0.1:5174/`。
收尾无 stray `cargo`／`tauri`／`vite`／`node`，5174 归零。

⇒ desktop 的四格由 T-05 的**「止于既有前置」转为端到端**，AC-03 因此成为 **16/16 端到端**。

## 4. 回归（`artifacts/t05a-desktop-test-sh.out`，`HTTPS_PROXY` 仅本次调用）

`scripts/test.sh` **exit=0**：cargo `372 passed／0 failed／5 ignored`、`control.test.sh: 12 passed, 0 failed`、
`release-versions tests: 20 passed, 0 failed`——**与修复前同读数**（T-01 基线），修复没有连带。

**改前查过有没有判据锚在这一行**：全仓 `tauri.conf.json` 的引用里，读该文件的只有
`bin/control.sh`（取 `devUrl`）、`release-versions.sh`（取 `version`）、`build-*`／`package-*`（取 `version`），
以及 `src-tauri/src/bootstrap.rs:250`（`serde_json` 解析后断言 **CSP 键不存在**）。
**没有任何一条读 `beforeDevCommand`**——改动不动 CSP、不动 `version`、不动 `devUrl`，JSON 仍合法，故四类读者全部不受影响。

## 5. 如实记

- 本次修复**只**改路径。`devUrl`／`frontendDist`／`beforeBuildCommand`／CSP 一律未动。
- 复跑会真开一个 desktop 窗口（`cargo tauri dev` 的正常行为），`stop` 后随之结束。
- 该缺陷是**既有**的，不是本 CHG 引入；本 CHG 引入的是「把它测出来并要求修」。
- 与 §7 第 1 项（`tests/package-release-macos.test.sh` 是 644）无关，两条线各自独立。
