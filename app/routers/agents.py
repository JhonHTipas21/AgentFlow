"""
AgentFlow Agents Router
CRUD endpoints and workflow execution for agents.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app import schemas
from app.services.agent_service import AgentService

router = APIRouter()


# ─── CREATE AGENT ────────────────────────────────────────
@router.post("/", response_model=schemas.AgentResponse, status_code=201)
def create_agent(
    agent: schemas.AgentCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new AI agent.

    Optionally assign tools from the available tool registry.
    """
    service = AgentService(db)
    return service.create_agent(agent)


# ─── LIST AGENTS ─────────────────────────────────────────
@router.get("/", response_model=List[schemas.AgentListResponse])
def list_agents(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db),
):
    """List all agents with optional status filtering."""
    service = AgentService(db)
    return service.list_agents(skip=skip, limit=limit, status=status)


# ─── GET AGENT ───────────────────────────────────────────
@router.get("/{agent_id}", response_model=schemas.AgentResponse)
def get_agent(
    agent_id: int,
    db: Session = Depends(get_db),
):
    """Get a specific agent by ID."""
    service = AgentService(db)
    return service.get_agent_or_404(agent_id)


# ─── UPDATE AGENT ────────────────────────────────────────
@router.put("/{agent_id}", response_model=schemas.AgentResponse)
def update_agent(
    agent_id: int,
    agent: schemas.AgentUpdate,
    db: Session = Depends(get_db),
):
    """Update an existing agent."""
    service = AgentService(db)
    return service.update_agent(agent_id, agent)


# ─── DELETE AGENT ────────────────────────────────────────
@router.delete("/{agent_id}", response_model=schemas.MessageResponse)
def delete_agent(
    agent_id: int,
    db: Session = Depends(get_db),
):
    """Delete an agent and its associated workflows."""
    service = AgentService(db)
    service.delete_agent(agent_id)
    return {"detail": f"Agent {agent_id} deleted successfully"}


# ─── EXECUTE WORKFLOW ────────────────────────────────────
@router.post("/{agent_id}/execute", response_model=schemas.WorkflowResponse)
async def execute_workflow(
    agent_id: int,
    request: schemas.WorkflowExecuteRequest,
    db: Session = Depends(get_db),
):
    """
    Execute a workflow with an agent.

    The agent processes the input using Claude API and available tools,
    then returns the result with execution metrics.
    """
    from app.agents import AgentOrchestrator

    # Verify agent exists
    service = AgentService(db)
    service.get_agent_or_404(agent_id)

    orchestrator = AgentOrchestrator(agent_id, db)
    result = await orchestrator.execute_workflow(
        request.input,
        request.metadata
    )
    return result


# ─── EXECUTE ASYNC (Celery) ──────────────────────────────
@router.post("/{agent_id}/execute-async")
async def execute_workflow_async(
    agent_id: int,
    request: schemas.WorkflowExecuteRequest,
    db: Session = Depends(get_db),
):
    """
    Queue a workflow for async execution via Celery.

    Returns a task ID that can be used to check status.
    """
    from app.celery_app import celery_app, execute_workflow_task

    # Verify agent exists
    service = AgentService(db)
    service.get_agent_or_404(agent_id)

    if celery_app is None:
        raise HTTPException(
            status_code=503,
            detail="Async execution not available. Celery is not configured."
        )

    task = execute_workflow_task.delay(
        agent_id,
        request.input,
        request.metadata
    )
    return {
        "task_id": task.id,
        "status": "queued",
        "detail": "Workflow queued for async execution",
    }


# ─── AGENT STATUS (Runtime State) ────────────────────────
@router.get("/{agent_id}/status")
def get_agent_status(
    agent_id: int,
    db: Session = Depends(get_db),
):
    """
    Get real-time runtime status for an agent.

    Returns execution metrics: total runs, success/failure counts,
    average execution time, and last execution details.
    """
    from app.state import StateManager

    # Verify agent exists
    service = AgentService(db)
    agent = service.get_agent_or_404(agent_id)

    state = StateManager(agent_id)
    runtime = state.get()

    return {
        "agent_id": agent_id,
        "agent_name": agent.name,
        "db_status": agent.status.value,
        "runtime": runtime,
    }

