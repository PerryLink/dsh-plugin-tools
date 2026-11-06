#!/usr/bin/env python3
"""README visuals for dsh-plugin-tools — v5 (1440x576 hero + 1100x660 flow).

Everything below is read out of the shipped code, not invented:

  src/tools.js  KNOWN[9] holds { id, pkg, bin, role }. Two fields are nullable
                on purpose: `standards` has no npm package (pkg: null) and
                `primer` / `test-drive` declare no executable (bin: null).
  src/tools.js  hasCommand(bin) runs `where` (win32) or `which` with a 3000 ms
                timeout; a null bin short-circuits to null, which list() prints
                as `unknown`.
                list()    -> all nine rows x probe, text table or --json
                doctor()  -> four fixed probes (node >=20, npm, dsh, git);
                             pass / pass-with-warnings / fail; exit 1 on fail
                install() -> one row matched by id or pkg; pkg null -> exit 1;
                             otherwise prints `npm install -g <pkg>` and
                             `executed: false`
                update()  -> the eight rows with a pkg, `@latest`, executed: false
  src/tools.js  parse() is strict: unknown option, extra argument or unknown
                subcommand -> error + usage, exit 1.
  package.json  zero runtime dependencies, one bin (`dsh-tools`), no config.

  hero  (Pillow, zh/en x light/dark) — a catalog sheet. The right half is a
        3x3 grid of the nine KNOWN ids; every cell carries two capability chips
        (pkg / bin) that are filled only when that field is declared, so the
        hollow chips of primer, test-drive and standards show the capability
        gap at a glance. Beneath it sits the only output that looks like an
        action — the printed install command — stamped `executed: false`, and
        then a dashed boundary: the commands stop at stdout.

  flow  (hand-written SVG, light/dark) — a capability matrix, not a row of
        boxes: nine rows x (id / pkg / bin / installed). The `installed` column
        can only hold what the probe can return — `yes / no`, or `unknown` when
        bin is null. Beside it are the four command exits that read those rows
        (list reads all nine, install one, update the eight with a pkg; doctor
        reads KNOWN not at all) with their real exit codes, and one print-only
        boundary rail that every exit drains into.

Labels are command tokens plus short Chinese notes, so the light/dark SVG pair
is shared by all five README languages; only the hero carries prose (zh / en).

Outputs (idempotent overwrite):
  docs/assets/dsh-plugin-tools-hero-{zh,en}-{light,dark}.webp
  docs/assets/dsh-plugin-tools-flow-v5-{light,dark}.svg

Run:  python scripts/gen-readme-assets.py
Needs: Pillow, plus msyh.ttc / msyhbd.ttc / consola.ttf (a CJK font is
       mandatory: Chinese must never render as tofu boxes).
"""
from __future__ import annotations

import os
from html import escape

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'docs', 'assets')

FONT_CJK = r'C:\Windows\Fonts\msyh.ttc'
FONT_CJK_BOLD = r'C:\Windows\Fonts\msyhbd.ttc'
FONT_MONO = r'C:\Windows\Fonts\consola.ttf'
for _p in (FONT_CJK, FONT_CJK_BOLD, FONT_MONO):
    if not os.path.exists(_p):
        raise SystemExit(f'FATAL: font missing: {_p}  (CJK must never render '
                         f'as tofu boxes; install the font and re-run)')

KIND = {'cjk': FONT_CJK, 'cjk_bold': FONT_CJK_BOLD, 'mono': FONT_MONO}

# --- palette: family accent + the two mandated page gradients ---------------
SKIN = {
    'light': dict(bg_from='#f9f6fd', bg_to='#e4eaf8', card='#ffffff',
                  card_edge='#e4e1ee', zone='#f7f5fc', text='#141419',
                  sub='#4d5261', faint='#8f94a4', accent='#4B67B4',
                  accent2='#6d80c4', ok='#16a34a', warn='#bc4c00',
                  fail='#cf222e', pill='#ece7f9', grid='#e7e4f0',
                  shadow=(32, 26, 64), flood='#a9b3d6'),
    'dark': dict(bg_from='#131a2a', bg_to='#0c1016', card='#1b2231',
                 card_edge='#2e374b', zone='#202839', text='#f0f3f9',
                 sub='#a8b1c4', faint='#737b8d', accent='#8496f5',
                 accent2='#a9b7f8', ok='#3fb950', warn='#d29922',
                 fail='#f85149', pill='#242d42', grid='#2a3348',
                 shadow=(0, 0, 0), flood='#000000'),
}

