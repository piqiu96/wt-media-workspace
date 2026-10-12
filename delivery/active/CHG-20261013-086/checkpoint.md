# CHG-20261013-086 Checkpoint

## Completed

- CHG 记录已建立（本文件与 `change.md`）。CHG-20261013-085（M4-C7）已于同日归档（四门全绿：Go exit 0 / Agent 705 OK / web 536 全绿 / governance exit 0）。
- T-01 环境基线与素材盘点完成（`evidence/T-01.md`）：server=4a3bee6、迁移至 054、agent-node_b27e0f251ffb07c2ae9a5da4 信任成立、三会话就绪、盘点 171/32/1/2/0/35；改动面核对——production 模块新增全在 compose 面（082～085 自有证据），素材四态与 usage SQL 零改动（061 机器读数可引用），web 素材页被 082/083 改过（UI 腿归用户签收）。

## Current

T-02 素材库与 my-materials 机器读数（AC-01/02/03/04）：四态视频状态、usage 创建/去重/移出/恢复、懒加载对照、任务快照不变。

## Next

T-03 合成链真实复测（AC-05/06/07）：重建 compose-worker、真实 FFmpeg 合成、取消/失败/Worker 重启无双执行抽测。

## Blockers

None.

## Recent verification

- T-01 全部读数见 `evidence/T-01.md`（health errcode 0、迁移 054、节点信任四条件、盘点 171/32/1/2/0/35、改动面 git log/diff 0 backend commits）。
