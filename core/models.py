from dataclasses import dataclass, field
from typing import TypedDict, Any

class NodeAttr(TypedDict):
    asn: str
    name: str
    id: Any
    color: str
    size: float
    centrality: str

class EdgeAttr(TypedDict):
    sourceID: int
    targetID: int

class GraphOutput(TypedDict):
    created: int
    nodes: list[NodeAttr]
    edges: list[EdgeAttr]

@dataclass
class RegistryConfig:
    registry_path: str
    data_path: str = "data"

@dataclass
class ASNData:
    aut_num: list[str] = field(default_factory=list)
    mnt_by: list[str] = field(default_factory=list)
    description: list[str] = field(default_factory=list)
    admin_c: list[str] = field(default_factory=list)
    tech_c: list[str] = field(default_factory=list)
    contact_info: dict[str, Any] = field(default_factory=dict)
    extras: dict[str, Any] = field(default_factory=dict)
