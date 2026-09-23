# CHG-20260923-054：M3 综合验收缺陷与安全问题处置

- Status: PLANNED
- Level: S
- 锚点：`delivery/milestones/M3-content-discovery-v2.md` §2.1；验收登记 `delivery/active/CHG-20260916-052/evidence/m3-e3-acceptance-20260923/`
- 日期：2026-09-23
- 基线：`docs/product/M3-content-mining-v2.md`；ADR-0013、ADR-0014、ADR-0015
- 当前仓库：`wt-media-cloud` 为主；`wt-media-workspace`（验收脚本与治理记录）为辅。
- 未激活：本草案按用户 2026-09-23 裁定登记——「缺陷移入 planned，另立后续 CHG」。**不在 `CHG-20260916-052` 内修复**，也不抢占其 active 名额。

## 独立目标与范围

处置 M3 E3 综合验收（`CHG-20260916-052`）登记、**验收当时只登记未修**的缺陷与安全问题。
本 CHG 的独立目标不是「继续做 M3 功能」，而是**关闭验收遗留**：让 M3 的残余缺陷有明确归宿与
可验证的修法，而不是长期挂在验收记录的「Open follow-ups」里。

**验收事实**：M3 的验收矩阵在补验后已无 FAIL、无 NOT VERIFIED（`14-verdict.md` 第 1～7 项全部通过），
下列缺陷均**不影响**验收项的成立，属质量、体验与安全债。

### 缺陷清单（来源：`12-defects-and-security.md`）

| 编号 | 现象 | 性质 | 关联验收项 |
| --- | --- | --- | --- |
| D1 | 策略重名返回 `500`，而非 `409 / 14007` | 错误映射（仓储包私有错误未翻译） | 否 |
| D2 | `schedule` 无服务端校验，`garbage` 可入库且永不触发 | 输入校验缺失 | 否 |
| D3 | `POST /discovery-strategies/:id/run` 可重复排队，违反基线 §5 | **功能不达标** | **是**（基线 §5） |
| D6 | UI 的「ID/链接发现」硬编码 `source_type:'search'`，来源方式失真 | 标签失真 | 否 |
| D7 | `errCrawlTaskNotFound` 同族未翻译（仅代码观察，未复现） | 错误映射 | 否 |
| D8 | `ErrCrawlerUnavailable` 未在 `writeDiscoveryError` 映射 | 错误映射 | 否 |
| D9 | 上游空返回被透传为「成功且 0 条发现」，界面无提示 | 上游行为 + 体验 | 否 |
| D10 | `scripts/verify_m2_acceptance.py` 指向已迁移路径，导致 M2 静态矩阵假 FAIL | 验收脚本陈旧 | 否 |
| D-scheduler-2 | `daily HH:MM` 漏 tick 即丢当天，无补偿机制 | 既有设计，可靠性 | 否（潜在） |

### 安全问题清单（来源：`12-defects-and-security.md` 第一节）

| 编号 | 内容 | 用户裁定 |
| --- | --- | --- |
| S-1 | `wt-media-cloud/config/credentials/douyin.toml` 被 git 跟踪（真实 `api_key` 与 6975 字符 `cookie`） | 2026-09-23 裁定**只登记**：本轮不改仓库、不加 `.gitignore`、不轮换、不重写历史 |
| S-2 | 验收工具曾把活会话令牌写进证据目录 | **已处置**（令牌从未提交，落点已改到 Cloud `.cache/m3-acc/`），本 CHG 无需重复处理 |

## 明确不做

- **不重写 git 历史**、不改 `config/credentials/douyin.toml`、不加 `.gitignore` —— S-1 的仓库动作
  需用户在激活本 CHG 时**重新确认**（原裁定是「只登记」，不自动转为「现在就修」）。
- 不借本 CHG 扩充 M3 业务能力；不重新打开已暂停的 C2（博主搜索）与 E2（作者策略）。
- 不复活「只读业务流转视图」——已按用户 2026-09-23 裁定移出验收范围，ADR-0013 第 8 条的
  禁止性约束不变。
