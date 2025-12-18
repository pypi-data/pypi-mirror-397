import xml.etree.ElementTree as ET
from typing import Dict, List, Tuple
from ..structures.graph import Node

class OSMParser:
    def parse_nodes(self, file_path: str) -> Dict[int, Node]:
        """Parses nodes from an OSM XML file."""
        nodes = {}
        context = ET.iterparse(file_path, events=("start", "end"))
        context = iter(context)
        event, root = next(context)

        for event, elem in context:
            if event == "end" and elem.tag == "node":
                node_id = int(elem.attrib['id'])
                lat = float(elem.attrib['lat'])
                lon = float(elem.attrib['lon'])
                tags = {}
                for tag in elem.findall("tag"):
                    tags[tag.attrib['k']] = tag.attrib['v']
                
                nodes[node_id] = Node(node_id, lat, lon, tags)
                root.clear() # Clear memory
        
        return nodes

    def parse_ways(self, file_path: str) -> List[Dict]:
        """Parses ways from an OSM XML file.
        Returns a list of dictionaries with 'id', 'nodes' (list of ids), and 'tags'.
        """
        ways = []
        context = ET.iterparse(file_path, events=("start", "end"))
        context = iter(context)
        event, root = next(context)

        for event, elem in context:
            if event == "end" and elem.tag == "way":
                way_id = int(elem.attrib['id'])
                node_refs = []
                for nd in elem.findall("nd"):
                    node_refs.append(int(nd.attrib['ref']))
                
                tags = {}
                for tag in elem.findall("tag"):
                    tags[tag.attrib['k']] = tag.attrib['v']
                
                ways.append({
                    'id': way_id,
                    'nodes': node_refs,
                    'tags': tags
                })
                root.clear()
        return ways
