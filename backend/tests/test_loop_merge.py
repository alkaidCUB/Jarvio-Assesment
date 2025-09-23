import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_loop_merge_workflow_via_api():
    """Test the Loop + Merge workflow through the live API"""
    
    # Login to get token
    login_response = client.post(
        "/auth/login",
        json={"email": "demo@example.com", "password": "demo123"}
    )
    assert login_response.status_code == 200
    token_data = login_response.json()
    assert "access_token" in token_data
    
    headers = {"Authorization": f"Bearer {token_data['access_token']}"}
    
    # Create a Loop + Merge workflow
    loop_merge_workflow = {
        "name": "Loop Merge Test Workflow",
        "description": "Test workflow for Loop and Merge nodes",
        "flow_data": {
            "nodes": [
                {
                    "id": "get-asins-loop-test",
                    "type": "get_bestselling_asins",
                    "data": {"topCount": 3}
                },
                {
                    "id": "loop-node-test",
                    "type": "loop",
                    "data": {}
                },
                {
                    "id": "get-details-loop-test",
                    "type": "get_asin_details",
                    "data": {}
                },
                {
                    "id": "merge-node-test",
                    "type": "merge",
                    "data": {}
                }
            ],
            "edges": [
                {
                    "id": "edge-1",
                    "source": "get-asins-loop-test",
                    "target": "loop-node-test"
                },
                {
                    "id": "edge-2", 
                    "source": "loop-node-test",
                    "target": "get-details-loop-test"
                },
                {
                    "id": "edge-3",
                    "source": "get-details-loop-test",
                    "target": "merge-node-test"
                }
            ]
        }
    }
    
    # Create the workflow
    create_response = client.post("/workflows/", json=loop_merge_workflow, headers=headers)
    assert create_response.status_code == 200
    workflow_data = create_response.json()
    workflow_id = workflow_data["id"]
    
    # Execute the workflow
    run_response = client.post(f"/workflows/{workflow_id}/run", headers=headers)
    assert run_response.status_code == 200
    run_data = run_response.json()
    
    # Verify the workflow executed successfully
    assert run_data["status"] == "completed"
    assert "results" in run_data
    
    results = run_data["results"]
    
    # Test Step 1: Get ASINs
    assert "get-asins-loop-test" in results
    asins_result = results["get-asins-loop-test"]
    assert asins_result["type"] == "asin_list"
    assert "value" in asins_result
    assert len(asins_result["value"]) == 3  # We requested top 3
    assert asins_result["count"] == 3
    
    # Test Step 2: Loop Node
    assert "loop-node-test" in results
    loop_result = results["loop-node-test"]
    assert loop_result["type"] == "loop_items"
    assert "items" in loop_result
    assert loop_result["items"] == asins_result["value"]  # Should be same ASINs
    assert loop_result["loop_id"] == "loop-node-test"
    assert loop_result["count"] == 3
    
    # Test Step 3: Merge Node (Final Result)
    assert "merge-node-test" in results
    merge_result = results["merge-node-test"]
    assert merge_result["type"] == "product_details_table"
    assert "value" in merge_result
    assert len(merge_result["value"]) == 3  # Should have details for all 3 ASINs
    assert merge_result["count"] == 3
    
    # Verify each product has the required fields
    for i, product in enumerate(merge_result["value"]):
        assert "asin" in product
        assert "title" in product
        assert "description" in product
        assert "bullet_points" in product
        
        # Verify the ASIN matches one from our original list
        assert product["asin"] in asins_result["value"]


def test_loop_node_validation():
    """Test that Loop node properly validates its input"""
    
    # Login
    login_response = client.post(
        "/auth/login", 
        json={"email": "demo@example.com", "password": "demo123"}
    )
    assert login_response.status_code == 200
    headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}
    
    # Create a workflow with invalid Loop input (should fail)
    invalid_loop_workflow = {
        "name": "Invalid Loop Test",
        "description": "Test Loop node with wrong input type",
        "flow_data": {
            "nodes": [
                {
                    "id": "get-asins-invalid",
                    "type": "get_bestselling_asins",
                    "data": {"topCount": 2}
                },
                {
                    "id": "get-index-invalid",
                    "type": "get_asin_by_index", 
                    "data": {"index": 0}
                },
                {
                    "id": "loop-invalid",
                    "type": "loop",
                    "data": {}
                }
            ],
            "edges": [
                {"id": "edge-1", "source": "get-asins-invalid", "target": "get-index-invalid"},
                {"id": "edge-2", "source": "get-index-invalid", "target": "loop-invalid"}
            ]
        }
    }
    
    # Create and run the workflow
    create_response = client.post("/workflows/", json=invalid_loop_workflow, headers=headers)
    assert create_response.status_code == 200
    workflow_id = create_response.json()["id"]
    
    # Execute - should fail because Loop gets single_asin instead of asin_list
    run_response = client.post(f"/workflows/{workflow_id}/run", headers=headers)
    assert run_response.status_code == 200
    run_data = run_response.json()
    
    # Should fail with validation error
    assert run_data["status"] == "failed"
    assert "error_message" in run_data
    assert "Loop node requires asin_list input" in run_data["error_message"]


