import json
import time
from collections import defaultdict
from pathlib import Path

from core import registry


def process() -> None:
    out_dir = Path("data/asn")
    out_dir.mkdir(parents=True, exist_ok=True)

    asn_list = registry.get_asn_list()
    route_list = registry.get_route_list()

    table_file = Path("cache/table/table.json")
    visible_routes = {"ipv4": set(), "ipv6": set()}

    if table_file.exists():
        try:
            with table_file.open("r") as f:
                raw_table = json.load(f)
                visible_routes["ipv4"] = {
                    r["prefix"] for r in raw_table.get("ipv4", [])
                }
                visible_routes["ipv6"] = {
                    r["prefix"] for r in raw_table.get("ipv6", [])
                }
        except json.JSONDecodeError:
            exit(1)

    asn_map = {"ipv4": defaultdict(list), "ipv6": defaultdict(list)}

    for ver in ["ipv4", "ipv6"]:
        for r in route_list[ver]:
            origins = r.get("origin", [])
            if isinstance(origins, str):
                origins = [origins]

            for origin in origins:
                clean_origin = origin.upper().replace("AS", "")

                prefix_key = "route" if ver == "ipv4" else "route6"

                prefix = r.get(prefix_key, [""])[0]
                r_copy = r.copy()
                r_copy["visible"] = prefix in visible_routes[ver]

                asn_map[ver][clean_origin].append(r_copy)

    current_time = int(time.time())

    for asn in asn_list:
        asn_str = asn.replace("AS", "")
        asn_info = registry.get_asn_info(asn)

        asn_routes_data = {
            "ipv4": asn_map["ipv4"].get(asn_str, []),
            "ipv6": asn_map["ipv6"].get(asn_str, []),
        }

        with (out_dir / f"AS{asn_str}.json").open("w") as f:
            json.dump(
                {"created": current_time, "asn": asn_info, "routes": asn_routes_data}, f
            )
