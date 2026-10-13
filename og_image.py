"""Link-preview image (og:image) from the top of the CV's first page.

Renders page 1, keeps everything above the Experience heading (name, contact
line, Summary, Technical), and centers it on a 1200x627 white card, the size
LinkedIn and most other sites expect.

Usage: python3 og_image.py dist/phil_genera_cv.pdf dist/og-image.png
"""

import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

W, H, PAD = 1200, 627, 36
DARK = 128  # grayscale threshold for "ink"


def ink_rows(img):
    """Per row, the number of dark pixels."""
    px = img.load()
    return [sum(px[x, y] < DARK for x in range(img.width)) for y in range(img.height)]


def main(pdf, out):
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp) / "p"
        subprocess.run(["pdftoppm", "-png", "-r", "300", "-f", "1", "-l", "1",
                        "-singlefile", pdf, str(base)], check=True)
        page = Image.open(f"{base}.png").convert("L")

    rows = ink_rows(page)
    # Section rules are rows inked across most of the text block.
    widest = max(rows)
    rules = [y for y, n in enumerate(rows) if n > 0.8 * widest]
    starts = [y for i, y in enumerate(rules) if i == 0 or y - rules[i - 1] > 1]
    if len(starts) < 3:
        sys.exit("og_image: expected Summary, Technical and Experience rules")
    # Walk up from the Experience rule through its heading to the blank gap.
    y = starts[2] - 1
    while y > 0 and rows[y] == 0:
        y -= 1
    while y > 0 and rows[y] > 0:
        y -= 1
    bottom = y

    top_part = page.crop((0, 0, page.width, bottom))
    left, top, right, low = Image.eval(top_part, lambda v: 255 - v).getbbox()
    content = top_part.crop((left, top, right, low))

    scale = min((W - 2 * PAD) / content.width, (H - 2 * PAD) / content.height)
    size = (round(content.width * scale), round(content.height * scale))
    content = content.resize(size, Image.LANCZOS)
    card = Image.new("L", (W, H), 255)
    card.paste(content, ((W - size[0]) // 2, (H - size[1]) // 2))
    card.save(out, optimize=True)


if __name__ == "__main__":
    main(*sys.argv[1:3])
