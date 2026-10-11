"""Downloads park walkways, park outlines and ride positions from OpenStreetMap (Overpass API)
and saves them next to the app, so phones load them from GitHub Pages instead of a busy public server."""
import json, sys, time, urllib.parse, urllib.request

MIRRORS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
]
REGIONS = {
    "resort": [28.4650, -81.4790, 28.4830, -81.4600],
    "epic": [28.4150, -81.4750, 28.4650, -81.4250],
}
HW = "footway|pedestrian|path|steps|living_street|corridor|service|unclassified|residential|track|cycleway"

def query(b):
    bb = ",".join(str(x) for x in b)
    return (f'[out:json][timeout:180];'
            f'(way["highway"~"^({HW})$"]({bb});way["area:highway"]({bb});way["place"="square"]({bb}););out body;>;out skel qt;'
            f'(way["tourism"="theme_park"]({bb});relation["tourism"="theme_park"]({bb}););out geom;'
            f'(node["tourism"="attraction"]({bb});way["tourism"="attraction"]({bb});'
            f'node["attraction"]({bb});way["attraction"]({bb}););out center tags;')

def fetch(q):
    body = urllib.parse.urlencode({"data": q}).encode()
    last = None
    for attempt in range(3):
        for url in MIRRORS:
            try:
                req = urllib.request.Request(url, data=body, headers={"User-Agent": "queue-compass/1.0 (github pages walkway cache)"})
                with urllib.request.urlopen(req, timeout=240) as r:
                    data = json.load(r)
                if len(data.get("elements", [])) > 100:
                    return data
                last = f"{url}: only {len(data.get('elements', []))} elements"
            except Exception as e:
                last = f"{url}: {e}"
            print("retry:", last, file=sys.stderr)
            time.sleep(10)
    raise SystemExit(f"all mirrors failed: {last}")

for name, bbox in REGIONS.items():
    data = fetch(query(bbox))
    data.pop("osm3s", None)
    with open(f"osm-{name}.json", "w") as f:
        json.dump(data, f, separators=(",", ":"))
    print(name, len(data["elements"]), "elements")
