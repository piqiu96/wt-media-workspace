---
id: CHG-20261107-126
parent: delivery/milestones/M4-content-production.md#m4-p-file-links-and-upload
status: VERIFYING
depends_on: []
affected_repos: ["wt-media-cloud", "wt-media-workspace"]
risk: M
verify_scenarios: ["repo", "integration"]
---

# CHG-20261107-126: 文件直链、上传交互及列表操作规范

## Change

用户已确认执行：文件管理复制URL使用已配置bucket公共HTTPS域名及持久化完整对象位置，改名不改变URL；保留旧平台资源入口兼容。使用公共上传、表单、列表组件优化上传及行操作颜色，修正文件管理、素材及相关合成列表。仅修改Workspace事实与Cloud后端/共享Vue，无数据库迁移，不改Agent/Desktop运行代码、不创建worktree、不调整bucket权限。

当前基线：Workspace main 794d82ff、Cloud main 0d161df7均干净且已发布；CHG121～125已归档。原文件管理仅复制平台capability URL，上传暴露原生文件控件，操作列写死宽度并混用Link/文字按钮，相关合成列表残留描边按钮类。实际存储公共域名已匿名读到现有运营文件。

## Done When

- Cloud兼容新增public_url，依据完整对象引用和files专用域名配置生成；中文/空格/%/#正确编码，错bucket或无效配置明确失败，上传前发现配置错误，不发布错误链接。改名URL不变；旧resource_path及合成引用继续可用。
- 文件列表复制直链可匿名读取且字节摘要一致；上传、改名、下载及删除真实对象闭环，旧文件兼容及角色授权回归通过。
- 上传使用TDesign选择/拖拽和共享Dialog/Form，文件预览/大小/重选/移除及可编辑名称清晰；上传中防重复、真实反馈，失败保留文件与名称，成功刷新。
- 文件管理及相关合成列表遵守ResourceRowActions/opColumnWidth和既定常规/危险/禁用颜色规范，核对实际页面与悬停；Cloud/桌面共享前端构建、定向行为测试及CHG检查通过。
- 独立Review通过，两个仓库各自PR合入main后归档，保留真实证据；自动化不替代用户人工视觉签收。

## References

- docs/decisions/0032-compose-resources-and-template-cutover.md
- docs/product/prd/详细文档/第五章_素材生产.md §5.10
- docs/engineering/specs/2026-09-24-m4-m5-cloud-content-production.md
- docs/standards/frontend/前端架构与视觉规范.md §3.7
- docs/standards/frontend/AdminUI页面规范.md §4.3
