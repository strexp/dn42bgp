import json
import time
from pathlib import Path
from core import registry

def get_asn_routes(asn: str, route_list: dict) -> dict:
    asn_routes = {"ipv4": [], "ipv6": []}
    asn_key = f"AS{asn}" if not asn.startswith("AS") else asn
    
    for r in route_list["ipv4"]:
        if asn_key in r.get("origin", []):
            asn_routes["ipv4"].append(r)
            
    for r in route_list["ipv6"]:
        if asn_key in r.get("origin", []):
            asn_routes["ipv6"].append(r)
            
    return asn_routes

def process() -> None:
    out_dir = Path("data/asn")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    asn_list = registry.get_asn_list()
    route_list = registry.get_route_list()
    
    table_file = Path("cache/table/table.json")
    visible_routes = {"ipv4": [], "ipv6": []}
    if table_file.exists():
        with table_file.open("r") as f:
            visible_routes = json.load(f)

    visible_sets = {
        "ipv4": {r["prefix"] for r in visible_routes["ipv4"]},
        "ipv6": {r["prefix"] for r in visible_routes["ipv6"]}
    }

    for asn in asn_list:
        asn_info = registry.get_asn_info(asn)
        asn_routes_data = get_asn_routes(asn, route_list)
        
        for r in asn_routes_data["ipv4"]:
            prefix = r.get("route", [""])[0]
            r["visible"] = prefix in visible_sets["ipv4"]
            
        for r in asn_routes_data["ipv6"]:
            prefix = r.get("route6", [""])[0]
            r["visible"] = prefix in visible_sets["ipv6"]
            
        with (out_dir / f"AS{asn}.json").open("w") as f:
            json.dump({
                "created": int(time.time()),
                "asn": asn_info,
                "routes": asn_routes_data
            }, f)
