# Task 4：集成核对

- 命令：`python3 scripts/release/update_desktop_downloads.py v0.1.0 --output /tmp/wt-desktop-downloads-verify.json`，随后 `cmp` 与 Cloud `web/public/desktop-downloads.json` 比较。
- 实际：脚本返回 0，`cmp` 返回 0；三个 URL 与当前 GitHub Release 回包一致。
- 命令：`python3 scripts/verify_delivery_governance.py`；实际通过，活动 CHG 为 CHG-20261010-078。
- 命令：两仓 `git diff --check`；实际通过。
- Web/Go/视觉结果分别见 Task 2–3 Evidence。
- 未宣称：线上 `/home` 可用、真实账号登录、用户网络可下载三平台包；本机 GitHub 下载地址 HEAD 请求超时，这三项需要部署后人工验收。
