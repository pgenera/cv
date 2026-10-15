"""Link-preview image (og:image): the site's hero map with name and headline.

A 1200x627 card, the size LinkedIn and most other sites expect. Colors come
from the day-map tokens in templates/site.html and type from its Overpass
font, so the card matches the site. The OpenStreetMap credit is in the PNG's
metadata (Copyright), not drawn on the image.

rsvg-convert renders the SVG. Pango can't load WOFF2, so the fonts are first
converted to TTF (fontTools) in a temporary fontconfig directory.

Usage: python3 og_image.py cv.yaml dist/og-image.png
"""

import html
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml
from fontTools.ttLib import TTFont
from PIL import Image
from PIL.PngImagePlugin import PngInfo

import boston_map

HERE = Path(__file__).parent
W, H = 1200, 627
DOT_X = 0.80  # where the dot sits across the card
CREDIT = "Map data © OpenStreetMap contributors, ODbL (https://www.openstreetmap.org/copyright)"

STYLE = """
.bg {{ fill: {land}; }}
.m-park {{ fill: {park}; }}
.m-sea {{ fill: {water}; }}
.m-airport {{ fill: {street-edge}; }}
.m-trunk {{ fill: none; stroke: {street}; stroke-width: 2.2; stroke-linecap: round; stroke-linejoin: round; }}
.m-hwy {{ fill: none; stroke: {hwy}; stroke-width: 3.2; stroke-linecap: round; stroke-linejoin: round; }}
.m-line {{ fill: none; stroke-width: 3; stroke-linecap: round; stroke-linejoin: round; }}
.m-cr {{ stroke: {t-cr}; stroke-width: 2; }}
.m-red {{ stroke: {t-red}; }}
.m-orange {{ stroke: {t-orange}; }}
.m-green {{ stroke: {t-green}; }}
.m-blue {{ stroke: {t-blue}; }}
.acc {{ fill: {blue}; fill-opacity: .16; stroke: {blue}; stroke-opacity: .35; stroke-width: 1; }}
.dot {{ fill: {blue}; stroke: #fff; stroke-width: 3; }}
.place, .halo {{ fill: {ink}; stroke: {label-halo}; stroke-linejoin: round; paint-order: stroke; }}
.place {{ font-family: Overpass; font-weight: 700; font-size: 15px; stroke-width: 5px; }}
.name {{ font-family: Overpass; font-weight: 800; font-size: 104px; letter-spacing: -1.5px; stroke-width: 16px; }}
.headline {{ font-family: Overpass; font-weight: 500; font-size: 38px; stroke-width: 10px; }}
.site {{ font-family: Overpass; font-weight: 600; font-size: 26px; fill: {blue}; stroke-width: 8px; }}
"""


def tokens():
    """The day-map custom properties from the site's first :root block."""
    css = (HERE / "templates" / "site.html").read_text()
    block = re.search(r":root \{(.*?)\}", css, re.S).group(1)
    return dict(re.findall(r"--([\w-]+):\s*([^;]+);", block))


def card_svg(cv):
    v, home = boston_map.DATA["view"], boston_map.DATA["home"]
    # Full map height; crop the width so the dot lands at DOT_X.
    vw = v["H"] * W / H
    x0 = min(max(home["x"] - DOT_X * vw, 0), v["W"] - vw)
    m = boston_map.svg(html.escape(cv["location"]))
    inner = m[m.index(">") + 1:m.rindex("</svg>")]
    inner = inner.replace('<g class="fix">', '<g class="fix" transform="scale(1.25)">')
    site = cv["site"].removeprefix("https://").rstrip("/")
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
        f"<style>{STYLE.format(**tokens())}</style>"
        f'<rect class="bg" width="{W}" height="{H}"/>'
        f'<svg width="{W}" height="{H}" viewBox="{x0:.1f} 0 {vw:.1f} {v["H"]}">{inner}</svg>'
        f'<text class="name halo" x="60" y="150">{html.escape(cv["name"])}</text>'
        f'<text class="headline halo" x="66" y="206">{html.escape(cv["headline"])}</text>'
        f'<text class="site halo" x="66" y="584">{html.escape(site)}</text>'
        "</svg>")


def main(cv_path, out):
    cv = yaml.safe_load(Path(cv_path).read_text())
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        for woff2 in (HERE / "templates" / "fonts").glob("*.woff2"):
            font = TTFont(woff2)
            font.flavor = None
            font.save(tmp / woff2.with_suffix(".ttf").name)
        (tmp / "fonts.conf").write_text(
            '<?xml version="1.0"?><!DOCTYPE fontconfig SYSTEM "fonts.dtd"><fontconfig>'
            '<include ignore_missing="yes">/etc/fonts/fonts.conf</include>'
            f"<dir>{tmp}</dir><cachedir>{tmp}/cache</cachedir></fontconfig>")
        (tmp / "card.svg").write_text(card_svg(cv))
        subprocess.run(["rsvg-convert", "-o", tmp / "card.png", tmp / "card.svg"], check=True,
                       env=dict(os.environ, FONTCONFIG_FILE=str(tmp / "fonts.conf")))
        card = Image.open(tmp / "card.png").convert("RGB")
    meta = PngInfo()
    meta.add_text("Title", cv["name"])
    meta.add_text("Author", cv["name"])
    meta.add_text("Description", f'{cv["name"]}, {cv["headline"]}. {cv["site"]}')
    meta.add_text("Copyright", CREDIT)
    card.save(out, optimize=True, pnginfo=meta)


if __name__ == "__main__":
    main(*sys.argv[1:3])
