# 任务 12 证据：素材状态落库并投影进素材 body（走查六轮追加裁定）

- 日期：2026-09-30
- CHG：CHG-20260930-069（M4-A 素材详情与下载中心走查修正）
- 仓库：`wt-media-cloud`（迁移 + 契约 + Go + 前端）
- 提交：`71deb48`（`feat(chg-069): 素材状态自成一列并投影进素材 body（走查六轮）`）

## 0. 裁定与它推翻的东西

走查六轮用户追加：

> 素材状态的值当下是可以有数据的，是素材库的内部职责，需要完成状态展示。

任务 9 曾按「先落纯交互层，后端另立 CHG」把这档排除在 `change.md` §3 之外，并把后端
实现登记给 `delivery/planned/CHG-20260930-071`。本轮裁定改变的是**归属**：素材生命周期
是素材库自己的职责，不等外部数据，因此在本 CHG 内落地。

对澄清问题的裁定（素材状态的值取自哪里）：**素材库新增自有字段**。

## 1. 动手前的只读盘点（不猜）

| 问题 | 命令 | 实测 |
| --- | --- | --- |
| 库里有没有这列 | `SHOW COLUMNS FROM materials`（dev DSN `root:root123@127.0.0.1:3306/wt_media_cloud`） | 14 列，无生命周期列 |
| 代码里有没有这个概念 | `git grep -n "delisted\|已下架\|已暂停"` | 0 命中 |
| 有没有写入口 | 素材相关路由盘点 | 4 条，无任何改状态的路径 |
| 能不能从来源行派生 | `SELECT ... material_created` | 149/149 全是 `material_created`，派生出来也是常量 |
| PRD 怎么说 | `docs/product/prd/详细文档/第五章_素材生产.md` | `material` 定义为「正式素材与源视频准备状态」，没有状态取值表 |

前四条合起来说明：**三种取值在库里都是同一个值**（无论新增列还是派生），差别只在语义归属。
这正是上表要交给用户裁定的原因，而不是由实现倒推。

## 2. 红：写在契约层，不靠编译错误

**顺序**：先改 `contracts/business-schemas/v1/content-production.yaml`（`Material` 增 `status`
枚举并列入 `required`）与 `internal/modules/production/wire_test.go` 的分母（24 → 25），再动
Go 结构体。

**命令**：`go test ./internal/modules/production/ -run TestMaterialBody`

**实测失败**：
`a fully known Material marshals to [... want [... status ...]]`

这条红证明的是「契约承诺了、body 给不出」——若先改结构体再补契约，红会退化成编译错误，
什么也证明不了。

## 3. 绿：最小实现

- `migrations/20260930_042_material_status.sql`：`ALTER TABLE materials ADD COLUMN status
  VARCHAR(16) NOT NULL DEFAULT 'available' AFTER video_status` + `CHECK (status IN
  ('available','paused','delisted'))`。只加列，不回填、不改既有列。
- `model.go`：`type MaterialStatus string` 与三个常量；`Material.Status MaterialStatus
  \`json:"status"\``（无 `omitempty`，键恒在）。
- `store_mysql.go`：`materialProjectionColumns` 增 `m.status`（插在 `m.video_status` 之后，
  与 scan 顺序一致）；`scanMaterial` 增 `materialStatus`（普通 `string`，列 NOT NULL）并回填。
- `store_mysql_test.go`：`materialColumns()` 增 `"status"`、mock 行增 `"available"`、断言读回值，
  另加 `TestMaterialProjectionCarriesTheLibraryLifecycleStatus` 钉住列清单里必须有 `m.status`
  （sqlmock 的期望只钉 FROM 子句，漏列要到运行时才以列数不符暴露）。
- 前端：`labels.js` 的注释回写为「字段已落地」；列表「素材状态」列与详情徽章读真值；
  **缺值仍渲染 `—`，不加兜底默认值**——`row.status || 'available'` 会把一条读不到状态的
  素材静默画成「可用」，而「可用」正是唯一能触发「加入我的素材」的那一个。

## 4. 复验读数

| 检查 | 命令 | 读数 |
| --- | --- | --- |
| 格式 | `gofmt -l internal/modules/production/` | 空（`model.go` 因字段对齐被重排，已 `gofmt -w` 单文件） |
| Go 全量 | `go test ./...` | exit 0；66 包 ok、0 FAIL |
| 迁移 | `migrations/20260930_042_material_status.sql` 应用 | `migration ok: 1 applied, 43 total` |
| 库列定义 | `SHOW COLUMNS FROM materials LIKE 'status'` | `varchar(16) NO available`（NOT NULL，默认 `available`） |
| 库内分布 | `SELECT status, COUNT(*) FROM materials GROUP BY status` | `available 149` |
| 迁移计数 | `SELECT COUNT(*) FROM schema_migrations` | 43 |
| API | `POST /api/v1/auth/login`（admin）后 `GET /api/v1/materials` | 149 行；`status` 在返回键里；值全 `available`；`video_status` 同时有 `ready` / `not_downloaded` 两个值 |
| 前端定向 | `npx vitest run src/modules/materials` | 6 文件 / 68 用例全绿 |
| 前端全量 | `npx vitest run` | 1 failed / 368 passed (369)——唯一失败是既有 `localSettingsWiring.test.js`，范围外，见任务 11 证据 §4 |
| 双构建 | `npm run build:cloud` / `npm run build:desktop` | 均 exit 0 |

**环境的有效性问题**：`start_cloud` 对已健康的 Cloud 直接返回（不重启），所以「改完代码
直接读 API」会读到旧编译产物。本节读数取自 `m2b_local_acceptance.py up --force-restart`
之后（`go run` 重新编译，pid 12267 → 15400）。

## 5. 阳性对照：这个值是不是恒定的

「149 行全是 `available`」本身分不清两种情形：读的是列内容，还是读了一个写死的默认值。
控制实验（dev 库，一次一行，随即还原）：

```text
UPDATE materials SET status='paused' WHERE id=1;   → API: {'available': 148, 'paused': 1}
UPDATE materials SET status='available' WHERE id=1; → API: {'available': 149}
```

读数随列变化，说明页面上的「可用」是**这列的内容**，不是常量；同时说明投影确实读的是
`materials.status` 而没读错别的列（读错会看到 `ready` / `not_downloaded`）。

## 6. 诚实的边界

- **没有写路径**：没有任何接口、服务或命令能把一行改成 `paused` / `delisted`。因此今天
  149 行全部读作「可用」，用户看到的徽章恒为绿色「可用」。这不是兜底默认值——它**就是**
  这批素材的真实状态（还没有人被暂停过）——但也不是一个**能用起来**的状态维度：
  在有人能暂停之前，页面上的这一列只能证明链路通了。
- `POST /materials/{id}/usages` 是无状态校验的 upsert（见 `store_mysql.go`），它不校验
  `status`；`canAdd()` 是目前唯一的拦截点，属前端规则，不是安全边界。
- 「使用情况」不在本轮：它要跨成片与发布聚合，仍留在 `delivery/planned/CHG-20260930-071`。
