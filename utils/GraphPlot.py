import pygraphviz as pgv
import time
import json
import copy
import os.path
import networkx as nx
from networkx.algorithms import centrality
from networkx.algorithms.community import k_clique_communities
from utils.DN42Reg import getASNName, checkASNExist


with open('data/table/table.json') as f:
    prefix = json.load(f)

def CreateGraph(graphobj):
    G = pgv.AGraph(strict=True, directed=True, size='10!')
    for idx, n in enumerate(graphobj["nodes"]):
        G.add_node(idx, label=n)
    for e in graphobj["edges"]:
        G.add_edge(graphobj["nodes"].index(e['from']),
                   graphobj["nodes"].index(e['to']), len=1.0)
    return G


def compute_betweenness(G):
    ng = nx.Graph()
    for start in G.iternodes():
        others = G.neighbors(start)
        for other in others:
            ng.add_edge(start, other)
    c = centrality.betweenness_centrality(ng)
    for k, v in c.items():
        c[k] = v
    return c


def canonalize_ip(ip):
    return ':'.join(i.rjust(4, '0') for i in ip.split(':'))


def checkRouteExist(asn):
    global prefix
    if asn == "4242421331":
        return True
    if any(asn in p["origin"] for p in prefix["ipv4"]):
        return True
    elif any(asn in p["origin"] for p in prefix["ipv6"]):
        return True
    else:
        return False


def GetGraphOutput(G):
    max_neighbors = 1
    for n in G.iternodes():
        neighbors = len(G.neighbors(n))
        if neighbors > max_neighbors:
            max_neighbors = neighbors
    print('Max neighbors: %d' % max_neighbors)

    out_data = {
        'created': int(time.time()),
        'nodes': [],
        'edges': []
    }

    G_ct = G.copy()
    for n in G.nodes():
        if not checkASNExist(n.attr["label"]):
            G_ct.remove_node(n)
        elif not checkRouteExist(n.attr["label"]):
            print("Remove: " + n.attr["label"])
            G_ct.remove_node(n)

    centralities = compute_betweenness(G_ct)

    for n in G.nodes():
        neighbor_ratio = len(G.neighbors(n)) / float(max_neighbors)
        centrality = centralities.get(n, -1.0)
        if centrality >= 0:
            pcentrality = (centrality + 0.0001) * 500
        else:
            pcentrality = 0.0001 * 500
        size = (pcentrality ** 0.3 / 500) * 1000 + 1

        out_data['nodes'].append({
            'asn': n.attr['label'],
            'name': getASNName(n.attr['label']),
            'id': n,
            'color': _gradient_color(neighbor_ratio, [(100, 100, 100), (0, 0, 0)]),
            'size': size,
            'centrality': '%.4f' % centrality
        })

    for e in G.edges():
        out_data['edges'].append({
            'sourceID': e[0],
            'targetID': e[1]
        })

    return out_data


def _gradient_color(ratio, colors):
    jump = 1.0 / (len(colors) - 1)
    gap_num = int(ratio / (jump + 0.0000001))

    a = colors[gap_num]
    b = colors[gap_num + 1]

    ratio = (ratio - gap_num * jump) * (len(colors) - 1)

    r = int(a[0] + (b[0] - a[0]) * ratio)
    g = int(a[1] + (b[1] - a[1]) * ratio)
    b = int(a[2] + (b[2] - a[2]) * ratio)

    return '#%02x%02x%02x' % (r, g, b)
