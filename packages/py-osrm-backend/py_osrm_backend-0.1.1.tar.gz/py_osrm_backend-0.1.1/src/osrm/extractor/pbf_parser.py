"""
OSM PBF Parser using osmium.

Requires: pip install osmium
"""

try:
    import osmium
    OSMIUM_AVAILABLE = True
except ImportError:
    OSMIUM_AVAILABLE = False

from typing import Dict, List
from ..structures.graph import Node


class PBFNodeHandler(osmium.SimpleHandler):
    """Handler to extract nodes from PBF file."""
    
    def __init__(self):
        super().__init__()
        self.nodes: Dict[int, Node] = {}
    
    def node(self, n):
        tags = dict(n.tags)
        self.nodes[n.id] = Node(n.id, n.location.lat, n.location.lon, tags)


class PBFWayHandler(osmium.SimpleHandler):
    """Handler to extract ways from PBF file."""
    
    def __init__(self):
        super().__init__()
        self.ways: List[Dict] = []
    
    def way(self, w):
        tags = dict(w.tags)
        node_refs = [n.ref for n in w.nodes]
        self.ways.append({
            'id': w.id,
            'nodes': node_refs,
            'tags': tags
        })


class OSMPBFParser:
    """Parser for OSM PBF files."""
    
    def __init__(self):
        if not OSMIUM_AVAILABLE:
            raise ImportError("osmium is required for PBF parsing. Install with: pip install osmium")
    
    def parse_nodes(self, file_path: str) -> Dict[int, Node]:
        """Parse nodes from a PBF file."""
        handler = PBFNodeHandler()
        handler.apply_file(file_path, locations=True)
        return handler.nodes
    
    def parse_ways(self, file_path: str) -> List[Dict]:
        """Parse ways from a PBF file."""
        handler = PBFWayHandler()
        handler.apply_file(file_path)
        return handler.ways
