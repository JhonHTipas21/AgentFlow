"""
AgentFlow State Manager
In-memory state management with optional Redis backend.
Tracks agent status, workflow progress, and runtime metrics.
"""
import json
import logging
from typing import Any, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class StateManager:
    """
    Manages agent runtime state.

    Uses an in-memory dict by default. When Redis is available,
    automatically switches to Redis for persistence across restarts.
    """

    _redis_client = None
    _memory_store: Dict[str, str] = {}
    _initialized = False

    @classmethod
    def _init_redis(cls):
        """Try to connect to Redis once."""
        if cls._initialized:
            return
        cls._initialized = True

        try:
            import redis
            from app.config import settings

            cls._redis_client = redis.Redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=2,
            )
            cls._redis_client.ping()
            logger.info("✅ StateManager connected to Redis")
        except Exception as e:
            cls._redis_client = None
            logger.info(f"📦 StateManager using in-memory store (Redis unavailable: {e})")

    def __init__(self, agent_id: int):
        self._init_redis()
        self.agent_id = agent_id
        self.key = f"agent:{agent_id}:state"

    # ─── Core Operations ────────────────────────────────

    def get(self) -> Dict[str, Any]:
        """Get the full agent state."""
        try:
            if self._redis_client:
                raw = self._redis_client.get(self.key)
            else:
                raw = self._memory_store.get(self.key)

            return json.loads(raw) if raw else self._default_state()
        except Exception as e:
            logger.error(f"StateManager.get failed: {e}")
            return self._default_state()

    def set(self, state: Dict[str, Any]) -> None:
        """Set the full agent state."""
        state["updated_at"] = datetime.utcnow().isoformat()
        serialized = json.dumps(state)

        try:
            if self._redis_client:
                self._redis_client.set(self.key, serialized, ex=86400)  # 24h TTL
            else:
                self._memory_store[self.key] = serialized
        except Exception as e:
            logger.error(f"StateManager.set failed: {e}")

    def update(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Merge updates into current state."""
        current = self.get()
        current.update(updates)
        self.set(current)
        return current

    def delete(self) -> None:
        """Clear the agent state."""
        try:
            if self._redis_client:
                self._redis_client.delete(self.key)
            else:
                self._memory_store.pop(self.key, None)
        except Exception as e:
            logger.error(f"StateManager.delete failed: {e}")

    # ─── Convenience Methods ─────────────────────────────

    def set_status(self, status: str) -> None:
        """Update agent runtime status (idle, running, error)."""
        self.update({"runtime_status": status})

    def record_execution(self, workflow_id: int, success: bool, execution_time: float) -> None:
        """Record a workflow execution in the agent's state."""
        state = self.get()

        # Update counters
        state["total_executions"] = state.get("total_executions", 0) + 1
        if success:
            state["successful_executions"] = state.get("successful_executions", 0) + 1
        else:
            state["failed_executions"] = state.get("failed_executions", 0) + 1

        state["last_execution"] = {
            "workflow_id": workflow_id,
            "success": success,
            "execution_time": execution_time,
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Running average execution time
        total = state["total_executions"]
        avg = state.get("avg_execution_time", 0)
        state["avg_execution_time"] = round(
            ((avg * (total - 1)) + execution_time) / total, 3
        )

        self.set(state)

    def _default_state(self) -> Dict[str, Any]:
        """Default state for a new agent."""
        return {
            "agent_id": self.agent_id,
            "runtime_status": "idle",
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "avg_execution_time": 0,
            "last_execution": None,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
