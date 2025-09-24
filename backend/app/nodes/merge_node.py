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
        
        # Check if this is loop execution results or nested merge results
        if input_data["type"] == "loop_execution_results":
            # Standard loop execution results
            pass
        elif input_data["type"] in ["product_details_table", "nested_results_table", "generic_results_table"]:
            # This is a nested merge - convert table back to loop_execution_results format
            input_data = {
                "type": "loop_execution_results",
                "results": [{"type": "product_details", "value": item} for item in input_data["value"]],
                "loop_depth": input_data.get("loop_depth", 0)
            }
        else:
            raise ValueError(f"Merge node expected loop_execution_results or table results, got {input_data['type']}")
        
        # Extract the individual results from the loop execution
        individual_results = input_data["results"]
        loop_depth = input_data.get("loop_depth", 0)
        
        # Handle nested results based on depth and content
        if self._contains_nested_results(individual_results):
            # Nested loop results - preserve hierarchy or flatten based on strategy
            return self._merge_nested_results(individual_results, loop_depth)
        else:
            # Single-level results - use existing logic
            return self._merge_flat_results(individual_results, loop_depth)
    
    def _contains_nested_results(self, results: List) -> bool:
        """Check if results contain nested loop execution results"""
        for result in results:
            if isinstance(result, dict) and result.get("type") == "loop_execution_results":
                return True
        return False
    
    def _merge_nested_results(self, results: List, depth: int) -> Dict[str, Any]:
        """Merge nested loop results with hierarchical structure"""
        collected_values = []
        
        for result in results:
            if result.get("type") == "loop_execution_results":
                # This is a nested loop result - recursively process
                nested_values = self._flatten_nested_loop_results(result["results"])
                collected_values.extend(nested_values)
            elif result.get("type") == "product_details":
                collected_values.append(result["value"])
            else:
                # For other result types, collect the whole result
                collected_values.append(result)
        
        return {
            "type": "nested_results_table",
            "value": collected_values,
            "count": len(collected_values),
            "nesting_depth": depth,
            "structure": "flattened"  # Could be "hierarchical" in future
        }
    
    def _merge_flat_results(self, results: List, depth: int) -> Dict[str, Any]:
        """Merge flat (single-level) loop results"""
        collected_values = []
        
        for result in results:
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
                "count": len(collected_values),
                "loop_depth": depth
            }
        else:
            # Generic results - format as generic table
            return {
                "type": "generic_results_table", 
                "value": collected_values,
                "count": len(collected_values),
                "loop_depth": depth
            }
    
    def _flatten_nested_loop_results(self, nested_results: List) -> List:
        """Recursively flatten nested loop results"""
        flattened = []
        
        for result in nested_results:
            if isinstance(result, dict) and result.get("type") == "loop_execution_results":
                # Recursively flatten deeper nesting
                flattened.extend(self._flatten_nested_loop_results(result["results"]))
            elif isinstance(result, dict) and result.get("type") == "product_details":
                flattened.append(result["value"])
            else:
                flattened.append(result)
        
        return flattened
