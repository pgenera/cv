#!/usr/bin/env python3
"""Fetch and bake the hero map from OpenStreetMap into map_data.json.

Run rarely, by hand, to refresh the map. Builds only read map_data.json, so
they stay offline and dependency-free. This script needs shapely:

    python3 -m venv /tmp/mapvenv && /tmp/mapvenv/bin/pip install shapely
    /tmp/mapvenv/bin/python map_fetch.py

Map data (c) OpenStreetMap contributors, ODbL. The site credits it.
"""

import json
import sys
import time
import urllib.parse
import urllib.request
from math import cos, radians

import numpy as np

from shapely import STRtree, transform
from shapely.geometry import LineString, MultiLineString, Point, Polygon, box
from shapely.geometry.polygon import orient
from shapely.ops import linemerge, polygonize, unary_union

# Framing: Boston to Beverly. The SVG uses preserveAspectRatio="xMidYMid slice",
# so phones see the full height and a centered slice of the width.
W, H = 1440, 460
LON_CENTER = -70.985

# Area fetched from OSM. Kept fixed so the raw-response cache stays valid while
# the view below is adjusted; the view must stay inside it.
_FT, _FB = 42.610, 42.335
_K = H / (_FT - _FB)
_KX = _K * cos(radians((_FT + _FB) / 2))
PAD = 0.02
S, N = _FB - PAD, _FT + PAD
WEST, EAST = LON_CENTER - (W / 2) / _KX - PAD, LON_CENTER + (W / 2) / _KX + PAD
BBOX = f"{S},{WEST},{N},{EAST}"

# View: same scale as the fetch, nudged north so Beverly clears the top edge.
LAT_TOP = 42.625
LAT_BOTTOM = LAT_TOP - (_FT - _FB)
K, KX = _K, _KX

# Where the location dot goes: Montserrat commuter rail station, Beverly.
HOME = (42.5621, -70.8696)

OVERPASS = "https://overpass-api.de/api/interpreter"
UA = "pgenera-cv-map/1.0 (+https://github.com/pgenera/cv)"

TOL = 1.2          # simplification tolerance, px
MIN_WATER = 150     # px^2
MIN_PARK = 2000     # px^2


def xy(lon, lat):
    return (W / 2 + (lon - LON_CENTER) * KX, (LAT_TOP - lat) * K)


CACHE = None  # set to a directory to reuse raw responses while iterating


def overpass(q):
    if CACHE:
        import hashlib, os
        path = os.path.join(CACHE, hashlib.sha1(q.encode()).hexdigest() + ".json")
        if os.path.exists(path):
            return json.load(open(path))
    els = _overpass(q)
    if CACHE:
        json.dump(els, open(path, "w"))
    return els


def _overpass(q):
    body = urllib.parse.urlencode({"data": f"[out:json][timeout:180];{q}"}).encode()
    req = urllib.request.Request(OVERPASS, data=body, headers={"User-Agent": UA})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=240) as r:
                return json.load(r)["elements"]
        except Exception as e:  # rate limits, timeouts
            print(f"  overpass retry {attempt + 1}: {e}", file=sys.stderr)
            time.sleep(15 * (attempt + 1))
    sys.exit("overpass failed")


def way_line(el):
    return LineString([(p["lon"], p["lat"]) for p in el["geometry"]])


def area_polys(elements):
    """Closed ways and multipolygon relations -> shapely polygons (lon/lat)."""
    out = []
    for el in elements:
        if el["type"] == "way" and len(el.get("geometry", [])) >= 4:
            pts = [(p["lon"], p["lat"]) for p in el["geometry"]]
            if pts[0] == pts[-1]:
                poly = Polygon(pts)
                if poly.is_valid:
                    out.append(poly)
        elif el["type"] == "relation":
            outer, inner = [], []
            for m in el.get("members", []):
                if m["type"] == "way" and m.get("geometry"):
                    (inner if m.get("role") == "inner" else outer).append(
                        LineString([(p["lon"], p["lat"]) for p in m["geometry"]]))
            shells = list(polygonize(unary_union(outer))) if outer else []
            holes = unary_union(list(polygonize(unary_union(inner)))) if inner else None
            for s in shells:
                p = s.difference(holes) if holes is not None else s
                if not p.is_empty:
                    out.append(p)
    return out


