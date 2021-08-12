import utils.Init as ModuleInit

import requests
import json
from bs4 import BeautifulSoup as BS
import re
import utils.DN42Reg as Reg
import time

cmd = "roa"
enabled = True


def init():
    ModuleInit.CheckDir("data/roa")


def getROA(url, timeout):
    rt = []
    r = requests.get(url, timeout=timeout)
    t = BS(r.text, features="lxml").pre.getText().split("\n")
    for l in t:
        ls1 = l.split(" ")
        if len(ls1) > 2:
            asn = ls1[len(ls1) - 1].lstrip().replace(
                "[", "").replace("]", "").replace("i", "").replace("?", "")
            rt.append({
                "asn": asn[2:],
                "name": Reg.getASNName(asn),
                "prefix": ls1[0].rstrip()
            })
    return rt


def process():
    roa4 = getROA('http://lg-grc.burble.com/route_generic/localhost/where%20roa_check%28dn42_roa6%2C%20net%2C%20bgp_path.last%29%20%21=%20ROA_VALID%20&&%20net.type%20=%20NET_IP6%20&&%20bgp_path.len%20>%201%20primary', 10)
    roa6 = getROA('http://lg-grc.burble.com/route_generic/localhost/where%20roa_check%28dn42_roa4%2C%20net%2C%20bgp_path.last%29%20%21=%20ROA_VALID%20&&%20net.type%20=%20NET_IP4%20&&%20bgp_path.len%20>%201%20primary', 10)
    with open('data/roa/alerts.json', 'w') as f:
        json.dump({
            "created": int(time.time()),
            "roa4_data": roa4,
            "roa6_data": roa6
        }, f)
    return {"invalidRoutes": len(roa4) + len(roa6)}


if __name__ == "__main__":
    init()
    process()
