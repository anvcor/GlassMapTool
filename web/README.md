# Optical Glass Map Tool — 网页版

原 `application/GlassMapTool.exe`（MATLAB R2024b 编译，作者 LinBao）的 HTML 复刻。
源码加密无法读取，按其界面与可观察行为重建，并补上 CODE V `GLA` 命令生成。

## 使用

直接双击 `GlassMapTool.html` 即可（Chrome / Edge，需支持 DecompressionStream）。
如果浏览器拦截本地 `glasses.js`，起一个静态服务：

```bash
python -m http.server 8765 --directory E:/GlassMapTool
```

访问 http://localhost:8765/web/GlassMapTool.html

## 与原程序的对应

| 原 exe | 网页版 |
|---|---|
| 扫描 exe 目录下 .xlsx | 浏览器不能扫目录，点 `...` 选文件或把 xlsx 拖进列表；列表下方附带 CODE V 内置 20 个厂商库（来自 `glasses.js`，可删） |
| Hold Ctrl 多选 | 同 |
| Auto-Draw Random Boundary | 载入/切换数据源后自动画边界：Map 1–5 能解析的照用，解析不到的用随机玻璃补齐（原程序"Random"的具体规则不可知，此为假设） |
| Search Glass Find / Clear | 同，找到后高亮并提示是否在边界内 |
| Map 1–5 默认 H-FK95N H-LAK52 H-ZLAF68C H-ZLAF96 H-ZF73 | 打开时默认选中 CODE V 的 HOYA 库，角点改为 FCD100 FCD705 TAC6 TAFD65 FDS16W；也接受 `1.517:64.2`、`487.704`、`517642` 假想玻璃 |
| Draw / Clear | 同；Draw 前自动做凸包排序，非凸角点会警告并剔除（GLA 只接受凸多边形） |
| Fine Tuning 九宫格 | 同；可选移动整个边界或单个角点，移动后角点变假想玻璃 `nd:Vd` |
| — | 图上交互：靠近玻璃点即高亮并显示提示（捕捉半径 18 px），点击设为/移除角点；角点可直接拖动，松手时吸附到 12 px 内的玻璃，否则成为假想玻璃 |
| 两个标签页 + 缩放工具条 | 同；阿贝图上的边界边按 nd–(nF−nC) 空间采样成曲线 |
| — | 新增：单行 `GLA` 命令 + 一键复制、边界内玻璃清单、解析已有 GLA 命令、导出 PNG |
| — | 新增：Auto Boundary 自动边界。先剥离离群玻璃（凸包上单点撑起面积超过 0.4% 的顶点，如 HWS 系列），直到覆盖率降到目标值（默认 97%）为止；再在剩余点的凸包上取 5 角点。假想角点模式收缩凸包成 5 边形，真实玻璃模式枚举凸包顶点 5 元组，覆盖数优先、面积次之 |

## 牌号输入规则

去掉连字符和空格、忽略大小写后比对，所以 `E-FDS1-W`、`EFDS1W`、`e-fds1-w`、`TAFD-55W` 都能命中同一块玻璃。
也可加厂商后缀限定：`EFDS1W_HOYA`。

## xlsx 识别规则

前 8 行内按表头找列：名称列含 `Glass`；`nd`、`nF`、`nC`（或 HOYA 的 `nF-nC`）。
已验证：CDGM202603、HIKARI_ALL_Catalog_Data、HOYA20260601、OHARA_20250312_L5、OHARA_20260402_5。
其它厂商表只要表头符合上述规则即可加载。

## GLA 语法（Optimization RM Ch5）

```
GLA [Si..j] [Zi..j] glass1 glass2 glass3 [glass4 [glass5]]
```

输出用 CODE V 内部名（去掉牌号中的 `-` 和空格）加 `_厂商` 后缀，如 `HFK95N_CDGM`。
