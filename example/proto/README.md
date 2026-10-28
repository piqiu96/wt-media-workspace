# 业务原型

此目录保存具体业务流程的可操作HTML原型。公共视觉与交互统一参考 [common](../common/README.md)，规则引用 [frontend正式规范](../../docs/standards/frontend/README.md)。

[打开起始页](starter.html)：一个精简资源信息区与新建Dialog，共用 `../common/example.css` 、`../common/controls.js`和 `../common/example.js`。复制到业务主题子目录时，先把公共资源路径调整为 `../../common/`，再替换标题、业务字段与场景。

## 组织方式

```text
example/
  common/                 公共参考与资源
  proto/
    starter.html          原型起始模板
    <业务主题>/
      index.html          业务原型入口
      README.md           关联正式需求、角色、场景入口与演示边界
      prototype.js        该业务特有的本地演示（确有需要时）
```

业务原型组合公共结构、扩展实际需求场景；不要每个原型重新维护颜色、基础控件和浮层。发现可复用的新模式时，先提出规范修订和公共影响，获批后写回common。业务特有权限、字段和异常语义应引用所属正式需求，不写进common。

所有演示数据明确标识，不填真实凭据，不连接业务服务，不将模拟结果当验收证据。starter只是起始模板；完整业务原型以对应主题的index.html为唯一当前入口。原型不等于真实业务已经完成落地。

[浏览器窗口与代理完整原型](browser-proxy/index.html)包含75个有效场景，按当前公共规范适配。只保留最终稿与必要资源，遵循[example约定](../README.md#当前稿保留)。
