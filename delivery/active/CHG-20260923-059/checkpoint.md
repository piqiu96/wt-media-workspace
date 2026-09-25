# CHG-20260923-059 Checkpoint

## Completed

- 2026-09-25：草案由 `delivery/planned/` 移入 `delivery/active/` 并改写为十三节执行记录
  （`change.md`、`checkpoint.md`、`status/`、`evidence/`）。
- `change.md` §4 的每条现状都是激活时**实测**得到的 file:line 与命中数。**两条草案预想被实测推翻并已更正**：
  ①草案说「Cargo 里没有哈希依赖」——实测 `sha2 = "0.10"` **已是直接依赖**（`src-tauri/Cargo.toml`），
  故 T-04 是「复用既有依赖」而非「新增依赖」；②草案未提 `config_online/agent.toml:17-21` 那段
  **过期的 Q-01 注释**，实测存在且与新裁定冲突 ⇒ 并入 T-10 回写。
- 其余 §4 事实逐条在案：就绪行打得出来（`server.py:627` 在 bind+listen 之后、`serve_forever()` 之前）
  但**消费者为零**、`start_timeout_ms` 是死配置；`already_running` 读的是 `session.current()`
  （`commands/agent.rs:171-172`），CHG-057 登记的实缺陷仍在；退出侧 `RunEvent`/`on_window_event`/`ExitRequested`
  **零命中**、`sidecar::stop` = `child.kill()`、Agent 只捕 `KeyboardInterrupt`；
  `tauri.conf.json:26` 的 `bundle.resources` 只含 Desktop 自己的 toml 且 `build_desktop_sidecar.py`
  对 `config_online` 零命中；两个版本号各读一处（`:53`/`:82`）**从不比对**。
- 用户 2026-09-25 的两条裁定落在 §6：**D-08**（Q-01 关闭＝生产 Cloud 保持本机 `http://127.0.0.1:18080`，
  两份出货配置的值与 CSP 均不改，只回写过期注释）、**D-09**（「干净机」安装验收**登记为未做**，
  `0.2.5` 的 status 保持 `verifying`，D 的 DONE Gate 因此**带一条登记过的例外**）。
- 本机环境：起改前已确认 18080 / 8765 空闲；54345 是用户自己的 BitBrowser，**全程不占用**。

## Current

- **激活（T-01 之前，不占任务号）已完成**：`git mv` + 十三节 `change.md` + 三份 `status/` + 本 `checkpoint.md`；
  `LEDGER.md` 表行改回 CHG-059、`planned/README.md` 的 D 行改 ACTIVE、里程碑状态行注明 D 已激活、
  程序总纲两行改「D 已激活」。快照经 `prepare_ai_workspace.py --change CHG-20260923-059` 再生成（2144 字符）。
- **激活期间被自己的门禁抓过一次**：`verify_delivery_governance.py` 报
  `current context and ledger disagree: CHG-20260923-059 != none` —— 起因是我把 LEDGER 首格写成了
  markdown 链接，而 `LEDGER_ROW_RE`（`scripts/verify_delivery_governance.py:37`）要求首格是**裸 id**。
  已按 CHG-058 的先例改回裸 id（链接移到标题格内），两个验证器随即转绿。
  这是「先证明检查能失败」的正面样本：门禁不是空转的。

## Next

- T-02 就绪闸门（两阶段：复用 Agent 自己那行 stdout + spawn 后真实健康探测），
  按 `先失败的验证/测试 → 最小实现 → 测试 → diff 检查 → evidence → checkpoint → 独立提交` 推进。

## Blocked

- 无硬阻塞。**T-06 内有一条待关闭的 Q-04**（「组件与资源版本」的**口径**——M-launch-engineering
  成功事实 #7 要求「发布可追溯五类版本」，而前端构建版本与组件/资源版本至今**没有任何表示**，
  是新建而非校验）。T-06 要么关闭它，要么如实退回给用户。

## Recent verification

- 激活时基线：agent **377 tests OK**；desktop **336 passed / 0 failed / 2 ignored**；
  workspace 三验证器绿 + `unittest discover` **69 tests / 4 failures**——**4 条红项为既知**
  （`test_verify_m0_config` ×2、`test_verify_m2_acceptance` ×1、`test_verify_product_master_alignment` ×1，
  与 `README.md` 的既有红项清单**逐条同名**），判定要用 `git archive HEAD` 的**同集合阳性对照**，
  不用「看着无关」。
