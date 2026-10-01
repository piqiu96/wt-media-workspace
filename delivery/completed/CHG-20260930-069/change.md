# CHG-20260930-069：M4-A 素材详情与下载中心走查修正

- Status: DONE
- Level: `S`
- Milestone: `delivery/milestones/M4-content-production.md`
- Closure anchor: §4「闭环卡 M4-A：素材库与我的素材」
- Current repository: `wt-media-cloud`
- 依赖：M4-A 用户走查尚未签收；本 CHG 修正走查反馈，不激活 M4-C2。

## 1. 独立结果

素材库和我的素材以封面缩略图及素材 ID 识别每条内容；作者主页、平台原视频页面、视频大小与云端视频地址放在详情中。下载中心将未完成任务与最近终态分开展示。

## 2. 范围与边界

- Cloud 素材投影补充来源已有的 `cover_url` 和 `author_home_url`；不新增数据库字段。
- 新增受登录和素材业务范围校验的详情链接接口；仅视频准备完成时返回稳定对象 URL。地址由现有对象存储 endpoint、bucket、prefix 和对象 key 组成，素材列表与素材对象 body 不携带该 URL。
- 更新 Cloud OpenAPI 与 Business Schema；这是可选字段和新增读取接口，保持现有 API 向后兼容。
- Cloud Web 素材列表保留素材 ID（第一业务列）与「素材」识别列（封面、标题、来源平台副行；游戏仍为独立列）、文件状态、入库/加入时间与操作；作者、链接、文件大小移至共用详情抽屉。
- 「该素材是否已加入我的素材」不新增后端字段：素材库页同时读取 `/api/v1/my-materials` 并按素材 ID 做客户端 join（2026-09-30 用户裁定）。两条接口都是全量返回，join 的覆盖范围与现有视频状态、游戏筛选一致。
- 素材状态（`materials.status`，2026-09-30 走查六轮用户裁定「这是素材库的内部职责」）：新增一列 `status VARCHAR(16) NOT NULL DEFAULT 'available'`，取值 `available / paused / delisted`，列为素材库自有生命周期，与 `video_status` 并排不合并；Business Schema 的 `Material` 增该属性并列入 `required`（revision `2026.09.30.3`）。**本轮不含写路径**——没有任何接口能把一行改成 `paused` / `delisted`。
- 全站筛选栏统一为「字段标题 + 控件」，标题在控件**左侧**（2026-09-30 走查七轮用户裁定）；Select 的默认展示用「全部」，不再拿字段名（「文件状态」「游戏」）当 placeholder。范围 7 页：素材库、我的素材、内容池 crawl-tasks / 挖掘策略、用户管理、运营分组、游戏管理——前三类已有 `.filter-field` 包裹，后三页补齐。
- 我的素材列表与共用详情抽屉（2026-09-30 走查七轮，用户带提示词）：列收敛为「素材 ID | 素材（封面 + 标题 + 游戏 · 作者副行）| 文件状态 | 使用状态 | 加入时间 | 操作」；「移出」文案改为「放弃使用」；页面副标题由「你收藏的素材，可随时下载到本机」改为「已加入的素材，在这里下载、补充文件并进入后续生产」。使用状态是 `material_usages.status` 的展示（`active` → 使用中，`removed` → 已放弃），与素材状态（`materials.status`）、文件状态（`video_status`）三者各自独立，不合并（§7.2）。
- 使用状态的读取与恢复（同轮）：`GET /api/v1/my-materials` 不再只取 `status = 'active'`，改为两类关系行都返回；新增 `POST /api/v1/material-usages/{usage_id}/restore`，把一行改回 `active` 并清 `removed_at`。**不需要迁移**——`material_usages` 自 M4-A（`20260926_039`）起就带 `status VARCHAR(16) (active/removed)`、`removed_at` 与 `UNIQUE KEY uq_material_usages_user_material (user_id, material_id)`，「移出保留同一行、只改状态，故历史可追溯、可恢复」本来就是 Business Schema `MaterialUsage` 写下的设计。恢复与素材库的 `POST /materials/{id}/usages`（`CreateOrRestoreUsage`）落到同一行，两条路径幂等。
- 关闭统一到抽屉标题栏右上角的 `×`（2026-09-30 用户裁定「关闭按钮统一做到右上角（统一改组件统一）」）：页脚不再放「关闭」，只放业务动作并靠右收；没有业务动作时整条页脚不出现。范围是全站 `t-drawer`。**这一条不只是删两颗页脚按钮**：本仓装的 `tdesign-vue-next` 1.20.3 里 drawer 的 `closeBtn` 没有 `default`（同版本的 `dialog` 写着 `default: true`），不写 `:close-btn="true"` 的抽屉今天**没有 ×**——2026-09-30 用 headless Chrome 渲染核对过 DOM 与量测（`.t-drawer__close-btn` 在 `top: 16px; right: 8px`，落在 56px 高的页头里）。因此 12 个抽屉一律补上该属性，由站级守卫 `web/src/drawerFooterConvention.test.js` 钉住。本仓没有共享抽屉包装组件，「统一」落在守卫与规范条目（`前端交互规范.md` §6.3 / §9.1）上，不是落在某一个组件里——用户那句「改组件」按「改在组件这一层、不逐页写布局」执行，若要的是抽出包装组件需另立任务。
- 我的素材详情的「文件信息」卡增加本机下载落点（2026-09-30 用户裁定「已下载的素材，需要有展示下载目录的地方同时能打开目录快速找到原视频」，并指定「放在文件信息一栏里」；范围裁定为「折进 CHG-069 任务 17」）：值来自两处已经存在的事实——会话里这张 `file_transfer_tasks`（`asset_type=material` + `asset_id` + `purpose=user_download` + `execution_scope=local_agent` + `status=success` + `file_name`，服务端按 `created_at DESC, id DESC` 返回，取第一条）与 Desktop 侧量出来的 `local_saved_file_states`（`directory`）。**「已下载」由本机事实判定，不拿 `video_status === 'ready'` 冒充**——文件状态说的是云端那份源文件，本机下载进度从来不是它的含义。按钮只做一件事：在文件管理器里打开那一份所在的目录。这需要 Desktop 新增一个命令 `local_reveal_saved_file`（收**名字**不收路径，与 `local_open_saved_file` 同形，复用 `saved_files::find_in_known` 与 `commands::reveal` 的打开动作）：现有命令里没有能按名定位到目录的——`local_open_saved_file` 是 `open::that(文件)`，交给默认播放器打开视频本身；`local_open_place` 只认 app 自有目录的位置标签。因此本 CHG 从「只改 Cloud」扩到 `wt-media-desktop/src-tauri`；Tauri 命令载荷不在 `docs/contracts/` 的跨仓契约里，按 Desktop 仓 `AGENT-INDEX.md` 那句「命令载荷构成前端接口，变化时核对 Cloud 的 Vue 调用」在同一任务内两侧一起改。
- 下载中心分为“正在下载”（pending/running）和“最近完成”（success/failed/cancelled）。保留真实任务状态、取消、重试、重新下载和打开文件行为。
- 下载中心显示层合并（2026-10-01 用户裁定「一次点击在下载中心只显示一条记录，用状态区分阶段」）：一次点击在库里是两行（`compose_input_prepare` 云准备 + `user_download` 本机下载，同一毫秒同建），下载中心只显示 `user_download` 那一条——**展示层合并，DB 不动**。过滤必须在 `transferRows` **之后**：`taskState → needsCloudPreparation` 要看到兄弟云任务才知道「等待云端准备」，提前滤掉云行会退化成「排队中」。轮询闸门同时改为只对 `user_download` 判断。
- 素材页「文件状态」补全下载侧生命周期（2026-10-01 用户裁定「排队到传输都算下载中」「准备失败和本地下载失败都属于下载失败，用户不需要知道那么细致」）：`MaterialUsage` 增**按用户派生**的可选 `download_status`（后端按该用户最新一条 `user_download` 任务派生：pending/running→`downloading`、success→`downloaded`、failed/cancelled→`failed`，`''`=从未下载过；`omitempty` 让从未下载的行与旧响应字节一致），我的素材列表与共用详情抽屉的「文件状态」= `download_status` 优先 + `video_status` 兜底（`video_status=failed` 也呈现「下载失败」）。这是第四组状态维度，与冻结的 `video_status` 分开。
- 公开对象 URL 的前提是现有对象存储地址与桶策略允许公开读取；本 CHG 不修改桶 ACL 或发布外部配置。

## 3. 明确不做

- 不合并 `file_transfer_tasks` 两行：`compose_input_prepare` 是 M4-B/M5 合成管线预留的共享输入准备契约，CHECK 约束/去重键/租约模型/执行器都建立在两行协作上（Python Agent 只执行 `user_download`），只做展示层合并；
- 不改 `video_status` 冻结枚举、不改 使用状态 字段与来源；下载中心单条任务仍细分阶段（准备中/下载中/已完成）——两处说法按用户裁定保留差异（列表页简化、下载中心细分）；
- 素材库页（`MaterialLibraryPage`）无用户关系语义，不加下载状态（默认；要加再议）；判定只看 `user_download` + 该用户，不看 `compose_input_prepare`（云准备只通过 `video_status` 兜底参与）。

