import json
import logging
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import mrtparse

def get_as_path(bgp_attr: list) -> list[str]:
    path = []
    for attr in bgp_attr:
        if attr["type"] == {2: "AS_PATH"}:
            for seg in attr["value"]:
                if seg["type"] == {2: "AS_SEQUENCE"}:
                    path.extend(map(str, seg["value"]))
    return path


def parse_worker(filepath: Path, ip_version: str) -> tuple[str, list, list, dict]:
    if not filepath.exists():
        logging.warning(f"MRT file {filepath} not found.")
        return ip_version, [], [], {}

    logging.info(f"Parsing {filepath} for {ip_version}...")

    local_table = []
    local_paths = []
    local_freq = Counter()

    reader = mrtparse.Reader(str(filepath))

    for record in reader:
        if record.err:
            continue

        data = record.data

        if data["type"] != {13: "TABLE_DUMP_V2"}:
            continue

        if "prefix" not in data or "rib_entries" not in data:
            continue

        prefix = f"{data['prefix']}/{data['length']}"
        origin_set = set()

        rib_entries = data["rib_entries"]
        for entry in rib_entries:
            bgp_attrs = entry.get("path_attributes")
            if not bgp_attrs:
                continue

            path_seq = get_as_path(bgp_attrs)

            if path_seq:
                local_paths.append(path_seq)
                origin_set.add(path_seq[-1])
                local_freq.update(path_seq)

        if origin_set:
            local_table.append({"prefix": prefix, "origin": list(origin_set)})

    return ip_version, local_table, local_paths, dict(local_freq)


def process() -> None:
    cache_dir = Path("cache/table")
    cache_dir.mkdir(parents=True, exist_ok=True)

    data_dir = Path("data/table")
    data_dir.mkdir(parents=True, exist_ok=True)

    table_data = {"ipv4": [], "ipv6": []}
    as_paths = {"ipv4": [], "ipv6": []}
    freq_data = {"ipv4": {}, "ipv6": {}}

    tasks = [
        (Path("cache/master4.mrt.bz2"), "ipv4"),
        (Path("cache/master6.mrt.bz2"), "ipv6"),
    ]

    logging.info("Starting parallel MRT parsing...")
    with ProcessPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(parse_worker, fp, ver) for fp, ver in tasks]

        for future in futures:
            try:
                ver, t_data, p_data, f_data = future.result()
                if t_data:
                    table_data[ver] = t_data
                    as_paths[ver] = p_data
                    freq_data[ver] = f_data
            except Exception as e:
                logging.error(f"Worker failed: {e}")
                exit(1)

    logging.info("Writing extracted data to cache...")
    
    with (cache_dir / "table.json").open("w") as f:
        json.dump(table_data, f)
    with (cache_dir / "aspaths.json").open("w") as f:
        json.dump(as_paths, f)
    with (data_dir / "freq.json").open("w") as f:
        json.dump(freq_data, f)
