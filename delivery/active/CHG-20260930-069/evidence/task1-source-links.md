# Task 1 证据：素材投影补充 cover_url 与 author_home_url

- 日期：2026-09-30
- 范围：`wt-media-cloud` production 模块（模型、投影 SQL、扫描）与 Business Schema 契约。

## 测试先行（红）

- 命令：`go test ./internal/modules/production/...`
- 预期：编译失败 —— `model.Material` 无 `CoverURL`/`AuthorHomeURL` 字段（wire_test、service_test、store_mysql_test 同时报 undefined）。
- 实际：三个包均 `[build failed]`，报错即为上述缺字段。
- 状态：PASS（失败形态正确）

## 实现后（绿）

- 命令：`go test ./internal/modules/production/...`
- 预期：production / repository / service 三包全部 `ok`。
- 实际：
  - `ok github.com/wt-media/wt-media-cloud/internal/modules/production 1.500s`
  - `ok .../production/repository 4.745s`
  - `ok .../production/service 0.677s`
- 状态：PASS

## 编译与静态检查

- 命令：`go build ./... && go vet ./internal/modules/production/...`
- 预期：无输出，退出码 0。
- 实际：`OK`。
- 状态：PASS

## 契约

- `contracts/business-schemas/v1/content-production.yaml`：Material 新增 `cover_url`、`author_home_url`（可选，未知时键不出现），revision `2026.09.27.1` → `2026.09.30.1`。
- `wire_test.go` 的量具同步：属性数 17 → 19，fixture 补两个链接；`TestMaterialBodyMarshalsExactlyTheFrozenPropertySet` 继续把模型键集钉在契约上。

## 数据库

- 无迁移：两列读取自既有 `source_contents.cover_url`（migration 028）与 `source_contents.author_home_url`（migration 034），SELECT 侧 JOIN 带出，未新增/修改任何表。

## 相关提交

- 见本 CHG 目录提交记录：`feat(chg-069): 素材投影带出封面与作者主页（契约+测试先行）`
