# 证据 — T-20 Agent 侧脱敏（两处真泄漏 + 一处形状错 + 一处遮蔽静默关闭）

范围：§7 **Q-07** 的三处实测缺陷（T-13 的 20 行差分表在 Agent 侧量出来的）**加上 T-13 之后
新发现的第四处**。三处真泄漏/形状错直接咬里程碑 `M-launch-engineering.md` 的成功事实 #5
（「敏感信息不进日志」），故按用户裁定在本 CHG 内修掉，而不是登记为未交付。

`Blocking = NO`（不挡 T-14…T-18），但 **DONE Gate 前必须落地**——本证据即该落地。

提交边界：

| 仓 | commit | 内容 |
|---|---|---|
| `wt-media-agent` | `65725f4` | `src/wt_media_agent/runtime/logging.py`（+55/−13）、`tests/test_log_redaction.py`（+147） |
| `wt-media-desktop` | `572d1cf` | **仅注释** 14 行（`src-tauri/src/logging/redact.rs`）：模块注释与一处用例注释把这四处
记成「Agent 侧缺陷」，T-20 落地后全部变假，改成两侧一致；代码与测试一字未动（已逐行核对：过滤掉注释行后 diff 为空） |

两个 id 与「在哪个提交上量的」：

| 文件 | sha256 | 说明 |
|---|---|---|
| `runtime/logging.py`（修后） | `d82d52efaa5f63351477abf64ebd4970c365dbd61c4147e643ba3c22db8251cd` | = `65725f4`，工作树干净 |
| `runtime/logging.py`（修前） | `cb97e581b321ebc579f9132c07600159bbe55a3f8b9aa8400b5350df0b9a4229` | = `978155f:src/…/logging.py`，`/tmp/t20/red` |
| `logging/redact.rs`（参考实现） | `a3fad427b690d38659f2ad73ffd50c269d262f3d38542cb7dc6663f446fc1cf7` | = `572d1cf^`，**20 行期望串是在这个版本上量的** |
| `logging/redact.rs`（现状） | `c47e5aca8a939c557ebc960a902060e9ad551cb842eef699283e5bb2f1e9ed07` | = `572d1cf`，只改了注释 |

---

## 1. 交付形态

| 处 | 内容 | 为什么不能是别的 |
|---|---|---|
| `_TAIL_KEYED` | 值组仍是 `[^\n]*`（整行剩余），只给**整尾家族**：cookie 与 authorization | 这两族的尾巴里**自带多个凭据**（`a=1; session=xyz`；一个 scheme 词 + 一个 blob）。按词元切会切错，按行尾切才对得上语义 |
| `_VALUE_KEYED` | 值组是 `{_LEADING_VALUE}`，**匹配在此结束** | 这一条界的全部意义：`re.sub` 从整段匹配之后**续扫**，值一旦吃到行尾就会把后面的东西一并吞掉、扫描就此停住——`token=aaa password=bbb` 掩了第一个、吞了第二个、把第二个留在日志里 |
| `_mask_tail_keyed` | 只处理自己两族，其余**原样返回** | 两个回调各带族守卫 ⇒ 两趟**与顺序无关**，不必钉顺序（见 §4 的 M6） |
| `_mask_value_keyed` | 回显用**原文字前缀** `match.group(0)[:match.start(3)-match.start()]` | 模式为了够到分隔符要跨过 JSON 键的**闭引号**（`"client_secret": `），而 `key + separator` 拼回来的前缀丢那个引号 ⇒ 写出 `{"client_secret: "***"}`，该行既不是合法 JSON 也不再说明掩的是哪个字段。改成原文字前缀后 `c` 一并修掉 |
| `_is_cookie_key` | 认得 `cookie` **与** `cookies` | 词表 `SENSITIVE_KEY_NAMES` 里两个都有（都是 config loader 拒绝赋值的名字），只认单数就把复数推给通用路径，在第一个 `;` 处停住 |
| `_KEYED` / `_mask_keyed` | **删除**，无残留引用 | 换成上面两条，一个函数不再身兼两族 |

**接口零变化**：`redact(text, secrets=())` 签名不动、不新增模块、不动 `SENSITIVE_KEY_NAMES`、
`configure_from` 与 formatter 的调用点一字未改。本 Task 只改「怎么掩」，不改「在哪掩」
（T-06 已定的落点：formatter，不是 Filter——Filter 改 `record.msg` 碰不到 traceback）。

## 2. 先红：四个缺陷各自把修前的实现打红

