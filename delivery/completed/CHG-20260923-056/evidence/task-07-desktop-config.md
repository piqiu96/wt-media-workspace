# Evidence: Desktop Config 链路 + sidecar 传参 + get_public_config（T-07）

- CHG: `CHG-20260923-056`
- Task: `T-07`
- Date: 2026-09-24
- Type: refactor + test + mutation + command + manual
- Status: PASS（含 1 处已登记缺口、1 处计划偏差）

## Purpose

T-07 让 Desktop 从「把部署事实写死在源码里」变成「从配置读」：Cloud 地址、Agent
回环端口、HTTP 超时、CSP 全部来自 `resources/desktop.production.toml`；per-launch token
取代「本地 API 无凭据」；sidecar 首次拿到受控参数；页面第一次能问出自己的配置。

三类判据：

1. **字面量真的消失**，且消失后**同一策略仍在生效**（不是「删掉即通过」）。
2. **新的规则有棘轮**：删掉的字面量若回来、漏掉的字段若被发布，都要能失败。
3. **token 从「可有可无」变成「强制」是行为变更**，其证据必须是**两个方向**的
   （带对 200 / 不带与带错 401），而不是只看到 200。

## Method

### 1. 提交序列（7 个 commit，`wt-media-desktop`）

| # | commit | 内容 |
|---|---|---|
| A | `1276e98` | `token.rs`：`RuntimeToken`（`Uuid::new_v4()`，无 `Debug`/`Display`/`Serialize`） |
| B1 | `b4d4dc4` | `paths.rs`：生产布局不再理会 `WT_MEDIA_DESKTOP_CONFIG` |
| B2 | `2afe1d9` | `bootstrap.rs`：配置定位/载入 + CSP 注入时机 + 编译内置兜底 |
| C | `d838ccd` | `http/`：两个 client 接配置（超时来自 TOML）；`LocalAgentClient` 持有 token |
| E | `14ff67c` | `tauri.conf.json` 的 CSP 字面量退役，改由配置注入；留下棘轮 + 金标 |
| F | `6f94cbb` | 第 18 个命令 `get_public_config`，只返回三个非敏感字段 |
| D | `35a2ee9` | sidecar 与 Python fallback 注入同一组四个环境变量，token 成为强制 |

逐 commit 实测（`/tmp/t07_matrix.sh`，每个 commit 后**强制重编**再量）：

    commit   | tests | bin warnings
    4b3a7b4  |  42   |  27     <- T-06 收尾基线
    1276e98  |  45   |  29
    b4d4dc4  |  46   |  29
    2afe1d9  |  52   |   7
    d838ccd  |  55   |   6
    14ff67c  |  56   |   6
    6f94cbb  |  59   |   6
    35a2ee9  |  63   |   4

**测试数单调不降**（42 → 63）。**告警先升后降**：A/B1 新增类型时尚无消费者，故 +2
（`RuntimeToken` 从未构造）；B2 一次降到 7，因为 `paths`/`config` 的产物首次被生产代码
使用；D 降到 4。**剩下的 4 条是 `filesystem/`、`secure_store/`、`system/`、`updater/`
四个空壳**——CHG-056 §5 明确「本 CHG 不动」，故 T-07 的告警收口到此为止，不虚报为 0。

### 2. 变异矩阵（四组，全部当场跑，非事后补记）

| 组 | 工具 | 结果 |
|---|---|---|
| CSP 棘轮 + 金标 | `/tmp/csp-mutants.py` | **6/6 杀，0 存活，0 无效** |
| `get_public_config` | `/tmp/public-config-mutants.py` | **6/6 杀，0 存活，0 无效** |
| `cloudBaseUrl` + 边界 | `/tmp/cloudbaseurl-mutants.py` | **5/5 杀，0 存活，0 无效**（属 T-08） |
| sidecar 环境变量 | `/tmp/sidecar-env-mutants.py` | **5/7 杀，2 存活（预期内，见 §6）** |

每组都先跑**未变异的阳性对照**，且每个变异体的锚点必须**恰好命中一次**，否则硬停。

CSP 组明细：

    M-01 conf 塞回 csp 字面量（死的）      -> tauri_conf_carries_no_policy_of_its_own  CAUGHT
    M-02 conf 塞回 devCsp 字面量（会赢的） -> 同上                                  CAUGHT
    M-03 apply_csp 两个字段都写            -> apply_csp_writes_the_field_...          CAUGHT
    M-04 apply_csp 只写 dev_csp            -> 同上                                  CAUGHT
    M-05 policy 丢掉 img-src               -> the_policy_is_shape_for_shape_...      CAUGHT
    M-06 policy 调换指令顺序               -> 同上                                  CAUGHT

`get_public_config` 组明细：

    M-01 多发布一个 agent_data_dir 字段    -> 键集棘轮        CAUGHT
    M-02 port 恒为 8765                    -> 取值来自配置    CAUGHT
    M-03 environment 恒为 development      -> 取值来自配置    CAUGHT
    M-04 cloud_base_url 恒为回环字面量     -> 取值来自配置    CAUGHT
    M-05 port 读另一个配置字段             -> 取值来自配置    CAUGHT
    M-06 port 在线上改名 agentPort         -> 键集棘轮        CAUGHT

