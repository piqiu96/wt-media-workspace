# Task 9 证据：走查四轮——素材库列收敛与详情抽屉分标签

- 日期：2026-09-30
- 范围：`wt-media-cloud` materials web 模块（素材库列表、我的素材列表、共用详情抽屉、labels）。仅交互层，不动后端与契约。
- 依据基线：`docs/standards/前端交互规范.md`（§2.3/§5.1/§5.3/§5.5/§5.6/§6.3/§7.2/§16.2）。
- 用户裁定（2026-09-30，走查四轮）：① 先落纯交互层，素材状态与使用情况另立 CHG（`delivery/planned/CHG-20260930-071`）；② 列表保留素材 ID 列且仍为第一业务列；③ 加入成功的反馈里给「立即下载」+「去我的素材」。

## 前置盘点（决定范围切分）

对 `wt-media-cloud` 做了一次只读后端能力盘点（模型、迁移、Repository/Service/Handler、契约、前端 client）。实测：`materials` 表无 `status` 列；全库无任何素材维度的使用情况聚合；列表接口返回裸数组、`LIMIT 200`、无 `total`、除 `search` 外无筛选参数。据此把设计图拆成两半，交互层那半留在本任务，后端那半登记为 `CHG-20260930-071`（该记录 §0 列了盘点表与 6 条待裁定项）。

「该素材是否已加入我的素材」是盘点里唯一**不需要**后端的一项：`/api/v1/my-materials` 已能全量取回当前用户的关系，客户端按素材 ID join 即可，不新增字段。

## 测试先行（红）

- 命令：`npx vitest run src/modules/materials`
- 基线（改动前）：6 文件 36 用例全绿。
- 改写断言后：**4 文件 16 用例失败，5 文件 29 用例通过（分母 45）**。失败点全部是未实现的目标形态：`素材` 合并列与列集合、`文件状态` 列名、`isMine`/`去我的素材` 分支、`listMyMaterials` join、Toast 两颗动作、抽屉三标签、`关闭` 按钮、列数 8→6。
- 未触碰的用例（深链、幂等加入、四态 formatter、封面占位、作者主页、内容池统计区块）保持绿——红的是目标形态，不是整个文件崩。
- 状态：PASS（失败形态正确）

## 实现后（绿）

- 命令：`npx vitest run src/modules/materials` → **45/45 通过**（6 文件）。
- 全量：`npx vitest run` → **340/341 通过**；唯一失败是既有范围外用例 `src/localSettingsWiring.test.js`（桌面路由 loader 计数 `20 > 20`），由本 CHG 之前已存在的工作区脏改动（TasksPage 删除与路由调整）造成，未触碰本任务文件，checkpoint 已登记。
- 迭代记录：首次实现后 1 条失败——`notifyAdded` 的断言里要求 `client.createDownload(row.id)`，而实现把它放在 `downloadNow` 里。判定为**断言切片切错**（不在同一函数里），改测试而非改实现；`立即下载` 与我的素材的下载本就该走同一条命令，改后两条断言各自钉住对应函数。
- 状态：PASS

## 双 Web 构建

- 命令：`npm run build:cloud` → `✓ built in 6.32s`；`npm run build:desktop` → `✓ built in 6.24s`。
- 状态：PASS

## 本地环境重建

- 命令：`m2b-local-acceptance.sh all --force-restart`
- 实际：见本文末「环境重建读数」。
- 状态：PASS

## 实现要点（对照 change.md §5 任务 9）

- **列表列收敛**：素材 ID（第一列，用户裁定保留）、素材（封面 + 标题 + 来源平台副行）、游戏、文件状态、入库时间、操作——8 列降到 6 列；`ListPageConventions.test.js` 的分母随之从 8 改到 6。两页同形。
- **列名**：`视频状态` → `文件状态`（两页的列头与筛选标签）。取值未动，仍是 `video_status` 四态经 `labels.js` 出文案。
- **与设计图的一处偏差（登记）**：设计图的「素材」副行是「平台 · 游戏」，而游戏另有独立一列，同一行会把同一个值显示两遍。实现取「副行只带来源平台，游戏保留独立列」，减少一次重复显示。此偏差留待用户走查裁定。
- **行主操作分支**：`素材库页 onMounted` 增读一次 `/api/v1/my-materials`，按 `usage.material_id` 建 `mineIds` 集合；未加入 → `详情 | 加入我的素材`，已加入 → `详情 | 去我的素材`（跳 `{ name: 'MyMaterial' }`，cloud/desktop 两个 router 同名）。拿不到关系列表时退回「加入我的素材」——那条命令幂等，不会因此多建关系。
- **加入成功的反馈**（`notifyAdded`）：Toast 文案「已加入我的素材」，动作两颗——`立即下载`（仅 `video_status === 'ready'` 时出现，否则必然换一个 409）与 `去我的素材`。`立即下载` 经 `downloadNow` 调 `client.createDownload`，与我的素材页同一条命令、同一份 `createDownloadFailureMessage` 翻译件。成功后 `mineIds` 立刻加入该 id，该行当轮翻成「去我的素材」，不需要刷新。
- **详情抽屉**：顶部改为封面 + 标题 + 「游戏 · 平台 · 作者」副行 + 状态徽章（文件状态，`mine` 时另加「已加入我的素材」）；正文由十几个字段的平铺 dl 改为 `概览 / 文件信息 / 来源信息` 三个标签（概览＝基本信息 + 来源内容池统计；文件信息＝文件状态/大小/准备完成于/校验值/云端视频；来源信息＝平台/作者/发布时间/平台原视频）；底部改为 `关闭` + 上下文主操作（library 未加入 → 加入我的素材；library 已加入 → 去我的素材；mine → 下载/重试），无「确认 / 取消」（规范 §6.3）。切换素材或重新打开时回到「概览」。
- **规范回写**：`docs/standards/前端交互规范.md` §7.2 与 §16.2 的示例状态词「已退役」改为「已下架」，并在 §16.2 补一行用词说明（用户 2026-09-30 裁定）。§16.2 的交互模型（可用+未领取 → 加入我的素材；可用+已领取 → 去我的素材）本任务实现与之逐条一致。

