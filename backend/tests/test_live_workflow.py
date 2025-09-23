import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_sequential_workflow_via_live_api():
    """Test the sequential workflow through the live API against actual database"""
    
    # Login to get token
    login_response = client.post(
        "/auth/login",
        json={"email": "demo@example.com", "password": "demo123"}
    )
    assert login_response.status_code == 200
    token_data = login_response.json()
    assert "access_token" in token_data
    
    headers = {"Authorization": f"Bearer {token_data['access_token']}"}
    
    # Get existing workflows to find our sequential example
    workflows_response = client.get("/workflows/", headers=headers)
    assert workflows_response.status_code == 200
    workflows = workflows_response.json()
    
    # Find the sequential workflow
    sequential_workflow = None
    for workflow in workflows:
        if "Sequential Product Analysis" in workflow.get("name", ""):
            sequential_workflow = workflow
            break
    
    # If no existing workflow, create one
    if not sequential_workflow:
        workflow_data = {
            "name": "Test Sequential Workflow",
            "description": "Test workflow for sequential ASIN processing",
            "flow_data": {
                "nodes": [
                    {
                        "id": "test-node-1",
                        "type": "get_bestselling_asins",
                        "position": {"x": 100, "y": 100},
                        "data": {"label": "Get Best Selling ASINs", "topCount": 3}
                    },
                    {
                        "id": "test-node-2",
                        "type": "get_asin_by_index",
                        "position": {"x": 400, "y": 100},
                        "data": {"label": "Get ASIN by Index", "index": 1}
                    },
                    {
                        "id": "test-node-3",
                        "type": "get_asin_details",
                        "position": {"x": 700, "y": 100},
                        "data": {"label": "Get ASIN Details"}
                    }
                ],
                "edges": [
                    {
                        "id": "test-edge-1",
                        "source": "test-node-1",
                        "target": "test-node-2",
                        "sourceHandle": "output",
                        "targetHandle": "input"
                    },
                    {
                        "id": "test-edge-2",
                        "source": "test-node-2",
                        "target": "test-node-3", 
                        "sourceHandle": "output",
                        "targetHandle": "input"
                    }
                ]
            }
        }
        
        create_response = client.post("/workflows/", json=workflow_data, headers=headers)
        assert create_response.status_code == 200
        sequential_workflow = create_response.json()
    
    workflow_id = sequential_workflow["id"]
    
    # Run the workflow
    run_response = client.post(f"/workflows/{workflow_id}/run", headers=headers)
    assert run_response.status_code == 200
    
    run_result = run_response.json()
    assert run_result["status"] == "completed"
    
    # Get workflow runs
    runs_response = client.get(f"/workflows/{workflow_id}/runs", headers=headers)
    assert runs_response.status_code == 200
    
    runs = runs_response.json()
    assert len(runs) >= 1
    
    # Get the most recent successful run
    latest_run = None
    for run in runs:
        if run["status"] == "completed":
            latest_run = run
            break
    
    assert latest_run is not None, "No completed workflow run found"
    assert "results" in latest_run
    
    results = latest_run["results"]
    
    # Verify sequential workflow execution
    # Step 1: Get best selling ASINs (should return list of ASINs)
    assert len(results) >= 1
    
    # Find the first node result (get_bestselling_asins)
    asins_result = None
    for node_id, result in results.items():
        if result.get("type") == "asin_list":
            asins_result = result
            break
    
    assert asins_result is not None, "No asin_list result found"
    assert "value" in asins_result
    assert "count" in asins_result
    assert isinstance(asins_result["value"], list)
    assert len(asins_result["value"]) >= 2  # Need at least 2 items to select index 1
    
    # Step 2: Get ASIN by index (should return single ASIN)
    single_asin_result = None
    for node_id, result in results.items():
        if result.get("type") == "single_asin":
            single_asin_result = result
            break
    
    assert single_asin_result is not None, "No single_asin result found"
    assert "value" in single_asin_result
    assert isinstance(single_asin_result["value"], str)
    # Should be the second item (index 1) from the list
    assert single_asin_result["value"] == asins_result["value"][1]
    
    # Step 3: Get ASIN details (should return product details)
    details_result = None
    for node_id, result in results.items():
        if result.get("type") == "product_details":
            details_result = result
            break
    
    assert details_result is not None, "No product_details result found"
    assert "value" in details_result
    product_details = details_result["value"]
    assert "asin" in product_details
    assert "title" in product_details
    assert "description" in product_details
    # Should match the ASIN selected in step 2
    assert product_details["asin"] == single_asin_result["value"]
    
    print(f"✅ Sequential workflow test passed!")
    print(f"   ASINs retrieved: {asins_result['value']}")
    print(f"   Selected ASIN (index 1): {single_asin_result['value']}")
    print(f"   Product title: {product_details['title']}")


def test_workflow_data_flow_types():
    """Test that the workflow properly handles different data types"""
    
    # Login
    login_response = client.post(
        "/auth/login",
        json={"email": "demo@example.com", "password": "demo123"}
    )
    assert login_response.status_code == 200
    headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}
    
    # Create a workflow that tests data type flow
    workflow_data = {
        "name": "Data Flow Test Workflow",
        "description": "Test workflow for validating data type flow",
        "flow_data": {
            "nodes": [
                {
                    "id": "dataflow-node-1",
                    "type": "get_bestselling_asins", 
                    "data": {"topCount": 2}
                },
                {
                    "id": "dataflow-node-2",
                    "type": "get_asin_by_index",
                    "data": {"index": 0}  # Get first item
                },
                {
                    "id": "dataflow-node-3",
                    "type": "get_asin_details",
                    "data": {}
                }
            ],
            "edges": [
                {
                    "id": "dataflow-edge-1",
                    "source": "dataflow-node-1",
                    "target": "dataflow-node-2",
                    "sourceHandle": "output",
                    "targetHandle": "input"
                },
                {
                    "id": "dataflow-edge-2", 
                    "source": "dataflow-node-2",
                    "target": "dataflow-node-3",
                    "sourceHandle": "output", 
                    "targetHandle": "input"
                }
            ]
        }
    }
    
    # Create and run workflow
    create_response = client.post("/workflows/", json=workflow_data, headers=headers)
    assert create_response.status_code == 200
    workflow_id = create_response.json()["id"]
    
    run_response = client.post(f"/workflows/{workflow_id}/run", headers=headers)
    assert run_response.status_code == 200
    
    # Verify data types in results
    runs_response = client.get(f"/workflows/{workflow_id}/runs", headers=headers)
    assert runs_response.status_code == 200
    
    runs = runs_response.json()
    latest_run = runs[0]  # Most recent run
    results = latest_run["results"]
    
    # Verify each step produces the expected data type
    node1_result = results["dataflow-node-1"]
    assert node1_result["type"] == "asin_list"
    assert isinstance(node1_result["value"], list)
    
    node2_result = results["dataflow-node-2"] 
    assert node2_result["type"] == "single_asin"
    assert isinstance(node2_result["value"], str)
    
    node3_result = results["dataflow-node-3"]
    assert node3_result["type"] == "product_details"
    assert isinstance(node3_result["value"], dict)
    
    print("✅ Data flow types test passed!")