- 除任务 18/19 外，不改变 Local Agent 下载、保存目录、任务记录或完整性校验（任务 18 改下载引擎的故障分类与重试，任务 19 改落盘命名与保存目录的一层子目录，均经用户裁定并入本 CHG）；
- 不把对象 key、长期存储凭据或本机路径写入素材列表、任务记录或日志；
- 不向非详情接口返回云端视频 URL；
- 不包含合成策略、合成任务或 M4-C2；
- 不含**使用情况统计**（成片数、发布数、最近生产/发布时间、重复风险）与列表分页总数、各状态计数、服务端筛选参数：这些要跨成片与发布聚合，数据源尚不存在（见 `delivery/planned/CHG-20260930-071`，本 CHG 关闭后按队列激活）。本 CHG 内只落前端读取协议与展现样式，协议是 `material.usage`（`clip_count`、`published_count`、`last_produced_at`、`last_published_at`、`duplicate_risk`），声明在 `web/src/modules/materials/labels.js`；字段未到达时渲染占位，不兜底默认值。
- **素材状态不在本节**（2026-09-30 走查六轮用户裁定推翻任务 9 的「后端另立 CHG」归属）：素材生命周期是素材库的内部职责，不等外部数据，见 §2 与任务 12。暂停 / 下架的**写路径**仍不在本 CHG 内，也没有登记给任何 CHG——谁来暂停、在哪一页操作尚未裁定。
- 同样因为数据未到，列表顶部的统计卡与状态筛选**本轮不动**：在缺 `status` 的数据上挂一排「素材状态」计数卡与筛选器，每一档点下去都是 0 行。这与页面上那条既有判断同源（游戏筛选项只列已加载数据里真出现过的值）——列一个点下去没有任何行的选项，和「筛了但服务端没筛」是同一种误导。它们随数据一起落地。
- **上传素材**（2026-09-30 走查七轮，用户裁定「暂时先不做」）：production 模块 7 条路由里没有上传端点，`materials` 也没有无来源的素材。我的素材页面级主操作本轮仍只有「刷新」。
- **使用状态的 tab 与计数**（同轮裁定「不用做」）：列表接口返回裸数组、`LIMIT 200`、无 `total`、无聚合——见 `delivery/planned/CHG-20260930-071` §0 盘点表。使用状态这一轮只作为**列**存在。2026-09-30 用户再次裁定「顶部 tab 切换不需要」：清单页顶部不加使用状态 tab，详情抽屉也不加标签页（自任务 11 起就是平铺一页）——两种读法都不新增 tab，本轮两者都不动。
- **「来源」列**（同轮裁定「不做这一列，以后再说」）：`materials.source_content_id` 是 `NOT NULL` 加 `UNIQUE`，每条素材都必须挂一条来源内容；加上上传不做，「素材库 / 手动添加」的第二个值无处产生。做出来是一列恒等于单个值的字段，正是用户提示词里那句「不要伪造新字段」要挡的东西。
- **「已中断」这一档使用状态**：`material_usages.status` 的 `CHECK` 只允许 `active / removed`，没有第三档。用户同轮裁定其含义为「准备 / 下载中途断了」——但那是文件状态那一维，与规范 §7.2 那句「可以同时存在 `使用中 + 下载失败`，不应为了页面简单重新制造混合状态」互斥；同时用户提示词自己写着「如果当前代码尚未正式存在某个状态，不要直接新增数据库 enum」。两种读法互相推翻，**本轮不实现、不猜**，等用户裁定机制（加第三个 enum 还是别的）。§7.2 里「使用状态：使用中 / 已放弃 / 已中断」那行因此仍是规范先行、实现未跟。
- **「文件异常」这一档**：`video_status` 四态（`not_downloaded / downloading / ready / failed`）里没有它，云端列表也不返回本机文件状态——它与规范 §7.4 的「文件异常 → 重新下载」今天都收在 `failed` 上。本轮按四态分支，不新造状态。

## 4. 验收标准

- 两个素材列表都有封面列与独立素材 ID 列（ID 为第一列）；无封面或图片加载失败时显示占位图；标题可点击跳转来源平台落地页；下载按钮文案为「下载」，按钮下无提示小字。
- 详情抽屉以独立区块展现来源内容池统计（点赞、收藏、评论、分享；抖音接口对全部来源行 `play_count` 恒为 0，经用户裁定 2026-09-30 不展示「播放」项，`view_count` 字段保留在契约中不渲染）。
- 行内不再提供作者、平台链接或文件大小；详情可打开作者主页、平台原视频页面和云端视频 URL，并准确显示文件大小。
- 越权和不存在素材不能取得云端视频 URL；视频未就绪时不返回地址；已就绪素材返回由当前对象存储配置生成的稳定 URL。
- 下载中心两个标签的计数及列表与任务事实一致；成功、失败、取消都进入最近完成，pending、running 只进入正在下载。
- 交互对齐 `docs/standards/前端交互规范.md`（2026-09-30 走查三轮，用户裁定）：三页「查看」统一为「详情」；素材库行操作为「详情 | 加入我的素材」，素材库行与其打开的详情抽屉不提供下载（下载归「我的素材」）；我的素材行操作为「详情 | 下载（`video_status=failed` 时文案为「重试」）| 移出」，按钮不超过 5 个全部平铺（规范 §5.6，2026-09-30 用户补充裁定），移出保留危险样式；我的素材打开的详情抽屉提供下载/重试、不提供「加入我的素材」。
- 素材库列表（2026-09-30 走查四轮，用户裁定 + 设计图）：两列表列收敛为「素材 ID（第一列）| 素材（封面 + 标题 + 来源平台副行）| 游戏 | 文件状态 | 入库时间 | 操作」；「视频状态」列名改为「文件状态」（取值不变，仍是 `video_status` 四态文案）；已加入我的素材的行，主操作改为「去我的素材」并跳转 `/my-material`（cloud 与 desktop router 的既有路由名均为 `MyMaterial`），未加入的行仍是「加入我的素材」。副行不含游戏名（设计图为「平台 · 游戏」）——游戏已独立成列，同一行重复渲染同一个值。此处与设计图的偏差已在 2026-09-30 走查六轮由用户裁定确认（「游戏是独立行」），登记撤销。
- 素材库上下文只有在**加入成功后的即时反馈**里才出现下载：Toast 提供「立即下载」（仅 `video_status=ready` 时出现）与「去我的素材」。这是对上一轮「素材库不提供下载入口」裁定的修订——修订范围仅限这条反馈，行与详情抽屉仍不提供下载入口。
- 共用详情抽屉（2026-09-30 走查四轮）：顶部为封面 + 标题 + 「游戏 · 平台 · 作者」副行 + 状态徽章（文件状态，另有加入状态徽章）；正文分「概览 / 文件信息 / 来源信息」三个标签，概览含基本信息与来源内容池统计，文件信息含文件状态、大小、准备完成于、校验值与云端视频，来源信息含平台、作者、发布时间与平台原视频；底部为「关闭」与上下文主操作，不出现「确认 / 取消」（规范 §6.3）。
- 素材库列表（2026-09-30 走查五轮，用户反馈 + 设计图）：列集合为「素材 ID | 素材 | 游戏 | **素材状态** | 文件状态 | **使用情况** | 入库时间 | 操作」（8 列），两个新维度并排且不合并（§7.2）。素材状态自任务 12 起有真值（`materials.status`）；使用情况的数据服务端仍未返回，渲染设计图的两行骨架（`成片 - · 发布 -` / `最近发布 -`）。**不得出现兜底默认值**——`row.status || 'available'` 这类写法会把一条读不到状态的素材静默画成「可用」。
- 素材库列表（同上，设计图要点④）：暂停与下架**禁止新增领取**——`未领取 + 非可用` 的行不提供主操作，渲染 `—`；**已领取**的行任何状态下仍给「去我的素材」（§16.2「历史关系和结果继续保留」）。任务 12 之后 `status` 已是真值，这条分支已是活的规则（今天恒为 `available`，因为没有任何写路径能暂停一行）。`POST /materials/{id}/usages` 不校验状态，拦截点只有前端这一处，**不是安全边界**。
- 共用详情抽屉（2026-09-30 走查五轮）：顶部为 hero（160×100 封面 + 标题 + 「游戏 · 平台 · 作者」副行 + 素材状态/文件状态/加入状态徽章，素材状态缺值时不出徽章）；正文每一段信息是一张有边界的卡（`.detail-card`），照内容池详情的框；概览 = 使用情况 + 基本信息，文件信息卡标题带文件状态徽章，来源信息 = 来源信息 + 来源内容池统计（走查五轮从概览移入，它是来源行的快照）；页脚左「关闭」、右上下文主操作，且钉在抽屉底部不随标签高度移动。
- 共用详情抽屉（2026-09-30 走查六轮，用户三条反馈）：正文五段信息**平铺在一页**，不再分标签（`t-tabs`、`t-tab-panel` 与 `activeTab` 都不存在），顺序为 使用情况 → 基本信息 → 文件信息 → 来源信息 → 来源内容池统计；hero 标题在 `material.source_url` 存在时是可点击外链、跳来源平台落地页，没有落地页时退回普通文本；hero 副行作者在 `material.author_home_url` 存在时可点击跳作者主页；副行只留「平台 · 作者」，游戏不入副行（它与列表的「游戏」列、详情「基本信息」里的游戏行重复同一个值）。
- 素材状态（2026-09-30 走查六轮追加裁定，见任务 12）：`GET /api/v1/materials` 与 `GET /api/v1/materials/{id}` 的每条素材带 `status`，取值 `available / paused / delisted`，与 `video_status` 相互独立；列表「素材状态」列与详情徽章渲染真值，缺值渲染 `—`、不兜底。库列为 `NOT NULL DEFAULT 'available'`，所以键恒在。**今天每一行都读作「可用」**——没有任何接口能把一行改成 `paused` / `delisted`，这是这批素材的真实状态，不是占位，但也不是一个能用起来的状态维度。
- 全站守卫测试：`web/src/**/*.vue` 里每个 `t-drawer` 必须对页脚表态（给 `#footer` 插槽或显式写 `footer` 属性）。TDesign 的 drawer footer 默认 `true`，不表态就渲染一对「取消 / 确认」。实测全站 12 个抽屉曾有 2 个漏写；`t-dialog` 不在扫描范围内（那对按钮正是它的用途）。
- 筛选栏（2026-09-30 走查七轮）：7 个管理列表的每一个筛选控件都有一个可见的字段标题，标题在控件左侧；判定不靠肉眼——守卫测试扫 `web/src/**/*.vue` 里所有含 `filter-row` 的页面，逐个断言控件被 `.filter-field` 的标题包裹、且 Select 的 placeholder 不等于它自己的字段标题。查询用 Primary、重置用次级（§4.3）。
- 我的素材（同轮）：页面副标题为「已加入的素材，在这里下载、补充文件并进入后续生产」；列表列集合为「素材 ID | 素材 | 文件状态 | 使用状态 | 加入时间 | 操作」；操作列文案为「放弃使用」而不是「移出」。使用状态列与文件状态列并排且不合并（§7.2）：`active` → 「使用中」、`removed` → 「已放弃」，缺值渲染 `—`、不兜底。
- 行操作按「使用状态 × 文件状态」分支，按钮总数 ≤5 时全部平铺、超过 5 个才出现「更多」（§5.6，2026-09-30 走查三轮用户补充裁定）——用户提示词里那套「3 个动作也进更多」的写法不采用，因为它是 3 个。使用中 + 可下载为「详情 | 加入合成 | 放弃使用」；使用中 + 准备失败为「详情 | 重试 | 放弃使用」；已放弃为「详情 | 恢复使用」。
- 恢复使用（同轮）：已放弃的行能直接恢复，走 `POST /api/v1/material-usages/{usage_id}/restore`；恢复后该行回到使用中，且与在素材库里再点一次「加入我的素材」落到同一行（`uq_material_usages_user_material` 保证一行）。越权（他人的 usage）与不存在的 usage 不生效。
- 共用详情抽屉（同轮）：hero 下是小型状态 Badge（使用状态 + 文件状态），不是横跨整页的状态色块（§7.1「状态颜色不得替代按钮层级」）；正文首段是「当前进度 / 使用情况」（文件状态、使用状态、加入时间、下一步），其后依次是文件信息、来源信息、来源内容统计；页脚按状态给真实业务动作，不出现「确认」。「下一步」是前端提示文案，不新增业务状态。
- 抽屉关闭统一（2026-09-30 用户裁定，见 §2 与任务 16）：全站 12 个 `t-drawer` 的页脚不含「关闭」按钮，关闭入口是标题栏右上角的 `×`；页脚只放业务动作并靠右收。守卫测试同时钉两条：页脚里不得出现 `关闭`（分母与不经切片的正则读数对齐，切片器坏掉时两数对不上）、每个抽屉必须写 `:close-btn="true"`（不写就没有 ×）。素材详情与本机扫描结果两个抽屉的页脚「关闭」在本任务撤掉；本机扫描结果的页脚在「没有可接受的变化」时整条不出现，不留空条。
- 我的素材详情（2026-09-30 用户裁定，见 §2 与任务 17）：已在本机下载过的素材，在「文件信息」卡里显示本机那一份所在的目录，并给一颗「打开目录」；未下载过、或本机事实读不到（浏览器构建、Desktop 还没扫到）时**整行不出现**，不写「未下载」——与下载中心同一条约定（读不到本机 ≠ 文件不在）。目录是 Desktop 量出来的，不是前端拼的路径；按钮的动作是打开该目录（不在文件管理器里选中该文件，见任务 17「不在本轮」）。
- 定向 Go/Web 测试、Desktop `cargo test`、Cloud 与 Desktop Web 构建通过；真实桌面页面留给用户走查签收。
- 下载中心（2026-10-01 任务 20）：一次点击下载只显示**一条**记录，从「准备中（等待云端准备）→ 下载中 → 已完成」随任务事实推进；DB 里仍是两行（`compose_input_prepare` + `user_download`），`file_transfer_tasks` 无变化。
- 我的素材列表「文件状态」列（任务 20）：点击下载即「下载中」，成功后「已下载」，重新下载失败显示「下载失败」（`video_status` 与 `download_status` 两种失败都呈现「下载失败」）；从未下载过的已就绪素材仍显示「可下载」；从未下载过的准备失败素材显示「下载失败」。

