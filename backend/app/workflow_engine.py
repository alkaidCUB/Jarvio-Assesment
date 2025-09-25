from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app import models
from app.nodes.node_factory import NodeExecutorFactory


class WorkflowEngine:
    def __init__(self, db: Session):
        self.db = db
    
    def execute_workflow(self, workflow: models.Workflow, user: models.User) -> Dict[str, Any]:
        """Execute a workflow and return results"""
        flow_data = workflow.flow_data
        nodes = flow_data.get("nodes", [])
        edges = flow_data.get("edges", [])
        
        # Validate Loop→Merge pairs before execution
        self._validate_loop_merge_pairs(nodes, edges)
        
        # Build execution graph
        execution_order = self._get_execution_order(nodes, edges)
        results = {}
        
        try:
            # Track active loop context
            active_loop = None
            
            for node_id in execution_order:
                node = next(n for n in nodes if n["id"] == node_id)
                node_type = node.get("type")
                
                if node_type == "loop":
                    # Execute loop node using Strategy pattern and set active loop context
                    loop_result = self._execute_single_node(node, results, edges, user)
                    results[node_id] = loop_result
                    active_loop = {
                        "loop_id": node_id,
                        "items": loop_result["items"],
                        "current_index": 0
                    }
                    
                elif node_type == "merge":
                    # Execute merge node using Strategy pattern and clear active loop
                    results[node_id] = self._execute_single_node(node, results, edges, user)
                    active_loop = None
                    
                elif active_loop is not None:
                    # We're in a loop context - execute this node for each loop item
                    loop_results = []
                    for i, item in enumerate(active_loop["items"]):
                        # Create a temporary single-item input for this iteration
                        temp_results = results.copy()
                        temp_results[active_loop["loop_id"]] = {
                            "type": "single_loop_item",
                            "value": item,
                            "loop_index": i
                        }
                        
                        # Execute the node for this specific item
                        item_result = self._execute_single_node(node, temp_results, edges, user)
                        loop_results.append(item_result)
                    
                    # Store all the individual results
                    results[node_id] = {
                        "type": "loop_execution_results",
                        "results": loop_results,
                        "loop_id": active_loop["loop_id"],
                        "count": len(loop_results)
                    }
                    
                else:
                    # Normal single execution outside of loop
                    results[node_id] = self._execute_single_node(node, results, edges, user)
            
            return {"status": "success", "results": results}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _execute_single_node(self, node: Dict, results: Dict, edges: List[Dict], user) -> Dict[str, Any]:
        """Execute a single node using Strategy pattern"""
        node_type = node.get("type")
        
        # Use factory to get the appropriate executor
        factory = NodeExecutorFactory(self.db)
        executor = factory.create_executor(node_type)
        
        # Execute using the strategy
        return executor.execute(node, results, edges, user)
    
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
    
    def _validate_loop_merge_pairs(self, nodes: List[Dict], edges: List[Dict]) -> None:
        """Validate that every Loop node has a corresponding Merge node"""
        loop_nodes = [n for n in nodes if n.get("type") == "loop"]
        
        for loop_node in loop_nodes:
            # Find if this loop has a corresponding merge by checking if there's a path from loop to merge
            has_merge = False
            for edge in edges:
                if edge["source"] == loop_node["id"]:
                    # Check if we can reach a merge node from this loop
                    if self._can_reach_merge_from_loop(loop_node["id"], edges, nodes):
                        has_merge = True
                        break
            
            if not has_merge:
                raise ValueError(f"Loop node '{loop_node['id']}' must have a corresponding Merge node")
    
    def _can_reach_merge_from_loop(self, loop_id: str, edges: List[Dict], nodes: List[Dict]) -> bool:
        """Check if we can reach a merge node from the given loop node"""
        visited = set()
        queue = [loop_id]
        
        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)
            
            # Check if current node is a merge
            current_node = next((n for n in nodes if n["id"] == current), None)
            if current_node and current_node.get("type") == "merge":
                return True
            
            # Add all targets of current node to queue
            for edge in edges:
                if edge["source"] == current:
                    queue.append(edge["target"])
        
        return False
    