# id, pkg, bin — exactly src/tools.js KNOWN (order preserved).
CATALOG = [
    ('start', 'dsh-plugin-start', 'dsh-start'),
    ('ready', 'dsh-plugin-ready', 'dsh-ready'),
    ('dev', 'dsh-plugin-dev', 'dsh-dev'),
    ('tools', 'dsh-plugin-tools', 'dsh-tools'),
    ('primer', 'dsh-primer', None),
    ('clinic', 'dsh-clinic', 'dsh-clinic'),
    ('test-drive', 'dsh-test-drive', None),
    ('codemod', 'dsh-codemod', 'dsh-codemod'),
    ('standards', None, None),
]


def font(size: float, kind: str = 'cjk') -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(KIND[kind], int(round(size)))


def hx(s: str) -> tuple[int, int, int]:
    s = s.lstrip('#')
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def gradient(w: int, h: int, c1: str, c2: str) -> Image.Image:
    img = Image.new('RGB', (w, h))
    d = ImageDraw.Draw(img)
    for y in range(h):
        t = 0.2 * (y / h) + 0.8 * (y / h) ** 1.5
        d.line([(0, y), (w, y)],
               fill=tuple(int(p + (q - p) * t)
                          for p, q in zip(hx(c1), hx(c2))))
    return img


def glow(img: Image.Image, cx: int, cy: int, r: int, color,
         alpha: int = 24) -> Image.Image:
    layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for i in range(9, 0, -1):
        rr = r * i / 9
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr],
                  fill=color + (int(alpha * (1 - i / 10)),))
    return Image.alpha_composite(img.convert('RGBA'), layer).convert('RGB')


