# M2-E 源码与 macOS 私有分发验证（2026-09-13）

## 已验证

- Agent frozen sidecar 本机启动后 `/healthz` 返回 `status=ok`，Ctrl-C 停止正常。
- Desktop Rust 单元测试：11/11 通过；`cargo fmt -- --check` 已通过（先执行 `cargo fmt`）。
- Cloud Web Local Agent 边界、状态和启动服务测试：3 个测试文件、10/10 通过。
- Agent sidecar 入口与代理解绑定向测试：5/5 通过。
- 已构建的 macOS ARM64 DMG：App 内 `codesign --verify --deep --strict` 通过；构建日志确认使用 ad-hoc identity `-`，无 Apple 开发者证书也可完成 App 签名。

## 发布边界

- release 只从 Tauri `externalBin` 启动包内 Agent；未找到 Sidecar 时返回明确错误，不回退客户机 Python。
- Python fallback 仅限 debug 构建且必须显式设置 `WT_MEDIA_DESKTOP_ALLOW_PYTHON_FALLBACK=1`。
- Vue 不再直连 `127.0.0.1:8765`；Desktop 入口通过 Rust invoke 启动 Local Agent。
- macOS ARM64/Intel 使用各自原生 Sidecar；Windows x64 仅允许在 Windows 原生环境构建。
- Agent 数据目录由 Agent 管理，构建脚本不删除或覆盖用户数据。

## 未完成的人工步骤

上一轮 DMG 构建完成后，Desktop `main.ts` 又补充了 Desktop 入口显式启动 Agent 的修正；本轮重新构建请求被执行环境 usage limit 拦截，因此现有 DMG 尚未包含该最后修正。额度恢复后需运行：

```text
bash scripts/build-release-macos.sh
```

随后在另一台未预装 Python 的 macOS 上完成安装、首次“未知开发者”放行、启动/健康/停止和数据目录保留验收。ad-hoc 签名不等于 Apple 证书，也不绕过 Gatekeeper。
