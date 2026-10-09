# 人工提交 Tag 并发布产品 RC

在 Workspace 根目录执行以下命令。先将需要更新的 Cloud、Agent 或 Desktop 源码提交到各自仓库，并推送对应分支；记下准备发布的完整 40 位 commit SHA。已有且无需更新的组件 Tag 可以直接写入产品 Manifest。

## 1. 推送新组件 Tag

脚本按 `config/repository-map.yaml` 找到组件仓库，检查指定 commit 在本地和 GitHub 都存在。预检只读；`--push` 才创建 annotated Tag、推送并回读远端 Tag 对象。以下以 Agent 为例，Cloud、Desktop 将第一个参数分别改为 `cloud`、`desktop`。

```bash
uv run scripts/release/submit_component_tag.py agent v0.2.2-rc.4 <完整40位Agent提交SHA>
uv run scripts/release/submit_component_tag.py agent v0.2.2-rc.4 <完整40位Agent提交SHA> --push
```

若 Tag 已在远端且与本地对象一致，脚本会报告已发布。若 Tag 名称已被其他对象使用，脚本拒绝覆盖。只更新确实变更的组件。

## 2. 推送产品 Tag 并等待发布

把 `releases/manifests/<产品Tag>.yaml` 提交到 Workspace 分支并推送。Manifest 固定三个组件 Tag；产品 Tag 推送会触发唯一的 `.github/workflows/release.yml`，由 CI 构建、打包并发布 Pre-release。

```bash
git push origin HEAD
uv run scripts/release/submit_tag.py v0.1.0-rc.18
uv run scripts/release/submit_tag.py v0.1.0-rc.18 --push --verify
```

产品脚本预检 Manifest 结构、三个远端组件 Tag、当前 Workspace 分支提交和重复 Tag。`--push` 创建并推送 annotated 产品 Tag；`--verify` 等待该 Tag 的 `release.yml` 成功，再从 GitHub Release 下载全部六项资产，检查资产清单、`SHA256SUMS`、`build-info.json` 的产品 Tag，并输出 Windows 安装包 SHA-256。发布任务失败或任一资产不符时命令返回非零。

如果 Tag 已推送而本机等待或下载中断，仅重做只读发布校验：

```bash
uv run scripts/release/submit_tag.py v0.1.0-rc.18 --verify
```

脚本不会自动部署 Cloud 或代替 Windows 真机验收。对 RC17 已发布资产可用 `v0.1.0-rc.17 --verify` 回读校验。
