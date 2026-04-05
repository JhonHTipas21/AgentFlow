"""
AgentFlow API Tests
Comprehensive test suite for all API endpoints.
"""
import pytest


# ═══════════════════════════════════════════════════════
# SYSTEM ENDPOINTS
# ═══════════════════════════════════════════════════════

class TestSystemEndpoints:
    """Tests for health, readiness, and info endpoints."""

    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["app"] == "AgentFlow"

    def test_readiness_check(self, client):
        response = client.get("/ready")
        assert response.status_code == 200
        assert response.json()["ready"] is True

    def test_app_info(self, client):
        response = client.get("/info")
        assert response.status_code == 200
        data = response.json()
        assert "version" in data
        assert "features" in data

    def test_get_token(self, client):
        response = client.post("/token")
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"


# ═══════════════════════════════════════════════════════
# AGENT CRUD
# ═══════════════════════════════════════════════════════

class TestAgentCRUD:
    """Tests for agent CRUD operations."""

    def test_create_agent(self, client, sample_agent_data):
        response = client.post("/agents/", json=sample_agent_data)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "test_agent"
        assert data["status"] == "active"
        assert "uuid" in data
        assert "id" in data

    def test_create_agent_minimal(self, client):
        response = client.post("/agents/", json={
            "name": "minimal_agent",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "minimal_agent"
        assert data["model"] == "claude-sonnet-4-20250514"

    def test_create_agent_duplicate_name(self, client, created_agent):
        response = client.post("/agents/", json={
            "name": "test_agent",
            "description": "Duplicate",
        })
        assert response.status_code == 400

    def test_list_agents(self, client, created_agent):
        response = client.get("/agents/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_get_agent(self, client, created_agent):
        agent_id = created_agent["id"]
        response = client.get(f"/agents/{agent_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == agent_id
        assert data["name"] == "test_agent"

    def test_get_agent_not_found(self, client):
        response = client.get("/agents/99999")
        assert response.status_code == 404

    def test_update_agent(self, client, created_agent):
        agent_id = created_agent["id"]
        response = client.put(f"/agents/{agent_id}", json={
            "description": "Updated description",
            "temperature": 0.9,
        })
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Updated description"
        assert data["temperature"] == 0.9

    def test_delete_agent(self, client, created_agent):
        agent_id = created_agent["id"]
        response = client.delete(f"/agents/{agent_id}")
        assert response.status_code == 200

        # Verify deleted
        response = client.get(f"/agents/{agent_id}")
        assert response.status_code == 404


# ═══════════════════════════════════════════════════════
# AGENT EXECUTION
# ═══════════════════════════════════════════════════════

class TestAgentExecution:
    """Tests for workflow execution."""

    def test_execute_workflow(self, client, created_agent):
        agent_id = created_agent["id"]
        response = client.post(f"/agents/{agent_id}/execute", json={
            "input": "Hello, test the agent workflow",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["agent_id"] == agent_id
        assert data["status"] in ["success", "failed"]
        assert "output" in data

    def test_execute_workflow_agent_not_found(self, client):
        response = client.post("/agents/99999/execute", json={
            "input": "Test input",
        })
        assert response.status_code == 404

    def test_agent_status_default(self, client, created_agent):
        """Status endpoint returns default idle state for new agents."""
        agent_id = created_agent["id"]
        response = client.get(f"/agents/{agent_id}/status")
        assert response.status_code == 200
        data = response.json()
        assert data["agent_id"] == agent_id
        assert data["agent_name"] == "test_agent"
        assert data["runtime"]["runtime_status"] == "idle"
        assert data["runtime"]["total_executions"] == 0

    def test_agent_status_after_execution(self, client, created_agent):
        """Status tracks metrics after workflow execution."""
        agent_id = created_agent["id"]

        # Execute a workflow
        client.post(f"/agents/{agent_id}/execute", json={
            "input": "Test for status tracking",
        })

        # Check status updated
        response = client.get(f"/agents/{agent_id}/status")
        data = response.json()
        assert data["runtime"]["total_executions"] == 1
        assert data["runtime"]["successful_executions"] == 1
        assert data["runtime"]["last_execution"] is not None
        assert data["runtime"]["last_execution"]["success"] is True


# ═══════════════════════════════════════════════════════
# WORKFLOWS
# ═══════════════════════════════════════════════════════

class TestWorkflows:
    """Tests for workflow listing and log retrieval."""

    def test_list_workflows_empty(self, client):
        response = client.get("/workflows/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_list_workflows_after_execution(self, client, created_agent):
        # Execute a workflow first
        agent_id = created_agent["id"]
        client.post(f"/agents/{agent_id}/execute", json={
            "input": "Test workflow",
        })

        response = client.get("/workflows/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    def test_get_workflow_logs(self, client, created_agent):
        # Execute a workflow
        agent_id = created_agent["id"]
        exec_response = client.post(f"/agents/{agent_id}/execute", json={
            "input": "Test workflow for logs",
        })
        workflow_id = exec_response.json()["id"]

        # Get logs
        response = client.get(f"/workflows/{workflow_id}/logs")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


# ═══════════════════════════════════════════════════════
# TOOLS
# ═══════════════════════════════════════════════════════

class TestTools:
    """Tests for the tool registry endpoints."""

    def test_list_tools(self, client):
        response = client.get("/tools/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 5  # We have 5 default tools

        # Check tool structure
        tool_names = [t["name"] for t in data]
        assert "read_email" in tool_names
        assert "create_jira_task" in tool_names
        assert "send_slack_message" in tool_names

    def test_get_tool_details(self, client):
        response = client.get("/tools/read_email")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "read_email"
        assert "description" in data
        assert "input_schema" in data
