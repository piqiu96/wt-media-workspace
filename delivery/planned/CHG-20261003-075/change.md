# CHG-20261003-075：CHG-074 遗留技术债与门禁缺口处置

- Status: PLANNED
- Level: L（跨 cloud / desktop / agent / workspace 四仓；`- Level` 写成裸词不用反引号——见 §2 第 10 项，反引号会让 `verify_delivery_governance.py` 的 `LEVEL_RE` 认不出级别、整段跳过里程碑引用检查）
- 依据基线：本记录只收 [CHG-20261002-074](../../completed/CHG-20261002-074/change.md) §8.4 登记、关闭时**有意不处置**的项；各条的业务语义仍以其来源 CHG 与既有契约为准。
- 来源：CHG-074 关闭时（2026-10-03）的实测读数与登记；用户裁定技术债**另立 planned 草案**、本 CHG 的复验留在归档记录。
- Milestone: `delivery/milestones/M2-account-runtime.md`
- 激活条件：无 active CHG 时可以激活；各项之间无强依赖，但第 1/2/3 项改的是同一批门禁与契约锁，同一次激活内处理更省事。

## 1. 独立结果

CHG-074 关闭时登记的技术债逐条有裁定与处置：契约锁与 M2 硬编码基线对齐、m0 钉子与 map 一致、`docs/standards/` 进索引且既有死链修掉、`node_id` 悬置类缺陷收口、会话 cookie 生命周期明确、`scan=reuse` 在真实安装包上验证过一次、「仅用反引号写 Level 会让门禁静默跳过」的缺口被堵住。workspace 测试套件回到 0 红。

## 2. 范围与边界

登记时的实测读数（2026-10-03，CHG-074 关闭读数：workspace `python3 -m unittest discover -s tests` **92 用例 / 3 红**，其中 2 条即第 1/2 项的产物）：

1. **契约锁与 M2 静态矩阵不一致**——`wt-media-desktop/contracts.lock.json` 与 `scripts/verify_m2_acceptance.py:114-128` 里**硬编码**的 M2 冻结基线对不上，这正是 `test_static_cross_repo_contract_and_security_matrix` 的红。实测使该用例变红的是 **`cloud_agent_api`**（lock 钉 `v1@2026.10.01.1`，硬编码期望 `v1@2026.07.15.1`，漂移自 desktop `20e00d1`），**不是** `local_agent_api` / `local_event_schemas` 相对 `config/contract-map.yaml` 的陈旧（见第 3 项）。**待裁定**：是推进 lock，还是让该门禁改为读 `config/contract-map.yaml`（硬编码基线会在每次契约前进时复发）。注意 CHG-074 判过「不 bump」，故此处不是补动作，是重新裁定。
2. **`scripts/verify_m0_config.py` 的 `cloud_agent_api` 钉子过期**——期望 `contract_revision '2026.07.14.7'`，map 写 `2026.10.01.1`；漂移引入于 `786fdeb docs(chg-069): 任务 21 落档`（只推 map 未同步钉子）。该门禁直接 `rc 1`，并使 workspace 的 `test_contract_map_matches_m1_cloud_agent_compatibility`、`test_contract_map_provider_paths_exist_in_full_workspace` 两条变红。同一条缺口在 CHG-20260923-059 Q-06 登记过：钉子只保证「map 没背着人动」，保证不了「这个值还对」，且从不与相邻定义文件对比。
3. **`contracts.lock.json` 相对 map 的陈旧条**（先于 CHG-074 就存在）：`local_agent_api` 钉 `v1@2026.07.14.7`（map 已到 `2026.10.03.1`，CHG-074 推进）、`local_event_schemas` 钉 `profile-guard@2026.07.14.8`（map 写 `2026.07.14.9`）；其余 3 条一致。**单独把 lock 的 `local_agent_api` 对齐会让静态矩阵由 1 条红变 2 条红**（该条恰好等于硬编码期望）——处置顺序上应先定第 1 项的裁定。
4. **`docs/standards/` 未被索引 + 两处死链**：`前端交互规范.md`、`前端架构与视觉规范.md` 在 `AGENT-INDEX.md` 里 0 命中（索引只列 product / engineering/architecture / engineering/specs / contracts / decisions）；`docs/engineering/specs/README.md:12` 与 `docs/decisions/0007-visual-engineering-baseline.md:9` 都链向已删除的 `docs/engineering/specs/web-desktop-visual-system.md`。同族还有**归档记录里的死链**——实测 `delivery/completed/**` 有 30 处相对链接解析不到（23 真链接 / 7 行文占位），其中 12 处指向 `wt-media-*` 兄弟仓（那几个仓不在本仓目录树内，任何相对路径都到不了）；按只读边界不回改，本项只裁定**此后的记录**该用哪种写法（裸路径串 vs 相对链接），以及是否给一条扫描这类链接的检查。
5. **`node_id` 悬置的同类点未修**——`sensitive_browser_tasks.node_id` / `browser_profile_runtime_presence.node_id` 与 CHG-074 已修的 `user_download.assigned_node_id` 同属「节点换代后旧 id 搁浅」：`assigned_node_id` 一侧已在 `runtimebinding.saveNode` 内重指（cloud `c33859d`），这两处是否同样需要重指、还是本就按历史留痕，需逐处判定。
6. **会话 cookie 无 `Max-Age`**（CHG-074 走查发现）：关掉浏览器即掉登录态。属会话层语义，与「同 client_type 才 20010」「凭据不随会话失效」两条已定语义一起裁定。
7. **`document.hidden` 未实测**：Tauri WebView 启动时是否为 `true` 未量；若为 `true`，CHG-074 走查修复 2 之前的 interval 从不建立（该修复已改为挂载/手动/轮询/可见共用，但这条读数仍空）。
8. **`scan=reuse` 在真实安装包上未验证**：CHG-074 只证到「打包 sidecar 二进制按 30 秒 tick 复用扫描、两次真扫描相隔 5 分 12 秒」，**「胶囊每 30 秒真的带上该参数」只由源串断言 + 变异对照覆盖**——当时打包 app 起不稳（`IPC custom protocol failed` 278 次 / `Couldn't find callback id` 122 次，`local_agent_start` 被调 279 次后 Agent 被停），胶囊未进稳态。
9. **两处测试在负载下会假红**：agent `test_reuse_serves_the_first_scan_to_the_second_request` 已定位并修（断言比较了整个响应体，而 `data.disk.free_megabytes` 是逐请求实测值；churn 下 8/8 红 → 修后 8/8 绿，变异对照仍红，见 agent `f7b8f11`）；**desktop `commands::agent::tests::a_tampered_sidecar_is_refused_and_an_intact_one_is_started` 未修**——它与三个重型套件并发时红（等 5 秒 marker 文件超时），单独跑 3/3 绿、整套单跑 507 通过 / 0 失败 / 6 ignored。两条是同一类：判据里含与负载相关的时序/主机事实。**待裁定**：修 desktop 那条（对齐 agent 的改法），还是按「负载相关、静默机上读数为准」登记。
10. **门禁缺口：反引号把 `Level` 写成不可解析**——`verify_delivery_governance.py:14` 的 `LEVEL_RE = ^- Level:\s*([A-Z])\s*$` 不接受反引号；实测 `delivery/completed/*/change.md` 与 `planned/*/change.md` 共 68 篇里 **6 篇**的 `Level` 行正则匹配不到（`CHG-20260930-069` `` `S` ``、`070` `` `S` ``、`071` `` `M` ``、`CHG-20261001-072` `` `L` ``、`073` `` `M` ``、`CHG-20261002-074` `` `L`（…）``），即这 6 篇活跃期间 `validate_milestone_reference()` **整段被跳过**；同一实测还有 **28 篇**记录根本没有 `- Milestone:` 行（两者都会让该检查空转）。**待裁定**：放宽正则以容忍反引号/注解，还是统一记录写法（新记录一律写裸词）。
11. **M2-F 里程碑基线回写**：`delivery/milestones/M2-account-runtime.md` §6 仍写「主账号仍按现有管理员解除流程处理」，已被 CHG-074 阶段 3 Item D 的用户自助「比特账号绑定」取代。CHG-074 只补了实施记录指针、**未动已签收的正文**，回写待裁定。

