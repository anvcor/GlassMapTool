# Optical Glass Map Tool

光学玻璃图（nd–Vd / 阿贝图）可视化工具，用于给 CODE V 优化中的 `GLA` 玻璃边界命令选角点、生成命令、列出边界内牌号。
纯 HTML + Canvas，无任何依赖，可直接在浏览器中运行。

**在线使用：** https://anvcor.github.io/GlassMapTool/

## 目录

| 目录 | 内容 |
|---|---|
| [`web/`](web/) | 正式版 `GlassMapTool.html`，是原 MATLAB 版 `GlassMapTool.exe` 的网页复刻并扩展了 GLA 生成；`samples/` 为 CDGM / HIKARI / HOYA / OHARA 官方数据表示例；`glasses.js` 是内置的 CODE V 20 个厂商库数据 |
| [`dev/`](dev/) | 开发版页面与数据提取脚本（`extract_glass.py` 解析 CODE V `glass/*.xml`，`extract_xlsx.py` 解析厂商 xlsx） |

原 MATLAB 编译的 exe 与其安装器不在仓库内（见 `.gitignore`）。

## 本地运行

直接双击 `web/GlassMapTool.html`（Chrome / Edge）。若浏览器拦截本地脚本：

```bash
python -m http.server 8765
```

然后打开 http://localhost:8765/web/GlassMapTool.html

## 功能概要

- 载入 CODE V 内置库或厂商 xlsx，在 nd–Vd 图 / 阿贝图上显示全部牌号
- 选 3–5 个角点（真实玻璃或 `nd:Vd`、6 位码假想玻璃），自动凸包排序与凸性检查
- 生成单行 `GLA` 命令并一键复制；也可解析已有 GLA 命令回显边界
- Auto Boundary：剥离离群玻璃后按目标覆盖率自动取 5 角点
- 角点可在图上拖动、微调，列出边界内所有牌号，导出 PNG

详细说明见 [web/README.md](web/README.md) 与 [dev/README.md](dev/README.md)。