- 不把 M3 标记 DONE；签收仍属用户裁定。
- 不把 D9、D-scheduler-2 这两项**需产品决策**的问题自行定调（见下「待决」）。

## 顺序任务

### Task 1：错误映射收口（D1 / D7 / D8）

- 工作：把仓储层包私有错误翻译为 service 层导出错误（`errStrategyDuplicate`、
  `errCrawlTaskNotFound`），并为 `ErrCrawlerUnavailable` 补 `writeDiscoveryError` 映射。
- 验收：重名创建返回 `409 / 14007`；任务不存在返回 `404 / 14004`；未配置 crawler 返回可解释错误
  而非 `500 / 50000`。三项各有真实请求读回。

### Task 2：输入校验（D2）

- 工作：`schedule` 在 `createStrategy` / `updateStrategy` 校验取值属于
  `manual | interval:<N> | daily HH:MM`，非法值 `400 / 14006`。
- 验收：`garbage` 被拒；`interval:0`、`daily 25:00`、`daily 9:5` 等边界同样被拒；
  合法三形态均可创建。**需先确认在库脏数据（策略 id=7 的 `garbage`）的处置方式**。

### Task 3：`/run` 防重（D3，唯一影响验收项者）

- 工作：`createRun` 不再以空字符串作为计划键；补「已有 pending/running 任务」前置检查，
  或让唯一索引 `uq_crawl_tasks_strategy_schedule` 对在途任务生效。
- 验收：对同一策略连调两次 `/run`，pending 行数 `0 → 1`；周期触发路径的防重不回退（既有 6.6/6.7）。

### Task 4：来源方式标签（D6）

- 工作：UI 的「ID/链接发现」不再一律传 `source_type:'search'`；或明确该入口的本质并统一文案。
- 验收：经「ID/链接发现」入池的行在界面上显示正确来源；`link` 枚举的可达性有明确结论
  （接入或删除，不保留不可达枚举）。

### Task 5：验收脚本与文档（D10）

- 工作：`scripts/verify_m2_acceptance.py:71` 路径改为
  `internal/modules/cloudagent/service/compatibility.go`。
- 验收：原脚本（非临时副本）跑出 M2 静态跨仓矩阵全绿。

### Task 6：安全问题 S-1（**激活时需用户重新确认范围**）

- 待确认动作集：轮换 `api_key` 与 cookie → 停止跟踪该文件 → 加 `.gitignore` 与 `*.example` 模板
  → 评估历史清理。任一项均需用户明确授权后再做。

## 待决（需产品决策，先决策再排期）

- **D9**：上游空返回是否应区分为「查无结果」与「上游异常」。当前为如实透传（`errcode=0` 且空列表），
  用户界面无任何提示；`2/8` 次实测复现。
- **D-scheduler-2**：`daily HH:MM` 漏 tick 即丢当天，是否补「当天未跑则补触发」的兜底。
  既有设计、非本次引入；影响无人值守可靠性。

## 验收口径

1. 每项缺陷有**可复现的失败样本**与**修复后的真实读回**，不以代码观察代替验证；
2. 修复不引入回归：Cloud `go test ./...` 全包 PASS、Web Vitest 全绿；
3. 错误码字符串与响应信封**不新增语义漂移**（沿用既有 code 体系）；
4. D3 的修复必须同时保住周期触发路径的既有防重（6.6/6.7 不回归）。

## 提交边界

`wt-media-cloud` 与 `wt-media-workspace` 分仓提交，一步一 commit，「改逻辑」与「改文档/脚本」不混提交。

## 激活前置

1. `CHG-20260916-052` 已离开 `delivery/active/`（`delivery/active` 只允许一个 CHG，脚本硬校验）；
2. 用户就 S-1 的处置范围、D9 与 D-scheduler-2 的产品决策给出结论；
3. 缺陷清单与 `12-defects-and-security.md` 逐条对齐，无新增未登记项。
