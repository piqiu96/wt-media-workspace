# Evidence: AST 边界测试与平台 URL 常量化（T-05）

- CHG: `CHG-20260923-056`
- Task: `T-05`
- Date: 2026-09-23
- Type: test + refactor + mutation + command
- Status: PASS

## Purpose

T-05 把 ADR-0016 §3 的「依赖规则机器校验」从条款变成可执行断言，并顺手清掉
`executors/` 里最后的外部访问痕迹。三类判据：

1. **边界可机器校验**：R1–R10 十条规则，每条都有对应的「故意写坏的源码」控制组，
   故「规则没报错」不等于「规则不会报错」。
2. **patch 面可机器校验**：凡测试 patch 的名字必须绑定在被 patch 模块自己的
   命名空间里——这是 `mock.patch("a.b.c")` 唯一依赖的源码形状。
3. **executors 里没有 URL 字面量、没有私有方法直达、没有 client 构造**：
   AC-02 的机器判据（grep 与 AST 双证据）。

## Method

### 1. 提交序列

`wt-media-agent`，`main`，基线 `7e19622`（T-04 收尾）→ `87cde92`，共 **3** 个 commit：

| # | commit | 内容 | 测试 |
|---|---|---|---|
| 1 | `a4a43cc` | 平台 URL 迁入 `clients/platform_urls.py`；`BitBrowserClient.open_url()` 公开；executor 不再调 `_post` | 214 OK |
| 2 | `d00147b` | `tests/test_dependency_boundaries.py`（R1–R10 + 13 个控制组） | 243 OK |
| 3 | `87cde92` | `tests/test_patch_targets.py`（发现 + 解析 + 绑定规则 + 3 个控制组） | 249 OK |

> 注：第 2 个 commit 的原始 hash 为 `87f8bf4`，因订正 commit message 里的文件数
> （写 64，实测 65）而 amend 为 `d00147b`，**内容未变**。

逐 commit 测试矩阵（`git archive` 导出后各自实跑）：

| commit | 结果 |
|---|---|
| `a4a43cc` | `Ran 214 tests` / `OK` |
| `d00147b` | `Ran 243 tests` / `OK` |
| `87cde92` | `Ran 249 tests` / `OK` |

单调不减，基线 214 ≥ T-04 收尾的 204。

### 2. 冻结项逐字节未动

```
7e19622  888113caaf5bb970   ← T-04 收尾
a4a43cc  888113caaf5bb970
d00147b  888113caaf5bb970
87cde92  888113caaf5bb970
```

本 CHG 范围（`99f408c^..87cde92`）内 `git log -- tests/test_runner_session.py` 计数 **0**。

### 3. 边界规则表与它们的控制组

`tests/test_dependency_boundaries.py`。每条规则是纯函数 `{相对路径: 源码} -> 违规列表`，
`BoundaryRuleControls` 把同一批函数跑在改坏的源码上。

| 规则 | 内容 | 控制组 |
|---|---|---|
| R1 | 每个模块落在已知层/占位包/根模块；三个占位包必须仍为空 | 植入 `runtimes/bitbrowser.py`；给 `adapters/__init__.py` 加代码 |
| R2 | 只允许 ADR-0016 §1 的下降方向 | 绝对导入；**相对导入**；例外收窄（见下） |
| R3 | ADR-0016 §3 的三条明禁边单独成一规则 | `clients→executors`；`utils→clients` |
| R4 | `executors/**` 不得 import `sqlite3/subprocess/socket/http/urllib/requests/ctypes/os` | 植入 `import sqlite3` |
| R5 | executors 不构造 client、不 import `runtime.config`、不调别的层私有方法；client 构造点只许在自己的包与 `bootstrap/app.py` | 自建 `BitBrowserClient`；调 `bitbrowser._post` |
| R6 | 环境变量只许 `runtime/config.py` | `os.environ`；**`from os import getenv`** |
| R7 | `src/` 字符串常量不得出现 `config_online`（docstring 豁免） | 植入 `ONLINE = "config_online"` |
| R8 | 冻结路径/符号/console script/构建脚本入口 | 把 `server.main` 改名；改一个 console script |
| R9 | `executors/**` 与 `local_api/**` 不得出现 URL 字面量 | 植入 `HOME = "https://…"` |
| R10 | 层对层边集快照（棘轮） | 植入 `storage→clients` |

三个特别值得记的控制组：

- **R2 的相对导入**：`from ...executors import noop` 与绝对导入同义。只跟绝对名的扫描器
  会放过它。控制组确认相对导入被正确解析。
- **R2 的例外收窄**（D-06）：两组控制证明「另一个 `runtime/` 模块碰 `clients` 会失败」
  与「`runtime/environment.py` 碰别的 client 包会失败」。没有这两条，把例外从单文件
  放宽到整层，看起来会和现在的冻结态**一模一样**。
