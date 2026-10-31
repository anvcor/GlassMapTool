# Optical Glass Map Tool — 网页版

在玻璃图上选角点、生成 CODE V `GLA` 玻璃边界命令的可视化工具。纯 HTML + Canvas，无任何依赖。

## 使用

直接双击 `GlassMapTool.html` 即可（Chrome / Edge，需支持 DecompressionStream）。
如果浏览器拦截本地 `glasses.js`，起一个静态服务：

```bash
python -m http.server 8765 --directory E:/GlassMapTool
```

访问 http://localhost:8765/web/GlassMapTool.html

## 功能

| 功能 | 说明 |
|---|---|
| 数据源 | 点 `...` 选文件或把厂商 xlsx 拖进列表；列表下方附带 CODE V 内置 20 个厂商库（来自 `glasses.js`，可删）。Hold Ctrl 多选 |
| 特殊玻璃隐藏 | CDGM 的 HWS 系列（Vd 2–10）默认不显示、不参与 Auto-Draw / Auto Boundary 和自动缩放；只有当它是角点、落在当前边界内或被 Find 搜到时才显示。规则在 `RARE` 数组里，可自行增减 |
| Auto-Draw Random Boundary | 载入/切换数据源后自动画边界：Map 1–5 能解析的照用，解析不到的用随机玻璃补齐 |
| Search Glass Find / Clear | 找到后高亮并提示是否在边界内 |
| GLC 变量 → 近邻玻璃 | 可视化的 GLASSFIT。把 LDM 里的玻璃变量粘进来（只复制玻璃列，或整行复制带上表面号都可以），按 `glassfit.seq` 的度量在所选库中找最近的 N 块玻璃，详见下文 |
| Map 1–5 | 打开时默认选中 CODE V 的 HOYA 库，角点为 FCD100 FCD705 TAC6 TAFD65 FDS16W；也接受 `1.517:64.2`、`487.704`、`517642` 假想玻璃 |
| Draw / Clear | Draw 前自动做凸包排序，非凸角点会警告并剔除（GLA 只接受凸多边形） |
| Fine Tuning 九宫格 | 可选移动整个边界或单个角点，移动后角点变假想玻璃 `nd:Vd` |
| 图上交互 | 靠近玻璃点即高亮并显示提示（捕捉半径 18 px），点击设为/移除角点；角点可直接拖动，松手时吸附到 12 px 内的玻璃，否则成为假想玻璃 |
| 两个标签页 + 缩放工具条 | nd–Vd 图与阿贝图；阿贝图上的边界边按 nd–(nF−nC) 空间采样成曲线 |
| GLA 命令 | 单行 `GLA` 命令 + 一键复制、边界内玻璃清单、解析已有 GLA 命令、导出 PNG |
| Auto Boundary | 自动边界。先剥离离群玻璃（凸包上单点撑起面积超过 0.4% 的顶点，如 HWS 系列），直到覆盖率降到目标值（默认 97%）为止；再在剩余点的凸包上取 5 角点。假想角点模式收缩凸包成 5 边形，真实玻璃模式枚举凸包顶点 5 元组，覆盖数优先、面积次之 |

## GLC 变量 → 近邻玻璃（GLASSFIT）

- **输入**：CODE V 假想玻璃名 `566548.413241` 解析为 nd = 1.566548、Vd = 41.3241（与 `glassfit.seq` 拆法相同），也接受 `1.5665:41.32`。行首是表面号时（LDM 整行复制，或 `GLA S16 …`）标为 `S16`，否则依次标为 `G1`、`G2`…
- **度量**：d = √(ΔNd² + (w·Δdisp)²)，disp = (nd−1)/Vd。GLASSFIT 里 w = disp_factor × 50 × (λ1−λn)/170.14 nm：C-d-F 三波长、disp_factor = 1 时 w = 50（默认值），656–436 nm 五波长时 w = 64.8。ΔNd、ΔVd 的符号同 GLASSFIT，为变量 − 玻璃。
- **范围**：在列表里当前选中的库中搜索（HWS 这类默认隐藏的特殊玻璃也算在内，同 GLASSFIT；入选候选时会在图上显示出来），牌号_厂商相同的只算一次。勾选“去停产”时剔除 CODE V 库里可用性代码为 3 / 4 的牌号（GLASSFIT 默认也这样做）。
- **图上显示**：变量画成玫红菱形。当前聚焦的变量画出到前 N 块玻璃的连线，以及经过第 N 块的 GLASSFIT 等距线：nd–(nF−nC) 图上是椭圆，定位时会锁定纵横比，让它显示成正圆，屏幕上看到的远近就是 GLASSFIT 距离；阿贝图上是斜椭圆。
- **交互**：点变量标题定位并放大；点候选行，或点图上的候选点，换选替换玻璃（候选点上的点击不会再去设边界角点）。带表面号的变量生成 `GLC Sk 100; GLA Sk 牌号`，与 GLASSFIT 替换时一致，一键复制。

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
