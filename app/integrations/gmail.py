"""
AgentFlow Gmail Integration
Email reading and processing via Gmail API.
"""
import logging
from typing import List, Optional
import os
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import asyncio

logger = logging.getLogger(__name__)

# Scopes needed for reading and sending email
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']


def _get_gmail_service():
    """Get instantiated Gmail service if token.json exists."""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        else:
            return None
    try:
        service = build('gmail', 'v1', credentials=creds)
        return service
    except Exception as e:
        logger.error(f"Failed to build Gmail service: {e}")
        return None


async def read_emails(
    mailbox: str = "INBOX",
    max_results: int = 5,
    query: Optional[str] = None,
) -> List[dict]:
    """
    Read emails from a Gmail mailbox.
    """
    service = _get_gmail_service()
    if service:
        try:
            logger.info(f"Reading emails from {mailbox} (max: {max_results})")
            q = query or f"label:{mailbox}"
            results = await asyncio.to_thread(
                service.users().messages().list(userId='me', labelIds=[mailbox], maxResults=max_results, q=query).execute
            )
            messages = results.get('messages', [])
            
            emails = []
            for msg in messages:
                msg_data = await asyncio.to_thread(
                    service.users().messages().get(userId='me', id=msg['id']).execute
                )
                headers = msg_data.get('payload', {}).get('headers', [])
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "No Subject")
                sender = next((h['value'] for h in headers if h['name'] == 'From'), "Unknown")
                
                emails.append({
                    "id": msg['id'],
                    "subject": subject,
                    "from": sender,
                    "snippet": msg_data.get('snippet', ''),
                    "is_read": 'UNREAD' not in msg_data.get('labelIds', [])
                })
            return emails
        except Exception as e:
            logger.error(f"Gmail API error reading emails: {e}")
            return [{"error": str(e)}]
    else:
        logger.warning(f"Mock: Reading emails from {mailbox} (No token.json found)")
        return [
            {
                "id": f"msg_{i}",
                "subject": f"Email subject {i}",
                "from": f"sender{i}@example.com",
                "date": "2026-04-05",
                "snippet": f"Preview of email {i}...",
                "is_read": i > 2,
                "mock": True
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
    """
    service = _get_gmail_service()
    if service:
        try:
            logger.info(f"Sending email to {to}: {subject}")
            import base64
            from email.message import EmailMessage

            message = EmailMessage()
            message.set_content(body)
            message['To'] = to
            message['From'] = 'me'
            message['Subject'] = subject

            encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            create_message = {'raw': encoded_message}

            send_message = await asyncio.to_thread(
                service.users().messages().send(userId="me", body=create_message).execute
            )
            return {
                "status": "sent",
                "to": to,
                "subject": subject,
                "message_id": send_message['id']
            }
        except Exception as e:
            logger.error(f"Gmail API error sending email: {e}")
            return {"status": "error", "error": str(e)}
    else:
        logger.warning(f"Mock: Sending email to {to}: {subject}")
        return {
            "status": "sent",
            "to": to,
            "subject": subject,
            "message_id": "mock_msg_id",
            "mock": True
        }
