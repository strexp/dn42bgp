import utils.Init as ModuleInit

import utils.DN42Reg as Reg
import json
import time

cmd = "isp"
enabled = True


def init():
    ModuleInit.CheckDir("data/isp")


def centrality(graph):
    isps = [
        {
            "name": "Tier 1 Operators",
            "desc": "Tier 1 ISPs have centrality more than 0.08.",
            "data": []
        },
        {
            "name": "Tier 2 Operators",
            "desc": "Tier 2 ISPs have centrality more than 0.03.",
            "data": []
        },
        {
            "name": "Tier 3 Operators",
            "desc": "Tier 3 ISPs have centrality more than 0.005.",
            "data": []
        },
        {
            "name": "Customers",
            "desc": "Customers have centrality more than 0.",
            "data": []
        },
        {
            "name": "Invalids",
            "desc": "Invalids are ASNs not belong to DN42.",
            "data": []
        },
    ]
    for isp in graph["nodes"]:
        isp["centrality"] = float(isp["centrality"])
        x = 4
        if isp["centrality"] > -1:
            x = x-1
        if isp["centrality"] > 0.005:
            x = x-1
        if isp["centrality"] > 0.03:
            x = x-1
        if isp["centrality"] > 0.08:
            x = x-1
        isps[x]["data"].append({
            "id": isp["id"],
            "asn": isp["asn"],
            "name": isp["name"],
            "centrality":  isp["centrality"]
        })
    for group in isps:
        group["data"].sort(key=lambda x: x["centrality"], reverse=True)
    return isps

def process():
    with open("data/graph/ipv4.json") as f4:
        graph4 = json.load(f4)
    with open("data/graph/ipv6.json") as f6:
        graph6 = json.load(f6)
    with open("data/isp/isp4.json", "w") as wf4:
        json.dump(centrality(graph4), wf4)
    with open("data/isp/isp6.json", "w") as wf6:
        json.dump(centrality(graph6), wf6)

if __name__ == "__main__":
    init()
    process()