sidecar 组明细：

    M-01 不传 token                        -> the_agent_is_told_...      CAUGHT
    M-02 data_dir 未设时传空串             -> an_unset_data_dir_...      CAUGHT
    M-03 host 与 port 对调                 -> the_agent_is_told_...      CAUGHT
    M-04 生成新 token 而非 client 自己的   -> the_token_the_agent_...    CAUGHT
    M-05 把 --token 加进命令行             -> the_fallback_command_...   CAUGHT
    M-06 fallback 路径不注入环境           -> 无                        SURVIVED（见 §6）
    M-07 sidecar 路径不注入环境            -> 无                        SURVIVED（见 §6）

### 3. 真实副作用验证（D 的前提，`evidence/tools/ac03-token-check.sh`、`evidence/tools/ac03-datadir-check.sh`；原跑于 `/tmp/`）

D 的整个论证建立在「这四个变量名就是 Agent 认的那四个」之上。名字漂了不是编译错误，而是
一个静默 401 或一个没人调用的端口，**故不靠读源码断言，直接启动一次**：

    PYTHONPATH=src WT_MEDIA_LOCAL_API_HOST=127.0.0.1 WT_MEDIA_LOCAL_API_PORT=18766 \
      WT_MEDIA_AGENT_RUNTIME_TOKEN="$TOK" WT_MEDIA_AGENT_DATA_DIR="$SCRATCH" \
      .venv/bin/python -m wt_media_agent.local_api.server

## Expected

- Agent 监听 `127.0.0.1:18766`（**不是**默认 8765）⇒ HOST/PORT 被采纳。
- `/healthz` 带对 token **200**；不带 **401**；带错 token **401** ⇒ token 被采纳且强制。
- `$SCRATCH` 下出现 `local-agent.sqlite3`、`logs/`、`versions/`，仓库 `.local/` **不被触碰**
  ⇒ DATA_DIR 被采纳且 override 优先。

## Actual

```
listening port       : 127.0.0.1:18766
healthz WITH token   : 200 body={"status":"ok","service":"wt-media-agent","mode":"m1"}
healthz WITHOUT token: 401 body={"error":"unauthorized"}
healthz WRONG token  : 401 body={"error":"unauthorized"}
```

```
scratch dir set to : /tmp/wt-agent-dd-9RRk
tree under it:
<scratch>
<scratch>/local-agent.sqlite3
<scratch>/logs
<scratch>/versions

repo .local/ touched (should be NOTHING):
(空)
```

三个状态码齐备，其中包括**错误 token 得 401**——没有它，「不带 token 得 401」也可能只是
「压根没开鉴权、而 healthz 恰好要求别的什么」。四次启动均在断言后自行停止，实测确认
**0 个残留监听**，未触碰用户既有的 :8765 dev Agent。

**一处自查纠正**：第一版脚本断言 `$SCRATCH/data` 存在，报 `exists=no`。查下去是**脚本
的问题**：`RuntimePaths.resolve` 的 override 分支把 `<override>` **本身**当 data_dir
（`runtime/paths.py:64-71`），只有 dev/installed 分支才在下面拼 `data/`。改正后如上。

## Follow-Up

### 1.（已登记）M-06/M-07 存活：「两条 spawn 路径都注入」无单元测试覆盖

`tauri_plugin_shell::Command` 需要 `AppHandle` 才能构造，故「两条路径都拿到同一组变量」
这一**结构性**性质在 `cargo test` 里看不到。代码侧的对策是只有**一处** `with_vars`
绑定、两条路径各用一次，说明就写在紧邻处。运行期补位在 **T-09**：真实启动 sidecar 走
bundled 路径，dev 流走 Python fallback 路径。**不写成「已覆盖」**。

### 2.（已登记）`generate_handler!` 的注册本身测试看不到

`get_public_config` 若写了却忘了注册，`cargo test` 一律绿，只有运行期会以「命令不存在」
暴露。由 **T-09** 的真实启动闭合（前端会真的调用它）。

### 3.（已登记）`connect_timeout` 未单独验证（M-06 of C）

`reqwest` 不把已建成 `Client` 的超时读回来，`build_client` 的
`a_request_to_a_silent_server_gives_up_instead_of_waiting_forever` 只能证明
**请求超时**生效；`connect_timeout` 单独失效需要黑洞地址，CI 上不稳定。**不虚报**。

### 4. 与计划的偏差（1 处）

计划写「CSP 改为运行时经 `ctx.config_mut()` 注入」，其中 `ctx` 指对了但**注入点写浅了**。
实测 Tauri 源码：`AppManager` 持有 config 的**拷贝**（`manager/mod.rs:39`），
`Manager::csp()` 从那份拷贝读（`:369-380`）；`App` 没有 `config_mut`；`.setup()` 更晚，
在**配置文件声明的窗口全部建好之后**（`app.rs:2524` 然后 `:2531`）。故唯一可行注入点是
`Builder::run` 之前对 `Context` 施加，调用链已逐行写进 `bootstrap.rs` 头部与该 commit。

### 5. `tauri.conf.json` 的 CSP 移除后仍受保护

退役的是「文件里那条字面量」，不是「策略本身」：
`tauri_conf_carries_no_policy_of_its_own`（棘轮，禁 `csp` 与 `devCsp` 回归）+
`the_policy_is_shape_for_shape_the_literal_it_replaced`（金标，逐字钉住原字面量）+
`apply_csp_writes_the_field_a_dev_build_would_otherwise_prefer_over`（钉住 `dev_csp`
保持 `None`）。三者合起来使「注入的策略就是策略，dev 与 production 都是」成立。

**后续 T-09 仍有一步未做**：AC-01/AC-03 的完整三模式启动与 AC-09 的 Desktop 真实启动，
以及两向 CSP 端到端检查（故意写错的 `csp_connect_src` 必须产生前端 CSP 违规，改对后
不得再有）。
