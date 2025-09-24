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
        
        # Handle different input types for nested loops
        if input_data.get("type") == "loop_execution_results":
            # This is a nested loop - extract array from loop execution results
            # For nested loops, we need to get the array from each individual result
            loop_results = input_data.get("results", [])
            if not loop_results:
                raise ValueError("Loop node received empty loop_execution_results")
            
            # For nested loops, we typically want to loop over the results themselves
            # Each result becomes an item to loop over
            items = []
            for result in loop_results:
                if result.get("type") == "asin_list":
                    # If the result is an asin_list, use its value
                    items.extend(result["value"])
                elif result.get("value"):
                    # Otherwise, use the result value directly
                    if isinstance(result["value"], list):
                        items.extend(result["value"])
                    else:
                        items.append(result["value"])
                else:
                    # Use the whole result as an item
                    items.append(result)
            
        elif isinstance(input_data.get("value"), list):
            # Standard array input
            items = input_data["value"]
            
        else:
            raise ValueError(f"Loop node requires array input or loop_execution_results, got {input_data.get('type', 'unknown')}")
        
        # Set up loop context - this will be used by subsequent nodes
        return {
            "type": "loop_items",
            "items": items,
            "loop_id": node["id"],
            "count": len(items),
            "loop_active": True,
            "original_input_type": input_data["type"]
        }
