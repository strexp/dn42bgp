import json
from pathlib import Path


def categorize_isps(graph_nodes: list[dict]) -> list[dict]:
    tiers = [
        {
            "name": "Tier 1 Operators",
            "desc": "Tier 1 ISPs have centrality more than 0.08.",
            "threshold": 0.08,
            "data": [],
        },
        {
            "name": "Tier 2 Operators",
            "desc": "Tier 2 ISPs have centrality more than 0.03.",
            "threshold": 0.03,
            "data": [],
        },
        {
            "name": "Tier 3 Operators",
            "desc": "Tier 3 ISPs have centrality more than 0.005.",
            "threshold": 0.005,
            "data": [],
        },
        {
            "name": "Customers",
            "desc": "Customers have centrality more than 0.",
            "threshold": 0.0,
            "data": [],
        },
        {
            "name": "Invalids",
            "desc": "Invalids are ASNs not belong to DN42.",
            "threshold": -1.0,
            "data": [],
        },
    ]

    valid_nodes = []
    for node in graph_nodes:
        try:
            c = float(node["centrality"])
            valid_nodes.append({**node, "centrality_val": c})
        except ValueError:
            continue

    for node in valid_nodes:
        c = node["centrality_val"]

        for tier in tiers:
            if c > tier["threshold"]:
                tier["data"].append(
                    {
                        "id": node.get("id", ""),
                        "asn": node["asn"],
                        "name": node["name"],
                        "centrality": c,
                    }
                )
                break
        else:
            # Fallback to Invalids (theoretical)
            tiers[-1]["data"].append(node)

    for group in tiers:
        group["data"].sort(key=lambda x: float(x["centrality"]), reverse=True)
        del group["threshold"]

    return tiers


def process() -> None:
    out_dir = Path("data/isp")
    out_dir.mkdir(parents=True, exist_ok=True)

    isp_list = []

    for ver in ["ipv4", "ipv6"]:
        graph_file = Path(f"data/graph/{ver}.json")
        if graph_file.exists():
            with graph_file.open("r") as f:
                data = json.load(f)
                nodes = data.get("nodes", [])

                ranked = categorize_isps(nodes)
                with (out_dir / f"isp{ver[-1]}.json").open("w") as wf:
                    json.dump(ranked, wf)

                for n in nodes:
                    isp_list.append((n["asn"], n["name"]))

    unique_isps = [{"asn": asn, "name": name} for asn, name in set(isp_list)]
    with (out_dir / "isp.json").open("w") as f:
        json.dump(unique_isps, f)