## 5. 有序任务

1. 先补 Contract/Repository/Service 测试，再让素材 API 返回封面和作者主页；
2. 为已就绪且有权访问的素材生成稳定对象 URL，更新 Cloud API/Business Schema；
3. 修改两个列表与共用详情抽屉，并测试空封面、缺链接和未就绪状态；
4. 将下载中心任务分组并提供两个可切换标签；
5. 跑定向测试及两种 Web 构建，启动桌面包供用户验收；
6. （2026-09-30 走查反馈）列表 ID 列移至第一列；标题改为蓝色可点击，跳转来源平台落地页；「下载到本机」按钮文案改为「下载」，删除按钮下方的提示小字（状态徽章已说明）；素材投影补充来源行的内容池统计（播放/点赞/收藏/评论/分享），在详情抽屉以独立区块展现。封面数据链路核对：`source_contents.cover_url` 已经由投影 JOIN 带出，无需再同步；走查所见占位图疑为来源 CDN 签名地址过期，属采集数据问题，不在本 CHG 内修。
7. （2026-09-30 走查二轮）素材 ID 显示不带 `#` 前缀（两列表与详情抽屉）；「统计全部为 0」根因是运行中的 Cloud 为旧编译产物（m2b 对已健康服务不重启），强制重启后 API 返回真实统计；抖音接口对全部 518 行带统计的来源行 `play_count` 均为 0，经用户裁定统计区块不展示「播放」项。
8. （2026-09-30 走查三轮，交互对齐 `docs/standards/前端交互规范.md`；用户裁定拆开执行——素材库/我的素材并入本 CHG，内容池另立 CHG-20260930-070 待本 CHG 关闭后激活）「查看」统一为「详情」；素材库行收敛为「详情 | 加入我的素材」，素材库上下文（行与详情抽屉）移除下载；我的素材行收敛为「详情 | 下载（failed 显示「重试」）| 移出」（按钮 ≤5 全平铺，§5.6 用户补充裁定：超过 5 个才把低频收敛进「更多」）；共用详情抽屉按上下文提供动作。范围仅交互层，不动后端与契约；需要新后端能力的状态矩阵（已领取/已放弃/生命周期/加入合成）不在本轮。
9. （2026-09-30 走查四轮，用户带设计图，裁定「先落纯交互层，后端另立 CHG」）素材库列表列收敛与详情抽屉分标签重构：
   1. 先改 `MaterialLibraryPage` / `MyMaterialsPage` / `MaterialDetailDrawer` / `ListPageConventions` 的测试，钉住目标形态（列集合与列名、「去我的素材」分支、抽屉三标签、关闭 + 主操作），确认红；
   2. 素材库页 join `/api/v1/my-materials` 得出「已加入」集合，行主操作按它分支；
   3. 「加入我的素材」成功后 Toast 提供「立即下载」（仅 ready）与「去我的素材」，并把该行翻成「去我的素材」；
   4. 抽屉按「概览 / 文件信息 / 来源信息」重组，顶部加来源副行与状态徽章，底部改为关闭 + 上下文主操作；
   5. 规范 §7.2 的示例状态词「已退役」改为「已下架」（用户 2026-09-30 裁定用词），并登记对应新 CHG；
   6. 定向 vitest 与双构建；重启桌面包供走查。
   不在本轮：素材状态生命周期、使用情况统计、分页计数与服务端筛选参数（另立 CHG，见 §3）。
10. （2026-09-30 走查五轮，用户四条反馈）状态维度、详情框与页脚：
   1. 先改 `labels.test.js` / `MaterialLibraryPage.test.js` / `MaterialDetailDrawer.test.js` / `ListPageConventions.test.js` / 新增 `datetime.test.js`、`drawerFooterConvention.test.js`，钉住目标形态，确认 19 红；
   2. `labels.js` 声明两组协议（`material.status`、`material.usage`）与展示函数：取值文案、色调、缺值 `—`、`0` 与缺省之分；`shared/utils/datetime.js` 增 `formatDate`（只要日期，供「最近发布」那一格）；
   3. 素材库列在「游戏」与「文件状态」之间加「素材状态」，在「文件状态」与「入库时间」之间加「使用情况」（两行）；`canAdd(row)` 落地 §16.2 的暂停/下架禁止新增领取，并在无主操作时画 `—`；
   4. 详情抽屉按内容池详情的框重做：hero + 五张 `.detail-card`，来源内容池统计移入「来源信息」，页脚改左关闭右主操作并接管 footer 插槽；
   5. 全站抽屉页脚守卫测试落地，修掉它扫出的两个漏写抽屉（`ProxyPage.vue`、`shared/ui/templates/DetailDrawerPage.vue`）；
   6. 规范 §7.2 文件状态文案改为「未准备 / 准备中 / 可下载 / 准备失败」并补用词说明，§16.2 操作矩阵补「已暂停 / 已下架 + 已领取」一行；
   7. 定向 vitest、全量 vitest、双构建；重启桌面包供走查。
   不在本轮：两个新维度的后端字段与投影、列表统计卡与状态筛选（见 §3）。`status` / `usage` 的服务端实现写入 `delivery/planned/` 的后端 CHG 草案。
