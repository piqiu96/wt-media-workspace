# RC14 手动 Tag 与 GitHub 打包构建

- 目标：Cloud `v0.1.0-rc.12`（Commit `be1d1a11a603da475b4d6ce16244927adc8d8486`）与产品 `v0.1.0-rc.14`；Agent `v0.2.2-rc.2`、Desktop `v0.1.0-rc.3` 沿用已发布组件 Tag。产品 Manifest 为 `releases/manifests/v0.1.0-rc.14.yaml`。
- Tag 脚本 RED：`python3 -m unittest tests.test_submit_tag -v` 起初因 `scripts.release.submit_tag` 缺失失败。后续真实 Git HTTPS 远端引用预检遇到 `Empty reply from server`，此时产品 Tag 尚未创建；新增失败测试证明该预检依赖 Git 传输，并改由 GitHub API 读取远端引用。又新增失败测试验证本地 Tag 创建后网络中断的可恢复推送。GREEN：7 项本地裸仓库脚本测试通过，覆盖只读预检、真实 Tag 推送、远端引用 Git 传输故障、相同本地 Tag 重试，以及未推送分支、未提交 Manifest、缺失组件 Tag、重复产品 Tag 的拒绝行为。
- Cloud 验证：`go test ./... -count=1` 通过；`go vet ./internal/config ./internal/bootstrap ./cmd/config-check ./cmd/migrate` 通过；`python3 -m unittest scripts.verify.test_package_release_linux scripts.verify.test_stamp_desktop_web -v` 4 项通过。
- Cloud 推送：`codex/cloud-runtime-paths-logs` 已推送到 `origin`；`v0.1.0-rc.12` 已推送，`git ls-remote origin 'refs/tags/v0.1.0-rc.12^{}'` 回读为 `be1d1a11a603da475b4d6ce16244927adc8d8486`，PASS。
- Workspace Manifest：`uv run --with pyyaml==6.0.3 --no-project python scripts/release/manifest.py --file releases/manifests/v0.1.0-rc.14.yaml --tag v0.1.0-rc.14` 通过。
- Workspace 全量测试：`uv run --with pyyaml==6.0.3 --no-project python -m unittest discover -s tests -q` 共 106 项，5 项失败。失败项为旧 M0 Cloud workflow 的 `scripts/build.sh` 断言、两项旧 Cloud Agent Contract revision 断言、一项 Desktop Contract lock 断言，以及一项既有 CHG Product/Master 对齐断言。相关检查/合同文件不在本次 diff；这些失败未被记为通过，也不是 `release.yml` 的执行门禁。
- 待回填：更新后的 Workspace 分支和产品 Tag 推送、GitHub Actions Run、各平台构建结论、Cloud Artifact 摘要与 Pre-release 回读。
