# CHG-111 验证记录

日期：2026-10-30。范围：Cloud 共用前端，按现有原型与规范纠偏；不改数据库、接口、Agent 或 Desktop Runtime。

## 自动验证

- `npm --prefix web test`：103 文件、892 测试 PASS。包括公共字段真实 Vue 模板的 v-model 联动、禁用/加载属性、分类切换清空、标签回车去重与移除。
- Cloud / Desktop 前端生产构建 PASS。
- Workspace `python3 -m unittest discover -s tests`：179 测试 PASS。
- Delivery governance / Product master alignment PASS。

## 安装包走查

首轮安装包 `0.1.0+0e70baf`：全量 `bin/control.sh start` 通过所有启动门槛；运营测试账号进入真实列表。未选隐藏批量入口，选中 1 项后显示工具栏；实际百度账号检查成功，公共结果弹窗显示总数 1 / 成功 1。新增表单的分类勾选、切换一级及回车标签行为正常，未保存新账号；960px 批量抽屉完整显示并保持底部动作。

首轮视觉复查另发现分类表单尚需左右排布、长 UID 换行和弹窗外部默认留白问题，已进入本 CHG 最终修正；最终安装包截图与走查结果补充于下方。原始两个登录窗口未被改写。
