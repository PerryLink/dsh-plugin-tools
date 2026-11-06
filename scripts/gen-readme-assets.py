#!/usr/bin/env python3
"""Generate README image assets for dsh-plugin-tools (docs/assets/).

Outputs (idempotent overwrite):
  dsh-plugin-tools-flow-light.svg / dsh-plugin-tools-flow-dark.svg
      Hero toolchain flow diagram. Two hand-written SVG files (vector — never
      rasterized to webp). Text inside is command-surface tokens only
      (dsh-tools list, dsh-tools install, npm i -g <pkg>, ...), so all five
      README languages share the same pair.

Run once:  python scripts/gen-readme-assets.py
Requires:  Pillow (pip install pillow)
"""
from __future__ import annotations

import os
import sys

from PIL import ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "assets")

# --- palette: PerryLink family (accent) + GitHub page backgrounds ----------
FAMILY = "#4B67B4"   # family accent (badges use labelColor #2B3245)
GREEN = {"light": "#16a34a", "dark": "#3fb950"}
SKIN = {
    "light": dict(bg="#ffffff", box="#f6f8fa", border="#d0d7de",
                  text="#1f2328", sub="#57606a"),
    "dark": dict(bg="#0d1117", box="#161b22", border="#30363d",
                 text="#f0f6fc", sub="#8b949e"),
}

# --- CJK font probe: localized hero variants must never render as tofu -----
# The shipped SVGs are token-only ASCII, but the probe keeps this script safe
# to extend with Chinese labels later (and matches the family asset skeleton).
FONT_CANDIDATES = [
    r"C:\Windows\Fonts\msyh.ttc",      # Microsoft YaHei
    r"C:\Windows\Fonts\simhei.ttf",    # SimHei
    r"C:\Windows\Fonts\Deng.ttf",      # DengXian
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/System/Library/Fonts/PingFang.ttc",
]
FONT_PATH = next((p for p in FONT_CANDIDATES if os.path.exists(p)), None)
if FONT_PATH is None:
    sys.exit("FATAL: no CJK font found (looked for msyh.ttc, simhei.ttf, "
             "Deng.ttf, Noto Sans CJK, PingFang). Refusing to render Chinese "
             "as tofu boxes; install one of the probed fonts and re-run.")


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_PATH, size)


# ---------------------------------------------------------------------------
# 1. Hero toolchain flow SVG (light + dark)
# ---------------------------------------------------------------------------
# Two lanes. Each node is (label, subtitle, accent): the label is a command
# token, the subtitle is a shorter token fragment. "<tool>" / "<pkg>" are
# escaped because the SVG is XML.
TOP_NODES = [
    ("dsh-tools list", "tools \u00b7 installed", "border"),
    ("dsh-tools doctor", "node \u00b7 npm \u00b7 dsh \u00b7 git", "border"),
    ("dsh-tools install", "&lt;tool&gt; \u2192 npm i -g", "family"),
    ("npm i -g &lt;pkg&gt;", "executed by you", "green"),
]
BOTTOM_NODES = [
    ("dsh-tools update", "\u2192 npm i -g @latest", "family"),
    ("npm i -g &lt;pkg&gt;@latest", "executed by you", "green"),
]


def accent_color(kind: str, skin: str) -> str:
    if kind == "green":
        return GREEN[skin]
    if kind == "family":
        return FAMILY
    return SKIN[skin]["border"]


