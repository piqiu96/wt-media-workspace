# M2 侧栏现代东方视觉更新（2026-09-14）

## 变更

- 仅更新 `wt-media-cloud/web/src/layout/AppLayout.vue` 的侧栏品牌区、TDesign 菜单视觉覆盖与展开状态持久化；菜单数据、路由和业务权限过滤均未修改。
- 侧栏采用 `#FAFAF8` 暖白背景、弱右边界、中文系统字体、44px 一级项和 40px 二级项。
- 二级项以细竖向引导线表达层级；活动项使用低饱和蓝色背景、蓝色文字和 3px 左侧竖线，不使用默认强按钮态。
- 展开箭头使用 14px、半透明和 200ms 旋转；菜单展开高度为 200ms 过渡。
- 展开分组保存为浏览器本地键 `wt-media:sidebar-expanded-groups`；路由变化时只补充当前所在分组，不覆盖用户已展开的分组。

## 验证

```text
cd wt-media-cloud/web && npm test -- --run src/layout/AppLayout.test.js
4 passed

cd wt-media-cloud/web && npm run build:desktop
vite production build passed

cd wt-media-workspace && ./scripts/local-control.sh start
Cloud health PASS
Agent health PASS
BitBrowser via Agent PASS
Desktop assets PASS
DMG PASS
Login smoke PASS user=admin
```
