"""Render the hero map from map_data.json (baked from OpenStreetMap by map_fetch.py).

Map data (c) OpenStreetMap contributors, ODbL; credited in the site footer.
"""

import json
from pathlib import Path

# Git-ignored: a derived OSM database is never committed. Rebuild it with map_fetch.py.
DATA = json.loads((Path(__file__).parent / "osm" / "map_data.json").read_text())

# Drawing order, bottom to top, and the CSS class for each layer.
LAYERS = [
    ("park", "m-park"), ("airport", "m-airport"), ("water", "m-sea"),
    ("trunk", "m-trunk"), ("motorway", "m-hwy"),
    ("cr", "m-line m-cr"), ("t_green", "m-line m-green"), ("t_orange", "m-line m-orange"),
    ("t_red", "m-line m-red"), ("t_blue", "m-line m-blue"),
]


def svg(place_label):
    v, home = DATA["view"], DATA["home"]
    # xMidYMin: if a wide, short window forces a crop, it comes off the bottom so
    # the dot, near the top, stays visible.
    o = [f'<svg class="map" viewBox="0 0 {v["W"]} {v["H"]}" preserveAspectRatio="xMidYMin slice" '
         f'style="--focus-x: {DATA.get("focus_x", 50)}%; --map-ratio: {v["W"]} / {v["H"]}" '
         'aria-hidden="true" focusable="false">']
    for key, cls in LAYERS:
        d = DATA["layers"].get(key)
        if d:
            o.append(f'<path class="{cls}" fill-rule="evenodd" d="{d}"/>')
    o.append(f'<g transform="translate({home["x"]} {home["y"]})"><g class="fix">'
             '<circle class="acc" r="26"/><circle class="dot" r="7.5"/>'
             f'<text class="place" x="15" y="5">{place_label}</text></g></g>')
    o.append("</svg>")
    return "".join(o)
