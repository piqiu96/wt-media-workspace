// 任务 27 的探针：无手势的新窗口请求会不会到达 WKUIDelegate。
//
// 为什么要自己写一个：这道闸门（`javaScriptCanOpenWindowsAutomatically`）的读数只能
// 来自 WKWebView 本身——Chrome 测不出 Safari 的规矩，而打包的 Desktop 正是 WKWebView。
// 四组读数要回答的是同一件事的两面：闸门在什么条件下关着，以及「有激活」时它开。
//
// 用法：
//   swiftc -O probe.swift -o probe
//   ./probe scripted false   # 页面脚本自己开（无手势），pref=false —— 宿主默认
//   ./probe scripted true    # 同一页 pref=true —— 阳性对照，证明探针接得住
//   ./probe trusted false    # 应用侧 evaluateJavaScript 触发（带激活），pref=false
//   ./probe window false     # 一次激活之后隔 N 毫秒再开，量激活能撑多久
//
// 事件一律直接投给自己的窗口（`window.sendEvent`），不经过系统事件队列：运营的桌面上
// 不会有任何一次点击被它碰到。

import AppKit
import WebKit

/// 三种触发方式各写一页：它们要问的是同一个 delegate 的不一样的两条路（JS 窗口 / 锚点）。
private let pageForScripted = """
<html><body>
  <a id="plain" href="https://example.com/probe-anchor" target="_blank" rel="noopener">anchor</a>
  <script>
    document.getElementById('plain').click();
    var r = window.open('https://example.com/probe-open', '_blank', 'noopener');
    document.title = 'openReturned=' + (r === null ? 'null' : 'window');
  </script>
</body></html>
"""

private let pageForTrusted = """
<html><body>
  <a id="plain" href="https://example.com/anchor-in-page" target="_blank">anchor</a>
  <script>
    // 同一页里的对照臂：页面自己的脚本、没有手势，必须到不了。
    document.getElementById('plain').click();
    function goOpen() { window.open('https://example.com/app-open', '_blank', 'noopener'); }
    function goAnchor() { document.getElementById('plain').click(); }
    function activation() { return String(navigator.userActivation.isActive); }
  </script>
</body></html>
"""

final class Delegate: NSObject, WKUIDelegate, WKNavigationDelegate {
    var fired: [String] = []
    func webView(
        _ webView: WKWebView,
        createWebViewWith configuration: WKWebViewConfiguration,
        for navigationAction: WKNavigationAction,
        windowFeatures: WKWindowFeatures
    ) -> WKWebView? {
        let path = navigationAction.request.url?.lastPathComponent ?? "nil"
        fired.append(path)
        print("DELEGATE \(path)")
        return nil
    }
}

let arm = CommandLine.arguments.count > 1 ? CommandLine.arguments[1] : "scripted"
let pref = CommandLine.arguments.count > 2 && CommandLine.arguments[2] == "true"
let delegate = Delegate()
let app = NSApplication.shared
app.setActivationPolicy(.prohibited)

let config = WKWebViewConfiguration()
config.preferences.javaScriptCanOpenWindowsAutomatically = pref
let web = WKWebView(frame: NSRect(x: 0, y: 0, width: 400, height: 300), configuration: config)
web.uiDelegate = delegate
web.navigationDelegate = delegate
let window = NSWindow(
    contentRect: NSRect(x: -4000, y: -4000, width: 400, height: 300),
    styleMask: [.titled], backing: .buffered, defer: false
)
window.contentView = web
window.orderFrontRegardless()

switch arm {
case "trusted":
    web.loadHTMLString(pageForTrusted, baseURL: nil)
    DispatchQueue.main.asyncAfter(deadline: .now() + 1.5) {
        print("CONTROL_AFTER_PAGE_SCRIPT calls=\(delegate.fired.count) \(delegate.fired)")
        web.evaluateJavaScript("activation()") { value, _ in
            print("APP_JS_SEES_ACTIVATION=\(value ?? "nil")")
        }
        web.evaluateJavaScript("goOpen()") { _, error in
            if let error { print("APP_OPEN_ERROR \(error)") }
        }
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.5) {
            print("AFTER_APP_WINDOW_OPEN calls=\(delegate.fired.count) \(delegate.fired)")
            web.evaluateJavaScript("goAnchor()") { _, error in
                if let error { print("APP_ANCHOR_ERROR \(error)") }
            }
            DispatchQueue.main.asyncAfter(deadline: .now() + 2) {
                print("PREF=\(pref) TOTAL=\(delegate.fired.count) \(delegate.fired)")
                exit(0)
            }
        }
    }
case "window":
    let delays = [0, 250, 1000, 2000, 3000, 5000, 8000]
    web.loadHTMLString("<html><body>waiting</body></html>", baseURL: nil)
    DispatchQueue.main.asyncAfter(deadline: .now() + 1.5) {
        // 一次激活（相当于运营那次点击），随后按上面的间隔各开一次。
        web.evaluateJavaScript(
            """
            \(delays).forEach(function (ms) {
              setTimeout(function () {
                window.open('https://example.com/' + ms, '_blank', 'noopener');
              }, ms);
            });
            true;
            """
        ) { _, error in
            if let error { print("EVAL_ERROR \(error)") }
        }
    }
    DispatchQueue.main.asyncAfter(deadline: .now() + 14) {
        let all = delays.map(String.init)
        let reached = all.filter { delegate.fired.contains($0) }
        let dropped = all.filter { !delegate.fired.contains($0) }
        print("PREF=\(pref) REACHED=\(reached) DROPPED=\(dropped)")
        exit(0)
    }
default:
    web.loadHTMLString(pageForScripted, baseURL: nil)
    DispatchQueue.main.asyncAfter(deadline: .now() + 4) {
        web.evaluateJavaScript("document.title") { value, _ in
            print("PREF=\(pref) TITLE=\(value ?? "nil") CALLS=\(delegate.fired.count) \(delegate.fired)")
            exit(0)
        }
    }
}
app.run()
