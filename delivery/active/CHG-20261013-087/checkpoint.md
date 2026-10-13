# CHG-20261013-087 Checkpoint

## Completed

- 已复现缺口：我的成片仅有详情/归档/去发布；下载中心仅能对已有任务重下；清理入口不存在；按 asset_id 收敛导致跨资产类型数字 ID 冲突。
- 已确认产品 §5.9.1/§5.9.9 与里程碑 §6 要求首次下载和清理显示，Cloud 拥有任务事实及会话 API。决定采用终态任务软隐藏，不删除任务或文件。

## Current

T-01：合同、迁移和里程碑状态同步。

## Next

依 T-02～T-04 实现、真实读回、回归与收口。

## Blockers

None.

## Recent verification

- Cloud、Web 健康端点 HTTP 200；Agent 8765 进程在运行（健康端点需身份，裸请求 401）。
- Cloud、Agent、Desktop 运行仓工作树干净；Workspace 仅 `AGENTS.md` 为用户既有修改，不触碰。
