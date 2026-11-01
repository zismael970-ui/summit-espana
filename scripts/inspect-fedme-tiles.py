#!/usr/bin/env python3
"""Diagnóstico no masivo del servicio oficial de teselas FEDME."""
import json
import math
import urllib.error
import urllib.request

LAT, LON, ZOOM = 37.7796, -3.7849, 11  # Jaén, muestra fija
n = 2 ** ZOOM
x = int((LON + 180) / 360 * n)
y = int((1 - math.asinh(math.tan(math.radians(LAT))) / math.pi) / 2 * n)
base = "https://vt-fedme.idee.es"
urls = [
    base + "/files/styles/style_gr.json",
    base + f"/vt.senderogr,vt.senderopr,vt.senderosl/{ZOOM}/{x}/{y}.pbf",
]
for url in urls:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "SUMMIT-research/0.1"})
        with urllib.request.urlopen(req, timeout=15) as response:
            data = response.read(2_000_000)
            print("URL:", url)
            print("HTTP:", response.status, "bytes:", len(data))
            print("Content-Type:", response.headers.get("Content-Type"))
            if url.endswith(".json"):
                obj = json.loads(data)
                print("Style sources:", list(obj.get("sources", {})))
                print("Style layers:", [layer.get("source-layer") for layer in obj.get("layers", []) if layer.get("source-layer")][:12])
            else:
                print("MVT signature:", data[:16].hex())
    except (urllib.error.URLError, TimeoutError, ValueError) as exc:
        print("ERROR:", url, str(exc))
        raise SystemExit(1) from exc
print("Diagnóstico completado. NO se han reconstruido rutas completas.")
