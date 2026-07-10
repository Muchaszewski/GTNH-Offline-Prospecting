import os
import json
import argparse
from pathlib import Path
import hashlib

def string_to_color(s):
    h = int(hashlib.md5(s.encode('utf-8')).hexdigest(), 16)
    r = (h & 0xFF0000) >> 16
    g = (h & 0x00FF00) >> 8
    b = h & 0x0000FF
    return ((r + 255)//2, (g + 255)//2, (b + 255)//2)

def get_dimension_id(dim_name):
    dim_name_lower = dim_name.lower()
    if dim_name_lower == "overworld":
        return 0
    elif dim_name_lower.startswith("dim"):
        try:
            return int(dim_name_lower[3:])
        except ValueError:
            return 0
    return 0

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dim-dir", required=True)
    parser.add_argument("--export-type", required=True, choices=['journeymap'])
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--ore-filter", required=False, default="All Ores")
    args = parser.parse_args()

    dim_dir = Path(args.dim_dir)
    out_dir = Path(args.out_dir)
    
    dict_path = dim_dir / "dictionary.json"
    dictionary = {}
    if dict_path.exists():
        with open(dict_path, 'r', encoding='utf-8') as f:
            dictionary = json.load(f)

    ore_chunks = {}
    
    for file_path in dim_dir.glob("r.*.json"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception:
            continue
            
        for chunk_key, blocks in data.items():
            ore_positions = {}
            for b in blocks:
                is_small = False
                x, z = 0, 0
                name = "Unknown Ore"
                
                if isinstance(b, list) and len(b) >= 6:
                    x, z = b[0], b[2]
                    is_small = (b[5] == 1 or b[5] is True)
                    key = f"{b[3]}:{b[4]}:{int(is_small)}"
                    name = dictionary.get(key, "Unknown Ore")
                
                elif isinstance(b, dict):
                    pos = b.get("position", [0, 0, 0])
                    x, z = pos[0], pos[2]
                    is_small = b.get("small", False)
                    name = b.get("name", "Unknown Ore")
                else:
                    continue

                if is_small: 
                    continue
                
                if args.ore_filter and args.ore_filter != "All Ores" and name != args.ore_filter:
                    continue

                if name not in ore_positions:
                    ore_positions[name] = {'x_sum': 0, 'z_sum': 0, 'count': 0}
                    
                ore_positions[name]['x_sum'] += x
                ore_positions[name]['z_sum'] += z
                ore_positions[name]['count'] += 1
            
            for name, d in ore_positions.items():
                if d['count'] >= 4: 
                    avg_x = int(d['x_sum'] / d['count'])
                    avg_z = int(d['z_sum'] / d['count'])
                    
                    if name not in ore_chunks:
                        ore_chunks[name] = []
                    ore_chunks[name].append((avg_x, avg_z, d['count']))

    veins = []
    for name, chunks in ore_chunks.items():
        chunks.sort(key=lambda x: x[2], reverse=True)
        while chunks:
            best_x, best_z, best_count = chunks.pop(0)
            veins.append({
                "name": name,
                "count": best_count,
                "x": best_x,
                "z": best_z
            })
            chunks = [c for c in chunks if abs(c[0] - best_x) > 48 or abs(c[1] - best_z) > 48]

    dim_id = get_dimension_id(dim_dir.name)

    if args.export_type == 'journeymap':
        jm_dir = out_dir / "journeymap"
        jm_dir.mkdir(parents=True, exist_ok=True)
        for i, v in enumerate(veins):
            r, g, b = string_to_color(v["name"])
            wp_id = f"vein_{v['x']}_{v['z']}_{i}" 
            
            export_x = v['x'] * 8 if dim_id == -1 else v['x']
            export_z = v['z'] * 8 if dim_id == -1 else v['z']
            
            wp = {
                "id": wp_id,
                "name": f"{v['name']} Vein",
                "icon": "waypoint-normal.png",
                "x": export_x, "y": 65, "z": export_z,
                "r": r, "g": g, "b": b,
                "enable": True,
                "type": "Normal",
                "origin": "journeymap",
                "dimensions": [dim_id]
            }
            with open(jm_dir / f"{wp_id}.json", 'w') as f:
                json.dump(wp, f, indent=4)
                
        print(f"Generated {len(veins)} Waypoints into {jm_dir}")

if __name__ == "__main__":
    main()
