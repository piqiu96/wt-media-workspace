# T-07 证据：升级不覆盖

CHG-20260923-059 T-07（`change.md` §8）／AC-07，兼 §6 D-07（路径判据）与 D-24（本任务交付的是判据）。
原始转录见本目录 `task-07-*.out`。

判据（T-07 行）：**用路径判据证明升级路径不写用户设置 / SQLite / 检查点 / 待回传结果**（「按路径而非名字」）。

---

## 1. 这条任务证的是什么，以及为什么交付物是判据

T-07 的命题是**否定命题**：*升级不写用户数据*。而本 CHG **不实现升级器**（§5 Explicitly Not Doing；
`updater/`（`src-tauri/src/updater/mod.rs`）与 `filesystem/`（`src-tauri/src/filesystem/mod.rs`）
仍各是一行声明的空壳，没有任何东西调用它们）。否定命题加上不存在的动作 ⇒ 能交付的只有**判据**：
一份「升级可以写哪些路径」的声明、一份对其它一切路径的拒绝、以及钉住这两者的臂。**一个没有调用方的守卫**
在这里等于一个 `dead_code` 警告加一句没人执行的声明；一个被测试钉住的判据才是「对不存在的动作证否定」
的诚实形态。将来升级器被写出来时，它要调的就是这个模块，而这些臂是它第一个版本必须保持绿的。

**两侧各自的「升级面」不是同一件事**，这一点决定了臂的形态：

| 侧 | 真正的升级面 | 为什么 |
|---|---|---|
| Agent | **`storage/migration.py` 的迁移**：新版本跑在旧版本写的库上 | 这个仓今天真的会做的事就是它：`apply_migrations` 对既有库应用新增迁移 |
| Desktop | **它自己的数据根**（`AppPaths` 的四个根，`app_paths::resolve`） | Desktop 没有迁移动作；它的升级写入面是「将来那个升级器会往哪儿写」 |

`config_online/agent.toml` 那类**出货配置文件**不在这条命题的范围内：它们随包、只读、由安装替换，
不是「用户数据」；用户数据是**运行期在数据根里长出来的东西**。

## 2. 交付物

### Desktop：`src-tauri/src/upgrade.rs`（新增，`#[cfg(test)]` 模块）

- `refuse(target, paths, agent_data) -> Result<(), Refusal>`：唯一的判定。
- `inside(target, root) = target.starts_with(root)`：**按路径分量**比较，这是判据的全部要害。
- `desktop_write_sites(paths) -> [PathBuf; 2]`：Desktop 侧只声明**两个**写入点——
  `settings::path(&paths.data)`（设置文件的唯一写者 `commands::settings` 也这样解析它）与
  `paths.versions`（`app_paths::Root::Versions`，按构造在数据根之内）。数据根下其它一切**都是用户数据**：
  架构基线 §6.8 列的就是剩下的那些（Agent 的 SQLite、文件索引、检查点、待回传结果、运行期文件）。
- `agent_data_root(home)`：Agent 的数据根（`~/Library/Application Support/WTMedia/Agent`），
  与 `logging::paths::agent_directory` 解析日志树是同一个 `WTMedia/<Component>` 形状、同一层父目录。
  Desktop 侧对它的唯一用途就是知道**不要写哪里**。
- `Class::{DesktopUserData, AgentData}` 与 `Refusal { class, path, because }`：拒绝报文只带
  路径与类别，**不带任何内容**（与 `settings`、`config` 的同一条规矩）。
- 声明处：`src-tauri/src/main.rs` 的 `#[cfg(test)] mod upgrade;`——**故意是 test-only 模块**，
  理由写在模块头（没有调用方，就不假装有）。

**九条臂**（`upgrade::tests`）：`the_declared_sites_are_writable`（**阳性对照**：两个写入点必须可写，
否则「拒绝一切」也会让下面每条通过）、`an_unrecognised_file_under_the_data_root_is_refused`、
`a_directory_under_the_data_root_is_refused`、`the_agent_root_is_refused_whatever_the_file_is_called`、
`a_sibling_with_a_shared_prefix_is_not_inside`、`the_two_roots_are_siblings_with_disjoint_sites`、
`allows_a_path_outside_both_roots`、`the_development_layout_gets_the_same_rule`、
`the_sites_are_the_roots_owner_declaration`。

