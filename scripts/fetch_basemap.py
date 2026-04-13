#!/usr/bin/env python3
"""
One-time script to download the Natural Earth 110m countries GeoJSON and
convert it to a flat SVG using an equirectangular projection.

Each country becomes a <path id="XX"> element keyed to its ISO A2 code.
The output is written to assets/world-110m.svg.

Usage:
    python scripts/fetch_basemap.py

Requirements: requests (already in requirements.txt)
"""

import json
import math
import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

try:
    import requests
except ImportError:
    print("ERROR: 'requests' not installed. Run: pip install requests")
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PATH = REPO_ROOT / "assets" / "world-110m.svg"
GEOJSON_URL = (
    "https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson"
)

# SVG canvas dimensions
SVG_WIDTH = 1800
SVG_HEIGHT = 900


def lon_to_x(lon):
    return (lon + 180.0) / 360.0 * SVG_WIDTH


def lat_to_y(lat):
    return (90.0 - lat) / 180.0 * SVG_HEIGHT


def simplify_ring(ring, tolerance=0.5):
    """Very simple point-removal: skip points within tolerance SVG units of previous point."""
    if len(ring) <= 3:
        return ring
    result = [ring[0]]
    for pt in ring[1:-1]:
        px, py = lon_to_x(result[-1][0]), lat_to_y(result[-1][1])
        cx, cy = lon_to_x(pt[0]), lat_to_y(pt[1])
        if abs(cx - px) > tolerance or abs(cy - py) > tolerance:
            result.append(pt)
    result.append(ring[-1])
    return result


def ring_to_path(ring):
    """Convert a GeoJSON coordinate ring to an SVG path 'd' string."""
    ring = simplify_ring(ring)
    parts = []
    for i, (lon, lat) in enumerate(ring):
        x = lon_to_x(lon)
        y = lat_to_y(lat)
        cmd = "M" if i == 0 else "L"
        parts.append(f"{cmd}{x:.1f},{y:.1f}")
    parts.append("Z")
    return "".join(parts)


def geometry_to_path(geometry):
    """Convert a GeoJSON geometry (Polygon or MultiPolygon) to a single SVG path 'd'."""
    geom_type = geometry["type"]
    coords = geometry["coordinates"]
    parts = []

    if geom_type == "Polygon":
        for ring in coords:
            parts.append(ring_to_path(ring))
    elif geom_type == "MultiPolygon":
        for polygon in coords:
            for ring in polygon:
                parts.append(ring_to_path(ring))
    else:
        return None

    return " ".join(parts)


def fetch_geojson():
    print(f"Downloading GeoJSON from {GEOJSON_URL} ...")
    resp = requests.get(GEOJSON_URL, timeout=30)
    resp.raise_for_status()
    print(f"Downloaded {len(resp.content):,} bytes.")
    return resp.json()


def build_svg(geojson):
    ET.register_namespace("", "http://www.w3.org/2000/svg")
    svg = ET.Element(
        "svg",
        {
            "xmlns": "http://www.w3.org/2000/svg",
            "viewBox": f"0 0 {SVG_WIDTH} {SVG_HEIGHT}",
            "width": str(SVG_WIDTH),
            "height": str(SVG_HEIGHT),
            "style": "background:#1a1a2e",
        },
    )

    # Background rect
    ET.SubElement(
        svg,
        "rect",
        {
            "width": str(SVG_WIDTH),
            "height": str(SVG_HEIGHT),
            "fill": "#1a1a2e",
            "id": "_ocean",
        },
    )

    skipped = 0
    added = 0

    for feature in geojson.get("features", []):
        props = feature.get("properties", {})
        # Try multiple property names for ISO A2 code
        iso_a2 = (
            props.get("ISO_A2")
            or props.get("iso_a2")
            or props.get("ISO3166-1-Alpha-2")
            or props.get("ADM0_A3_US")  # fallback
        )
        name = props.get("ADMIN") or props.get("name") or props.get("NAME") or "Unknown"

        if not iso_a2 or iso_a2 == "-99" or len(iso_a2) != 2:
            skipped += 1
            continue

        iso_a2 = iso_a2.upper()
        geom = feature.get("geometry")
        if not geom:
            skipped += 1
            continue

        d = geometry_to_path(geom)
        if not d:
            skipped += 1
            continue

        path_el = ET.SubElement(
            svg,
            "path",
            {
                "id": iso_a2,
                "d": d,
                "fill": "#cccccc",  # default: no data
                "stroke": "#ffffff",
                "stroke-width": "0.5",
                "data-name": name,
            },
        )
        title = ET.SubElement(path_el, "title")
        title.text = name
        added += 1

    print(f"Added {added} country paths. Skipped {skipped} features.")
    return svg


def main():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    if OUTPUT_PATH.exists():
        print(f"Basemap already exists at {OUTPUT_PATH}")
        ans = input("Re-download and overwrite? [y/N] ").strip().lower()
        if ans != "y":
            print("Skipping download.")
            return

    geojson = fetch_geojson()
    svg = build_svg(geojson)

    tree = ET.ElementTree(svg)
    ET.indent(tree, space="  ")
    with open(OUTPUT_PATH, "wb") as f:
        tree.write(f, encoding="utf-8", xml_declaration=True)

    print(f"Basemap written to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
