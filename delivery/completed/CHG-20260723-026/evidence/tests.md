# CHG-20260723-026 Task 5 Evidence：自动验证汇总

> 日期：2026-07-23

## 后端验证

命令：

```bash
env GOCACHE=/Users/aqiuye/Develop/workspace/wt-media/wt-media-cloud/.cache/go-build go test ./internal/modules/profilebinding ./internal/modules/identity
```

结果：PASS

覆盖：

- Profile 扫描、Diff 暂存、确认应用；
- 主账号确认与静默换绑阻断；
- 本地可信节点阻断；
- Cloud 窗口授权；
- 已被媒体账号引用窗口的授权阻断；
- 用户权限、分组、游戏访问控制基础逻辑。

## 前端单元测试

命令：

```bash
npm --prefix wt-media-cloud/web test -- --run profileBindings usersApi localAgentService
```

结果：PASS

覆盖：

- Cloud Profile API 客户端；
- 用户/运营分组/游戏 API 客户端；
- Desktop Local Agent Tauri 调用封装；
- Profile Restore payload 不携带 Cookie、授权用户或敏感字段；
- Cloud 窗口授权 API 请求。

## Desktop Rust 验证

命令：

```bash
cargo test --manifest-path wt-media-desktop/src-tauri/Cargo.toml
cargo check --manifest-path wt-media-desktop/src-tauri/Cargo.toml
```

结果：PASS

备注：

- `cargo test/check` 仍存在既有 unused/dead_code warning，不影响本 CHG 功能验证。

## 前端构建

命令：

```bash
npm run build:desktop --prefix wt-media-cloud/web
npm run build:cloud --prefix wt-media-cloud/web
```

结果：PASS

备注：

- Vite 输出 chunk size warning，属于既有构建体量提示，不阻塞本 CHG。

## Diff 检查

命令：

```bash
git -C wt-media-cloud diff --check
git -C wt-media-desktop diff --check
git -C wt-media-workspace diff --check
```

结果：PASS

备注：

- `wt-media-workspace/docs/engineering/.DS_Store` 是既有无关脏文件，未纳入本 CHG 提交。
