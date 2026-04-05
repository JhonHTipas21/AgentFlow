"""
AgentFlow Tool System
Extensible tool registry with async execution support.
"""
from typing import Callable, Any, Dict, List, Optional
import inspect
import logging
import time

logger = logging.getLogger(__name__)


class ToolDefinition:
    """
    A tool that agents can invoke during workflow execution.

    Each tool wraps a callable function and provides metadata
    for the agent to understand when/how to use it.
    """

    def __init__(
        self,
        name: str,
        description: str,
        func: Callable,
        category: Optional[str] = None,
    ):
        self.name = name
        self.description = description
        self.func = func
        self.category = category
        self.input_schema = self._extract_schema()

    def _extract_schema(self) -> Dict:
        """Extract input schema from function signature."""
        sig = inspect.signature(self.func)
        params = {}
        for param_name, param in sig.parameters.items():
            annotation = param.annotation
            param_type = "string"
            if annotation != inspect.Parameter.empty:
                param_type = getattr(annotation, "__name__", str(annotation))
            params[param_name] = {
                "type": param_type,
                "required": param.default == inspect.Parameter.empty,
            }
        return params

    async def execute(self, **kwargs) -> Any:
        """Execute the tool function with timing and error handling."""
        start = time.time()
        try:
            if inspect.iscoroutinefunction(self.func):
                result = await self.func(**kwargs)
            else:
                result = self.func(**kwargs)

            elapsed = time.time() - start
            logger.info(f"Tool '{self.name}' executed in {elapsed:.3f}s")
            return result

        except Exception as e:
            elapsed = time.time() - start
            logger.error(f"Tool '{self.name}' failed after {elapsed:.3f}s: {e}")
            return {"error": str(e), "tool": self.name}

    def to_dict(self) -> Dict:
        """Serialize tool info for API responses."""
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "input_schema": self.input_schema,
        }


# ═══════════════════════════════════════════════════════
# TOOL IMPLEMENTATIONS
# (Mock implementations — swap for real APIs in integrations/)
# ═══════════════════════════════════════════════════════

async def read_email(mailbox: str = "INBOX", max_results: int = 5) -> str:
    """Read emails from a Gmail mailbox."""
    logger.info(f"Reading {max_results} emails from {mailbox}")
    # Mock response — will be replaced by app/integrations/gmail.py
    return (
        f"Found {max_results} emails in {mailbox}:\n"
        f"1. [URGENT] Budget approval needed - finance@company.com\n"
        f"2. Meeting notes Q4 review - manager@company.com\n"
        f"3. New feature request - client@partner.com\n"
        f"4. Weekly standup reminder - calendar@company.com\n"
        f"5. Invoice #2847 attached - vendor@supplier.com"
    )


async def create_jira_task(
    summary: str,
    description: str,
    project_key: str = "PROJ"
) -> Dict:
    """Create a task in Jira."""
    logger.info(f"Creating Jira task: {summary}")
    # Mock response — will be replaced by app/integrations/jira.py
    return {
        "task_id": f"{project_key}-{1000 + hash(summary) % 900}",
        "summary": summary,
        "status": "created",
        "url": f"https://jira.example.com/browse/{project_key}-123",
    }


async def send_slack_message(channel: str, text: str) -> Dict:
    """Send a message to a Slack channel."""
    logger.info(f"Sending Slack message to #{channel}")
    # Mock response — will be replaced by app/integrations/slack.py
    return {
        "channel": channel,
        "ok": True,
        "message": text[:100],
    }


async def search_web(query: str, max_results: int = 5) -> str:
    """Search the web for information."""
    logger.info(f"Searching web for: {query}")
    return (
        f"Search results for '{query}':\n"
        f"1. {query} - Wikipedia overview\n"
        f"2. {query} best practices - Medium article\n"
        f"3. How to implement {query} - Stack Overflow\n"
        f"4. {query} documentation - Official docs\n"
        f"5. {query} tutorial - YouTube"
    )


async def generate_report(data: str, format: str = "text") -> str:
    """Generate a structured report from data."""
    logger.info(f"Generating {format} report")
    return (
        f"═══ GENERATED REPORT ═══\n"
        f"Format: {format}\n"
        f"Data Summary: {data[:200]}\n"
        f"Analysis: Based on the provided data, key findings include...\n"
        f"Recommendations: 1) Optimize workflow... 2) Improve monitoring...\n"
        f"═══ END REPORT ═══"
    )


# ═══════════════════════════════════════════════════════
# TOOL REGISTRY
# ═══════════════════════════════════════════════════════

AVAILABLE_TOOLS: Dict[str, ToolDefinition] = {
    "read_email": ToolDefinition(
        name="read_email",
        description="Reads emails from a Gmail mailbox. Returns email subjects and senders.",
        func=read_email,
        category="email",
    ),
    "create_jira_task": ToolDefinition(
        name="create_jira_task",
        description="Creates a new task in Jira with given summary and description.",
        func=create_jira_task,
        category="project_management",
    ),
    "send_slack_message": ToolDefinition(
        name="send_slack_message",
        description="Sends a message to a Slack channel.",
        func=send_slack_message,
        category="communication",
    ),
    "search_web": ToolDefinition(
        name="search_web",
        description="Searches the web for information on a given topic.",
        func=search_web,
        category="research",
    ),
    "generate_report": ToolDefinition(
        name="generate_report",
        description="Generates a structured report from provided data.",
        func=generate_report,
        category="analysis",
    ),
}


def get_tool(name: str) -> Optional[ToolDefinition]:
    """Get a tool by name from the registry."""
    return AVAILABLE_TOOLS.get(name)


def list_tools() -> List[Dict]:
    """List all available tools."""
    return [tool.to_dict() for tool in AVAILABLE_TOOLS.values()]
