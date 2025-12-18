import unittest
import sys
import os
import json
from unittest.mock import MagicMock, patch

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from osrm.server.api import app, init_app, _find_nearest_node
from osrm.structures.graph import Graph, Node

class TestAPIWaypoints(unittest.TestCase):
    
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        
        # Mock graph and engine
        self.graph = Graph()
        self.graph.add_node(1, 0, 0)
        self.graph.add_node(2, 0, 1)
        self.graph.add_node(3, 0, 2)
        
        # 1->2->3
        self.graph.add_edge(1, 2, 10.0)
        self.graph.add_edge(2, 3, 10.0)
        
        # Patch the global graph in api
        patchER = patch('osrm.server.api.graph', self.graph)
        patchER.start()
        self.addCleanup(patchER.stop)
        
        # Mock engine
        data_engine = MagicMock()
        data_engine.shortest_path.side_effect = self.mock_shortest_path
        
        patchER2 = patch('osrm.server.api.engine', data_engine)
        patchER2.start()
        self.addCleanup(patchER2.stop)

    def mock_shortest_path(self, start, end):
        if start == 1 and end == 2:
            return 10.0, [1, 2]
        if start == 2 and end == 3:
            return 10.0, [2, 3]
        if start == 1 and end == 3: # Direct query should fail if engine only supports direct edges, but here we mock it
            return 20.0, [1, 2, 3]
        return float('inf'), []

    def test_two_waypoints(self):
        # Route 1->2
        resp = self.app.get('/route/v1/driving/0,0;1,0') # lon,lat -> matches node 1 (0,0) and 2 (0,1) reversed? Wait. 
        # Node 1: lat=0, lon=0. Node 2: lat=0, lon=1.
        # Request: lon,lat. 0,0 -> Node 1. 1,0 -> Node 2.
        
        # My graph setup:
        # Node 1: 0, 0
        # Node 2: 0, 1 (lat=0, lon=1)
        
        data = json.loads(resp.data)
        self.assertEqual(data['code'], 'Ok')
        self.assertEqual(data['routes'][0]['distance'], 10.0)

    def test_three_waypoints(self):
        # Route 1->2->3
        # Node 3: lat=0, lon=2
        resp = self.app.get('/route/v1/driving/0,0;1,0;2,0')
        
        data = json.loads(resp.data)
        self.assertEqual(data['code'], 'Ok')
        self.assertEqual(data['routes'][0]['distance'], 20.0)
        
        # Check geometry stitching
        # Path 1->2 is [1, 2]
        # Path 2->3 is [2, 3]
        # Result should be [1, 2, 2, 3] -> deduplicated -> [1, 2, 3]
        # Geometry is list of coords.
        geometry = data['routes'][0]['geometry']['coordinates']
        self.assertEqual(len(geometry), 3)
        self.assertEqual(geometry[0], [0.0, 0.0])
        self.assertEqual(geometry[1], [1.0, 0.0])
        self.assertEqual(geometry[2], [2.0, 0.0])

if __name__ == '__main__':
    unittest.main()
