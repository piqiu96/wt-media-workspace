# 人工提交 Tag 并发布产品 RC

在 Workspace 根目录执行以下命令。先将需要更新的 Cloud、Agent 或 Desktop 源码提交到各自仓库，并推送对应分支；记下准备发布的完整 40 位 commit SHA。已有且无需更新的组件 Tag 可以直接写入产品 Manifest。

## 1. 推送新组件 Tag

脚本按 `config/repository-map.yaml` 找到组件仓库，检查指定 commit 在本地和 GitHub 都存在。预检只读；`--push` 才创建 annotated Tag、推送并回读远端 Tag 对象。以下以 Agent 为例，Cloud、Desktop 将第一个参数分别改为 `cloud`、`desktop`。

```bash
AGENT_COMMIT='在此填写完整40位Agent提交SHA'
uv run scripts/release/submit_component_tag.py agent v0.2.2-rc.4 "$AGENT_COMMIT"
uv run scripts/release/submit_component_tag.py agent v0.2.2-rc.4 "$AGENT_COMMIT" --push
```

若 Tag 已在远端且与本地对象一致，脚本会报告已发布。若 Tag 名称已被其他对象使用，脚本拒绝覆盖。Git 推送超过 45 秒或失败时，脚本会使用已登录的 `gh` 通过 GitHub API 创建相同的 Tag 对象，并再次回读其 SHA。只更新确实变更的组件。

## 2. 推送产品 Tag 并等待发布

把 `releases/manifests/<产品Tag>.yaml` 提交到 Workspace 分支并推送。Manifest 固定三个组件 Tag；产品 Tag 推送会触发唯一的 `.github/workflows/release.yml`，由 CI 构建、打包并发布 Pre-release。

```bash
git push origin HEAD
uv run scripts/release/submit_tag.py v0.1.0-rc.19
uv run scripts/release/submit_tag.py v0.1.0-rc.19 --push --verify
```

产品脚本预检 Manifest 结构、三个远端组件 Tag、当前 Workspace 分支提交和重复 Tag。`--push` 创建并推送 annotated 产品 Tag；Git 推送失败时也使用相同的 GitHub API 备用路径。`--verify` 等待该 Tag 的 `release.yml` 成功，再从 GitHub Release 下载全部六项资产，检查资产清单、`SHA256SUMS`、`build-info.json` 的产品 Tag，并输出 Windows 安装包 SHA-256。发布任务失败或任一资产不符时命令返回非零。

如果 Tag 已推送而本机等待或下载中断，仅重做只读发布校验：

```bash
uv run scripts/release/submit_tag.py v0.1.0-rc.19 --verify
```

脚本不会自动部署 Cloud 或代替 Windows 真机验收。对 RC17 已发布资产可用 `v0.1.0-rc.17 --verify` 回读校验。

## 官网桌面安装包下载清单

清单 `desktop-downloads.json` 由 CI 在构建期自动生成：正式版（`channel: stable`）的 `release.yml` 在 vite 产出 `web/dist-cloud` 之后、打入 Cloud 包之前，按产品 Tag 生成清单覆盖 `web/dist-cloud/desktop-downloads.json`，随后随 Cloud 包部署到 `current/web/` 生效。RC/预览构建不执行该步骤，预览包保留仓库初始清单。清单仅保存公开 GitHub Release 的 URL，访客下载时直接前往 GitHub；不会下载安装包到 Cloud 服务器。

部署顺序约束：CI 在资产校验通过后自动公开发布正式版 Release，正常流程中部署总在 CI 之后；若人工干预过 Release 状态（如重新转草稿），部署前需确认 Release 已公开（`gh release view vX.Y.Z --json isDraft,isPrerelease`）。顺序颠倒时官网下载链接在 Release 公开前指向 404，公开后自愈。每次部署后用 `curl https://<Cloud域名>/desktop-downloads.json` 回读版本号与三项 URL，并在目标用户网络中分别点击验证下载。

### 手动兜底

只更新桌面端而不重新部署 Cloud 包，或回滚后需要钉住指定版本时，在服务器上直接运行生成脚本（单文件、纯标准库、无需 `gh`）：

```bash
python3 desktop_downloads.py --tag v0.1.0 \
  --output /home/www/wt-media-cloud/current/web/desktop-downloads.json
```

`desktop_downloads.py` 位于 Workspace 仓 `scripts/release/`；目标 Web 目录以 `wtmctl` 实际布局为准（执行前 `readlink -f current` 确认）。写入为临时文件原子替换，Tag 非正式版或目录不存在时不触碰旧清单。

## 正式版

人工验收确认后，增加 `releases/manifests/vX.Y.Z.yaml`，`channel: stable`，记录固定组件 Tag 和生产环境 Cloud origin。提交并推送 Manifest 后，用 `submit_tag.py vX.Y.Z --push --verify` 触发相同的构建和资产校验。正式版工作流先创建 Draft Release 并复验资产名与 SHA256，校验全部通过后**自动公开发布**（`publish-release` job 内 `gh release edit --draft=false --prerelease=false` 并回读断言状态），无需人工执行公开命令；`submit_tag.py --verify` 只核对资产与摘要、不区分草稿与公开状态。正式版从 Tag 重新构建，不把 RC 附件改名；构建期已把对应版本的官网下载清单烙入 Cloud 包，CI 绿即公开，按上一节部署即可。
