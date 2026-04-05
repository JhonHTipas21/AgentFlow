"""
AgentFlow Celery App
Async task queue for background workflow execution.
"""
import os
import logging

logger = logging.getLogger(__name__)

try:
    from celery import Celery

    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

    celery_app = Celery(
        "agentflow",
        broker=REDIS_URL,
        backend=REDIS_URL,
    )

    celery_app.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
        task_track_started=True,
        task_acks_late=True,
        worker_prefetch_multiplier=1,
        result_expires=3600,  # Results expire after 1 hour
    )

    @celery_app.task(
        name="execute_workflow",
        bind=True,
        max_retries=3,
        default_retry_delay=10,
    )
    def execute_workflow_task(self, agent_id: int, input_data: str, metadata: dict = None):
        """Execute a workflow asynchronously via Celery."""
        import asyncio
        from app.agents import AgentOrchestrator
        from app.database import SessionLocal

        db = SessionLocal()
        try:
            orchestrator = AgentOrchestrator(agent_id, db)
            result = asyncio.run(
                orchestrator.execute_workflow(input_data, metadata)
            )
            return result
        except Exception as e:
            logger.error(f"Celery task failed for agent {agent_id}: {e}")
            raise self.retry(exc=e)
        finally:
            db.close()

except ImportError:
    logger.info("Celery not available — async tasks disabled")
    celery_app = None

    def execute_workflow_task(*args, **kwargs):
        raise RuntimeError("Celery is not installed. Install with: pip install celery")