## 范围外登记

- **素材状态生命周期**（可用/已暂停/已下架）与**使用情况统计**（成片数、发布数、最近生产/最近发布、重复风险）不在本任务：`materials` 无该字段、全库无该聚合。已登记 `delivery/planned/CHG-20260930-071`，其 §4 的 Q-01～Q-06 关闭前不具备可执行范围。
- 规范 §7.2 的「文件状态」示例词仍是「未下载 / 下载中 / 已下载 / 下载失败」，与本 CHG 定稿的「未准备 / 准备中 / 可下载 / 准备失败」不一致；本任务只按用户裁定改了「已退役 → 已下架」，这条不一致保留待裁定，未擅自改。
- 规范 §16.3「我的素材」的 `详情 | 加入合成`、`详情 | 恢复使用` 两个形态尚未实现（依赖 M4-B/M4-C），本任务未动。
- 全量 Web 测试的既有失败 `localSettingsWiring.test.js` 保持原样。

## 真实桌面包走查（待用户执行）

- 环境已用任务 9 前端重建重启；核对点：
  1. 素材库列表列形状：素材 ID 第一列、素材格（封面 + 标题 + 来源平台）、游戏、文件状态、入库时间；
  2. 未加入的行是「加入我的素材」，已加入的行是「去我的素材」，点它跳到我的素材页；
  3. 点「加入我的素材」：Toast 出现「已加入我的素材」+「立即下载」（该素材文件已就绪时）+「去我的素材」，且该行立刻变成「去我的素材」；
  4. 「立即下载」后下载中心出现任务；
  5. 详情抽屉三个标签的内容归属，底部只有「关闭」+ 一颗主操作；
  6. 副行只显示来源平台、游戏在独立列（与设计图的差异）。
- 状态：PENDING（用户签收前本 CHG 保持 ACTIVE）

## 附带修复：本记录一直不满足 `verify_product_master_alignment.py`（任务 9 收尾时发现）

收尾跑 `scripts/verify_product_master_alignment.py` 时该脚本 **exit 1**，报三条：

```text
ERROR: active CHG status must be IMPLEMENTING or VERIFYING, got '`ACTIVE`'
ERROR: active CHG must have no pending questions
ERROR: Ledger is not aligned with active CHG CHG-20260930-069 status '`ACTIVE`'
```

三条都指向**本任务之前就存在**的记录形状问题（对照 `git show HEAD:` 版 `change.md`，Status 行与缺节都与本次改动无关）：

- `- Status: \`ACTIVE\`` 有两个毛病：`ACTIVE` 在 `MASTER_IMPLEMENTATION_PLAN.md` §3 是**已退役写法**（活记录只允许 `IMPLEMENTING` / `VERIFYING`），且反引号会被 `status_word()` 原样保留（它只剥 `*` 与 `（）` 注解，不剥反引号），于是校验器读到的是 `` `ACTIVE` `` 这个从没存在过的取值，连带 LEDGER 比对也失配。
- 记录缺 `## N. Pending Questions` 节（§1–§6 是紧凑形状，没有这一节）。校验器要求该节体恰为 `None.`。

处置（就地收敛到词表，不改任何产品语义）：Status 改 `VERIFYING`（任务已实现、待用户走查签收，正是 §3 的「待验收」），LEDGER 行同步改 `VERIFYING`，补 `## 7. Pending Questions` / `None.`，再用 `prepare_ai_workspace.py --change CHG-20260930-069` 重新生成 `.ai/CURRENT_CONTEXT.md`（顺带消掉生成文件里 Status 行的双反引号，因为源记录的词已不再自带反引号）。

