import json
import gc
import logging
from pathlib import Path
from core import graph as graph_utils

def create_graph_struct(paths: list[list[str]]) -> dict:
    nodes = set()
    edges = []
    for path in paths:
        for i in range(1, len(path)):
            u, v = path[i-1], path[i]
            nodes.add(u)
            nodes.add(v)
            edges.append({"from": u, "to": v})
    return {"nodes": list(nodes), "edges": edges}

def process_ip_version(version: str, paths: list[list[str]], output_dir: Path):
    logging.info(f"Building graph for {version}...")
    raw_graph = create_graph_struct(paths)
    
    pgv_graph = graph_utils.create_pgv_graph(raw_graph["nodes"], raw_graph["edges"])
    
    output_data = graph_utils.get_graph_output(pgv_graph)
    
    with (output_dir / f"{version}.json").open("w") as f:
        json.dump(output_data, f)
    
    del raw_graph, pgv_graph, output_data
    gc.collect()

def process() -> None:
    graph_dir = Path("data/graph")
    graph_dir.mkdir(parents=True, exist_ok=True)
    
    aspaths_file = Path("cache/table/aspaths.json")
    if not aspaths_file.exists():
        logging.error("AS Paths file not found.")
        return

    with aspaths_file.open("r") as f:
        paths_data = json.load(f)

    process_ip_version("ipv4", paths_data["ipv4"], graph_dir)
    process_ip_version("ipv6", paths_data["ipv6"], graph_dir)
