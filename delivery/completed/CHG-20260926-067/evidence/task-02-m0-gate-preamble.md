# T-02 证据：M0 门禁前置（workspace）

- CHG: `CHG-20260926-067`
- Task: T-02（`change.md` §8）
- 日期: 2026-09-26
- 锚: 开工前 workspace HEAD `214d65a`（T-01 的提交）

## 1. 改动文件

| 文件 | 改动 |
|---|---|
| `scripts/verify_m0_config.py` | `validate_ci_workflows` 的 desktop needle 元组 7 条 → 3 条；docstring 补上「为什么收窄」与两条注意 |
| `scripts/verify_m0_local.sh` | `:39-45` 的 desktop 块 4 条 → 只剩 `scripts/test.sh` |

## 2. 为什么这个 Task 必须早于 T-03

T-03 会删掉 desktop 的 `scripts/bootstrap.sh`／`build.sh` 并把 CI 改成 Rust-only。这两件事一发生，
**两条 workspace 门禁当场红**——它们断言的正是不复存在的文件与 npm 动词。T-02 先把断言收窄到
终态，T-03 才可能在两仓之间不产生红窗。实测见 `artifacts/t02-m0-gate-arms.out` §A：

| 臂 | 组合 | 结果 |
|---|---|---|
| 0 | 现状 workflow × 新 tuple | `errors: []`（改后到 T-03 之间无红） |
| 1 | **变异**：workflow 里 `scripts/test.sh` 改名 | `missing 'scripts/test.sh'`——点名，还原后绿 |
| 2 | **前瞻**：T-03 终态 workflow × 新 tuple | `errors: []`——新 tuple 是终态文本的**子集** |
| 3 | 旧 tuple × T-03 终态 workflow | **3 处红**——证明收窄是承重的，不是白收 |

臂 0／1／2／3 都**直接调门禁自己的函数**（`importlib` 载入后把 `OUTER_ROOT` 指到模拟树，
再调 `validate_ci_workflows(False)`），没有另写一份等价正则——量法与判据必须同一个定义。

## 3. 收窄的边界：3 条是被迫，1 条是主动

臂 3 只报 **3** 处红，不是 4：`node-version: "26"` 在终态 workflow 里仍然存在（`setup-node` 保留），
它是**主动**删掉的。理由写在 `verify_m0_config.py` 的 docstring 里：node 已不是本仓的工具链，
把它的版本号当 desktop 的契约来卡，会让这条判据的可满足性取决于一个 T-03 尚未做的决定。
如实记：这一条不是被迫的。

## 4. 一条顺带查出的旧账：needle 绿 ≠ 那一步能跑

这些 needle 是**对 workflow 文本的字符串检查**，从不证明那一步真的执行过。
`npm run lint` 自 `7aabb1a`（`package.json` 在那次提交被删）起就已经是坏的，而 needle 一直是绿的。
本案实测：`npm run lint` 在 desktop 下 `exit=254`（`npm error enoent Could not read package.json`）；
旧块的第一颗钉 `scripts/bootstrap.sh`（`npm ci`）更是 `exit=1` 就停住，**根本走不到 lint 那一行**。
⇒ 计划里写的变异（「把 `npm run lint` 放回 → 脚本失败」）成立，但**降级了**：它不是被第二个动词抓到的，
是第一个动词就断了。两臂读数见 `artifacts/t02-m0-gate-arms.out` §B（A1 停在 `npm ci`／A2 单跑 lint 得 254）。

## 5. 给 T-03 的一条实测输入：`setup-node` 不能整个删掉

计划把 `setup-node` 的去留留给 T-03 ① 的 clean-clone 读数。这里先量到一个会改变该决定的读数：
desktop 的两个 shell 套件**确实调用 `node`**——但只是当 JSON 读取器，不碰 npm/vite。

| 套件 | 命中行 |
|---|---|
| `tests/package-release-macos.test.sh` | `:15` `node -p 'require(process.argv[1]).version' …tauri.conf.json` |
| `tests/release-versions.test.sh` | `:168`、`:267`、`:314` 三处 `node -p` / `node -e` 读 `$record` |

分母 2 个套件、共 4 处命中（`grep -cE '\b(node|npm|npx|vite|pnpm|yarn)\b'`）。⇒ 「Rust-only」在本仓的含义是
**没有 Node 包工具链**，不是**没有 node 可执行文件**。`setup-node` 保留，`cache:` 与
`cache-dependency-path: package-lock.json` 必须去掉（锁文件不存在）。

## 6. 本次两臂跑在脏树，不是干净克隆

`artifacts/t02-m0-gate-arms.out` §B 的臂 B 是在**当前工作树**上跑 `scripts/test.sh` 得到的读数
（`running 377 tests` / `372 passed; 0 failed; 5 ignored` ＋ 2 个 shell 套件各 `exit=0`）。
clean-clone 读数是 T-03 ① 的交付物，本 Task 不主张它。desktop 的 `target/` 已有 18G 构建产物，
故 3.06s 不是冷启动读数。所有 npm 报错文本按原样摘录。

## 7. 门禁读数

六门禁 ＋ 套件 ＋ `sync_skills check` 取在**本 Task 全部改动落地之后**，落
`artifacts/t02-gate-final.out`（**不在此内联**，同 T-00／T-01 的处置）。本 Task 记录体量落
`artifacts/t02-record-size.out`。
