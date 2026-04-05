"""
AgentFlow Agent Orchestrator
Core engine that executes workflows using Claude API.
"""
from sqlalchemy.orm import Session
from datetime import datetime
import logging
import time

from app import models
from app.config import settings
from app.tools import AVAILABLE_TOOLS
from app.state import StateManager

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """
    Main agent orchestration engine.

    Manages the lifecycle of a workflow execution:
    1. Load agent configuration from DB
    2. Create workflow record
    3. Call Claude API with system prompt + tools context
    4. Track execution time, tokens, and cost
    5. Log all events
    """

    def __init__(self, agent_id: int, db: Session):
        self.agent_id = agent_id
        self.db = db
        self.agent = db.query(models.Agent).filter(
            models.Agent.id == agent_id
        ).first()

        if not self.agent:
            raise ValueError(f"Agent {agent_id} not found")

        self.tool_names = [t.name for t in self.agent.tools]
        self.state = StateManager(agent_id)

    async def execute_workflow(
        self,
        input_data: str,
        metadata: dict = None
    ) -> dict:
        """Execute a complete workflow with the agent."""

        start_time = time.time()
        self.state.set_status("running")

        # Create workflow record
        workflow = models.Workflow(
            agent_id=self.agent_id,
            input=input_data,
            status=models.WorkflowStatus.RUNNING,
            metadata_json=metadata or {},
        )
        self.db.add(workflow)
        self.db.commit()
        self.db.refresh(workflow)

        self._log_event(
            workflow.id, "info", "started",
            f"Workflow started for agent '{self.agent.name}'"
        )

        try:
            # Build the system prompt with tool awareness
            system_prompt = self._build_system_prompt()

            # Call Claude API
            result = await self._call_claude(system_prompt, input_data)

            execution_time = time.time() - start_time

            # Update workflow with results
            workflow.output = result["content"]
            workflow.status = models.WorkflowStatus.SUCCESS
            workflow.execution_time = round(execution_time, 3)
            workflow.tokens_used = result.get("tokens_used")
            workflow.cost_usd = result.get("cost_usd")
            workflow.completed_at = datetime.utcnow()

            self._log_event(
                workflow.id, "info", "completed",
                f"Workflow completed in {execution_time:.2f}s"
            )

            # Record state metrics
            self.state.record_execution(workflow.id, True, execution_time)
            self.state.set_status("idle")

            logger.info(
                f"Workflow {workflow.id} completed in {execution_time:.2f}s "
                f"(tokens: {result.get('tokens_used', 'N/A')})"
            )

        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = str(e)

            workflow.status = models.WorkflowStatus.FAILED
            workflow.error_message = error_msg
            workflow.execution_time = round(execution_time, 3)
            workflow.completed_at = datetime.utcnow()

            self._log_event(
                workflow.id, "error", "failed",
                f"Workflow failed: {error_msg}"
            )

            # Record failure in state
            self.state.record_execution(workflow.id, False, execution_time)
            self.state.set_status("error")

            logger.error(f"Workflow {workflow.id} failed: {error_msg}")

        self.db.commit()
        self.db.refresh(workflow)

        return {
            "id": workflow.id,
            "workflow_id": workflow.id,
            "uuid": workflow.uuid,
            "agent_id": self.agent_id,
            "input": workflow.input,
            "output": workflow.output,
            "status": workflow.status.value,
            "execution_time": workflow.execution_time,
            "tokens_used": workflow.tokens_used,
            "cost_usd": workflow.cost_usd,
            "error_message": workflow.error_message,
            "created_at": workflow.created_at.isoformat(),
            "completed_at": (
                workflow.completed_at.isoformat()
                if workflow.completed_at else None
            ),
        }

    def _build_system_prompt(self) -> str:
        """Build the system prompt with agent config and available tools."""
        base_prompt = self.agent.system_prompt or (
            f"You are {self.agent.name}, an AI assistant. "
            f"{self.agent.description or ''} "
            f"Be helpful, accurate, and concise."
        )

        if self.tool_names:
            tools_desc = "\n".join(
                f"- {name}: {AVAILABLE_TOOLS[name].description}"
                for name in self.tool_names
                if name in AVAILABLE_TOOLS
            )
            base_prompt += (
                f"\n\nYou have access to the following tools:\n{tools_desc}\n"
                f"When you need to use a tool, describe what you would do with it."
            )

        return base_prompt

    async def _call_claude(self, system_prompt: str, user_input: str) -> dict:
        """Call the Claude API."""
        try:
            import anthropic

            client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

            response = client.messages.create(
                model=self.agent.model or "claude-sonnet-4-20250514",
                max_tokens=self.agent.max_tokens or 2000,
                temperature=self.agent.temperature or 0.7,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_input}
                ],
            )

            # Extract usage
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            total_tokens = input_tokens + output_tokens

            # Estimate cost (Claude Sonnet pricing approximate)
            cost = (input_tokens * 0.003 + output_tokens * 0.015) / 1000

            return {
                "content": response.content[0].text,
                "tokens_used": total_tokens,
                "cost_usd": round(cost, 6),
                "model": response.model,
            }

        except ImportError:
            logger.warning("anthropic package not installed, using mock response")
            return self._mock_response(user_input)
        except Exception as e:
            if "api_key" in str(e).lower() or "auth" in str(e).lower():
                logger.warning(f"Claude API auth error: {e}. Using mock response.")
                return self._mock_response(user_input)
            raise

    def _mock_response(self, user_input: str) -> dict:
        """Generate a mock response when Claude API is not available."""
        mock_output = (
            f"[Mock Response — Claude API not configured]\n\n"
            f"Agent '{self.agent.name}' received your request:\n"
            f"'{user_input[:200]}'\n\n"
            f"Available tools: {', '.join(self.tool_names) or 'none'}\n\n"
            f"To enable real AI responses, set ANTHROPIC_API_KEY in your .env file."
        )
        return {
            "content": mock_output,
            "tokens_used": 0,
            "cost_usd": 0.0,
            "model": "mock",
        }

    def _log_event(
        self,
        workflow_id: int,
        level: str,
        event_type: str,
        message: str,
    ):
        """Record a workflow event in the database."""
        log_level = getattr(models.LogLevel, level.upper(), models.LogLevel.INFO)
        log = models.WorkflowLog(
            workflow_id=workflow_id,
            level=log_level,
            message=message,
            event_type=event_type,
        )
        self.db.add(log)
        # Don't commit here — let the caller commit
