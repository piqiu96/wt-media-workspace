---
id: CHG-20261118-101
parent: delivery/milestones/M6-single-publishing.md#单任务从内容准备到真实作品
status: DONE
depends_on: []
affected_repos: ["wt-media-workspace", "wt-media-cloud", "wt-media-agent", "wt-media-desktop"]
risk: H
merge_commits: {"wt-media-workspace": "447b6c56e792841ff14f2e4cbe54af471eff3bcf", "wt-media-cloud": "df5cb11da6ed2a451786e5a90598669846f463b7", "wt-media-agent": "2a3a372cfc975c8f19d1851035b1bceca8a3f638", "wt-media-desktop": "61010d61adba51b2c311aacfb989d30944e7799d"}
---

# CHG-20261118-101：M6 既有发布代码集中合入与收口

## Change

按2026-11-20用户最新指令，集中提交、独立Review并合入Workspace、Cloud、Agent、Desktop现有本地代码，关闭本CHG。交付边界为已有百度单任务发布基线与走查修复：正式成片占用投影、账号只读摘要和现场入口、页面历史与预览、开发入口隔离、不可变分片上传、发现错误处理、百度封面内容校验和安全草稿替换、原结果补报、Desktop精确媒体来源。

图片库、封面模板及真实渲染、单条AI、续编、成片缩略图、完整状态处置、公开作品关联与成功统计全部移交[CHG-20261120-106](../../active/CHG-20261120-106/change.md)。本次是用户确认的范围拆分，不将未交付功能或审核中回执记为完成。M6保持IN_PROGRESS，仅包含百度，其他平台后续。

101～105既有合并基线及真实投稿结果保留在[最终验证结论](evidence/verification.md)。本轮不重新投稿；只补跑现有代码回归和隔离浏览器/数据库检查。各仓一个引用CHG101的PR，提供方先合入，Workspace最后收口。最终入口：Workspace [#58](https://github.com/piqiu96/wt-media-workspace/pull/58)、Cloud [#47](https://github.com/piqiu96/wt-media-cloud/pull/47)、Agent [#14](https://github.com/piqiu96/wt-media-agent/pull/14)、Desktop [#14](https://github.com/piqiu96/wt-media-desktop/pull/14)。Workspace提交指针为同一PR包含的契约/工程提交，最终merge提交由PR追溯；后续CHG须确认四个指针均已进入本地main。

## Done When

- 四仓全部现有本地修改已核对、提交、独立Review，通过对应PR以merge commit合入远端main，并同步本地main；不提交生成文件、凭据及过程截图。
- Cloud提供方契约、Workspace映射和消费路径一致；变更相关的后端、前端、Agent、Desktop及隔离数据库/浏览器验证通过，最终结论仅保留摘要。
- 百度已有真实审核中回执与不可变结果继续保留，不冒充公开作品；两条原任务不重复投稿。
- CHG106明确承接全部未完成M6范围，M6、总计划与Delivery索引同步；CHG101移出Active归档，M6不标记DONE。

## References

- [M6完整闭环](../../milestones/M6-single-publishing.md#单任务从内容准备到真实作品)
- [发布工程设计](../../../docs/engineering/specs/publishing-management.md)
- [PRD第六章](../../../docs/product/prd/详细文档/第六章_发布管理.md)
