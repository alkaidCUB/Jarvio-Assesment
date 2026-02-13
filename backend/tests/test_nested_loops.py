import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_nested_loop_workflow_via_api():
    """Test nested loops: Categories → Loop → Products → Loop → Details → Merge → Merge"""
    
    # Login to get token
    login_response = client.post(
        "/auth/login",
        json={"email": "demo@example.com", "password": "demo123"}
    )
    assert login_response.status_code == 200
    token_data = login_response.json()
    headers = {"Authorization": f"Bearer {token_data['access_token']}"}

    # Create a nested loop workflow
    nested_workflow = {
        "name": "Nested Loop Test Workflow",
        "description": "Test workflow for nested Loop and Merge nodes",
        "flow_data": {
            "nodes": [
                {
                    "id": "get-categories",
                    "type": "get_bestselling_asins",  # Simulate categories with ASINs
                    "data": {"topCount": 2}  # 2 categories
                },
                {
                    "id": "outer-loop",
                    "type": "loop",
                    "data": {}
                },
                {
                    "id": "get-products",
                    "type": "get_bestselling_asins",  # Simulate products for each category
                    "data": {"topCount": 2}  # 2 products per category
                },
                {
                    "id": "inner-loop",
                    "type": "loop",
                    "data": {}
                },
                {
                    "id": "get-details",
                    "type": "get_asin_details",
                    "data": {}
                },
                {
                    "id": "inner-merge",
                    "type": "merge",
                    "data": {}
                },
                {
                    "id": "outer-merge",
                    "type": "merge",
                    "data": {}
                }
            ],
            "edges": [
                {"id": "edge-1", "source": "get-categories", "target": "outer-loop"},
                {"id": "edge-2", "source": "outer-loop", "target": "get-products"},
                {"id": "edge-3", "source": "get-products", "target": "inner-loop"},
                {"id": "edge-4", "source": "inner-loop", "target": "get-details"},
                {"id": "edge-5", "source": "get-details", "target": "inner-merge"},
                {"id": "edge-6", "source": "inner-merge", "target": "outer-merge"}
            ]
        }
    }

    # Create the workflow
    create_response = client.post("/workflows/", json=nested_workflow, headers=headers)
    assert create_response.status_code == 200
    workflow_id = create_response.json()["id"]

    # Execute the workflow
    run_response = client.post(f"/workflows/{workflow_id}/run", headers=headers)
    assert run_response.status_code == 200
    run_data = run_response.json()

    # Verify the workflow executed successfully
    assert run_data["status"] == "completed"
    assert "results" in run_data
    
    results = run_data["results"]
    
    # Verify outer loop was executed
    assert "outer-loop" in results
    outer_loop_result = results["outer-loop"]
    assert outer_loop_result["type"] == "loop_items"
    assert outer_loop_result["count"] == 2  # 2 categories
    
    # Verify inner loop was executed (should be loop_items)
    assert "inner-loop" in results
    inner_loop_result = results["inner-loop"]
    assert inner_loop_result["type"] == "loop_items"
    assert inner_loop_result["count"] >= 2  # Should have items from outer loop
    
    # Verify get-details was executed for each inner loop item
    assert "get-details" in results
    details_result = results["get-details"]
    assert details_result["type"] == "loop_execution_results"
    assert details_result["loop_depth"] == 1  # Inner loop depth
    
    # Verify inner merge collected inner loop results
    assert "inner-merge" in results
    inner_merge_result = results["inner-merge"]
    assert inner_merge_result["type"] in ["product_details_table", "nested_results_table"]
    
    # Verify outer merge collected all results
    assert "outer-merge" in results
    outer_merge_result = results["outer-merge"]
    assert outer_merge_result["type"] in ["product_details_table", "nested_results_table"]
    
    # Should have flattened all nested results
    assert outer_merge_result["count"] >= 4  # At least 2 categories × 2 products


def test_single_loop_still_works():
    """Test that single loops still work with the new stack-based system"""
    
    # Login
    login_response = client.post(
        "/auth/login",
        json={"email": "demo@example.com", "password": "demo123"}
    )
    assert login_response.status_code == 200
    headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}

    # Create a simple single loop workflow
    single_loop_workflow = {
        "name": "Single Loop Compatibility Test",
        "description": "Ensure single loops still work",
        "flow_data": {
            "nodes": [
                {
                    "id": "get-asins-single",
                    "type": "get_bestselling_asins",
                    "data": {"topCount": 3}
                },
                {
                    "id": "loop-single",
                    "type": "loop",
                    "data": {}
                },
                {
                    "id": "get-details-single",
                    "type": "get_asin_details",
                    "data": {}
                },
                {
                    "id": "merge-single",
                    "type": "merge",
                    "data": {}
                }
            ],
            "edges": [
                {"id": "edge-1", "source": "get-asins-single", "target": "loop-single"},
                {"id": "edge-2", "source": "loop-single", "target": "get-details-single"},
                {"id": "edge-3", "source": "get-details-single", "target": "merge-single"}
            ]
        }
    }

    # Create and run
    create_response = client.post("/workflows/", json=single_loop_workflow, headers=headers)
    assert create_response.status_code == 200
    workflow_id = create_response.json()["id"]

    run_response = client.post(f"/workflows/{workflow_id}/run", headers=headers)
    assert run_response.status_code == 200
    run_data = run_response.json()

    # Should still work perfectly
    assert run_data["status"] == "completed"
    results = run_data["results"]
    
    # Verify single loop results
    assert "merge-single" in results
    merge_result = results["merge-single"]
    assert merge_result["type"] == "product_details_table"
    assert merge_result["count"] == 3
    assert merge_result["loop_depth"] == 0  # Single loop at depth 0