def flow_svg(skin: str) -> str:
    s = SKIN[skin]
    w, h = 1200, 460
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" '
        f'aria-label="dsh-plugin-tools command flow">',
        '<title>dsh-plugin-tools command flow</title>',
        f'<rect width="{w}" height="{h}" rx="18" fill="{s["bg"]}"/>',
        f'<text x="60" y="62" fill="{s["text"]}" font-family="ui-sans-serif,'
        f'system-ui,sans-serif" font-size="30" font-weight="700">'
        f'dsh-plugin-tools</text>',
        f'<text x="60" y="94" fill="{s["sub"]}" font-family="ui-monospace,'
        f'monospace" font-size="16">dsh-tools list \u00b7 doctor \u00b7 '
        f'install \u00b7 update</text>',
        f'<line x1="60" y1="116" x2="1140" y2="116" stroke="{s["border"]}"/>',
    ]
    # top-right token badge
    parts.append(
        f'<rect x="1018" y="40" width="122" height="34" rx="17" '
        f'fill="{s["box"]}" stroke="{FAMILY}" stroke-width="2"/>')
    parts.append(
        f'<text x="1079" y="62" fill="{FAMILY}" text-anchor="middle" '
        f'font-family="ui-monospace,monospace" font-size="13" '
        f'font-weight="700">print-only</text>')

    # --- top lane: discover -> diagnose -> install guidance -> run ---------
    y0, nh, nw, gap = 150, 96, 240, 40
    for i, (label, sub, kind) in enumerate(TOP_NODES):
        x = 60 + i * (nw + gap)
        parts.append(
            f'<rect x="{x}" y="{y0}" width="{nw}" height="{nh}" rx="14" '
            f'fill="{s["box"]}" stroke="{accent_color(kind, skin)}" '
            f'stroke-width="2"/>')
        parts.append(
            f'<text x="{x + nw // 2}" y="{y0 + 40}" fill="{s["text"]}" '
            f'text-anchor="middle" font-family="ui-monospace,monospace" '
            f'font-size="16" font-weight="700">{label}</text>')
        parts.append(
            f'<text x="{x + nw // 2}" y="{y0 + 68}" fill="{s["sub"]}" '
            f'text-anchor="middle" font-family="ui-monospace,monospace" '
            f'font-size="12">{sub}</text>')
        if i < len(TOP_NODES) - 1:
            ax, ay = x + nw + 4, y0 + nh // 2
            parts.append(
                f'<path d="M{ax} {ay}h{gap - 12}" stroke="{s["sub"]}" '
                f'stroke-width="3"/>')
            parts.append(
                f'<path d="M{ax + gap - 14} {ay - 7}l10 7-10 7" fill="none" '
                f'stroke="{s["sub"]}" stroke-width="3" '
                f'stroke-linecap="round" stroke-linejoin="round"/>')

    # --- bottom lane: update guidance -> run -------------------------------
    by, bh, bw, bgap = 310, 84, 280, 60
    for i, (label, sub, kind) in enumerate(BOTTOM_NODES):
        x = 290 + i * (bw + bgap)
        parts.append(
            f'<rect x="{x}" y="{by}" width="{bw}" height="{bh}" rx="14" '
            f'fill="{s["box"]}" stroke="{accent_color(kind, skin)}" '
            f'stroke-width="2"/>')
        parts.append(
            f'<text x="{x + bw // 2}" y="{by + 34}" fill="{s["text"]}" '
            f'text-anchor="middle" font-family="ui-monospace,monospace" '
            f'font-size="16" font-weight="700">{label}</text>')
        parts.append(
            f'<text x="{x + bw // 2}" y="{by + 60}" fill="{s["sub"]}" '
            f'text-anchor="middle" font-family="ui-monospace,monospace" '
            f'font-size="12">{sub}</text>')
        if i < len(BOTTOM_NODES) - 1:
            ax, ay = x + bw + 4, by + bh // 2
            parts.append(
                f'<path d="M{ax} {ay}h{bgap - 12}" stroke="{s["sub"]}" '
                f'stroke-width="3"/>')
            parts.append(
                f'<path d="M{ax + bgap - 14} {ay - 7}l10 7-10 7" fill="none" '
                f'stroke="{s["sub"]}" stroke-width="3" '
                f'stroke-linecap="round" stroke-linejoin="round"/>')

    parts.append(
        f'<text x="60" y="432" fill="{s["sub"]}" font-family="ui-monospace,'
        f'monospace" font-size="13">--json \u00b7 schema '
        f'dsh-plugin-tools/1 \u00b7 no network \u00b7 no writes</text>')
    parts.append('</svg>')
    return "\n".join(parts) + "\n"


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    for skin in ("light", "dark"):
        with open(os.path.join(OUT, f"dsh-plugin-tools-flow-{skin}.svg"),
                  "w", encoding="utf-8", newline="\n") as fh:
            fh.write(flow_svg(skin))
    print("wrote 2 SVG assets to docs/assets/")


if __name__ == "__main__":
    main()