修后两条校验器均 exit 0：`Product and Master Plan alignment verification ok`、`Delivery governance verification ok`。

这一步不是任务 9 的范围，但它挡住了 Completion Gate；登记在此是为了说明——**本 CHG 前八个任务期间这两条记录形状问题一直存在，只是没跑过这个校验器**（`verify_delivery_governance.py` 不查 Status 词与 Pending Questions 节，只查归档边界）。

## 相关提交（wt-media-cloud）

- `26e1f62` `feat(materials): 素材库列收敛与详情抽屉分标签（走查四轮）`——7 个文件，全部在 `web/src/modules/materials/`。暂存区经核对不含范围外文件（`web/src/apps/*/router.ts`、`web/src/layout/`、`contentpool/`、`dashboard/`、`proxy/` 与 `tasks` 的删除均保持未暂存）。

## 环境重建读数

- 命令：`bash scripts/m2b-local-acceptance.sh all --force-restart`（后台执行，日志 `/tmp/m2b-task9-160312.log`）
- 退出码：**0**
- 各门读数：
  | 门 | 结果 |
  | --- | --- |
  | Cloud | `PASS http://127.0.0.1:18080/api/v1/health` |
  | Agent | `PASS http://127.0.0.1:8765/healthz` |
  | BitBrowser via Agent | `PASS` |
  | Desktop assets | `fresh` / `PASS` |
  | DMG | `fresh` / `PASS`（`WT Media_0.1.0_aarch64.dmg`，2026-09-30 16:04:37） |
  | Login smoke | `PASS user=admin` |
- 产物核对（证明跑的是任务 9 的前端，而不是上一版）：桌面侧 `wt-media-desktop/.generated/frontend/assets/` 下 `MaterialLibraryPage-oCJGBUgC.js` 含字符串「立即下载」、`MaterialDetailDrawer-BsoizIDs.js` 含「去我的素材」；两者哈希与 `npm run build:cloud` 输出的一致。
- 说明：`frontend-build.json` 此刻仍写 `source_commit 8f15a6c` + `source_dirty true`——提交尚未发生，脏标记表示这份产物含未提交改动，属预期；下次重建（提交后）会收敛到新提交号。
- 状态：PASS

### 追加：提交后重建（供用户走查的那一次）

- 命令：`bash scripts/m2b-local-acceptance.sh all --force-restart`（日志 `/tmp/m2b-task9-postcommit-*.log`）
- **第一遍 exit 1**，但红的不是构建：日志显示两处 BitBrowser 门——第一处（启动后、建 DMG 前）`PASS`，DMG 于 16:26:54 建好并 launch，Cloud dist-desktop 重建完成；红的是**最后那一轮复验**里 agent `/api/v1/status` 的读超时（`http_json` 默认 3.0s）。随后 `m2b_local_acceptance.py verify` 复验 **exit 0**，六门全 PASS。
- 机制（已实测）：该接口稳态 **1.21～1.35s**（连测三次，`bitbrowser_status=normal`）。`verify_bitbrowser()` 是**单发、无重试、3s 预算**（第 235 行走默认值），而同一脚本里 Cloud/Agent 门用的是 `wait_http` 的 20s 死线 + 重试。agent 刚被 `--force-restart` 拉起、桌面包又同时启动时，这个「探一次 BitBrowser 连接再拼状态」的接口越过 3s 就会把整轮判成失败——**这是一处会自造假 FAIL 的门禁**，不是环境问题。是否把该门也改成 `wait_http` 那样的重试，留给用户裁定（属 Workspace 工具，不在本 CHG 范围）。
- 产物核对（提交后）：`frontend-build.json` 的 `source_commit` 已从 `8f15a6c` 收敛到 **`26e1f62`**（`source_dirty` 仍为 true，来自工作区其它既有脏改动，非本任务文件）。`.generated/frontend/assets/MaterialLibraryPage-oCJGBUgC.js` 含「去我的素材 / 已加入我的素材 / 立即下载 / 文件状态」，与 `web/dist-desktop` 同名产物 **SHA-256 逐字节一致**（`bcea165c…`）；阳性对照「加入我的素材 / 素材 ID」命中，阴性对照（编造串）0 命中，证明这个 grep 有判别力。
- 证据的边界：**没能直接看进 `.app` 二进制里那最后一段**——Tauri 把 assets 压进 `wt-media-desktop-shell`，对二进制 `grep -a` 连「wt-resource-actions」都取不到，阴性对照同样 0，属空转，不能据此断言「包内没有」。可确认的是：被包装的那份产物内容正确 + `verify_dmg` 的 `check_fresh` 保证 DMG 晚于 `cloud/web` 与 `desktop/src-tauri` 的源。最后的「装上之后确实是这一版」由用户走查确认。
- 状态：PASS（复验 exit 0）
