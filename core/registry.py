from pathlib import Path
from typing import Any, Iterator
from .config import settings

def get_file_content(path: Path) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    if not path.exists():
        return result

    try:
        with path.open("r", encoding="utf-8", errors="ignore") as f:
            prev_key = ""
            for line in f:
                if line.startswith(" ") and prev_key:
                    result[prev_key].append(line.lstrip())
                elif line.startswith("+") and prev_key:
                    result[prev_key].append("\n")
                elif ":" in line:
                    key, val = line.split(":", 1)
                    key = key.strip()
                    val = val.strip()
                    if key not in result:
                        result[key] = []
                    result[key].append(val)
                    prev_key = key
    except OSError:
        pass
    return result

def get_asn_name(asn: str) -> str:
    if asn.startswith("AS"):
        asn = asn[2:]
    
    path = settings.REGISTRY_DATA / "aut-num" / f"AS{asn}"
    if not path.exists():
        return "Null"

    try:
        with path.open("r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if line.startswith("as-name:"):
                    return line.split(":", 1)[1].strip()
    except OSError:
        pass
    return "Null"

def check_asn_exists(asn: str) -> bool:
    if asn.startswith("AS"):
        asn = asn[2:]
    return (settings.REGISTRY_DATA / "aut-num" / f"AS{asn}").exists()

def iter_registry_files(subdir: str) -> Iterator[tuple[str, dict[str, list[str]]]]:
    target_dir = settings.REGISTRY_DATA / subdir
    if not target_dir.exists():
        return
    
    for item in target_dir.iterdir():
        if item.is_file():
            yield item.name, get_file_content(item)

def get_asn_info(asn_str: str) -> dict[str, Any]:
    if asn_str.startswith("AS"):
        asn_str = asn_str[2:]
    
    asn_path = settings.REGISTRY_DATA / "aut-num" / f"AS{asn_str}"
    info = get_file_content(asn_path)
    if not info:
        return {}
    
    mnt_by = info.get("mnt-by", [])
    if mnt_by:
        first_mnt = mnt_by[0]
        if first_mnt == "DN42-MNT" and "admin-c" in info:
            info["contact-info"] = _get_person_or_role(info["admin-c"][0])
        else:
            mnt_info = get_file_content(settings.REGISTRY_DATA / "mntner" / first_mnt)
            if "admin-c" in mnt_info:
                info["contact-info"] = _get_person_or_role(mnt_info["admin-c"][0])
                if "auth" in mnt_info:
                    info["contact-info"]["pgp-fingerprint"] = mnt_info["auth"][0]
    return info

def _get_person_or_role(handle: str) -> dict[str, list[str]]:
    p_path = settings.REGISTRY_DATA / "person" / handle
    if p_path.exists():
        return get_file_content(p_path)
    
    r_path = settings.REGISTRY_DATA / "role" / handle
    if r_path.exists():
        return get_file_content(r_path)
    
    return {}

def get_route_list() -> dict[str, list[dict]]:
    routes: dict[str, list[dict]] = {"ipv4": [], "ipv6": []}
    
    # IPv4
    for fname, content in iter_registry_files("route"):
        content["inetnum"] = get_file_content(settings.REGISTRY_DATA / "inetnum" / fname)
        if "inetnum" in content["inetnum"]:
            content["inetnum"].pop("inetnum")
        routes["ipv4"].append(content)
        
    # IPv6
    for fname, content in iter_registry_files("route6"):
        content["inetnum"] = get_file_content(settings.REGISTRY_DATA / "inet6num" / fname)
        if "inet6num" in content["inetnum"]:
            content["inetnum"].pop("inet6num")
        routes["ipv6"].append(content)
        
    return routes

def get_asn_list() -> list[str]:
    return [
        f.name.replace("AS", "") 
        for f in (settings.REGISTRY_DATA / "aut-num").iterdir()
        if f.is_file() and f.name.startswith("AS")
    ]