新用例与实现同批写入，所以「先红」不能靠「测试先写」，只能靠**把模块换回修前的版本**再跑同一份用例。
在 git 对象上做，不碰工作树（`git archive HEAD` + `git show 978155f:…`）：

| 臂 | 树 | 模块 | 结果 |
|---|---|---|---|
| 控制 | `/tmp/t20/ctl`（`git archive HEAD`） | 修后 | **19 tests OK** |
| 红 | `/tmp/t20/red`（同源，只换 `logging.py`） | 修前 | **FAILED (failures=7)** |

控制臂先绿是必须的：它证明这份用例本身不红、`red` 树的红来自换掉的那一个文件。

7 个失败落在 **5 个用例**上，逐个点名（`/tmp/t20/red`）：

| 用例 | 失败数 | 量到的输出 |
|---|---|---|
| `test_every_row_matches_the_desktop_reference` | **3**（三条 subTest） | `cookies: ***; b=2`、`token=*** password=bbb`、`{"client_secret: "***", "port": 8765}` |
| `test_the_three_rows_that_used_to_differ_are_named` | 1 | `token=*** password=bbb` |
| `test_the_json_row_is_still_json` | 1 | `{"client_secret: "***", "port": 8765}` |
| `test_the_tail_families_reach_the_end_of_the_line_on_both_sides` | 1 | `cookies: ***; b=2 group_id=g-1` |
| `test_a_lookalike_key_no_longer_hides_the_credential_behind_it` | 1 | `mytoken=abcdefghijkl password=zzz`（**原样**） |

三条 subTest 命中的正是 T-13 量出的那三行（差分表第 7/13/16 行），与 T-13 的结论逐字一致。

## 3. 第四处：T-13 那张表看不见的那一行

T-13 的 20 行表把 `mytoken=` 与 `tokenizer` 单列成「两方皆 no-op」。**对那两行**是对的；
它看不见的是形似键**排在最前**时的那一行：`mytoken=` 先匹配、整段 `([^\n]*)` 吃到行尾、
`re.sub` 从行尾之后续扫 ⇒ 后面的真凭据 `password=zzz` **从未进过扫描**。
性质与 a 同源（同一处 `[^\n]*` + 同一处「非敏感键直接 `return match.group(0)`」，
`logging.py:118` 与 `:187`），但后果更重：**遮蔽被静默关掉**，而不是掩得不全。

修法是「匹配在值处结束」而**不是**「让形似键归入敏感」——后者会把 `mytoken`/`tokenizer`
这类普通英文词的值一起掩掉。这条边界在用例里是**双向写死**的：

```
redact("mytoken=abcdefghijkl password=zzz") == "mytoken=abcdefghijkl password=***"
redact("mytoken=abcdefghijkl")               == "mytoken=abcdefghijkl"      # 有意不动
```

## 4. 差分表 fixture：20 行，期望串是**量出来的**

`DIFFERENTIAL_ROWS`（`tests/test_log_redaction.py:160-190`）就是 T-13 跑过的那 20 行，
每行的期望串 = **在 Desktop 实现上测量**得到的输出，而**不是**从它的测试表里抄的。
做法：往 `redact.rs` 临时塞一个用例（`/tmp/t20/probe.rs`）逐行 `println!`，跑出 20 行，
然后 `git checkout` 还原并核对 sha256 = `a3fad427…`（见上表）。

> 抄一份期望不等于测一个实现——这正是 T-13 那轮「17 同 / 3 异」能成立的唯一理由。

断言风格也一并换了：**整行精确字符串**（照 Desktop `redact.rs:501` 的 `assert_eq!` 形），
因为既有的「两列」风格**看不见缺陷 c**——`{"client_secret: "***"}` 里 `client_secret` 还在、
`s3cr3tvalue` 不在，两列都过。形状错只有整行断言抓得住。JSON 那两行另加 `json.loads`，
**阳性对照在前**（先断言同一份输入能被 `json.loads` 解开），否则解析失败说不清是谁的错。

## 5. 变异：控制行先绿，8 个里 7 个打掉自己的用例，1 个如实 SURVIVED

控制行：工作树干净、`bash scripts/test.sh` → **371 OK**，再逐个施加、每次只改一处、跑完即还原
（`/tmp/t20_mutate.py`，驱动里先 `copyfile` 备份、每轮 `parse` 后 `copyfile` 还原）。

