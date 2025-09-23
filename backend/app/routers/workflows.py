from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas, auth
from app.workflow_engine import WorkflowEngine

router = APIRouter(prefix="/workflows", tags=["workflows"])


@router.get("/", response_model=List[schemas.Workflow])
def get_workflows(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Get all workflows for current user"""
    workflows = db.query(models.Workflow).filter(models.Workflow.user_id == current_user.id).all()
    return workflows


@router.post("/", response_model=schemas.Workflow)
def create_workflow(
    workflow: schemas.WorkflowCreate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new workflow"""
    db_workflow = models.Workflow(**workflow.dict(), user_id=current_user.id)
    db.add(db_workflow)
    db.commit()
    db.refresh(db_workflow)
    return db_workflow


@router.get("/{workflow_id}", response_model=schemas.Workflow)
def get_workflow(
    workflow_id: str,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific workflow"""
    workflow = db.query(models.Workflow).filter(
        models.Workflow.id == workflow_id,
        models.Workflow.user_id == current_user.id
    ).first()
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    return workflow


@router.put("/{workflow_id}", response_model=schemas.Workflow)
def update_workflow(
    workflow_id: str,
    workflow_update: schemas.WorkflowUpdate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Update a workflow"""
    workflow = db.query(models.Workflow).filter(
        models.Workflow.id == workflow_id,
        models.Workflow.user_id == current_user.id
    ).first()
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    update_data = workflow_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(workflow, key, value)
    
    workflow.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(workflow)
    return workflow


@router.delete("/{workflow_id}")
def delete_workflow(
    workflow_id: str,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a workflow"""
    workflow = db.query(models.Workflow).filter(
        models.Workflow.id == workflow_id,
        models.Workflow.user_id == current_user.id
    ).first()
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    db.delete(workflow)
    db.commit()
    return {"message": "Workflow deleted successfully"}


@router.post("/{workflow_id}/run", response_model=schemas.WorkflowRun)
def run_workflow(
    workflow_id: str,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Execute a workflow"""
    workflow = db.query(models.Workflow).filter(
        models.Workflow.id == workflow_id,
        models.Workflow.user_id == current_user.id
    ).first()
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    # Create workflow run record
    workflow_run = models.WorkflowRun(
        workflow_id=workflow.id,
        user_id=current_user.id,
        status="running"
    )
    db.add(workflow_run)
    db.commit()
    db.refresh(workflow_run)
    
    # Execute workflow
    engine = WorkflowEngine(db)
    try:
        result = engine.execute_workflow(workflow, current_user)
        
        workflow_run.status = "completed" if result["status"] == "success" else "failed"
        workflow_run.results = result.get("results")
        workflow_run.error_message = result.get("error")
        workflow_run.completed_at = datetime.utcnow()
        
    except Exception as e:
        workflow_run.status = "failed"
        workflow_run.error_message = str(e)
        workflow_run.completed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(workflow_run)
    return workflow_run


@router.get("/{workflow_id}/runs", response_model=List[schemas.WorkflowRun])
def get_workflow_runs(
    workflow_id: str,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Get all runs for a specific workflow"""
    runs = db.query(models.WorkflowRun).filter(
        models.WorkflowRun.workflow_id == workflow_id,
        models.WorkflowRun.user_id == current_user.id
    ).order_by(models.WorkflowRun.started_at.desc()).all()
    
    return runs