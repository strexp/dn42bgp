from typing import List, Dict, TypedDict, Optional

class ConfigItem(TypedDict):
    dir: str
    key_field: str
    track_fields: List[str]

class StateValue(TypedDict):
    val: Dict[str, str]
    start: str

class TimelineItem(TypedDict):
    value: Dict[str, str]
    start: str
    end: str

class AppState(TypedDict):
    last_commit: Optional[str]
    timeline_data: Dict[str, Dict[str, List[TimelineItem]]]
    active_states: Dict[str, Dict[str, StateValue]]

CONFIG: Dict[str, ConfigItem] = {
    "aut-num": {
        "dir": "aut-num",
        "key_field": "aut-num",
        "track_fields": ["as-name", "mnt-by"],
    },
    "dns": {
        "dir": "dns", 
        "key_field": "domain", 
        "track_fields": ["mnt-by"]
    },
    "mntner": {
        "dir": "mntner", 
        "key_field": "mntner", 
        "track_fields": []
    },
    "registry": {
        "dir": "registry", 
        "key_field": "registry", 
        "track_fields": []
    },
    "organisation": {
        "dir": "organisation",
        "key_field": "organisation",
        "track_fields": ["org-name", "mnt-by"],
    },
}
