import utils.Init as ModuleInit

import utils.DN42Reg as Reg
import bz2
import json

enabled = True

def decode(entry: dict) -> None:
    if entry["type"] in {"ipv4", "ipv6"}:
        for rib in entry["rib"]:
            print("%s_prefix:" % entry["type"], entry["prefix"])
            attrs = ("as_path", "community",
                     "extended_community", "large_community")
            for attr in attrs:
                attr_val = rib.get(attr)
                if attr_val:
                    print(attr, ":", attr_val)
            assert not any(filter(lambda x: x not in attrs, rib))
    else:
        assert False


def init():
    ModuleInit.CheckDir("data/table")


def process():
    s = {"ipv4": [], "ipv6": []}
    p = {"ipv4": [], "ipv6": []}
    with bz2.BZ2File("data/table.jsonl.bz2", 'r') as f:
        while line := f.readline():
            item = json.loads(line)
            if item["type"] == "ipv4":
                obj = {"prefix": item["prefix"], "origin": set()}
                for rib in item["rib"]:
                    p["ipv4"].append(rib["as_path"])
                    obj["origin"].add(rib["as_path"][-1])
                obj["origin"] = list(obj["origin"])
                s["ipv4"].append(obj)
            if item["type"] == "ipv6":
                obj = {"prefix": item["prefix"], "origin": set()}
                for rib in item["rib"]:
                    p["ipv6"].append(rib["as_path"])
                    obj["origin"].add(rib["as_path"][-1])
                obj["origin"] = list(obj["origin"])
                s["ipv6"].append(obj)
    with open("data/table/table.json", "w") as tf:
        json.dump(s, tf)
    with open("data/table/aspaths.json", "w") as pf:
        json.dump(p, pf)

if __name__ == "__main__":
    init()
    process()