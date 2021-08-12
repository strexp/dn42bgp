import json
import os
import ipaddress

dn42prefix4 = ipaddress.ip_network("172.20.0.0/14")
otherprefix4 = ipaddress.ip_network("10.0.0.0/8")
prefix6 = ipaddress.ip_network("fd00::/8")

DATAPREFIX = "~/registry/data/"


def calcAddressNum4(pfx):
    return pow(2, 32 - int(pfx))


def calcAddressNum6(pfx):
    return pow(2, 64 - int(pfx))


def getRouteList():
    returnList = {
        "ipv4": [],
        "ipv6": []
    }
    route4FileList = os.listdir(DATAPREFIX + "route")
    for route4File in route4FileList:
        f = open(DATAPREFIX + "route/" + route4File, "r")
        route4 = _getRegistryKeys(f)
        route4["inetnum"] = getInetNumInfo(route4File)
        returnList["ipv4"].append(route4)
    route6FileList = os.listdir(DATAPREFIX + "route6")
    for route6File in route6FileList:
        f = open(DATAPREFIX + "route6/" + route6File, "r")
        route6 = _getRegistryKeys(f)
        route6["inetnum"] = getInetNumInfo(route6File, True)
        returnList["ipv6"].append(route6)
    return returnList


def _getkey(ln):
    spl = ln.split(":", 1)
    return {
        "key": spl[0],
        "val": spl[1].lstrip()
    }


def getMNT(mnt):
    try:
        f = open(DATAPREFIX + "mntner/" + mnt)
        return _getRegistryKeys(f)
    except IOError:
        return {}


def getPerson(person):
    try:
        f = open(DATAPREFIX + "person/" + person)
        return _getRegistryKeys(f)
    except IOError:
        pass
    try:
        f = open(DATAPREFIX + "role/" + person)
        return _getRegistryKeys(f)
    except IOError:
        pass
    return {}


def getInetNumInfo(inetnum, ipv6=False):
    try:
        if ipv6:
            f = open(DATAPREFIX + "inet6num/" + inetnum)
            k = _getRegistryKeys(f)
            k.pop("inet6num")
        else:
            f = open(DATAPREFIX + "inetnum/" + inetnum)
            k = _getRegistryKeys(f)
            k.pop("inetnum")
        return k
    except IOError:
        return {}


def _getRegistryKeys(f):
    returnValue = {}
    prevkey = ""
    for ln in f:
        if ln.startswith(" "):
            returnValue[prevkey].append(ln.lstrip())
        elif ln.startswith("+"):
            returnValue[prevkey].append("\n")
        else:
            k = _getkey(ln)
            prevkey = k["key"]
            if(k["key"] in returnValue):
                returnValue[k["key"]].append(k["val"].rstrip())
            else:
                returnValue[k["key"]] = [k["val"].rstrip()]
    return returnValue


def getASNName(asn):
    asname = "Null"
    if asn is None:
        return asname
    try:
        if(asn.startswith("AS")):
            asn = asn[2:]
        f = open(DATAPREFIX + "aut-num/AS" + asn)
        for ln in f:
            if ln.startswith("as-name:"):
                asname = ln[len("as-name:"):]
                asname = asname.lstrip()
    except IOError:
        pass
    return asname.rstrip()


def checkASNExist(asn):
    if asn.startswith("AS"):
        asn = asn[2:]
    return os.path.exists(DATAPREFIX + "aut-num/AS" + asn)


def calcIPv4Usage():
    used = 0
    total = calcAddressNum4(14) - calcAddressNum4(24)
    used_others = 0
    total_others = calcAddressNum4(8)
    inet4numFileList = os.listdir(DATAPREFIX + "inetnum")
    for inet4numFile in inet4numFileList:
        inet4num = ipaddress.ip_network(inet4numFile.replace("_", "/"))
        if inet4num.subnet_of(dn42prefix4):
            if inet4num.prefixlen > 21:
                used = used + inet4num.num_addresses
        else:
            if inet4num.prefixlen > 14 and inet4num != ipaddress.ip_network("10.127.0.0/16"):
                used_others = used_others + inet4num.num_addresses
    return {"used": used, "total": total, "used_others": used_others, "total_others": total_others}


def calcIPv6Usage():
    used = 0
    total = calcAddressNum6(8)
    inet6numFileList = os.listdir(DATAPREFIX + "inet6num")
    for inet6numFile in inet6numFileList:
        inet6num = ipaddress.ip_network(inet6numFile.replace("_", "/"))
        if inet6num.prefixlen > 8:
            used = used + calcAddressNum6(inet6num.prefixlen)
    return {"used": used, "total": total}


def getASNInfo(search_str):
    whois = dict()
    if search_str.startswith("AS"):
        search_str = search_str[2:]
    try:
        f = open(DATAPREFIX + "aut-num/AS" + search_str)
        asnInfo = _getRegistryKeys(f)
        if asnInfo["mnt-by"][0] == "DN42-MNT":
            if "admin-c" in asnInfo:
                asnInfo["contact-info"] = getPerson(asnInfo["admin-c"][0])
        else:
            mntInfo = getMNT(asnInfo["mnt-by"][0])
            if "admin-c" in mntInfo:
                asnInfo["contact-info"] = getPerson(mntInfo["admin-c"][0])
                if "auth" in mntInfo:
                    asnInfo["contact-info"]["pgp-fingerprint"] = mntInfo["auth"][0]
        return asnInfo
    except IOError:
        return {}


def getASNList():
    returnList = []
    ASNList = os.listdir(DATAPREFIX + "aut-num")
    for ASNFile in ASNList:
        f = open(DATAPREFIX + "aut-num/" + ASNFile, "r")
        asn = _getRegistryKeys(f)
        returnList.append(asn["aut-num"][0])
    return returnList


def getASNRoute(asn, routeList=None):
    returnList = {
        "ipv4": [],
        "ipv6": []
    }
    if not asn.startswith("AS"):
        asn = "AS" + asn
    if routeList == None:
        routeList = getRouteList()
    for route in routeList["ipv4"]:
        if asn in route["origin"]:
            returnList["ipv4"].append(route)
    for route in routeList["ipv6"]:
        if asn in route["origin"]:
            returnList["ipv6"].append(route)
    return returnList


if __name__ == "__main__":
    print(getASNInfo("4242421331"))
    print(getASNName("4242421332"))
    print(getASNRoute("4242421331"))