- **R6 的别名导入**：`from os import getenv` 正是为躲开 `os.getenv` 这类 grep 而会
  被写出来的形式。控制组确认它被抓住。

分母断言（防止「扫了个空」被当成通过）：`test_the_scan_sees_the_whole_package` 断言
扫描到的文件数等于 `rglob("*.py")` 实测数（**65**）、≥60、且层集合逐个包含九个已知层。

### 4. 失败验证：规则在 T-05 之前的树上转红

把 `test_dependency_boundaries.py` 放到 `a4a43cc~1`（即 `7e19622`）的源码树上跑：

```
Ran 29 tests ... FAILED (failures=2)
FAIL: test_r5_executors_have_no_construction_config_or_private_seams
FAIL: test_r9_no_url_literals_in_executors_or_the_control_plane
```

报出的违规正是 `a4a43cc` 修掉的那六处：

```
R5 wt_media_agent/executors/account_check.py:65: calls BitBrowserClient._post outside clients/bitbrowser/
R5 wt_media_agent/executors/account_check.py:80: calls BitBrowserClient._post outside clients/bitbrowser/
R9 wt_media_agent/executors/account_check.py:29: URL literal 'https://www.douyin.com/'
R9 wt_media_agent/executors/account_check.py:30: URL literal 'https://www.bilibili.com/'
R9 wt_media_agent/executors/account_check.py:31: URL literal 'https://baijiahao.baidu.com/'
R9 wt_media_agent/executors/account_check.py:82: URL literal 'http://detect.ocsp.intra'
```

在 `a4a43cc` 的树上全绿。所以 R5/R9 的绿不是「规则没说话」。

### 5. 变异对照（`a4a43cc` 的代码改动）

`/tmp/t05mut.py`（与 T-04 同一形状：基线先绿 / 植入 / 还原三步俱全，锚点必须唯一匹配）：

| # | 变异 | 命中 |
|---|---|---|
| M-1 | `open_url(profile_id, navigate_url)` 改回 `_post("/browser/open-url", …)` | 3 失败 1 错误 |
| M-2 | 探针 URL 换成别的地址 | 2 失败 |
| M-3 | `login_url(platform)` 挪进 `try` 内 | 4 失败 1 错误 |
| M-4 | `LOGIN_URLS["bilibili"]` 主机名打错 | 1 失败 |
| M-5 | 未知平台改为返回 douyin 而非抛出 | 2 失败 |
| M-6 | `open_url` 改用 `_post_with_timeout`（不同超时） | 1 失败 |

结果 **6/6 全部可判别**。两处**我自己的脚本缺陷**已修正并披露：

- M-2 初版把常量替换成**它自己的字面量**（等值替换），报「未判别」——那不是测试有洞，
  是那条变异根本不构成变异。改用不同 URL 后转红。
- M-5 的锚点缩进写错（12 空格 vs 实际 8），报 ANCHOR MISMATCH 而非静默跳过——
  这正是锚点唯一匹配这条硬规则在起作用。

### 6. patch 目标检查的失败验证

`/tmp/t05patch.py`：把 `local_api/server.py` 改成经模块别名访问的形态
（`from wt_media_agent.services.net import proxy as proxy_check` +
`proxy_check.check_proxy_connectivity(...)`），两处替换各断言锚点唯一匹配。

| 目标 | 基线 | 变异 | 还原 |
|---|---|---|---|
| `test_patch_targets.py` | 6 tests OK | **FAILED (failures=3)** | OK |
| `test_proxy_check.py`（既有） | 2 tests OK | **FAILED (errors=1)** | OK |

三条规则同时点名 `check_proxy_connectivity`：`test_every_patch_target_resolves`、
`test_every_patched_name_is_bound_in_the_module_it_is_patched_on`、
`test_the_frozen_patch_targets_still_resolve`。**既有的** `test_proxy_check.py` 也报错，
这正是文件顶部那句「它替我们盯住这三个冻结目标」的实测依据。

`test_patch_targets.py` 初版的控制组写错了前提：断言
`import X as name` 不绑定 `name`，实测相反（它也绑定）。判定为**我的控制组有洞而非规则有洞**，
已改为模拟真实会失败的形态（`from X import net` 后 `net.proxy.x()`），并据实收窄了
文件顶部对规则的表述——机器判据取的是「名字是否被绑定」这更弱的一半，因为
`import X as name` 无法被调用、实际不出现。

### 7. AC-02 的双证据（grep + AST）

grep（`executors/` 与 `local_api/` 下的 client 构造、私有 `_post`、环境变量读取）：

```
当前树（HEAD）      分母 1109 行 -> 命中 0
对照（7e19622 树）  分母 1120 行 -> 命中 2
  executors/account_check.py:65: self.bitbrowser._post("/browser/open-url", {
  executors/account_check.py:80: self.bitbrowser._post("/browser/open-url", {
```

