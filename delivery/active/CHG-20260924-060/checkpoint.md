# Checkpoint — CHG-20260924-060

- 状态：IMPLEMENTING（2026-09-24 激活）。
- 性质：处置 `CHG-20260923-056` 归档时随记录留下的四项待用户裁定。Level S，跨三仓（desktop / agent / workspace）。

## Completed

- 2026-09-24 T-01：建 `delivery/active/CHG-20260924-060/`（`change.md` 十三节、本 `checkpoint.md`、`evidence/`、
  `status/`），`delivery/LEDGER.md` 加一行表行，快照经 `prepare_ai_workspace.py --change CHG-20260924-060` 再生成。
- 2026-09-24 T-02（Desktop CSP，commit `9945f58`）：出货 TOML 的 `csp_connect_src` 加 `ipc:`；
  先失败恰好两条守卫红（61 passed; 2 failed），同步后 63 passed。真实启动两条 leg：出货值 → `ipc://` 拒绝 0，
  改动前的值（阳性对照）→ 3。顺带纠正金标 docstring 的失效说法。

## Current

- T-03 待开始（回环目标绕过系统代理）。

## Next

- T-03 Desktop 回环代理 → T-04 Agent 删占位包 → T-05 文档回写与归档。
- 一仓一 commit；「删除/搬移」与「改逻辑」不混进同一提交。
- **T-05 新增一项**：归档的 CHG-056 有个**被引用但未入库**的证据文件 `ac05-run5.log`
  （见 `evidence/task-02-csp.md` 末节），与被 *.gitignore* 的 `*.log` 规则吃掉，T-05 一并补入。

## Blockers

- None。CHG-056 §12 的四项待裁定已由用户于 2026-09-24 全部裁定（见 `change.md` §6 D-01…D-04）。

## Recent verification

- Start Gate（2026-09-24）：四仓工作区全部干净（各 `main` 与远端 ahead，无未提交改动）；
  `delivery/active/` 仅 `.gitkeep`；`LEDGER.md` 无表行；快照 `Active CHG: none`。
- T-01：见 `evidence/task-01-governance.md`。

## 执行期间的边界（不得越界）

- 开发者自己的 BitBrowser `:54345`、Cloud `:18080`（PID 55442）、dev Agent `:8765`（PID 55443）**全程不碰**；
  所有启动用 scratch 端口。
- 项 4（被误建的 `noop_task`）**只登记不处置**——清除它要动开发者的 Cloud，超出授权。
- `.ai/CURRENT_CONTEXT.md` 由脚本生成，**禁手改**。
