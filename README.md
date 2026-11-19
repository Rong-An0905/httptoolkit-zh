# HTTP Toolkit 中文化（本地镜像 + 注入层）

在不修改 HTTP Toolkit 安装包的前提下，让桌面版界面显示中文，并支持**运行时随时切换中英文**。

## 原理

HTTP Toolkit 桌面版的界面本身是一个网页（默认从 `https://app.httptoolkit.tech` 加载）。本项目：

1. 把该网页的静态资源镜像到本地 `ui/`；
2. 在 `index.html` 里注入 `i18n-zh.js`（词表 + DOM 翻译层）；
3. 通过 `APP_URL` 环境变量让桌面端改从本地 `http://127.0.0.1:8899` 加载界面。

程序本身、拦截与抓包逻辑均未改动。

## 使用

1. 确认 HTTP Toolkit 安装路径与 `start-zh.ps1` 中的 `$Exe` 一致（默认 `D:\HTTP Toolkit\HTTP Toolkit.exe`）；
2. 确认 `start-zh.ps1` 中的 `$Python` 指向本机 Python 3；
3. 完全退出已运行的 HTTP Toolkit；
4. 双击 `启动汉化版.bat`。

切换语言：

- 点击窗口右下角悬浮按钮 `中文 / EN`；
- 或按 `Ctrl + Alt + L`。

选择会写入 localStorage，下次启动沿用上次语言（首次默认中文）。

## 目录

```
ui/                 镜像的界面资源 + i18n-zh.js
serve.py            本地静态服务器（127.0.0.1:8899）
start-zh.ps1        启动器：起服务 → 设 APP_URL → 启动客户端
启动汉化版.bat       双击入口
还原原版.bat         撤销对 HTTP Toolkit 服务端的 CORS 补丁
tools/              源码与构建脚本
  mirror.py           镜像 UI 静态资源
  fetch_chunks.py     补齐懒加载分片
  extract_strings.py  从打包产物抽取界面文案
  translate.py        批量机翻，生成 dict.json
  overrides.json      专有名词人工校正
  build_i18n.py       合成 i18n-zh.js 并注入 index.html
  patch_server.py     给本地 API server 的 CORS 白名单加上本地源
  restore_server.py   还原服务端文件
  cdp_test.mjs        用 CDP 校验翻译覆盖率与切换效果
```

## 关于 CORS 补丁

本地页面（`http://127.0.0.1:8899`）默认不在 HTTP Toolkit 服务端的允许来源里，`patch_server.py` 会在
`resources/httptoolkit-server/bundle/index.js` 的白名单中追加本地源，并把原文件备份为 `index.js.bak-orig`。

- 该改动只影响跨域白名单，用于让本地页面能调用本机服务端；
- HTTP Toolkit 自动更新服务端后会覆盖补丁，重跑 `python tools\patch_server.py` 即可；
- 运行 `还原原版.bat` 可恢复安装目录原状。

## 已知限制

- Electron 原生菜单栏（File / Edit / View / Help）不属于网页，无法翻译；
- 翻译基于词表 + 机器翻译，专业术语可能不完美，可在 `tools/overrides.json` 中补正后重新 `build_i18n.py`；
- 界面更新后需重新执行 `mirror.py` → `fetch_chunks.py` → `extract_strings.py` → `translate.py` → `build_i18n.py`。

## 许可与致谢

- 本项目中的 `ui/` 资源来自 [HTTP Toolkit](https://github.com/httptoolkit/httptoolkit-ui)，遵循 AGPL-3.0；
- HTTP Toolkit 版权归 Tim Perry 及贡献者所有；
- 本仓库仅提供本地化外壳脚本与翻译层，用于个人学习与自用。
