 
import os
import logging
from azure.communication.email import EmailClient
from dotenv import load_dotenv
 
load_dotenv()
 
email_connection_string = os.getenv("ACS_EMAIL_CONNECTION_STRING")
sender_address = os.getenv("ACS_SENDER_ADDRESS")
 
logger = logging.getLogger(__name__)
 
def send_email(subject, body, to_emails, html_body=None):
    try:
        client = EmailClient.from_connection_string(email_connection_string)
        message = {
            "senderAddress": sender_address,
            "recipients": {
                "to": [{"address": email} for email in to_emails],
            },
            "content": {
                "subject": subject,
                "plainText": body,
            },
        }
        if html_body:
            message["content"]["html"] = html_body
 
        poller = client.begin_send(message)
        result = poller.result()
        logger.info(f"Email sent. Message ID: {result['id']}")
        return result
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        raise
 
 