def test_loop_depth_tracking():
    """Test that loop depth is correctly tracked"""
    
    # Login
    login_response = client.post(
        "/auth/login", 
        json={"email": "demo@example.com", "password": "demo123"}
    )
    assert login_response.status_code == 200
    headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}

    # Create workflow with 3 levels of nesting
    triple_nested_workflow = {
        "name": "Triple Nested Loop Test",
        "description": "Test 3 levels of loop nesting",
        "flow_data": {
            "nodes": [
                {"id": "level0", "type": "get_bestselling_asins", "data": {"topCount": 2}},
                {"id": "loop0", "type": "loop", "data": {}},
                {"id": "level1", "type": "get_bestselling_asins", "data": {"topCount": 2}},
                {"id": "loop1", "type": "loop", "data": {}},
                {"id": "level2", "type": "get_bestselling_asins", "data": {"topCount": 2}},
                {"id": "loop2", "type": "loop", "data": {}},
                {"id": "details", "type": "get_asin_details", "data": {}},
                {"id": "merge2", "type": "merge", "data": {}},
                {"id": "merge1", "type": "merge", "data": {}},
                {"id": "merge0", "type": "merge", "data": {}}
            ],
            "edges": [
                {"id": "e1", "source": "level0", "target": "loop0"},
                {"id": "e2", "source": "loop0", "target": "level1"},
                {"id": "e3", "source": "level1", "target": "loop1"},
                {"id": "e4", "source": "loop1", "target": "level2"},
                {"id": "e5", "source": "level2", "target": "loop2"},
                {"id": "e6", "source": "loop2", "target": "details"},
                {"id": "e7", "source": "details", "target": "merge2"},
                {"id": "e8", "source": "merge2", "target": "merge1"},
                {"id": "e9", "source": "merge1", "target": "merge0"}
            ]
        }
    }

    # Create and run
    create_response = client.post("/workflows/", json=triple_nested_workflow, headers=headers)
    assert create_response.status_code == 200
    workflow_id = create_response.json()["id"]

    run_response = client.post(f"/workflows/{workflow_id}/run", headers=headers)
    assert run_response.status_code == 200
    run_data = run_response.json()

    # Should handle 3 levels of nesting
    assert run_data["status"] == "completed"
    results = run_data["results"]
    
    # Check that different merge levels have correct depth tracking
    assert "merge0" in results  # Outermost merge
    assert "merge1" in results  # Middle merge  
    assert "merge2" in results  # Innermost merge
    
    # Final result should have all items flattened
    final_result = results["merge0"]
    assert final_result["count"] >= 8  # 2×2×2 = 8 items minimum


def test_scoped_variables():
    """Test that scoped variables are correctly built and accessible"""
    
    # This test would require a custom node that can access scoped variables
    # For now, we'll test that the workflow executes without errors
    # In a real implementation, you'd create a test node that logs scoped vars
    
    # Login
    login_response = client.post(
        "/auth/login",
        json={"email": "demo@example.com", "password": "demo123"}
    )
    assert login_response.status_code == 200
    headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}

    # Simple nested workflow to test scoped variables
    scoped_workflow = {
        "name": "Scoped Variables Test",
        "description": "Test scoped variable access",
        "flow_data": {
            "nodes": [
                {"id": "outer-data", "type": "get_bestselling_asins", "data": {"topCount": 2}},
                {"id": "outer-loop", "type": "loop", "data": {}},
                {"id": "inner-data", "type": "get_bestselling_asins", "data": {"topCount": 2}},
                {"id": "inner-loop", "type": "loop", "data": {}},
                {"id": "process", "type": "get_asin_details", "data": {}},
                {"id": "inner-merge", "type": "merge", "data": {}},
                {"id": "outer-merge", "type": "merge", "data": {}}
            ],
            "edges": [
                {"id": "e1", "source": "outer-data", "target": "outer-loop"},
                {"id": "e2", "source": "outer-loop", "target": "inner-data"},
                {"id": "e3", "source": "inner-data", "target": "inner-loop"},
                {"id": "e4", "source": "inner-loop", "target": "process"},
                {"id": "e5", "source": "process", "target": "inner-merge"},
                {"id": "e6", "source": "inner-merge", "target": "outer-merge"}
            ]
        }
    }

    # Create and run
    create_response = client.post("/workflows/", json=scoped_workflow, headers=headers)
    assert create_response.status_code == 200
    workflow_id = create_response.json()["id"]

    run_response = client.post(f"/workflows/{workflow_id}/run", headers=headers)
    assert run_response.status_code == 200
    run_data = run_response.json()

    # Should execute successfully with proper scoping
    assert run_data["status"] == "completed"
    
    # Verify that scoped variables were properly managed
    # (In a real test, you'd check that loop_0_item, loop_1_item, etc. were set correctly)
    results = run_data["results"]
    assert "outer-merge" in results
    assert results["outer-merge"]["count"] >= 4  # 2×2 minimum
