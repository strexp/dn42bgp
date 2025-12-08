import bz2
import json
import logging
from pathlib import Path

def process() -> None:
    cache_dir = Path("cache/table")
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    data_dir = Path("data/table")
    data_dir.mkdir(parents=True, exist_ok=True)

    input_file = Path("cache/table.jsonl.bz2")
    if not input_file.exists():
        logging.error(f"Input file {input_file} not found.")
        return

    table_data = {"ipv4": [], "ipv6": []}
    as_paths = {"ipv4": [], "ipv6": []}
    freq_data = {"ipv4": {}, "ipv6": {}}

    logging.info("Extracting BZ2 table data...")
    with bz2.BZ2File(input_file, "r") as f:
        while line := f.readline():
            try:
                item = json.loads(line)
                ip_type = item.get("type")

                if ip_type in ("ipv4", "ipv6"):
                    obj = {"prefix": item["prefix"], "origin": set()}
                    for rib in item.get("rib", []):
                        if "as_sequence" in rib and rib["as_sequence"]:
                            as_paths[ip_type].append(rib["as_sequence"])
                            obj["origin"].add(rib["as_sequence"][-1])
                            for asn in rib["as_sequence"]:
                                if asn in freq_data[ip_type]:
                                    freq_data[ip_type][asn] = freq_data[ip_type][asn] + 1
                                else:
                                    freq_data[ip_type][asn] = 1

                    obj["origin"] = list(obj["origin"])
                    table_data[ip_type].append(obj)
            except json.JSONDecodeError:
                logging.error("JSON decode error.")
                exit(1)

    with (cache_dir / "table.json").open("w") as f:
        json.dump(table_data, f)

    with (cache_dir / "aspaths.json").open("w") as f:
        json.dump(as_paths, f)

    with (data_dir / "freq.json").open("w") as f:
        json.dump(freq_data, f)
