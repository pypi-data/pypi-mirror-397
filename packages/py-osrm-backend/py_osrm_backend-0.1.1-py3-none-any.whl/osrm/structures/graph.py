from dataclasses import dataclass, field
from typing import Dict, List, Tuple
import math

@dataclass
class Node:
    id: int
    lat: float
    lon: float
    tags: Dict[str, str] = field(default_factory=dict)

@dataclass
class Edge:
    source: int
    target: int
    weight: float
    name: str = ""

class Graph:
    def __init__(self):
        self.nodes: Dict[int, Node] = {}
        self.adj_list: Dict[int, List[Edge]] = {}

    def add_node(self, id: int, lat: float, lon: float, tags: Dict[str, str] = None):
        if tags is None:
            tags = {}
        self.nodes[id] = Node(id, lat, lon, tags)
        if id not in self.adj_list:
            self.adj_list[id] = []

    def add_edge(self, source: int, target: int, weight: float, name: str = ""):
        if source not in self.nodes or target not in self.nodes:
            raise ValueError(f"Source {source} or Target {target} node not found in graph.")
        
        edge = Edge(source, target, weight, name)
        self.adj_list[source].append(edge)

    def get_edges(self, node_id: int) -> List[Edge]:
        return self.adj_list.get(node_id, [])

    def get_node(self, node_id: int) -> Node:
        return self.nodes.get(node_id)
    
    def __len__(self):
        return len(self.nodes)

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) * math.sin(dlat / 2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) * math.sin(dlon / 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c
