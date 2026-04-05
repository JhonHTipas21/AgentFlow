"""
AgentFlow Workflows Router
Endpoints for viewing workflow history and logs.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app import schemas
from app.services.workflow_service import WorkflowService

router = APIRouter()


# ─── LIST WORKFLOWS ──────────────────────────────────────
@router.get("/", response_model=List[schemas.WorkflowResponse])
def list_workflows(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    agent_id: Optional[int] = Query(None, description="Filter by agent ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db),
):
    """List workflow execution history with optional filters."""
    service = WorkflowService(db)
    return service.list_workflows(
        skip=skip, limit=limit, agent_id=agent_id, status=status
    )


# ─── GET WORKFLOW ────────────────────────────────────────
@router.get("/{workflow_id}", response_model=schemas.WorkflowResponse)
def get_workflow(
    workflow_id: int,
    db: Session = Depends(get_db),
):
    """Get details of a specific workflow execution."""
    service = WorkflowService(db)
    return service.get_workflow(workflow_id)


# ─── GET WORKFLOW LOGS ───────────────────────────────────
@router.get("/{workflow_id}/logs", response_model=List[schemas.WorkflowLogResponse])
def get_workflow_logs(
    workflow_id: int,
    level: Optional[str] = Query(None, description="Filter by log level"),
    db: Session = Depends(get_db),
):
    """Get detailed logs for a workflow execution."""
    service = WorkflowService(db)
    return service.get_workflow_logs(workflow_id, level=level)
