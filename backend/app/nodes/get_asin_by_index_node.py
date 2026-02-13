from typing import Dict, Any, List
from .base_node import BaseNodeExecutor


class GetAsinByIndexNodeExecutor(BaseNodeExecutor):
    """Executor for get_asin_by_index node type"""
    
    def get_node_type(self) -> str:
        return "get_asin_by_index"
    
    def execute(self, node: Dict, results: Dict, edges: List[Dict], user=None) -> Dict[str, Any]:
        """Execute get_asin_by_index node"""
        # Get index from node data, default to 0
        index = node.get("data", {}).get("index", 0)
        
        # Get input data from previous node
        input_data = self._get_input_data(node, results, edges)
        
        if input_data["type"] != "asin_list":
            raise ValueError(f"Expected asin_list input, got {input_data['type']}")
        
        asin_list = input_data["value"]
        if index >= len(asin_list):
            raise ValueError(f"Index {index} out of range for list of length {len(asin_list)}")
        
        selected_asin = asin_list[index]
        return {"type": "single_asin", "value": selected_asin}
