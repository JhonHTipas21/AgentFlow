"""
AgentFlow Gmail Integration
Email reading and processing via Gmail API.
"""
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)


async def read_emails(
    mailbox: str = "INBOX",
    max_results: int = 5,
    query: Optional[str] = None,
) -> List[dict]:
    """
    Read emails from a Gmail mailbox.

    TODO: Implement with google-auth and google-api-python-client
    Currently returns mock data for development.
    """
    logger.info(f"Reading emails from {mailbox} (max: {max_results})")

    # Mock implementation
    return [
        {
            "id": f"msg_{i}",
            "subject": f"Email subject {i}",
            "from": f"sender{i}@example.com",
            "date": "2026-04-05",
            "snippet": f"Preview of email {i}...",
            "is_read": i > 2,
        }
        for i in range(1, max_results + 1)
    ]


async def send_email(
    to: str,
    subject: str,
    body: str,
) -> dict:
    """
    Send an email via Gmail API.

    TODO: Implement with OAuth2 credentials
    """
    logger.info(f"Sending email to {to}: {subject}")
    return {
        "status": "sent",
        "to": to,
        "subject": subject,
        "message_id": "mock_msg_id",
    }
