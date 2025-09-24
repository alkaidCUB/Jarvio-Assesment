from typing import Dict, Any, List
from .base_node import BaseNodeExecutor


class MergeNodeExecutor(BaseNodeExecutor):
    """Executor for merge node type"""
    
    def get_node_type(self) -> str:
        return "merge"
    
    def execute(self, node: Dict, results: Dict, edges: List[Dict], user=None) -> Dict[str, Any]:
        """Execute merge node - pure collector that gathers loop execution results"""
        
        # Get input data from previous node (should be loop execution results)
        input_data = self._get_input_data(node, results, edges)
        
        # Check if this is loop execution results
        if input_data["type"] != "loop_execution_results":
            raise ValueError(f"Merge node expected loop_execution_results, got {input_data['type']}")
        
        # Extract the individual results from the loop execution
        individual_results = input_data["results"]
        collected_values = []
        
        for result in individual_results:
            if result["type"] == "product_details":
                collected_values.append(result["value"])
            else:
                # For other result types, just collect the whole result
                collected_values.append(result)
        
        # Determine output format based on the type of results
        if all(isinstance(item, dict) and "asin" in item for item in collected_values):
            # ASIN-based results - format as product details table
            return {
                "type": "product_details_table",
                "value": collected_values,
                "count": len(collected_values)
            }
        else:
            # Generic results - format as generic table
            return {
                "type": "generic_results_table", 
                "value": collected_values,
                "count": len(collected_values)
            }
