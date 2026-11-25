# 全新环境门禁（PASS）

2026-11-25，统一入口 `python3 scripts/dev/local_env.py all --force-restart` 完成787d4e1环境与安装包，实际退出0，日志 `/tmp/chg110-environment-delivery.log`。使用既有operator01凭证，未重置密码。

Cloud/API、发现worker、Compose worker/scheduler、Agent8765、BitBrowser54345、Web5173、Desktop dev5174、生产资源无预置loopback、CORS、登录、签名/DMG哈希/挂载版本全部PASS。构建完成后 `up --force-restart` 建独立Agent，再串行 `wt chg verify CHG-20261125-110` 退出0（`/tmp/chg110-governance-serial.log`），Cloud测试、Workspace220测试、集成门禁通过，避免构建中读取暂时移除的app或安装版Agent令牌。

之后 `launch-dmg` 实际挂载 `../.local/m2b/desktop-review-mount/起飞.app`；frontend `0.1.0+787d4e1.dirty`，shell `0.1.0-local.0764ec2ed7`，Agent0.3.0。dirty来自其他会话example原型工作，正式功能源码无未提交修改，生产不引用example。日志 `/tmp/chg110-delivery-launch.log`。

18:34安装版实际登录operator01，读回已结束批次与计划，快速多类目勾选回归通过；工作环境显示三项就绪。真实发布证据见real-operations.md。合并main后的新包版本将在最终交付记录补齐。