def ocean(coast_ways):
    """Water faces of the bbox, using OSM's rule that land is left of the coastline."""
    lines = [way_line(w) for w in coast_ways if len(w.get("geometry", [])) >= 2]
    frame = box(WEST, S, EAST, N)
    noded = unary_union(lines + [frame.exterior])
    segs, dirs = [], []
    for ln in lines:
        c = list(ln.coords)
        for a, b in zip(c, c[1:]):
            segs.append(LineString([a, b]))
            dirs.append((b[0] - a[0], b[1] - a[1]))
    tree = STRtree(segs)
    water = []
    for face in polygonize(noded):
        if not frame.contains(face.representative_point()):
            continue
        ring = list(orient(face, 1.0).exterior.coords)  # counter-clockwise
        vote = 0
        for a, b in zip(ring, ring[1:]):
            mid = Point((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
            for i in tree.query(mid.buffer(1e-9)):
                if segs[i].distance(mid) < 1e-9:
                    d = dirs[i]
                    vote += 1 if (b[0] - a[0]) * d[0] + (b[1] - a[1]) * d[1] > 0 else -1
                    break
        if vote < 0:           # face is right of the coastline: water
            water.append(face)
    return unary_union(water)


def project(geom):
    return transform(geom, lambda c: np.column_stack(
        [W / 2 + (c[:, 0] - LON_CENTER) * KX, (LAT_TOP - c[:, 1]) * K]))


def d_poly(geom, min_area=0):
    geom = project(geom).simplify(TOL, preserve_topology=True)
    polys = [geom] if geom.geom_type == "Polygon" else list(getattr(geom, "geoms", []))
    parts = []
    for p in polys:
        if p.geom_type != "Polygon" or p.area < min_area:
            continue
        for ring in [p.exterior, *p.interiors]:
            c = list(ring.coords)
            parts.append("M" + "L".join(f"{x:.0f} {y:.0f}" for x, y in c[:-1]) + "Z")
    return "".join(parts)


def d_lines(lines):
    if not lines:
        return ""
    merged = linemerge(unary_union(lines))
    geom = project(merged).simplify(TOL, preserve_topology=False)
    geom = geom.intersection(box(-20, -20, W + 20, H + 20))
    ls = [geom] if geom.geom_type == "LineString" else list(getattr(geom, "geoms", []))
    parts = []
    for l in ls:
        if l.geom_type != "LineString" or l.length < 2:
            continue
        parts.append("M" + "L".join(f"{x:.0f} {y:.0f}" for x, y in l.coords))
    return "".join(parts)


def route_lines(rels):
    out = []
    for r in rels:
        for m in r.get("members", []):
            if m["type"] == "way" and m.get("geometry") and m.get("role", "") in ("", "forward", "backward"):
                out.append(LineString([(p["lon"], p["lat"]) for p in m["geometry"]]))
    return out


def main():
    global CACHE
    if len(sys.argv) > 1:
        CACHE = sys.argv[1]  # e.g. map_fetch.py /tmp/osm-cache
    print("coastline"); coast = overpass(f'way["natural"="coastline"]({BBOX});out geom;')
    time.sleep(3)
    print("water"); water_el = overpass(
        f'(way["natural"="water"]({BBOX});relation["natural"="water"]({BBOX});'
        f'way["waterway"="riverbank"]({BBOX}););out geom;')
    time.sleep(3)
    print("parks"); park_el = overpass(
        f'(way["leisure"~"^(park|nature_reserve)$"]({BBOX});'
        f'relation["leisure"~"^(park|nature_reserve)$"]({BBOX}););out geom;')
    time.sleep(3)
    print("airport"); airport_el = overpass(
        f'(way["aeroway"="aerodrome"]["iata"="BOS"]({BBOX});'
        f'relation["aeroway"="aerodrome"]["iata"="BOS"]({BBOX}););out geom;')
    time.sleep(3)
    print("roads"); roads = overpass(f'way["highway"~"^(motorway|trunk)$"]({BBOX});out geom;')
    time.sleep(3)
    print("transit"); transit = overpass(
        f'(relation["route"~"^(subway|light_rail)$"]["network"="MBTA"]({BBOX});'
        f'relation["route"="train"]["network"="MBTA"]["name"~"Newburyport|Rockport"]({BBOX}););out geom;')

    home = xy(HOME[1], HOME[0])

    sea = ocean(coast)
    lakes = unary_union([p for p in area_polys(water_el) if p.is_valid])
    parks = unary_union([p.buffer(0) for p in area_polys(park_el)])
    airport = unary_union([p.buffer(0) for p in area_polys(airport_el)])

    lines = {"t_red": [], "t_orange": [], "t_blue": [], "t_green": [], "cr": []}
    for r in transit:
        name = r.get("tags", {}).get("name", "")
        key = ("t_red" if "Red" in name or "Mattapan" in name else
               "t_orange" if "Orange" in name else
               "t_blue" if "Blue" in name else
               "t_green" if "Green" in name else
               "cr" if r["tags"].get("route") == "train" else None)
        if key:
            lines[key] += route_lines([r])

    layers = {
        "water": d_poly(unary_union([sea] + [p for p in getattr(lakes, "geoms", [lakes])
                                             if project(p).area >= MIN_WATER])),
        "park": d_poly(parks, MIN_PARK),
        "airport": d_poly(airport),
        "trunk": d_lines([way_line(w) for w in roads if w["tags"]["highway"] == "trunk"]),
        "motorway": d_lines([way_line(w) for w in roads if w["tags"]["highway"] == "motorway"]),
        **{k: d_lines(v) for k, v in lines.items()},
    }
    data = {
        "view": {"W": W, "H": H, "LAT_TOP": LAT_TOP, "LAT_BOTTOM": LAT_BOTTOM, "LON_CENTER": LON_CENTER},
        "home": {"name": "Montserrat station, Beverly", "x": round(home[0], 1), "y": round(home[1], 1)},
        "source": "OpenStreetMap contributors, ODbL",
        "fetched": time.strftime("%Y-%m-%d"),
        "layers": layers,
    }
    with open("map_data.json", "w") as f:
        json.dump(data, f, separators=(",", ":"))
    for k, v in layers.items():
        print(f"  {k:9s} {len(v):>7,d} chars")


if __name__ == "__main__":
    main()
