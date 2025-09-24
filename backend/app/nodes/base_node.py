from abc import ABC, abstractmethod
from typing import Dict, Any, List


class BaseNodeExecutor(ABC):
    """Abstract base class for all node executors (Strategy Pattern)"""
    
    def __init__(self, db_session):
        """Initialize with database session"""
        self.db = db_session
    
    @abstractmethod
    def execute(self, node: Dict, results: Dict, edges: List[Dict], user=None) -> Dict[str, Any]:
        """
        Execute the node logic
        
        Args:
            node: The node configuration
            results: Current workflow results
            edges: Workflow edges for finding connections
            user: User context (optional)
            
        Returns:
            Dict containing the execution result
        """
        pass
    
    @abstractmethod
    def get_node_type(self) -> str:
        """Return the node type this executor handles"""
        pass
    
    def _get_input_data(self, node: Dict, results: Dict, edges: List[Dict]) -> Dict[str, Any]:
        """Helper method to get input data from previous node"""
        input_node_id = None
        for edge in edges:
            if edge["target"] == node["id"]:
                input_node_id = edge["source"]
                break
        
        if not input_node_id or input_node_id not in results:
            raise ValueError(f"No input found for node {node['id']}")
        
        return results[input_node_id]
