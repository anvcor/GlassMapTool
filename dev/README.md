# CODE V Glass Boundary Tool（开发版）

给 CODE V 优化中的 `GLA` 玻璃边界命令做可视化：在玻璃图上选 3–5 个角点，自动做凸包排序、
凸性检查，生成可直接粘进 AUT 的 `GLA` 命令，并列出落在边界内的所有牌号。

## 文件

| 文件 | 作用 |
|---|---|
| `extract_glass.py` | 解析 CODE V 安装目录 `glass/*.xml`（20 个厂商库，3163 条），按色散公式算 nd / nF / nC，输出 `glasses.json` |
| `extract_xlsx.py` | 解析厂商官方数据表 xlsx（CDGM / HIKARI / HOYA / OHARA，875 条），输出 `glasses_xlsx.json` |
| `../web/glasses.js` | 上面两个 json 合并成的静态数据文件，dev 页与 web 页共用 |
| `glass_boundary_tool.html` | 工具本体，纯 HTML + Canvas，无任何依赖 |

## 更新数据

```bash
python extract_glass.py E:/CODEV2026/glass
python extract_xlsx.py  E:/Download/20macro
python -c "import json;d=json.load(open('glasses.json',encoding='utf-8'));x=json.load(open('glasses_xlsx.json',encoding='utf-8'));open('../web/glasses.js','w',encoding='utf-8').write('window.GLASS_DATA='+json.dumps(d,separators=(',',':'))+';\nwindow.GLASS_XLSX='+json.dumps(x,separators=(',',':'))+';')"
```

## 打开

浏览器从 `file://` 打开可能拦截本地脚本，用任意静态服务即可：

```bash
python -m http.server 8765 --directory E:/GlassMapTool
```

然后访问 http://localhost:8765/dev/glass_boundary_tool.html

## CODE V 语法依据（Optimization RM Ch5, GLA 命令）

```
GLA [Si..j] [Zi..j] glass1 glass2 glass3 [glass4 [glass5]]
```

- 约束可变假想玻璃落在 nd vs (nF−nC) 平面上的**凸多边形**内，角点 3–5 个。
- 角点写法：`NBK7_SCHOTT`（名_目录）、`517642`（6 位码）、`487.704`（假想码）、`1.517:64.2`（nd:Vd）。
- 默认边界：`NFK5 NSK16 NLAF2 SF4`（SCHOTT）。
- 多条 GLA 累加；不写面范围则作用于所有可变玻璃。
- 配合 `GLC Sk 0` 把玻璃设为变量，`GLC Sk D 0` 让玻璃只沿边界 D 边移动。

## 色散公式实现说明

- Laurent / GM Laurent / GM Sellmeier / Standard Sellmeier / Cauchy 按 LensSystemSetupRM 实现。
- HIKARI 库有 9 系数的 GM Laurent 条目，手册只列 7 项；经与厂商 xlsx 比对，第 8、9 项为 λ⁻¹⁰、λ⁻¹²。
- Herzberger 按标准式（n² 形式）实现，已用 6 位码校验。
- 已知差异：SUMITA 的 M（模压）系列 6 位码沿用基础牌号，与实际 nd 差 ~0.005；nd≥2 的玻璃 6 位码回绕，均非公式问题。
