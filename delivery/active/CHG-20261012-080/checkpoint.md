# CHG-20261012-080 Checkpoint

## Completed

- T-01：FFmpeg/FFprobe 配置与启动校验；部署测试夹具补齐新增变量（Cloud commit `058d411`），证据见 `evidence/T-01.md`。
- T-02：模板版本注册表和 `basic_cut` v1 固定参数，证据见 `evidence/T-02.md`。
- T-03：隔离运行目录、输入/输出 FFprobe 校验、固定切段执行；异常输入、执行失败和输出时长异常均失败。Cloud commit `5e28c51`，证据见 `evidence/T-03.md`。
- T-04：跨进程单任务锁与独立 `cmd/compose-worker`；缺凭据或工具时启动检查失败。Cloud commit `f179d6e`，证据见 `evidence/T-04.md`。
- T-05：临时键上传、Stat、签名 GET 读回 SHA256、清理；模拟未配置、上传失败和读回不一致。Cloud commits `67bfd65`、`869120c`，证据见 `evidence/T-05.md`。
- T-06 已完成部分：真实测试视频本机切段得到 7.007 秒 H.264/AAC MP4；Cloud `go test ./... -count=1`、Web 507 项测试和 `build:cloud` 通过。尚未完成真实 Garage 读写。

## Current

等待对象存储凭据后执行 T-06 完整链路；CHG 保持 `IMPLEMENTING`，不报告真实存储验收成功。

## Next

确认 `wt-media-cloud/config/credentials/object_storage.toml` 已放置后，以本机“三角洲-2”视频运行 `compose-worker`；核对签名 GET 哈希、临时键清理、异常对照，再补齐 T-06 证据并收口 CHG。

## Blockers

- 本机 `wt-media-cloud/config/credentials/object_storage.toml` 尚不存在。真实 Garage 验收必须使用用户提供的凭据；不可用模拟存储代替。

## Recent verification

- `go test ./... -count=1`：全部包通过。
- `npm test -- --run`：55 个文件、507 项测试通过。
- `npm run build:cloud`：通过；Vite 报已有的大 chunk 提示。
- 本机 FFmpeg/FFprobe：真实 67.754 秒、21,358,859 字节输入切为 7.007 秒、3,619,554 字节 H.264/AAC MP4。