### Agent：`tests/test_upgrade_preserves_data.py`（新增，4 条臂）

- `test_the_database_is_the_declared_path_under_the_data_directory`：`default_db_path` 就是
  数据目录自己那条规则（配置层），不是第二个算出来的路径。
- `test_a_new_migration_leaves_existing_rows_alone`：**加性**——运行期插一条 `0003_additive_probe`
  迁移（`finally` 还原 `migration.MIGRATIONS`），升级后 `agent_metadata` / `task_checkpoints` /
  `offline_results` 三张表逐行未变，且 `applied` **只**含新迁移。
- `test_the_upgrade_writes_the_database_and_no_other_path`：**路径判据**——操作员留下的
  `operator-notes.txt` 与 `versions/0.2.2/payload.bin` 逐字节未变、无新路径；
  并且**以「这个用例动手之前的目录」为基准**再量一次（见 §4.2，这一条不是冗余）。
- `test_the_console_script_an_installer_runs_is_the_same_operation`：`migration.main(["--db-path", …])`
  ——安装脚本 `migrate-storage.sh` 走的那个入口——是同一个操作：exit 0、行还在、旁边没有新路径、
  报出它动的是哪个文件。第二个入口若与 `apply_migrations` 不一致，就是一条没有任何用例走过的升级路。

**Agent 侧没有改动任何实现文件**（`git status` 只有新增的测试文件）：迁移本来就是加性的、本来也只写一个路径。
所以这一侧的「红」不可能来自实现，只能来自变异——见 §4。

## 3. 先红读数

### 3.1 Desktop：判据写成名字清单（`task-07-desktop-red.out`）

首轮把 `refuse` 写成**名字清单**（`settings.toml` / `local-agent.sqlite3` 命中就拒，其余放行）：

```
test result: FAILED. 3 passed; 6 failed; 0 ignored; 0 measured; 368 filtered out
failures:
    upgrade::tests::a_directory_under_the_data_root_is_refused
    upgrade::tests::a_sibling_with_a_shared_prefix_is_not_inside
    upgrade::tests::an_unrecognised_file_under_the_data_root_is_refused
    upgrade::tests::the_agent_root_is_refused_whatever_the_file_is_called
    upgrade::tests::the_declared_sites_are_writable
    upgrade::tests::the_development_layout_gets_the_same_rule
```

**这六条正是「名字 vs 路径」的判别力所在**，也是 AC-07「按路径而非名字」这句话的读数：
一个操作员改名过的文件（`notes.db`）、一个目录（`checkpoints/task-1.json`）、
一个**归另一侧所有**的位置（Agent 根下无论叫什么）、一个带点的兄弟目录（`versions-backup`）、
以及检出布局下的同一问句——名字清单要么漏掉，要么连自己该放行的写入点也拒掉
（`the_declared_sites_are_writable` 首轮就是红的：清单按名字拒了 `<data>/settings.toml` 本身）。

### 3.2 一处臂的判据被实测改掉

`a_sibling_with_a_shared_prefix_is_not_inside` 首版把 `<WTMedia>/Desktop-backup` 断言成**必须被拒**。
实测它是错的：那个路径**在两个根之外**，本判据不声称它、也就不拒绝它（与 `allows_a_path_outside_both_roots`
是同一条作用域线）。**危险的方向是写入点的兄弟**：字符串前缀会让 `<data>/versions-backup/payload.bin`
读成「在 payload 区里面」⇒ 升级把它写到区**旁边**，那里没人会去找、也没人会清。臂已按这个方向重写：
拒绝 `<data>/versions-backup/payload.bin`（`Class::DesktopUserData`），放行两个**根**的兄弟。
变异 M2（把 `inside` 改成字符串前缀）就是它的守卫，实测只打掉这一条臂。

### 3.3 Agent：**没有实现级的先红，如实登记**

今天的迁移已经是加性的（`CREATE TABLE IF NOT EXISTS`）且已经只写一个路径 ⇒ 首轮用例是**绿的**。
按本 CHG 的规矩，这种情况下「绿」不构成证据，**证据是变异表**：能打掉这四条臂的实现变异见 §4.2。
这不是为绿开脱——`error: no such file` 式的红什么都不证明，而「已经在做正确的事」的代码也没有可红的实现。
两条都如实写，不拿一条去冒充另一条。

