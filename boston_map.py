"""Render the hero map from map_data.json (baked from OpenStreetMap by map_fetch.py).

Map data (c) OpenStreetMap contributors, ODbL; credited in the site footer.
"""

import json
from pathlib import Path

DATA = json.loads((Path(__file__).parent / "map_data.json").read_text())

# Drawing order, bottom to top, and the CSS class for each layer.
LAYERS = [
    ("park", "m-park"), ("airport", "m-airport"), ("water", "m-sea"),
    ("trunk", "m-trunk"), ("motorway", "m-hwy"),
    ("cr", "m-line m-cr"), ("t_green", "m-line m-green"), ("t_orange", "m-line m-orange"),
    ("t_red", "m-line m-red"), ("t_blue", "m-line m-blue"),
]


def svg(place_label):
    v, home = DATA["view"], DATA["home"]
    o = [f'<svg class="map" viewBox="0 0 {v["W"]} {v["H"]}" preserveAspectRatio="xMidYMid slice" '
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
