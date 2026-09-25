#!/usr/bin/env python3
"""T-11: 合并件的双向探针检查（保留项必须在 / 删除项必须不在），带双向阳性对照。

用法: python3 .../t11_probe_check.py [--inject]
  --inject 在每一向各注入一条必然违反的探针，证明两个方向都能报 FAIL。
"""
import re, sys

MERGED = "docs/engineering/specs/web-desktop-visual-system.md"

KEEP = [
    # 视觉：Design Tokens 全量
    "--wt-color-primary: #0052d9", "--wt-color-primary-hover: #266fe8",
    "--wt-color-primary-active: #003cab", "--wt-color-primary-light: #e8f3ff",
    "--wt-color-primary-border: #bbd3fb", "--wt-color-success: #00a870",
    "--wt-color-success-bg: #e8f8f2", "--wt-color-success-border: #a7e3cf",
    "--wt-color-warning: #ed7b2f", "--wt-color-warning-bg: #fff3e8",
    "--wt-color-warning-border: #f7c797", "--wt-color-danger: #d54941",
    "--wt-color-danger-hover: #e34d59", "--wt-color-danger-bg: #fff0ed",
    "--wt-color-danger-border: #f5b7b1", "--wt-color-text-primary: #1d2129",
    "--wt-color-text-secondary: #4e5969", "--wt-color-text-assist: #86909c",
    "--wt-color-text-disabled: #c9cdd4", "--wt-color-text-inverse: #ffffff",
    "--wt-color-bg-page: #f2f3f5", "--wt-color-bg-container: #ffffff",
    "--wt-color-bg-subtle: #f7f8fa", "--wt-color-bg-hover: #f2f3f5",
    "--wt-color-border: #e5e6eb", "--wt-color-border-strong: #c9cdd4",
    "--wt-shadow-fixed-column: -6px 0 12px rgb(0 0 0 / 6%)",
    "--wt-shadow-popup: 0 8px 24px rgb(0 0 0 / 12%)",
    # 视觉：字号/间距/取值
    "4 / 8 / 12 / 16 / 20 / 24 / 32", "页面标题", "24–28px",
    "普通控件高度", "关键表单控件", "表格密度", "暗色模式",
    # 视觉：五层模型与决策顺序
    "第五层：页面局部样式", "PageContainer", "ResultSummary",
    "AccountInfoCell", "BrowserProfileSummary", "AccountStatusBadge",
    "BatchCheckProgress", "MaterialInfoCell", "PublicationStatusCell",
    "约 70%：TDesign 现成组件与交互",
    # 视觉：按钮/状态/标签
    "Link Primary", "部分成功", "结果待确认", "BusinessStatus",
    # 视觉：模板与表格/表单/反馈
    "SummaryMetrics", "SelectionToolbar", "FilterPanel", "DataTable",
    "360–440px", "560–640px", "44–48px", "64–76px", "72–80px",
    "仅用于需要长期观察整体运行态势的页面",
    # 视觉：多套样式工具风险 7 节
    "组件库互相污染", "大量覆盖组件库内部 CSS", "ECharts 与系统主题不一致",
    "多套图标库", "全量引入导致体积膨胀", "Desktop 多系统 WebView 差异",
    "appChartTheme", "125% / 150% 系统缩放",
    # 视觉：检查与 Review
    "是否把请求提交展示为真实成功", "未在共享业务组件直接调用 Tauri",
    "单页面临时样式不得直接升级为全局规范",
    # 架构：实测值
    "wt-media-cloud/web", "src/apps/", "apps → modules", "shared → modules",
    "interface RuntimeAdapter", "WebRuntimeAdapter", "DesktopRuntimeAdapter",
    "frontendDist", "beforeDevCommand", "devUrl",
    "127.0.0.1:5174", "npm run dev:desktop", "npm run build:cloud",
    "npm run build:desktop", "dist-cloud", "dist-desktop",
    "vite.config.cloud.js", "vite.config.desktop.js",
    "index.cloud.html", "index.desktop.html", "package-lock.json",
    "config/release-matrix.yaml", "config/repository-map.yaml",
    "scripts/release-versions.sh", "scripts/build-desktop.sh",
    "frontend-build.json", "source_commit", "frontend_build_version",
    "两套完整前端", "Desktop 内再嵌套 iframe Web 后台",
    "Desktop 永远直接加载线上 Web 地址",
    "Cloud API 必须兼容一定范围内的旧客户端",
    "一套组件库、一套同源图标、一个图表引擎",
]

DROP = [
    # 死路径 / 旧包管理器 / 旧脚本名
    "wt-media-cloud/frontend", "pnpm", "build:web", "dist-web", "dev:web",
    "frontendCommit", "localhost:5173", "VITE_RUNTIME",
    # 未落地的推荐内部结构
    "apps/console", "packages/business-components", "packages/runtime",
    "entries/web.ts", "entries/desktop.ts", "build:web       → 部署到 Cloud/Web",
    # 功能类：各模块复用情况
    "各模块复用情况", "完全复用", "页面复用，执行能力不同", "Desktop 独有",
    # 功能类：系统导航
    "系统导航建议", "运营执行", "资源管理\n├── 社媒账号",
    # 功能类：模板的「适用于」清单与业务字段例
    "适用于：", "material_usage", "compose_task", "composite_output",
    "| pending | 待执行 |", "| queued | 排队中 |", "| discarded | 已丢弃 |",
    # 功能类：首页工作台
    "首页工作台建议", "导入抖音链接", "4 个发布任务失败",
    "内容抓取 → 素材生产 → 合成 → 发布 → 互动",
    # 功能类：优先改造顺序
    "优先改造顺序", "三个页面定型后", "Desktop 系统状态中心",
]


def main():
    inject = "--inject" in sys.argv
    flat = open(MERGED, encoding="utf-8").read()
    bad = 0

    keep = list(KEEP) + (["__T11_KEEP_阳性对照_必然不在__"] if inject else [])
    drop = list(DROP) + (["商业运营后台", ] if inject else [])

    print(f"注入模式: {'开（阳性对照）' if inject else '关（实测）'}")
    print(f"\n[方向一] 必须保留：分母 {len(keep)}")
    for p in keep:
        if p not in flat:
            bad += 1
            print(f"  FAIL  应保留但缺失: {p}")
    print(f"  失败 {bad}")

    before = bad
    print(f"\n[方向二] 必须删除：分母 {len(drop)}")
    for p in drop:
        if p in flat:
            bad += 1
            print(f"  FAIL  应删除但仍存在: {p}")
    print(f"  失败 {bad - before}")

    print(f"\n合计失败 {bad}")


main()
