# RC 发布人工脚本证据

- 操作说明：`scripts/release/README.md` 写明先推送变更组件的源码分支、再按完整 commit SHA 预检并推送组件 Tag、提交并推送产品 Manifest、最后预检并推送产品 Tag。产品 Tag 触发原有 `release.yml`；人工不直接创建 GitHub Release。
- 组件脚本：`scripts/release/submit_component_tag.py` 从 `config/repository-map.yaml` 定位 Cloud、Agent、Desktop 仓库。预检确认指定 commit 在本地及 GitHub 存在、Tag 名称可用；`--push` 创建 annotated Tag，并回读远端 Tag 对象。相同对象重试可识别，冲突对象拒绝覆盖。
- 产品脚本：`scripts/release/submit_tag.py` 新增 `--verify`，可与 `--push` 一起执行，也可在 Tag 已推送后单独重试。它按产品 Tag 查找并等待 `release.yml`，确认 Pre-release 资产清单，下载六项资产，验证每个 SHA-256 和 `build-info.json` 的产品 Tag，输出 Windows 安装包摘要。
- 测试：`uv run --with pyyaml==6.0.3 --no-project python -m unittest tests.test_submit_component_tag tests.test_submit_tag -v`，12 项通过；包括本地裸仓库真实 Tag 推送、未推送 commit 拒绝、冲突 Tag 拒绝、发布资产正确校验与错误摘要拒绝。
- 实际只读回读：`uv run scripts/release/submit_component_tag.py agent v0.2.2-rc.3 106f6ffb1942b90d2269f1e55fef3e4ec4423562` 返回“已发布且对象一致”。RC17 Run 成功；GitHub 发布六项资产本地下载后 `shasum -a 256 -c SHA256SUMS` 全部通过。
- 边界：脚本不提交源码、不自动挑选 commit、不部署 Cloud；Windows D: 目录下载和 Cloud 成功状态仍需真机验收。