def test_merge_without_loop():
    """Test that Merge node fails without a corresponding Loop node"""
    
    # Login
    login_response = client.post(
        "/auth/login",
        json={"email": "demo@example.com", "password": "demo123"}
    )
    assert login_response.status_code == 200
    headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}
    
    # Create workflow with Merge but no Loop
    no_loop_workflow = {
        "name": "Merge Without Loop Test",
        "description": "Test Merge node without Loop",
        "flow_data": {
            "nodes": [
                {
                    "id": "get-asins-no-loop",
                    "type": "get_bestselling_asins",
                    "data": {"topCount": 2}
                },
                {
                    "id": "merge-no-loop",
                    "type": "merge",
                    "data": {}
                }
            ],
            "edges": [
                {"id": "edge-1", "source": "get-asins-no-loop", "target": "merge-no-loop"}
            ]
        }
    }
    
    # Create and run
    create_response = client.post("/workflows/", json=no_loop_workflow, headers=headers)
    assert create_response.status_code == 200
    workflow_id = create_response.json()["id"]
    
    run_response = client.post(f"/workflows/{workflow_id}/run", headers=headers)
    assert run_response.status_code == 200
    run_data = run_response.json()
    
    # Should fail - no corresponding Loop node
    assert run_data["status"] == "failed"
    assert "error_message" in run_data
    assert "no corresponding Loop node" in run_data["error_message"]


def test_loop_merge_data_flow():
    """Test the complete data flow through Loop + Merge"""
    
    # Login
    login_response = client.post(
        "/auth/login",
        json={"email": "demo@example.com", "password": "demo123"}
    )
    assert login_response.status_code == 200
    headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}
    
    # Create workflow with specific topCount to verify data flow
    data_flow_workflow = {
        "name": "Data Flow Test",
        "description": "Test data flow through Loop + Merge",
        "flow_data": {
            "nodes": [
                {"id": "get-asins-flow", "type": "get_bestselling_asins", "data": {"topCount": 2}},
                {"id": "loop-flow", "type": "loop", "data": {}},
                {"id": "get-details-flow", "type": "get_asin_details", "data": {}},
                {"id": "merge-flow", "type": "merge", "data": {}}
            ],
            "edges": [
                {"id": "e1", "source": "get-asins-flow", "target": "loop-flow"},
                {"id": "e2", "source": "loop-flow", "target": "get-details-flow"},
                {"id": "e3", "source": "get-details-flow", "target": "merge-flow"}
            ]
        }
    }
    
    create_response = client.post("/workflows/", json=data_flow_workflow, headers=headers)
    assert create_response.status_code == 200
    workflow_id = create_response.json()["id"]
    
    run_response = client.post(f"/workflows/{workflow_id}/run", headers=headers)
    assert run_response.status_code == 200
    run_data = run_response.json()
    
    assert run_data["status"] == "completed"
    results = run_data["results"]
    
    # Verify data consistency through the pipeline
    original_asins = results["get-asins-flow"]["value"]
    loop_items = results["loop-flow"]["items"] 
    final_products = results["merge-flow"]["value"]
    
    # All should have same count
    assert len(original_asins) == 2
    assert len(loop_items) == 2  
    assert len(final_products) == 2
    
    # ASINs should match through the pipeline
    assert original_asins == loop_items
    
    # Final products should have ASINs from original list
    final_asins = [p["asin"] for p in final_products]
    assert set(final_asins) == set(original_asins)


if __name__ == "__main__":
    # Run tests manually if needed
    test_loop_merge_workflow_via_api()
    test_loop_node_validation() 
    test_merge_without_loop()
    test_loop_merge_data_flow()
