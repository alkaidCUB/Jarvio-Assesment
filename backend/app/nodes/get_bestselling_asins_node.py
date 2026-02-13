from typing import Dict, Any, List
from app import models
from .base_node import BaseNodeExecutor


class GetBestSellingAsinsNodeExecutor(BaseNodeExecutor):
    """Executor for get_bestselling_asins node type"""
    
    def get_node_type(self) -> str:
        return "get_bestselling_asins"
    
    def execute(self, node: Dict, results: Dict, edges: List[Dict], user=None) -> Dict[str, Any]:
        """Execute get_bestselling_asins node"""
        # Get topCount from node data, default to 5
        top_count = node.get("data", {}).get("topCount", 5)
        
        # Query top products by sales amount
        products = (
            self.db.query(models.MyProduct)
            .order_by(models.MyProduct.sales_amount.desc())
            .limit(top_count)
            .all()
        )
        
        # Extract ASINs
        asins = [product.asin for product in products]
        
        return {
            "type": "asin_list",
            "value": asins,
            "count": len(asins)
        }
