"""
py-osrm-backend: A Python implementation of OSRM backend core functionality.

This package provides routing capabilities using OpenStreetMap data.
"""

__version__ = "0.1.0"
__author__ = "GalTechDev"

# Public API
from osrm.structures.graph import Graph
from osrm.engine.dijkstra import DijkstraEngine
from osrm.extractor.graph_builder import GraphBuilder

__all__ = [
    "__version__",
    "__author__",
    "Graph",
    "DijkstraEngine",
    "GraphBuilder",
]
