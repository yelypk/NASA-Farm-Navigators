from pathlib import Path
import json

def region_meta_from_geojson(geojson_path: str) -> dict:
    gj = json.loads(Path(geojson_path).read_text(encoding="utf-8"))
    # Expect Polygon/MultiPolygon
    def bounds(coords):
        xs, ys = [], []
        def walk(ring):
            for x,y in ring:
                xs.append(x); ys.append(y)
        if gj["features"]:
            geom = gj["features"][0]["geometry"]
        else:
            geom = gj["geometry"]
        if geom["type"] == "Polygon":
            for ring in geom["coordinates"]:
                walk(ring)
        elif geom["type"] == "MultiPolygon":
            for poly in geom["coordinates"]:
                for ring in poly:
                    walk(ring)
        else:
            raise ValueError("Geometry must be Polygon/MultiPolygon")
        return min(xs), min(ys), max(xs), max(ys)

    xmin, ymin, xmax, ymax = bounds(None)
    return {
        "bbox": [xmin, ymin, xmax, ymax],
        "grid_w": 200, "grid_h": 200, "tile_m": 250,
        "layers": ["ndvi","rain","dry","temp"],
        "seasons_per_year": 4, "years": 20
    }

if __name__ == "__main__":
    import sys, json
    meta = region_meta_from_geojson(sys.argv[1])
    print(json.dumps(meta, ensure_ascii=False, indent=2))
