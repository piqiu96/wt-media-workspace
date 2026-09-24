# 证据 — T-10 引入 `tracing` + `tracing-subscriber`

范围：裁定（批注）「这里需要重新确定，使用后端的方案」——**只用官方后端**，
`tracing` + `tracing-subscriber`。本 Task 是计划里**明示的例外**：没有「先失败的测试」，
判据是依赖树的前后对比 + 具名的下载清单 + 起点测试数不动。

提交：`wt-media-desktop`（`Cargo.toml` + `Cargo.lock`，见 change.md 的 T-10 行）。
改动面：**两行依赖 + 一段说明注释，零源码改动**。

---

## 1. 起点

`cd wt-media-desktop/src-tauri && cargo test --workspace` → **68 passed; 0 failed**。
与计划登记的起点（68；CHG-060 checkpoint「测试 63 → 68」为终点）**一致，无偏差**。

依赖树起点：`cargo tree --prefix none --no-dedupe | sort -u | wc -l` → **267** 个具名节点。
其中 `tracing v0.1.44` 与 `tracing-core v0.1.36` **已在树里**（h2 / hyper-util / softbuffer
的传递依赖），`tracing-subscriber` **不在**。

## 2. 加的是什么

```toml
tracing = { version = "0.1", default-features = false, features = ["std"] }
tracing-subscriber = { version = "0.3", default-features = false, features = ["fmt", "std"] }
```

| 决定 | 理由 |
|---|---|
| `tracing` 关掉默认 features | 默认含 `attributes`（拖进 `tracing-attributes` 过程宏），本仓不用 `#[instrument]`；`tracing-log` 桥也不需要 |
| `tracing-subscriber` 关掉默认 features | 默认会开 `env-filter`（`matchers` + `regex`）与 `ansi`（`nu-ansi-term`）；本 CHG 的级别来自 `[logging]` 配置，不用环境变量过滤，日志文件也不要 ANSI |
| **不引 `tracing-appender`** | 它的 rolling 只能按日期切文件，表达不了 20MB 单文件上限、总量预算与「单条超限截断」这三条硬验收；writer 无论走哪个方案都是自写的（T-12） |
| **不自写后端、不留降级路径** | 本轮批注。`cargo fetch` 失败按阻塞处理，不换实现 |

## 3. 依赖树前后对比：恰好 +4，且具名

```
before=267  after=271
=== added ===
lazy_static
sharded-slab
thread_local
tracing-subscriber
=== removed ===
（无）
```

锁定版本（`Cargo.lock` 新增条目）：`tracing-subscriber v0.3.23`、`sharded-slab v0.1.7`、
`thread_local v1.1.10`、`lazy_static v1.5.0`。

`tracing-subscriber` 实际启用的 features（`cargo tree -e features -i`）只有
`fmt` / `registry` / `sharded-slab` / `std` / `thread_local` / `alloc`，**没有 `env-filter` / `json` /
`regex` / `time` / `ansi`**；`tracing` 只启用 `std`。

### 3.1 阴性对照：刻意避开的那些 crate 确实没进来

| crate | 改前在树里 | 改后在树里 | 说明 |
|---|---|---|---|
| `nu-ansi-term` | 0 | **0** | 关 `ansi` 的效果 |
| `matchers` | 0 | **0** | 关 `env-filter` 的效果 |
| `tracing-log` | 0 | **0** | 关默认 features 的效果 |
| `tracing-attributes` | 0 | **0** | `tracing` 关默认 features 的效果 |
| `regex` | **1** | 1 | **本来就在树里**（别的依赖拉的）——所以「不引 `env-filter`」省下的不是 regex，是 matchers/nu-ansi-term |
| `smallvec` | 1 | 1 | 同上，本就在树里 |

这一列的用途是防止把「本来就有」记成「我们的开销」。

## 4. 起点测试不动，lint 不动

- `cargo test --workspace` → **68 passed; 0 failed**（与改前逐字相同；本 Task 按计划不加测试）。
- `cargo clippy --workspace --all-targets` 警告数 **before=10 / after=10**（同一条命令、同一筛法，
  用 `git stash` 取得改前的读数）。既有的 10 条是源码里的（`drain` 测试的 `assert!(…is_some())`
  与 `SystemBridge`/`Updater` 未构造），与本次依赖无关，也没有新增。
- `cargo build` 成功。

## 5. 一处环境阻塞与它的根因（不是本仓的问题，但记在这里）

第一次 `cargo add tracing-subscriber` 失败：

```
Updating crates.io index
error: failed to load source for dependency `tracing-subscriber`
Caused by: download of config.json failed
Caused by: [60] SSL peer certificate or SSH remote key was not OK
           (SSL certificate problem: certificate has expired)
```

**先证根因，没有直接换实现，也没有直接报障**：

| 路径 | 结果 |
|---|---|
| 直连 `index.crates.io:443` | TLS 落在 `issuer=Let's Encrypt CN=YE1`、`notBefore=Sep 14 / notAfter=**Sep 20 2026**` 的证书上，且**主题名不匹配**该主机 → 证书 4 天前已过期，且不是 crates.io 的真证书（被劫持/污染的路径） |
| 经 `http://127.0.0.1:7897`（开发者本机代理，macOS 系统代理设置里就有） | `config.json` **200**；`tracing-subscriber-0.3.20.crate` **200 / 212274 字节**（`file` 认作 gzip 归档）→ 代理是好的 |

即：**`curl` 与 `cargo` 都不读 macOS 的 `scutil --proxy` 设置**，于是两者都走了直连那条坏路。
修法是**本次调用带上 `HTTPS_PROXY=http://127.0.0.1:7897`**，走官方 crates.io 后端下载——
这既不是换实现，也不写进仓库配置（写了就把「某台机器的 localhost 代理」固化进出货产物）。

后续 Task 若还需访问 registry，同样需要这个环境变量。**这是环境事实，不是本 CHG 的缺陷**，
登记在此以免后来者把它当成「依赖装不上」。
