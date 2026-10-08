# Windows Agent 下载提交故障证据

- Windows 真机回归：两个任务在进度 99% 后重复记录 `executor_error` / `[Errno 9] Bad file descriptor`。用户提供的 D: 盘类型为固定 NTFS；对应 `.part` 大小分别为 16,348,585 与 37,033,927 字节，均等于其所有分片长度之和。分片合并已经发生，故障集中在合并后的提交路径。
- 权限观察：用户提供的文件 ACL 中 Administrators 为完全控制，Users 为读取；`whoami /groups` 来自 High Mandatory Level 进程。该信息不证明 Desktop 的实际令牌，但已完整写入的 `.part` 排除了下载阶段完全无法写入。
- 根因：`DownloadSink.commit` 在 Windows 上以只读句柄打开 `.part` 后调用 `os.fsync`，而 Windows 文件刷新要求可写句柄；随后原实现还尝试对目录调用 POSIX 风格 `fsync`。`os.replace` 在这两步之间，故首个失败会保留 `.part` 且没有最终文件。
- 修复：Agent commit `106f6ff` 使 Windows 使用可写句柄同步已校验的 `.part`，重命名后跳过不兼容的目录 `fsync`；POSIX 同步顺序保留。无 Cloud API、数据库或任务状态协议变更。
- 本地复现与验证：新增 Windows 句柄语义故障注入测试；旧代码运行 `PYTHONPATH=src python3 -m unittest discover -s tests -p test_download_sink.py -v` 得到 `OSError: [Errno 9] Bad file descriptor`；修复后同文件 61 项通过，`test_material_download_executor.py` 78 项通过，Agent 全量 `python3 -m unittest discover -s tests` 701 项通过。全量运行有既有资源清理警告，但无失败。
- 发布源核对：Agent 工作区另有未提交改动，因此从 commit `106f6ff` 建立独立本地克隆并运行 `PYTHONPATH=src python3 -m unittest discover -s tests`，690 项通过。最初仅用 `git archive` 的核对因缺少 `.git`，两项 Git 索引检查失败；本地克隆保留 Git 元数据后两项均通过。
- 发布准备：Agent annotated Tag `v0.2.2-rc.3` 已推送并通过 GitHub API 回读，Tag 对象 `435be3a2b12e3a21726f6e1214f7dcd331572a02` 指向 commit `106f6ff`。产品 `v0.1.0-rc.17` Manifest 固定 Cloud `v0.1.0-rc.13`、Agent `v0.2.2-rc.3`、Desktop `v0.1.0-rc.5`，本地 Manifest 校验和发布脚本 4 项测试通过。
- 待验证：Windows 包构建、D: 保存目录上的最终文件及 Cloud 成功状态仍需真机验收；旧任务可能因默认三次领取上限已失败，不能仅凭 `.part` 手工标记成功。
