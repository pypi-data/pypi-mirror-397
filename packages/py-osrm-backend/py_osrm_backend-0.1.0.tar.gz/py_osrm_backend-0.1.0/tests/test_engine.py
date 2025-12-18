import unittest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from osrm.structures.graph import Graph
from osrm.engine.dijkstra import DijkstraEngine

class TestDijkstra(unittest.TestCase):
    
    def setUp(self):
        """Create a simple test graph:
           1 --2--> 2 --3--> 3
           |                 ^
           +-------6---------+
        """
        self.graph = Graph()
        self.graph.add_node(1, 0, 0)
        self.graph.add_node(2, 0, 1)
        self.graph.add_node(3, 0, 2)
        
        self.graph.add_edge(1, 2, 2.0)  # 1 -> 2, weight 2
        self.graph.add_edge(2, 3, 3.0)  # 2 -> 3, weight 3
        self.graph.add_edge(1, 3, 6.0)  # Direct 1 -> 3, weight 6
        
        self.engine = DijkstraEngine(self.graph)

    def test_shortest_path_via_intermediate(self):
        dist, path = self.engine.shortest_path(1, 3)
        # Shortest is 1->2->3 = 5, not direct 1->3 = 6
        self.assertEqual(dist, 5.0)
        self.assertEqual(path, [1, 2, 3])
    
    def test_direct_path(self):
        dist, path = self.engine.shortest_path(1, 2)
        self.assertEqual(dist, 2.0)
        self.assertEqual(path, [1, 2])

    def test_no_path(self):
        # Add an isolated node
        self.graph.add_node(99, 10, 10)
        dist, path = self.engine.shortest_path(1, 99)
        self.assertEqual(dist, float('inf'))
        self.assertEqual(path, [])

if __name__ == '__main__':
    unittest.main()
