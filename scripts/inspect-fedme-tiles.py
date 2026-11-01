#!/usr/bin/env python3
"""Diagnóstico acotado de teselas vectoriales FEDME (no importa rutas completas).

Uso: python3 scripts/inspect-fedme-tiles.py
Opcional: python3 -m pip install mapbox-vector-tile
"""
import json
import math
import urllib.error
import urllib.request

BASE = "https://vt-fedme.idee.es"
SAMPLES = [("Jaén", 37.7796, -3.7849, 11), ("Madrid", 40.4168, -3.7038, 11), ("Pirineos", 42.65, 0.0, 11)]
MAX_BYTES = 2_000_000


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "SUMMIT-FEDME-research/0.2 (nonbulk)"})
    with urllib.request.urlopen(req, timeout=18) as response:
        data = response.read(MAX_BYTES + 1)
        if len(data) > MAX_BYTES:
            raise ValueError("Respuesta superior al límite de seguridad")
        return data


def tile(lat, lon, z):
    n = 2 ** z
    return int((lon + 180) / 360 * n), int((1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n)


def inspect():
    report = {"source": "IGN/CNIG FEDME vector tiles", "tiles": [], "caution": "Tile fragments are NOT complete GPX routes."}
    style = json.loads(get(BASE + "/files/styles/style.json"))
    report["style_layers"] = sorted(set(str(layer.get("source-layer")) for layer in style.get("layers", []) if layer.get("source-layer")))
    try:
        import mapbox_vector_tile
    except ImportError:
        mapbox_vector_tile = None
        report["decoder"] = "not installed: pip install mapbox-vector-tile"
    for name, lat, lon, zoom in SAMPLES:
        x, y = tile(lat, lon, zoom)
        url = f"{BASE}/vt.senderogr,vt.senderopr,vt.senderosl/{zoom}/{x}/{y}.pbf"
        try:
            raw = get(url)
            result = {"place": name, "z": zoom, "x": x, "y": y, "bytes": len(raw)}
            if mapbox_vector_tile:
                decoded = mapbox_vector_tile.decode(raw)
                result["layers"] = {}
                for layer_name, layer in decoded.items():
                    features = layer.get("features", [])
                    keys = sorted({key for feature in features[:100] for key in feature.get("properties", {})})
                    id_keys = [key for key in keys if any(part in key.lower() for part in ("id", "codigo", "ref", "nombre", "name"))]
                    result["layers"][layer_name] = {
                        "feature_count": len(features), "property_keys": keys,
                        "potential_route_id_fields": id_keys,
                        "sample_properties": [f.get("properties", {}) for f in features[:2]],
                    }
            report["tiles"].append(result)
        except (urllib.error.URLError, TimeoutError, ValueError) as exc:
            report["tiles"].append({"place": name, "error": str(exc)})
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return report


if __name__ == "__main__":
    inspect()
