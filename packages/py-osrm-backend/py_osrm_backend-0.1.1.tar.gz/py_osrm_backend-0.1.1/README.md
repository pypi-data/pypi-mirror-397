# py-osrm-backend

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://img.shields.io/pypi/v/py-osrm-backend.svg)](https://pypi.org/project/py-osrm-backend/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Flask](https://img.shields.io/badge/Flask-API-green.svg)](https://flask.palletsprojects.com/)
[![OpenStreetMap](https://img.shields.io/badge/OSM-Compatible-brightgreen.svg)](https://www.openstreetmap.org/)
[![Documentation](https://img.shields.io/badge/docs-GitHub%20Pages-blue.svg)](https://galtechdev.github.io/py-osrm-backend/)

A Python implementation of core OSRM (Open Source Routing Machine) functionality.

## Installation

```bash
pip install py-osrm-backend
```

## Features

- **OSM Parsing**: Parse `.osm` XML files to extract nodes and ways
- **Graph Building**: Build a routable graph with haversine distance weights
- **Routing**: Dijkstra's algorithm for shortest path computation
- **API Server**: Flask-based REST API compatible with OSRM-like endpoints

## Quick Start

```python
from osrm.extractor.graph_builder import GraphBuilder
from osrm.engine.dijkstra import DijkstraEngine

# Build graph from OSM
builder = GraphBuilder()
graph = builder.build_graph("your_map.osm")

# Route
engine = DijkstraEngine(graph)
distance, path = engine.shortest_path(start_id, end_id)
print(f"Distance: {distance} km, Path: {path}")
```

## Run Tests

```bash
python -m unittest discover -s tests -v
```

## License

MIT
