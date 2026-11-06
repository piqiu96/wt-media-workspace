# 自动切片库验证

- 新 Cloud CLI prepare/publish/verify，复用既有抖音客户端、来源下载、ffprobe和不可变存储；配置/线上模板包含片长、候选/单源/下载预算和编码。migration099实际应用，累计101项。Cloud运行不依赖Workspace，发布构建/包已包含slice-video工具。
- 初始定向测试失败（工具尚不存在），实现后PASS；独立Review发现prepare采样范围未绑定publish配置，新增回归测试先失败，再保存候选profile/reviewed_seconds并限制发布和恢复范围，测试PASS。发布另以实际视频/音轨时长验证，不能以长音轨撑大短视频。
- `go test ./...`最终PASS；Python发布包/前端标记4项PASS。首次误选测试目录0tests不计证据，改用现有正式测试入口；新增二进制后修正包测试fixture并验证真实包成员包含工具。
- Skill源skills/cloud/build-slice-video：Skill Creator验证PASS，Workspace Skill和分发校验PASS。只读基线测试识别新增数与库总数、逐项失败/重复、预算和实际读回规则；前向测试发现游标推进未写明，已明确失败和重复也推进，发布后立即核对实际新增。
- 实际抖音搜索“动漫舞蹈 配乐”并抓取源7657390032668762218，54.266667秒、1920×1080、带音轨；完整解码、采样图/音频生成完成。模型根据前12秒舞蹈画面与音轨事实判可用，未声称已听音频。短标题“动漫舞蹈DNA律动”，按原声连续切片；首轮实际上传2片，发布索引成功。最终版重新prepare固定12秒审核范围，同源重试后索引仍为2片，未重命名或重复上传；最终独立全库verify已PASS，两条对象完整读回，与最终版list索引完全相同。
- 并发实际验证：首进程上传持有专用DB连接库锁时，另一独立CLI发布立即明确拒绝“slice library is being updated”，未覆盖索引。
- 不适合分支单测：匹配的否定判断只删除本地候选、不访问存储；错误摘要拒绝；审核范围扩大拒绝；切片尾数舍弃/每源预算PASS。

- 两个实际片段的video/audio各自均6.000000秒。索引对象：动漫舞蹈DNA律动_1.mp4（0秒起，5,357,422 bytes，SHA256 80add9328c189c7dac0f36a83f39f18cd233ff1a5c31d5a4193f5f376d0de038）；_2.mp4（6秒起，4,846,677 bytes，SHA256 cacd2f29a2b8e927da3a845327ed45bee6cbbadaef74f116998783577d4678c2），均位于wt-media/file-ku/随机视频切片/。
- 真实DB TestLiveNamingAndLock PASS：两个独立连接不能同占锁，不同源同名自动改名，同源重试保留原名，不同摘要拒绝；测试行已按专用ID清理。首次测试未指定Cloud根，加载配置失败；已按测试位置显式设置Home后重跑PASS。
- 最终追加路径不再每次下载全库；新对象仍在PutImmutable内完整读回。list读取index投影，verify --source只审核本轮新增源，显式全库verify仍保留。实际最终版publish/list成功，索引仍两条；代码无对象覆盖，只有index投影按锁重建。
- 190项Workspace测试最终PASS（初次Skill把生成二进制写成文件引用触发路径检查，改为明确的发布环境命令后通过）；Skill/分发/文档/Delivery/Product/AI/config检查PASS。

- Cloud PR35最终CI verify PASS（3m18s）。独立全库verify日志末行为verified 2 library clips，最终版同源publish/list仍两条且索引逐项相同。后续只按新源verify，避免正常批量追加退化为反复下载全库。

- Cloud PR35已merge到原仓main：9ddfacab5d62802dadd8dfd27d4d55ea271a8593。本轮本地候选目录（原片/采样/裁剪输出）已清理；源摘要、判断和运行报告保留，正式两条切片与索引未删除。
