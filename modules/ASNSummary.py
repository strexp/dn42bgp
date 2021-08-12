import utils.Init as ModuleInit

import utils.DN42Reg as Reg
import time
import requests
import json
from bs4 import BeautifulSoup as BS

cmd = "asnsummary"
enabled = True


def init():
    ModuleInit.CheckDir("data/asn")


def process():
    asnList = Reg.getASNList()
    routeList = Reg.getRouteList()
    with open("data/table/table.json") as tf:
        visiblePrefixList = json.load(tf)
    for asn in asnList:
        asnInfo = Reg.getASNInfo(asn)
        asnRoute = Reg.getASNRoute(asn, routeList)
        for idx, asnr4 in enumerate(asnRoute["ipv4"]):
            if any(p['prefix'] == asnr4["route"][0] for p in visiblePrefixList["ipv4"]):
                asnRoute["ipv4"][idx]["visible"] = True
            else:
                asnRoute["ipv4"][idx]["visible"] = False
        for idx, asnr6 in enumerate(asnRoute["ipv6"]):
            if any(p['prefix'] == asnr6["route6"][0] for p in visiblePrefixList["ipv6"]):
                asnRoute["ipv6"][idx]["visible"] = True
            else:
                asnRoute["ipv6"][idx]["visible"] = False
        with open('data/asn/' + asn + '.json', 'w') as f:
            json.dump({
                "created": int(time.time()),
                "asn": asnInfo,
                "routes": asnRoute
            }, f)
    return {
        "registeredASN": len(asnList),
        "registeredRoutes": len(routeList),
        "observedRoutes": len(visiblePrefixList)
    }


if __name__ == "__main__":
    init()
    process()
