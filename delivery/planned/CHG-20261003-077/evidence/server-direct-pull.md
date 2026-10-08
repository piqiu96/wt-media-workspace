# RC14 Cloud Artifact 服务器直拉步骤验证

- 用户要求：宝塔服务器直接从 GitHub 拉取 Cloud 部署输入，不通过本地电脑下载与上传。
- 固定输入：产品 `v0.1.0-rc.14`，Run `37581481877`，Actions Artifact `cloud-linux-amd64`，Cloud tar SHA-256 `e7ea73b3984c4735d3e61db1a008ff1e8ea0c48966cf50cc39b0323485d9ac4e`。执行步骤见 `server-acceptance.md`。
- 命令核对：从 `server-acceptance.md` 抽取直拉 Bash 块后执行 `bash -n`，PASS；本机 `gh run download --help` 确认 `--repo`、`--name`、`--dir` 参数存在，PASS。此前从同一 Run 下载的 Cloud tar 经本机 `shasum -a 256` 再次核对，与固定摘要一致，PASS。
- 权限与失败边界：私有 Workspace 仓库需要 Actions 只读权限；无 `GH_TOKEN`、非 x86_64、包目录已存在、下载失败或摘要不符时命令停止，不进入迁移和 `current` 切换。服务器上的凭据注入、网络和实际执行仍待用户验收。
- 结论：本地命令语法与固定制品核对通过；尚不能宣称宝塔服务器直拉、数据库迁移或运行验收通过。
