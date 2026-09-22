# CHG-20260914-037：M3-0 真实链接查询与云端执行链路

- Status: SUPERSEDED
- Superseded by: `delivery/milestones/M3-content-discovery-v2.md`（2026-09-15；V2 CHG-044～051 按新闭环拆分，并非一对一继承）
- 本文为历史草案，以下原任务与排除项不再拥有实施资格；未实现，不记为完成。
- Level: M
- Milestone: `delivery/milestones/M3-content-discovery.md#m3-0-真实链接查询`
- 预计影响仓库：wt-media-cloud、wt-media-agent、wt-media-workspace；Desktop 复用 Web 产物。

## 独立验收结果

有权限的运营在内容搜索页面输入真实抖音作品链接，Cloud Agent 返回可与原作品核对的详情或明确失败；关闭本地 Desktop 后云端执行仍可工作。未确认导入不创建 crawl_task、source_content 或 material。

## 前置与待决

- Q-01：供应方文档、四类接口能力、限流/计费与授权测试环境；仅文档位置，不将密钥写入 CHG。
- Q-03：用户确认或调整首批顺序。
- 技术设计需明确短期查询 TTL、云端机器身份、能力路由、结果权限与短链接解析；重用现有框架但不假定 scaffold 入口可运行。
- 正式内容共享等 Q-02/04/05/06 不由本 CHG擅自定义；如查询所需权限也受影响，先记录对应 Decision。

## 明确不做

正式素材入库、source_content/material 表、关键词/作者监控、定时调度、完整素材管理、下载/合成、重写 M2、通用任务平台扩建、绕过外部登录或访问控制。

## 顺序任务

1. 核实供应接口：详情/短链接真实样本、错误、作者与关键词能力矩阵；脱敏证据说明支持与缺失。
2. 定义最小 Cloud-owned 查询 API 和任务 payload/result/错误合同，区分技术 task 与 crawl_task；任务路由只发给 Cloud Agent，定义期限和权限。
3. 接通 Cloud Agent 常驻运行、注册/鉴权、能力过滤领取和外部适配器；查询结果回报和过期失败可追踪。
4. 实现复用 Cloud/Desktop 的链接查询页面及逐条结果；失败链接可重查，未选结果不入正式业务数据。
5. 从真实入口验收：有效作品、重复输入、无效链接、作品不可访问、接口失败、Agent 离线/恢复；证明本地 Agent 不会误领云端查询。

## 验收与 Evidence

- 确定性适配/合同/权限/任务路由测试；真实接口单独取证。
- MySQL 读回技术查询状态；未确认导入无来源/素材/抓取业务记录。
- Cloud Web 与 Desktop 页面核验；真实作品身份匹配，错误逐条呈现。
- Cloud Agent 部署后持续运行；凭据不进入前端或普通日志。
- 记录命令、预期、实际、PASS/FAIL、源码提交；不要把计划写成已完成证据。

## 提交边界

Cloud API/任务路由/Web 属 Cloud；Cloud Agent 入口/适配器属于 Agent；决策、合同索引与验收属于 Workspace。分别提交，按合同先提供方再消费者集成；真实联调通过才交付该阶段。

## Checkpoint

- Completed：定向代码审计与纵向交付拆分；确认云端入口仍为 scaffold、发现页面仍为占位。
- Current：SUPERSEDED；未激活、未实施，不能按下列旧 Next 继续执行。
- Next：仅按 V2 Milestone 与当前 planned 索引选择新 CHG。
- Blockers：外部接口资料/授权样本未核实；新权限业务决策未确认。
- Verification：仅规划检查；本 CHG 尚无运行时测试或真实接口 PASS 声明。
