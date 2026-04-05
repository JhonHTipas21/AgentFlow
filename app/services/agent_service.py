"""
AgentFlow Agent Service
Business logic for agent CRUD operations.
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import List, Optional
import logging

from app import models, schemas
from app.tools import AVAILABLE_TOOLS

logger = logging.getLogger(__name__)


class AgentService:
    """Handles all agent-related business logic."""

    def __init__(self, db: Session):
        self.db = db

    def create_agent(self, data: schemas.AgentCreate) -> models.Agent:
        """Create a new agent with optional tool assignments."""
        # Check for duplicate name
        existing = self.db.query(models.Agent).filter(
            models.Agent.name == data.name
        ).first()
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Agent with name '{data.name}' already exists"
            )

        # Create agent
        agent = models.Agent(
            name=data.name,
            description=data.description,
            model=data.model,
            system_prompt=data.system_prompt,
            max_tokens=data.max_tokens,
            temperature=data.temperature,
        )
        self.db.add(agent)
        self.db.flush()  # Get the ID without committing

        # Assign tools
        if data.tools:
            self._assign_tools(agent, data.tools)

        self.db.commit()
        self.db.refresh(agent)

        logger.info(f"Created agent '{agent.name}' (id={agent.id})")
        return agent

    def get_agent(self, agent_id: int) -> Optional[models.Agent]:
        """Get an agent by ID."""
        return self.db.query(models.Agent).filter(
            models.Agent.id == agent_id
        ).first()

    def get_agent_or_404(self, agent_id: int) -> models.Agent:
        """Get an agent by ID or raise 404."""
        agent = self.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        return agent

    def list_agents(
        self,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None,
    ) -> List[models.Agent]:
        """List agents with optional filtering."""
        query = self.db.query(models.Agent)

        if status:
            query = query.filter(models.Agent.status == status)

        return query.order_by(
            models.Agent.created_at.desc()
        ).offset(skip).limit(limit).all()

    def update_agent(
        self,
        agent_id: int,
        data: schemas.AgentUpdate,
    ) -> models.Agent:
        """Update an existing agent."""
        agent = self.get_agent_or_404(agent_id)

        update_data = data.model_dump(exclude_unset=True)

        # Handle tool assignment separately
        tool_names = update_data.pop("tools", None)
        if tool_names is not None:
            # Clear existing tools and reassign
            agent.tools.clear()
            self._assign_tools(agent, tool_names)

        # Update scalar fields
        for field, value in update_data.items():
            setattr(agent, field, value)

        self.db.commit()
        self.db.refresh(agent)

        logger.info(f"Updated agent '{agent.name}' (id={agent.id})")
        return agent

    def delete_agent(self, agent_id: int) -> None:
        """Delete an agent and all related data."""
        agent = self.get_agent_or_404(agent_id)
        agent_name = agent.name

        self.db.delete(agent)
        self.db.commit()

        logger.info(f"Deleted agent '{agent_name}' (id={agent_id})")

    def _assign_tools(self, agent: models.Agent, tool_names: List[str]):
        """Assign tools to an agent, creating Tool records if needed."""
        for name in tool_names:
            if name not in AVAILABLE_TOOLS:
                logger.warning(f"Tool '{name}' not found in registry, skipping")
                continue

            # Find or create the tool record
            tool = self.db.query(models.Tool).filter(
                models.Tool.name == name
            ).first()

            if not tool:
                tool_def = AVAILABLE_TOOLS[name]
                tool = models.Tool(
                    name=name,
                    description=tool_def.description,
                    function_name=name,
                    category=tool_def.category,
                    input_schema=tool_def.input_schema,
                )
                self.db.add(tool)
                self.db.flush()

            if tool not in agent.tools:
                agent.tools.append(tool)