| # | 变异（改回/改成什么） | 结果 | 打掉的用例（点名） |
|---|---|---|---|
| M1 | 值组改回 `[^\n]*`（修前的形态） | **KILLED** | 新表 3 条 subTest + 第四处 + JSON + 三条命名 + **既有** `RedactTableTest` 7 条（`password assignment` / `json-shaped password` / `credential in a url` …） |
| M2 | `_is_cookie_key` 只认单数 | **KILLED** | 新表 `cookies:` 行、尾部族触达、三条命名 |
| M3 | 回显改回 `key + separator` | **KILLED** | JSON 行、`test_the_json_row_is_still_json`、三条命名 |
| M4 | 单值趟丢掉守卫的「非敏感」半 | **KILLED** | 第四处、新表 `mytoken=abcdefghijkl` 行 |
| M5 | 单值趟丢掉守卫的「家族」半 | **KILLED** | 新表 Cookie/Set-Cookie/`cookies` 三行、尾部族、三条命名 |
| M6 | **两趟换序** | **SURVIVED** | —（见下） |
| M7 | 整尾趟**不跑** | **KILLED** | 新表 5 行 + 既有 `RedactTableTest` 3 条 + `test_every_configured_sensitive_key_name_is_covered` 6 条 subTest |
| M8 | cookie 尾只吃一个前导词元 | **KILLED** | 新表 3 行 + 既有 `cookie with several pairs` / `set-cookie header` |

**M6（换序）如实 SURVIVED，而这个幸存者本身就是证据**：它证明的是「两趟与顺序无关」——
两个回调各带族守卫（`_mask_tail_keyed` 对非自己两族原样返回、`_mask_value_keyed` 对 cookie/opaque
原样返回），所以先跑哪趟都一样。**没有**为它补一条「钉顺序」的用例：那会把一条**有意成立的
性质**写死成实现细节，下一轮想并成一趟时反而被挡住。

M1 特意去动用**既有**用例（T-06 的 15 行两列表）而不是只靠新写的：修前的形态本来就该被
老用例打掉——它没被打掉，正说明老用例的覆盖面止于「一个键一个值」。

## 6. 真机臂：两条臂，同五个请求，一个真实进程各跑一次

脚手架（`/tmp/t20/real_arm.sh`，两条臂共用，只有 `WS`/`ARM` 两个环境变量不同）：

- 仓库副本 `/tmp/t20/ws`（修后，sha256 `d82d52ef…` 与 `65725f4` 逐字相同）/ `/tmp/t20/red`（修前，`cb97e581…`）；
- `PYTHONPATH=<副本>/src` ⇒ `repository_root()` 解析到副本，**不碰真实检出**；
- scratch 端口 `18769`；BitBrowser 指向 **死端口** `18790`、Cloud 指向死端口 `18791`；
- `WT_MEDIA_LOG_FILE` / `WT_MEDIA_AGENT_DATA_DIR` 指向 `/tmp` 下的 scratch 目录；token 是 scratch 值；
- 五个 `POST /api/v1/bit-browser/profile-create`（`.start` 记录写在依赖调用**之前**，
  所以 502 照样把 payload 落盘），body 逐条写进 `requests.out` 供对照；
- 全程**未碰** `:8765` / `:18080` / `:54345`；跑完 `lsof -nP -iTCP:18769 -sTCP:LISTEN` 为空。

响应：`502 Bad Gateway` × 5（两个死端口各自拒绝连接，符合预期）。

**修后的 `agent.log`（逐字，10 条记录）**：

```
2026-09-24T18:54:27 [INFO] wt_media_agent.local_api.server: wt-media-agent local API listening on 127.0.0.1:18769
2026-09-24T18:54:40 [INFO] wt_media_agent.local_api.server: local_api.profile_create.start name=token=*** password=*** group_id=g-1
2026-09-24T18:54:40 [WARNING] wt_media_agent.local_api.server: local_api.profile_create.failure name=token=*** password=*** group_id=g-1 duration_ms=11 error=BitBrowser Local API request failed: <urlopen error [Errno 61] Connection refused>
2026-09-24T18:54:40 [INFO] wt_media_agent.local_api.server: local_api.profile_create.start name=cookies: a=***; b=***
2026-09-24T18:54:40 [WARNING] wt_media_agent.local_api.server: local_api.profile_create.failure name=cookies: a=***; b=***
2026-09-24T18:54:40 [INFO] wt_media_agent.local_api.server: local_api.profile_create.start name={"client_secret": "***"} group_id=g-1
2026-09-24T18:54:40 [WARNING] wt_media_agent.local_api.server: local_api.profile_create.failure name={"client_secret": "***"} group_id=g-1 duration_ms=0 error=BitBrowser Local API request failed: <urlopen error [Errno 61] Connection refused>
2026-09-24T18:54:40 [INFO] wt_media_agent.local_api.server: local_api.profile_create.start name=mytoken=abcdefghijkl password=*** group_id=g-1
2026-09-24T18:54:40 [WARNING] wt_media_agent.local_api.server: local_api.profile_create.failure name=mytoken=abcdefghijkl password=*** group_id=g-1 duration_ms=0 error=BitBrowser Local API request failed: <urlopen error [Errno 61] Connection refused>
2026-09-24T18:54:40 [INFO] wt_media_agent.local_api.server: local_api.profile_create.start name=plain-name-with-no-secret group_id=g-1
2026-09-24T18:54:40 [WARNING] wt_media_agent.local_api.server: local_api.profile_create.failure name=plain-name-with-no-secret group_id=g-1 duration_ms=0 error=BitBrowser Local API request failed: <urlopen error [Errno 61] Connection refused>
```

