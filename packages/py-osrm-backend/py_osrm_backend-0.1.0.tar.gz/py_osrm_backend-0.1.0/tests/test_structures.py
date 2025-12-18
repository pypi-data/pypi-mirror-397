import unittest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from osrm.structures.graph import Graph, Node, Edge, haversine_distance

class TestGraph(unittest.TestCase):
    
    def test_add_node(self):
        g = Graph()
        g.add_node(1, 48.8566, 2.3522)
        self.assertIn(1, g.nodes)
        self.assertEqual(g.nodes[1].lat, 48.8566)
        self.assertEqual(g.nodes[1].lon, 2.3522)
    
    def test_add_edge(self):
        g = Graph()
        g.add_node(1, 48.8566, 2.3522)
        g.add_node(2, 48.8580, 2.3540)
        g.add_edge(1, 2, 0.5, "Test Road")
        
        edges = g.get_edges(1)
        self.assertEqual(len(edges), 1)
        self.assertEqual(edges[0].target, 2)
        self.assertEqual(edges[0].weight, 0.5)
    
    def test_haversine_distance(self):
        # Paris to London approx 344 km
        dist = haversine_distance(48.8566, 2.3522, 51.5074, -0.1278)
        self.assertAlmostEqual(dist, 344, delta=5)

class TestNode(unittest.TestCase):
    def test_node_creation(self):
        node = Node(id=1, lat=10.0, lon=20.0, tags={'name': 'Test'})
        self.assertEqual(node.id, 1)
        self.assertEqual(node.tags['name'], 'Test')

if __name__ == '__main__':
    unittest.main()
