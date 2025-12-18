import unittest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from osrm.extractor.graph_builder import GraphBuilder

class TestExtractor(unittest.TestCase):
    
    def test_build_graph_from_osm(self):
        sample_osm = os.path.join(os.path.dirname(__file__), 'sample.osm')
        builder = GraphBuilder()
        graph = builder.build_graph(sample_osm)
        
        # Check nodes were parsed
        self.assertIn(1, graph.nodes)
        self.assertIn(2, graph.nodes)
        self.assertIn(3, graph.nodes)
        self.assertIn(4, graph.nodes)
        
        # Check edges from way 100 (1-2-3 bidirectional)
        edges_from_1 = graph.get_edges(1)
        targets_from_1 = [e.target for e in edges_from_1]
        self.assertIn(2, targets_from_1) # from way 100
        self.assertIn(4, targets_from_1) # from way 101
        
        # Check bidirectional
        edges_from_2 = graph.get_edges(2)
        targets_from_2 = [e.target for e in edges_from_2]
        self.assertIn(1, targets_from_2)
        self.assertIn(3, targets_from_2)

if __name__ == '__main__':
    unittest.main()