## 4. 变异表

两侧的驱动都在 `/tmp/chg059/`（`t07-mutate.py`、`t07-mutate-agent.py`），每次变异后**从原始字节还原**并
**用 sha256 校验还原成功**，任何一条「打不掉任何用例」或「还原失败」都让整轮失败。

原始 sha256（还原判据）：desktop `src-tauri/src/upgrade.rs`
`6ab1fc90abaad170c1d1af25b868f8f1ca1aba4231c74d27050292b9699989af`；
agent `src/wt_media_agent/storage/migration.py`
`248307e7bd8f826488f84899fca74f6093adb59f2642b827197103128a4499ec`。

### 4.1 Desktop：**9 条变异 / 9 条打中 / 0 未证**（`task-07-desktop-mutations.out`）

| # | 变异 | 打掉的臂 |
|---|---|---|
| M1 | 判据退回**名字清单**（把包含式判定的整个函数体按原始字节切出来换成首轮那一版） | 6 条（含两个写入点的阳性对照） |
| M2 | `inside` 改成**字符串前缀** | `a_sibling_with_a_shared_prefix_is_not_inside` |
| M3 | Agent 根**完全不拒** | `the_agent_root_is_refused_whatever_the_file_is_called` |
| M4 | Desktop 分支**接受数据根下的一切** | 4 条 |
| M5 | payload 区被声明成 **cache 根** | `the_declared_sites_are_writable`、`the_sites_are_the_roots_owner_declaration` |
| M6 | Agent 的拒绝**报成 Desktop 的类别** | `the_agent_root_is_refused_whatever_the_file_is_called` |
| M7 | 写入点**连自己的子路径也拒**（只允许精确相等） | `the_declared_sites_are_writable`、`the_development_layout_gets_the_same_rule` |
| M8 | Agent 根被建成**Desktop 自己的目录**（组件常量抄错） | 5 条（含 `the_two_roots_are_siblings_with_disjoint_sites`） |
| M9 | Desktop 分支**忘了自己只在数据根内生效** | `a_sibling_with_a_shared_prefix_is_not_inside`、`allows_a_path_outside_both_roots` |

**第一轮是 7 条，有两条臂没有任何变异能打掉**：`the_two_roots_are_siblings_with_disjoint_sites` 与
`allows_a_path_outside_both_roots`。这不是记分问题而是**判据上的洞**：M3 关掉的是「拒绝」，
而这两条臂量的是常量之间的关系（两个根是兄弟、写入点不在 Agent 根内）与判据的**作用域**
（两个根之外不拒）。谁都到不了它们 ⇒ 补 M8（改 `agent_data_root` 的组件常量，让两个根重合）
与 M9（去掉数据根这一个合取项，让判据拒掉包内暂存的 `agent.toml`）。**九条臂现在逐条有主**
（`the_agent_root_…` 由 M3/M6，`the_two_roots_…` 由 M8，`allows_a_path_outside_both_roots` 由 M9，
其余见上表）。

### 4.2 Agent：**6 条变异 / 6 条打中 / 0 未证**（`task-07-agent-mutations.out`）

| # | 变异 | 打掉的臂 |
|---|---|---|
| M1 | 已应用的迁移**再应用一遍** | 加性臂 + 控制台入口臂 + 路径臂 |
| M2 | 升级在库**旁边留一份安全副本**（`<db>.bak`） | 控制台入口臂 + 路径臂 |
| M3 | 声明的库名**不是**实际用的那个（`agent.sqlite3`） | 声明路径臂 + 路径臂 |
| M4 | 升级在数据目录里**暂存一份 payload**（`upgrade-staging/`） | 路径臂 |
| M5 | 升级**从一个空库开始**（先 `unlink`） | 加性臂 + 控制台入口臂 + 路径臂 |
| M6 | 升级**清掉它以为是过期的待回传结果**（`DELETE FROM offline_results WHERE delivered = 0`） | **加性臂**（正好一条） |

