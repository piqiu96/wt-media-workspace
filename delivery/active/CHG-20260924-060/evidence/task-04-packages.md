# evidence — T-04 删 `modes/` 与 `generated/` 占位包

- CHG: CHG-20260924-060
- Task: T-04
- Date: 2026-09-24
- Type: test + command
- Status: PASS
- Commit: `wt-media-agent` — **`c33680f`**

## Purpose

D-03：`modes/` 与 `generated/` 占位包与架构基线 §5.2「不保留」冲突，裁定**删**。

## 一、删之前先证「该删」与「删得掉」

**该删 —— 基线原文（逐字，`docs/engineering/architecture/社媒运营平台工程架构与分层设计_V1.md:1040`）：**

> 不保留 `modes/`、`core/`、`communication/`、`runtimes/`、`platforms/`、`generated/`，
> 也不保留根级 `patches/`、`packaging/`。目录职责、依赖方向与配置目录约定的完整定义见 ADR-0016。

该列表**含** `modes/` 与 `generated/`，**不含** `adapters/`（已全文核对）。故删除是让**代码满足基线**，
**基线无需回写**——这是本次一个需要论证的结论，理由就是这一行：基线早已明写不保留，是目录一直没删。

> 检索订正：本 CHG 计划把该行记作「架构基线 §5.2 `:1040`」，**行号准确**。
> 但首轮 `grep docs/engineering/*.md` 无命中，因为该文件在 `docs/engineering/architecture/` 子目录、
> 非递归 glob 扫不到——**是检索方式的问题，不是基线的问题**。记在这里以免后人重踩。

**ADR-0016 不改，理由两条（均核对原文）：**

- 其 **Decision 从未点名这三个占位包**：第 4 条只撤销 `runtimes/`（`:31`），第 5 条只撤销 §5.5 的
  `platforms/`（`:32`）。
- `Context:15` 提到 `adapters/`、`modes/`、`generated/` 是**决策时的状态快照**（「均只有一行 docstring」）。
  改写 ADR 的 Context 等于改写历史，不做。

**一个被检查并排除的疑点**：基线 `:1298` 也出现 `generated/`，看似自相矛盾。实为
`wt-media-desktop/src/generated/`（**Desktop 仓**的前端目录，`:1296-1299` 的树），
与 Agent 的 `wt_media_agent/generated/` 无关。**不是矛盾。**

**删得掉 —— 删之前实测零引用**（先证再删，不留悬空导入）：

```
$ grep -rn --include='*.py' --include='*.toml' ... -e 'wt_media_agent\.modes' -e 'wt_media_agent\.generated' \
    -e 'from modes' -e 'import modes' -e 'from generated' -e 'import generated' .
（零命中，exit=1）
```

内容也核过：三个包各只有一行 docstring 的 `__init__.py`——
`adapters`「Platform adapters…」、`modes`「Agent mode selection…」、
`generated`「Generated contract types. Do not edit generated files by hand.」

## 二、先失败

```
$ rm -rf src/wt_media_agent/modes src/wt_media_agent/generated
$ bash scripts/test.sh
```

**恰好两条红，一条一个包**（原文 `artifacts/t04-r1-red-after-delete.out`）：

```
FAIL: test_r1_every_module_is_in_a_known_place (...)
AssertionError: Lists differ: ['R1 wt_media_agent/generated/ must stay a[81 chars] []'] != []
+ []
- ['R1 wt_media_agent/generated/ must stay a placeholder, found []',
-  'R1 wt_media_agent/modes/ must stay a placeholder, found []']
Ran 253 tests in 2.967s
FAILED (failures=1)
```

`Ran 253` 说明被删的两个包**零测试**（计数不变，见第四节）。这条红也是 R1 规则的**阳性对照**：
它证明「占位包存在」这件事真的被检查着，而不是一条永远为真的断言。

## 三、最小实现

`tests/test_dependency_boundaries.py:80` 收紧常量，并改写其上两行注释：

```diff
-#: Declared empty. `adapters/` emptied when M3 dropped discovery, `platforms/`
-#: was revoked by ADR-0016 §5 and has never existed; all three are placeholders.
-PLACEHOLDER_PACKAGES = frozenset({"adapters", "modes", "generated"})
+#: Declared empty. `adapters/` was emptied when M3 dropped discovery and is the
+#: only one left: `modes/` and `generated/` no longer exist — the architecture
+#: baseline §5.2 never kept either of them, so the directories were the side that
+#: was out of step; `platforms/` was revoked by ADR-0016 §5 and has never existed.
+PLACEHOLDER_PACKAGES = frozenset({"adapters"})
```

注释必须同批改：原文的「all three are placeholders」与 `modes`/`generated` 的并列措辞
在目录消失后就成了假话。

**未动**：`R2` 白名单、`FROZEN_LAYER_EDGES`、`KNOWN_LAYERS`、`FROZEN_DEFINITIONS`、
`URL_LITERAL_LAYERS`、`ROOT_MODULES` —— 这三个包从不出现在其中（已核）。
`R1` 里 `head not in PLACEHOLDER_PACKAGES` 那一支也无需改：它检查的是**存在**的文件，
而这两个目录下已无文件。

## 四、验证

```
$ bash scripts/test.sh
Ran 253 tests in 3.001s
OK
```

`artifacts/t04-green-after-const-update.out`。**253 → 253**，计数不变——被删的是两个零测试的包。

**副作用（已量，非推断）**：`test_the_scan_sees_the_whole_package`（`:613`）的
`len(self.files)` **由 65 降到 63**，对 `assertGreaterEqual(len(self.files), 60)` 的**余量由 5 缩到 3**。

```
$ find src/wt_media_agent -name '*.py' -not -path '*__pycache__*' | wc -l
      63
```

余量仍为正、测试仍绿，故不调该阈值；但余量变小是**真实的收窄**，登记在此，
以免后人在此基础上继续删包时才发现。该测试的第一条断言
（`assertEqual(len(self.files), len(list(SOURCE_ROOT.rglob("*.py"))))`）仍成立，
说明扫描覆盖面未因子目录消失而漏扫。

## 五、未做（有理由）

- **`adapters/` 保留**：基线 §5.2 的名单里没有它（逐字核对）；且 R1 的对照测试正是拿 `adapters`
  当宿主，删它会连带废掉一个对照。基线未撤销它 ⇒ 不在本 CHG 的裁定范围内。
- **文档回写不在本 Task**：`DIRECTORY_MAP.md:98/102/104/117`、`AGENTS.md:27/36`、
  `CLAUDE.md:9`、`AGENT-INDEX.md:64` 现在指向已不存在的路径。它们归 **T-05**（按计划的分工）。
  **代价如实登记**：在本 Task 提交到 T-05 提交之间，agent 仓存在少量悬空文档引用。
  这是计划选择的两提交切分（结构改动 vs 文档），不是遗漏。
  （另核：`.claude/skills/` 与 `.codex/skills/` 里的 `generated` 命中指的是 Desktop 的
  `http-*.js` chunk，**不是**本次删的包，无需改。）
- **workspace 侧无悬空指针**：全仓检索 `wt_media_agent/modes`、`wt_media_agent/generated`，
  命中仅在本 CHG 自己的 `change.md:97/98/159`（正确地描述删除动作本身），无需修。
