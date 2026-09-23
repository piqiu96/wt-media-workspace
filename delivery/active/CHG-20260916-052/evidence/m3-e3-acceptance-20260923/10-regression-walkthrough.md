# 阶段 10：回归与视觉走查

> 由 `tools/render-evidence.py` 从 `run-manifest.json` 渲染，每一步可回溯。
> 判定分布：ADJUDICATED=1，FAIL=1，PASS=6。

| 步骤 | 判定 | 请求 | 期望 | 实际 |
| --- | --- | --- | --- | --- |
| 10.1 | PASS | Cloud scripts/test.sh: go test ./... | 全部包通过，无 FAIL | ok 包数=57，FAIL 行=0 |
| 10.2 | PASS | Cloud scripts/test.sh: npm test --prefix web | 全部测试文件与用例通过 | files=Test Files  20 passed (20) tests=Tests  87 passed (87) |
| 10.3 | FAIL | python3 scripts/verify_m2_acceptance.py（原样） | 0 ERROR | 命中陈旧路径：ERROR: missing file: /Users/aqiuye/Develop/workspace/wt-media/wt-media-cloud/internal/modules/cloudagent/compatibility.go |
| 10.4 | PASS | python3 <仅改 compatibility.go 路径的临时副本>（用后即删） | M2 静态跨仓矩阵 ok | M2 static cross-repository acceptance matrix ok |
| 10.5 | PASS | scripts/m2b-local-acceptance.sh verify | Cloud 与 Agent 健康检查通过 | Cloud=PASS Agent=PASS（见 p10-m2-regression.log） |
| 10.6 | PASS | scripts/m2b-local-acceptance.sh verify: BitBrowser 腿 | Agent 经真实 BitBrowser 得到 bitbrowser_status=normal | 脚本对该 dev Agent 报 unreachable；原因为该 Agent 以 WT_MEDIA_BITBROWSER_API_URL=http://127.0.0.1:8899（mock，/browser/list 返回 404）启动；改用 Agent 自身代码直连真实 BitBrowser(54345) 得 profiles=40, main_user_id 非空, bitbrowser_status=normal, ffmpeg=normal |
| 10.7 | PASS | 无头 Chrome 经 cookie 注入代理(5190 -> Vite 5180)逐页截图 | 内容池 / 素材库 / 挖掘策略 / 挖掘任务 四页均可读回真实数据 | 截图=01-content-pool.png, 02-material-library.png, 03-discovery-strategies.png, 04-crawl-tasks.png |
| 10.8 | ADJUDICATED | grep 流转/业务流转/工作流视图/全景 于 Cloud internal+web/docs | 本期不交付独立只读业务流转视图（用户 2026-09-23 裁定「就当没有」） | Cloud 侧 0 命中；前端路由仅四个内容挖掘页面（content-pool / discovery-strategies / crawl-tasks / material-library）；原始记录见 raw/p10-flowview-grep.txt |

## 备注

- **10.3**：缺陷 D10：compatibility.go 已于 2026-09-18 bf499d9 迁至 service/ 子目录，脚本路径未同步
- **10.4**：用于把「脚本陈旧路径」与「M2 真实回归」两件事分开；原脚本未被修改
- **10.6**：脚本那条 FAIL 是环境前置（dev Agent 指向 mock），非 M3 回归；未重启用户正在跑的 Agent
- **10.7**：内容池 319 全部/231 待处理/87 已转素材；任务页见「部分成功」徽标与仅失败行可重试；策略页见 赞≥2.3千（AND）/ 赞≥200000万 或 藏≥1（OR）/ 关闭 三种转素材规则，以及 D2 的 schedule=garbage 被 UI 原样显示
- **10.8**：按裁定移出验收范围，基线 §6 相应改写为「本期交付功能链路而非视图」
