import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from osrm.structures.graph import Graph
from osrm.engine.contraction_hierarchies import ContractionHierarchies

class TestContractionHierarchies(unittest.TestCase):
    
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
        
        # Bidirectional edges for CH
        self.graph.add_edge(1, 2, 2.0)
        self.graph.add_edge(2, 1, 2.0)
        self.graph.add_edge(2, 3, 3.0)
        self.graph.add_edge(3, 2, 3.0)
        self.graph.add_edge(1, 3, 6.0)
        self.graph.add_edge(3, 1, 6.0)

    def test_preprocessing(self):
        ch = ContractionHierarchies(self.graph)
        ch.preprocess()
        
        # All nodes should be contracted
        for node in ch.ch_nodes.values():
            self.assertTrue(node.contracted)
    
    def test_query_shortest_path(self):
        ch = ContractionHierarchies(self.graph)
        ch.preprocess()
        
        dist, path = ch.query(1, 3)
        # Shortest is 1->2->3 = 5
        self.assertEqual(dist, 5.0)
        self.assertIn(1, path)
        self.assertIn(3, path)

if __name__ == '__main__':
    unittest.main()
