from typing import Dict, Any, Union

def format_content_display(value_dict: Union[Dict[str, str], Any]) -> str:
    if not isinstance(value_dict, dict):
        return str(value_dict)
    items = [v for _, v in value_dict.items() if v]
    return " | ".join(items) if items else ""

def format_title_display(key: str, value_dict: Dict[str, str], start: str, end: str) -> str:
    val_str = "<br>".join([f"{k}: {v}" for k, v in value_dict.items()])
    return f"Obj: {key}<br>{val_str}<br>Start: {start}<br>End: {end}"
