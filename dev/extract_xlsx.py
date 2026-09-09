"""
extract_xlsx.py  --  从厂商官方玻璃数据表 (CDGM / HIKARI / HOYA / OHARA 的 .xlsx) 提取 nd / nF / nC。
仅用 Python 标准库 (zipfile + xml)。输出与 extract_glass.py 相同的记录格式。

用法:
    python extract_xlsx.py  <xlsx目录>  [out.json]

识别方式：在前 8 行里按表头文字找列——
    名称列: 含 "Glass"      nd: "nd" / "d\n0.5875"      nF: "nF" / "F\n0.486"      nC: "nC" / "C\n0.656"
    HOYA 没有 nF、nC 列，用 nd 和 "nF-nC" 列。
CODE V 内部名 = 厂商牌号去掉 '-' 和空格并大写（H-FK55 -> HFK55, S-FPM 2 -> SFPM2）。
"""
import sys, os, re, json, glob, zipfile
import xml.etree.ElementTree as ET

NS = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}


def read_sheets(path):
    """返回 {sheet名: [[cell,...],...]}，单元格为 str 或 None"""
    z = zipfile.ZipFile(path)
    ss = []
    if 'xl/sharedStrings.xml' in z.namelist():
        for si in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si', NS):
            ss.append(''.join(t.text or '' for t in si.iter('{%s}t' % NS['m'])))
    wb = ET.fromstring(z.read('xl/workbook.xml'))
    names = [s.get('name') for s in wb.find('m:sheets', NS)]
    files = sorted(n for n in z.namelist() if re.match(r'xl/worksheets/sheet\d+\.xml$', n))
    out = {}
    for name, f in zip(names, files):
        root = ET.fromstring(z.read(f))
        rows = []
        for r in root.find('m:sheetData', NS):
            vals = {}
            for c in r:
                v = c.find('m:v', NS)
                if v is None:
                    continue
                col = re.match(r'[A-Z]+', c.get('r')).group(0)
                ci = 0
                for ch in col:
                    ci = ci * 26 + ord(ch) - 64
                vals[ci - 1] = ss[int(v.text)] if c.get('t') == 's' else v.text
            if vals:
                row = [None] * (max(vals) + 1)
                for k, val in vals.items():
                    row[k] = val
                rows.append(row)
            else:
                rows.append([])
        out[name] = rows
    return out


def find_cols(rows):
    """在前 8 行找 name/nd/nF/nC/dn 列号"""
    pats = {
        'name': re.compile(r'glass', re.I),
        'nd':   re.compile(r'^\s*nd\s*$|^d\s*\n|^n?d\s*\(?587', re.I),
        'nF':   re.compile(r'^\s*nF\s*$|^F\s*\n|^n?F\s*\(?486', re.I),
        'nC':   re.compile(r'^\s*nC\s*$|^C\s*\n|^n?C\s*\(?656', re.I),
        'dn':   re.compile(r'^\s*nF\s*-\s*nC\s*$', re.I),
    }
    cols, hdr_row = {}, 0
    for ri, row in enumerate(rows[:8]):
        for ci, cell in enumerate(row):
            if not isinstance(cell, str):
                continue
            for key, p in pats.items():
                if key not in cols and p.search(cell):
                    cols[key] = ci
                    hdr_row = max(hdr_row, ri)
    return cols, hdr_row


def parse_file(path):
    cat = re.match(r'[A-Za-z]+', os.path.basename(path)).group(0).upper()
    src = os.path.basename(path)
    out = []
    for sheet, rows in read_sheets(path).items():
        cols, hdr = find_cols(rows)
        if 'name' not in cols or 'nd' not in cols or not ({'nF', 'nC'} <= cols.keys() or 'dn' in cols):
            continue
        for row in rows[hdr + 1:]:
            try:
                name = row[cols['name']]
                nd = float(row[cols['nd']])
                if 'dn' in cols:
                    dn = float(row[cols['dn']])
                else:
                    dn = float(row[cols['nF']]) - float(row[cols['nC']])
            except (TypeError, ValueError, IndexError):
                continue
            if not isinstance(name, str) or not name.strip() or not (1.2 < nd < 4.5) or dn <= 0:
                continue
            name = name.strip()
            cvname = re.sub(r'[\s\-]', '', name).upper()
            out.append(dict(name=cvname, vendor_name=name, cat=cat, sheet=sheet, src=src,
                            nd=round(nd, 6), vd=round((nd - 1) / dn, 3), dn=round(dn, 6)))
    return out


def main():
    d = sys.argv[1] if len(sys.argv) > 1 else '.'
    outp = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(os.path.abspath(__file__)), 'glasses_xlsx.json')
    allg = []
    for f in sorted(glob.glob(os.path.join(d, '*.xlsx'))):
        g = parse_file(f)
        sheets = sorted({x['sheet'] for x in g})
        print(f'{os.path.basename(f):32s} {len(g):4d} glasses  sheets={sheets}')
        allg += g
    with open(outp, 'w', encoding='utf-8') as fp:
        json.dump(allg, fp, ensure_ascii=False, separators=(',', ':'))
    print(f'共 {len(allg)} 条 -> {outp}')


if __name__ == '__main__':
    main()
