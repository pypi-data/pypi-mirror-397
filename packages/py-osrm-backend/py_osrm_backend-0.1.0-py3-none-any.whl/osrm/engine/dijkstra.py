import heapq
from typing import List, Optional, Tuple, Dict
from ..structures.graph import Graph, Node

class DijkstraEngine:
    def __init__(self, graph: Graph):
        self.graph = graph

    def shortest_path(self, start_node_id: int, end_node_id: int) -> Tuple[float, List[int]]:
        """
        Computes shortest path using Dijkstra's algorithm.
        Returns (total_distance, list_of_node_ids).
        Returns (infinity, []) if no path found.
        """
        if start_node_id not in self.graph.nodes or end_node_id not in self.graph.nodes:
             raise ValueError("Start or End node not in graph")

        # Priority queue stores (distance, node_id)
        pq = [(0.0, start_node_id)]
        distances: Dict[int, float] = {start_node_id: 0.0}
        previous: Dict[int, int] = {start_node_id: None}
        visited = set()

        while pq:
            current_dist, current_node = heapq.heappop(pq)

            if current_node in visited:
                continue
            visited.add(current_node)

            if current_node == end_node_id:
                break

            for edge in self.graph.get_edges(current_node):
                neighbor = edge.target
                if neighbor in visited:
                    continue
                
                new_dist = current_dist + edge.weight
                
                if new_dist < distances.get(neighbor, float('inf')):
                    distances[neighbor] = new_dist
                    previous[neighbor] = current_node
                    heapq.heappush(pq, (new_dist, neighbor))

        if end_node_id not in distances or distances[end_node_id] == float('inf'):
            return float('inf'), []

        # Reconstruct path
        path = []
        current = end_node_id
        while current is not None:
            path.append(current)
            current = previous[current]
        path.reverse()

        return distances[end_node_id], path
