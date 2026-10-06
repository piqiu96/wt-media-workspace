# 手动提交产品 Tag

先提交并推送 Cloud、Agent、Desktop 的固定组件 Tag，再把同名产品 Manifest 提交并推送到 Workspace 分支。产品 Tag 的推送事件触发唯一的 `.github/workflows/release.yml`，不需要单独运行第二条打包工作流。

预检（只读）：

```bash
uv run scripts/release/submit_tag.py v0.1.0-rc.14
```

提交产品 Tag 并触发 GitHub Actions：

```bash
uv run scripts/release/submit_tag.py v0.1.0-rc.14 --push
```

脚本要求 Manifest 已提交且当前 Workspace 分支已推送到 `origin`；检查 Manifest 结构、三个组件 Tag、已有产品 Tag 和远端分支提交。`--push` 创建不可移动的 annotated Tag，推送后通过 GitHub API 回读 Tag 对象。若网络在推送前中断，已创建但尚未推送、且仍指向当前 Commit 的本地 Tag 可用同一命令重试。构建进度与制品摘要仍需在 GitHub Actions 和 Pre-release 中核对。
