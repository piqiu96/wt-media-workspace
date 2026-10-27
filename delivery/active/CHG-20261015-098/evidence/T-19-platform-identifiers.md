# T-19 平台标识与展示文案统一

日期：2026-10-27（Asia/Shanghai）
结论：PASS（机器腿）；真实页面读回并入 T-26 复走查

## 提交

| 仓 | 分支 | 提交 |
| --- | --- | --- |
| wt-media-cloud | `chg/CHG-20261015-098-round3` | `753fbce` |
| wt-media-agent | `chg/CHG-20261015-098-round3` | `5d83146` |
| wt-media-desktop | `chg/CHG-20261015-098-round3` | `4409946` |
| wt-media-workspace | `chg/CHG-20261015-098-docs` | `0bfaeaf` |

## 归属结论

展示文案由前端公共常量持有（`wt-media-cloud/web/src/shared/utils/platforms.js`），后端、数据库与合同只存英文代码。理由与发布/回滚约束见 `docs/decisions/0024-platform-identifiers-and-display-labels.md`。

## 前端

| 项 | 实测 |
| --- | --- |
| 新常量 | `PLATFORM_LABELS`（douyin/bilibili/xhs/baidu）、`platformLabel`、`MINING/ACCOUNT/ACCOUNT_OPENING` 三组选项集 |
| 替换点 | 内容池（列表格、筛选、详情、人工导入）、挖掘策略（表单、详情）、挖掘任务（策略抽屉）、素材库列表、素材详情抽屉、社媒账号（列表格、筛选、创建、详情、编辑）、账户开户（导入选项、预览与结果表）、游戏关联详情 |
| 内容池平台筛选 / 人工导入 | 只剩「抖音」一个选项；「B站（待接入）」禁用占位删除 |
| 社媒账号平台选项 | 只剩「B站 / 百度」 |
| 开户平台选项 | 「抖音 / B站 / 百度」 |
| 测试 | `npx vitest run`（在 `web/` 下）85 文件 / 762 测试全绿；新增 `shared/utils/platforms.test.js` 5 条 |

否定结论分母：`web/src` 内 `百家号|哔哩|xiaohongshu` 0 命中；阳性对照 `抖音` 12 命中（证明扫描不是空转），`bilibili: '` 只剩 `platforms.js` 自身。

## Cloud

| 项 | 实测 |
| --- | --- |
| 代码 | `PlatformBaijiahao` → `PlatformBaidu = "baidu"`；服务别名与 `validPlatform` 同步；`go test ./...` 85 包 0 FAIL |
| Migration | `20261027_076_media_account_platform_baidu.sql` 在开发库 `wt_media_cloud` 应用：`migration ok: 1 applied, 78 total` |
| 读回 1 | `SELECT platform, COUNT(*)` → `bilibili 7`，无 `baijiahao` 行 |
| 读回 2 | `information_schema.CHECK_CONSTRAINTS` 的 `chk_media_accounts_platform` 为 `platform in ('douyin','bilibili','baidu')` |
| 读回 3 | 事务内 `INSERT platform='baidu'` 成功后 `ROLLBACK`；`INSERT platform='baijiahao'` 返回 `ERROR 3819 Check constraint ... violated`；探针残留 0 行 |
| 残留 | `git grep baijiahao` 仅命中历史 migration `20260714_002_media_accounts.sql:28`（已应用的历史文件，不回改） |

## Agent

| 项 | 实测 |
| --- | --- |
| 重命名 | `clients/baijiahao/` → `clients/baidu/`，`identify_baijiahao` → `identify_baidu`，`BAIJIAHAO_HOST` → `BAIDU_LOGIN_HOST`；`LOGIN_URLS` 键改 `baidu`，URL 仍为 `https://baijiahao.baidu.com/`（登录态实际所在站点） |
| 任务入口 | `executors/account_check.py` 与 `local_api/server.py` 接受集合与分支改 `baidu` |
| 测试 | `PYTHONPATH=src .venv/bin/python -m unittest discover -s tests` 728 tests OK |
| 合同 | `contracts/local-agent-api/v1/local-agent.openapi.yaml` → `2026.10.27.1`；README 修订号同步（契约文档一致性用例先红后绿） |
| 残留 | `git grep baijiahao` 仅剩登录 URL `baijiahao.baidu.com` 与 OpenAPI 变更说明各一处 |

`REQUIRED_CONTRACT_REVISION`（cloud_agent_api）未改。

## 合同与发布

| 项 | 实测 |
| --- | --- |
| cloud-api `media-accounts.openapi.yaml` | `2026.07.14.3` → `2026.10.27.3`，Platform enum `[douyin, bilibili, baidu]` |
| business-schemas `media-account.yaml` | `2026.10.23.1` → `2026.10.27.2` |
| business-enums `media-account.yaml` | `2026.07.14.3` → `2026.10.27.1` |
| Desktop `contracts.lock.json` | `local_agent_api: v1@2026.10.27.1` |
| `config/contract-map.yaml` | cloud_api `2026.10.27.3`、business_schemas `2026.10.27.2`、business_enums `2026.10.27.1`、local_agent_api `2026.10.27.1` |
| `config/release-matrix.yaml` | 新增 `platform-identifier-rename-20261027`（status `verifying`，登记发布顺序与回滚） |
| 校验 | `python3 scripts/verify/verify_m0_config.py` → Workspace config verification ok；`verify_delivery_governance.py` / `verify_product_master_alignment.py` / `verify_ai_workspace.py` 全通过 |

## 未覆盖

- 真实页面按三账号读回中文平台名并入 T-26。
- 本机 Cloud API 进程仍是改动前二进制；T-26 重启后读回。
- 生产/外部环境不存在 `baijiahao` 历史数据的前提未验证；migration 076 只改写本机开发库与后续部署库。
