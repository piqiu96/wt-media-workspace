# M2-B 多游戏 Cloud Web（Task 8 / 计划 Task 5）

- Commands: `npm run test -- --run`; `npm run build:cloud`; `npm run build:desktop`.
- Expected: 客户端只发送 `game_ids`；创建/编辑支持完整多选和清空；列表按任一游戏筛选；页面展示完整游戏集合；两个静态构建成功。
- Actual: 10 个 Vitest 文件、40 个测试全部 PASS；Cloud 与 Desktop Vite 构建均退出 0（2026-09-04）。
- Status: PASS
- Notes: 新建表单默认不选游戏，未从 `users.game_ids` 预填；页面未读取兼容 `game_id`，仅使用正式 `game_ids`。