M6 就是里程碑失败行为「升级或清理删除业务数据」的形态：它只打掉加性臂，报文是
`offline_results lost rows`，即**按表逐行比对**抓到的，不是靠「有没有异常」。

**两处过程订正（都不静默）**：

1. **M4 首轮「打不掉任何用例」，根因是臂有一个真盲点。** 首版把 `upgrade-staging/` 建在
   `apply_migrations` 里，本该被路径臂看到。它没被看到的原因是：**那条臂自己的 planting 步骤先调了一次
   `apply_migrations`**，于是「每次 apply 都会产生的路径」在 before 快照里**已经有了**。
   ⇒ 该臂原来只量得到**第二次** apply 的写入集（也就是升级那一次），第一次（安装那一次）的写入集无人看。
   修法不是改断言也不是换变异，而是**补一个比较**：以「这个用例动手之前的目录」为基准，
   `after - empty - planted` 必须**恰好**等于 `{DEFAULT_DB_NAME}`。补完后 M4 打掉路径臂。
   （这条也写进了测试文件的 docstring，免得后来者以为那两个比较有一个是多余的。）
2. **M6 首轮红在错误的原因上。** 它最初被锚在迁移循环**之前**，于是新库上表还不存在，
   四条臂是被 `sqlite3.OperationalError: no such table: offline_results` 打红的——**一个异常不是那条
   被禁止的写入**。锚点移到循环之后（表已建、planting 时表为空 ⇒ 无副作用），现在它只打掉加性臂，
   报文是丢行而不是报错。这一版的首轮读数留在 `task-07-agent-mutations.out` 之外的过程记录里，
   与 T-06 的「两条 needle 会被另一条拒绝路径满足」同类：**红的理由必须与被证的那条性质同源**。

## 5. 套件读数（计数只增不减）

| 仓 | 命令 | 起点（§4.8） | T-06 后 | 本次 | 增量 |
|---|---|---|---|---|---|
| `wt-media-desktop` | `cargo test --workspace` | 336 | 363 | **372 passed / 0 failed / 5 ignored** | **+9**（正好九条臂） |
| `wt-media-agent` | `bash scripts/test.sh` | 377 | 397 | **401 OK**（`Ran 401 tests ... OK`，0 failures / 0 errors） | **+4**（正好四条臂） |

编译警告 **7 → 7**：`mod upgrade` 是 `#[cfg(test)]`，所以它不引入 `dead_code`——
这正是当初选 test-only 形态的理由之一（T-04 起的基线是 7 条，含 `Updater` / `FileSystemBridge` /
`SecureStore` / `SystemBridge` 未构造）。转录：`task-07-desktop-green.out`（含
`test result: ok. 372 passed; 0 failed; 5 ignored`）、`task-07-agent-green.out`（四条臂的逐条 OK）、
`task-07-agent-suite.out`（全仓 `Ran 401 tests in 14.590s / OK`）。

## 6. 结论与未覆盖项

- **AC-07 满足（判据那一半，按 D-24）**：升级写入面被一条**路径**判据声明与拒绝，
  两侧各有先红（desktop 的名字清单首轮 / agent 的变异）与逐条有主的臂（desktop 9 条臂 / 9 条变异，
  agent 4 条臂 / 6 条变异），且两侧套件计数只增不减。
- **如实登记：这条命题的**动作**仍不存在。** 本任务证的是判据与臂，不是「某次升级跑过。
  AC-07 的判据行写的就是「路径判据的用例（先红）」——这一条已满足；不要把它读成
  「升级器已被验证」。
- **作用域**：`allows_a_path_outside_both_roots` 明确把两个根之外的路径排除在本判据之外
  （要暂存的产物、cache 树、日志树都不是用户数据）。**检出布局下 Agent 的数据根不在 crate 之内**，
  故 `the_development_layout_gets_the_same_rule` 只量 Desktop 自己那一半——这条限制写在臂里。
- **Agent 侧那一半的边界**：用户设置、检查点、待回传结果在这个仓里**是库里的表**（不是库旁的文件），
  所以它们由加性臂（逐行比对）覆盖，而「库旁的一切」由路径臂覆盖。两侧看起来不对称，
  是因为两侧承载数据的方式本来就不同。
