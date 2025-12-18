"""
Contraction Hierarchies (CH) implementation.

CH is a speed-up technique for shortest path queries:
1. Preprocessing: Contract nodes in order of importance, adding shortcuts
2. Query: Bidirectional Dijkstra on the augmented graph (upward searches only)
"""

import heapq
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, field
from ..structures.graph import Graph, Edge, haversine_distance

@dataclass
class CHNode:
    """Node with contraction hierarchy level."""
    id: int
    level: int = 0  # Higher = more important
    contracted: bool = False

@dataclass
class Shortcut:
    """A shortcut edge bypassing a contracted node."""
    source: int
    target: int
    weight: float
    via: int  # The contracted node this shortcut bypasses

class ContractionHierarchies:
    """
    Contraction Hierarchies for fast shortest path queries.
    
    Usage:
        ch = ContractionHierarchies(graph)
        ch.preprocess()
        distance, path = ch.query(start, end)
    """
    
    def __init__(self, graph: Graph):
        self.original_graph = graph
        self.ch_nodes: Dict[int, CHNode] = {}
        self.upward_edges: Dict[int, List[Edge]] = {}  # Edges to higher-level nodes
        self.downward_edges: Dict[int, List[Edge]] = {}  # Edges to lower-level nodes
        self.shortcuts: List[Shortcut] = []
        self._initialize()
    
    def _initialize(self):
        """Initialize CH nodes from original graph."""
        for node_id in self.original_graph.nodes:
            self.ch_nodes[node_id] = CHNode(id=node_id)
            self.upward_edges[node_id] = []
            self.downward_edges[node_id] = []
    
    def _compute_node_importance(self, node_id: int, contracted: Set[int]) -> int:
        """
        Compute importance of a node for contraction ordering.
        Lower importance = contract first.
        
        Simplified heuristic: edge difference + contracted neighbors
        """
        # Count edges to non-contracted neighbors
        in_edges = 0
        out_edges = 0
        neighbors_in = []
        neighbors_out = []
        
        for edge in self.original_graph.get_edges(node_id):
            if edge.target not in contracted:
                out_edges += 1
                neighbors_out.append(edge.target)
        
        # Count incoming edges (check all nodes)
        for other_id, edges in self.original_graph.adj_list.items():
            if other_id in contracted:
                continue
            for edge in edges:
                if edge.target == node_id:
                    in_edges += 1
                    neighbors_in.append(other_id)
        
        # Shortcuts needed = in_edges * out_edges (worst case)
        shortcuts_needed = in_edges * out_edges
        
        # Edge difference = shortcuts added - edges removed
        edge_diff = shortcuts_needed - (in_edges + out_edges)
        
        # Contracted neighbors penalty
        contracted_neighbors = sum(1 for n in neighbors_in + neighbors_out if n in contracted)
        
        return edge_diff + contracted_neighbors
    
    def preprocess(self, max_nodes: int = None):
        """
        Contract nodes in order of importance.
        
        Args:
            max_nodes: Limit preprocessing to first N nodes (for testing)
        """
        print("CH Preprocessing: Computing contraction order...")
        contracted: Set[int] = set()
        node_ids = list(self.original_graph.nodes.keys())
        
        if max_nodes:
            node_ids = node_ids[:max_nodes]
        
        # Priority queue: (importance, node_id)
        pq = []
        for node_id in node_ids:
            importance = self._compute_node_importance(node_id, contracted)
            heapq.heappush(pq, (importance, node_id))
        
        level = 0
        total = len(node_ids)
        
        while pq:
            _, node_id = heapq.heappop(pq)
            
            if node_id in contracted:
                continue
            
            # Lazy update: recompute importance
            new_importance = self._compute_node_importance(node_id, contracted)
            if pq and new_importance > pq[0][0]:
                heapq.heappush(pq, (new_importance, node_id))
                continue
            
            # Contract this node
            self._contract_node(node_id, contracted)
            self.ch_nodes[node_id].level = level
            self.ch_nodes[node_id].contracted = True
            contracted.add(node_id)
            level += 1
            
            if level % 100 == 0:
                print(f"  Contracted {level}/{total} nodes...")
        
        # Build upward/downward edge lists
        self._build_ch_graph()
        print(f"CH Preprocessing complete. {len(self.shortcuts)} shortcuts created.")
    
    def _contract_node(self, node_id: int, contracted: Set[int]):
        """Contract a node by adding necessary shortcuts."""
        # Find incoming edges from non-contracted nodes
        incoming = []
        for other_id, edges in self.original_graph.adj_list.items():
            if other_id in contracted or other_id == node_id:
                continue
            for edge in edges:
                if edge.target == node_id:
                    incoming.append((other_id, edge.weight))
        
        # Find outgoing edges to non-contracted nodes
        outgoing = []
        for edge in self.original_graph.get_edges(node_id):
            if edge.target not in contracted and edge.target != node_id:
                outgoing.append((edge.target, edge.weight))
        
        # Add shortcuts if needed
        for u, w_in in incoming:
            for v, w_out in outgoing:
                if u == v:
                    continue
                
                shortcut_weight = w_in + w_out
                
                # Check if shortcut is necessary (witness search)
                # Simplified: always add shortcut (proper implementation would do witness search)
                shortcut = Shortcut(u, v, shortcut_weight, node_id)
                self.shortcuts.append(shortcut)
                
                # Add to graph temporarily for further contractions
                self.original_graph.adj_list[u].append(
                    Edge(u, v, shortcut_weight, f"shortcut_via_{node_id}")
                )
    
    def _build_ch_graph(self):
        """Build upward and downward edge lists based on node levels."""
        # Include original edges + shortcuts
        all_edges = []
        for node_id, edges in self.original_graph.adj_list.items():
            for edge in edges:
                all_edges.append(edge)
        
        for edge in all_edges:
            src_level = self.ch_nodes[edge.source].level
            tgt_level = self.ch_nodes[edge.target].level
            
            if tgt_level > src_level:
                self.upward_edges[edge.source].append(edge)
            else:
                self.downward_edges[edge.source].append(edge)
    
    def query(self, start: int, end: int) -> Tuple[float, List[int]]:
        """
        Bidirectional Dijkstra query on CH graph.
        
        Returns (distance, path).
        """
        if start not in self.ch_nodes or end not in self.ch_nodes:
            raise ValueError("Start or end node not in graph")
        
        # Forward search (upward from start)
        dist_forward: Dict[int, float] = {start: 0.0}
        prev_forward: Dict[int, Optional[int]] = {start: None}
        pq_forward = [(0.0, start)]
        visited_forward: Set[int] = set()
        
        # Backward search (upward from end, on reversed graph)
        dist_backward: Dict[int, float] = {end: 0.0}
        prev_backward: Dict[int, Optional[int]] = {end: None}
        pq_backward = [(0.0, end)]
        visited_backward: Set[int] = set()
        
        best_dist = float('inf')
        meeting_node = None
        
        while pq_forward or pq_backward:
            # Forward step
            if pq_forward:
                d, u = heapq.heappop(pq_forward)
                if u not in visited_forward and d < best_dist:
                    visited_forward.add(u)
                    
                    # Check if backward search reached this node
                    if u in dist_backward:
                        total = d + dist_backward[u]
                        if total < best_dist:
                            best_dist = total
                            meeting_node = u
                    
                    # Relax upward edges
                    for edge in self.upward_edges.get(u, []):
                        v = edge.target
                        new_dist = d + edge.weight
                        if new_dist < dist_forward.get(v, float('inf')):
                            dist_forward[v] = new_dist
                            prev_forward[v] = u
                            heapq.heappush(pq_forward, (new_dist, v))
            
            # Backward step (using downward edges in reverse = upward in reverse graph)
            if pq_backward:
                d, u = heapq.heappop(pq_backward)
                if u not in visited_backward and d < best_dist:
                    visited_backward.add(u)
                    
                    if u in dist_forward:
                        total = d + dist_forward[u]
                        if total < best_dist:
                            best_dist = total
                            meeting_node = u
                    
                    # In backward search, go upward = follow edges where this node is target
                    for other_id, edges in self.original_graph.adj_list.items():
                        for edge in edges:
                            if edge.target == u:
                                # Check if this is an upward edge from other's perspective
                                if self.ch_nodes[u].level > self.ch_nodes[other_id].level:
                                    v = other_id
                                    new_dist = d + edge.weight
                                    if new_dist < dist_backward.get(v, float('inf')):
                                        dist_backward[v] = new_dist
                                        prev_backward[v] = u
                                        heapq.heappush(pq_backward, (new_dist, v))
        
        if meeting_node is None:
            return float('inf'), []
        
        # Reconstruct path
        path = self._reconstruct_path(prev_forward, prev_backward, meeting_node)
        return best_dist, path
    
    def _reconstruct_path(self, prev_forward: Dict, prev_backward: Dict, meeting: int) -> List[int]:
        """Reconstruct the full path from forward and backward predecessors."""
        # Forward path: start -> meeting
        path_forward = []
        node = meeting
        while node is not None:
            path_forward.append(node)
            node = prev_forward.get(node)
        path_forward.reverse()
        
        # Backward path: meeting -> end
        path_backward = []
        node = prev_backward.get(meeting)
        while node is not None:
            path_backward.append(node)
            node = prev_backward.get(node)
        
        return path_forward + path_backward
