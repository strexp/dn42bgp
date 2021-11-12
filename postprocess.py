import json

def main():
    with open("data/registry/prefix.6.json") as pf:
        p = json.load(pf)
    g32 = []
    g48 = []
    g64 = []
    etc = []
    for pfx in p["children"][0]["children"]:
        if pfx["size"] >= pow(2, 128 - 32):
            g32.append(pfx)
        elif pfx["size"] >= pow(2, 128 - 48):
            g48.append(pfx)
        elif pfx["size"] >= pow(2, 128 - 64):   
            g64.append(pfx) 
        else:
            etc.append(pfx)
    p["children"][0]["children"] = []
    p["children"][0]["children"].append({
        "prefix": "ABOVE /32",
        "size": sum([ i["size"] for i in g32 ]),
        "children": g32
    })
    p["children"][0]["children"].append({
        "prefix": "ABOVE /48",
        "size": sum([ i["size"] for i in g48 ]),
        "children": g48
    })
    p["children"][0]["children"].append({
        "prefix": "ABOVE /64",
        "size": sum([ i["size"] for i in g64 ]),
        "children": g64
    })
    p["children"][0]["children"].append({
        "prefix": "OTHERS",
        "size": sum([ i["size"] for i in etc ]),
        "children": etc
    })
    with open("data/registry/prefix.6.processed.json", "w") as pf:
        json.dump(p, pf)

if __name__ == "__main__":
    try:
        main()
    except:
        print("Error when postprocessing prefix file!")