# T-12 个人信息页本机展示信息

## 实施事实

- Cloud Vue 个人信息页把两处账号行改为“绑定比特账号”“当前比特账号”，并在 Desktop 上展示设备 ID、操作系统、CPU 架构、Agent 状态与版本。
- Desktop 从操作系统机器标识派生应用专用的 128 位哈希展示 ID。原始标识不交给 Vue、Cloud 或 Agent；读取失败时页面显示“无法读取”，不使用可能重复的 Agent ID。
- 本机设备 ID 与 Agent 状态独立读取。Agent 不可达时，页面仍能展示设备 ID，并把 Agent 状态显示为“无法连接”。

## 验证

| 动作 | 期望 | 实际 | 结果 |
| --- | --- | --- | --- |
| `cargo test -p wt-media-desktop-shell device_identity::tests --offline` | 派生稳定、不同机器输入不同、原生输出可解析、本机连续读取一致 | 3 个测试通过 | PASS |
| `npm test -- localAgentStatus.test.js workEnvStatus.test.js` | 原有 Agent 状态与环境判断不回归 | 26 个测试通过 | PASS |
| `npm run build:desktop` | Vue Desktop 构建成功 | 构建成功 | PASS |
| `cargo tauri build` | 新原生命令与前端一同进入 macOS App 和 DMG | 两个 bundle 生成 | PASS |
| `python3 scripts/verify/verify_delivery_governance.py` | 交付记录与索引有效 | 检查通过 | PASS |
| `python3 -B -m unittest discover -s tests` | Workspace 测试通过 | 174 个测试运行，全部通过 | PASS |
| 个人信息页真实登录后 GUI 走查 | 新字段正确显示 | 当前验证环境无可用登录账号，尚未执行 | 待验证 |

Workspace 测试依赖 `yaml`。修复前默认解释器（Homebrew Python 3.14，PEP 668 externally-managed）没有 `PyYAML`，3 个发布模块在导入期失败：151 项、`errors=3`。已用 `python3 -m pip install --user --break-system-packages PyYAML` 装到用户 site-packages（PyYAML 6.0.3），同一条命令重跑为 174 项全绿，不再需要一次性 venv。

Windows 与 Linux 原生机器标识读取已实现，但本次只在 macOS 实机验证。
