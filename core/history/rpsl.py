from typing import Dict

def parse_rpsl(content: str) -> Dict[str, str]:
    data: Dict[str, str] = {}
    lines = content.split("\n")

    for line in lines:
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("%"):
            continue

        if ":" in line:
            parts = line.split(":", 1)
            key = parts[0].strip()
            val = parts[1].strip()
            
            if key in data:
                data[key] = f"{data[key]}, {val}"
            else:
                data[key] = val
    return data

def is_valid_aut_num(filename: str) -> bool:
    if not filename.upper().startswith("AS"):
        return False
    clean_name = filename.upper().replace("AS", "")
    return clean_name.isdigit()