11. （2026-09-30 走查六轮，用户三条反馈：游戏是独立行 / 详情取消标签平铺一页 / 标题与作者可点击跳转）纯交互层：
    1. 先改 `MaterialDetailDrawer.test.js`，钉住四条目标形态（无标签与 `activeTab`、五张卡依序、标题外链、作者外链、副行不含游戏），确认 4 红；
    2. 删 `activeTab` 与 `t-tab-panel`，五个面板平铺为 `.detail-card`，间距改由 `.detail-workspace` 的 `gap` 给；
    3. hero 标题与副行作者挂 `source_url` / `author_home_url`，无落地页时退回普通文本；副行去掉游戏名；
    4. 定向 vitest、全量 vitest、双构建。
    证据 `evidence/task11-walkthrough-six.md`，提交 `004272d`。
12. （2026-09-30 走查六轮追加裁定：素材状态是素材库的内部职责，需要完成状态展示；对澄清问题的裁定为「素材库新增自有字段」）后端 + 契约 + 前端读真值：
    1. 先改契约（`Material` 增 `status` 枚举并列入 `required`，revision `2026.09.30.3`）与 `wire_test.go` 分母（24 → 25），确认红落在「契约承诺了、body 给不出」而非编译错误；
    2. 迁移 `20260930_042_material_status.sql`：加 `status VARCHAR(16) NOT NULL DEFAULT 'available'` 与 `CHECK`，只加列不回填；
    3. `model.MaterialStatus` + 三常量 + 结构体字段；投影列与 `scanMaterial` 增 `m.status`；repository 测试钉住列清单与读回值；
    4. 前端注释回写为「字段已落地」，列表列与详情徽章读真值（缺值仍渲染 `—`）；
    5. `go test ./...`、定向 vitest、全量 vitest、双构建；`up --force-restart` 后读 API 与库，并做一次「改成 paused → API 变化 → 还原」的阳性对照。
    证据 `evidence/task12-material-status.md`，提交 `71deb48`。
    不在本轮：暂停 / 下架的写路径（无人裁定发起方与操作页）；使用情况（仍在 `CHG-20260930-071`）。
13. （2026-09-30 走查七轮，用户提示词第「四」「筛选区域」节 + 末尾「统一到整个项目」）筛选栏统一「标题 + 控件」，纯前端、跨 7 页：
    1. 先写守卫测试：扫 `web/src/**/*.vue` 里含 `filter-row` 的页面，钉住「每个筛选控件都被 `.filter-field` 的标题包裹」「Select 的 placeholder ≠ 它自己的字段标题」「查询按钮 theme=primary、重置为次级」；同时改 `ListPageConventions` 与各页既有断言，确认红——红线要落在**缺标题的那三页**（用户管理 / 运营分组 / 游戏管理）上，只红在别处说明扫的位置不对；
    2. 素材库、我的素材、内容池两页已用 `.filter-field`（后两页的改动仍在工作区未提交，一并纳入本次提交），本轮补「全部」默认值：Select 加一条 `value: ''` 的「全部」选项并置默认，替掉拿字段名当 placeholder 的写法；
    3. 用户管理、运营分组、游戏管理三页的裸 placeholder 控件套上同一套 `.filter-field`，并按 §4.3 补齐「查询 / 重置」；
    4. 定向 vitest、全量 vitest、双构建。
    不在本轮：把筛选改成服务端参数（见 §3 与 `CHG-20260930-071` Q-06）。
14. （2026-09-30 走查七轮，用户提示词第「一、二、五、六、七、九、十、十一」节）我的素材列表与共用详情抽屉重构，纯前端：
    1. 先改 `MyMaterialsPage.test.js` / `MaterialDetailDrawer.test.js` / `labels.test.js`，钉住目标形态（副标题、列集合、放弃使用文案、使用状态列、≤5 平铺、hero 小型 Badge、正文四段顺序、页脚无「确认」），确认红；
    2. `labels.js` 增使用状态协议（`material.usage_status`：`active` / `removed` → 使用中 / 已放弃），与 `material.status`（素材库自有）、`video_status`（文件状态）三组并列，函数一律缺值渲染 `—`；
    3. 列表列收敛为 6 列，游戏并入「素材」格副行（`游戏 · 作者`）；「移出」→「放弃使用」；
    4. 行操作按「使用状态 × 文件状态」分支，≤5 全平铺、超过 5 个才出现「更多」；
    5. 共用详情抽屉：hero 下改小型 Badge 组，正文首段换成「当前进度 / 使用情况」并带「下一步」提示文案，文件信息 / 来源信息 / 来源内容统计顺延，页脚按状态给动作；
    6. 副标题改写；定向 vitest、全量 vitest、双构建。
    不在本轮：使用状态的 tab 与计数、来源列、已中断、文件异常（见 §3）。
15. （2026-09-30 走查七轮，用户裁定「其他的前后端一起改」）使用状态的读与恢复，后端 + 契约 + 前端：
    1. 先改 Go 测试钉住新行为（`repository` 的关系行读回含 `removed`、`service` 的恢复幂等与越权拒绝、`handler` 的路由与错误码），确认红；
    2. `ListMyMaterials` 的 SQL 去掉 `status = 'active'`，两类关系行都返回，`removed_at` 随行带出；
    3. 新增 `RestoreMaterialUsage`（Repository → Service → Handler）与路由 `POST /api/v1/material-usages/{usage_id}/restore`，条件更新 `status = 'active' AND removed_at IS NULL`，受影响 0 行时按「已是他人的行 / 已恢复」区分错误；
    4. `contracts/cloud-api/v1/content-production.openapi.yaml` 增该路径；Business Schema `MaterialUsage` 已是 `active / removed`，不改；
    5. 前端接上：使用状态列读真值、已放弃的行给「恢复使用」，恢复后重取列表；
    6. `go test ./...`、全量 vitest、双构建；`up --force-restart` 后做一次「放弃 → 读回 removed → 恢复 → 读回 active」的真实往返，并核对库里的 `removed_at` 被清掉。
    证据 `evidence/task15-usage-restore.md`（原写 `evidence/task13-15-walkthrough-seven.md`，
    实际落成时 13、14 各自成文）。两处与计划不符、已在证据 §5/§4 登记：恢复的语句不返回
    bool（0 行能描述的唯一结果就是「已在使用中」，即调用方要的状态）；列表排序由 `updated_at`
    改 `created_at`（页面上那一列是「加入时间」，且改状态不该让行跳位置）。
    没有迁移——`material_usages` 自 M4-A 起就是这个形状（见 §2）。
    不在本轮：上传素材、使用状态 tab 与计数、来源列、已中断（见 §3）。
16. （2026-09-30 用户对走查图五条裁定的第 5 条）抽屉关闭统一到右上角，纯前端：
    1. 先改 `MaterialDetailDrawer.test.js` / `drawerFooterConvention.test.js` / `ProfilesPage.test.js` 钉住目标形态（页脚无「关闭」、页脚只剩业务动作并靠右、每个抽屉带 `:close-btn="true"`），确认红；
    2. `MaterialDetailDrawer` 与 `ProfilesPage` 扫描抽屉撤掉页脚那颗「关闭」，`ProfilesPage` 的页脚改用 `:footer="scanAcceptsChanges"` 门（没有可接受的变化时整条不出现，否则 TDesign 会留下一道空条）；
    3. 12 个 `t-drawer` 全部补 `:close-btn="true"`——不写就没有 ×（`tdesign-vue-next` 1.20.3 的 drawer `closeBtn` 无 default，见 §2）；
    4. 站级守卫：页脚不得含「关闭」（切片按标签配对，分母与 `hasFooterSlot` 正则对齐）；每个抽屉必须启用 ×；
    5. `前端交互规范.md` §6.3 / §9.1 回写规则；定向 vitest、全量 vitest、双构建。
    证据 `evidence/task16-drawer-close-header.md`。
    不在本轮：抽共享抽屉包装组件（本仓没有；用户那句「统一改组件统一」按第 3 步执行，若要包装组件需另立任务）、顶部 tab（§3）。
17. （2026-09-30 用户裁定「我的素材的详情里还需要加一项，已下载的素材，需要有展示下载目录的地方同时能打开目录快速找到原视频」，并指定「放在文件信息一栏里」；范围裁定为「折进 CHG-069 任务 17」）本机下载落点，Desktop + Cloud 两仓：
    1. 先红：`downloadFacts.test.js` 钉住「从任务表里选出这个素材本机那一份的文件名」（只认 `execution_scope=local_agent` + `purpose=user_download` + `status=success` + 有名字 + `asset_id` 相符；按服务端给的顺序取第一条，其余一律不选）；`desktopBridge.test.js` 钉住新命令名的字面量、浏览器里拒绝、空名字拒绝；`MaterialDetailDrawer.test.js` 钉住「文件信息」卡里有这一行、只在 `mine` 上下文出、值来自 `local_saved_file_states` 而不是前端拼的；
    2. Desktop 新增 `local_reveal_saved_file(name)`（`commands/downloads.rs`），复用 `saved_files::find_in_known` 与 `commands::reveal` 的目录打开；注册进 `generate_handler!`；取父目录这一步提成纯函数并单测（含「没有父目录」那一支）；
    3. Cloud：`downloadFacts` 增选名字的纯函数，`desktopBridge` 增 `revealSavedFile`，共用详情抽屉在 `mine` 上下文里读一次任务表 + `savedFileStates([name])`，在「文件信息」卡渲染目录与按钮；
    4. Desktop `cargo test`、定向 vitest、全量 vitest、双构建；`up --force-restart` 后用真实任务表读一次目录，并核对新命令已在 Rust 侧注册。
    证据 `evidence/task17-download-directory.md`。
    不在本轮：在文件管理器里**选中**那个文件（`open -R` / `tauri-plugin-opener` 是平台分支，本仓 `open` 这个轮子只做到「打开目录」；`bundle.targets` 是 `all`，写一条只有 macOS 能跑的分支等于另外两个平台拿不到实现）；「已下载」这一维不进列表列与筛选（用户只说了详情）。
