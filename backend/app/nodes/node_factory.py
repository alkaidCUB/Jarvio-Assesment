from typing import Dict
from .base_node import BaseNodeExecutor
from .get_bestselling_asins_node import GetBestSellingAsinsNodeExecutor
from .get_asin_by_index_node import GetAsinByIndexNodeExecutor
from .get_asin_details_node import GetAsinDetailsNodeExecutor
from .loop_node import LoopNodeExecutor
from .merge_node import MergeNodeExecutor


class NodeExecutorFactory:
    """Factory for creating node executors (Factory Pattern)"""
    
    def __init__(self, db_session):
        """Initialize factory with database session"""
        self.db_session = db_session
        self._executors = {}
        self._register_executors()
    
    def _register_executors(self):
        """Register all available node executors"""
        executor_classes = [
            GetBestSellingAsinsNodeExecutor,
            GetAsinByIndexNodeExecutor,
            GetAsinDetailsNodeExecutor,
            LoopNodeExecutor,
            MergeNodeExecutor,
        ]
        
        for executor_class in executor_classes:
            executor = executor_class(self.db_session)
            self._executors[executor.get_node_type()] = executor
    
    def create_executor(self, node_type: str) -> BaseNodeExecutor:
        """
        Create a node executor for the given node type
        
        Args:
            node_type: The type of node to create executor for
            
        Returns:
            BaseNodeExecutor instance for the node type
            
        Raises:
            ValueError: If node type is not supported
        """
        if node_type not in self._executors:
            raise ValueError(f"Unsupported node type: {node_type}")
        
        return self._executors[node_type]
    
    def get_supported_node_types(self) -> list:
        """Get list of all supported node types"""
        return list(self._executors.keys())
