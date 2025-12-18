from flask import Flask, request, jsonify
from ..extractor.graph_builder import GraphBuilder
from ..engine.dijkstra import DijkstraEngine
import os

app = Flask(__name__)
graph = None
engine = None

def init_app(osm_file_path: str):
    global graph, engine
    if not os.path.exists(osm_file_path):
        raise FileNotFoundError(f"OSM file not found: {osm_file_path}")
    
    print("Initializing Graph...")
    builder = GraphBuilder()
    graph = builder.build_graph(osm_file_path)
    engine = DijkstraEngine(graph)
    print("Initialization complete.")

@app.route('/route/v1/driving/<coords>')
def route(coords):
    # Expected format: lon1,lat1;lon2,lat2
    # This is a simplified OSRM-like endpoint
    try:
        parts = coords.split(';')
        if len(parts) < 2:
            return jsonify({'code': 'InvalidRequest', 'message': 'At least two coordinates required'}), 400
        
        waypoints = []
        for part in parts:
            try:
                lon, lat = map(float, part.split(','))
                node = _find_nearest_node(lat, lon)
                if not node:
                     return jsonify({'code': 'NoSegment', 'message': f'Could not find node near {lat},{lon}'}), 400
                waypoints.append(node)
            except ValueError:
                return jsonify({'code': 'InvalidRequest', 'message': 'Coordinates must be lon,lat'}), 400

        total_dist = 0.0
        full_path_ids = []

        for i in range(len(waypoints) - 1):
            start_node = waypoints[i]
            end_node = waypoints[i+1]
            
            dist, path = engine.shortest_path(start_node.id, end_node.id)
            
            if not path:
                 return jsonify({'code': 'NoRoute', 'message': 'No route found between waypoints'}), 404
            
            total_dist += dist
            
            # Append path (avoid duplicating the connection node)
            if i > 0:
                full_path_ids.extend(path[1:])
            else:
                full_path_ids.extend(path)

        return jsonify({
            'code': 'Ok',
            'routes': [{
                'distance': total_dist,
                'duration': total_dist / 13.8, # Rough estimate (50km/h)
                'geometry': _encode_path_geometry(full_path_ids)
            }]
        })

    except Exception as e:
        return jsonify({'code': 'Error', 'message': str(e)}), 500

def _find_nearest_node(lat, lon):
    # O(N) naive search - improved to check connectivity
    nearest = None
    min_dist = float('inf')
    
    # Optimization: pre-filter routable nodes if possible, or just check during scan
    # For now, check connectivity on the fly
    for node_id, node in graph.nodes.items():
        # strict check: must have outgoing edges or be target of edges? 
        # Simplest is: strictly outgoing (start node) or incoming (end node).
        # But graph is directed.
        # Ideally, we want a node that is part of the largest component.
        # For now, just check if it has ANY edges connected (in adjacency list)
        if node_id not in graph.adj_list or not graph.adj_list[node_id]:
             # Also check if it is a target of some edge? (for end node)
             # But our graph is usually bidirectional for roads unless oneway.
             # If oneway, a node might have 0 outgoing but valid incoming.
             # However, typical road nodes have at least one outgoing (continuing the road).
             # Let's stick to "has outgoing edges" for simplicity as a "routable" proxy.
             continue

        d = (node.lat - lat)**2 + (node.lon - lon)**2
        if d < min_dist:
            min_dist = d
            nearest = node
    return nearest

def _encode_path_geometry(path_ids):
    # Return list of [lon, lat] for simplicity
    coords = []
    for nid in path_ids:
        node = graph.get_node(nid)
        coords.append([node.lon, node.lat])
    return {'type': 'LineString', 'coordinates': coords}

if __name__ == '__main__':
    # Default to a sample file or env var
    osm_path = os.environ.get('OSRM_FILE', 'data.osm')
    init_app(osm_path)
    app.run(debug=True, port=5000)