def card(img: Image.Image, box, skin: dict, radius: int = 20, shadow: int = 14,
         fill: str | None = None, edge: str | None = None,
         width: int = 2) -> Image.Image:
    """Rounded card with a soft offset shadow."""
    x0, y0, x1, y1 = box
    sh = Image.new('RGBA', img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    for i in range(shadow, 0, -2):
        sd.rounded_rectangle([x0 - i // 4, y0 + i // 2, x1 + i // 4, y1 + i],
                             radius=radius + i // 4,
                             fill=skin['shadow'] + (int(6 * (1 - i / shadow)),))
    base = Image.alpha_composite(img.convert('RGBA'),
                                 sh.filter(ImageFilter.GaussianBlur(10)))
    d = ImageDraw.Draw(base)
    d.rounded_rectangle(box, radius=radius, fill=hx(fill or skin['card']),
                        outline=hx(edge or skin['card_edge']), width=width)
    return base.convert('RGB')


def pill(img: Image.Image, xy, text: str, skin: dict, size: int = 17,
         fg: str | None = None, bg: str | None = None) -> Image.Image:
    d = ImageDraw.Draw(img)
    f = font(size, 'cjk')
    tw = d.textlength(text, font=f)
    x, y = xy
    h = size + 16
    d.rounded_rectangle([x, y, x + tw + 28, y + h], radius=h // 2,
                        fill=hx(bg or skin['pill']))
    d.text((x + 14, y + 7), text, font=f, fill=hx(fg or skin['accent']))
    return img


def assure(d, text: str, f, limit: float, label: str) -> None:
    w = d.textlength(text, font=f)
    if w > limit:
        raise SystemExit(f'FATAL: {label} overflows ({w:.0f}px > {limit:.0f}px):'
                         f' {text!r}')


# ---------------------------------------------------------------------------
# hero copy — only prose is localised; the right-hand labels are tokens
# ---------------------------------------------------------------------------
HERO = {
    'zh': dict(
        kicker='DSH 插件工具链 · 目录与体检',
        value=['九个工具，一张清单', '谁装了、缺什么、敲哪条'],
        sub=['list 列出九个工具的 pkg/bin/职责与本机状态；',
             'doctor 只探 Node、npm、dsh、git 四项前提；',
             'install 与 update 只打印命令，绝不执行。'],
        meta='无配置文件 · 零依赖 · 零网络 · Node ≥24.9.0 · exit 0/1',
        foot='Apache-2.0 · 社区工具，与 DeepSeek 官方无关',
        note='实心 = 已声明 · 空心 = 缺省 · 缺 bin → unknown',
        caption='命令只写到 stdout：npm 从不被调用 · 不联网 · 不写文件',
    ),
    'en': dict(
        kicker='DSH plugin toolchain · catalog & preflight',
        value=['Nine tools, one list', 'installed, missing, next command'],
        sub=["list: nine tools' pkg / bin / role and install state;",
             'doctor: Node, npm, dsh, git — four local probes;',
             'install / update: print the command, never run it.'],
        meta='no config · 0 deps · 0 network · Node >=24.9.0 · exit 0/1',
        foot='Apache-2.0 · community tool, not affiliated with DeepSeek',
        note='filled = declared · hollow = absent · no bin = unknown',
        caption='commands stop at stdout: npm is never called — no network, no writes',
    ),
}


def hero(lang: str, skin: str) -> Image.Image:
    s = SKIN[skin]
    c = HERO[lang]
    W, H = 1440, 576
    img = gradient(W, H, s['bg_from'], s['bg_to'])
    img = glow(img, 1210, 60, 360, hx(s['accent']),
              20 if skin == 'light' else 34)
    img = glow(img, 120, 560, 280, hx(s['accent']),
              8 if skin == 'light' else 16)
    m = 60

    # ---- left column: kicker / title / two value lines / sub / meta / foot --
    img = pill(img, (m, 46), c['kicker'], s, size=17)
    d = ImageDraw.Draw(img)

    title_f = font(80, 'mono')
    assure(d, 'dsh-plugin-tools', title_f, 712, 'title')
    d.text((m - 2, 94), 'dsh-plugin-tools', font=title_f, fill=hx(s['text']))

    value_f = font(38, 'cjk_bold')
    for i, line in enumerate(c['value']):
        assure(d, line, value_f, 700, f'value[{i}]')
        d.text((m, 220 + i * 58), line, font=value_f, fill=hx(s['text']))

    sub_f = font(25, 'cjk')
    for i, line in enumerate(c['sub']):
        assure(d, line, sub_f, 700, f'sub[{i}]')
        d.text((m + 1, 348 + i * 34), line, font=sub_f, fill=hx(s['sub']))

    d.text((m + 1, 464), c['meta'], font=font(20, 'cjk'), fill=hx(s['faint']))
    d.line([m + 1, 498, 640, 498], fill=hx(s['grid']), width=2)
    d.text((m + 1, 512), c['foot'], font=font(18, 'cjk'), fill=hx(s['faint']))

    # ---- right column: the nine-tool catalog grid -------------------------
    RX = 800
    img = card(img, (RX, 58, 1390, 386), s, radius=22)
    d = ImageDraw.Draw(img)
    d.text((RX + 24, 72), 'KNOWN · 9', font=font(20, 'cjk_bold'),
           fill=hx(s['accent']))
    d.text((1390 - 24, 76), 'src/tools.js', font=font(17, 'mono'),
           fill=hx(s['faint']), anchor='ra')
    d.line([RX + 24, 106, 1390 - 24, 106], fill=hx(s['grid']), width=1)

    cw, ch, gap = 170, 66, 13
    gx, gy = RX + 24, 120
    for i, (tid, pkg, bin_) in enumerate(CATALOG):
        col, row = i % 3, i // 3
        x = gx + col * (cw + gap)
        y = gy + row * (ch + 10)
        d.rounded_rectangle([x, y, x + cw, y + ch], radius=14,
                            fill=hx(s['zone']), outline=hx(s['card_edge']),
                            width=1)
        d.text((x + 14, y + 6), tid, font=font(20, 'mono'),
               fill=hx(s['text']))
        # capability chips: filled when the field is declared, hollow if not
        chip_f = font(15, 'mono')
        for j, (label, declared) in enumerate((('pkg', pkg is not None),
                                               ('bin', bin_ is not None))):
            cx = x + 14 + j * 51
            cy = y + 35
            wdt = int(d.textlength(label, font=chip_f)) + 20
            if declared:
                d.rounded_rectangle([cx, cy, cx + wdt, cy + 21], radius=11,
                                    fill=hx(s['pill']))
                d.text((cx + 10, cy + 2), label, font=chip_f,
                       fill=hx(s['accent']))
            else:
                d.rounded_rectangle([cx, cy, cx + wdt, cy + 21], radius=11,
                                    outline=hx(s['faint']), width=1)
                d.text((cx + 10, cy + 2), label, font=chip_f,
                       fill=hx(s['faint']))

    assure(d, c['note'], font(16, 'cjk'), 554, 'note')
    d.text((RX + 24, 348), c['note'], font=font(16, 'cjk'), fill=hx(s['faint']))

    # ---- the only action-shaped output: a printed command, stamped ---------
    img = card(img, (RX, 400, 1390, 502), s, radius=20)
    d = ImageDraw.Draw(img)
    d.text((RX + 24, 412), '$ dsh-tools install ready', font=font(18, 'mono'),
           fill=hx(s['text']))
    d.text((RX + 24, 438), 'npm install -g dsh-plugin-ready',
           font=font(18, 'mono'), fill=hx(s['accent']))
    d.text((RX + 24, 466), '(not executed by dsh-tools; run it yourself)',
           font=font(15, 'mono'), fill=hx(s['faint']))

    stamp = 'executed: false'
    d.rounded_rectangle([1390 - 24 - 148, 410, 1390 - 24, 438], radius=14,
                        fill=hx(s['pill']))
    d.text((1390 - 24 - 74, 424), stamp, font=font(15, 'mono'),
           fill=hx(s['accent']), anchor='mm')

    # ---- print boundary: a dashed line, nothing crosses it -----------------
    x = RX
    while x + 10 <= 1390:
        d.line([x, 522, x + 10, 522], fill=hx(s['accent']), width=2)
        x += 19
    d.text((RX + 24, 532), c['caption'], font=font(16, 'cjk'),
           fill=hx(s['accent']))
    return img


# ---------------------------------------------------------------------------
# flow: capability matrix -> four command exits -> one print-only boundary
# ---------------------------------------------------------------------------
SANS = ("'Segoe UI','Microsoft YaHei','PingFang SC','Noto Sans CJK SC',"
        "system-ui,sans-serif")
MONO = "'Consolas','SFMono-Regular',ui-monospace,monospace"


def est(text: str, size: float, mono: bool = False) -> float:
    w = 0.0
    for ch in text:
        if ord(ch) >= 0x2E80:          # CJK ideographs + full-width punct
            w += size
        elif ch in '→←↑↓⊣—·≥≤':
            w += size * 0.8
        else:
            w += size * (0.55 if mono else 0.5)
    return w


def guard(text, size, limit, mono, label):
    w = est(text, size, mono)
    if w > limit:
        raise SystemExit(f'FATAL: flow {label} overflows ({w:.0f}px > '
                         f'{limit:.0f}px): {text!r}')


def svg_text(x, y, s, size, fill, weight='400', anchor='start', mono=False):
    fam = MONO if mono else SANS
    return (f'<text x="{x}" y="{y}" font-family="{fam}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}" '
            f'text-anchor="{anchor}">{escape(s)}</text>')


def flow_svg(skin: str) -> str:
    s = SKIN[skin]
    W, H = 1100, 660
    p: list[str] = []
    add = p.append

    add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" role="img" '
        f'aria-label="dsh-plugin-tools structure: a nine-row capability matrix '
        f'beside four command exits, all ending at a print-only boundary">')
    add('<title>dsh-plugin-tools — KNOWN[9] capability matrix and '
        'print-only boundary</title>')
    add('<defs>')
    add('<linearGradient id="bg" x1="0" y1="0" x2="0.35" y2="1">'
        f'<stop offset="0" stop-color="{s["bg_from"]}"/>'
        f'<stop offset="1" stop-color="{s["bg_to"]}"/></linearGradient>')
    op = '0.10' if skin == 'light' else '0.45'
    add(f'<filter id="sh" x="-20%" y="-20%" width="140%" height="140%">'
        f'<feDropShadow dx="0" dy="6" stdDeviation="9" flood-color="'
        f'{s["flood"]}" flood-opacity="{op}"/></filter>')
    add('</defs>')
    add(f'<rect width="{W}" height="{H}" rx="18" fill="url(#bg)"/>')
    add('<g>')

    # ---- header ------------------------------------------------------------
    add(svg_text(48, 62, 'dsh-tools · src/tools.js · KNOWN[9] · parse(argv) · '
                         'hasCommand()', 14, s['faint'], mono=True))
    add(svg_text(48, 102, '九个工具的能力矩阵，四条命令的打印出口', 24, s['text'],
                 '700'))
    sub = ('pkg / bin 是否声明决定行为：无 pkg 不可安装，无 bin 只能 unknown；'
           '所有出口都停在打印边界。')
    guard(sub, 15, 780, False, 'sub')
    add(svg_text(48, 132, sub, 15, s['sub']))

    # schema chip (the fixed --json contract) + argv note
    add(f'<rect x="846" y="44" width="218" height="36" rx="18" '
        f'fill="{s["card"]}" stroke="{s["card_edge"]}" stroke-width="1.5"/>')
    add(svg_text(955, 68, 'schema dsh-plugin-tools/1', 14, s['accent'],
                 '700', 'middle', mono=True))
    add(svg_text(1064, 102, 'argv → 4 verbs + --json', 14, s['faint'],
                 anchor='end'))

    # ---- capability matrix -------------------------------------------------
    add(f'<rect x="36" y="150" width="664" height="434" rx="20" '
        f'fill="{s["card"]}" stroke="{s["card_edge"]}" stroke-width="1.5" '
        f'filter="url(#sh)"/>')
    add(svg_text(56, 176, 'KNOWN[9] · pkg / bin 决定行为', 14, s['accent'], '700'))
    add(svg_text(680, 176, 'role 只进输出', 14, s['faint'], anchor='end'))

    for x, label, anchor in ((58, 'id', 'start'), (170, 'pkg', 'start'),
                             (396, 'bin', 'start'), (560, 'installed', 'start')):
        add(svg_text(x, 206, label, 15, s['faint'], '600', anchor))
    add(f'<line x1="48" y1="216" x2="688" y2="216" stroke="{s["grid"]}" '
        f'stroke-width="1.5"/>')

    for i, (tid, pkg, bin_) in enumerate(CATALOG):
        top = 222 + i * 34
        if i % 2 == 0:
            add(f'<rect x="48" y="{top}" width="640" height="34" rx="8" '
                f'fill="{s["zone"]}"/>')
        base = top + 23
        add(svg_text(58, base, tid, 17, s['text'], '700', mono=True))
        add(svg_text(170, base, pkg or '—', 17,
                     s['sub'] if pkg else s['faint'], mono=True))
        add(svg_text(396, base, bin_ or '—', 17,
                     s['sub'] if bin_ else s['faint'], mono=True))
        if bin_:
            add(svg_text(560, base, 'yes / no', 17, s['sub'], mono=True))
        else:
            add(svg_text(560, base, 'unknown', 17, s['faint'], mono=True))

    n1 = 'installed = hasCommand(bin) → where|which（3s）：yes / no，无 bin → unknown'
    n2 = 'role 只进 stdout；无 pkg（standards）→ install 拒绝、update 跳过'
    guard(n1, 14, 640, False, 'footnote1')
    guard(n2, 14, 640, False, 'footnote2')
    add(svg_text(56, 552, n1, 14, s['faint']))
    add(svg_text(56, 572, n2, 14, s['faint']))

    # ---- four command exits ------------------------------------------------
    add(f'<rect x="724" y="150" width="340" height="434" rx="20" '
        f'fill="{s["card"]}" stroke="{s["card_edge"]}" stroke-width="1.5" '
        f'filter="url(#sh)"/>')
    add(svg_text(744, 176, '四条命令 · 四种出口', 14, s['accent'], '700'))

    EXITS = [
        ('list', '全量 9 行 + 探测', 'text 表格 · --json', '0'),
        ('doctor', '不读 KNOWN · 4 项探测', 'pass / pass-with-warnings / fail',
         '0 | 1'),
        ('install', 'id 或 pkg 命中 1 行', 'npm install -g <pkg>', '0 | 1'),
        ('update', '有 pkg 的 8 行', 'npm install -g <pkg>@latest', '0'),
    ]
    for i, (verb, what, out, code) in enumerate(EXITS):
        top = 196 + i * 92
        add(svg_text(744, top + 22, verb, 19, s['accent'], '700', mono=True))
        add(svg_text(1044, top + 22, f'exit {code}', 14,
                     s['sub'] if code == '0' else s['warn'], '600', 'end',
                     mono=True))
        add(svg_text(744, top + 50, what, 15, s['sub']))
        add(svg_text(744, top + 72, out, 14,
                     s['accent2'] if i in (2, 3) else s['faint'], mono=True))
        if i < 3:
            add(f'<line x1="744" y1="{top + 88}" x2="1044" y2="{top + 88}" '
                f'stroke="{s["grid"]}" stroke-width="1"/>')

    # ---- both halves drain into the print boundary ------------------------
    for x in (368, 894):
        add(f'<path d="M{x} 586V591" stroke="{s["accent"]}" stroke-width="2" '
            f'stroke-dasharray="4 3"/>')
        add(f'<path d="M{x - 5} 590L{x} 597L{x + 5} 590" fill="none" '
            f'stroke="{s["accent"]}" stroke-width="2" stroke-linecap="round" '
            f'stroke-linejoin="round"/>')

    add(f'<rect x="36" y="598" width="1028" height="34" rx="17" '
        f'fill="{s["pill"]}" stroke="{s["accent"]}" stroke-width="1.5" '
        f'stroke-dasharray="8 5"/>')
    add(f'<rect x="48" y="604" width="93" height="22" rx="11" '
        f'fill="{s["accent"]}"/>')
    add(svg_text(94.5, 619, 'print only', 14,
                 '#ffffff' if skin == 'light' else '#131a2a', '700', 'middle',
                 mono=True))
    rail = '输出只有文本 / JSON · executed 恒为 false'
    guard(rail, 15, 380, False, 'rail')
    add(svg_text(154, 620, rail, 15, s['sub']))
    add(svg_text(1052, 620, 'npm 从不被调用 · 不联网 · 不写文件', 14, s['sub'],
                 anchor='end'))

    # ---- footer ------------------------------------------------------------
    add(svg_text(48, 648, '未知子命令 / 未知选项 / 多余参数 → exit 1 并打印用法',
                 14, s['faint']))
    add(svg_text(1052, 648, '无配置文件 · 零运行时依赖 · Node ≥24.9.0', 14,
                 s['faint'], anchor='end'))
    add('</g></svg>')
    return '\n'.join(p) + '\n'


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    for skin in ('light', 'dark'):
        svg = flow_svg(skin)
        path = os.path.join(OUT, f'dsh-plugin-tools-flow-v5-{skin}.svg')
        with open(path, 'w', encoding='utf-8', newline='\n') as fh:
            fh.write(svg)
    for lang in ('zh', 'en'):
        for skin in ('light', 'dark'):
            img = hero(lang, skin)
            path = os.path.join(
                OUT, f'dsh-plugin-tools-hero-{lang}-{skin}.webp')
            img.save(path, 'WEBP', quality=92, method=6)
    print('wrote 4 webp + 2 svg to docs/assets/')


if __name__ == '__main__':
    main()