18. （2026-09-30 用户裁定「帮我解决当前下载不成功的问题」，修法范围「改 Agent 引擎 + 我留意基建」；故障取证见 checkpoint「走查反馈四条」第③条——丢包 16.5% 的链路上，早断流被归成 `Integrity`（丢 part 从头下）、连接失败被归成非 retryable 的 `SourceUnavailable`，两者都把坏链路变成终态）下载引擎硬化，Agent 一仓：
    1. 先红：`tests/test_transfer_source.py` 与 `tests/test_material_download_executor.py` 钉住目标分类——早断流 → `download_stalled` 且 part 保留续传；unreachable host → retryable；签名过期仍非 retryable；secret-policy 全绿；:1096 词表不变；
    2. `executors/material_download.py` 末尾大小校验：`written < total`（早断）改抛 `Stalled`（retryable、不丢 part），over-delivery / 摘要不符仍 `Integrity`；
    3. `clients/transfer/source.py`：`URLError` 非超时与 `OSError` 从 `SourceUnavailableError` 改抛 `SourceStalledError`；`HTTPError`（签名过期）与 `ValueError`（畸形地址）保持非 retryable；
    4. `clients/cloud/client.py` `_http_transfer_transport`：捕 `URLError`/`TimeoutError` → `TransferUnavailableError`（心跳/进度/complete 的网络失败从 `executor_error` 终态改为 `LeaseUnconfirmed` 重试）；
    5. 全量 Agent 测试；在丢包链路上实测一条断链重试到完成。
    证据 `evidence/task18-download-engine.md`。不新增下载错误码（复用 `download_stalled`）；契约 `local-error-codes/v1/transfer.yaml` 不动。
19. （2026-09-30 用户裁定「对于文件名按照日期/游戏-素材ID进行命名」；命名形状「日期目录不带横杠 + 文件名 `游戏-素材ID`」，无游戏兜底 `未分类`，日期取下载日期 Agent 本机时钟）落盘命名改 日期/游戏-素材ID，Agent + Cloud + Desktop + Contract 四侧：
    1. Contract：`LocalLease` 增可选 `game_name`；`Completion.file_name` 模式放宽为至多一层子目录 `^[^/\\]+(?:/[^/\\]+)?$`；`info.version` → `2026.09.30.1`；`compatibility.go` 与 `contract-map.yaml` 同步；
    2. Cloud：迁移 `20260930_043_file_transfer_game_name.sql` 加 `game_name VARCHAR(64) NULL AFTER asset_title`；production `CreateDownload` 用 `identityservice.ResolveGame` 解析游戏名 → `CreateUserDownloadInput.GameName`；filetransfer 落库 + `leaseBody` 带出；前端不动（`file_name` 透传）；
    3. Agent：`DownloadSink.file_name` 改 `日期/游戏-素材ID`（`today` 注入可测试），executor `_prepare` 用 `lease.game_name`（空 → `未分类`），`commit` 对日期子目录 `mkdir`；
    4. Desktop：`file_name_of` 放宽为一层相对子目录 + 文件名（逐段校验、拒深层/绝对路径），`entry_in` 一层下钻查日期目录，`find_in_known`/`scout`/`presences` 经 `entry_in` 自动生效；
    5. 三仓测试 + 契约核对 + m2b 端到端：真实下载落 `20260930/三角洲行动-30.mp4`，详情「本机下载目录」与「打开目录」在日期目录生效。
    证据 `evidence/task19-date-game-naming.md`。不改后端 API 语义/数据库状态枚举/权限模型；`<标题>` 在下载中心记录里保持。
20. （2026-10-01 用户裁定「一次点击在下载中心只显示一条记录，用状态区分阶段」「排队到传输都算下载中」「准备失败和本地下载失败都属于下载失败」）下载中心显示层合并 + 素材页「文件状态」补全下载生命周期，Cloud 一仓（后端 + 前端）：
    1. 先红：filetransfer `LatestUserDownloadStatuses` 仓存测试（多条取最新一条、空 ID 列表不查询、命中/空集）与 service 测试（透传用户、`userID <= 0` 拒绝）；production `ListMyMaterials` 派生测试与映射函数 `downloadStatusOf`（pending/running→downloading、success→downloaded、failed/cancelled→failed、''→空）测试；wire_test 分母 9 → 10；
    2. 后端：filetransfer 仓存新增 `LatestUserDownloadStatuses(userID, materialIDs)`（`requested_by=? AND asset_type='material' AND purpose='user_download' AND asset_id IN (…)`，`ORDER BY created_at DESC, id DESC` 首见去重=最新一条）→ Store 接口 + service 方法 + `operations.go` wired 函数；production `TransferCreator` 接口接线 → `ListMyMaterials` 建好 `visible` 后批量查、把原始任务状态映射为 `MaterialUsage.DownloadStatus`（`json:"download_status,omitempty"`，与 `status` 平级按用户派生）；
    3. 契约（增量兼容）：`content-production.yaml` `MaterialUsage` properties 增**可选** `download_status` enum [downloading, downloaded, failed]，revision `2026.10.01.1`；冻结 `video_status` 枚举不动；
    4. 前端 `labels.js`：增三档 下载中(info)/已下载(success)/下载失败(danger)，不改 `VIDEO_STATUSES` 冻结数组；
    5. 前端列表与详情：`MyMaterialsPage` 的 `toRows` 带 `download_status`，文件状态 cell 按 `download_status` 优先 + `video_status` 兜底；`MaterialDetailDrawer` 从已拉的 `transfer.listTasks()` 就地派生同一语义（mine 上下文）；
    6. 下载中心：`rows` 在 `transferRows` **之后** `.filter((row) => row.task.purpose === 'user_download')`（提前滤掉云行会让 `needsCloudPreparation` 退化），轮询闸门 `hasLiveTask` 改对 `user_download` 判断；
    7. `go test ./...`、全量 vitest（web/ 下）、双构建；`up --force-restart` 后走查：点一次下载 → 下载中心一条（准备中→下载中→已完成）；素材页 文件状态：点击即「下载中」、成功后「已下载」、重下失败「下载失败」、从未下载的已就绪素材「可下载」；DB 依旧两行。
    证据 `evidence/task20-one-row-download-status.md`。不合并 DB 两行、不改 `video_status` 枚举、下载中心保留细分阶段（见 §3）。
21. （2026-10-01 用户裁定「下载的文件名修改 日期/游戏名-ID-发布时间-标题名」）命名规则再改 + 修复任务 19 的 complete 400 缺陷，Agent + Cloud + Contract 三侧：
    1. 先红：Cloud `TestCompleteTaskEnforcesTheFrozenOneSubdirectoryNamePattern` 钉住运行时校验（`20261001/三角洲-31.mp4`、`a/b.mp4` 放行；`a\b.mp4`、`a/b/c.mp4`、`/abs.mp4`、`a/b.mp4/`、`a//b.mp4`、256 字节拒绝），红在「新语义 vs 旧 `strings.ContainsAny(/\\)` 校验」；Agent executor 默认租约带 `title` 后命名形状红（红还先撞出实现丢扩展名圆点的 bug）；
    2. 修复任务 19 缺陷：Cloud `service.go` complete 校验与契约 `Completion.file_name` pattern `^[^/\\]+(?:/[^/\\]+)?$` 对齐（`validCompletedFileName`：至多一层相对子目录、两段非空、不含 `\`、拒绝对路径/两层/`.`/`..`，空名=可选键放行）——否则新形状 `20261001/三角洲行动-30-20260922-….mp4` 同任务 19 一样被 400 卡死；
    3. Contract：`LocalLease` 增**可选** `published_at`（format date-time，description 说明用于命名）；`info.version` → `2026.10.01.1`；`compatibility.go` 与 `contract-map.yaml` 同步（最小兼容版本 `2026.07.14.7` 不动）；
    4. Cloud：迁移 `20261001_044_file_transfer_publish_time.sql` 加 `published_at DATETIME(6) NULL AFTER game_name`；production `CreateDownload` 把 `material.PublishedAt` 经 `CreateUserDownloadInput.PublishedAt` 传入；filetransfer 落库 + `scanTask` 读回 + `leaseBody` 带出（仿任务 19 game_name 全链路）；
    5. Agent：`TransferLease` 增可选 `published_at: date | None`（`parse_lease` 宽容解析，不可解析→None→省略）；`DownloadSink.file_name` 新签名 → `日期/游戏名-ID[-YYYYMMDD][-标题].ext`（发布段非空才拼、空则省略；标题 `_sanitize` 消毒 + 字节预算内尾部截断；有标题时游戏名封顶 `budget//2`、标题截空则整段连同 `-` 省略；无游戏兜底 `未分类`、碰撞 `(2)`、日期目录不变）；executor `_prepare` 透传 `lease.published_at, lease.title`；
    6. 三侧测试 + 契约三处一致核对 + m2b 端到端（重建 Cloud 含 044 迁移，Agent 保留不重启）：真实下载落 `20261001/三角洲行动-30-20260922-标题.mp4` 形状，complete 不再 400，下载中心一条「已完成」、素材页「已下载」；无发布时间的素材省略该段；标题超长截断。
    证据 `evidence/task21-publish-time-naming.md`。不改 `LocalLease` 语义/权限模型；`game_name`/`Completion.file_name` pattern 不动（新形状仍是一层子目录）；任务 19 卡死残留两行属历史数据，验证靠新行。
