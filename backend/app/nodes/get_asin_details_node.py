import asyncio
from typing import Dict, Any, List
from app import models
from .base_node import BaseNodeExecutor


class GetAsinDetailsNodeExecutor(BaseNodeExecutor):
    """Executor for get_asin_details node type"""
    
    def get_node_type(self) -> str:
        return "get_asin_details"
    
    async def _execute_get_asin_details_for_item(self, asin: str) -> Dict[str, Any]:
        """Execute ASIN details lookup for a single ASIN"""
        product = self.db.query(models.MyProduct).filter(models.MyProduct.asin == asin).first()
        
        if not product:
            raise ValueError(f"Product not found for ASIN: {asin}")
        
        return {
            "asin": product.asin,
            "title": product.title,
            "description": product.description,
            "bullet_points": product.bullet_points
        }
    
    def execute(self, node: Dict, results: Dict, edges: List[Dict], user=None) -> Dict[str, Any]:
        """Execute get_asin_details node - processes single ASIN only"""
        # Get input data from previous node
        input_data = self._get_input_data(node, results, edges)
        
        # Handle different input types
        if input_data["type"] == "single_asin":
            # Normal single execution
            asin = input_data["value"]
        elif input_data["type"] == "single_loop_item":
            # Single item from loop iteration
            asin = input_data["value"]
        else:
            raise ValueError(f"Expected single_asin or single_loop_item input, got {input_data['type']}")
        
        # Process single ASIN
        item_result = asyncio.run(self._execute_get_asin_details_for_item(asin))
        
        return {
            "type": "product_details",
            "value": item_result
        }
