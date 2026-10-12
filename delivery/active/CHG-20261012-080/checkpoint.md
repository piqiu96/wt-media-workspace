# CHG-20261012-080 Checkpoint

## Completed

- CHG 记录已建立：范围、任务、验收标准经用户裁定（本机存储验收、`basic_cut` v1 仅切段）。
- 前置事实已核对：本机 FFmpeg/FFprobe 8.1.2 可用；真实测试视频在 `wt-media-download/20261008/`（21MB 起三条）；对象存储 endpoint 为 Garage `s3.oss.longyanyue.cn`，凭据文件待用户重新发到 `config/credentials/object_storage.toml`（git-ignored）。

## Current

尚未开始 T-01；Cloud 仓工作树干净（`3535f86`）。

## Next

T-01：FFmpeg 工具环境检查（配置 + 先红测试）。

## Blockers

- 对象存储凭据待用户放入本机 `wt-media-cloud/config/credentials/object_storage.toml`（T-05/T-06 真实验收前到位即可；T-01～T-04 不需要）。

## Recent verification

- `verify_delivery_governance.py` / `verify_product_master_alignment.py` 将在激活后重跑。