边界：本记录不重开 CHG-074 的任何已交付范围；不改已归档记录（`delivery/completed/README.md:11`）；第 1/3/10 项的裁定结果若改变门禁行为，须同步登记在门禁自身或 `docs/engineering/` 的规范处，不建第二套台账（`AGENT-INDEX.md:40`）。

## 3. 明确不做

- 不为让 workspace 测试套件变绿而改判据（第 1/2 项的处置是「对齐契约锁/钉子」或「改门禁读源」，两者都要各自裁定）；
- 不重打 DMG、不重跑 CHG-074 的走查（用户已签收）；
- 不把第 9 项的 desktop 侧当成 CHG-074 的未完成项——它先于本 CHG 存在，且只在负载下出现。

## 4. 验收标准

- workspace `python3 -m unittest discover -s tests`（判据：`scripts/verify_m0_config.py` 与 `scripts/verify_m2_acceptance.py` 各自的函数）**0 红**，且每条的处置方式有裁定记录（不是把判据改松）。
- `docs/standards/` 两篇在 `AGENT-INDEX.md` 可索引；两处死链指向存在的文件。
- 反引号缺失解析的缺口有结论，且用**门禁自己的** `LEVEL_RE` 复测：再扫描时要么 0 篇不可解析，要么门禁容忍注解（两种都可，但要有阳性对照——对已知反引号记录应仍能读出级别）。
- 第 5/6/7/8 项各有明确裁决（修 / 不修 / 未覆盖即登记），不留下「登记了但没人看」的条目。

## 5. 有序任务

1. 先裁定第 1 项（契约锁 vs 硬编码基线），因为它决定第 3 项的顺序；
2. 按裁定对齐第 1/3 项，第 2 项随之把 m0 钉子移到 map 当前值（钉子移动即那次契约前进的复核动作）；
3. 第 4 项：补索引 + 修死链（纯 workspace 文档，判据是链接 resolve 且字符串扫描无旧路径——两条都要，扫链前先剥代码跨）；
4. 第 5/6/7/8 项逐处测定后处置或登记；
5. 第 9/10/11 项按裁定收口。

## 6. 验证与提交边界

- 门禁类改动跑 `scripts/verify_m0_config.py`、`scripts/verify_m2_acceptance.py`、`scripts/verify_delivery_governance.py` 三个直接入口并记 rc，另附阳性对照；
- 契约锁/契约文件改动按 `docs/contracts/compatibility-policy.md` 判定是否需要 decision record；
- 各仓独立提交，不与其他 CHG 混杂；workspace 的记录改动与本记录自身的激活状态同一次提交（`prepare_ai_workspace.py --no-active` 反向）。
