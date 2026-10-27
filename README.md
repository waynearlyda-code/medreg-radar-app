# MedReg Radar App · 法规雷达

[MedReg Radar](https://github.com/waynearlyda-code/medreg-radar)（医疗器械法规雷达）的应用版：同一份数据，手机和电脑都能装。

- **PWA**：用浏览器打开后“添加到主屏幕”或“安装”，像 App 一样全屏使用，离线也能看上次的内容。iPhone、安卓、电脑通用。
- **安卓安装包**：在 Releases 下载 `.apk` 直接安装。

## 功能

| 页面 | 内容 |
|---|---|
| 动态 | 最新法规与政策，按时间、分级（影像设备 / 医疗器械 / 背景）、关键词筛选，附 AI 解读与原文链接 |
| 雷达 | 每个点是一份新文件，越靠近中心越和影像设备相关 |
| 数据 | 历年政策文件数、药监局每月批准注册数、主题分布、近 12 个月收录量，可切换表格 |
| 问 AI | 针对收录的文件提问，回答标注出处。使用者自备 DeepSeek API key，key 只存在本机 |
| 指南 | 安装、申请 key、数据来源、常见问题 |

## 数据与同步

App 不自己抓取数据，而是读取雷达发布的公开数据文件（`config.js` 里的 `dataUrl`）。所有设备读同一份数据；打开时自动检查更新，没网时显示缓存。首次安装自带一份数据快照。

想接自己部署的雷达：改 `www/config.js` 的两个地址即可。

## 开发

```bash
python3 -m http.server 8080 -d www     # 本地预览：浏览器打开 http://localhost:8080
python3 tools/make_icons.py            # 重新生成图标（纯 Python，无依赖）
```

安卓安装包由 `.github/workflows/android.yml` 在 GitHub 上用 Capacitor 打包，本机不需要安卓开发环境。当前为调试签名，用于自行安装体验。

## 声明

本 App 由程序从公开渠道整理信息，非官方发布，不提供法律或合规意见。一切以官方原文为准。

## 许可

MIT
