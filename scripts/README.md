# WT Media Workspace Scripts

本文件是 `scripts/` 的逐文件用途索引。每个可执行脚本都必须在下表登记；`tests/test_scripts_index.py` 会检查未登记的新文件。

## 逐文件索引

| 路径 | 类型 | 用途 | 调用方式 |
| --- | --- | --- | --- |
| `bin/control.sh` | 入口 | 本地开发环境启停、状态与 readiness 验收的稳定入口 | `bin/control.sh <start\|stop\|restart\|status\|verify\|help>` |
| `scripts/wt.py` | 入口 | 唯一 CLI：`status`、`chg`、`dev`、`test` 的薄分派 | `python3 scripts/wt.py ...` |
| `scripts/chg/__init__.py` | 库 | CHG 共享必要条件：仓库映射、Git、依赖提交、References、handoff | 不直接执行；由 `wt chg` 调用 |
| `scripts/chg/start.py` | CHG 动词 | `wt chg start`：依赖、main、脏树与分支预检 | 由 `scripts/wt.py` 调用 |
| `scripts/chg/resume.py` | CHG 动词 | `wt chg resume`：重生成上下文、报告 main 漂移与 checkpoint | 由 `scripts/wt.py` 调用 |
| `scripts/chg/verify.py` | CHG 动词 | `wt chg verify` 的风险→场景策略 | 由 `scripts/wt.py` 调用 |
| `scripts/docs/check.py` | 校验入口 | 文档分类、索引、标记与相对链接检查 | `python3 scripts/docs/check.py` |
| `scripts/dev/local_env.py` | 实现 | `bin/control.sh` 下游：本地环境启停、状态、验收与 DMG | `python3 scripts/dev/local_env.py <verb>` |
| `scripts/lib/change_metadata.py` | 库 | 新/旧格式 CHG 元数据解析 | 不直接执行 |
| `scripts/lib/workspace_config.py` | 库 | 仓库映射与 Skill 分发配置读取 | 不直接执行 |
| `scripts/prepare_ai_workspace.py` | 维护入口 | 生成 `.ai/CURRENT_CONTEXT.md` 执行快照 | `python3 scripts/prepare_ai_workspace.py --change <CHG>` |
| `scripts/sync_skills.py` | 维护入口 | 按 `config/skills-distribution.yaml` 检查或分发 Skills | `python3 scripts/sync_skills.py check\|sync` |
| `scripts/build-desktop-frontend.sh` | 构建 | 构建 Desktop 前端并复制到 Desktop 仓库 | `bash scripts/build-desktop-frontend.sh` |
| `scripts/verify/verify_ai_workspace.py` | 验收 | AI 入口文件、执行快照与配置一致性 | `python3 scripts/verify/verify_ai_workspace.py` |
| `scripts/verify/verify_delivery_governance.py` | 验收 | Delivery、CHG 引用与只读归档边界 | `python3 scripts/verify/verify_delivery_governance.py` |
| `scripts/verify/verify_m0_config.py` | 验收 | Contract map、release matrix 与契约版本 | `python3 scripts/verify/verify_m0_config.py` |
| `scripts/verify/verify_m1_integration.py` | 验收 | M1 Cloud-Agent-Desktop 跨端集成（行为已知阻塞，见根 README） | `python3 scripts/verify/verify_m1_integration.py` |
| `scripts/verify/verify_m2_acceptance.py` | 验收 | M2 静态跨仓验收矩阵 | `python3 scripts/verify/verify_m2_acceptance.py` |
| `scripts/verify/verify_m3_acceptance.py` | 验收 | M3 真实环境全量验收 | `python3 scripts/verify/verify_m3_acceptance.py --phase all` |
| `scripts/verify/verify_product_master_alignment.py` | 验收 | 状态词、LEDGER 行与 Milestone 对齐 | `python3 scripts/verify/verify_product_master_alignment.py` |
| `scripts/verify/verify_skills.py` | 验收 | Skill 源文件与 frontmatter | `python3 scripts/verify/verify_skills.py` |
| `scripts/verify/verify-control.sh` | 验收 | `bin/control.sh` 的判别式验收 | `bash scripts/verify/verify-control.sh` |
| `scripts/verify/verify_m0_local.sh` | 聚合验收 | M0 本地全套：单测、治理门禁、文档检查、三仓构建/测试 | `sh scripts/verify/verify_m0_local.sh` |
| `scripts/verify/windows_uninstall.ps1` | 验收 | Windows 安装包卸载验收 | 在 Windows 上执行；见脚本头 |
| `scripts/release/__init__.py` | 库 | 发布工具包标记 | 不直接执行 |
| `scripts/release/submit_tag.py` | 发布入口 | 校验并手动推送一个产品 Tag；正式版先建同名发布分支 | `uv run scripts/release/submit_tag.py <tag> --push --verify` |
| `scripts/release/submit_component_tag.py` | 发布入口 | 为指定源码提交预检或推送不可变组件 Tag | `python3 scripts/release/submit_component_tag.py ...` |
| `scripts/release/manifest.py` | 发布入口 | 校验产品 Release Manifest | `python3 scripts/release/manifest.py ...` |
| `scripts/release/stage_config.py` | 发布入口 | 向客户端构建输入写入公开 Cloud origin | `python3 scripts/release/stage_config.py ...` |
| `scripts/release/desktop_downloads.py` | 发布入口 | 生成公开的 Desktop 下载清单 | `python3 scripts/release/desktop_downloads.py ...` |
| `scripts/release/package_assets.py` | 发布入口 | 拒绝不完整 Release 并生成资产清单与校验和 | `python3 scripts/release/package_assets.py ...` |
| `scripts/release/tag_transport.py` | 库 | 经 GitHub Git Data API 推送精确 annotated Tag | 不直接执行；由发布入口调用 |
| `scripts/release/publish.sh` | 发布入口 | 发布 rc/stable Release 资产 | `bash scripts/release/publish.sh <rc\|stable> <tag> <assets-dir>` |
| `scripts/release/test_desktop_downloads.py` | 测试 | Desktop 下载清单生成器测试 | `python3 -m unittest scripts.release.test_desktop_downloads` |
| `scripts/release/test_package_assets.py` | 测试 | Release 资产与密钥边界测试 | `python3 -m unittest scripts.release.test_package_assets` |

