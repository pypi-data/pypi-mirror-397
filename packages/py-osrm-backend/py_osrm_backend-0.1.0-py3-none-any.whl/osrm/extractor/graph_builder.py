from typing import Dict, List
from ..structures.graph import Graph, haversine_distance
from .parser import OSMParser

# Try to import PBF parser (optional dependency)
try:
    from .pbf_parser import OSMPBFParser
    PBF_AVAILABLE = True
except ImportError:
    PBF_AVAILABLE = False

class GraphBuilder:
    def __init__(self):
        self.xml_parser = OSMParser()
        self.pbf_parser = OSMPBFParser() if PBF_AVAILABLE else None

    def build_graph(self, file_path: str) -> Graph:
        graph = Graph()
        
        # Detect format
        is_pbf = file_path.endswith('.pbf')
        
        if is_pbf:
            if not PBF_AVAILABLE:
                raise ImportError("osmium required for PBF. Install with: pip install osmium")
            parser = self.pbf_parser
        else:
            parser = self.xml_parser
        
        # 1. Parse Nodes
        print(f"Parsing nodes from {file_path}...")
        nodes = parser.parse_nodes(file_path)
        for node in nodes.values():
            graph.add_node(node.id, node.lat, node.lon, node.tags)
            
        # 2. Parse Ways and build Edges
        print(f"Parsing ways from {file_path}...")
        ways = parser.parse_ways(file_path)
        
        print("Building graph...")
        for way in ways:
            tags = way['tags']
            # Basic filter: only allow highways
            if 'highway' not in tags:
                continue
            
            node_refs = way['nodes']
            # One-way logic can be complex; simplified here: assumed bidirectional unless specified
            oneway = tags.get('oneway') == 'yes'
            
            for i in range(len(node_refs) - 1):
                u_id = node_refs[i]
                v_id = node_refs[i+1]
                
                if u_id not in graph.nodes or v_id not in graph.nodes:
                    continue # Skip if node missing (e.g. pbf bounds)
                
                u_node = graph.nodes[u_id]
                v_node = graph.nodes[v_id]
                
                dist = haversine_distance(u_node.lat,u_node.lon, v_node.lat, v_node.lon)
                name = tags.get('name', '')
                
                # Add forward edge
                graph.add_edge(u_id, v_id, dist, name)
                
                # Add backward edge if not one-way
                if not oneway:
                    graph.add_edge(v_id, u_id, dist, name)
                    
        print(f"Graph built with {len(graph.nodes)} nodes.")
        return graph
