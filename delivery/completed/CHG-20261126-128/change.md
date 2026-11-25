---
id: CHG-20261126-128
parent: delivery/milestones/M7-batch-publishing.md#逐页一致性复核
status: DONE
depends_on: ["CHG-20261125-113"]
dependency_merge_commits: {"CHG-20261125-113":{"wt-media-cloud":"69e865c03e5c90c4c9107ee2faf2323e3f753e8a","wt-media-workspace":"96a8bbed29b1e023b1bfba3c23a0e3fb84930bc0"}}
affected_repos: ["wt-media-cloud", "wt-media-workspace"]
merge_commits: {"wt-media-cloud":"eb1355ec1c202eedd4e9cf58d64402ef70d77f08"}
risk: M
---

# CHG-20261126-128：计划批次逐页对齐与异常走查

## Change

按2026-11-26用户“设计＋规划”要求，对计划和批次逐页建立原型—正式页面—业务事实映射，修复状态、按钮、布局、导航和异常反馈。继承107保存零任务/零占用、108启动原子建单、109冻结/10%推进、112单向步骤和113详情修复，不重做业务流程。先收敛原型旧样例，再固定可复核输入；接口不足沿现框架补齐，不为普通视觉差异反复让用户裁定。

2026-11-26用户确认按128→129→130执行。详细设计、已观察问题、页级清单与9步实施见[plan.md](plan.md)。前置113合入已核对：Cloud69e865c0、Workspace96a8bbed；实施前重新核对main及本轮其他会话原型修改。

## Done When

- [x] 列表、创建/编辑/续编、三步批次、两类详情、计划Drawer/快捷入口及确认弹层逐项对照固定原型并留证。
- [x] 三角色、七类批次状态、计划推进门槛、未知/读取失败/冲突/恢复等矩阵通过；没有将演示状态当业务事实。
- [x] 编码与针对性自测完成后运行生产路由E2E，最后实际打开浏览器及新安装版逐页走查；问题修复并回归。
- [x] PR/CI、合并各仓main与交付归档完成；用户最终整体签收另行。