发布流程细节见 [`release/README.md`](release/README.md)，本文件不重复。

## 落位规则

- CHG 动词与共享前置条件 → `scripts/chg/`。目录固定为 `__init__.py`、`start.py`、`resume.py`、`verify.py` 四个文件；共享逻辑进 `__init__.py`，不建 `common.py`、`checks/` 或 `scenario/`。`scripts/wt.py` 是唯一命令入口，`chg/*` 不带 `__main__`。
- 文档治理校验 → `scripts/docs/`。
- 本地环境行为 → `scripts/dev/`；`bin/` 只保留稳定的操作入口，不放实现或验收。
- 验收、门禁与聚合验证 → `scripts/verify/`。
- 被多处 import 的共享库 → `scripts/lib/`；库文件不带头部 shebang，不提供命令入口。
- 发布工具 → `scripts/release/`；流程说明留在该目录的 README。
- `scripts/` 根层只放名字自解释的稳定入口，或外部配置已经引用、移动会改变运行仓配置的文件。`build-desktop-frontend.sh` 属于后者：Desktop 的 Tauri 配置直接引用这个路径，所以保留在根层。
- **禁止纯转发脚本**：只 `exec` 或调用另一个脚本、自己不承载参数、退出码或环境语义的 wrapper 不新增。需要改调用方时直接改调用方。`bin/control.sh` 是唯一保留的稳定分派器，因为它承载动词映射、`restart` 组合和未知名词退出码 2。
- 新增 `.py` / `.sh` / `.ps1` 必须在上面登记；`tests/test_scripts_index.py` 未登记即红。
- 数值型运行参数（端口、地址、凭据、超时、保留期）只在配置或实现中；本文件和 `bin/control.sh` 都不复述，`verify-control.sh` 继续机检 `control.sh` 无端口字面量。

## 旧 → 新映射

| 旧路径 | 新路径 |
| --- | --- |
| `scripts/m2b_local_acceptance.py` | `scripts/dev/local_env.py` |
| `scripts/m2b-local-acceptance.sh` | 已删除；`bin/control.sh` 直接调用 `scripts/dev/local_env.py` |
| `scripts/verify_*.py` | `scripts/verify/verify_*.py` |
| `scripts/verify-control.sh` | `scripts/verify/verify-control.sh` |
| `scripts/verify_m0_local.sh` | `scripts/verify/verify_m0_local.sh` |
| `scripts/change_metadata.py` | `scripts/lib/change_metadata.py` |
| `scripts/workspace_config.py` | `scripts/lib/workspace_config.py` |

`scripts/wt.py` 仍是入口；新增 `scripts/chg/` 只是把三个 CHG 动词和共享前置条件归位。历史归档（`delivery/completed/`、`docs/superpowers/`、`delivery/reports/`）中的旧路径是历史叙述，不追改。
