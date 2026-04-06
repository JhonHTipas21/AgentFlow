"""
AgentFlow Agent Logic Tests
Unit tests for the AgentOrchestrator and agent service layer.
"""
import pytest
from unittest.mock import patch, MagicMock
from app.agents import AgentOrchestrator
from app.services.agent_service import AgentService
from app import models


@pytest.mark.asyncio
class TestAgentOrchestrator:
    """Tests for the core AgentOrchestrator class."""

    def test_orchestrator_initialization(self, db, created_agent):
        """Orchestrator initializes correctly with a valid agent."""
        agent_id = created_agent["id"]
        orchestrator = AgentOrchestrator(agent_id=agent_id, db=db)
        assert orchestrator.agent_id == agent_id
        assert orchestrator.agent is not None
        assert orchestrator.agent.name == "test_agent"

    def test_orchestrator_invalid_agent(self, db):
        """Orchestrator raises error for non-existent agent."""
        with pytest.raises(ValueError, match="Agent 99999 not found"):
            AgentOrchestrator(agent_id=99999, db=db)

    async def test_execute_workflow_creates_record(self, db, created_agent):
        """Workflow execution creates a database record."""
        agent_id = created_agent["id"]
        orchestrator = AgentOrchestrator(agent_id=agent_id, db=db)
        result = await orchestrator.execute_workflow("Test input for workflow")

        assert result["agent_id"] == agent_id
        assert result["input"] == "Test input for workflow"
        assert result["status"] in ["success", "failed"]
        assert "id" in result
        assert result["execution_time"] is not None
        assert result["execution_time"] >= 0

    async def test_execute_workflow_generates_output(self, db, created_agent):
        """Successful workflow returns output."""
        agent_id = created_agent["id"]
        orchestrator = AgentOrchestrator(agent_id=agent_id, db=db)
        result = await orchestrator.execute_workflow("Summarize this: hello world")

        assert result["status"] == "success"
        assert result["output"] is not None
        assert len(result["output"]) > 0

    async def test_workflow_persisted_to_database(self, db, created_agent):
        """Verify workflow is persisted in the database after execution."""
        agent_id = created_agent["id"]
        orchestrator = AgentOrchestrator(agent_id=agent_id, db=db)
        result = await orchestrator.execute_workflow("Persisted test")

        workflow = db.query(models.Workflow).filter(
            models.Workflow.id == result["id"]
        ).first()
        assert workflow is not None
        assert workflow.input == "Persisted test"
        assert workflow.status.value in ["success", "failed"]

    async def test_workflow_handles_long_input(self, db, created_agent):
        """Orchestrator handles maximum-length input."""
        agent_id = created_agent["id"]
        orchestrator = AgentOrchestrator(agent_id=agent_id, db=db)
        long_input = "A" * 5000
        result = await orchestrator.execute_workflow(long_input)
        assert result["status"] in ["success", "failed"]

    async def test_multiple_workflows_sequential(self, db, created_agent):
        """Multiple sequential workflow executions work correctly."""
        agent_id = created_agent["id"]
        orchestrator = AgentOrchestrator(agent_id=agent_id, db=db)

        results = []
        for i in range(3):
            result = await orchestrator.execute_workflow(f"Test workflow #{i}")
            results.append(result)

        assert len(results) == 3
        ids = [r["id"] for r in results]
        assert len(set(ids)) == 3  # All unique IDs


class TestAgentService:
    """Tests for the agent service layer."""

    def test_create_agent(self, db):
        """Service creates agent with correct defaults."""
        from app.schemas import AgentCreate
        service = AgentService(db)
        agent = service.create_agent(AgentCreate(
            name="service_agent",
            description="Created by service",
        ))
        assert agent.name == "service_agent"
        assert agent.status.value == "active"
        assert agent.temperature == 0.7

    def test_list_agents_with_pagination(self, db, client):
        """Agents list supports skip/limit pagination."""
        # Create 5 agents
        for i in range(5):
            client.post("/agents/", json={"name": f"agent_{i}"})

        # Paginate
        response = client.get("/agents/?skip=0&limit=2")
        assert response.status_code == 200
        page1 = response.json()
        assert len(page1) == 2

        response = client.get("/agents/?skip=2&limit=2")
        assert response.status_code == 200
        page2 = response.json()
        assert len(page2) == 2

    def test_update_agent_preserves_tools(self, db, client, created_agent):
        """Updating description doesn't alter tool assignments."""
        agent_id = created_agent["id"]
        original_tools = created_agent.get("tools", [])

        client.put(f"/agents/{agent_id}", json={
            "description": "Updated",
        })

        response = client.get(f"/agents/{agent_id}")
        updated = response.json()
        assert updated["description"] == "Updated"
        assert len(updated.get("tools", [])) == len(original_tools)

    def test_delete_cascades_workflows(self, db, client, created_agent):
        """Deleting agent cascades to delete associated workflows."""
        agent_id = created_agent["id"]

        # Execute a workflow
        client.post(f"/agents/{agent_id}/execute", json={
            "input": "Cascade test",
        })

        # Delete agent
        client.delete(f"/agents/{agent_id}")

        # Verify workflows are gone too
        workflows = db.query(models.Workflow).filter(
            models.Workflow.agent_id == agent_id
        ).all()
        assert len(workflows) == 0