**修前的同一条臂（逐字，只列 `.start` 五条）**——这就是「泄漏真的落到了盘上」：

```
… start name=token=*** password=bbb group_id=g-1
… start name=cookies: ***; b=2 group_id=g-1
… start name={"client_secret: "***"} group_id=g-1
… start name=mytoken=abcdefghijkl password=zzz group_id=g-1
… start name=plain-name-with-no-secret group_id=g-1
```

### 6.1 断言与**每一条的分母和阳性对照**

断言脚本 `/tmp/t20/assert_arm.py`。脚本第一版把 6 个「必须不在」的针**共用一个对照**（修前日志），
**当场报出 3 条 `CONTROL INVALID`**：`aaa`、`a=1`、`s3cr3tvalue` 在修前日志里**也是 0**——
这三个值（第一个 cookie 值、token 值、JSON 值）本来就掩着，缺陷在**形状**与**第二个值**上，
不在它们身上。处置：把针分成两组，各自配**能失败的对照**。

| 针 | 修后 `agent.log` | 对照 | 判定 |
|---|---|---|---|
| `bbb`（第二个凭据的值） | 0 | payload **1** / 修前日志 **2** | PASS |
| `b=2`（复数 cookies 的第二个值） | 0 | payload **1** / 修前日志 **2** | PASS |
| `password=zzz`（形似键后面那个） | 0 | payload **1** / 修前日志 **2** | PASS |
| `aaa`（第一个值，两侧都掩） | 0 | payload **1**（修前日志 = 0，**故不作对照**） | PASS |
| `a=1`（同上） | 0 | payload **1**（同上） | PASS |
| `s3cr3tvalue`（形状错，值从未漏） | 0 | payload **1**（同上） | PASS |

「必须仍在」的一列（分母 = 10 条记录）：`name=` **10**、`local_api.profile_create.start` **5**、
`…failure` **5**、`error=BitBrowser Local API request failed` **4**、`duration_ms=` **4**、
`plain-name-with-no-secret` **2**、`mytoken=abcdefghijkl` **2**。

结论行：**ALL ASSERTIONS PASS**（脚本 exit 0）。`plain-name-with-no-secret` 那两条是**阴性对照臂**：
一个不带任何敏感形态的值**原样通过**，证明掩码不是「见什么都掩」。

## 7. 如实登记的代价：整尾家族的触达是行尾

真机臂量到一处**新事实**，如实登记：`group_id=g-1`（每次请求都带）在修后日志里出现
**8 次 / 10 条记录**——缺的 2 条正是 `cookies:` 那两条。原因是整尾家族按设计吃到行尾，
`cookies:` 之后的 `group_id=g-1` 与 cookie 头同处一行，于是被一并掩掉，
输出 `name=cookies: a=***; b=***`（**连 `group_id` 一起不见了**）。

三件事逐条钉住，确保这不是我这边新引入的分歧：

1. **两侧一致，实测**：同样三行（`cookies:` / `Cookie:` / `Authorization:` + 尾随 `group_id=g-1`）
   跑 Desktop 的 `masked()`，返回与 Agent **逐字相同**的三个串；
2. **修前也一样**：修前的输出是 `cookies: ***; b=2 group_id=g-1`——**带**着 `group_id`，
   但那是因为它连 `; b=2` 都没掩到；触达范围这一点修前修后并未改变，改变的是掩得全不全；
3. **有用例钉住这条界**（`test_the_tail_families_reach_the_end_of_the_line_on_both_sides`），
   且它的 docstring 写明代价；**没有**顺手把某一侧的答案改成有界触达——那是对一个**两侧早已
   一致回答过**的问题单方面改答案，不属于本 Task。

