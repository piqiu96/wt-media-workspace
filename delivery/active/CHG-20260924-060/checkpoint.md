# Checkpoint — CHG-20260924-060

- 状态：IMPLEMENTING（2026-09-24 激活）。
- 性质：处置 `CHG-20260923-056` 归档时随记录留下的四项待用户裁定。Level S，跨三仓（desktop / agent / workspace）。

## Completed

- 2026-09-24 T-01：建 `delivery/active/CHG-20260924-060/`（`change.md` 十三节、本 `checkpoint.md`、`evidence/`、
  `status/`），`delivery/LEDGER.md` 加一行表行，快照经 `prepare_ai_workspace.py --change CHG-20260924-060` 再生成。
- 2026-09-24 T-02（Desktop CSP，commit `9945f58`）：出货 TOML 的 `csp_connect_src` 加 `ipc:`；
  先失败恰好两条守卫红（61 passed; 2 failed），同步后 63 passed。真实启动两条 leg：出货值 → `ipc://` 拒绝 0，
  改动前的值（阳性对照）→ 3。顺带纠正金标 docstring 的失效说法。
- 2026-09-24 T-03（Desktop 回环代理，commit `d329abc`）：`http/mod.rs` 抽出 `timed_builder`、
  新增 `build_client_without_proxy` 与 `is_loopback_url`；`local_agent.rs` 无条件改用无代理 client；
  `cloud.rs` 拆 `proxied`/`direct` + `client_for`。测试 **63 → 68**。
  - **先失败证据**：经代理的 client 对一个**无人监听**的回环端口拿到 `Ok(502)`（3.0s），
    不经代理的 client 405µs 内 `is_connect`——只有代理能替不存在的服务作答。bug 真实且当前。
  - **阳性对照有效**：删掉 `.no_proxy()` 后 5 条新增测试里**红了 2 条**，且 Debug 臂打出活的
    `http://127.0.0.1:7897/`（本机 Clash）。
  - **阳性对照无效（如实降级）**：计划里的 20× 循环，对照臂（指回带代理的 client）**20/20 全绿**
    ⇒ 该循环区分不了两个 client，按计划自己的判据记为**无效对照，不计为通过**。机制已查明：
    代理会自己去拨那个静默监听器，本 client 自己的截止时间先到，同样产出 `is_timeout`。
  - **纠正计划两处**：(a) 验证命令 `cargo test --lib` 在本仓不成立（二进制 crate），
    正确目标是 `--bin wt-media-desktop-shell`；(b) 「假代理臂能抓住变异」是错的——
    代理把回环请求转发到目标、目标答 200，该臂所有断言仍成立。代码 docstring 已改写为实测结论。
  - 未做：真机启动 + Clash 连接日志（登记为佐证而非唯一证据）；`cargo fmt`（本仓无 rustfmt 配置、
    刻意放宽到约 136 列，跑它会重写二十余个无关文件）。

## Current

- T-05 待开始（文档回写与归档）。

## Next

- T-05 文档回写与归档（含 CHG-056 那个被引用但未入库的 `ac05-run5.log`）。
- 一仓一 commit；「删除/搬移」与「改逻辑」不混进同一提交。
- **T-05 新增一项**：归档的 CHG-056 有个**被引用但未入库**的证据文件 `ac05-run5.log`
  （见 `evidence/task-02-csp.md` 末节），与被 *.gitignore* 的 `*.log` 规则吃掉，T-05 一并补入。

## Blockers

- None。CHG-056 §12 的四项待裁定已由用户于 2026-09-24 全部裁定（见 `change.md` §6 D-01…D-04）。

## Recent verification

- Start Gate（2026-09-24）：四仓工作区全部干净（各 `main` 与远端 ahead，无未提交改动）；
  `delivery/active/` 仅 `.gitkeep`；`LEDGER.md` 无表行；快照 `Active CHG: none`。
- T-01：见 `evidence/task-01-governance.md`。
- T-02：见 `evidence/task-02-csp.md`。
- T-03：见 `evidence/task-03-proxy.md`；原始输出 4 份在 `evidence/artifacts/t03-*.out`。
  末轮 `cargo test --workspace` = **68 passed; 0 failed**，`cargo build` 通过，
  `cargo clippy` 零新增 warning。
- T-04：见 `evidence/task-04-packages.md`；原始输出 2 份在 `evidence/artifacts/t04-*.out`。
  `bash scripts/test.sh` = **253 tests OK**（与删包前一致）。

## T-05 待清单（收尾用）

- agent 仓文档回写：`DIRECTORY_MAP.md:98/102/104/117`、`AGENTS.md:27/36`、`CLAUDE.md:9`、
  `AGENT-INDEX.md:64`。注意 `AGENTS.md:36` 与 `CLAUDE.md:9` 的**意图**（不得手改生成代码）
  仍然成立，但不能再指向一个不存在的路径——是**改写**，不是直接删。
- 修归档 CHG-056 那个**被引用但未入库**的 `ac05-run5.log`（见 `evidence/task-02-csp.md` 末节）。
- `CHG-056` §12 四项待裁定按裁定结果标注处置去向。
- `Status: DONE` → 移入 `delivery/completed/CHG-20260924-060/` → 移除 LEDGER 行 →
  `prepare_ai_workspace.py --no-active` 重生成快照 → **主动扫**归档连带的失效指针。

## 执行期间的边界（不得越界）

- 开发者自己的 BitBrowser `:54345`、Cloud `:18080`（PID 55442）、dev Agent `:8765`（PID 55443）**全程不碰**；
  所有启动用 scratch 端口。
- 项 4（被误建的 `noop_task`）**只登记不处置**——清除它要动开发者的 Cloud，超出授权。
- `.ai/CURRENT_CONTEXT.md` 由脚本生成，**禁手改**。