22. （2026-10-01 走查反馈「一直卡在正在取消过程中，状态卡住无法处理」）下载取消卡死修复——transfer-reconcile 从未被调度，Cloud 一仓：
    1. 先核实根因（只读）：取消是两阶段——`CancelTask` 对 `running` 只写 `cancel_requested_at`，终态 `cancelled` 由执行器在下次上报撞 `cancel_requested_at IS NOT NULL` 谓词时自写；执行器失联则永不写终态，且带取消请求的任务不可被认领（`leaseable` 要求 `cancel_requested_at IS NULL`）。兜底 `ReconcileCancelledTasks`/`ReconcileExhaustedTasks`（`store_mysql.go:801/829`）早已写好、单测通过，但**从未被任何调度进程注册**（死代码）；而部署只跑 `cmd/server` + `cmd/discovery-worker`，scheduler 进程根本没起。线上库 3 行实证：`running` + `cancel_requested_at` 已置 + 租约过期 + claimed 于已死节点；
    2. 新增 `internal/jobs/transfer_reconcile.go`：`RunTransferReconcile(ctx)` 依次调 `ReconcileCancelledTasks`/`ReconcileExhaustedTasks`（`time.Now()`），计数 >0 才打一条日志（同 material-prepare 的静默原则）；reconcile 走全局 `database.DB()`，不需对象存储；
    3. `internal/bootstrap/jobs.go` `runWorkerProcess` 注册 `transfer-reconcile`（复用 `cfg.Scheduler.WorkerInterval`，零 config 改动）——挂 worker 进程而非 scheduler 进程，因为部署只跑 server+worker，挂 scheduler 仍是死代码；
    4. 新增 jobs 级编译期绑定测试（`var run func(context.Context) error = RunTransferReconcile`，照 `discovery_test.go:8` 范式）；既有 repo 机制测试（`store_mysql_test.go:425/449`）重跑即证据；
    5. `go test -count=1 ./...`（66 包 0 FAIL）；m2b 重建 Cloud 后只重启 worker 进程（Agent 保留不重启），一个 `worker_interval` 内 3 行自愈成 `cancelled`，走查「正在取消」清成「已取消」可再次下载。
    证据 `evidence/task22-transfer-reconcile-scheduled.md`。不改两阶段取消机制、不改 `CancelTask`/`leaseable` 谓词、不改前端 `downloadFacts.js`（终态优先本就正确）、不做一次性手工 UPDATE（修复自愈即可）。
23. （2026-10-01 用户裁定：①折入本 CHG（不新建）；②生命周期走**展示层截断**（DB 不删不归档，成功 30 天/失败 90 天/取消 7 天只是显示窗口）；③我的素材文件状态列**纯 `download_status`**（去掉 video_status 兜底）；④游戏/平台/时间/状态筛选本轮不做）三页职责重定义——我的素材按钮矩阵 + 下载中心三 Tab + 下载记录生命周期，Cloud 一仓（后端 + 前端），任务状态与业务状态严格隔离：
    1. 后端：`dto.Task` 增**可选** `finished_at *time.Time json:"finished_at"`（无 omitempty，nullable 序列化为 `null`；不能用 `updated_at`——会被租约续租移动）；契约 `file-transfer.yaml` 属性增 `finished_at` + revision `2026.09.27.1 → 2026.10.01.1`（`contract-map business_schemas.schema_revision` 不动，任务 20 确认的独立版本空间）；`GET /api/v1/file-transfer-tasks` 增 `status`（逗号分隔、枚举校验、未知值 400 `10001`）/`finished_after`（RFC3339、解析失败 400、SQL `finished_at >= ?`）/`limit`（≤200 封顶、缺省 100、≤0 或畸形 400），handler+service+repository 三层。先红锚点：`dto_test.go` 键集测试「Go dto 键集 == yaml 属性集」，加字段后失配即红，分母 20/12；
    2. 前端 `downloadFacts.js` 增 `isFailed`/`isHistory`（success|cancelled）/`withinDays`（取 `finished_at`，缺了退 `updated_at`）；`transferRows.js` `splitTransferRows` 改三分（active/failed/history），row 增 `finishedAt`/`finishedText`；
    3. 下载中心三 Tab：进行中 `status=pending,running`（含云 prepare 兄弟行，`purpose==='user_download'` 过滤保留在 `transferRows` **之后**，`needsCloudPreparation` 不退化）；失败 `status=failed&finished_after=now-90d`；历史 `status=success,cancelled&finished_after=now-30d&limit=50`，cancelled 客户端再收到 7 天内。每栏各拉各的查询、计数只挂当前栏；历史用 `t-table`（素材/大小/完成时间/状态/操作）；失败行「详情」开 `MaterialDetailDrawer mode="transfer"`（只读无页脚——下载中心不承担素材管理）；轮询门加 `activeTab==='active'`；
    4. 我的素材 `#op` 改状态矩阵（全部平铺 ≤3，无「更多」）：removed→恢复使用；active+''→下载；active+downloading→不给主操作（文件已在准备）；active+downloaded→加入合成；active+failed→重新下载；恒有 详情/放弃使用。`labels.js` `DOWNLOAD_STATUSES` 增 `''`→未下载(neutral)、failed 主操作词改「重新下载」。文件状态列 `fileStatus(row)` 改**纯 `download_status`**（未下载/下载中/已下载/下载失败），video_status 兜底拿掉，云端源文件态只留详情抽屉「文件信息」区；
    5. `MaterialDetailDrawer` mine 页脚同矩阵；downloading 时「文件信息」卡渲染下载进度/速度/ETA（复用 `transferRow`，从已拉 `transfer.listTasks()` 找该素材 pending/running 的 user_download 行）+ 取消下载（`canCancel`→`transfer.cancelTask`→本地 `cancelRequested`，与下载中心同一条「本机记忆」约定）；云端文件态与本地目录区保留不动；
    6. `go test -count=1 ./...`（66 包 0 FAIL）+ 全量 vitest（web/ 下，46 文件 425 用例）+ 双构建；m2b 重建走查（不碰 8765 Agent 的 runner 入口）：三 Tab 各自窗口、矩阵 5 行、downloading 进度/取消、取消落「已取消」进历史（7 天窗口内）。
    证据 `evidence/task23-three-page-redesign.md`。不做 DB 删除/归档 job、不加 `requested_by` 索引（展示层截断即可）；不从详情抽屉移除云端文件态；不改两阶段取消机制、不动节点注册/绑定；边界观察「从未下载 + 云端准备失败 → 显示『未下载』+『下载』（点了在下载中心快速失败）」按严格隔离接受。走查修正（cloud `560b875`）：下载中心抽屉 `min(46vw, 640px)` → `min(62vw, 880px)`（与详情抽屉同宽，用户反馈「参考详情的弹窗、需要更大一些」；旧宽度下历史表格五列 ≈720px 必然横向滚动），新增测试钉住尺寸，vitest 425 → 426。**走查修正第二轮（cloud `7955724`）**，用户三条反馈 + 两项裁定（「重试」与「重新下载」合并为单一「重新下载」，前后端一起清；每个素材一行 + 已成功的不能再次下载）：① 历史 Tab 标题溢出——`.transfer-table__title` 三件套齐全但是行内 `<span>`，补 `display: block; max-width: 100%`（对齐 `.material-title`）；② 去「重试」——前端删 `canRetry`/`WAITER_RELEASE_CODES`/`retryTask`/按钮与处理、后端逐层删 `RetryTask`（路由/handler/operations/service/Store 接口/store_adapter/repository）、契约删 retry path + `info.version 2026.09.26.2 → 2026.10.01.1`（`cloudagent` 模块的同名 `RetryTask` 不动）；③ 每素材一行——下载中心改**一次查询 + 客户端按素材首见去重**（口径与「我的素材」`LatestUserDownloadStatuses` 取最新一条对齐；执行记录按状态模型规则 4/5 原样保留，只是展示层收敛），后端 `createUserDownloadTask` 增「最新为 success 则返回既有行」的幂等去重防绕过；④ 已成功不重下——`canRedownload` 只认 failed/cancelled，去掉「文件已不在…可以重新下载」的后半句承诺。读数：66 包 ok / 0 FAIL、全量 vitest（web/ 下）**46 文件 / 428 用例全绿**、双构建 exit 0。

24. （2026-10-01 用户裁定：并行分片折进本 CHG；分片默认 8）分片 part 文件的存储层支持，`wt-media-agent` 一仓（`storage/download_sink.py` + `tests/test_download_sink.py`）：
    1. 诊断实测对象存储对**每条 TCP 流**限速 ~112–160 KB/s、聚合随连接数线性（8 流 8.44×、64 流 80 Mbps 撞线路）、全程回 206 —— 分片**不必动基建**；Agent 引擎严格单连接串行，46 MB 素材只用掉线路 0.9%；
    2. 分片 k 写自己的 `<safe_task_id>.part.<k>`，各自**只追加**、各自的大小就是它自己的续传依据 —— 不引入任何持久化分片账本，崩溃一致性与改动前相同（既有不变式：**磁盘文件大小是唯一的续传依据**，`resume_offset` docstring 明写「不信 checkpoint」）。代价是拼装期间磁盘峰值 2×；
    3. 新增 `part_path(task_id, shard=None)`（`None` 保持单流形状，负序号 `ValueError`）/`shard_offset`/`append_shard`/`assemble_shards`（`"wb"` 拼装、顺带截断上次中断的合并；哈希留在执行器）/`written_bytes`/`shard_indices`；`discard` 与 `commit` 扩展为连分片一起收（`commit` 在 `replace` **之后**清理，先删会把 re-merge 需要的字节丢掉）；
    4. 匹配一律**精确词干**，不用 `glob(f"{safe}.part*")` —— 任务 `a` 不能删掉任务 `a1` 的文件；
    5. 本任务**没有调用方**（执行器在任务 25 才接上），只增加 API 与测试；13 条变异逐条变红后还原、还原后逐文件 sha256 一致；一条登记为**等价变异**（`_task_parts` 的 `.isdigit()` 子句不可达，改为简化匹配器而不是编夹具）；
    6. 自查时发现并修掉自己刚写的缺陷：`written_bytes` 第一版把该任务所有 part 大小相加，「拼装完成、尚未 commit」窗口里报 `2 × total` 给 Cloud。抓法是**跟着消费者走**（读 `_report_failure` 的调用点）而不是推演生产者；改成 `max(合并, 分片之和)` 后 amend 进本任务提交。
    证据 `evidence/task24-shard-part-files.md`。不改 `LocalLease`、契约、`info.version`、`contract-map.yaml`、`REQUIRED_LEASE_FIELDS`。
