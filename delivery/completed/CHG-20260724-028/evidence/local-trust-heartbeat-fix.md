# 本机可信绑定稳定性修复

## 时间

2026-07-24 22:19:30 +0800

## 人工验收问题

用户反馈：Desktop完成可信绑定后，使用过程中会时不时提示本机不可信，需要人工再次绑定。

## 根因判断

Cloud的`CheckLocalTrust`要求本机节点`last_heartbeat_at`在新鲜窗口内；当前实现只在绑定时上报一次运行状态，后续“重新检测本机环境”、Profile扫描、接受本地变化和账号检查前没有稳定刷新Cloud心跳。

因此，用户在同一Desktop停留超过Cloud freshness窗口后，本机节点会被判断为不可信，表现为“绑定自动断了”。

## 修复

- Desktop Rust新增`local_agent_refresh_runtime`命令：
  - 使用Rust内存中的`node_id`和`node_credential`；
  - 读取Local Agent当前状态；
  - 向Cloud上报runtime report刷新`last_heartbeat_at`；
  - 不创建新节点，不重新绑定，不改变BitBrowser主账号绑定。
- Desktop账号检查在Cloud预检前先刷新runtime report，避免超过90秒后预检失败。
- Desktop Web本机服务新增`refreshRuntime()`，Vue仍不接触node credential或Local Agent动态凭据。
- 环境状态页“刷新本机可信状态”：
  - 已有本地node时优先刷新Cloud心跳；
  - 如果Tauri重启导致Rust内存凭据丢失，再走重新绑定；
  - 不允许切换BitBrowser主账号后静默改绑。
- 浏览器窗口扫描、接受本地变化、恢复Cloud配置前使用`refreshRuntime()`刷新Cloud可信状态。
- 媒体账号单个检查前使用`refreshRuntime()`刷新Cloud可信状态，并修正Desktop dev下Rust调用Cloud地址为`18080`。

## 追加修复：降低误判掉线和无差异操作成本

用户继续验收发现：

- 绑定后部分操作延迟较高，像是每次操作都重新刷新本机可信状态；
- 前端偶发显示“无可用环境”或“身份不可信”，但环境状态页显示本机节点仍可信；
- 浏览器窗口扫描没有差异时仍出现“接受本地变化 / 恢复Cloud配置 / 取消变更”，容易误导用户做不必要保存。

本次追加修复：

- Desktop账号检查和浏览器窗口页面增加60秒本机可信刷新缓存；
- 当Cloud可信状态刷新暂时失败，但Rust/Local Agent本地仍能读到`node_id`时，前端不立刻把当前电脑判定为掉线；继续交给Cloud预检做最终阻断；
- 浏览器窗口扫描Diff为0时，抽屉展示“本机窗口与Cloud记录一致，无需处理”，并隐藏接受、恢复、取消变更按钮，只保留关闭；
- 保持BitBrowser主账号不一致时的强阻断规则，不允许静默从账号A改绑到账号B。

## 追加修复：刷新失败自动重新绑定Desktop执行凭证

人工验收发现：环境状态页显示“已完成可信绑定”，但点击“刷新本机可信状态”直接失败。

根因：页面展示的“已完成可信绑定”来自Local Agent已保存的`node_id`；但刷新Cloud可信状态还需要Desktop Rust当前进程内的`node_credential`。当Tauri重新启动后，Rust内存凭证会丢失，导致页面看似已绑定，刷新动作实际无法签名上报。

修复：

- 环境状态页主按钮文案调整为“确认并刷新本机可信环境”；
- `bindTrustedLocalAgent()`在发现已有`node_id`时先尝试刷新；
- 如果刷新失败，不再直接向用户报错，而是在BitBrowser主账号已确认一致的前提下重新申请Cloud绑定票据，并调用Desktop Rust重新绑定当前执行凭证；
- 该逻辑不允许BitBrowser主账号不一致时静默改绑，主账号不一致仍会阻断并要求联系管理员处理。

## 验证

- `cargo test`：PASS，5 tests；
- `npm --prefix web test -- --run localAgentService localAgentStatus profileBindings mediaAccounts`：PASS，15 tests；
- `npm --prefix web run build:desktop`：PASS。
- 追加修复后再次执行`npm --prefix web test -- --run localAgentService localAgentStatus profileBindings mediaAccounts`：PASS，15 tests；
- 追加修复后再次执行`npm --prefix web run build:desktop`：PASS。
- 刷新失败自动重新绑定修复后执行`npm --prefix web test -- --run localAgentStatus localAgentService profileBindings mediaAccounts`：PASS，15 tests；
- 刷新失败自动重新绑定修复后执行`npm --prefix web run build:desktop`：PASS。

## 人工验收重点

1. Desktop登录并完成可信绑定；
2. 等待超过90秒；
3. 不重新绑定，直接进入浏览器窗口页面扫描/接受本地变化；
4. 预期不再因为心跳过期提示“当前电脑尚未完成可信绑定”；
5. 切换BitBrowser主账号后仍应阻断，不允许静默从账号A改绑到账号B。
6. 浏览器窗口扫描无差异时，只提示无需处理，不出现保存类按钮。

## 人工验收结果

2026-07-24 23:37 +0800，用户确认验收成功。

本轮验收覆盖：

- 环境状态页“确认并刷新本机可信环境”不再直接失败；
- Desktop重新启动后，已有`node_id`但Rust内存执行凭证缺失时，可以自动重新绑定当前Desktop执行凭证；
- 成功后页面保持“可执行本机浏览器操作”；
- 后续浏览器窗口验收可继续基于该可信环境推进。