AST：R4/R5 两条规则在 `test_dependency_boundaries.py` 里常驻，其控制组已在上表。

### 8. 静态扫描（含阳性对照）

- **死 import**：AST 扫描 `src/` 65 个文件 → **0 条**；阳性对照植入的
  `import json` 被报出。**我的第一版扫描器自身有误**：它把每个文件的
  `from __future__ import annotations` 都报成未使用（45 条），排除 `__future__` 后归零。
  那是扫描器缺陷，不是源码问题——记录在此以免后来者复现同一个假阳性。
- **冻结脚本**：`migrate-storage.sh --data-dir` ×2 → `2 applied` 后 `0 applied`；
  `verify-health.sh` → `health ok`。

### 9. 新增测试文件的两处形状修正

- `test_account_check_executor.py`（8 例）用**只暴露公开面**的假 client：它没有 `_post`，
  故「又伸手调私有方法」会在此失败而不是静默可用。另有 3 例钉住 URL 表自身的契约
  （三个平台 id、https 主机名、未知平台抛出），因为导航测试读的是同一张表，
  单靠它挡不住表里的错别字。
- `test_bitbrowser_runtime.py` 新增 2 例覆盖 `open_url` 的路径、载荷键与所用超时——
  该方法是新的公开面，除它之外没有任何测试能碰到（M-1/M-6 证明这两条确实在守）。

## Expected

- R1–R10 全绿，且每条都有控制组证明它**能**红；
- patch 目标可解析，且绑定规则能在别名重构下转红；
- `executors/` 与 `local_api/` 无 URL 字面量、无 client 构造、无私有直达；
- 测试数 ≥ 214 且 OK；冻结文件逐字节未改。

## Actual

全部达成。需要如实记录的有：

### 9.1 未覆盖面（枚举，不以「测试通过」代替）

- **R10 只到层对层**：同层内换一个模块不触发（`clients/foo.py → runtime` 变成
  `clients/bar.py → runtime` 照样绿）。这是计划指定的粒度。
- **`from pkg import mod` 只记成 `pkg`**：R2 因此对该形态保守（报父层，可能误报为
  例外越界），但不会失明。真实树用的是 `from pkg.mod import X` 窄形态，有专门断言钉住。
- **R9 看不见运行期拼出来的 URL**（`"".join(...)`），也管不到 `runtime/constants.py`
  里的三个配置默认地址（`DEFAULT_CLOUD_BASE_URL`、`DEFAULT_BITBROWSER_API_URL`）——
  它们是配置默认值而非业务目的地，R9 的范围按计划只覆盖 `executors/**` 与 `local_api/**`。
- **R5 的「私有方法」判据按名字前缀 + 接收者**，看不见 `getattr(client, "_post")` 这类动态取用。
- **`patch.object`/`patch.dict` 不解析**：前者首个实参是对象而非字符串，后者的字符串
  实参指的是要更新的 dict 而非可调用对象。
- **`clients/` 内的硬编码值**（如 `PAGE_SIZE = 100`、CDP 的 `timeout=10`）不在任何规则内，
  计划亦未要求。

### 9.2 一处与计划的偏差

计划 T-05 写「`executors/account_check.py:31-33` 的 `PLATFORM_URLS` 与 `:84` 的内部探针
URL 移入 `clients/**`」。实测：

- `PLATFORM_URLS` 在 `:28-32`（不是 `:31-33`），探针 URL 在 `:82`（不是 `:84`）——计划行号偏移。
- 计划未指定落在 `clients/` 的哪儿。实际新建 `clients/platform_urls.py`（与既有的
  `clients/platform_identity.py` 同层同风格的扁平模块），探针常量 `PROXY_PROBE_URL`
  放进 `clients/bitbrowser/client.py`（它是 BitBrowser 面向的操作细节，不是平台目的地）。

### 9.3 顺手订正的一处既存矛盾

`clients/bitbrowser/__init__.py` 的 docstring 同时写着「`clients/` 之外不得构造
`BitBrowserClient`」与「它在 bootstrap 构造一次」——两句不可能同真（T-03 遗留①）。
改为准确表述：每进程只构造一次，在 `bootstrap/app.py`，经本包的 `bitbrowser_from_config`；
「唯一装配点」而非「clients 之外禁止构造」。R5 的构造点规则就是这句话的机器形式。

## Follow-Up

- **T-09 的 AC-02 证据已具备**：§7 的 grep 双证据 + R4/R5 常驻规则。
- **T-09 的 AC-10 仍需 `WT_MEDIA_AGENT_RUN_RUNNER=true`**，T-05 未触及。
- **`adapters/`、`modes/`、`generated/` 三个占位包**现在被 R1 钉住必须为空——若
  CHG-B/C 要用它们，需同时更新 R1 的白名单（这是有意的摩擦）。
- **`local_api/server.py:340` 的 `check_items` 契约分歧**仍未动（计划细节 11）。
