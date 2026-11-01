#!/usr/bin/env python3
"""FEDME pilot: bounded tile scan in Jaén, deduplicate by official route id.

Only metadata and official links are stored; no route geometries are inferred.
"""
import argparse
import json
import math
import pathlib
import time
import urllib.error
import urllib.request

BASE = "https://vt-fedme.idee.es/vt.senderogr,vt.senderopr,vt.senderosl"
# Jaén province approximate bbox (west,south,east,north); deliberately pilot-only.
REGIONS = {"jaen": (-4.30, 37.38, -2.42, 38.58)}
ATTRIBUTION = "FEDME / CNIG · CC BY 4.0"


def tile_xy(lon, lat, z):
    n = 2 ** z
    x = int((lon + 180) / 360 * n)
    y = int((1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n)
    return max(0, min(n - 1, x)), max(0, min(n - 1, y))


def collect(region, zoom, max_tiles, delay):
    import mapbox_vector_tile
    west, south, east, north = REGIONS[region]
    x0, y0 = tile_xy(west, north, zoom)
    x1, y1 = tile_xy(east, south, zoom)
    tiles = [(x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)]
    if len(tiles) > max_tiles:
        raise ValueError(f"{len(tiles)} teselas exceden límite {max_tiles}; reducir zoom o zona")
    routes = {}
    failures = []
    for i, (x, y) in enumerate(tiles, 1):
        url = f"{BASE}/{zoom}/{x}/{y}.pbf"
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "SUMMIT-FEDME-pilot/0.1 (bounded research)"})
            with urllib.request.urlopen(request, timeout=20) as response:
                payload = response.read(1_500_001)
            if len(payload) > 1_500_000:
                raise ValueError("tesela demasiado grande")
            if payload:
                decoded = mapbox_vector_tile.decode(payload)
                for layer, obj in decoded.items():
                    if layer not in ("vt.senderogr", "vt.senderopr", "vt.senderosl"):
                        continue
                    for feature in obj.get("features", []):
                        p = feature.get("properties", {})
                        rid = str(p.get("id") or "").strip()
                        name = str(p.get("nombre") or "").strip()
                        if not rid or not name:
                            continue
                        gpx = str(p.get("gpx") or "")
                        if not gpx.startswith("https://centrodedescargas.cnig.es/"):
                            gpx = None
                        routes[rid] = {
                            "id": rid, "name": name, "type": layer.split("sendero")[-1].upper(),
                            "distance_km": float(p["longitud"]) if str(p.get("longitud", "")).replace(".", "", 1).isdigit() else None,
                            "gpx_url": gpx, "kml_url": p.get("kml"),
                            "info_url": p.get("url_info"),
                            "source": ATTRIBUTION,
                        }
        except (urllib.error.URLError, TimeoutError, ValueError) as exc:
            failures.append({"x": x, "y": y, "error": str(exc)})
        print(f"tile {i}/{len(tiles)} routes={len(routes)}", flush=True)
        if i < len(tiles):
            time.sleep(delay)
    return {"region": region, "zoom": zoom, "tile_count": len(tiles),
            "failed_tiles": failures, "routes": sorted(routes.values(), key=lambda r: r["name"])}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--region", choices=REGIONS, default="jaen")
    p.add_argument("--zoom", type=int, choices=(8, 9, 10), default=9)
    p.add_argument("--max-tiles", type=int, default=80)
    p.add_argument("--delay", type=float, default=0.4)
    p.add_argument("--output", default="data/fedme-jaen-pilot.json")
    args = p.parse_args()
    if args.delay < 0.3:
        p.error("Delay mínimo 0.3 s para evitar consultas agresivas")
    result = collect(args.region, args.zoom, args.max_tiles, args.delay)
    dest = pathlib.Path(args.output)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(result, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"Saved {len(result['routes'])} unique routes to {dest}; failed tiles: {len(result['failed_tiles'])}")
    if result["failed_tiles"]:
        raise SystemExit("Cobertura incompleta: revisar failed_tiles antes de publicar")


if __name__ == "__main__":
    main()
