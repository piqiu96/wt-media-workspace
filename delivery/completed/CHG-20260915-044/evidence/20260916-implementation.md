# CHG-20260915-044 实施证据（自动化）

日期：2026-09-16（Asia/Shanghai）

## 范围

- Cloud：`source_contents` / `materials` migration、内容池 API、团队级范围校验、状态管理、幂等转素材。
- Web：内容池列表/筛选/详情/状态操作/批量忽略、素材库只读投影、内容挖掘导航入口。
- 明确未包含：抖音外部请求与敏感凭据（M3-B）、下载/文件存储、自动转素材、工作流引擎。

## 自动化验证

| 检查 | 结果 |
| --- | --- |
| `env GOCACHE=... go test ./...` | PASS：Cloud 全部 Go 包通过 |
| `npm test` | PASS：19 个测试文件、74 个测试 |
| `npm run build:cloud` | PASS：Vite Cloud 生产构建 |
| `npm run build:desktop` | PASS：Vite Desktop 生产构建 |
| `git diff --check` | PASS：无空白错误 |

## 业务规则测试覆盖

- 普通/高级运营只能访问所属团队；管理员可跨团队读取。
- 同团队相同平台内容 ID 返回重复冲突；不同团队可独立建档。
- 内容状态覆盖 `pending`、`ignored`、`material_created`，已转素材不可恢复为待处理。
- 跨团队转素材被拒绝；同团队转素材保留来源内容 ID。
- 批量状态处理逐条提交，单条失败不回滚之前成功项。

## 待人工读回

在配置最新 MySQL 的 Cloud 环境运行迁移后，需要用真实登录会话核对：内容池列表/详情、团队隔离、转素材后素材库投影及页面交互。上述人工读回完成前不关闭 M3-A。
