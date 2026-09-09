"""
extract_glass.py  --  从 CODE V 安装目录的 glass/*.xml 提取玻璃库，计算 nd / nF / nC / Vd / (nF-nC)。
仅用 Python 标准库。输出 glasses.json，供 glass_boundary_tool.html 使用。

用法:
    python extract_glass.py [CODEV_glass_dir] [out.json]
默认: E:/CODEV2026/glass  ->  ./glasses.json

色散公式来源: CODE V Lens System Setup RM, "Dispersion formulae"（波长单位 µm）。
"""
import sys, os, json, math, glob
import xml.etree.ElementTree as ET

LAM_D = 0.5875618   # d  He
LAM_F = 0.4861327   # F  H
LAM_C = 0.6562725   # C  H


def n_of(eq, A, lam):
    """按 CODE V 色散公式类型计算折射率. A: 系数列表, lam: µm"""
    L2 = lam * lam
    A = list(A) + [0.0] * 12
    if eq == "Laurent":
        n2 = A[0] + A[1] * L2 + sum(A[k] * L2 ** -(k - 1) for k in range(2, 12))
    elif eq == "Glass Manufacturer Laurent":
        # 手册只列 7 项；HIKARI 库里有 9 项的条目，经与厂商数据表比对，A7、A8 为 λ^-10、λ^-12 项
        n2 = (A[0] + A[1] * L2 + A[2] / L2 + A[3] / L2**2 + A[4] / L2**3 + A[5] / L2**4
              + A[6] * L2**2 + A[7] / L2**5 + A[8] / L2**6)
    elif eq == "Glass Manufacturer Sellmeier":      # B1 C1 B2 C2 ...
        n2 = 1.0 + sum(A[2 * i] * L2 / (L2 - A[2 * i + 1]) for i in range(6))
    elif eq == "Standard Sellmeier":                # C 项为平方
        n2 = 1.0 + sum(A[2 * i] * L2 / (L2 - A[2 * i + 1] ** 2) for i in range(6))
    elif eq == "Glass Manufacturer Cauchy":
        return A[0] + A[1] / L2 + A[2] / L2**2
    elif eq == "Herzberger":
        # n = A + B*L + C*L^2 + D*lam^2 + E*lam^4 + F*lam^6,  L = 1/(lam^2 - 0.028)
        # CODE V 手册未列出，按 Herzberger 标准式写，并用 NumericName 校验（见 validate）。
        Lh = 1.0 / (L2 - 0.028)
        n2 = A[0] + A[1] * Lh + A[2] * Lh**2 + A[3] * L2 + A[4] * L2**2 + A[5] * L2**3
        # 首项 ~2.6 说明是 n^2 形式
    else:
        raise ValueError(eq)
    return math.sqrt(n2)


def load_catalog(path):
    root = ET.parse(path).getroot()
    cat = root.findtext("Name").strip()
    out = []
    for g in root.iter("Glass"):
        name = g.findtext("GlassName").strip()
        eq = g.findtext("EquationType").strip()
        coef = [float(c.text) for c in g.find("DispersionCoefficients")]
        numeric = (g.findtext("NumericName") or "").strip()
        avail = g.findtext("Availability")
        try:
            nd = n_of(eq, coef, LAM_D)
            nF = n_of(eq, coef, LAM_F)
            nC = n_of(eq, coef, LAM_C)
        except (ValueError, ZeroDivisionError):
            continue
        if not (1.2 < nd < 4.5) or nF <= nC:
            continue
        dn = nF - nC
        vd = (nd - 1.0) / dn
        out.append(dict(name=name, cat=cat, nd=round(nd, 6), vd=round(vd, 3),
                        dn=round(dn, 6), code=numeric, eq=eq, avail=avail))
    return out


def validate(glasses):
    """用 6 位玻璃码 (nd-1)*1000 / vd*10 校验公式实现"""
    bad = {}
    for g in glasses:
        c = g["code"]
        if not (c.isdigit() and len(c) == 6):
            continue
        nd_code = 1 + int(c[:3]) / 1000
        vd_code = int(c[3:]) / 10
        if abs(nd_code - g["nd"]) > 0.0015 or abs(vd_code - g["vd"]) > 0.6:
            bad.setdefault(g["eq"], []).append((g["cat"], g["name"], c, g["nd"], g["vd"]))
    return bad


def main():
    gdir = sys.argv[1] if len(sys.argv) > 1 else "E:/CODEV2026/glass"
    outp = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(__file__), "glasses.json")
    allg = []
    for f in sorted(glob.glob(os.path.join(gdir, "*.xml"))):
        gs = load_catalog(f)
        print(f"{os.path.basename(f):16s} {len(gs):5d} glasses")
        allg += gs
    bad = validate(allg)
    for eq, lst in bad.items():
        print(f"\n[校验不符] {eq}: {len(lst)} 条")
        for row in lst[:5]:
            print("   ", row)
    with open(outp, "w", encoding="utf-8") as fp:
        json.dump(allg, fp, ensure_ascii=False, separators=(",", ":"))
    print(f"\n共 {len(allg)} 条 -> {outp}")


if __name__ == "__main__":
    main()
