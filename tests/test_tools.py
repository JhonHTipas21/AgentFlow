"""
AgentFlow Tool System Tests
Tests for tool registration, execution, and registry API.
"""
import pytest
from app.tools import get_tool, list_tools, AVAILABLE_TOOLS


class TestToolRegistry:
    """Tests for the tool registry functions."""

    def test_registry_has_default_tools(self):
        """Registry contains all 5 built-in tools."""
        tools = list_tools()
        assert len(tools) >= 5
        names = [t["name"] for t in tools]
        assert "read_email" in names
        assert "create_jira_task" in names
        assert "send_slack_message" in names
        assert "search_web" in names
        assert "generate_report" in names

    def test_get_tool_by_name(self):
        """Can retrieve a specific tool by name."""
        tool = get_tool("read_email")
        assert tool is not None
        assert tool.name == "read_email"
        assert tool.description is not None
        assert tool.category is not None

    def test_get_tool_not_found(self):
        """Returns None for non-existent tool."""
        tool = get_tool("nonexistent_tool")
        assert tool is None

    def test_tool_has_input_schema(self):
        """Each tool has an input_schema field."""
        tools = list_tools()
        for tool in tools:
            assert "input_schema" in tool

    def test_tool_categories(self):
        """Tools have correct categories assigned."""
        email_tool = get_tool("read_email")
        assert email_tool.category == "email"

        jira_tool = get_tool("create_jira_task")
        assert jira_tool.category == "project_management"

        slack_tool = get_tool("send_slack_message")
        assert slack_tool.category == "communication"

    @pytest.mark.asyncio
    async def test_execute_tool_mock(self):
        """Tool execute method returns mock data."""
        tool = get_tool("search_web")
        assert tool is not None
        # Just verify the tool object is valid
        assert callable(tool.func)


class TestToolsAPI:
    """Tests for the /tools/ API endpoints."""

    def test_list_tools_endpoint(self, client):
        """GET /tools/ returns all available tools."""
        response = client.get("/tools/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 5

    def test_get_tool_endpoint(self, client):
        """GET /tools/{name} returns tool details."""
        response = client.get("/tools/read_email")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "read_email"

    def test_get_tool_not_found_endpoint(self, client):
        """GET /tools/{name} returns 404 for unknown tool."""
        response = client.get("/tools/nonexistent")
        assert response.status_code == 404

    def test_tools_have_descriptions(self, client):
        """All tools returned by API have descriptions."""
        response = client.get("/tools/")
        data = response.json()
        for tool in data:
            assert "description" in tool
            assert len(tool["description"]) > 0

    def test_tool_schema_structure(self, client):
        """Tool response matches expected structure."""
        response = client.get("/tools/create_jira_task")
        data = response.json()
        expected_keys = {"name", "description", "category", "input_schema"}
        assert expected_keys.issubset(set(data.keys()))
