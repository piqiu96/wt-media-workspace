# T-21 素材操作人（素材创建人）

日期：2026-10-27（Asia/Shanghai）
结论：PASS（机器腿）；真实页面读回并入 T-26 复走查

## 提交

| 仓 | 分支 | 提交 |
| --- | --- | --- |
| wt-media-cloud | `chg/CHG-20261015-098-round3` | `f73bebf`（后端 + 合同 + 前端） |
| wt-media-workspace | `chg/CHG-20261015-098-docs` | `c05f667`（contract-map / PRD / 设计稿） |

## 结论：操作人 = 素材创建人

`materials.created_by` 从 M3 起就写入（迁移 `20260916_028_content_pool.sql`，外键到 `users`，NOT NULL），但读取投影一直没带，所以页面说不出是谁把素材放进来。人工转素材写入执行转换的人；自动转素材写入任务创建人（`actorForTask(task).ID = task.CreatedBy`，见 `internal/modules/contentpool/service/discovery.go:700-703`）。本轮只补读取侧，不回填、不改写路径。

## 后端

| 项 | 实测 |
| --- | --- |
| 模型 | `model.Material` 增 `CreatedBy identity.UserID`（json `created_by`）与 `CreatedByName string`（json `created_by_name,omitempty`） |
| 投影 | `materialProjectionColumns` 末尾追加 `m.created_by`；`scanMaterial` 位置扫描同步，三条读取（按团队 / 不限团队 / 列表）共用同一常量 |
| 姓名解析 | `decorateMaterials` 把创建人 ID 并入 `composeOperatorNameLookup` 的同一次目录读取；`ListMyMaterials` 单独一次批量解析（两个页面的详情抽屉共用，我的素材里的素材也可能是别人创建的） |
| 角色边界 | 创建人姓名三种角色都读；「谁用过」的 `usage.operators` 姓名仍只给高级运营与管理员（既有规则未动） |
| 目录缺人 | 目录里查不到创建人时 `created_by_name` 不出现（omitempty），页面画占位符 |
| 测试 | `go test -count=1 ./internal/modules/production/...` 全部 ok；新增 service 用例断言普通运营/详情/我的素材三处都能读到姓名、目录缺人时为空；新增投影断言 `m.created_by`；`wire_test` 的 Material 键集分母 29 → 31 |

## 合同

| 项 | 实测 |
| --- | --- |
| `business-schemas/v1/content-production.yaml` | revision `2026.10.27.1` → `2026.10.27.3`；Material 增 `created_by`（required）与 `created_by_name`；`wire_test` 先红（29≠31）后绿 |
| `cloud-api/v1/content-production.openapi.yaml` | `2026.10.27.2` → `2026.10.27.4`；`listMaterials` 说明补创建人语义 |
| `config/contract-map.yaml` | cloud_api `2026.10.27.4`、business_schemas `2026.10.27.3` |
| 校验 | `python3 scripts/verify/verify_m0_config.py` → Workspace config verification ok |

## 前端

| 项 | 实测 |
| --- | --- |
| 素材库列表 | 「入库时间」后新增「操作人」列（`created_by_name`，宽 110）；缺失画 `—` |
| 素材详情 | 「基本信息」新增「操作人」，缺失画 `-`；我的素材共用同一抽屉，服务端已解析姓名 |
| 我的素材列表 | 不加列（个人工作集），详情仍显示创建人 |
| 测试 | `npx vitest run`（在 `web/` 下）85 文件 / 765 测试全绿；新增详情抽屉与列表两条断言；`ListPageConventions` 列数分母 10 → 11 |

## 数据库读回（开发库）

只读查询，凭据走 `/tmp` 下 600 权限临时 cnf，用后即删，未打印任何凭据值。

| 项 | 读数 |
| --- | --- |
| `materials` 总行数 | 172 |
| `created_by > 0` 的行 | 172（100%） |
| `created_by` 在 `users` 中不存在的行 | 0 |
| 不同创建人数 | 2 |
| 创建人无昵称（会回退用户名）的人数 | 0 |

## 未覆盖

- 本机 Cloud API 进程仍是改动前二进制；`created_by_name` 的 HTTP 读回并入 T-26 重启后验证。
- 开发库里所有创建人都有昵称，用户名回退分支只有单元测试覆盖（`composeOperatorNameLookup` 既有用例），没有真实数据对照。
- 历史素材不回填创建人（库列本来就非空，无需回填）；生产/外部环境未验证。