## 8. 读数与未覆盖项（如实登记，不静默吸收）

**测试**：`bash scripts/test.sh` **365 → 371 OK**（+6 = 新类 6 个用例）。**只增不减**。
`tests/test_log_redaction.py` 19 个用例（原 13）。本仓无 build/clippy 类读数。

**工作树**：`wt-media-agent` 干净（`git status --porcelain` 空），模块 sha256 与 `65725f4` 一致；
`wt-media-desktop` 干净，`572d1cf` 只动注释。

**两处自查**（本 CHG 里「检查自己先坏了 / 对照不成立」的又一例，与 T-09 的探针解析器、T-19 的两处对照缺陷同形）：
① 真机断言脚本的共用对照（§6.1，当场报 3 条 `CONTROL INVALID` 而不是静默放过）；
② M6 起初被我自己当成「少了一个变异」，复核后确认为**有意成立**的性质，改为登记而非补用例。

未覆盖 / 需要下一个人知道的：

- **`error.log` / `task.log` 两条臂未在本 Task 重跑**：T-06 已证「落盘后读回文件」这条路，
  本 Task 的四个缺陷都在**同一个 formatter 路径**上（`agent.log` 与另两文件共用 `redact`），
  故未重复三文件臂——**但 T-04/T-06 的三文件臂是在修前的模块上跑的**，其结论
  「三文件路由正确」不受影响（路由未改），「文件里的凭据不在」那部分则由本 Task 的
  `agent.log` 臂 + 单测表覆盖。**若要三文件逐条重跑，本 Task 未做。**
- **`SENSITIVE_KEY_NAMES` × {`=`, `:`} 的覆盖**由既有 `test_every_configured_sensitive_key_name_is_covered`
  承担（M7 能打掉它），本 Task 未重写这条用例。
- **形似键的边界是「匹配在值处结束」，不是「形似键归敏感」**：`mytoken=` 自身的值仍原样保留。
  这是有意保留的边界（见 §3），不是漏修。
- **Windows 日志布局仍属未测**（T-11 起的同一登记）。
- `redact.rs` 里**仍然成立**的那条差异（键前边界 Desktop 按 ASCII、Agent 的 `\b` 按 Unicode，
  紧贴非 ASCII 字符的键 Agent 侧会漏）**本 Task 未改**——`572d1cf` 的注释已经把它按实测口径写明，
  改它要动 `_KEY` 的边界定义，超出 Q-07 的范围。

## 9. 复现命令

```bash
# 1. 单测（模块级，含差分表 20 行）
cd wt-media-agent && bash scripts/test.sh                            # 371 OK（起点 365）

# 2. 先红：同一份用例打在修前的模块上（git 对象上做，不碰工作树）
mkdir -p /tmp/t20/red && cd /path/to/wt-media-agent && git archive HEAD | tar -x -C /tmp/t20/red
git show 978155f:src/wt_media_agent/runtime/logging.py > /tmp/t20/red/src/wt_media_agent/runtime/logging.py
cd /tmp/t20/red && PYTHONPATH=src:tests python3 -m unittest tests.test_log_redaction   # FAILED (failures=7)
# 对照：同源但不换模块 ⇒ 19 tests OK

# 3. 变异（控制行先绿；逐次改一处、跑完即还原）
python3 /tmp/t20_mutate.py            # M1-M5/M7/M8 KILLED；M6 SURVIVED（有意）

# 4. 真机两臂（scratch 端口，两个死端口，跑完 lsof 为空）
bash /tmp/t20/real_arm.sh                                  # 修后：/tmp/t20/real2
WS=/tmp/t20/red ARM=/tmp/t20/real_prefix bash /tmp/t20/real_arm.sh   # 修前：/tmp/t20/real_prefix
python3 /tmp/t20/assert_arm.py                             # ALL ASSERTIONS PASS

# 5. Desktop 参考实现的 20 行期望串（测量，不是抄表）
#    往 src-tauri/src/logging/redact.rs 临时加 /tmp/t20/probe.rs 的用例，跑：
cargo test --bin wt-media-desktop-shell t20_reference_probe -- --nocapture | grep '^PROBE'
#    然后 git checkout 还原并核对 sha256 = a3fad427b690d38659f2ad73ffd50c269d262f3d38542cb7dc6663f446fc1cf7
cd wt-media-desktop && cargo test --workspace               # 175 passed（未增；本 Task 未动 desktop 代码）
```
