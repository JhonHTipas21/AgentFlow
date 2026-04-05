"""
AgentFlow Workflow Service
Business logic for workflow queries and log retrieval.
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import List, Optional
import logging

from app import models

logger = logging.getLogger(__name__)


class WorkflowService:
    """Handles workflow-related business logic."""

    def __init__(self, db: Session):
        self.db = db

    def get_workflow(self, workflow_id: int) -> models.Workflow:
        """Get a workflow by ID or raise 404."""
        workflow = self.db.query(models.Workflow).filter(
            models.Workflow.id == workflow_id
        ).first()
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        return workflow

    def list_workflows(
        self,
        skip: int = 0,
        limit: int = 20,
        agent_id: Optional[int] = None,
        status: Optional[str] = None,
    ) -> List[models.Workflow]:
        """List workflows with optional filtering."""
        query = self.db.query(models.Workflow)

        if agent_id:
            query = query.filter(models.Workflow.agent_id == agent_id)
        if status:
            query = query.filter(models.Workflow.status == status)

        return query.order_by(
            models.Workflow.created_at.desc()
        ).offset(skip).limit(limit).all()

    def get_workflow_logs(
        self,
        workflow_id: int,
        level: Optional[str] = None,
    ) -> List[models.WorkflowLog]:
        """Get logs for a specific workflow."""
        # Verify workflow exists
        self.get_workflow(workflow_id)

        query = self.db.query(models.WorkflowLog).filter(
            models.WorkflowLog.workflow_id == workflow_id
        )

        if level:
            query = query.filter(models.WorkflowLog.level == level)

        return query.order_by(
            models.WorkflowLog.created_at.asc()
        ).all()

    def count_workflows(
        self,
        agent_id: Optional[int] = None,
        status: Optional[str] = None,
    ) -> int:
        """Count workflows with optional filtering."""
        query = self.db.query(models.Workflow)

        if agent_id:
            query = query.filter(models.Workflow.agent_id == agent_id)
        if status:
            query = query.filter(models.Workflow.status == status)

        return query.count()
