"""
AgentFlow Slack Integration
Message sending and channel management via Slack API.
"""
import logging
from typing import Optional
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.errors import SlackApiError
from app.config import settings

logger = logging.getLogger(__name__)


def _get_client() -> Optional[AsyncWebClient]:
    """Get instantiated Slack client if token exists."""
    if not settings.SLACK_BOT_TOKEN:
        return None
    return AsyncWebClient(token=settings.SLACK_BOT_TOKEN)


async def send_message(
    channel: str,
    text: str,
    thread_ts: Optional[str] = None,
) -> dict:
    """
    Send a message to a Slack channel.
    Uses real Slack SDK if SLACK_BOT_TOKEN is set.
    """
    client = _get_client()
    if client:
        try:
            logger.info(f"Sending Slack message to {channel}")
            response = await client.chat_postMessage(
                channel=channel,
                text=text,
                thread_ts=thread_ts
            )
            return {
                "ok": True,
                "channel": channel,
                "ts": response.get("ts"),
                "message": response.get("message"),
            }
        except SlackApiError as e:
            logger.error(f"Slack API error: {e.response['error']}")
            return {"ok": False, "error": e.response['error']}
    else:
        # Mock mode
        logger.warning(f"Mock: Sending Slack message to {channel} (No SLACK_BOT_TOKEN)")
        return {
            "ok": True,
            "channel": channel,
            "ts": "1234567890.123456",
            "message": {"text": text[:100], "type": "message"},
            "mock": True
        }


async def send_notification(
    channel: str,
    title: str,
    message: str,
    color: str = "#36a64f",
) -> dict:
    """
    Send a rich notification (attachment) to Slack.
    Uses real Slack SDK if SLACK_BOT_TOKEN is set.
    """
    client = _get_client()
    if client:
        try:
            attachments = [{
                "color": color,
                "title": title,
                "text": message
            }]
            response = await client.chat_postMessage(
                channel=channel,
                attachments=attachments
            )
            return {"ok": True, "channel": channel, "ts": response.get("ts")}
        except SlackApiError as e:
            logger.error(f"Slack API error: {e.response['error']}")
            return {"ok": False, "error": e.response['error']}
    else:
        # Mock mode
        logger.warning(f"Mock: Sending notification to {channel}")
        return {
            "ok": True,
            "channel": channel,
            "notification_type": "attachment",
            "title": title,
            "mock": True
        }
