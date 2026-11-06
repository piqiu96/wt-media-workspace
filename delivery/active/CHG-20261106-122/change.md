---
id: CHG-20261106-122
parent: delivery/milestones/M4-content-production.md#m4-o-resource-composition-cutover
status: IMPLEMENTING
depends_on: ["CHG-20261106-121"]
dependency_merge_commits: {"CHG-20261106-121": {"wt-media-workspace": "c2713530432d3bbb068236b596e4800be6b59e07", "wt-media-cloud": "58d409e0843b05b1cec71ca6652065bcd8eabe50"}}
affected_repos: ["wt-media-workspace", "wt-media-cloud"]
risk: H
---

# CHG-20261106-122: 独立运营文件管理

## Change

1. Cloud自有运营文件API/Contract与model/repository/service：必填文件名、安全扩展名、大小/类型边界、本地暂存并计算摘要，ID分配后上传正式键，完整校验后才可见；三角色读取/修改/删除范围测试。
2. 稳定随机令牌资源路径；请求时验证文件仍存在并签发短期对象GET，下载附带附件文件名；删除先撤销访问，再清理对象，失败可重试，不增加停用功能。显示名称修改不移动对象。
3. 共用Vue页面及双端菜单：运营工具/文件管理，图片/视频筛选、必填命名上传、外部预览、下载、复制完整资源URL、改名和删除；复用common布局/反馈，不另建下载中心。
4. 真实上传/读回/三角色/改名/删除撤销验证，相关Go与前端测试及双前端构建，独立Review、按Contract/后端/前端提交合并。

## Execution details

Cloud新增`internal/modules/files/{model,repository,service}`及协议Handler，正式API归`contracts/cloud-api/v1/files.openapi.yaml`，不更改Agent契约。前端新增files页面和API客户端，两端路由指向同一组件。运营文件预览与下载交给系统浏览器（沿用Desktop已有新窗口交接），材料/成片继续原file_transfer；不建立另一套本机落盘执行器。API给出稳定resource_path，客户端使用实际Cloud地址构成URL：线上HTTPS，本机开发使用本机HTTP，任务执行在Cloud识别自己签发的有效文件令牌后直接读取已验证对象。

## Current facts

CHG121 Cloud PR33与Workspace PR36均已合并至原仓main；两个仓干净。新bucket写读与并发冲突实际PASS；历史来源待补，CHG125负责迁移。`bin/control.sh verify`开发Agent恢复后全PASS；Desktop业务流程尚待最终验收。

## Risks

大文件请求上限及临时文件清理；上传失败不能出现在正式列表；已删除链接不得重新授权；管理员无团队也能管理自己上传的文件，团队范围按上传时归属。URL令牌不可枚举，存储凭据和短期签名不作为策略持久字段。

## Done When

- [ ] 对应M4-O交付项真实结果可读回，失败行为经过验证，不借其他CHG的PASS替代。
- [ ] 修改按所有权提交，相关测试/构建通过，独立Review和PR合并后回写事实。

## References

- docs/product/prd/详细文档/第五章_素材生产.md#510-合成与资源管理增量2026-11-06-用户确认执行
- docs/decisions/0032-compose-resources-and-template-cutover.md
- docs/engineering/specs/2026-09-24-m4-m5-cloud-content-production.md

## Constraints

按用户要求在原仓库分支执行，不创建worktree；不打印/提交AK/SK。角色与业务事实仍在Cloud，Workspace不承载运行代码。按依赖完成后自行启动后续已授权任务。
