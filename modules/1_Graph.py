import utils.Init as ModuleInit

import utils.DN42Reg as Reg
import utils.GraphPlot as Plot
import json
import time
import gc

cmd = "graph"
enabled = True


def init():
    ModuleInit.CheckDir("data/graph")

def createGraphs(paths):
    graph = {"nodes": set(), "edges": []}
    for path in paths:
        for i in range(1, len(path)):
            graph["nodes"].add(path[i])
            graph["nodes"].add(path[i-1])
            graph["edges"].append({"from": path[i-1], "to": path[i]})
    graph["nodes"] = list(graph["nodes"])
    return graph


def process():
    with open("data/table/aspaths.json") as pf:
        paths = json.load(pf)
    graph4 = createGraphs(paths["ipv4"])
    graph6 = createGraphs(paths["ipv6"])
    print("create graph!")
    graphObj4 = Plot.CreateGraph(graph4)  
    graphOutput4 = Plot.GetGraphOutput(graphObj4)
    with open("data/graph/ipv4.json","w") as g4f:
        json.dump(graphOutput4, g4f)  
    del graph4,graphObj4,graphOutput4
    gc.collect()
    graphObj6 = Plot.CreateGraph(graph6)  
    graphOutput6 = Plot.GetGraphOutput(graphObj6)
    with open("data/graph/ipv6.json","w") as g4f:
        json.dump(graphOutput6, g4f)  
    del graph6,graphObj6,graphOutput6
    gc.collect()

if __name__ == "__main__":
    init()
    process()
