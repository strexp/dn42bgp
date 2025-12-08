import time
import json
import networkx as nx
from networkx.algorithms import centrality
import pygraphviz as pgv
from typing import Any
from . import registry

def create_pgv_graph(json_nodes: list[str], json_edges: list[dict[str, str]]) -> pgv.AGraph:
    G = pgv.AGraph(strict=True, directed=True, size='10!')
    node_to_idx = {n: i for i, n in enumerate(json_nodes)}
    
    for idx, n in enumerate(json_nodes):
        G.add_node(idx, label=n)
        
    for e in json_edges:
        if e['from'] in node_to_idx and e['to'] in node_to_idx:
            u = node_to_idx[e['from']]
            v = node_to_idx[e['to']]
            G.add_edge(u, v, len=1.0)
            
    return G

def compute_betweenness(pgv_G: pgv.AGraph) -> dict[Any, float]:
    nx_G = nx.Graph()
    for node in pgv_G.iternodes():
        for neighbor in pgv_G.neighbors(node):
            nx_G.add_edge(node, neighbor)
            
    return centrality.betweenness_centrality(nx_G)

def _gradient_color(ratio: float, colors: list[tuple[int, int, int]]) -> str:
    jump = 1.0 / (len(colors) - 1)
    gap_num = int(ratio / (jump + 1e-7))
    
    if gap_num >= len(colors) - 1:
        gap_num = len(colors) - 2

    c1 = colors[gap_num]
    c2 = colors[gap_num + 1]

    local_ratio = (ratio - gap_num * jump) * (len(colors) - 1)

    r = int(c1[0] + (c2[0] - c1[0]) * local_ratio)
    g = int(c1[1] + (c2[1] - c1[1]) * local_ratio)
    b = int(c1[2] + (c2[2] - c1[2]) * local_ratio)

    return f'#{r:02x}{g:02x}{b:02x}'

def check_route_exist_lazy(asn: str, cached_table: dict | None = None) -> bool:
    if asn == "4242421331": return True
    if cached_table is None:
        try:
            with open('cache/table/table.json') as f:
                cached_table = json.load(f)
        except FileNotFoundError:
            return False

    if any(asn in p.get("origin", []) for p in cached_table["ipv4"]):
        return True
    if any(asn in p.get("origin", []) for p in cached_table["ipv6"]):
        return True
    return False

def get_graph_output(G: pgv.AGraph) -> dict[str, Any]:
    try:
        with open('cache/table/table.json') as f:
            route_table = json.load(f)
    except FileNotFoundError:
        route_table = {"ipv4": [], "ipv6": []}

    max_neighbors = 1
    for n in G.iternodes():
        nb = len(G.neighbors(n))
        if nb > max_neighbors:
            max_neighbors = nb
            
    print(f'Max neighbors: {max_neighbors}')

    nodes_to_remove = []
    for n in G.nodes():
        asn_label = n.attr["label"]
        if not registry.check_asn_exists(asn_label):
            nodes_to_remove.append(n)
        elif not check_route_exist_lazy(asn_label, route_table):
            # print(f"Remove inactive: {asn_label}")
            nodes_to_remove.append(n)
    
    for n in nodes_to_remove:
        G.remove_node(n)

    centralities = compute_betweenness(G)

    out_data = {
        'created': int(time.time()),
        'nodes': [],
        'edges': []
    }

    for n in G.nodes():
        neighbor_ratio = len(G.neighbors(n)) / float(max_neighbors)
        cent_val = centralities.get(n, -1.0)
        
        pcentrality = (cent_val + 0.0001) * 500 if cent_val >= 0 else 0.05
        size = (pcentrality ** 0.3 / 500) * 1000 + 1
        
        asn = n.attr['label']
        out_data['nodes'].append({
            'asn': asn,
            'name': registry.get_asn_name(asn),
            'id': n,
            'color': _gradient_color(neighbor_ratio, [(100, 100, 100), (0, 0, 0)]),
            'size': size,
            'centrality': f'{cent_val:.4f}'
        })

    for e in G.edges():
        out_data['edges'].append({
            'sourceID': e[0],
            'targetID': e[1]
        })

    return out_data
