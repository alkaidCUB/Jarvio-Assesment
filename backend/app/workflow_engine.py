from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app import models


class WorkflowEngine:
    def __init__(self, db: Session):
        self.db = db
    
    def execute_workflow(self, workflow: models.Workflow, user: models.User) -> Dict[str, Any]:
        """Execute a workflow and return results"""
        flow_data = workflow.flow_data
        nodes = flow_data.get("nodes", [])
        edges = flow_data.get("edges", [])
        
        # Build execution graph
        execution_order = self._get_execution_order(nodes, edges)
        results = {}
        
        try:
            for node_id in execution_order:
                node = next(n for n in nodes if n["id"] == node_id)
                node_type = node.get("type")
                
                if node_type == "get_bestselling_asins":
                    results[node_id] = self._execute_get_bestselling_asins(node, user)
                elif node_type == "get_asin_by_index":
                    results[node_id] = self._execute_get_asin_by_index(node, results, edges)
                elif node_type == "get_asin_details":
                    # Check if input is from a loop - if so, skip execution (merge will handle it)
                    input_node_id = self._get_input_node_id(node, edges)
                    if input_node_id and input_node_id in results and results[input_node_id].get("type") == "loop_items":
                        # Skip execution - merge node will handle this
                        results[node_id] = {"type": "loop_placeholder", "message": "Handled by merge node"}
                    else:
                        results[node_id] = self._execute_get_asin_details(node, results, edges)
                elif node_type == "loop":
                    results[node_id] = self._execute_loop(node, results, edges)
                elif node_type == "merge":
                    results[node_id] = self._execute_merge(node, results, edges, nodes)
            
            return {"status": "success", "results": results}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _get_execution_order(self, nodes: List[Dict], edges: List[Dict]) -> List[str]:
        """Determine execution order based on node dependencies"""
        # Simple topological sort
        in_degree = {node["id"]: 0 for node in nodes}
        
        for edge in edges:
            in_degree[edge["target"]] += 1
        
        queue = [node_id for node_id, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            node_id = queue.pop(0)
            result.append(node_id)
            
            for edge in edges:
                if edge["source"] == node_id:
                    in_degree[edge["target"]] -= 1
                    if in_degree[edge["target"]] == 0:
                        queue.append(edge["target"])
        
        return result
    
    def _execute_get_bestselling_asins(self, node: Dict, user: models.User) -> Dict[str, Any]:
        """Execute get_bestselling_asins node"""
        node_data = node.get("data", {})
        top_count = node_data.get("topCount", 10)
        
        products = (
            self.db.query(models.MyProduct)
            .order_by(models.MyProduct.sales_amount.desc())
            .limit(top_count)
            .all()
        )
        
        asins = [product.asin for product in products]
        return {"type": "asin_list", "value": asins, "count": len(asins)}
    
    def _execute_get_asin_by_index(self, node: Dict, results: Dict, edges: List[Dict]) -> Dict[str, Any]:
        """Execute get_asin_by_index node"""
        node_data = node.get("data", {})
        index = node_data.get("index", 0)
        
        # Find input from previous node
        input_node_id = None
        for edge in edges:
            if edge["target"] == node["id"]:
                input_node_id = edge["source"]
                break
        
        if not input_node_id or input_node_id not in results:
            raise ValueError(f"No input found for node {node['id']}")
        
        input_data = results[input_node_id]
        if input_data["type"] != "asin_list":
            raise ValueError(f"Expected asin_list input, got {input_data['type']}")
        
        asin_list = input_data["value"]
        if index >= len(asin_list):
            raise ValueError(f"Index {index} out of range for list of length {len(asin_list)}")
        
        selected_asin = asin_list[index]
        return {"type": "single_asin", "value": selected_asin}
    
    def _execute_get_asin_details(self, node: Dict, results: Dict, edges: List[Dict]) -> Dict[str, Any]:
        """Execute get_asin_details node"""
        # Find input from previous node
        input_node_id = None
        for edge in edges:
            if edge["target"] == node["id"]:
                input_node_id = edge["source"]
                break
        
        if not input_node_id or input_node_id not in results:
            raise ValueError(f"No input found for node {node['id']}")
        
        input_data = results[input_node_id]
        if input_data["type"] != "single_asin":
            raise ValueError(f"Expected single_asin input, got {input_data['type']}")
        
        asin = input_data["value"]
        product = self.db.query(models.MyProduct).filter(models.MyProduct.asin == asin).first()
        
        if not product:
            raise ValueError(f"Product not found for ASIN: {asin}")
        
        return {
            "type": "product_details",
            "value": {
                "asin": product.asin,
                "title": product.title,
                "description": product.description,
                "bullet_points": product.bullet_points
            }
        }
    
    def _execute_loop(self, node: Dict, results: Dict, edges: List[Dict]) -> Dict[str, Any]:
        """Execute loop node - splits array input into individual items"""
        # Find input from previous node
        input_node_id = None
        for edge in edges:
            if edge["target"] == node["id"]:
                input_node_id = edge["source"]
                break
        
        if not input_node_id or input_node_id not in results:
            raise ValueError(f"No input found for node {node['id']}")
        
        input_data = results[input_node_id]
        if input_data["type"] != "asin_list":
            raise ValueError(f"Loop node requires asin_list input, got {input_data['type']}")
        
        # Return metadata for merge node to process
        return {
            "type": "loop_items",
            "items": input_data["value"],
            "loop_id": node["id"],
            "count": len(input_data["value"])
        }
    
    def _execute_merge(self, node: Dict, results: Dict, edges: List[Dict], nodes: List[Dict]) -> Dict[str, Any]:
        """Execute merge node - collects individual results into table"""
        # Find corresponding loop node by traversing backwards
        loop_node_id = self._find_paired_loop(node["id"], edges)
        
        if not loop_node_id or loop_node_id not in results:
            raise ValueError(f"Merge node {node['id']} has no corresponding Loop node")
        
        loop_data = results[loop_node_id]
        if loop_data["type"] != "loop_items":
            raise ValueError(f"Expected loop_items from loop node, got {loop_data['type']}")
        
        # Process each item through the path between loop and merge
        collected_results = []
        items = loop_data["items"]
        
        for i, item in enumerate(items):
            try:
                # Execute the path between loop and merge for this item
                item_result = self._execute_loop_path(item, loop_node_id, node["id"], nodes, edges, results)
                collected_results.append(item_result)
            except Exception as e:
                raise ValueError(f"Failed processing ASIN {item} in loop: {str(e)}")
        
        # Format as table
        return {
            "type": "product_details_table",
            "value": collected_results,
            "count": len(collected_results)
        }
    
    def _find_paired_loop(self, merge_node_id: str, edges: List[Dict]) -> str:
        """Find the loop node that pairs with this merge node"""
        # Traverse backwards from merge to find loop
        visited = set()
        queue = [merge_node_id]
        
        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)
            
            # Add all sources of current node to queue
            for edge in edges:
                if edge["target"] == current:
                    source_id = edge["source"]
                    # Check if this source is a loop node by checking if it starts with "loop"
                    if source_id.startswith("loop"):
                        return source_id
                    queue.append(source_id)
        
        return None
    
    def _execute_loop_path(self, item: str, loop_node_id: str, merge_node_id: str, 
                          nodes: List[Dict], edges: List[Dict], results: Dict) -> Dict[str, Any]:
        """Execute the path between loop and merge for a single item"""
        # Find nodes between loop and merge
        path_nodes = self._get_path_nodes(loop_node_id, merge_node_id, edges)
        
        # Create temporary results with the single item
        temp_results = results.copy()
        temp_results[loop_node_id] = {"type": "single_asin", "value": item}
        
        # Execute each node in the path
        for node_id in path_nodes:
            node = next(n for n in nodes if n["id"] == node_id)
            node_type = node.get("type")
            
            if node_type == "get_asin_details":
                temp_results[node_id] = self._execute_get_asin_details(node, temp_results, edges)
            # Add other node types as needed
        
        # Return the final result from the last node in path
        if path_nodes:
            last_node_id = path_nodes[-1]
            return temp_results[last_node_id]["value"]
        
        return {"asin": item, "title": "Unknown", "description": "No details", "bullet_points": []}
    
    def _get_path_nodes(self, start_id: str, end_id: str, edges: List[Dict]) -> List[str]:
        """Get the nodes in the path between start and end (excluding start and end)"""
        # Simple path finding - assumes linear path for now
        path = []
        current = start_id
        
        while current != end_id:
            # Find next node
            next_node = None
            for edge in edges:
                if edge["source"] == current:
                    next_node = edge["target"]
                    break
            
            if not next_node or next_node == end_id:
                break
                
            path.append(next_node)
            current = next_node
        
        return path
    
    def _get_input_node_id(self, node: Dict, edges: List[Dict]) -> str:
        """Helper method to get the input node ID for a given node"""
        for edge in edges:
            if edge["target"] == node["id"]:
                return edge["source"]
        return None