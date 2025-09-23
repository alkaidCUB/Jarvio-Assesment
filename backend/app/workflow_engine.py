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
                    results[node_id] = self._execute_get_asin_details(node, results, edges)
            
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