25. （接任务 24）执行器并行分片，`wt-media-agent` 一仓（`executors/material_download.py` + `tests/test_material_download_executor.py`）：
    1. 新增模块常量（构造函数可注入，对齐既有 `DEFAULT_CHUNK_BYTES` 范式）：`DEFAULT_SHARD_COUNT = 8`、`MIN_SHARD_BYTES = 4 MiB`、`DEFAULT_SHARD_POLL_SECONDS = 0.5`。分片数是**模块常量 + 构造函数默认值**，不是契约字段、不是配置项；
    2. `_attempt` 拆出 `_classify_transfer_error` 供线程体复用；`_transfer` 变分派器，原主体原样搬进 `_transfer_single`；`_plan` 判定顺序：`count==1` → 单流｜有分片 part（含序号 ≥ count 的残留）→ 分片｜否则有正式 `.part` → 单流（改动前就在下载中的旧任务）｜否则 → 分片。**这个顺序别换**；
    3. `ThreadPoolExecutor`（stdlib；ADR-0016 禁的是 `os/socket/http/urllib/subprocess/sqlite3/ctypes/requests`，**没禁 `threading`/`concurrent.futures`**；HTTP 仍只经 `clients/transfer.open_source`）。分片线程只做「读网络 + 追加自己的 part + 累加一个加锁的总数」，**主线程独占** `_Progress.note`，所以进度上报与心跳仍是既有 ~2 秒窗口语义、Cloud 侧流量不变；
    4. 三种情况回退单流，其中「服务端不认 Range」**在同一次尝试内**回退（`200` 不是故障，不该吃掉 attempt 预算）；判据落在**任何 `offset > 0`** 的分片拿到 `range_honoured == False`（分片 0 本来就不发 Range 头）。「206 但 `Content-Range` 起点不符」判 `SourceUnavailable`（非 retryable）是**照既有**（`source.py` 已这么判，任务 18 定过），一致性优先于自创；
    5. 收尾逐分片校验 `size == region_len` 再顺序拼装，同一次读里算整份 sha256（sha256 不可由分片摘要合成，这一遍躲不掉）；`_prepare` 的 `require_room` 在分片路径上按 **2×** 申请；`_report_failure` 的 `completed_bytes` 改用 `written_bytes`；
    6. 22 条变异逐条变红后还原；并发臂用 `threading.Barrier(N)` 放进假 opener（串行实现会超时失败，不是时序测试）。**计划里两处判断被实测推翻并如实登记**：① 「既有单流臂会静默切到分片路径」不成立（body 4096 字节，`4096 // 4 MiB == 0`，本来就是 1），仍显式钉 `shards=1` 但理由改成「一个只是碰巧单流的臂会在阈值移动那天开始量另一条路」；② 计划要求给测试假 opener 加锁 —— **没加**，`list.append`/`pop` 在 GIL 下本就原子，加一把从不 acquire 的锁是装饰（先确实写了那把锁和一段「防日志交织」的注释，自查时改回一句实话）。
    证据 `evidence/task25-parallel-shard-transfer.md`。已知代价写进证据：故障时一次尝试最多多等一个 socket 超时（`shutdown(wait=True)` 等运行中的分片在下一块察觉 `stop`；未启动的 future 靠 `cancel_futures=True` + worker 开头查 `stop` 收掉）。**端到端真机验证未执行**，见 checkpoint Blockers。
26. （2026-10-01 用户裁定：video-url 的 403 由端点改签发 presign；抽屉里的视频链接改成点击时才取地址）视频链接改签发 presign + 前端点击取址，`wt-media-cloud` 一仓（后端 + 前端 + 契约）：
    1. 诊断的附带发现：`GET /api/v1/materials/:id/video-url` 返回**无签名**地址，桶拒绝匿名读（403 `Garage does not support anonymous access yet`），任务 2 的验收项「云端视频 URL 实际可访问性」当前不成立；
    2. 后端：`productionObjectLinker.PublicObjectURL`（`storage.PublicURL`）→ `PresignObjectURL(ctx, objectKey)`（`storage.PresignGet`），`ObjectLinker` 随接口改形，`Service.VideoURL`/`operations.VideoURL`/handler 增 `ctx` 并透传。grant 的 `ExpiresAt` **不到达响应体**（契约只有 `url`，点击时取址后没有持有中的地址需要过期信息）；
    3. 前端 `MaterialDetailDrawer.vue`：去掉开抽屉预取、`videoUrl` ref 与「地址获取中」中间态，链接按 `video_status === 'ready'` 直接渲染、点击才取址。**空标签页在 `await` 之前同步开出来**（跨过 await 后浏览器不算「用户手势」，那时才调的 `window.open` 会被 WebKit 拦，而打包的 Desktop 用的就是它），`opener` 置空、拿到地址后 `location.replace`；同步就被拦时不发那次签名请求；
    4. 契约（本任务的核心之一，不是附注）：openapi `info.version 2026.09.30.2 → 2026.10.01.1` + `summary`/`description`/`200` 改写（原文「it is not a presigned grant and carries no expiry」改后即假话）；业务 schema `MaterialVideoLink` 描述改写 + `revision 2026.10.01.1 → 2026.10.01.2`。**不加 `expires_at` 字段**；
    5. **对计划的一处偏离**：计划写「同步 `contract-map.yaml business_schemas.schema_revision`」，**未动**（仍 `2026.07.14.4`）—— `scripts/verify_m0_config.py:99-100` 把它钉成常量，任务 20 已确认那是与业务 schema 文件 `revision` **独立的版本空间**，任务 21/23 改同类契约时同样只动前者。按计划改会同时打红校验器并覆盖一条已确认的裁定；
    6. 读数：`go test -count=1 ./...` 66 包 ok / 0 FAIL、全量 vitest（web/ 下）46 文件 / 430 用例全绿、双构建 rc=0；5 条变异逐条变红后还原、还原后逐文件 sha256 一致；真实链路两读数（不打印地址）：生产适配器签发的地址 + `Range: bytes=0-1023` → **206，`bytes 0-1023/48511909`**，同一 key 的**无签名**地址 → **403**（阴性对照成立）。
    证据 `evidence/task26-video-url-presign.md`。**遗留（当时不阻塞本 CHG 任何验收项，交用户另裁；2026-10-01 已裁定「删掉」）**：`storage.PublicURL` 改动后已无生产调用方，但「对象存储加 CDN」正是它的用途，故当时未删；留一个会构造**已知 403 地址**的导出函数是个坑。**裁定后的落地**：删 `public_url.go`（`PublicURL` + `publicBaseOf`）、`registry.go` 的 `publicBase` 字段与两处赋值/回收、`storage_test.go` 的 4 条相关用例，`wiring_test.go` 那段变异注释改名为「稳定的无签名地址」（判别力未减，实测把适配器改成无签名地址仍红）；提交 cloud `594a99c`，`go test -count=1 ./...` 66 包 ok / 0 FAIL。**当时未写成 `Q-xx`** 的理由保留在册 —— `scripts/verify_product_master_alignment.py:337-342` 要求 active CHG 的 §7 恰好是 `None.`，而这不是一个阻塞本 CHG 的决定。

