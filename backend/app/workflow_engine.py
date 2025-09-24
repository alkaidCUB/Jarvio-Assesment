from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app import models
from app.nodes.node_factory import NodeExecutorFactory


class WorkflowEngine:
    def __init__(self, db: Session):
        self.db = db
        self.loop_stack = []  # Stack for nested loop contexts
    
    def execute_workflow(self, workflow: models.Workflow, user: models.User) -> Dict[str, Any]:
        """Execute a workflow and return results"""
        flow_data = workflow.flow_data
        nodes = flow_data.get("nodes", [])
        edges = flow_data.get("edges", [])
        
        # Build execution graph
        execution_order = self._get_execution_order(nodes, edges)
        results = {}
        
        try:
            # Initialize loop stack for this workflow execution
            self.loop_stack = []
            
            for node_id in execution_order:
                node = next(n for n in nodes if n["id"] == node_id)
                node_type = node.get("type")
                
                if node_type == "loop":
                    # Execute loop node and push new loop context
                    loop_result = self._execute_single_node(node, results, edges, user)
                    results[node_id] = loop_result
                    self._push_loop_context(loop_result)
                    
                elif node_type == "merge":
                    # Execute merge node and pop current loop context
                    results[node_id] = self._execute_single_node(node, results, edges, user)
                    self._pop_loop_context()
                    
                elif self._is_in_loop_context():
                    # We're in a loop context - execute this node for each item in current loop
                    current_loop = self._get_current_loop_context()
                    loop_results = []
                    
                    for i, item in enumerate(current_loop["items"]):
                        # Update current loop context
                        current_loop["current_index"] = i
                        current_loop["current_item"] = item
                        
                        # Create temporary results with scoped variables
                        temp_results = results.copy()
                        
                        # Add single loop item for current execution
                        temp_results[current_loop["loop_id"]] = {
                            "type": "single_loop_item",
                            "value": item,
                            "loop_index": i,
                            "loop_depth": self._get_loop_depth() - 1,
                            "scoped_vars": self._build_scoped_variables()
                        }
                        
                        # Execute the node for this specific item
                        item_result = self._execute_single_node(node, temp_results, edges, user)
                        loop_results.append(item_result)
                    
                    # Store all the individual results
                    results[node_id] = {
                        "type": "loop_execution_results",
                        "results": loop_results,
                        "loop_id": current_loop["loop_id"],
                        "loop_depth": current_loop["depth"],
                        "count": len(loop_results)
                    }
                    
                else:
                    # Normal single execution outside of any loop
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
    
    def _push_loop_context(self, loop_result: Dict[str, Any]) -> None:
        """Push a new loop context onto the stack"""
        loop_context = {
            "loop_id": loop_result["loop_id"],
            "items": loop_result["items"],
            "current_index": 0,
            "current_item": loop_result["items"][0] if loop_result["items"] else None,
            "total_items": len(loop_result["items"]),
            "scope_vars": {},
            "depth": len(self.loop_stack)  # Track nesting depth
        }
        self.loop_stack.append(loop_context)
    
    def _pop_loop_context(self) -> Dict[str, Any]:
        """Pop the current loop context from the stack"""
        return self.loop_stack.pop() if self.loop_stack else None
    
    def _get_current_loop_context(self) -> Dict[str, Any]:
        """Get the current (top) loop context without removing it"""
        return self.loop_stack[-1] if self.loop_stack else None
    
    def _is_in_loop_context(self) -> bool:
        """Check if we're currently executing within any loop"""
        return len(self.loop_stack) > 0
    
    def _get_loop_depth(self) -> int:
        """Get current loop nesting depth"""
        return len(self.loop_stack)
    
    def _build_scoped_variables(self) -> Dict[str, Any]:
        """Build scoped variables from all active loop contexts"""
        scoped_vars = {}
        for i, context in enumerate(self.loop_stack):
            # Add loop-specific variables
            scoped_vars[f"loop_{i}_item"] = context["current_item"]
            scoped_vars[f"loop_{i}_index"] = context["current_index"]
            scoped_vars[f"loop_{i}_total"] = context["total_items"]
            
            # Add custom scope variables
            scoped_vars.update(context["scope_vars"])
        
        return scoped_vars
    