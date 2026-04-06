"""
AgentFlow Jira Integration
Task creation and management via Jira API.
"""
import logging
from typing import Optional
from jira import JIRA
from jira.exceptions import JIRAError
from app.config import settings
import asyncio

logger = logging.getLogger(__name__)


def _get_client() -> Optional[JIRA]:
    """Get instantiated Jira client if credentials exist."""
    if not settings.JIRA_SERVER or not settings.JIRA_EMAIL or not settings.JIRA_API_TOKEN:
        return None
    try:
        return JIRA(
            server=settings.JIRA_SERVER,
            basic_auth=(settings.JIRA_EMAIL, settings.JIRA_API_TOKEN)
        )
    except Exception as e:
        logger.error(f"Failed to initialize Jira client: {e}")
        return None


async def create_task(
    summary: str,
    description: str,
    project_key: str = "PROJ",
    issue_type: str = "Task",
    priority: str = "Medium",
) -> dict:
    """
    Create a task in Jira.
    """
    client = _get_client()
    if client:
        try:
            logger.info(f"Creating Jira task: {summary} in {project_key}")
            # Python-jira is synchronous; use to_thread to avoid blocking async loop
            issue_dict = {
                'project': {'key': project_key},
                'summary': summary,
                'description': description,
                'issuetype': {'name': issue_type},
            }
            issue = await asyncio.to_thread(client.create_issue, fields=issue_dict)
            return {
                "issue_key": issue.key,
                "summary": summary,
                "status": "To Do",
                "url": f"{settings.JIRA_SERVER}/browse/{issue.key}"
            }
        except JIRAError as e:
            logger.error(f"Jira API error creating task: {e}")
            return {"error": str(e)}
    else:
        logger.warning(f"Mock: Creating Jira task: {summary} in {project_key} (Missing config)")
        return {
            "issue_key": f"{project_key}-{hash(summary) % 1000 + 100}",
            "summary": summary,
            "status": "To Do",
            "priority": priority,
            "url": f"https://jira.example.com/browse/{project_key}-123",
            "mock": True
        }


async def get_task(issue_key: str) -> dict:
    """
    Get task details from Jira.
    """
    client = _get_client()
    if client:
        try:
            logger.info(f"Fetching Jira task: {issue_key}")
            issue = await asyncio.to_thread(client.issue, issue_key)
            return {
                "issue_key": issue.key,
                "summary": issue.fields.summary,
                "status": issue.fields.status.name,
                "assignee": issue.fields.assignee.displayName if issue.fields.assignee else "Unassigned",
            }
        except JIRAError as e:
            logger.error(f"Jira API error fetching task: {e}")
            return {"error": str(e)}
    else:
        logger.warning(f"Mock: Fetching Jira task: {issue_key}")
        return {
            "issue_key": issue_key,
            "summary": "Mock task",
            "status": "In Progress",
            "assignee": "developer@example.com",
            "mock": True
        }
