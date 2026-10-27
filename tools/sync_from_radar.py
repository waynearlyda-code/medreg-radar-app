"""从雷达项目同步界面代码到 App：雷达网页改了以后运行一次。

    python3 tools/sync_from_radar.py ../medreg-radar

同步内容：样式（www/app.css 的前半部分）、脚本（www/app.js）、index.html 里的
雷达图、筛选与导出面板、图表区。App 自己的部分（标签栏、指南、启动逻辑）不动。
"""
import os
import re
import sys

APP_CSS_MARK = "/* ====== App 布局"

BOOT = r'''
/* ---------- 启动：先用缓存秒开，再去网上取最新数据 ---------- */
(function boot() {
  var KEY = "mr_data_cache", app = null, current = null;
  function cached() { try { return JSON.parse(localStorage.getItem(KEY) || "null"); } catch (e) { return null; } }
  function save(d) { try { localStorage.setItem(KEY, JSON.stringify(d)); } catch (e) {} }
  function stamp(d, src) {
    document.getElementById("upd").textContent = "数据 " + d.today + (src === "snapshot" ? " · 内置" : src === "cache" ? " · 离线缓存" : "");
  }
  function run(d, src) { current = d; stamp(d, src); app = startApp(d); }

  window.showView = function (name) {
    if (!document.getElementById("v-" + name)) name = "feed";
    document.querySelectorAll(".view").forEach(function (v) { v.classList.toggle("on", v.id === "v-" + name); });
    document.querySelectorAll(".tabs button").forEach(function (b) { b.setAttribute("aria-selected", b.dataset.view === name ? "true" : "false"); });
    try { history.replaceState(null, "", "#/" + name); } catch (e) {}
    if (name === "data" && app) app.renderCharts();
    window.scrollTo(0, 0);
  };
  document.querySelectorAll(".tabs button").forEach(function (b) { b.addEventListener("click", function () { window.showView(b.dataset.view); }); });

  var c = cached();
  if (c) run(c, "cache"); else run(window.MR_SNAPSHOT, "snapshot");
  window.showView(location.hash.replace(/^#\/?/, "") || "feed");

  function toast(msg, onclick) {
    var t = document.getElementById("toast"); t.textContent = msg; t.classList.add("on"); t.onclick = onclick || null;
    if (!onclick) setTimeout(function () { t.classList.remove("on"); }, 2200);
  }
  function refresh(manual) {
    return fetch(window.MR_CONFIG.dataUrl + "?t=" + Date.now(), { cache: "no-store" }).then(function (r) {
      if (!r.ok) throw new Error(r.status); return r.json();
    }).then(function (d) {
      save(d);
      if (!current || d.today !== current.today || d.items.length !== current.items.length) toast("有新数据（" + d.today + "），点这里刷新", function () { location.reload(); });
      else { stamp(d, "net"); if (manual) toast("已经是最新的了"); }
    }).catch(function () { if (manual) toast("连不上数据源，先显示离线内容"); });
  }
  document.getElementById("refresh").addEventListener("click", function () { refresh(true); });
  refresh(false);

  /* 安装提示（安卓 Chrome / 电脑 Chrome、Edge） */
  var deferred = null;
  window.addEventListener("beforeinstallprompt", function (e) { e.preventDefault(); deferred = e; document.querySelectorAll(".install-btn").forEach(function (b) { b.hidden = false; }); });
  document.querySelectorAll(".install-btn").forEach(function (b) {
    b.addEventListener("click", function () { if (deferred) { deferred.prompt(); deferred = null; b.hidden = true; } });
  });
  if ("serviceWorker" in navigator && location.protocol.indexOf("http") === 0) navigator.serviceWorker.register("sw.js").catch(function () {});
})();
'''


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def write(p, s):
    with open(p, "w", encoding="utf-8") as f:
        f.write(s)


def between(s, a, b, include_end=False):
    i = s.index(a)
    j = s.index(b, i)
    return s[i:j + (len(b) if include_end else 0)]


def main(radar):
    here = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "www")
    web = os.path.join(radar, "medreg", "web")

    # 样式：雷达的样式 + App 自己的布局
    css_app = read(os.path.join(here, "app.css"))
    write(os.path.join(here, "app.css"), read(os.path.join(web, "style.css")) + "\n" + css_app[css_app.index(APP_CSS_MARK):])

    # 脚本：把网页版的立即执行函数改成 startApp(MR)，档案链接指向雷达网站，再接上 App 的启动逻辑
    js = read(os.path.join(web, "app.js"))
    js = re.sub(r'^/\*.*?\*/\s*\(function \(\) \{\s*"use strict";\s*var MR = window\.MR;',
                '/* MedReg Radar App。界面逻辑由 tools/sync_from_radar.py 从雷达网页同步而来；数据从网上的 data.json 读取，\n   失败时用缓存或内置快照。所有来自数据的文字都用 textContent 写入。 */\nfunction startApp(MR) {\n  "use strict";',
                js, count=1, flags=re.S)
    assert js.rstrip().endswith("})();")
    js = js.rstrip()[:-len("})();")] + "  return { renderCharts: renderCharts };\n}\n"
    js = js.replace('href: kind + "/" + r.label + ".html" }', 'href: window.MR_CONFIG.siteUrl + kind + "/" + r.label + ".html", target: "_blank", rel: "noopener" }')
    write(os.path.join(here, "app.js"), js + BOOT)

    # 页面片段
    src = read(os.path.join(web, "index.html"))
    page = read(os.path.join(here, "index.html"))
    for a, b in [('<svg viewBox="0 0 400 400">', '</svg>'),
                 ('<div class="filters">', '<div class="feed" id="feed">')]:
        new = between(src, a, b, include_end=(b == '</svg>'))
        old = between(page, a, b, include_end=(b == '</svg>'))
        page = page.replace(old, new)
    charts_new = between(src, '<div class="charts">', '</section>')
    charts_new = charts_new[:charts_new.rindex("</div>")]
    charts_old = between(page, '<div class="charts">', '<h3 style="margin:26px 0 8px')
    charts_old = charts_old[:charts_old.rindex("</div>")]
    page = page.replace(charts_old, charts_new)
    write(os.path.join(here, "index.html"), page)
    print("已同步：app.css / app.js / index.html")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join("..", "medreg-radar"))
