import networkx as nx
from typing import List, Dict, Any, Optional
import logging

class GraphEngine:
    def __init__(self, graph_store, vector_engine):
        self.graph_store = graph_store
        self.vector_engine = vector_engine
        self.graph = nx.DiGraph()
        self.logger = logging.getLogger(__name__)
    
    async def traverse(self, start_node: str, max_depth: int = 2) -> List[Dict]:
        if start_node not in self.graph:
            return []
        visited = set()
        result = []
        queue = [(start_node, 0)]
        while queue:
            node_id, depth = queue.pop(0)
            if node_id in visited or depth > max_depth:
                continue
            visited.add(node_id)
            result.append({'id': node_id, 'depth': depth})
            for neighbor in self.graph.neighbors(node_id):
                queue.append((neighbor, depth + 1))
        return result
