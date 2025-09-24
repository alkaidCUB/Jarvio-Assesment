from typing import Dict, Any, List
from .base_node import BaseNodeExecutor


class LoopNodeExecutor(BaseNodeExecutor):
    """Executor for loop node type"""
    
    def get_node_type(self) -> str:
        return "loop"
    
    def execute(self, node: Dict, results: Dict, edges: List[Dict], user=None) -> Dict[str, Any]:
        """Execute loop node - splits array input into individual items for processing"""
        # Get input data from previous node
        input_data = self._get_input_data(node, results, edges)
        
        # Generic: Accept any array-like input (asin_list, user_list, etc.)
        if not isinstance(input_data.get("value"), list):
            raise ValueError(f"Loop node requires array input, got {input_data.get('type', 'unknown')}")
        
        # Set up loop context - this will be used by subsequent nodes
        return {
            "type": "loop_items",
            "items": input_data["value"],
            "loop_id": node["id"],
            "count": len(input_data["value"]),
            "loop_active": True,
            "original_input_type": input_data["type"]
        }