27. （2026-10-01 走查现场裁定：修法选「交给系统浏览器」，范围选「连其它外链一起修」）把外链交给系统浏览器——修「打开云端视频」在打包桌面端点不动，`wt-media-desktop` 两提交 + `wt-media-cloud` 一提交（前端，不动 Go）：
    1. 根因（查实，非猜测）：打包的 Desktop 是 Tauri 2.11.5 的 WKWebView，而 WebView 不是浏览器。`window.open`（以及每一个 `<a target="_blank">`，走同一条路）不自己开窗口，它抛出「新窗口请求」由壳接；`new_window_handler` 从没装过（`tauri-2.11.5/src/webview/mod.rs:354,433` 两处默认构造都是 `None`），能力里也没有 `core:webview:allow-create-webview-window` → 请求被丢，`window.open` 恒返回 null。任务 26 那句「浏览器拦截了新标签页」是自造误报；
    2. Desktop `a09dccb`：新模块 `external_links.rs`（判据只放行 `http`/`https`，`open::that` 交给系统默认浏览器，一律 `NewWindowResponse::Deny`，应用内永不开窗）；主窗口不再由 `tauri.conf.json` 自动创建（`"create": false`）而是在 setup 里用 `WebviewWindowBuilder::from_config` 重建——`on_new_window` 只在 builder 上（`webview/mod.rs:585` 按值收 `self`），且 `tauri::Builder` 没有够得到已存在 webview 的钩子。**处理器一行日志都不加**：`logging::targets` 的 target 词表是 Q-07 定死的，`webview` 那个 target 又明写只放两条 JS 错误记录；附带好处是签名地址不进 `desktop.log`；
    3. 闸门（本任务的核心发现）：WebKit 在「有没有新窗口请求」之外还问「这次有没有用户手势」，`javaScriptCanOpenWindowsAutomatically` 在 macOS 上 wry 不设（`wry-0.55.1/src/android/kotlin/RustWebView.kt:26` 只在 Android 设）→ 留的是默认 false。用最小 WKWebView 探针量了四组：无手势的 `window.open` 与无手势锚点都到不了（pref=true 时两者都到达，阳性对照）；有激活时两者都到达；**一次激活只撑得到 250ms 与 0ms，1000ms 起全被丢**。所以「取到地址再 `window.open`」（计划里的前端那条）是亚秒级竞态，桌面端必须是本任务 `967ddb2` 那条偏好（主窗口从自己设了该偏好的 `WKWebViewConfiguration` 建；`Cargo.lock` +2 行，无新 crate）；
    4. 对计划的偏离：计划钉的「**不要**新增 `local_open_external_url` 之类的命令」**保持住了**——收尾选的是打开那道闸门，页面要的仍然只是导航、落点由壳决定；计划写的「处理器记一条日志」**没做**（见第 2 小条）；
    5. Cloud `b51108e`：前端按宿主交付地址，判据与两条分支的理由抽到 `web/src/modules/materials/cloudVideo.js`，抽屉只回答「现在跑在哪个宿主里」；抽出来是为了能按行为测（本仓 vitest environment 是 node、没有组件挂载），「浏览器先预留标签页再取地址」「桌面端一次都不预留」「壳返回的 null 不算被拦」「取址失败要关预留标签页」「空地址算失败」逐条钉住；
    6. 读数：`cargo test` 502 通过 / 0 失败 / 6 忽略（与改动前同）、`cargo build` 12 条警告与改动前逐条同一批（stash 实测基线也是 12，顺带更正 `a09dccb` 里把汇总行数进去的「13」）、全量 vitest（web/ 下）47 文件 / 436 通过（任务 26 记的 46/430，+6 全是本任务新增用例）；前端 6 个变异逐条变红，还原后两文件 sha256 逐字节一致。**未跑 Go**（未改）；
    7. 真机验收 5 条（用户手动，先提交 Cloud 再重建 DMG —— 否则 `frontend-build.json` 会把 `source_commit`/`source_dirty` 记成脏工作区）：点「打开云端视频」系统浏览器打开并播放、应用内不出新窗口；点「平台原视频」系统浏览器打开（补第 3 小条没量到的那条）；目录选择器仍可用；窗口标题/尺寸/单实例聚焦无回归；日志里不得出现签名地址。未做完，故本任务不关闭。
    证据 `evidence/task27-external-links.md`（含可重放探针 `evidence/task27-wkwebview-probe.swift`）。**顺带查实的 Garage 一问**：Garage v2.x 没有匿名访问（403 体是上游硬编码拒绝），公开读只有 bucket website 模式一条路，bucket 级匿名访问是 WIP（上游 PR #1306，目标 3.0）——桶侧没有可翻转的开关，任务 26 的签发方向是唯一方向；本任务不改也不动桶。

## 6. 验证与提交边界

- Cloud Repository/Service/Handler 与 wire/schema 测试覆盖字段映射、权限、就绪状态及 URL 生成；
- Cloud Web 测试覆盖两列表、详情字段和下载任务分组；
- 生产代码与契约可分提交；当前工作区的其他已有修改保持原样。
- 不在用户完成 M4-A 走查前关闭本 CHG，也不启动 M4-C2。

## 7. Pending Questions

None.

## 8. 验收与关闭（2026-10-01）

用户裁定：**「确认修改好了，这个CHG走查完毕」**；对这次没走到的项，用户选定**「登记为遗留并照常关闭」**。§1 的激活前提（M4-A 用户走查签收）与 §6 的关闭条件（用户完成走查）据此满足。**本记录不据此宣称 M4-A 里程碑已签收**——CHG 的走查与里程碑签收是两件事，见遗留 (e)。

### 8.1 走查结果（用户自报，逐项标注证据覆盖）

| 走查项 | 用户结果 | 机器证据 |
| --- | --- | --- |
| 任务 27：重链已交给系统浏览器 | 通过 | **覆盖**：DMG 于 19:21:15 由 `967ddb2`（19:14:36）构建，19:22:04 启动，用户在该产物上确认。任务 27 的判据正是「打包桌面端」，无从别处代偿。 |
| 任务 19/20/21/22/23：下载链路各条 | 通过 | **部分覆盖**：DB 里 18:05:02–18:07:11 共 7 条 `user_download` 任务全部 `success`/attempt 1、`transferred_bytes == total_bytes`；落盘 `/tmp/wt-media-m4a-acceptance/20261001/` 6 个文件。但**这批跑的是任务 19 级引擎**（见 8.2），任务 21 的形状（`-发布时间-标题`）在文件名里不存在，任务 22/23 属 Cloud 侧、未随本批单独取证。 |
| 任务 16/17：抽屉与下载目录 | 通过 | **部分覆盖**：19:22 启动的产物含 `967ddb2`；但 §8.2 的 401 使该窗口内不可能有下载，故「打开目录」依赖的「本机确有下载文件」只由 18:07 那批（任务 19 级引擎所产）提供。 |
| 任务 24/25：分片下载端到端 | **用户报通过** | **不覆盖**（见 8.2）。 |

### 8.2 任务 24/25（及任务 21 的 agent 侧）真机端到端**未跑**——如实登记

用户的结论按其观察记账，但机器证据不支持「分片代码已真跑」。三条独立读数：

1. **进程装载的代码早于改动**。8765 上的 Agent 是 pid 54067，`lstart` = `Thu Oct 1 01:47:36 2026`，到关闭时**未重启过**。而 `local_main` → `bootstrap.local` → `local_api/server.py:19` → `bootstrap/app.py:35` 在**模块作用域**导入 `MaterialDownloadExecutor`，执行器的代码在进程启动那一刻就固定了；任务 21 的 agent 提交 `c9915a3`（10:27:11）、任务 24 `d5cf2a7`（16:18:36）、任务 25 `ac2ed81`（16:28:24）都晚于该时刻。`pgrep -P 54067` 为空——没有子进程可以装载更新的代码。
2. **产物形状是任务 19 的**。18:05–18:07 落盘的是 `20261001/三角洲-152.mp4` 一类（日期目录 + `游戏-素材ID`），任务 21 之后的名字应带 `-发布时间-标题` 段。
3. **关闭前那次窗口根本没有下载**。Cloud 于 19:20:48 重启（pid 93170），Agent 在 19:22:19 报 `Cloud refused this node's credential (HTTP 401); not claiming until it is replaced`——此后它不领取任何任务，故 19:22 之后的走查不可能跑出下载（这条同时说明 8.1 里任务 16/17 的「打开目录」不是本轮新产的文件）。

**由此，任务 24/25 的分片下载在本机一次都没真跑过**；任务 21 的命名形状与 complete 缺陷修复同理（契约与 Cloud 侧已按 8.3 的读数覆盖，agent 侧未跑）。分片聚合倍数因此也仍未量（遗留 b）。

### 8.3 关闭读数（最后一次代码改动之后重跑，改动为 cloud `594a99c`）

| 仓 | 读数 |
| --- | --- |
| `wt-media-cloud` | `go test -count=1 ./...` **66 包 ok / 0 FAIL**；`gofmt -l` 仅既有 `internal/modules/production/model/model.go`（本 CHG 之前既有） |
| `wt-media-cloud/web` | `npx vitest run`（cwd 必须为 `web/`）**47 文件 / 436 用例通过** |
| `wt-media-agent` | `Ran 677 tests … OK` |
| `wt-media-desktop/src-tauri` | `cargo test` **502 通过 / 0 失败 / 6 忽略**；`cargo build` **12 条警告**（与改动前逐条同一批） |
| DB | 7 条 `user_download` 任务全部 success、attempt 1、`transferred_bytes == total_bytes` |
| 磁盘 | `/tmp/wt-media-m4a-acceptance/20261001/` 6 个文件 |

以上四个套件在 `594a99c` 之后未再改动任何运行时代码（三个运行仓工作树无代码改动），故这些是关闭读数。

### 8.4 遗留（登记，不阻塞关闭）

- **a. 任务 21/24/25 的真机端到端未跑**。需重启 8765 上带 runner 的 Agent（`PYTHONPATH=src WT_MEDIA_AGENT_RUN_RUNNER=true .venv/bin/python -m wt_media_agent.local_main`）并在 Desktop App 里重绑节点——当前节点 `agent-node_7333d38c5e659e92bff5af7b`（2026-10-01 18:04:37 绑定）。**本次不重启**：该进程持有节点绑定，重启会改变绑定状态，须由用户执行。
- **b. 分片聚合倍数仍未量**。对照实验的同对象两臂（152：18.8→34.7 MB/s；28：31.7→78.5 MB/s）**两臂都是单流**，不能当分片证据；计划里写的 ~8× 既未成立也未被否证。
- **c. 素材状态的写入口未裁定**——谁来暂停/下架、在哪一页操作，见 `delivery/planned/CHG-20260930-071` §4 `Q-01`。
- **d. `agent /api/v1/status` 的 3s 单发门禁偶发假 FAIL**（`all` 收尾门实测过一次 exit 1，见 checkpoint 任务 16 条），改不改交用户裁定。
- **e. M4-A 里程碑的用户签收未因此闭合**。本 CHG 走查的是走查反馈的修正；`delivery/MASTER_IMPLEMENTATION_PLAN.md` 里「M4-A 实施记录虽已归档，其用户走查和签收尚未闭合」这句是否随本 CHG 关闭而解除、M4-C2 是否可激活，是里程碑层裁定，不在本 CHG 范围。
- **f. 走查观察项**（任务 16「标题过长可能压到 `×`」、任务 17「返回目录没有单测 / 同一素材多行成功下载取最新一条」）保留在原 evidence 中，未升格为缺陷。
